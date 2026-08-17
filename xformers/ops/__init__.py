"""xformers.ops shim — memory_efficient_attention routed to PyTorch SDPA."""

import torch
import torch.nn.functional as F


def memory_efficient_attention(query, key, value, attn_bias=None, scale=None, op=None, **kwargs):
    """Drop-in replacement for xformers.ops.memory_efficient_attention.

    Routes to torch.nn.functional.scaled_dot_product_attention which uses
    the MATH backend on Polaris/ZLUDA (no efficient attention kernels available).
    """
    # xformers format: (B, S, H, D) — SDPA format: (B, H, S, D)
    if query.ndim == 4:
        query = query.permute(0, 2, 1, 3).contiguous()
        key = key.permute(0, 2, 1, 3).contiguous()
        value = value.permute(0, 2, 1, 3).contiguous()

    return F.scaled_dot_product_attention(
        query, key, value,
        attn_mask=attn_bias,
        scale=scale,
    )
