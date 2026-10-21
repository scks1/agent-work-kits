# Title II Document-Accessibility Readiness Kit for Small Municipalities

Prepared by Árbol, an AI assistant.

**What this kit is.** A practical starting point for a small town or small
public entity that publishes PDFs — meeting agendas, minutes, budgets,
forms, notices — and needs to get those documents ready for the ADA
Title II web and mobile app rule. It explains the rule in plain terms,
gives a self-audit checklist you can run with free tools, and works
through one real municipal agenda PDF end to end, findings included.

**What this kit is not.** It is not legal advice, and it is not a
compliance determination. Only your entity, advised by its own counsel
and accessibility reviewers, can determine that it complies. Automated
validators catch machine-checkable problems; they do not prove a
document is accessible to every reader.

## Contents

| File | What it covers |
| --- | --- |
| `01-rule-explainer.md` | The Title II web/mobile rule: who it covers, the compliance dates, WCAG 2.1 AA, the exceptions, and what the rule does not change. |
| `02-self-audit-checklist.md` | How to inventory, prioritize, sample, and test the PDFs a small municipality actually publishes, using veraPDF and PAC-style checks. |
| `03-sample-report.md` | A worked example on a real public agenda PDF (Town of Westford, MA, Select Board agenda, October 13, 2026): before findings, the targeted fixes that were applied, and the after findings — including what still fails and why. |
| `sources/SOURCES.md` | Every source used, with URLs and the date accessed. |
| `sample/` | The sample PDF (before and after states), its SHA-256 checksum, and the full veraPDF XML reports for both states. |

## The short version

- The U.S. Department of Justice's Title II rule names **WCAG 2.1
  Level AA** as the technical standard for state and local governments'
  web content and mobile apps.
- After an April 2026 extension, the compliance date is **April 26,
  2027** for public entities with a total population of 50,000 or more,
  and **April 26, 2028** for entities under 50,000 and for **any special
  district government**.
- Most municipal PDFs posted after your compliance date — and older
  PDFs still used to apply for, access, or participate in services —
  are in scope. Documents, not just web pages, are where most small
  towns will feel this rule.
- The cheapest fix is upstream: a tagged, properly structured document
  exported from the source file beats a repaired scan every time.
- Even tagged output fails in predictable ways. In the worked example,
  a born-digital, tagged agenda from a town website failed 11 of 106
  PDF/UA-1 rules on its first veraPDF run — missing document title,
  links without descriptions, an image with empty alt text, unembedded
  fonts, and table-structure errors. Five of the eleven failed rules
  were fixable in minutes at the metadata level; the rest need the
  source document fixed and re-exported.

Prepared by Árbol, an AI assistant. Sources: see `sources/SOURCES.md`.
