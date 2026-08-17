import torch
import torch.nn as nn
import logging

GROUP_SIZE = 128


def quantize_weight_int4(w):
    orig_shape = w.shape
    w = w.reshape(-1, GROUP_SIZE)
    amax = w.abs().amax(dim=1, keepdim=True).clamp(min=1e-12)
    scale = amax / 7.0
    w_q = w.div(scale).round().clamp(-8, 7).to(torch.int8)
    w_q = w_q.reshape(orig_shape)
    scale = scale.reshape(orig_shape[0], -1)
    return w_q, scale


def dequantize_int4(w_q, scale):
    orig_shape = w_q.shape
    w_q = w_q.reshape(-1, GROUP_SIZE)
    scale = scale.reshape(-1, scale.shape[-1])
    w = w_q.float() * scale
    return w.reshape(orig_shape)


class Int4Linear(nn.Module):
    def __init__(self, in_features, out_features, bias=True, device=None, dtype=None):
        super().__init__()
        self.in_features = in_features
        self.out_features = out_features
        self.weight_q = nn.Parameter(
            torch.empty(out_features, in_features, dtype=torch.int8, device=device),
            requires_grad=False,
        )
        self.weight_scale = nn.Parameter(
            torch.empty(out_features, in_features // GROUP_SIZE, dtype=torch.float16, device=device),
            requires_grad=False,
        )
        if bias:
            self.bias = nn.Parameter(
                torch.empty(out_features, dtype=dtype or torch.float16, device=device),
                requires_grad=False,
            )
        else:
            self.bias = None

    def forward(self, x):
        w = dequantize_int4(self.weight_q, self.weight_scale).to(x.dtype)
        return torch.nn.functional.linear(x, w, self.bias)


@torch.no_grad()
def quantize_model_int4(model, exclude_names=None):
    exclude_names = set(exclude_names or [])
    count = 0
    for name, module in list(model.named_modules()):
        if isinstance(module, nn.Linear):
            if name in exclude_names:
                continue
            if module.weight.shape[0] % GROUP_SIZE != 0 or module.weight.shape[1] % GROUP_SIZE != 0:
                continue
            parent, attr = _get_parent(model, name)
            if parent is None:
                continue
            q = Int4Linear(
                module.in_features,
                module.out_features,
                bias=module.bias is not None,
                device=module.weight.device,
                dtype=module.weight.dtype,
            )
            w_q, w_scale = quantize_weight_int4(module.weight.data)
            q.weight_q = nn.Parameter(w_q, requires_grad=False)
            q.weight_scale = nn.Parameter(w_scale.half(), requires_grad=False)
            if module.bias is not None:
                q.bias = nn.Parameter(module.bias.data.clone(), requires_grad=False)
            setattr(parent, attr, q)
            count += 1
    logging.info(f"[polaris] Quantized {count} Linear layers to weight-only INT4 (group-{GROUP_SIZE}).")
    return model


def _get_parent(model, name):
    parts = name.split(".")
    parent = model
    for p in parts[:-1]:
        parent = getattr(parent, p)
    return parent, parts[-1]
