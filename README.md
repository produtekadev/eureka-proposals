# Eureka Proposals

Client proposals for Eureka, built as single-page websites.

## Structure

- `proposals/<client>/index.html`: one folder per client proposal, as published.
- `proposals/demo/`: fake client used to test shared pieces.
- `components/accept/`: the "Accept proposal" block (acceptance form, payment details, kickoff link). Placeholders in `{{double_braces}}`.
- `proposals/vercel.json`: settings for proposals.eureka.ceo (no search indexing, redirects).

## Deploys

- **proposals.eureka.ceo**: Vercel project `eureka-proposals`, serves `proposals/`. Each folder is a page, e.g. `proposals.eureka.ceo/demo`.
- **trolley.eureka.ceo**: the Vercel project `eureka-propuesta-federico` is linked to this repo. Every push to `main` updates the live site from `proposals/federico-gonzalez/`.

## Proposals

| Client | Live URL | Status |
|---|---|---|
| Federico González (Trolley.ai) | https://eureka-propuesta-federico.vercel.app | Sent, Nov 6 2026 |

Next: extract a shared template and design system from the Federico proposal, so new proposals are built from a content file instead of hand-edited HTML.
