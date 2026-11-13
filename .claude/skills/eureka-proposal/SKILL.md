---
name: eureka-proposal
description: Turn a discovery call into a published Eureka proposal page. Use when the team wants to create, draft, scope or price a proposal for a client ("make the proposal for X", "build a proposal from the discovery call", "crea la propuesta para X", "propuesta para"), or to edit, rebuild or publish an existing one in this repo.
---

# Eureka proposal

Turns discovery-call transcripts into a proposal page at `proposals.eureka.ceo/<slug>`, built from this repo's template.

The rule that matters most: **we propose what we believe will help, not a copy of the client's wish list.** Never write the proposal before the team has confirmed the focus, the phases, the prices and the duration.

Talk to the user in the language they use with you. Write the proposal in the client's language (from the transcripts).

## Files you work with

- `proposals/<slug>/proposal.json`: the only file you write per proposal. Schema in `references/content-schema.md`.
- `python3 build.py <slug>`: builds `proposals/<slug>/index.html` and the server data for the accept email.
- `data/team.json`, `data/company.json`: shared team, bank accounts, kickoff link, terms. Don't edit per proposal.
- `references/playbook.md`: what has worked in accepted proposals (structure, pricing, wording). Read it before step 3.
- Never edit `proposals/federico-gonzalez/`. It was hand-built and is already shared with the client.

## Workflow

### 1. Gather the discovery

Ask which client, if the user hasn't said. Then:
- Circleback: `FindProfiles` and `SearchMeetings` with the client's name, then `GetTranscriptsForMeetings` for **every** related meeting (full transcripts, not summaries).
- If the user pasted a transcript or notes, use those too. If nothing is found, ask for it. Don't invent context.

Extract, with evidence (short quotes) from the transcripts:
- Who: name, role, company, team size, location, language, tone.
- Today: tools, how work flows, what's already built.
- Pains, ranked by how often and how strongly they came up.
- What they explicitly asked for.
- Budget and timing signals, objections, decision-makers.
- 1 or 2 quotable phrases in their own words.

### 2. Their ask vs. our criteria (stop and discuss)

Show the user a short read, then two lists side by side:

> **What they asked for** · everything they mentioned
> **What we recommend focusing on** · our call, and why (order, dependencies, what creates value first, what to leave for later)

Propose **one focus sentence** (the North Star: what this project must achieve). Ask the user to agree or adjust. This becomes the `focus` section. Skip that section only if the user says the ask and our recommendation are the same.

### 3. Scope, price and duration (stop and confirm)

Using `references/playbook.md`, propose phases. For each one give the name, tag (`essential`, `recommended` or `optional`), price, weeks and 3 to 6 deliverables. Then show the total, the deposit and the payment schedule.

**Every proposal has one fixed price: all phases are included.** The tag only tells the client how important a phase is; they can't remove phases on the page. If the client later asks to change the scope, the team edits `proposal.json`, rebuilds and republishes.

> **01 · Discovery** · Essential · 1 week · USD 500
> → …
> **Total USD X** · deposit 50% = USD Z
> Should we adjust anything?

Do not continue until the user confirms. Then confirm the details: projected start, valid-until date (default: two weeks from today), deposit % (default 50), payment reference (default `CLIENT-DDMM`), and who prepares it (team ids from `data/team.json`).

### 4. Write the content file

- `slug`: short, lowercase, no client-sensitive words (e.g. `acme`, `nickel-ai`). Ask if unsure.
- Create `proposals/<slug>/proposal.json` following `references/content-schema.md`.
- Write `team_roles` for every person shown: a role and a one or two line description of what they do in this project, tied to its phases. Never leave the generic bios from `data/team.json`.
- Copy rules (always):
  - No em dashes. Use commas, periods or colons.
  - Price first, then the value explanation.
  - Never commit to file volumes, record counts or hours, unless the user explicitly asks to include hours.
  - Pains and quotes come from the transcripts. Use the client's own words where natural.
  - Plain, specific, human. Nothing that sounds generated: no "seamless", "leverage", "unlock", "robust", "streamline", "elevate".
  - Never mention other clients by name in the body (the client grid handles that).
  - Integrations are "defined in the roadmap, subject to technical feasibility", never "included" by default.

### 5. Build and check

```
python3 build.py <slug>
```

Then check it in a browser with Playwright (it is installed):
- No JavaScript errors, no horizontal scroll at 390 px width.
- Every section renders.
- The totals box matches the sum of the phases.
- The accept flow works: the scope list shows every phase and the total; fill name and email, accept, payment details and kickoff link appear.

Show the user screenshots of the cover and the proposal section.

### 6. Preview, then publish

- Create a branch `proposal/<slug>`, commit, push. Vercel builds a preview of the `eureka-proposals` project; share that link for review.
- Apply the user's feedback in `proposal.json` and rebuild. Never hand-edit the generated `index.html`.
- When the user approves, merge to `main` and push. The proposal is live at `https://proposals.eureka.ceo/<slug>`. Open it and confirm it loads.

### 7. Log it

In the Notion Proposals database (data source `65eab1f5-f843-4819-a6b8-7bbfbb5a7d4d`) create or update the row: `Name` = "Proposal <Company> + Eureka", `Status` = `Sent`, `Budget` = total with recommended pieces on. Put the live link in the page body.

Then offer to draft the send email (from the team, in the client's language): one personal line from the call, one or two lines on what the proposal covers, the link, and "accept directly on the page when you're ready".

## Before every publish

- `data/company.json` has `"demo": true` while bank accounts, kickoff link and terms are placeholders. If it's still true, tell the user the page shows demo payment data and don't publish to a real client until they confirm.
- The accept email only sends once the Vercel project has `RESEND_API_KEY`, `EMAIL_FROM` and `TEAM_EMAIL`. If they're missing, the page still works, but say so.
