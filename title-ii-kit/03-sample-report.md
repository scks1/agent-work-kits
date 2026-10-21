# Sample Report: One Real Agenda, Before and After

Prepared by Árbol, an AI assistant.

This report runs the checklist in `02-self-audit-checklist.md` against
one real, currently published municipal PDF. Everything below is
measured from the file itself or from the validator output preserved
in `sample/`. Nothing was sent to the town; this is a local worked
example for the kit.

## The document

| | |
| --- | --- |
| Document | Select Board Meeting Agenda — Town of Westford, Massachusetts — Tuesday, October 13, 2026, 6:45 PM, Town Hall Meeting Room, 55 Main Street |
| Source | The Town of Westford's Agenda Center: https://www.westfordma.gov/AgendaCenter/ViewFile/Agenda/_10132026-6982 |
| Retrieved | October 21, 2026 |
| File | PDF 1.5, 5 pages, 54,733 bytes |
| SHA-256 (before) | `2acd5c403d9155ed76dc32f95d7c4662adf25fd49505b3dbe0afc4a3e76bb01e` |
| Producer | Acrobat PDFMaker 11 for Word / Adobe PDF Library 11.0 (created October 8, 2026) |
| Validator | veraPDF 1.30.3, PDF/UA-1 validation profile (ISO 14289-1:2014) |

The before file is preserved as
`sample/westford-ma-select-board-agenda-2026-10-13-before.pdf`, and
the full validator output as `sample/verapdf-ua1-before.xml`.

## Before state — what inspection found

The good base, first: this is a born-digital, **tagged** PDF with the
document language set (EN-US), marked content present, and a bookmark
("SELECT BOARD"). Its producer chain (Word → PDFMaker) is exactly what
most small towns use, and it clears most of the bar.

**veraPDF verdict: not compliant with PDF/UA-1.** 95 rules passed,
**11 rules failed**; 22,604 checks passed, **64 checks failed**.

| # | ISO 14289-1 clause | Failed checks | Finding, in plain terms |
| --- | --- | ---: | --- |
| 1 | 7.1, test 2 | 18 | Tagged content sits inside content marked as an artifact (export-level structure conflict). |
| 2 | 7.1, test 1 | 18 | Content marked as artifact sits inside tagged content (the same conflict, other direction). |
| 3 | 7.2, test 10 | 9 | Table rows contain paragraph elements instead of only header/data cells (TH/TD). |
| 4 | 7.21.4.1, test 1 | 6 | Font programs used by the document are not embedded. |
| 5 | 7.18.1, test 2 | 4 | Link annotations have neither a Contents description nor an enclosing alt entry. |
| 6 | 7.18.5, test 2 | 4 | Links lack an alternate description in their Contents key. |
| 7 | 7.3, test 1 | 1 | The one figure — the town seal in the header — has an **empty** alt text. |
| 8 | 7.1, test 10 | 1 | No ViewerPreferences with DisplayDocTitle; the document **title metadata is empty**, so assistive tech and search results have no title to announce. |
| 9 | Clause 5, test 1 | 1 | The metadata carries no PDF/UA identification schema. |
| 10 | 7.2, test 42 | 1 | Table rows span different numbers of columns. |
| 11 | 7.21.4.2, test 2 | 1 | A CIDSet entry does not identify all glyphs in an embedded font subset. |

The four undescribed links are real content links: the Zoom webinar
registration for the meeting and a Special Town Meeting attendance
survey (page 1), and the WestfordCAT video-on-demand page and the
town's accessibility contact email (page 4).

## Targeted fixes applied (the "after" state)

Five of the eleven failed rules are metadata- and annotation-level
problems that can be repaired directly in the PDF without touching
its content or layout. Using pikepdf, the kit author applied exactly
these changes to a copy of the file:

1. **Document title set** (info dictionary and XMP `dc:title`):
   "Select Board Meeting Agenda — Town of Westford — October 13, 2026".
2. **ViewerPreferences → DisplayDocTitle = true** added.
3. **PDF/UA identification added** to the XMP metadata (`pdfuaid:part
   = 1`, with the required PDF/A extension-schema description).
4. **Contents descriptions added to all four link annotations**, e.g.
   "Register for this meeting on Zoom (webinar registration link)".
5. **Alt text set on the seal figure**: "Town of Westford seal". (The
   image was inspected before writing this: a circular seal showing a
   church with a steeple, lettered "TOWN OF WESTFORD" and
   "INCORPORATED SEPT. 23, 1729".)

The repaired file is
`sample/westford-ma-select-board-agenda-2026-10-13-after-targeted-fixes.pdf`
(SHA-256 `a3bcb561f42e297eabc92a5a3cafb41f5c64d42810e67d317d0a1412ff786b9d`),
with validator output at `sample/verapdf-ua1-after-targeted-fixes.xml`.

**veraPDF verdict after: still not compliant** — and that is the
honest headline. Passed rules rose 95 → **100**; failed rules fell
11 → **6**; failed checks fell 64 → **53**. All five targeted findings
cleared.

## What remains, and what it would take

| Clause | Failed checks | Why a metadata pass cannot fix it |
| --- | ---: | --- |
| 7.21.4.1 (fonts not embedded) | 6 | The font programs are absent from the file; embedding them requires re-export from the Word source with font embedding on, or a preflight tool that can source the exact fonts. |
| 7.1 tests 1–2 (artifact/tag nesting) | 36 | The conflict is baked into the structure tree by the export. The fix is at the source/export settings, not in the PDF. |
| 7.2 tests 10 & 42 (table structure) | 10 | The agenda's table needs real header/data cell structure and consistent columns — a source-document fix in Word's table tools, then re-export. |
| 7.21.4.2 (CIDSet) | 1 | A font-subsetting defect from the original export. |

So the worked example lands where most real remediation lands: the
cheap layer (title, identification, link descriptions, image alt) is
an afternoon's work across a whole inventory; the structural layer is
a source-and-template fix — fix the Word template and export settings
once, and every future agenda inherits the fix.

## Limits of this report

- One validator (veraPDF, PDF/UA-1 profile) was run. No PAC run was
  performed, and **no screen-reader testing was performed** — there is
  no screen reader on the machine that produced this kit, so
  screen-reader behavior is recorded as *not tested*, not as passed.
- A PDF/UA-1 pass would not by itself prove WCAG 2.1 AA conformance or
  legal compliance; this file does not pass, and no such claim is made
  for either state.
- The "after" file is the kit author's local repair of a public
  document, made to demonstrate the workflow. It is not a Town of
  Westford publication.

Prepared by Árbol, an AI assistant.
