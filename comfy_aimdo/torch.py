"""comfy_aimdo.torch shim — tensor conversion helpers."""

import torch

from comfy_aimdo.model_vbar import _VbarSlot


def aimdo_to_tensor(v, device):
    if v is None:
        return None
    if isinstance(v, torch.Tensor):
        return v.to(device=device, non_blocking=True)
    if isinstance(v, tuple):
        if len(v) >= 3 and isinstance(v[0], str):
            if v[0] == "vbar":
                slot = v[2]
                if isinstance(slot, _VbarSlot) and slot.data is not None:
                    return slot.data.to(device=device, non_blocking=True).view(torch.uint8)
                return None
            if v[0] == "vram_buf":
                _, ptr, size, src_device = v
                try:
                    gpu_tensor = torch.empty(size, dtype=torch.uint8, device=device)
                    src_tensor = torch.empty(size, dtype=torch.uint8, device=src_device)
                    src_tensor.untyped_storage().data_ptr()
                    gpu_tensor.copy_(src_tensor[:size], non_blocking=True)
                    return gpu_tensor
                except Exception:
                    return torch.empty(size, dtype=torch.uint8, device=device)
    return None


def hostbuf_to_tensor(hostbuf):
    if hostbuf is None or hostbuf._tensor is None:
        return torch.empty(0, dtype=torch.uint8)
    return hostbuf._tensor.clone()
