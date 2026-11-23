---
name: eureka-proposal
description: Turn a discovery call into a published Eureka proposal page. Use when the team wants to create, draft, scope or price a proposal for a client ("make the proposal for X", "build a proposal from the discovery call", "crea la propuesta para X", "propuesta para"), or to edit, rebuild or publish an existing one in this repo.
---

# Eureka proposal

Turns discovery-call transcripts into a proposal page at `proposals.eureka.ceo/<slug>`, built from this repo's template.

The rule that matters most: **we propose what we believe will help, not a copy of the client's wish list.** Never write the proposal before the team has confirmed the goal, the phases, the prices and the duration.

Talk to the user in their language. Write the proposal in the client's language (from the transcripts).

## Files

- `proposals/<slug>/proposal.json`: the only file you write per proposal. Fields in `references/content-schema.md`.
- `python3 build.py <slug>`: builds `proposals/<slug>/index.html` and the accept-email data. Never hand-edit `index.html`.
- `references/playbook.md`: structure, design defaults, prices and wording. Read it before step 3.
- `data/team.json`, `data/company.json`: shared team, bank accounts, terms. Don't edit per proposal.
- Never edit `proposals/federico-gonzalez/` (hand-built, already shared).

## Workflow

### 1. Gather the discovery

Ask which client if not given. In Circleback, `FindProfiles` and `SearchMeetings` with the client's name, then `GetTranscriptsForMeetings` for **every** related meeting (full transcripts). Also use anything the user pasted and the client's page in Notion. If nothing is found, ask. Don't invent context.

Extract, with short quotes: who (name, role, company, team size, location, tone), today's tools and what's already built, pains ranked by how often they came up, what they asked for, budget, timing, decision-makers, and 1 or 2 quotable phrases.

### 2. Their ask vs. our recommendation (stop and discuss)

Show a short read, then two lists: **what they asked for** and **what we recommend** (order, dependencies, what creates value first, what waits). Propose one goal sentence (the North Star) and let the user agree or adjust.

### 3. Scope, price and duration (stop and confirm)

Using the playbook, propose phases: name, tag (`essential`, `recommended`, `optional`), price, weeks, 3 to 6 deliverables. Show the total, deposit and payment schedule. Every phase is in one fixed total; tags only show importance.

Don't continue until the user confirms. Then confirm: projected start, valid-until (default two weeks), deposit % (default 50), and who prepares it (`data/team.json`).

### 4. Write `proposal.json`

`slug`: short, lowercase, nothing sensitive (`acme`, `nickel-ai`). Follow the structure and defaults in the playbook. Copy rules:

- No em dashes. Plain, specific, human: no "seamless", "leverage", "unlock", "robust", "streamline", "elevate".
- Pains and quotes come from the transcripts, in the client's words. Never single out one of their team members.
- Price first, then the value. Never commit to file volumes, record counts or hours unless asked.
- Deliverables are concrete things they receive (a report, a database, a guide, a session), and each title must make sense without its detail.
- Every phase has a `you_do` list ("Your part"): what the client does or decides.
- Integrations are "defined in the roadmap, subject to technical feasibility". Never promise to automate a whole process; map it first and cap the number of agents.
- Never name other clients in the body (the logo grid does that).

### 5. Build and check

Run `python3 build.py <slug>`, then check with Playwright: no JS errors, no horizontal scroll at 390 px, every section renders, totals match the phases, and the accept flow shows every phase, the total, payment details and next steps. Show the user screenshots.

### 6. Card payment link (Stripe)

Once the price is confirmed, create the link in the live **Eureka** Stripe account:

- Amount: `total × deposit_pct / 100 × (1 + card.fee_pct / 100)` (`fee_pct` in `data/company.json`). Example: USD 3,200 at 50% = 1,600 × 1.04 = USD 1,664.
- `PostPrices`: `unit_amount` in cents, `product_data.name` "<Company>: Notion implementation (50% payment)", `metadata.proposal` = slug.
- `PostPaymentLinks` with that price: `metadata.proposal` = slug; `payment_intent_data.description` "<Company> payment (50% of USD <total>)"; hosted confirmation "Thank you! We received your payment and will email you the next steps."; `restrictions.completed_sessions.limit` 2 for a 50/50 split (1 for a single payment); `inactive_message` "Both payments for this project have been received. Contact team@eureka.ceo if you need help."
- Put the URL in `payment.stripe_url` and mention the 4% card option in `payment.schedule`.
- If the total changes: new link, and deactivate the old one (`active: false`, `inactive_message` "This link was replaced. Please use the payment link in your proposal, or contact team@eureka.ceo."). Deploy right after, or the live page points to a dead link.

### 7. Review, then publish

- Publish the built page as a private claude.ai artifact (review copy) for comments. Apply feedback in `proposal.json`, rebuild, update the copy.
- Publish only when the user says so: push to `main`, then confirm `https://proposals.eureka.ceo/<slug>` loads with the changes.

### 8. Log it in Notion

In Proposals (data source `65eab1f5-f843-4819-a6b8-7bbfbb5a7d4d`), create or update the client's row: `Name` "Proposal <Company> + Eureka", `Status` `Definition`, `Budget` total, `Person` the team (`notion_user_id`), `Proposal URL`. Put the row's id in `notion_page_id` and rebuild.

Publishing is not sending: set `Status` = `Sent` only when the team sends the link (ask). Accepting on the page (`api/accept.js`) only updates rows in `Sent` or a Follow Up status. Then offer to draft the send email in the client's language: one personal line, what the proposal covers, the link, "accept directly on the page".

## Deploy budget

Vercel allows 100 deploys a day for the whole team (each push to `main` builds two projects). Group changes: apply a whole review round, then push once. Pushes to `claude/*` branches don't build. A 402 "api-deployments-free-per-day" means the limit, not a bug.

## Before publishing

- If `data/company.json` has `"demo": true`, the page shows placeholder payment data: don't publish to a real client until the user confirms.
- The accept email needs `RESEND_API_KEY`, `EMAIL_FROM` and `TEAM_EMAIL` in Vercel; without them the page works but sends nothing.
