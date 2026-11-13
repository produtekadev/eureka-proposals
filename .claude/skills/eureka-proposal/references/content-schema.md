# proposal.json

One file per proposal at `proposals/<slug>/proposal.json`. `proposals/demo/proposal.json` is a complete example; copy it and replace the content.

Text fields may use a few inline tags: `<b>`, `<em>`, `<i>`, `<br>`, and `<span class="hl">` (purple highlight, for one word in the cover headline). Everything else is plain text.

```jsonc
{
  "lang": "en",                         // "en" or "es": all labels switch with it
  "client": { "company": "", "contact": "", "role": "", "location": "" },
  "prepared_by": ["paula", "mateo"],    // ids from data/team.json, shown on the cover
  "team": ["abel"],                     // extra team members shown in About us
  "date": "2026-11-13",                 // proposal date (YYYY-MM-DD)
  "valid_until": "2026-11-27",
  "start": "Week of November 30",       // free text
  "duration_label": null,               // optional: overrides the cover's "N weeks" (e.g. "6 months")

  "cover": {
    "tag": "Implementation proposal",
    "headline": "One place to run<br><em>the whole</em> <span class=\"hl\">studio.</span>",
    "lede": "One or two sentences: what this plan does and the call it's based on.",
    "glance": [ { "k": "small label", "h": "title", "p": "one line" } ]   // 3 items, optional
  },

  "context": {
    "title": "What we<br><em>heard.</em>",
    "lede": "Who they are and the core problem, 2 sentences.",
    "stats": [ { "n": "9", "t": "people, plus 4 freelancers" } ],       // 2 or 3, optional
    "pains_label": "The challenge",                                        // optional
    "pains_title": "Three things <em>slowing down</em> the studio.",
    "pains": [ { "k": "Sales", "h": "No pipeline", "it": "In their words.", "p": "The consequence." } ],  // 3
    "quote": { "text": "Their words.", "who": "Name, role" },           // optional
    "opportunity_label": "The opportunity",                              // optional
    "opportunity": "Why now, 2 sentences."                               // optional
  },

  "focus": {                            // optional: omit when ask and recommendation match
    "title": "Where we'd<br><em>start.</em>",
    "statement": "The focus sentence and why.",
    "asked": ["everything they asked for"],
    "recommend": ["what we recommend, in order"],
    "why": "One sentence on the main trade-off."                         // optional
  },

  "proposal": {
    "title": "Two phases,<br><em>clear prices.</em>",
    "intro": "One or two sentences.",
    "currency": "USD",
    "phases": [
      {
        "id": "build",                  // unique, lowercase
        "name": "Build and training",
        "tag": "essential",             // essential (always on) | recommended (on, can switch off) | optional (off unless default_on)
        "default_on": false,            // optional, only for "optional"
        "price": 1500,
        "weeks": 3,                     // used for the total duration; 0 if it runs in parallel
        "duration": "Runs in parallel", // optional text that replaces "3 weeks"
        "summary": "One sentence.",
        "deliverables": ["3 to 6 short items"]
      }
    ],
    "included": ["…"],
    "excluded": ["…"],
    "guarantee": "One month after delivery to fix issues within the delivered scope, at no extra cost."   // optional
  },

  "payment": {
    "deposit_pct": 50,
    "schedule": "50% when you accept, 50% on delivery. By bank transfer, no card fees.",
    "ref": "ACME-2611"                  // payment reference shown after acceptance
  },

  "next_steps": [ { "when": "Today", "h": "Accept and send the deposit", "p": "Right here, below." } ],
  "closing": "We're ready to build<br><em>your Eureka moment.</em>",     // optional
  "about_title": "The team <em>behind it.</em>"                          // optional
}
```

Section order is fixed: Cover, Context, Focus (if present), Proposal, About us, Start (next steps and accept).
