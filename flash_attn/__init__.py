"""flash_attn shim — routes to torch.nn.functional.scaled_dot_product_attention.

Flash Attention requires Ampere+ SM (SM 8.x+). This shim provides the same
API using PyTorch's MATH SDPA backend on Polaris.
"""

import torch
import torch.nn.functional as F


def flash_attn_func(q, k, v, dropout_p=0.0, causal=False, softmax_scale=None, **kwargs):
    """Drop-in replacement for flash_attn.flash_attn_func.

    Routes to torch.nn.functional.scaled_dot_product_attention.

    Args:
        q: (batch, seqlen, nheads, headdim) or (batch, nheads, seqlen, headdim)
        k: same shape as q
        v: same shape as q
        dropout_p: dropout probability (ignored in MATH backend)
        causal: whether to apply causal mask
        softmax_scale: optional scale factor
    """
    if softmax_scale is None:
        softmax_scale = q.shape[-1] ** -0.5

    return F.scaled_dot_product_attention(
        q, k, v,
        dropout_p=dropout_p if q.requires_grad else 0.0,
        is_causal=causal,
        scale=softmax_scale,
    )
