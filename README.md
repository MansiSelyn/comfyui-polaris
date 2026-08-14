# ComfyUI Polaris

> **This is an experiment.** This fork exists to see what agentic AI can do: it
> was produced entirely by an AI coding agent working against a goal, not by a
> human team. Expect rough edges, and treat it as a proof of concept rather than
> a polished product.

ComfyUI Polaris is a modified copy of [ComfyUI](https://github.com/comfyanonymous/ComfyUI)
(upstream commit `7fe8a613`) made to run on **AMD Polaris** graphics cards
(RX 4xx / 5xx series, e.g. an RX 570) under Windows. Those GPUs are old enough
that the normal AMD tooling dropped support for them, so stock ComfyUI cannot
use them for GPU-accelerated image generation.

## What it is

ComfyUI itself is unchanged in spirit: a node-based tool for building image,
video, audio, and text-generation workflows. What this fork changes is the
plumbing that lets your graphics card actually do the work.

Polaris GPUs are not supported by AMD's official ROCm platform, so this fork
gives you two ways to run on the GPU instead:

- **DirectML** (the default, most reliable): uses a Microsoft layer that talks
  to any modern GPU, including older AMD cards.
- **ZLUDA** (optional, often faster): an open-source compatibility layer that
  tricks software written for NVIDIA GPUs into running on AMD hardware.

## How it differs from the original ComfyUI

- **Made for old AMD cards.** Stock ComfyUI targets NVIDIA and newer AMD GPUs.
  This fork adds support for Polaris (RX 4xx/5xx), which AMD no longer supports.
- **Two GPU backends.** Original ComfyUI only really knows about NVIDIA (CUDA)
  and newer AMD (ROCm). This fork adds DirectML and ZLUDA backends, and you pick
  one when you start it.
- **Split installation.** Because the two backends cannot live in the same
  Python environment, the installer creates two separate environments and the
  one requirements file is organized into sections for each.
- **Self-installing setup.** `install.bat` downloads and sets up the ZLUDA
  runtime automatically instead of expecting you to place files by hand.
- **A few compatibility patches.** Some newer, GPU-accelerated model features
  are too tied to NVIDIA-only libraries to work on this hardware, so those code
  paths are guarded to give a clear error instead of crashing.
- **Trimmed repo.** Things that aren't relevant to this experiment were removed:
  CI/test infrastructure, the example workflows, and repo-meta files.

The user interface, workflows, custom nodes, and model support are otherwise the
same ComfyUI you know. It is a fork of the upstream project, and upstream fixes
do not flow into it automatically.

## Installation

Requirements:

- Windows
- An AMD Polaris GPU (RX 4xx / 5xx)
- Python 3.8-3.12 ([python.org](https://www.python.org/downloads/))
  — newer Python versions are not supported by one of the backends

Steps:

1. Install Python (check the box to add it to your `PATH`).
2. Run `install.bat` in this folder and wait. It creates the two Python
   environments and downloads what it needs on first run.
3. Optionally install the AMD HIP SDK 5.7.1 and set the `HIP_PATH` environment
   variable — this is only needed for the faster ZLUDA backend.

That's it. If the ZLUDA download fails or HIP is missing, the installer warns
and continues; DirectML still works.

## Running

Put your models in `models\checkpoints` (Stable Diffusion checkpoints) and
`models\vae`, then start one of:

```powershell
.\.venv\Scripts\python.exe main.py --directml
```

or, for the faster ZLUDA backend:

```powershell
python main.py --zluda
```

Then open the URL printed in the console (usually http://127.0.0.1:8188) in your
browser and build a workflow.

Notes for typical usage:

- If the VAE errors with an out-of-memory message, add `--cpu-vae`: it moves the
  image encode/decode step to the CPU (sampling still runs on the GPU), which
  avoids a graphics-memory bug on Polaris.
- If you run out of graphics memory, add `--lowvram`.
- SD 1.5-class models work well. Some very new model families require NVIDIA-only
  libraries and will show a clear error instead of working.

## What works and what doesn't

Verified on an 8 GB RX 570:

- DirectML: stable diffusion 1.5, 512x512 images, GPU sampling with `--cpu-vae`.
- ZLUDA: same workload end-to-end, roughly twice as fast when it works.

Known rough edges (the experiment in action):

- Not every model type is supported — anything needing NVIDIA-only kernel
  libraries (fp8/fp4 quantized models, some newer VAEs) errors out clearly.
- Don't let `pip` upgrade `torch` yourself; it can break the pinned versions.
  Re-run `install.bat` to restore them.
- A harmless `Could not autodetect AIMDO implementation` warning appears at
  startup. Ignore it.

## Project layout

- `install.bat` — the whole setup: environments + automatic ZLUDA runtime
  download and deployment.
- `requirements.txt` — dependency manifest organized into DIRECTML / ZLUDA /
  MANAGER sections.
- `comfy\` — the ComfyUI engine, lightly patched for this experiment.
- `main.py` — the entry point; it knows how to relaunch itself into the right
  environment for the backend you chose.
