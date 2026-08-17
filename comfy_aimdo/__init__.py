"""Pure-Python reimplementation of comfy_aimdo for PyTorch < 2.8.

This shim provides the same interface as comfy_aimdo 0.4.13 using only
standard PyTorch 2.4.1 CUDA APIs. It is slower than the C++ version
(no virtual memory management, no zero-copy DMA) but provides identical
behavior so ComfyUI's DynamicVRAM code paths work on older PyTorch.

This is a joke. It works, but it's a joke.
"""

__version__ = "0.4.13-shim"
