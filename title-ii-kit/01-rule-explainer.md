# The ADA Title II Web and Mobile Rule, Explained for Small Municipalities

Prepared by Árbol, an AI assistant.

This explainer summarizes the U.S. Department of Justice's rule on the
accessibility of web content and mobile apps under Title II of the
Americans with Disabilities Act. It is a summary, not legal advice.
The primary source is the Department's own Small Entity Compliance
Guide on ADA.gov, read on October 21, 2026; full citations are in
`sources/SOURCES.md`.

## The rule in one paragraph

On April 24, 2024, the Department of Justice published a final rule
updating its Title II regulations. The rule sets a specific technical
standard — the **Web Content Accessibility Guidelines (WCAG) version
2.1, Level AA**, published by the World Wide Web Consortium (W3C) —
for the web content and mobile apps that state and local governments
provide or make available. "Web content" includes documents: the text,
images, and files a government posts online, including PDFs. Content a
vendor or contractor provides on the government's behalf is the
government's responsibility under the rule.

## Who must comply, and by when

The rule applies to all Title II public entities: states, counties,
municipalities, townships, independent school districts, and special
district governments — and to their departments and agencies, which use
the population of the larger government they belong to.

On April 20, 2026, the Department published an Interim Final Rule
extending the compliance dates. The current dates are:

| Public entity | Compliance date |
| --- | --- |
| Total population of 50,000 or more | **April 26, 2027** |
| Total population of less than 50,000 | **April 26, 2028** |
| Any special district government | **April 26, 2028** |

Details that matter for small entities:

- **What counts as a special district government.** A public entity
  other than a county, municipality, township, or independent school
  district, authorized by state law to provide one function or a
  limited number of designated functions, with enough independence to
  be a separate government — for example a water or sewer board,
  utility district, transit authority, or mosquito abatement district.
  Special districts do not have Census-calculated populations, which is
  why the rule gives them the later date outright.
- **School districts are not special districts.** A city school
  district uses its city's population; a county school district uses
  its county's; an independent school district uses its own population
  estimate from the Census Bureau's Small Area Income and Poverty
  Estimates.
- **Which population figure.** For most governments, the total
  population in the 2020 Census data. A department or agency (a town
  library, a police department) uses the population of the government
  it is part of.
- **The pre-existing duties do not wait for these dates.** Title II has
  always required effective communication, reasonable modifications,
  and an equal opportunity to participate in or benefit from services,
  programs, and activities — including online ones. Those duties apply
  now, before your compliance date, and continue after it, including
  for content an exception covers: an excepted document must still be
  provided in an accessible format when a person with a disability
  needs it.

## What has to meet WCAG 2.1 AA

As a working rule: web content and mobile apps your entity provides or
makes available, including content a contractor posts for you, must
meet WCAG 2.1 Level AA by your compliance date, unless a specific
exception applies. Two flexibility provisions exist: **equivalent
facilitation** (an alternative that provides equal or greater
accessibility and usability) and the long-standing defenses of
**fundamental alteration** and **undue burden**, which are fact-specific
and are determinations for the entity to make with counsel — not boxes
a checklist can tick. A separate accessible version ("conforming
alternate version") is permitted only in very limited circumstances
involving technical or legal limitations.

For documents specifically, WCAG 2.1 AA compliance in practice means a
PDF that is **tagged** (a logical structure tree: headings, paragraphs,
lists, tables in reading order), has a **document title and language**
set, gives **text alternatives** for images and **descriptive text**
for links, embeds its **fonts**, and keeps a reading order that matches
the visual order. The machine-checkable core of this is the PDF/UA
standard (ISO 14289), which is what the validator in this kit tests
against.

## The five exceptions — and their limits

The rule excepts five categories of content from the WCAG 2.1 AA
requirement. Every condition listed must hold; if one fails, the
exception fails. And per the section above, an exception never removes
the duty to provide the content accessibly on request.

1. **Archived web content.** Content that (1) was created before your
   compliance date (or reproduces physical media created before it),
   (2) is kept only for reference, research, or recordkeeping, (3) is
   kept in a designated archive area, and (4) has not been changed
   since it was archived. Minutes created *after* your compliance date
   do not qualify even if filed in the archive area.
2. **Preexisting conventional electronic documents.** Word-processing,
   presentation, PDF, or spreadsheet files that (1) were available on
   your website or app before your compliance date, and (2) are **not
   currently used to apply for, access, or participate in** your
   services, programs, or activities. A 2020 permit application PDF
   that residents still file is *not* excepted.
3. **Third-party content** posted by a third party who is not acting
   under a contract, license, or other arrangement with your entity —
   for example, a resident's post on a town message board. Content your
   vendor posts for you, and the platform itself, are not excepted.
4. **Individualized, password-protected documents** — word-processing,
   presentation, PDF, or spreadsheet files that are about a specific
   person, property, or account and are password-protected or
   otherwise secured (for example, a resident's water bill in a secure
   account portal). The website around them is not excepted.
5. **Preexisting social media posts** made before your compliance date.

Practical consequence for a small town: the archive exception and the
preexisting-documents exception reward **housekeeping done before your
date** — a clearly separated archive area, and an honest inventory of
which old documents are still in active use. Anything you post new, and
anything old that residents still rely on to do business with you, is
in scope.

## Where documents fit

The documents a small municipality publishes every week — agendas,
minutes, budgets, application forms, public notices — are the bulk of
its web content by volume, and they are mostly PDFs. Most are produced
in Word or a meeting-management platform and exported. That is good
news: the accessibility of the PDF is largely decided at export time,
by choices the checklist in `02-self-audit-checklist.md` covers —
styles instead of direct formatting, alt text at insertion, a document
title in the file properties, and a tagged export. The worked example
in `03-sample-report.md` shows what a typical agenda looks like to a
validator and what it takes to fix it.

Prepared by Árbol, an AI assistant. This explainer is general
information about a federal rule, not legal advice for any specific
entity. Sources: `sources/SOURCES.md`.
