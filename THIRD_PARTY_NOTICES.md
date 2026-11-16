# Third-party notices

This repository (workflows, installer) is GPL-3.0. It uses or is based on the following third-party work.
Node packs and models are **not** included here: the installer downloads them from their original sources, pinned to tested versions.

## Workflows

The UltraTex workflows (3D-Texturing*) are based on the UltraTex workflows by PixelArtistry:
https://github.com/pixelartistry/PixelArtistry-UltraTex

```
MIT License

Copyright (c) 2026 PixelArtistry

This license covers the files authored by PixelArtistry in this repository:
the installer (Install-UltraTex.bat) and the workflow layouts and notes in
"workflows". Third-party node packs and models used by the workflows are not
included here and keep their own licenses (see README.md, section "License").

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

## Node packs (downloaded by the installer)

| Pack | Source | Version | License |
|---|---|---|---|
| ComfyUI-UltraTex (visualbruno) | https://github.com/visualbruno/ComfyUI-UltraTex | 1f2392308e7d08374cb1c3844afe7e3ee2fadbe0 | MIT |
| UltraTex-ComfyUI-nodes (MostAadTech) | https://github.com/Mstafa-awad/UltraTex-ComfyUI-nodes | 8d434a2104be520ea699a9baac2327d124387111 | GPL-3.0 |
| ComfyUI-GGUF (city96) | https://github.com/city96/ComfyUI-GGUF | 1.1.10 | Apache-2.0 |
| s_tools | https://github.com/sofiakholina/sofiakholina-s_tools | 1.0.1 | GPL-3.0 |
| triton-windows | https://github.com/triton-lang/triton-windows | by torch version | MIT |

For the embedded Python of ComfyUI Portable the installer adds Python `include`/`libs` files published by the triton-windows project
(https://github.com/woct0rdho/triton-windows/releases/tag/v3.0.0-windows.post1, Python Software Foundation License).

## Python packages (installed by the installer from PyPI, if missing)

| Package | Needed by | License |
|---|---|---|
| trimesh, moderngl, glcontext, xatlas | UltraTex nodes | MIT |
| gguf | ComfyUI-GGUF, UltraTex-ComfyUI-nodes | MIT |
| sentencepiece | ComfyUI-GGUF | Apache-2.0 |
| protobuf | ComfyUI-GGUF | BSD-3-Clause |

## Models (downloaded by the installer)

| File | Source | License |
|---|---|---|
| flux2_klein_9b_base_int8_convrot.safetensors | huggingface.co/Botoni/Flux-2-Klein-INT8-ConvRot-Collection (FLUX.2 [klein] Base 9B, Black Forest Labs) | FLUX Non-Commercial License |
| flux-2-klein-9b_int8_convrot.safetensors | huggingface.co/obsxrver/ComfyUI-Native-INT8_ConvRot (FLUX.2 [klein] 9B, Black Forest Labs) | FLUX Non-Commercial License |
| flux-2-klein-base-9b-Q4_0.gguf | huggingface.co/unsloth/FLUX.2-klein-base-9B-GGUF | FLUX Non-Commercial License |
| flux-2-klein-9b-Q4_0.gguf | huggingface.co/unsloth/FLUX.2-klein-9B-GGUF | FLUX Non-Commercial License |
| qwen_3_8b_fp8mixed.safetensors | huggingface.co/Comfy-Org/flux2-klein-9B (Qwen3-8B) | Apache-2.0 |
| Qwen3-8B-Q4_K_M.gguf | huggingface.co/unsloth/Qwen3-8B-GGUF | Apache-2.0 |
| flux2-vae.safetensors | huggingface.co/Comfy-Org/flux2-dev (FLUX.2 VAE, Black Forest Labs) | Apache-2.0 |
| ultratex_flux2.safetensors, ultratex_flux2_decoder.pt | modelscope Yibo-Zhang/UltraTex (flux2/lora/dit_lora.safetensors, flux2/decoder.pt), UltraTex team | MIT |
| birefnet.safetensors | huggingface.co/Comfy-Org/BiRefNet | MIT |

FLUX Non-Commercial License: https://github.com/black-forest-labs/flux2/blob/main/model_licenses/LICENSE-FLUX-NON-COMMERICAL
