# ACX Spec Checker

Batch-check a folder of audiobook chapter files against the measurable
subset of the ACX audio submission requirements, and get a per-file
PASS/FAIL report with the measured value next to the requirement for every
check.

Built by Árbol, an AI assistant, as an open tool for narrators, producers,
and rights holders who want to catch technical rejections before ACX does.
ACX review delays for fixable level and format problems run to weeks; every
check in this tool runs locally in seconds.

## The spec

Source, verified 2026-10-21: ACX Help Center, "What are the ACX audio
submission requirements?"
https://help.acx.com/s/article/what-are-the-acx-audio-submission-requirements

| Requirement (per file) | ACX limit |
| --- | --- |
| Overall volume | −23 to −18 dB RMS |
| Peak level | no higher than −3 dB |
| Noise floor | no higher than −60 dB RMS |
| Format | MP3, 192 kbps or higher, constant bit rate (CBR) |
| Sample rate | 44.1 kHz |
| File length | no longer than 120 minutes |
| Channels | all files mono, or all files stereo (per book) |
| Room tone | at the beginning and end of each file (see note) |

**Target format.** The checker targets the MP3 submission format because
that is the only format ACX accepts for upload. WAV/FLAC masters are
production intermediates; if you feed them to this tool they will fail the
format check, and the level checks tell you how the master measures before
you encode. Encode at 192 kbps CBR or higher, 44.1 kHz, and check the files
you will actually upload.

**Spec note on room tone.** The ACX help page as fetched on 2026-10-21
recommends 1–5 seconds of room tone at the beginning *and* end of each file
and states room tone must not exceed 5 seconds. Long-standing ACX
production guidance narrows the head to 0.5–1 second. This tool's defaults
follow the production guidance (head 0.5–1.0 s, tail 1.0–5.0 s); all four
limits are command-line options, so you can set `--head-min 1` if you want
to enforce the help page's wording exactly.

## What is measured, and how

Files are probed with ffprobe and decoded with ffmpeg to 32-bit float PCM,
then measured with NumPy in the sample domain:

- **RMS level** — root mean square of all samples, in dBFS.
- **Peak level** — largest absolute sample value, in dBFS. This is sample
  peak, not true (inter-sample) peak.
- **Noise floor** — an estimate: the file is split into 100 ms windows;
  the reported floor is the median RMS of the quietest 10% of windows. On
  real narration, the quietest windows are the room tone. See the limits
  below.
- **Head/tail room tone** — the leading/trailing run of windows that stay
  within 12 dB of the estimated floor; reported in seconds.
- **Bit rate / CBR** — stream bit rate from ffprobe, plus a CBR test on MP3
  packet sizes (CBR frames differ only by the padding byte, so packet sizes
  are near-constant; VBR spreads them widely).
- **Duration, sample rate, channel count** — from ffprobe and the decoded
  stream. Channel consistency is reported as a batch check across the
  whole folder.

## Usage

Requires Python 3.11+, NumPy, and ffmpeg/ffprobe on PATH.

```sh
pip install -r requirements.txt
python acx_check.py /path/to/chapter-files
```

Outputs `acx-report.json` and `acx-report.txt` in the checked directory
(paths overridable with `--out-json` / `--out-text`), prints the text
report, and exits 0 when every file passes, 1 when any file or the batch
channel check fails, 2 on usage errors. Options: `--recursive`,
`--head-min`, `--head-max`, `--tail-min`, `--tail-max`.

Example (from the self-test's compliant file):

```text
PASS  compliant.mp3
      PASS  format_mp3         measured=mp3
      PASS  sample_rate        measured=44100
      PASS  bitrate_cbr        measured=192000 bps, CBR
      PASS  rms_level          measured=-20.77   (required -23.0 to -18.0 dB)
      PASS  peak_level         measured=-9.04    (required no higher than -3.0 dB)
      PASS  noise_floor        measured=-65.58   (required no higher than -60.0 dB)
      PASS  head_room_tone     measured=0.7 s     (required 0.5 to 1.0 s)
      PASS  tail_room_tone     measured=1.9 s     (required 1.0 to 5.0 s)
```

## Self-test

```sh
python self_test.py
```

Synthesizes five MP3s with ffmpeg — one compliant file and four files with
exactly one deliberate defect each — runs the checker on each, and asserts
the defect is caught by its named check:

| Case | Defect | Caught by | Measured |
| --- | --- | --- | --- |
| compliant | — | all pass | RMS −20.77 dB, peak −9.04 dB, floor −65.58 dB |
| wrong_rms | gain pulled −8 dB | `rms_level` | −28.77 dB |
| hot_peak | 60 ms burst ≈ −1.4 dBFS | `peak_level` | −0.21 dB |
| high_noise | white noise at −50 dBFS throughout | `noise_floor` | −50.68 dB |
| long_head | 2.5 s extra head room tone | `head_room_tone` | 3.2 s |

Result on last run (2026-10-21): **all 5 cases pass** — the compliant file
passes every check and each defect is caught. Generated files and reports
are kept under `selftest_output/` so you can inspect them.

## Limits — read this before relying on a PASS

This tool checks the **measurable subset** of the ACX requirements. A PASS
means the numbers are inside the published limits under the measurement
methods above. It does not mean ACX will accept the book:

- **Performance and content are out of scope**: pronunciation, pacing,
  characterization, chapter/section correctness, and whether opening and
  closing credits carry the required wording are not checked.
- **Perceptual defects are out of scope**: ACX also rejects files for
  plosives, microphone pops, mouse clicks, and excessive mouth noise. A
  click loud enough to breach −3 dB will trip the peak check; a quiet one
  will not be detected. No listening judgement is made.
- **The noise floor is an estimate.** With long pauses it reflects room
  tone well; on wall-to-wall loud material with no quiet windows it
  overstates the floor, and on heavily gated/edited audio (silence
  replaced with digital black) it understates it. Treat borderline
  results (within ~2 dB of −60) as "measure the room tone directly."
- **Sample peak, not true peak.** Encoders can create inter-sample peaks
  above the sample peak; keep a margin below −3 dB rather than mastering
  to exactly −3.0 dB.
- **Consistency across chapters** (tone, EQ, microphone sound) is an ACX
  requirement with no published number. The report shows the batch RMS
  spread as advisory information only.
- **Narration eligibility is not this tool's business, but it is ACX's:**
  ACX requires titles to be narrated by a human unless otherwise
  authorized, and prohibits unauthorized text-to-speech/AI recordings.
  This checker measures files; it does not create narration.

## Authorship and licence

Built by Árbol, an AI assistant working for Simon Koch-Sultan, and released
for anyone to use. No warranty: verify borderline files with a second tool
or ACX's own audio analysis tool before submitting a book.
