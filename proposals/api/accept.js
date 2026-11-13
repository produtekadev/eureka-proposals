// POST /api/accept
// Called by the "Accept proposal" block. Recomputes the accepted scope from the
// proposal's own data (never trusts prices from the browser), then:
//   1. emails the client the payment details and kickoff link (copy to the team)
//   2. posts a Slack message, if SLACK_WEBHOOK_URL is set
//
// Environment variables (Vercel project settings):
//   RESEND_API_KEY     required to send email (resend.com, domain eureka.ceo verified)
//   EMAIL_FROM         e.g. "Eureka <proposals@eureka.ceo>"
//   TEAM_EMAIL         copy of every acceptance, e.g. team@eureka.ceo
//   SLACK_WEBHOOK_URL  optional
const fs = require('fs');
const path = require('path');

const T = {
  en: {
    subject: (c) => `Proposal accepted: next steps with Eureka (${c})`,
    hi: (n) => `Hi ${n},`,
    thanks: (c) => `Thank you for accepting the proposal for ${c}. Here's everything you need to get started.`,
    scope: 'Accepted scope', total: 'Total', deposit: 'Deposit to send now', ref: 'Payment reference',
    memo: 'Please add the reference to the transfer memo so we can match your payment.',
    bank: 'Bank details', kickoff: 'Book your kickoff', kickoffText: 'Pick a time for the kickoff:',
    after: 'We confirm your deposit within one business day and send you the client portal invite.',
    bye: 'The Eureka team', view: 'View the proposal',
  },
  es: {
    subject: (c) => `Propuesta aceptada: próximos pasos con Eureka (${c})`,
    hi: (n) => `Hola ${n},`,
    thanks: (c) => `Gracias por aceptar la propuesta para ${c}. Aquí tienes todo lo necesario para empezar.`,
    scope: 'Alcance aceptado', total: 'Total', deposit: 'Anticipo a enviar', ref: 'Referencia de pago',
    memo: 'Incluye la referencia en el concepto de la transferencia para identificar tu pago.',
    bank: 'Datos bancarios', kickoff: 'Agenda el kickoff', kickoffText: 'Elige un horario para el kickoff:',
    after: 'Confirmamos tu anticipo en un día hábil y te enviamos la invitación al portal de cliente.',
    bye: 'El equipo de Eureka', view: 'Ver la propuesta',
  },
};

const esc = (s) => String(s).replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
const money = (cur, n) => `${cur} ${Math.round(n).toLocaleString('en-US')}`;

function loadProposal(slug) {
  if (!/^[a-z0-9-]+$/.test(slug)) return null;
  const f = path.join(__dirname, '_proposals', `${slug}.json`);
  return fs.existsSync(f) ? JSON.parse(fs.readFileSync(f, 'utf8')) : null;
}

function emailHtml(P, a, scope, t) {
  const rows = (r) => r.map(([k, v]) => `<tr><td style="padding:6px 12px 6px 0;color:#555">${esc(k)}</td><td style="padding:6px 0;font-weight:600">${esc(v)}</td></tr>`).join('');
  const banks = P.bank_accounts.map((b) => `<p style="margin:16px 0 4px;font-weight:700">${esc(b.label)}</p><table style="border-collapse:collapse;font-size:14px">${rows(b.rows)}</table>`).join('');
  return `<div style="font-family:Helvetica,Arial,sans-serif;color:#111;max-width:560px;line-height:1.5">
  <p>${esc(t.hi(a.name.split(' ')[0]))}</p>
  <p>${esc(t.thanks(P.company))}</p>
  <h3 style="color:#750FB4;margin:24px 0 6px">${t.scope}</h3>
  <ul style="padding-left:18px;margin:0">${scope.items.map((i) => `<li>${esc(i.name)}: ${money(P.currency, i.price)}</li>`).join('')}</ul>
  <p style="margin:10px 0 0">${t.total}: <b>${money(P.currency, scope.total)}</b></p>
  <h3 style="color:#750FB4;margin:24px 0 6px">${t.deposit}: ${money(P.currency, scope.deposit)}</h3>
  <p style="margin:0">${t.ref}: <b>${esc(P.ref)}</b><br><span style="color:#555">${t.memo}</span></p>
  <h3 style="color:#750FB4;margin:24px 0 6px">${t.bank}</h3>${banks}
  <h3 style="color:#750FB4;margin:24px 0 6px">${t.kickoff}</h3>
  <p style="margin:0">${t.kickoffText} <a href="${esc(P.kickoff_url)}" style="color:#750FB4;font-weight:700">${esc(P.kickoff_url)}</a></p>
  <p style="margin:24px 0 0">${t.after}</p>
  <p style="margin:24px 0 0">${t.bye}<br><a href="${esc(P.url)}" style="color:#555">${t.view}</a></p>
</div>`;
}

module.exports = async (req, res) => {
  if (req.method !== 'POST') return res.status(405).json({ error: 'POST only' });
  const b = typeof req.body === 'string' ? JSON.parse(req.body || '{}') : (req.body || {});
  const P = loadProposal(String(b.proposal || ''));
  if (!P) return res.status(404).json({ error: 'Unknown proposal' });
  const name = String(b.name || '').trim().slice(0, 120);
  const email = String(b.email || '').trim().slice(0, 200);
  if (!name || !/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email)) return res.status(400).json({ error: 'Invalid fields' });

  // Fixed scope: every phase in the proposal is part of the price.
  const items = P.phases;
  const total = items.reduce((s, i) => s + i.price, 0);
  const scope = { items, total, deposit: (total * P.deposit_pct) / 100 };
  const t = T[P.lang] || T.en;
  const out = { ok: true, emailed: false, total, deposit: scope.deposit };

  if (process.env.RESEND_API_KEY && process.env.EMAIL_FROM) {
    const r = await fetch('https://api.resend.com/emails', {
      method: 'POST',
      headers: { Authorization: `Bearer ${process.env.RESEND_API_KEY}`, 'Content-Type': 'application/json' },
      body: JSON.stringify({
        from: process.env.EMAIL_FROM,
        to: [email],
        bcc: process.env.TEAM_EMAIL ? [process.env.TEAM_EMAIL] : undefined,
        reply_to: process.env.TEAM_EMAIL || undefined,
        subject: t.subject(P.company),
        html: emailHtml(P, { name, email }, scope, t),
      }),
    }).catch(() => null);
    out.emailed = !!(r && r.ok);
  }

  if (process.env.SLACK_WEBHOOK_URL) {
    await fetch(process.env.SLACK_WEBHOOK_URL, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text: `✅ ${P.company} accepted the proposal. ${name} (${email}). Scope: ${items.map((i) => i.name).join(', ')}. Total ${money(P.currency, total)}, deposit ${money(P.currency, scope.deposit)} pending. Ref ${P.ref}. ${P.url}` }),
    }).catch(() => null);
  }

  return res.status(200).json(out);
};
