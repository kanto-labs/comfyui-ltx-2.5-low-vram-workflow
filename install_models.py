#!/usr/bin/env python3
"""
install_models.py - Low-VRAM AI Video Pack (Kanto Labs)

Downloads the model files the pack's workflows need, from the publishers' own
Hugging Face repositories, into the right ComfyUI folders, and verifies every
file by exact byte size AND SHA-256.

This pack ships NO model weights. Every file is fetched from its publisher and
remains under the publisher's licence (summarised in THIRD_PARTY.md). Read the
licences before downloading - both carry conditions that matter for
commercial use.

Requirements: Python 3.8+ (standard library only), enough disk space, and for
LTX-2.5 a free Hugging Face account that has accepted the LTX-2.5 licence on
https://huggingface.co/Lightricks/LTX-2.5 plus a read token.

Examples
  python install_models.py --comfy "C:/ComfyUI" --list
  python install_models.py --comfy "C:/ComfyUI" --workflow 01 --dry-run
  python install_models.py --comfy "C:/ComfyUI" --workflow 01 02 03 --token hf_xxx
  python install_models.py --comfy "C:/ComfyUI" --workflow 04 --yes
  python install_models.py --comfy "C:/ComfyUI" --ltx-quant q6 --workflow 01
  python install_models.py --comfy "C:/ComfyUI" --verify-only --workflow all

The token can also come from the HF_TOKEN environment variable.
Downloads resume: re-run the same command after an interruption.
"""
import argparse
import hashlib
import os
import shutil
import sys
import time
import urllib.error
import urllib.request

MANIFEST = [
    {"key": "ltx_text_encoder", "groups": ["ltx"], "repo": "Lightricks/LTX-2.5", "path": "text_encoders/gemma4-12b-with-proj-ltx-2.5-comfy-int8-convrot.safetensors", "file": "gemma4-12b-with-proj-ltx-2.5-comfy-int8-convrot.safetensors", "folder": "text_encoders", "size": 15372969374, "sha256": "6ce688a0aa98a5fa36a9f1e6c3f42152a498cc2b53ee8c15674c64244f91487f", "license": "ltx", "publisher": "official", "note": "Gemma text encoder, int8 (ComfyUI build)", "hash_source": "modelscope (official Lightricks mirror, size cross-checked with Hugging Face)"},
    {"key": "ltx_video_vae", "groups": ["ltx"], "repo": "Lightricks/LTX-2.5", "path": "vae/ltx-2.5-video-vae-conv-bf16.safetensors", "file": "ltx-2.5-video-vae-conv-bf16.safetensors", "folder": "vae", "size": 1452269922, "sha256": "685b06ee3d9b2039647698fc4ea33175112462fc374e2777312c907897dfce8d", "license": "ltx", "publisher": "official", "note": "LTX video VAE", "hash_source": "modelscope (official Lightricks mirror, size cross-checked with Hugging Face)"},
    {"key": "ltx_audio_vae", "groups": ["ltx"], "repo": "Lightricks/LTX-2.5", "path": "vae/ltx-2.5-audio-vae-bf16.safetensors", "file": "ltx-2.5-audio-vae-bf16.safetensors", "folder": "vae", "size": 364866540, "sha256": "c52733d37f6a7fb7949c3dc0fb468c6cb2169e4d836983a73babb9f0d54837a5", "license": "ltx", "publisher": "official", "note": "LTX audio VAE", "hash_source": "modelscope (official Lightricks mirror, size cross-checked with Hugging Face)"},
    {"key": "ltx_upscaler", "groups": ["ltx", "upscale"], "repo": "Lightricks/LTX-2.5", "path": "latent_upscale_models/ltx-2.5-latent-spatial-upscaler-x2-bf16-1.0.safetensors", "file": "ltx-2.5-latent-spatial-upscaler-x2-bf16-1.0.safetensors", "folder": "latent_upscale_models", "size": 995778752, "sha256": "eb5a71fe4068ee87ccdb1c3aa635e547ca76bd2d30ae20ae889f2c325c0677e8", "license": "ltx", "publisher": "official", "note": "learned x2 spatial latent upscaler", "hash_source": "modelscope (official Lightricks mirror, size cross-checked with Hugging Face)"},
    {"key": "ltx_int8", "groups": ["ltx-int8"], "repo": "Lightricks/LTX-2.5", "path": "diffusion_models/ltx-2.5-22b-distilled-transformer-comfy-int8-convrot.safetensors", "file": "ltx-2.5-22b-distilled-transformer-comfy-int8-convrot.safetensors", "folder": "diffusion_models", "size": 21504034224, "sha256": "c4279eeff115cbeaca494bd2183e7d768c38fe85a184dc6afbb7159157c44334", "license": "ltx", "publisher": "official", "note": "distilled model, int8 (needs UNETLoader instead of the GGUF loader)", "hash_source": "modelscope (official Lightricks mirror, size cross-checked with Hugging Face)"},
    {"key": "ltx_q3", "groups": ["ltx-q3"], "repo": "Abiray/LTX-2.5-Distilled-GGUF", "path": "LTX-2.5-Distilled-Q3_K_M.gguf", "file": "LTX-2.5-Distilled-Q3_K_M.gguf", "folder": "diffusion_models", "size": 12923897280, "sha256": "f593274e67dc0c4714240539c57b76fc6ecac2256fbab9fb32b2a0f72b8d3dea", "license": "ltx", "publisher": "community quantization", "note": "distilled model, GGUF Q3_K_M (workflow default)", "hash_source": "huggingface"},
    {"key": "ltx_q4", "groups": ["ltx-q4"], "repo": "Abiray/LTX-2.5-Distilled-GGUF", "path": "LTX-2.5-Distilled-Q4_K_M.gguf", "file": "LTX-2.5-Distilled-Q4_K_M.gguf", "folder": "diffusion_models", "size": 15687639488, "sha256": "0f51eb0d82b19bddbfb3b0371a65217844ea03750f27dd733528f22152e0e0d0", "license": "ltx", "publisher": "community quantization", "note": "distilled model, GGUF Q4_K_M", "hash_source": "huggingface"},
    {"key": "ltx_q6", "groups": ["ltx-q6"], "repo": "Abiray/LTX-2.5-Distilled-GGUF", "path": "LTX-2.5-Distilled-Q6_K.gguf", "file": "LTX-2.5-Distilled-Q6_K.gguf", "folder": "diffusion_models", "size": 18624033216, "sha256": "ee8835ff8f11e4f59fa4be7bf31b1200172659364e724de444d790ddf4869a58", "license": "ltx", "publisher": "community quantization", "note": "distilled model, GGUF Q6_K", "hash_source": "huggingface"},
    {"key": "krea_int8", "groups": ["krea"], "repo": "Comfy-Org/Krea-2", "path": "diffusion_models/krea2_turbo_int8_convrot.safetensors", "file": "krea2_turbo_int8_convrot.safetensors", "folder": "diffusion_models", "size": 13492686496, "sha256": "8e4eeda70dd5037ab1ba2bef6b417f9f901e26093117cf397f741fc1fdaaf3f1", "license": "krea", "publisher": "official repackage (Comfy-Org)", "note": "Krea 2 Turbo, int8 (RTX 30 series)", "hash_source": "huggingface"},
    {"key": "krea_fp8", "groups": ["krea-fp8"], "repo": "Comfy-Org/Krea-2", "path": "diffusion_models/krea2_turbo_fp8_scaled.safetensors", "file": "krea2_turbo_fp8_scaled.safetensors", "folder": "diffusion_models", "size": 13141730784, "sha256": "eb4dd8c612cfd10f64f25b057e6e6bbcb5737c94a7372177e456dbf7579502f1", "license": "krea", "publisher": "official repackage (Comfy-Org)", "note": "Krea 2 Turbo, fp8 (RTX 40/50 series)", "hash_source": "huggingface"},
    {"key": "krea_text_encoder", "groups": ["krea"], "repo": "Comfy-Org/Krea-2", "path": "text_encoders/qwen3vl_4b_fp8_scaled.safetensors", "file": "qwen3vl_4b_fp8_scaled.safetensors", "folder": "text_encoders", "size": 5242467968, "sha256": "54bd5144df0bbc25dd6ccadfcb826b521445a1b06ae5a42570bdd2974ca87094", "license": "krea", "publisher": "official repackage (Comfy-Org)", "note": "Qwen3-VL-4B text encoder, fp8", "hash_source": "huggingface"},
    {"key": "krea_vae", "groups": ["krea"], "repo": "Comfy-Org/Krea-2", "path": "vae/qwen_image_vae.safetensors", "file": "qwen_image_vae.safetensors", "folder": "vae", "size": 253806246, "sha256": "a70580f0213e67967ee9c95f05bb400e8fb08307e017a924bf3441223e023d1f", "license": "krea", "publisher": "official repackage (Comfy-Org)", "note": "VAE", "hash_source": "huggingface"}
]

LICENSES = {
    "ltx": "LTX-2.x Community License (Lightricks). Free incl. commercial use for entities under "
           "$10M annual revenue; above that a paid licence is required. Outputs must be disclosed as "
           "machine-generated where published; do not remove watermarks/provenance. "
           "https://github.com/Lightricks/LTX-2/blob/main/LICENSE-2_x",
    "krea": "Krea 2 Community License. Commercial use only if your company-wide annual revenue is "
            "under $1M; content-filter and AI-disclosure duties apply. "
            "https://huggingface.co/krea/Krea-2-Turbo/blob/main/LICENSE.pdf",
}

# workflow number -> manifest keys it needs ({q} = LTX quant, {k} = Krea quant)
WORKFLOWS = {
    "01": ["ltx_text_encoder", "ltx_video_vae", "ltx_audio_vae", "ltx_upscaler", "ltx_{q}"],
    "02": ["ltx_text_encoder", "ltx_video_vae", "ltx_audio_vae", "ltx_upscaler", "ltx_{q}"],
    "03": ["ltx_video_vae", "ltx_upscaler"],
    "04": ["krea_{k}", "krea_text_encoder", "krea_vae"],
}

GATED = {"Lightricks/LTX-2.5"}
CHUNK = 8 * 1024 * 1024


def human(n):
    """Decimal units (1 GB = 1,000,000,000 bytes), the same way Hugging Face shows sizes."""
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if n < 1000 or unit == "TB":
            return f"{n:,.1f} {unit}" if unit != "B" else f"{n} B"
        n /= 1000.0


def select(workflows, ltx_quant, krea_quant):
    keys = []
    for w in workflows:
        for k in WORKFLOWS[w]:
            k = k.replace("{q}", ltx_quant).replace("{k}", krea_quant)
            if k not in keys:
                keys.append(k)
    by_key = {m["key"]: m for m in MANIFEST}
    return [by_key[k] for k in keys]


def url_for(m):
    return f"https://huggingface.co/{m['repo']}/resolve/main/{m['path']}"


def sha256_of(path, total):
    h = hashlib.sha256()
    done = 0
    t0 = time.time()
    with open(path, "rb") as f:
        while True:
            b = f.read(CHUNK)
            if not b:
                break
            h.update(b)
            done += len(b)
            if time.time() - t0 > 2:
                print(f"\r    hashing {done * 100 // max(total, 1):3d}%", end="", flush=True)
                t0 = time.time()
    print("\r    hashing 100%", flush=True)
    return h.hexdigest()


def verify(path, m, do_hash=True):
    if not os.path.exists(path):
        return "missing"
    size = os.path.getsize(path)
    if size != m["size"]:
        return f"wrong size ({size:,} bytes, expected {m['size']:,})"
    if do_hash and sha256_of(path, size) != m["sha256"]:
        return "SHA-256 MISMATCH"
    return "ok"


def download(m, dest, token):
    part = dest + ".part"
    have = os.path.getsize(part) if os.path.exists(part) else 0
    if have > m["size"]:
        os.remove(part)
        have = 0
    req = urllib.request.Request(url_for(m), headers={"User-Agent": "kanto-install-models/1.0"})
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    if have:
        req.add_header("Range", f"bytes={have}-")
    try:
        resp = urllib.request.urlopen(req, timeout=60)
    except urllib.error.HTTPError as e:
        if e.code in (401, 403) and m["repo"] in GATED:
            raise SystemExit(
                f"\n  {m['repo']} is gated. 1) open https://huggingface.co/{m['repo']} while logged in and "
                "accept the licence, 2) create a READ token at https://huggingface.co/settings/tokens, "
                "3) re-run with --token hf_xxx (or set HF_TOKEN).")
        raise
    if have and resp.status != 206:  # server ignored the Range header: start over
        have = 0
    mode = "ab" if have else "wb"
    done = have
    t0 = time.time()
    last = t0
    with open(part, mode) as f:
        while True:
            b = resp.read(CHUNK)
            if not b:
                break
            f.write(b)
            done += len(b)
            now = time.time()
            if now - last > 1:
                rate = (done - have) / max(now - t0, 1e-6)
                eta = (m["size"] - done) / max(rate, 1)
                print(f"\r    {done * 100 // m['size']:3d}%  {human(done)} / {human(m['size'])}  "
                      f"{human(rate)}/s  eta {int(eta // 60)}m{int(eta % 60):02d}s   ", end="", flush=True)
                last = now
    print()
    os.replace(part, dest)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--comfy", required=True, help="your ComfyUI folder (the one that contains 'models')")
    ap.add_argument("--workflow", nargs="+", default=["02"],
                    help="workflow numbers to install for: 01 02 03 04, or all")
    ap.add_argument("--ltx-quant", choices=["q3", "q4", "q6", "int8"], default="q3",
                    help="LTX model file: q3 (12.9 GB, workflow default), q4 (15.7 GB), q6 (18.6 GB), "
                         "int8 (21.5 GB, official; switch the loader to UNETLoader)")
    ap.add_argument("--krea-quant", choices=["int8", "fp8"], default="int8",
                    help="int8 for RTX 30 series, fp8 for RTX 40/50 series")
    ap.add_argument("--token", default=os.environ.get("HF_TOKEN", ""), help="Hugging Face read token (LTX-2.5 is gated)")
    ap.add_argument("--list", action="store_true", help="list files, sizes, licences and exit")
    ap.add_argument("--dry-run", action="store_true", help="show what would be downloaded")
    ap.add_argument("--verify-only", action="store_true", help="check existing files, download nothing")
    ap.add_argument("--no-hash", action="store_true", help="size check only (faster, weaker)")
    ap.add_argument("--yes", action="store_true", help="I have read the licences listed; do not ask")
    a = ap.parse_args()

    models_dir = os.path.join(a.comfy, "models")
    if not os.path.isdir(models_dir):
        raise SystemExit(f"'{models_dir}' not found - point --comfy at your ComfyUI folder.")
    wfs = list(WORKFLOWS) if a.workflow == ["all"] else [w.zfill(2) for w in a.workflow]
    for w in wfs:
        if w not in WORKFLOWS:
            raise SystemExit(f"unknown workflow '{w}'. Use 01-04 or all.")
    files = select(wfs, a.ltx_quant, a.krea_quant)

    total = sum(m["size"] for m in files)
    print(f"\nWorkflows: {' '.join(wfs)}   LTX quant: {a.ltx_quant}   Krea quant: {a.krea_quant}")
    print(f"{len(files)} files, {human(total)} in total\n")
    lic_needed = sorted({m["license"] for m in files})
    for m in files:
        dest = os.path.join(models_dir, m["folder"], m["file"])
        state = "present" if os.path.exists(dest) else "to download"
        print(f"  {m['folder'] + '/' + m['file']:<82} {human(m['size']):>10}  [{state}]")
        print(f"      from {m['repo']} ({m['publisher']}) - {m['note']}")
    print("\nLicences that apply to these files (READ THEM - summaries only, not legal advice):")
    for lid in lic_needed:
        print(f"  - {LICENSES[lid]}")
    if a.list or a.dry_run:
        if a.dry_run:
            print("\nURLs:")
            for m in files:
                print("  " + url_for(m))
        return

    if a.verify_only:
        bad = 0
        for m in files:
            dest = os.path.join(models_dir, m["folder"], m["file"])
            print(f"\n  {m['file']}")
            r = verify(dest, m, not a.no_hash)
            print(f"    -> {r}")
            bad += r != "ok"
        raise SystemExit(1 if bad else 0)

    if not a.yes:
        ans = input("\nI have read the licences above and accept them (type yes): ").strip().lower()
        if ans != "yes":
            raise SystemExit("Stopped. Nothing downloaded.")

    need = [m for m in files if not os.path.exists(os.path.join(models_dir, m["folder"], m["file"]))]
    need_bytes = sum(m["size"] for m in need)
    free = shutil.disk_usage(models_dir).free
    if need_bytes > free:
        raise SystemExit(f"Not enough disk space: need {human(need_bytes)}, free {human(free)}.")

    failures = []
    for m in files:
        folder = os.path.join(models_dir, m["folder"])
        os.makedirs(folder, exist_ok=True)
        dest = os.path.join(folder, m["file"])
        print(f"\n{m['file']}  ({human(m['size'])})")
        if os.path.exists(dest):
            r = verify(dest, m, not a.no_hash)
            if r == "ok":
                print("    already present and verified - skipping")
                continue
            print(f"    existing file is not valid ({r}) - moving it aside and downloading again")
            os.replace(dest, dest + ".bad")
        if m["repo"] in GATED and not a.token:
            print(f"    SKIPPED: {m['repo']} is gated - accept the licence on its page and pass --token")
            failures.append(m["file"])
            continue
        download(m, dest, a.token)
        r = verify(dest, m, not a.no_hash)
        print(f"    verify: {r}")
        if r != "ok":
            failures.append(m["file"])
    print()
    if failures:
        print("NOT INSTALLED: " + ", ".join(failures))
        raise SystemExit(1)
    print("All files installed and verified. Restart ComfyUI so it sees the new files.")


if __name__ == "__main__":
    main()
