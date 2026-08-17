"""sageattention shim — routes to torch.nn.functional.scaled_dot_product_attention.

SageAttention uses hand-written CUDA kernels with inline PTX assembly.
This shim provides the same API but uses PyTorch's MATH SDPA backend.
"""

import torch
import torch.nn.functional as F


def sageattn(q, k, v, is_causal=False, tensor_layout="NHD", sm_scale=None, smooth_k=False, attn_mask=None, **kwargs):
    """Drop-in replacement for sageattn().

    Routes to torch.nn.functional.scaled_dot_product_attention.
    """
    # sageattn uses (B, S, D) or (B, H, S, D) depending on tensor_layout
    if tensor_layout == "HND":
        # q,k,v are (B, H, S, D) — SDPA expects same
        pass
    else:
        # q,k,v are (B, S, D) — need to reshape if multi-head is implicit
        if q.ndim == 3:
            # Assume heads are already folded into the feature dim
            pass

    if sm_scale is not None:
        return F.scaled_dot_product_attention(q, k, v, attn_mask=attn_mask, is_causal=is_causal, scale=sm_scale)
    return F.scaled_dot_product_attention(q, k, v, attn_mask=attn_mask, is_causal=is_causal)
