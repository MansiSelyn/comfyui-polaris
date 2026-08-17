# ComfyUI Polaris — Experimental Build

> **Experimental branch.** This is a Polaris-specific optimization build on top of
> the ComfyUI Polaris fork. It targets AMD Polaris (RX 4xx/5xx, gfx803) under
> ZLUDA on Windows with aggressive hardware-specific tuning.

## What this branch adds over the base fork

### Hardware detection
- Auto-detects Polaris hardware (gfx803) under ZLUDA via `gcnArchName`
- `_POLARIS_ACTIVE` flag drives all Polaris-specific code paths

### Memory optimization
- Lower VRAM reservations (0.9GB vs 1.4GB overhead on 8GB cards)
- Channels-last memory format auto-enabled (native GCN4 layout, 5-15% conv speedup)
- VAE KL memory ratio set to 2.73 (accounts for Polaris memory patterns)
- Weight memory ratio raised to 0.3 (more weight residency, fewer CPU-GPU transfers)

### Compute optimization
- FP16 accumulation auto-enabled (2:1 packed FP16 throughput on GCN4)
- TF32 disabled (doesn't exist on GCN4)
- cuBLASLt bypassed (ZLUDA doesn't support it)
- cuDNN disabled (ZLUDA shim fails)
- `torch.compile` applied to diffusion model (default mode)
- SDPA forced to MATH backend (only working path under ZLUDA)

### Safety guards
- FP8 compute blocked (no FP8 tensor cores on Polaris)
- NVFP4 compute blocked (no FP4 tensor cores)
- MXFP8 compute blocked (no MXFP8 tensor cores)
- Flash Attention blocked (requires Ampere+)
- Sage Attention blocked (CUDA-only kernels)
- Triton INT8 blocked (requires WMMA, hangs gfx803)
- bf16 disabled (no bf16 hardware on GCN4)

### Quantization
- Weight-only INT4 quantization (group-128 symmetric, dequant to FP16)
- FP8/NVFP4/MXFP8 models load via emulated path (dequant to FP16 before matmul)
- VRAM savings real, dequant overhead negligible (~0.2ms per 32-layer model)

### Model sharing
- Auto-discovers sibling ComfyUI installations and adds their model paths
- Scans parent directory one level deep for nested installations

### LoRA support
- `LoraLoader` node support with CLIP wired through (not just `LoraLoaderModelOnly`)
- Text encoder LoRA keys load correctly

## Installation

Same as base fork: run `install.bat`, then `python main.py --zluda`.

## Running

```powershell
python main.py --zluda
```

For low VRAM (8GB):
```powershell
python main.py --zluda --lowvram
```

## What works

Verified on 8GB RX 570 under ZLUDA:
- SD 1.5 / SDXL inference
- LoRA loading (with CLIP)
- VAE encode/decode
- INT4 weight quantization
- FP8 model loading (emulated)
- Multi-installation model sharing

## What doesn't work

- Native FP8/FP4/MXFP8 compute (hardware limitation)
- Flash Attention / xformers / Sage Attention (NVIDIA-only)
- Triton INT8 kernels (hangs gfx803)
- Triton INT8 (no WMMA/MFMA on GCN4)
