"""xformers.ops shim — memory_efficient_attention routed to PyTorch SDPA."""

import torch
import torch.nn.functional as F


def memory_efficient_attention(query, key, value, attn_bias=None, scale=None, op=None, **kwargs):
    """Drop-in replacement for xformers.ops.memory_efficient_attention.

    Routes to torch.nn.functional.scaled_dot_product_attention which uses
    the MATH backend on Polaris/ZLUDA (no efficient attention kernels available).
    """
    if query.ndim == 3:
        # (B, S, D) -> (B, H, S, D) expected by SDPA
        # Caller already handled reshaping; just pass through
        pass

    return F.scaled_dot_product_attention(
        query, key, value,
        attn_mask=attn_bias,
        scale=scale,
    )
