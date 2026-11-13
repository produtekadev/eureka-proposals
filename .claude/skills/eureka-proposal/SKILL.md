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

Do not continue until the user confirms. Then confirm the details: projected start, valid-until date (default: two weeks from today), deposit % (default 50) and who prepares it (team ids from `data/team.json`).

### 4. Write the content file

- `slug`: short, lowercase, no client-sensitive words (e.g. `acme`, `nickel-ai`). Ask if unsure.
- Create `proposals/<slug>/proposal.json` following `references/content-schema.md`.
- Copy rules (always):
  - No em dashes. Use commas, periods or colons.
  - Price first, then the value explanation.
  - Never commit to file volumes, record counts or hours, unless the user explicitly asks to include hours.
  - Pains and quotes come from the transcripts. Use the client's own words where natural.
  - Plain, specific, human. Nothing that sounds generated: no "seamless", "leverage", "unlock", "robust", "streamline", "elevate".
  - Never mention other clients by name in the body (the client grid handles that).
  - Integrations are "defined in the roadmap, subject to technical feasibility", never "included" by default.
  - Deliverables are concrete things the client receives (a report, a database, a template, a guide, a training session), never qualities or goals ("privacy for your space", "a clear structure"). If something is advice or a plan, make it a deliverable document, e.g. a migration guide.

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

### 7. Log it in Notion (before sharing the link)

The proposal lives in GitHub; its Notion row holds the metadata and is what the team's workflows run on.

- In the Proposals database (data source `65eab1f5-f843-4819-a6b8-7bbfbb5a7d4d`) create the row, or update it if one exists for this client: `Name` = "Proposal <Company> + Eureka", `Status` = `Sent`, `Budget` = total, `Person` = the assigned team (`notion_user_id` from `data/team.json`), `Proposal URL` = `https://proposals.eureka.ceo/<slug>`.
- Copy the row's page id into `proposal.json` as `notion_page_id`, rebuild and push. Without it, accepting on the page can't update Notion.
- When the client accepts, `api/accept.js` sets `Status` = `Accepted`, `Accepted on` and `Accepted by` (needs `NOTION_TOKEN` in Vercel, with the integration connected to the database). It only changes rows that are `Sent`, `Follow Up Sent` or `Follow Up Required`.

Then offer to draft the send email (from the team, in the client's language): one personal line from the call, one or two lines on what the proposal covers, the link, and "accept directly on the page when you're ready".

## Deploy budget (read before pushing)

Vercel's free plan allows 100 deployments a day for the whole team, counted over a rolling 24 hours. On 2026-11-13 a review session hit it in one hour: one push per comment, pushed to two branches, with two Vercel projects building from this repo (4 deploys per edit).

- Group changes. During a review, apply every comment locally, rebuild, and update the review copy as you go; push to `main` once per review round (or when the user asks to see it live), not once per comment.
- Push only to `main` to publish. Pushes to `claude/*` branches don't build (see `proposals/vercel.json`).
- If a push doesn't show up live, check the Vercel deployments list before assuming the code is wrong: a 402 "api-deployments-free-per-day" means the limit, not a bug.

## Before every publish

- `data/company.json` has `"demo": true` while bank accounts, kickoff link and terms are placeholders. If it's still true, tell the user the page shows demo payment data and don't publish to a real client until they confirm.
- The accept email only sends once the Vercel project has `RESEND_API_KEY`, `EMAIL_FROM` and `TEAM_EMAIL`. If they're missing, the page still works, but say so.
