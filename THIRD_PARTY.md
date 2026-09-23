# Third-party software and models

> This file is shared with the full Low-VRAM AI Video Pack. This free repository contains only the
> text-to-video workflow (02) and the installer; rows for workflows 01, 03 and 04 describe the full pack.

This pack contains **only files written by Kanto Labs**: four workflow graphs (`.json`), the
installer script, a helper script and documentation. It contains **no third-party code and no model
weights**. The workflows *reference* nodes and models that you install yourself, from their authors,
under their licences. Thank you to every author below - these workflows are built entirely on your work.

Licence summaries below are our plain-English reading, not legal advice. The linked licence text is
what binds you. Read it.

## 1. Software you install

| component | used by | repository | licence |
|---|---|---|---|
| ComfyUI (core; LTX-2.5 and Krea 2 nodes are built in) | all | https://github.com/comfyanonymous/ComfyUI | GPL-3.0 |
| ComfyUI-GGUF by city96 (`UnetLoaderGGUF`) | 01, 02 | https://github.com/city96/ComfyUI-GGUF | Apache-2.0 |
| ComfyUI-VideoHelperSuite by Kosinkadink (`VHS_LoadVideoPath`) | 03 | https://github.com/Kosinkadink/ComfyUI-VideoHelperSuite | GPL-3.0 |
| ffmpeg (for `tools/mux_original_audio.py`) | 03 | https://ffmpeg.org | LGPL/GPL |

We do not bundle or modify any of this code; each workflow is a JSON description that calls nodes by
name. Validated against ComfyUI 0.37.0 with the pack revisions current in September 2026.

## 2. Models the installer downloads

`install_models.py` downloads each file from the repository below and checks its exact size and
SHA-256. "Official" means published by the model's creator or by Comfy-Org as a ComfyUI repackage;
"community" means a third-party conversion of the official weights, which remains under the original
model licence.

| file | repository | publisher | licence |
|---|---|---|---|
| gemma4-12b-with-proj-ltx-2.5-comfy-int8-convrot.safetensors | Lightricks/LTX-2.5 | official | LTX-2.x Community |
| ltx-2.5-video-vae-conv-bf16.safetensors | Lightricks/LTX-2.5 | official | LTX-2.x Community |
| ltx-2.5-audio-vae-bf16.safetensors | Lightricks/LTX-2.5 | official | LTX-2.x Community |
| ltx-2.5-latent-spatial-upscaler-x2-bf16-1.0.safetensors | Lightricks/LTX-2.5 | official | LTX-2.x Community |
| ltx-2.5-22b-distilled-transformer-comfy-int8-convrot.safetensors (optional) | Lightricks/LTX-2.5 | official | LTX-2.x Community |
| LTX-2.5-Distilled-Q3_K_M / Q4_K_M / Q6_K .gguf | Abiray/LTX-2.5-Distilled-GGUF | community | LTX-2.x Community |
| krea2_turbo_int8_convrot / krea2_turbo_fp8_scaled | Comfy-Org/Krea-2 | official repackage | Krea 2 Community |
| qwen3vl_4b_fp8_scaled.safetensors | Comfy-Org/Krea-2 | official repackage | Krea 2 Community (repackage) |
| qwen_image_vae.safetensors | Comfy-Org/Krea-2 | official repackage | Krea 2 Community (repackage) |

Exact sizes and SHA-256 hashes are inside `install_models.py`. Run
`python install_models.py --comfy <your ComfyUI> --list` to see them with the licence for each.

## 3. Model licences - what to know before you use the outputs

### LTX-2.x Community License (Lightricks) - LTX-2.5, workflows 01, 02, 03
Text: https://github.com/Lightricks/LTX-2/blob/main/LICENSE-2_x (licence date 11 Aug 2026)
- **Free for any purpose, including commercial**, for individuals and companies with **under
  $10,000,000 annual revenue** (counted with affiliates). At or above that, a paid commercial licence
  is required (contact Lightricks).
- Lightricks claims **no rights in your outputs** (s.5).
- **Restriction that affects commercial output:** Attachment A item 5 - you may not place generated
  content in any context "without expressly and intelligibly disclaiming that the information and/or
  content is machine generated". **Label your LTX videos as AI-generated where you publish them.**
- You must not remove or circumvent watermarking, content-provenance or latent-disclosure features
  (s.6, Attachment A item 19), and must follow the Acceptable Use Policy (no deepfakes of real people
  without consent, no harassment, no deception, etc.).
- Attachment A item 20: no use in a product or service that directly competes with Lightricks'
  commercial offerings without a separate licence. Item 18: commercial users may not use it to train
  other models except LTX derivatives.
- The weights are **gated** on Hugging Face: log in and accept the licence on the model page first.

### Krea 2 Community License - workflow 04
Text: https://huggingface.co/krea/Krea-2-Turbo/blob/main/LICENSE.pdf (v1, 22 Jun 2026)
- **Commercial use of the model and of its outputs only if your company-wide annual revenue is under
  $1,000,000** (trailing 12 months, affiliates included). Above that, an enterprise licence is needed.
- You own your outputs (s.5.3). You must implement reasonable content filtering for your deployment
  (s.4.2) and disclose AI generation where law or platform policy requires (s.4.3). Krea may
  terminate the licence on 30 days' notice (s.9.2).

## 4. Credits
- Workflow design, graphs, notes and scripts: Kanto Labs.
- The LTX two-stage recipe (8-step distilled sigma schedule, x2 latent upscale, 3-step refine) uses the
  sampling parameters published for the distilled model by Lightricks and in ComfyUI's LTX-2.5 support.
- Node, model and product names belong to their owners. Kanto Labs is not affiliated with or endorsed
  by Lightricks, Krea, Comfy-Org or any author above.
