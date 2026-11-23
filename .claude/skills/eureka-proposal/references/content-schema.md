# proposal.json

One file per proposal at `proposals/<slug>/proposal.json`. `proposals/sync/proposal.json` is a recent full example.

Text fields accept `<b>`, `<em>`, `<i>`, `<br>` and `<span class="hl">` (purple highlight, one word in the cover headline). Everything else is plain text. Fields marked "optional" can be left out.

```jsonc
{
  "lang": "en",                          // "en" or "es": all labels follow it
  "client": { "company": "", "contact": "", "role": "", "location": "",
              "logo": "clients/acme.png" },          // optional: under template/assets/, black (recolor white logos)
  "prepared_by": ["paula", "mateo"],     // ids from data/team.json
  "team": [],                            // extra team members in Team
  "notion_page_id": "",                  // the row in Notion Proposals
  "clients": ["henkel", "toggl-hire"],   // logo grid, ids from data/clients.json, most relevant first
  "date": "2026-11-23", "valid_until": "2026-12-07", "start": "Week of November 30",

  "cover": {
    "tag": "Implementation proposal",
    "headline": "Everything X knows,<br><em>in one</em> <span class=\"hl\">place.</span>",
    "lede": "One or two sentences: what the plan does and which calls it's based on.",
    "goal": { "h": "One source of truth", "p": "One line on the outcome." },   // minimal cover (default): goal + duration & price (computed)
    "price_note": "Audit, build and training. Starts the week of November 30."
    // legacy alternative to "goal": "glance": [ { "k": "", "h": "", "p": "" } ] (3 items)
  },

  "context": {
    "title": "What we<br><em>heard.</em>",
    "lede": "Who they are and the core problem.",
    "stats": [ { "n": "9+", "t": "tools in use" } ],                   // optional, 2 or 3
    "pains_title": "Three things <em>slowing down</em> the team.",
    "illustration": "too-many-apps",                                     // optional: between the pains title and the cards
    "pains": [ { "k": "Tools", "h": "Short name", "it": "\"Their words.\"", "p": "The consequence." } ],   // 3
    "quote": { "text": "Their words.", "who": "Name" },                 // optional
    "opportunity": "Why now, 2 sentences."                               // optional
  },

  "focus": {
    "nav": "Goal",                                                       // menu name (default "Focus")
    "title": "What changes<br><em>for your team.</em>",
    "statement": "<b>The goal in one sentence.</b>",
    "benefits": [ { "icon": "purple-shape", "h": "Short benefit", "p": "One line." } ],   // 6 cards; icons: purple-shape, magenta-shape, orange-cross
    "mockups": [ {                                                       // optional, only when the team asks: one Notion AI chat
      "type": "chat", "label": "Notion AI",
      "q": "Their real question", "a": "How Notion answers it",
      "sources": ["Product catalog", "Google Drive"],
      "suggestions": [ { "icon": "meetings", "q": "Another question in their words" } ],   // icons: meetings, goals, team, ask
      "reads": ["Google Drive", "Meeting notes", "Product catalog", "OKRs", "Team boards"]   // logos in MK_ICONS (build.py); unknown names get a document icon
    } ],
    "why": "One line that leads into the proposal."                      // optional
    // legacy alternative to "benefits": "asked" / "recommend" lists (two columns)
  },

  "proposal": {
    "title": "What we'll build<br><em>and what it costs.</em>",
    "intro": "Each phase has its own price and they add up to one fixed total.",
    "currency": "USD",
    "phases": [ {
      "id": "audit", "name": "Information audit and roadmap",
      "tag": "essential",                // essential | recommended | optional (label only)
      "price": 500, "weeks": 1,          // weeks 0 if it runs in parallel; "duration" text overrides
      "illustration": "map",             // map / build / scale
      "summary": "One sentence.",
      "deliverables": [ { "h": "Title that stands on its own", "p": "One short line, shown on hover" } ],
      "you_do": ["What the client does or decides"]
    } ],
    "included": ["…"],
    "excluded": ["…"],
    "guarantee": "Two weeks after launch to fix issues within the delivered scope, at no extra cost."
  },

  "payment": {
    "deposit_pct": 50,
    "schedule": "50% when you accept (USD X), 50% on delivery (USD X). By bank transfer, or by card through Stripe with a 4% card fee.",
    "stripe_url": "https://buy.stripe.com/..."   // deposit + card fee, see step 6 of SKILL.md
  },

  "next_steps": [ { "when": "Today", "h": "Accept and send the deposit", "p": "Right here, below." } ],
  "closing": "We're ready to build<br><em>your Eureka moment.</em>",
  "closing_illustration": "team-work"
}
```

Also supported, rarely used: phase `visual` (SVG from `template/visuals/`), phase `callout`, `proposal.examples` (screenshots), other mockup types (`ask`, `notes`, `progress`), `duration_label`, `about_title`. See `build.py`.

Section order is fixed: Cover, Context, Goal (if `focus`), Proposal, Team, Start.
