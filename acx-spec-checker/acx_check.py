#!/usr/bin/env python3
"""ACX audiobook spec checker.

Measures a directory of chapter files against the measurable subset of the
ACX audio submission requirements and emits a per-file PASS/FAIL report
(JSON + readable text).

Spec source (verified 2026-10-21):
  ACX Help Center, "What are the ACX audio submission requirements?"
  https://help.acx.com/s/article/what-are-the-acx-audio-submission-requirements

Checks implemented (per file):
  format_mp3          file is MP3 (ACX upload format is MP3 only)
  sample_rate         44,100 Hz
  bitrate_cbr         >= 192 kbps and constant bit rate (packet-size test)
  rms_level           overall RMS between -23 and -18 dBFS
  peak_level          peak no higher than -3 dBFS
  noise_floor         estimated noise floor no higher than -60 dBFS RMS
  duration            no longer than 120 minutes (7,200 s)
  head_room_tone      leading room tone within configured limits
  tail_room_tone      trailing room tone within configured limits

Batch check:
  channel_consistency all files mono or all files stereo (ACX requirement)

Measurement method:
  Files are decoded with ffmpeg to 32-bit float PCM and measured with NumPy
  (overall RMS, sample peak, windowed RMS) -- the same sample-domain RMS
  approach this workspace's podcast pipeline uses. The noise floor is an
  estimate: the median RMS of the quietest 10% of 100 ms windows. Head/tail
  room tone is the leading/trailing run of windows that stay within 12 dB
  of that estimated floor (and below -45 dBFS).

Not measured (out of scope, see README): performance, pronunciation,
editing quality, mouth clicks / plosives / pops as a perceptual judgement,
chapter-content correctness, opening/closing credit wording.

Built by Arbol, an AI assistant.
"""

from __future__ import annotations

import argparse
import json
import math
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np

SPEC = {
    "source": "ACX Help Center - What are the ACX audio submission requirements?",
    "url": "https://help.acx.com/s/article/what-are-the-acx-audio-submission-requirements",
    "verified": "2026-10-21",
    "rms_min_db": -23.0,
    "rms_max_db": -18.0,
    "peak_max_db": -3.0,
    "noise_floor_max_db": -60.0,
    "sample_rate_hz": 44100,
    "min_bitrate_bps": 192_000,
    "max_duration_s": 7200.0,
    # ACX's current help page recommends 1-5 s of room tone at the beginning
    # and end of each file and caps room tone at 5 s. The widely used ACX
    # production guidance narrows the head to 0.5-1 s. Defaults below follow
    # that production guidance (head 0.5-1.0 s, tail 1.0-5.0 s); every limit
    # is overridable on the command line. See README "Spec notes".
    "head_min_s": 0.5,
    "head_max_s": 1.0,
    "tail_min_s": 1.0,
    "tail_max_s": 5.0,
}

AUDIO_EXTS = {".mp3", ".wav", ".flac", ".m4a", ".ogg", ".aac"}
SILENCE_ABS_MAX_DB = -45.0  # windows louder than this are never "room tone"
WINDOW_S = 0.100


@dataclass
class Check:
    name: str
    status: str  # PASS | FAIL
    measured: object
    requirement: str

    def as_dict(self):
        return {
            "name": self.name,
            "status": self.status,
            "measured": self.measured,
            "requirement": self.requirement,
        }


@dataclass
class FileResult:
    path: str
    checks: list = field(default_factory=list)
    error: str | None = None

    @property
    def passed(self) -> bool:
        return self.error is None and all(c.status == "PASS" for c in self.checks)

    def as_dict(self):
        return {
            "file": self.path,
            "status": "PASS" if self.passed else "FAIL",
            "error": self.error,
            "checks": [c.as_dict() for c in self.checks],
        }


def run(cmd: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, capture_output=True, check=False)


def probe(path: Path) -> dict:
    """ffprobe JSON for the first audio stream + format block."""
    out = run(
        [
            "ffprobe", "-v", "error", "-select_streams", "a:0",
            "-show_entries",
            "stream=codec_name,sample_rate,channels,bit_rate:"
            "format=duration,bit_rate,format_name",
            "-of", "json", str(path),
        ]
    )
    if out.returncode != 0:
        raise RuntimeError(out.stderr.decode("utf-8", "replace").strip()[:400])
    return json.loads(out.stdout.decode())


def decode_samples(path: Path) -> tuple[np.ndarray, int]:
    """Decode to float32 PCM with ffmpeg; return (samples[n, ch], sample_rate)."""
    info = probe(path)
    stream = info["streams"][0]
    sr = int(stream["sample_rate"])
    out = run(
        [
            "ffmpeg", "-v", "error", "-i", str(path),
            "-f", "f32le", "-acodec", "pcm_f32le", "-",
        ]
    )
    if out.returncode != 0:
        raise RuntimeError(out.stderr.decode("utf-8", "replace").strip()[:400])
    samples = np.frombuffer(out.stdout, dtype=np.float32)
    ch = int(stream.get("channels") or 1)
    if ch > 1:
        samples = samples[: (len(samples) // ch) * ch].reshape(-1, ch)
    else:
        samples = samples.reshape(-1, 1)
    return samples, sr


def dbfs(value_linear_rms: float) -> float:
    if value_linear_rms <= 0:
        return -120.0
    return 20.0 * math.log10(value_linear_rms)


def window_rms_db(samples: np.ndarray, sr: int) -> np.ndarray:
    """RMS (dBFS) per non-overlapping 100 ms window, all channels combined."""
    win = max(1, int(sr * WINDOW_S))
    n = (len(samples) // win) * win
    if n == 0:
        return np.array([])
    blocks = samples[:n].reshape(-1, win, samples.shape[1])
    rms = np.sqrt(np.mean(blocks.astype(np.float64) ** 2, axis=(1, 2)))
    with np.errstate(divide="ignore"):
        out = 20.0 * np.log10(np.where(rms > 0, rms, 1e-9))
    return out


def edge_room_tone_s(win_db: np.ndarray, noise_floor_db: float, from_start: bool) -> float:
    """Duration of the leading/trailing run of room-tone windows."""
    threshold = min(noise_floor_db + 12.0, SILENCE_ABS_MAX_DB + 12.0)
    threshold = max(threshold, noise_floor_db + 6.0)
    seq = win_db if from_start else win_db[::-1]
    count = 0
    for v in seq:
        if v <= threshold:
            count += 1
        else:
            break
    return count * WINDOW_S


def mp3_is_cbr(path: Path) -> tuple[bool | None, str]:
    """CBR test from MP3 packet sizes (CBR frames differ only by the padding
    byte, so sampled packet sizes span at most a couple of bytes). Returns
    (is_cbr or None if undeterminable, note)."""
    out = run(
        [
            "ffprobe", "-v", "error", "-select_streams", "a:0",
            "-show_entries", "packet=size", "-of", "csv=p=0", str(path),
        ]
    )
    if out.returncode != 0:
        return None, "packet probe failed"
    sizes = [int(x) for x in out.stdout.decode().split() if x.strip().isdigit()]
    if len(sizes) < 20:
        return None, "too few packets to judge"
    sample = sizes[:2000]
    span = max(sample) - min(sample)
    return span <= 4, f"packet size span {span} B over {len(sample)} packets"


def check_file(path: Path, limits: dict) -> FileResult:
    res = FileResult(path=str(path))
    try:
        info = probe(path)
        stream = info["streams"][0]
        fmt = info.get("format", {})
        samples, sr = decode_samples(path)
    except Exception as exc:  # unreadable file: a FAIL with the reason kept
        res.error = f"could not read audio: {exc}"
        return res

    flat = samples.astype(np.float64).ravel()
    overall_rms_db = dbfs(float(np.sqrt(np.mean(flat**2))) if flat.size else 0.0)
    peak_db = dbfs(float(np.max(np.abs(flat))) if flat.size else 0.0)
    win_db = window_rms_db(samples, sr)
    if win_db.size:
        quiet = np.sort(win_db)[: max(1, int(math.ceil(len(win_db) * 0.10)))]
        noise_floor_db = float(np.median(quiet))
    else:
        noise_floor_db = -120.0
    duration_s = len(samples) / float(sr)
    channels = int(stream.get("channels") or samples.shape[1])
    codec = (stream.get("codec_name") or "").lower()
    bitrate = int(stream.get("bit_rate") or fmt.get("bit_rate") or 0)
    head_s = edge_room_tone_s(win_db, noise_floor_db, True) if win_db.size else 0.0
    tail_s = edge_room_tone_s(win_db, noise_floor_db, False) if win_db.size else 0.0

    def add(name, ok, measured, requirement):
        res.checks.append(Check(name, "PASS" if ok else "FAIL", measured, requirement))

    add("format_mp3", codec == "mp3", codec or "unknown",
        "MP3 (ACX accepts MP3 uploads only)")
    add("sample_rate", sr == limits["sample_rate_hz"], sr,
        f"{limits['sample_rate_hz']} Hz")
    if codec == "mp3":
        is_cbr, note = mp3_is_cbr(path)
        add("bitrate_cbr",
            bitrate >= limits["min_bitrate_bps"] and is_cbr is True,
            {"bitrate_bps": bitrate, "cbr": is_cbr, "note": note},
            f">= {limits['min_bitrate_bps']} bps, constant bit rate")
    else:
        add("bitrate_cbr", False,
            {"bitrate_bps": bitrate, "cbr": None, "note": "not an MP3 file"},
            f">= {limits['min_bitrate_bps']} bps, constant bit rate")
    add("rms_level", limits["rms_min_db"] <= overall_rms_db <= limits["rms_max_db"],
        round(overall_rms_db, 2),
        f"{limits['rms_min_db']} to {limits['rms_max_db']} dB RMS")
    add("peak_level", peak_db <= limits["peak_max_db"], round(peak_db, 2),
        f"no higher than {limits['peak_max_db']} dB")
    add("noise_floor", noise_floor_db <= limits["noise_floor_max_db"],
        round(noise_floor_db, 2),
        f"no higher than {limits['noise_floor_max_db']} dB RMS (estimated, see README)")
    add("duration", duration_s <= limits["max_duration_s"], round(duration_s, 2),
        f"no longer than {limits['max_duration_s']:.0f} s (120 minutes)")
    add("head_room_tone",
        limits["head_min_s"] <= head_s <= limits["head_max_s"],
        round(head_s, 2),
        f"{limits['head_min_s']} to {limits['head_max_s']} s of room tone at file head")
    add("tail_room_tone",
        limits["tail_min_s"] <= tail_s <= limits["tail_max_s"],
        round(tail_s, 2),
        f"{limits['tail_min_s']} to {limits['tail_max_s']} s of room tone at file tail")
    # carried for the batch consistency check
    res.checks.append(Check("channels_info", "PASS", channels, "info only"))
    return res


def render_text(report: dict) -> str:
    lines = []
    lines.append("ACX spec check report")
    lines.append(f"Spec: {report['spec']['source']} (verified {report['spec']['verified']})")
    lines.append(f"Directory: {report['directory']}")
    lines.append("")
    for fr in report["files"]:
        lines.append(f"{fr['status']:4}  {Path(fr['file']).name}")
        if fr["error"]:
            lines.append(f"      ERROR: {fr['error']}")
        for c in fr["checks"]:
            if c["name"] == "channels_info":
                continue
            lines.append(
                f"      {c['status']:4}  {c['name']:<18} measured={c['measured']}  "
                f"required: {c['requirement']}"
            )
        lines.append("")
    batch = report["batch"]
    lines.append(f"Batch channel consistency: {batch['channel_consistency']}"
                 f" (channel counts seen: {batch['channel_counts']})")
    if batch["rms_spread_db"] is not None:
        lines.append(
            f"Batch RMS spread across files: {batch['rms_spread_db']} dB "
            "(advisory only -- ACX requires consistent sound but publishes no number)"
        )
    lines.append(f"Overall: {report['summary']['passed']}/{report['summary']['total']} files PASS")
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Check chapter files against the ACX audio spec.")
    ap.add_argument("directory", help="directory containing chapter audio files")
    ap.add_argument("--out-json", default=None, help="write JSON report here (default: <dir>/acx-report.json)")
    ap.add_argument("--out-text", default=None, help="write text report here (default: <dir>/acx-report.txt)")
    ap.add_argument("--recursive", action="store_true", help="recurse into subdirectories")
    for key in ("head_min_s", "head_max_s", "tail_min_s", "tail_max_s"):
        ap.add_argument("--" + key.replace("_", "-"), type=float, default=SPEC[key],
                        help=f"default {SPEC[key]}")
    args = ap.parse_args(argv)

    root = Path(args.directory)
    if not root.is_dir():
        print(f"not a directory: {root}", file=sys.stderr)
        return 2
    files = sorted(
        p for p in (root.rglob("*") if args.recursive else root.iterdir())
        if p.is_file() and p.suffix.lower() in AUDIO_EXTS
    )
    if not files:
        print(f"no audio files found in {root}", file=sys.stderr)
        return 2

    limits = dict(SPEC)
    for key in ("head_min_s", "head_max_s", "tail_min_s", "tail_max_s"):
        limits[key] = getattr(args, key)

    results = [check_file(p, limits) for p in files]

    channel_counts = []
    rms_values = []
    for r in results:
        for c in r.checks:
            if c.name == "channels_info":
                channel_counts.append(c.measured)
            if c.name == "rms_level" and isinstance(c.measured, (int, float)):
                rms_values.append(c.measured)
    consistent = len(set(channel_counts)) <= 1 if channel_counts else True
    report = {
        "spec": {k: SPEC[k] for k in ("source", "url", "verified")},
        "limits_used": {k: limits[k] for k in (
            "rms_min_db", "rms_max_db", "peak_max_db", "noise_floor_max_db",
            "sample_rate_hz", "min_bitrate_bps", "max_duration_s",
            "head_min_s", "head_max_s", "tail_min_s", "tail_max_s")},
        "directory": str(root),
        "files": [r.as_dict() for r in results],
        "batch": {
            "channel_consistency": "PASS" if consistent else "FAIL",
            "channel_counts": channel_counts,
            "rms_spread_db": (round(max(rms_values) - min(rms_values), 2)
                              if len(rms_values) > 1 else None),
        },
        "summary": {
            "total": len(results),
            "passed": sum(1 for r in results if r.passed),
        },
    }
    # A batch channel mismatch fails the run even if each file passes alone.
    all_ok = all(r.passed for r in results) and consistent

    out_json = Path(args.out_json) if args.out_json else root / "acx-report.json"
    out_text = Path(args.out_text) if args.out_text else root / "acx-report.txt"
    out_json.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    out_text.write_text(render_text(report), encoding="utf-8")
    print(render_text(report))
    print(f"Reports written: {out_json} , {out_text}")
    return 0 if all_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
