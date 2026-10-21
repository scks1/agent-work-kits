# Self-Audit Checklist: The PDFs a Small Municipality Publishes

Prepared by Árbol, an AI assistant.

Run this checklist against your own document inventory. It assumes a
small staff, free tools where possible, and documents produced in Word
or a meeting platform and posted as PDFs. It is a readiness aid, not a
compliance determination.

## Phase 0 — Set up (once)

- [ ] Name one person as document-accessibility owner. Every later
      step has an owner or it does not happen.
- [ ] Write down your entity's compliance date (see
      `01-rule-explainer.md`): April 26, 2027 if your total population
      is 50,000 or more; April 26, 2028 if under 50,000 or you are a
      special district government.
- [ ] Install the test tools:
  - **veraPDF** (free, open source; Windows/macOS/Linux) — validates a
    PDF against the PDF/UA-1 profile, the machine-checkable core of
    accessible PDF. This kit's sample report uses veraPDF 1.30.3.
  - **PAC (PDF Accessibility Checker)** (free; Windows) — checks
    PDF/UA and WCAG machine criteria and adds a visual
    screen-reader-preview and logical-structure view. A PAC-style pass
    complements veraPDF: where the two disagree, read both reports
    before deciding.
  - **Your office suite's built-in checker** (e.g., Microsoft Word's
    Check Accessibility) — run *before* export, where fixes are
    cheapest.
  - A PDF inspector for metadata (title, language, tagged flag) —
    your PDF reader's document properties will show most of it.
- [ ] Create a results log (spreadsheet is fine) with the columns in
      Phase 6. You will re-test; keep the history.

## Phase 1 — Inventory what you actually publish

Walk every place documents live, not just the website menu:

- [ ] Agenda center / meeting portal (agendas, packets, minutes)
- [ ] Clerk's pages (notices, ordinances, election information)
- [ ] Finance (budgets, audit reports, tax forms, fee schedules)
- [ ] Departments (applications, permits, program flyers, reports)
- [ ] Vendor platforms that post for you (meeting management,
      payment, permitting, recreation) — these are your responsibility
      under the rule even though a vendor operates them.

For each document or document series, record: title, location (URL),
owning department, date posted, format, and **whether residents use it
to apply for, access, or participate in a service**. That last column
decides most exception questions later.

Group the inventory into series (e.g., "Select Board agendas, 2024–")
rather than individual files wherever a series shares a template —
you will sample within series, not test every file ever posted.

## Phase 2 — Prioritize

In this order:

1. **Forms and applications residents must use.** Fillable forms are
   the highest-stakes documents you publish; an inaccessible form can
   block a service outright.
2. **Current agendas, minutes, budgets, and notices** — high traffic,
   posted continuously, and outside every exception once posted after
   your compliance date.
3. **Documents still in active use from before the date** — they lose
   the preexisting-documents exception precisely because they are used.
4. **Reference and archive material** — move what genuinely qualifies
   into a clearly separated archive area before your date (see the
   archived-content exception's four conditions in the explainer), and
   leave everything else in the remediation queue.

## Phase 3 — Sample

- [ ] From each series, pull a sample: the most recent item, one from
      mid-series, and the most complex item (longest, most tables,
      most scanned pages). Template-driven series usually fail or pass
      as a family — three items tell you which.
- [ ] Add every fillable form, regardless of sampling; forms are few
      and each is a service doorway.
- [ ] Save an untouched copy of each sample as the **before** state,
      with its source URL and retrieval date. Never remediate your
      only copy.

## Phase 4 — Test each sample

Automated pass first, then human checks. Automated tools cannot judge
reading order sanity, alt-text quality, or whether a heading structure
makes sense — budget the ten minutes.

**Machine checks (veraPDF PDF/UA-1 profile, or PAC):**

- [ ] File is **tagged** (has a structure tree). An untagged PDF fails
      at the door; scanned-image PDFs are untagged by construction.
- [ ] **Document title** is set in metadata, and the viewer is set to
      display it (DisplayDocTitle). An empty title is the single most
      common failure in real municipal PDFs.
- [ ] **Document language** is set.
- [ ] The file declares **PDF/UA identification** in its metadata if
      it is offered as a conforming file.
- [ ] Every **image/figure has alt text** (or is marked as a decorative
      artifact). Empty alt text on a real image fails.
- [ ] Every **link has a descriptive text or Contents description** —
      "click here" and bare URLs fail readers even when they pass
      some checkers.
- [ ] **Fonts are embedded.** Unembedded fonts are a frequent export
      failure and break text extraction downstream.
- [ ] **Tables** have header cells (TH), data cells (TD), rows that
      contain only cells, and a consistent column count. Word tables
      pasted from spreadsheets are the usual offender.
- [ ] **No artifact/tag nesting errors** (content marked as artifact
      inside tagged content or vice versa) — these come from the
      export tool and usually mean "fix the source, re-export," not
      "repair the PDF."
- [ ] Form fields (if any) have **tooltips/descriptions**, a logical
      **tab order**, and are tagged.

**Human checks (no tool substitutes):**

- [ ] Read the document through with the text-extraction or
      screen-reader preview order: does it read in the order a person
      would read the page? Multi-column layouts and text boxes are
      where order breaks.
- [ ] Check the heading outline: does it match the document's real
      sections, in order, without skipped levels doing structural work?
- [ ] Follow every link: does its text say where it goes?
- [ ] If the document contains a table, confirm a reader can tell
      which row and column headers govern each cell.
- [ ] Contrast and legibility of any stamped, scanned, or
      image-only pages; a scan that OCR was run on is not thereby
      tagged or readable in order.

**By document type, add:**

- *Agendas/minutes:* the meeting platform's export settings are the
  whole game — test the platform's output once per template change,
  not once per meeting. Confirm the packet attachments inherit the
  same scrutiny as the agenda itself.
- *Budgets:* expect the worst table findings here. Wide financial
  tables need real header rows and columns; a budget that cannot be
  linearized should also be published as an accessible spreadsheet or
  HTML table.
- *Forms:* test with keyboard only — tab through, fill, and submit.
  A form that validates in a checker but cannot be completed by
  keyboard has not been tested.
- *Notices:* short documents; the common failures are a missing title,
  an image-only posting (a photo of a paper notice), and a scanned
  signature page appended to a born-digital file, silently making the
  tail of the document image-only.

## Phase 5 — Fix at the source, then re-export

- [ ] Fix in Word/the source system first: use heading styles, list
      styles, and table tools instead of direct formatting; add alt
      text when inserting images; set the document title in file
      properties; mark the header row in tables.
- [ ] Export with the tagged-PDF option (in Word: the PDF export's
      "document structure tags for accessibility" setting).
- [ ] Reserve PDF-level repair tools (tagging, reading-order, and
      metadata fixes in a PDF editor) for documents whose source is
      gone — vendor exports, signed records — and record that the fix
      is a repair, with the before/after validator reports attached.
- [ ] A metadata-level repair pass (title, DisplayDocTitle, PDF/UA
      identification, link descriptions, image alt text) is cheap and
      real, and `03-sample-report.md` shows one: it cleared 5 of 11
      failed rules on the sample agenda. It does not touch structural
      failures — unembedded fonts, broken tables, artifact nesting —
      which require regeneration from source.

## Phase 6 — Verify and record

For every remediated document:

- [ ] Re-run the same validator profile on the new file; save the
      report next to the before report.
- [ ] Record: document, URL, before result (validator, profile,
      version, failed rules/checks), what was changed, after result,
      date, and who checked.
- [ ] Post the remediated file at the same URL where possible, so
      existing links land on the accessible version.
- [ ] Keep a short public accessibility statement with a contact for
      alternate-format requests — the underlying ADA duty to provide
      effective communication applies to excepted and remediated
      documents alike.

## Standing habits (so this does not regress)

- [ ] New templates get a Phase 4 pass before first use.
- [ ] Vendor contracts for meeting, web, permitting, and payment
      platforms state that posted content must meet WCAG 2.1 AA, and
      you test one vendor export per quarter.
- [ ] Born-digital first: no image-only postings of documents that
      exist as text anywhere in your systems.
- [ ] Re-run Phase 3 sampling on your top series annually.

Prepared by Árbol, an AI assistant. Tool and rule references:
`sources/SOURCES.md` and `01-rule-explainer.md`.
