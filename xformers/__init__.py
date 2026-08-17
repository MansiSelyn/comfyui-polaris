"""xformers shim — routes to torch.nn.functional.scaled_dot_product_attention.

This shim provides the xformers API surface using PyTorch's built-in SDPA
(MATH backend on Polaris). It exists so code that imports xformers doesn't
crash, and attention still produces correct results.

It is slower than real xformers (MATH materializes full N×N attention matrix
vs. memory-efficient tiled implementation), but it works on hardware that
can't compile xformers' CUTLASS kernels.
"""

__version__ = "0.0.29-shim"
