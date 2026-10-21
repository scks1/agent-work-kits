#!/usr/bin/env python3
"""Self-test for acx_check.py.

Synthesizes (NumPy -> WAV -> ffmpeg MP3 encode at 192 kbps CBR, 44.1 kHz,
mono) one compliant chapter file and four files that each carry exactly one
deliberate defect, then runs the checker CLI on each and asserts that the
compliant file passes and each defect is caught by its named check.

Cases:
  compliant     should PASS every check
  wrong_rms     overall RMS pulled ~8 dB low        -> rms_level FAIL
  hot_peak      a 60 ms burst at about -1.4 dBFS    -> peak_level FAIL
  high_noise    white noise at -50 dBFS throughout  -> noise_floor FAIL
  long_head     2.5 s of extra head room tone       -> head_room_tone FAIL

Run:  python self_test.py
Exit: 0 if every expectation holds, 1 otherwise.
Built by Arbol, an AI assistant.
"""

from __future__ import annotations

import json
import math
import subprocess
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
OUT = HERE / "selftest_output"
SR = 44_100
rng = np.random.default_rng(20261021)


def noise(n: int, rms_db: float) -> np.ndarray:
    amp = 10 ** (rms_db / 20.0)
    return rng.standard_normal(n).astype(np.float64) * amp


def room_tone(seconds: float, rms_db: float = -70.0) -> np.ndarray:
    return noise(int(seconds * SR), rms_db)


def narration(seconds: float) -> np.ndarray:
    """Speech-like phrases: modulated sine bursts over room-tone pauses."""
    n = int(seconds * SR)
    t = np.arange(n) / SR
    out = room_tone(seconds)
    pos = 0.0
    while pos < seconds - 0.6:
        dur = 0.8
        seg = int(dur * SR)
        start = int(pos * SR)
        tt = t[start:start + seg]
        env = 0.5 - 0.5 * np.cos(2 * np.pi * (tt - tt[0]) / dur)  # Hann-ish
        tone = np.sin(2 * np.pi * 170 * tt) + 0.4 * np.sin(2 * np.pi * 340 * tt)
        out[start:start + seg] += (tone * env * 0.16)
        pos += dur + 0.35
    return out


def scale_to_rms(x: np.ndarray, target_db: float) -> np.ndarray:
    rms = float(np.sqrt(np.mean(x**2)))
    return x * (10 ** (target_db / 20.0) / rms)


def build_compliant() -> np.ndarray:
    head = room_tone(0.7)
    body = narration(4.3)
    tail = room_tone(2.0)
    sig = np.concatenate([head, body, tail])
    sig = scale_to_rms(sig, -20.5)
    peak = float(np.max(np.abs(sig)))
    assert 20 * math.log10(peak) <= -5.0, f"compliant peak too hot: {peak}"
    return sig


def encode_mp3(samples: np.ndarray, path: Path) -> None:
    wav = path.with_suffix(".wav")
    pcm = np.clip(samples, -1.0, 1.0)
    pcm16 = (pcm * 32767).astype("<i2")
    subprocess.run(
        ["ffmpeg", "-v", "error", "-y", "-f", "s16le", "-ar", str(SR),
         "-ac", "1", "-i", "-", str(wav)],
        input=pcm16.tobytes(), check=True)
    subprocess.run(
        ["ffmpeg", "-v", "error", "-y", "-i", str(wav),
         "-codec:a", "libmp3lame", "-b:a", "192k", "-ar", str(SR), "-ac", "1",
         str(path)], check=True)
    wav.unlink()


def run_checker(case_dir: Path) -> dict:
    proc = subprocess.run(
        [sys.executable, str(HERE / "acx_check.py"), str(case_dir)],
        capture_output=True, text=True)
    report = json.loads((case_dir / "acx-report.json").read_text())
    report["_exit"] = proc.returncode
    return report


def checks_by_name(report: dict) -> dict:
    return {c["name"]: c for c in report["files"][0]["checks"]}


def main() -> int:
    OUT.mkdir(exist_ok=True)
    base = build_compliant()

    cases: dict[str, tuple[np.ndarray, str | None]] = {}
    cases["compliant"] = (base, None)

    cases["wrong_rms"] = (base * 10 ** (-8.0 / 20.0), "rms_level")

    hot = base.copy()
    burst_at = int(2.0 * SR)
    tt = np.arange(int(0.06 * SR)) / SR
    hot[burst_at:burst_at + len(tt)] += 0.85 * np.sin(2 * np.pi * 440 * tt)
    cases["hot_peak"] = (hot, "peak_level")

    cases["high_noise"] = (base + noise(len(base), -50.0), "noise_floor")

    long_head = np.concatenate([room_tone(2.5, -70.0) * (np.std(base[:100]) / np.std(room_tone(1))), base])
    # keep the prepended tone at the same floor as the file's own room tone
    floor_amp = float(np.sqrt(np.mean(base[: int(0.5 * SR)] ** 2)))
    long_head[: int(2.5 * SR)] = noise(int(2.5 * SR), 20 * math.log10(floor_amp))
    cases["long_head"] = (long_head, "head_room_tone")

    failures = []
    for name, (sig, expect_fail) in cases.items():
        case_dir = OUT / name
        case_dir.mkdir(exist_ok=True)
        mp3 = case_dir / f"{name}.mp3"
        encode_mp3(sig, mp3)
        report = run_checker(case_dir)
        checks = checks_by_name(report)
        status = report["files"][0]["status"]
        if expect_fail is None:
            ok = status == "PASS" and report["_exit"] == 0
            detail = f"expected PASS, got {status} (exit {report['_exit']}); " + \
                "; ".join(f"{c['name']}={c['measured']}"
                          for c in report["files"][0]["checks"]
                          if c["status"] == "FAIL")
        else:
            got = checks.get(expect_fail, {}).get("status")
            ok = status == "FAIL" and got == "FAIL" and report["_exit"] == 1
            detail = (f"expected {expect_fail} FAIL, got {got}; file status {status}; "
                      f"measured={checks.get(expect_fail, {}).get('measured')}")
        print(f"{'PASS' if ok else 'FAIL'}  self-test case {name:<12} {detail if not ok else ''}")
        if not ok:
            failures.append(name)

    print()
    if failures:
        print(f"SELF-TEST FAILED: {failures}")
        return 1
    print("SELF-TEST PASSED: compliant file passes; all 4 deliberate defects caught "
          "by their named checks.")
    print(f"Artifacts: {OUT} (per-case .mp3 + acx-report.json/.txt)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
