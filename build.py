#!/usr/bin/env python3
"""Build a proposal page from its content file.

Usage:
  python3 build.py <slug>        builds proposals/<slug>/index.html from proposals/<slug>/proposal.json
  python3 build.py --all         builds every proposal that has a proposal.json

The page is a single self-contained HTML file (fonts, styles, photos inlined),
so it works offline and can be shared as one link.
"""
import base64, html, json, os, re, sys

ROOT = os.path.dirname(os.path.abspath(__file__))
T = os.path.join(ROOT, 'template')

# ---------- UI strings ----------
UI = {
  'en': {
    'section': 'Section', 'proposal_for': 'Proposal for', 'for': 'For', 'prepared_by': 'Prepared by',
    'duration': 'Duration', 'date': 'Date', 'investment': 'Investment', 'context': 'Context', 'focus': 'Focus',
    'proposal': 'Proposal', 'about': 'Team', 'start': 'Start', 'cover': 'Cover',
    'essential': 'Essential', 'recommended': 'Recommended', 'optional': 'Optional', 'included_tag': 'Included',
    'build_scope': 'Scope and investment',
    'total': 'Total', 'weeks': 'weeks', 'week': 'week', 'deposit': 'Deposit', 'on_accept': 'when you accept',
    'deliverables': 'What you get', 'included': 'Included in this proposal', 'excluded': 'Not included',
    'guarantee': 'Guarantee', 'team': 'Your team', 'clients': 'Some of our clients', 'partner': 'Notion Consulting Partner',
    'partner_text': 'Certified by Notion to design and implement workspaces.',
    'asked': 'What you asked for', 'recommend': 'What we recommend', 'next': 'Next steps',
    'valid': 'Proposal valid until', 'starts': 'Projected start', 'the_goal': 'The goal', 'dur_price': 'Duration & price', 'valid_short': 'valid until',
    'accepting': "You're accepting", 'accept_btn': 'Accept proposal →', 'name': 'Full name', 'email': 'Email',
    'i_accept': 'I accept this proposal and the', 'terms': 'terms and conditions', 'read_terms': 'Read the terms',
    'submit': 'Accept and see payment details', 'accepted_by': 'Accepted by', 'on': 'on',
    'send_deposit': 'Send the deposit', 'reference': 'Reference', 'memo': 'Add the reference to the transfer memo so we can match your payment.',
    'book': 'Book your kickoff', 'book_text': 'Pick a time for the kickoff. We use it to meet the team, confirm the plan and open your Slack channel.',
    'book_btn': 'Book the kickoff →', 'from_there': 'We take it from there', 'from_there_text': 'As soon as we receive your payment, we email you the next steps, including the link to book your kickoff.',
    'pay_card': 'Pay with card →', 'card_amount': 'Amount with the {pct}% card fee', 'card_text': 'Secure payment through Stripe. The card fee is added to the deposit.',
    'card_soon': 'We send you the card payment link by email.',
    'emailed': 'We also sent these details to', 'reset': 'Reset (test only)', 'demo': 'Demo data', 'copy': 'Copy',
    'err_name': 'Please add your full name.', 'err_email': 'Please add a valid email.', 'err_terms': 'Please accept the terms to continue.',
    'scope_selected': 'Scope and investment', 'client_logo': 'Client logo', 'we_did': 'What we did', 'your_part': 'Your part', 'illustrative': 'Illustrative view', 'see_details': 'See what each one includes', 'hover_hint': 'Hover or tap an item for details', 'accepted_scope': 'Accepted scope',
    'ready': 'Ready to', 'ready_em': 'start?',
  },
  'es': {
    'section': 'Sección', 'proposal_for': 'Propuesta para', 'for': 'Para', 'prepared_by': 'Preparado por',
    'duration': 'Duración', 'date': 'Fecha', 'investment': 'Inversión', 'context': 'Contexto', 'focus': 'Enfoque',
    'proposal': 'Propuesta', 'about': 'Equipo', 'start': 'Empezar', 'cover': 'Portada',
    'essential': 'Indispensable', 'recommended': 'Recomendado', 'optional': 'Opcional', 'included_tag': 'Incluido',
    'build_scope': 'Alcance e inversión',
    'total': 'Total', 'weeks': 'semanas', 'week': 'semana', 'deposit': 'Anticipo', 'on_accept': 'al aceptar',
    'deliverables': 'Lo que recibes', 'included': 'Incluido en esta propuesta', 'excluded': 'No incluido',
    'guarantee': 'Garantía', 'team': 'Tu equipo', 'clients': 'Algunos de nuestros clientes', 'partner': 'Notion Consulting Partner',
    'partner_text': 'Certificados por Notion para diseñar e implementar workspaces.',
    'asked': 'Lo que nos pidieron', 'recommend': 'Lo que recomendamos', 'next': 'Próximos pasos',
    'valid': 'Propuesta válida hasta', 'starts': 'Inicio proyectado', 'the_goal': 'El objetivo', 'dur_price': 'Duración y precio', 'valid_short': 'válida hasta',
    'accepting': 'Estás aceptando', 'accept_btn': 'Aceptar propuesta →', 'name': 'Nombre completo', 'email': 'Email',
    'i_accept': 'Acepto esta propuesta y los', 'terms': 'términos y condiciones', 'read_terms': 'Leer los términos',
    'submit': 'Aceptar y ver datos de pago', 'accepted_by': 'Aceptada por', 'on': 'el',
    'send_deposit': 'Envía el anticipo', 'reference': 'Referencia', 'memo': 'Incluye la referencia en el concepto de la transferencia para identificar tu pago.',
    'book': 'Agenda el kickoff', 'book_text': 'Elige un horario para el kickoff. Lo usamos para conocer al equipo, confirmar el plan y abrir tu canal de Slack.',
    'book_btn': 'Agendar kickoff →', 'from_there': 'Nosotros nos encargamos', 'from_there_text': 'Apenas recibamos tu pago, te enviamos por email los próximos pasos, incluido el enlace para agendar el kickoff.',
    'pay_card': 'Pagar con tarjeta →', 'card_amount': 'Monto con el recargo del {pct}% por tarjeta', 'card_text': 'Pago seguro a través de Stripe. El recargo por tarjeta se suma al anticipo.',
    'card_soon': 'Te enviamos el enlace de pago con tarjeta por email.',
    'emailed': 'También enviamos estos datos a', 'reset': 'Reiniciar (solo prueba)', 'demo': 'Datos demo', 'copy': 'Copiar',
    'err_name': 'Agrega tu nombre completo.', 'err_email': 'Agrega un email válido.', 'err_terms': 'Acepta los términos para continuar.',
    'scope_selected': 'Alcance e inversión', 'client_logo': 'Logo de cliente', 'we_did': 'Qué hicimos', 'your_part': 'Tu parte', 'illustrative': 'Vista ilustrativa', 'see_details': 'Ver qué incluye cada uno', 'hover_hint': 'Pasa el cursor o toca un ítem para ver el detalle', 'accepted_scope': 'Alcance aceptado',
    'ready': '¿Listos para', 'ready_em': 'empezar?',
  },
}

MONTHS = {
  'en': ['January','February','March','April','May','June','July','August','September','October','November','December'],
  'es': ['enero','febrero','marzo','abril','mayo','junio','julio','agosto','septiembre','octubre','noviembre','diciembre'],
}

def esc(s):
  return html.escape(str(s), quote=True)

def rich(s):
  """Content fields may use a few inline tags: <b>, <em>, <i>, <br>, <span class="hl">."""
  return str(s)

def fmt_money(n, cur='USD'):
  return f'{cur} {n:,.0f}'

def fmt_date(iso, lang):
  y, m, d = (int(x) for x in iso.split('-'))
  if lang == 'es':
    return f'{d} de {MONTHS["es"][m-1]} de {y}'
  return f'{MONTHS["en"][m-1]} {d}, {y}'

def read(p, mode='r'):
  with open(p, mode, **({} if 'b' in mode else {'encoding': 'utf-8'})) as f:
    return f.read()

def data_uri(path):
  ext = path.rsplit('.', 1)[-1].lower()
  mime = {'jpg': 'image/jpeg', 'jpeg': 'image/jpeg', 'png': 'image/png', 'svg': 'image/svg+xml', 'webp': 'image/webp'}[ext]
  return f'data:{mime};base64,' + base64.b64encode(read(path, 'rb')).decode()

# ---------- sections ----------
class Page:
  def __init__(self, P, lang):
    self.P, self.lang, self.u = P, lang, UI[lang]
    self.sections = []

  def add(self, sid, name, body):
    n = f'{len(self.sections):02d}'
    label = '' if sid == 'cover' else f'<div class="label">{self.u["section"]} {n}</div>\n'
    self.sections.append(f'<section class="page" id="{sid}" data-n="{n}" data-name="{esc(name)}">\n{label}{body}\n  <div class="pager"></div>\n</section>')

def sec_cover(pg, P, team):
  u, c, cv = pg.u, P['client'], P['cover']
  prep = ' & '.join(team[t]['name'] for t in P['prepared_by'])
  weeks = sum(ph.get('weeks', 0) for ph in P['proposal']['phases'] if ph.get('tag') != 'optional')
  glance = ''.join(f'<div><div class="n">{rich(g["k"])}</div><h3>{rich(g["h"])}</h3><p>{rich(g["p"])}</p></div>' for g in cv.get('glance', []))
  body = f'''  <span class="ncp cv-badge" role="img" aria-label="{u['partner']}"></span>
  <div class="cv-pad">
  {f'<img class="cv-logo"{(' style="height:' + str(int(c["logo_height"])) + 'px"') if c.get("logo_height") else ''} src="{data_uri(os.path.join(T, "assets", c["logo"]))}" alt="{esc(c["company"])}">' if c.get('logo') else ''}
  <span class="tag">{esc(cv.get('tag', ''))}</span>
  <h1>{rich(cv['headline'])}</h1>
  </div>
  <p class="lede">{rich(cv['lede'])}</p>
  <div class="meta">
    <div><div class="k">{u['for']}</div><div class="v">{esc(c['company'])}</div><div class="d">{esc(c.get('contact', ''))}{', ' + esc(c['role']) if c.get('role') else ''}</div></div>
    <div><div class="k">{u['prepared_by']}</div><div class="v">{esc(prep)}</div><div class="d">Eureka</div></div>
    <div><div class="k">{u['duration']}</div><div class="v">{rich(P.get('duration_label') or f'<em>{weeks}</em> {u["weeks"]}')}</div><div class="d">{esc(P.get('start', ''))}</div></div>
    <div><div class="k">{u['date']}</div><div class="v">{esc(fmt_date(P['date'], pg.lang))}</div><div class="d">{u['valid']} {esc(fmt_date(P['valid_until'], pg.lang))}</div></div>
  </div>'''
  if cv.get('goal'):
    # Minimal cover: goal and duration/price first, who and when in a small footer line.
    g = cv['goal']
    total = sum(ph['price'] for ph in P['proposal']['phases'])
    show_price = cv.get('show_price', True)  # false for live presentations: the price first appears in the Proposal section
    dur = rich(P.get('duration_label') or f'<em>{weeks}</em> {u["weeks"]}')
    head = body.split('  <div class="meta">')[0]
    body = head + f'''  <div class="cv-key">
    <div><div class="k">{u['the_goal']}</div><h3>{rich(g['h'])}</h3><p>{rich(g.get('p', ''))}</p></div>
    <div><div class="k">{u['dur_price'] if show_price else u['duration']}</div><h3>{dur}{' · ' + esc(fmt_money(total, P['proposal'].get('currency', 'USD'))) if show_price else ''}</h3><p>{rich(cv.get('price_note', ''))}</p></div>
  </div>
  <p class="cv-foot">{u['for']} <b>{esc(c['company'])}</b>{' · ' + esc(c['contact']) if c.get('contact') else ''} · {u['prepared_by']} <b>{esc(prep)}</b>, Eureka · {esc(fmt_date(P['date'], pg.lang))}, {u['valid_short']} {esc(fmt_date(P['valid_until'], pg.lang))}</p>'''
  elif glance:
    body += f'\n  <div class="sec-sm"><div class="glance">{glance}</div></div>'
  pg.add('cover', u['cover'], body)

def sec_context(pg, P):
  u, x = pg.u, P['context']
  stats = ''
  if x.get('stats'):
    stats = f'<div class="stats s{len(x["stats"])}">' + ''.join(f'<div><span class="n">{esc(s["n"])}</span><span>{rich(s["t"])}</span></div>' for s in x['stats']) + '</div>'
  cls = ['c-p', 'c-m', 'c-o']
  pains = ''.join(f'''<article class="fc"><div class="fc-h"><span class="num {cls[i % 3]}">{i+1:02d}</span><div><div class="k">{esc(p.get('k', ''))}</div><h3>{rich(p['h'])}</h3></div></div><div class="fc-b">{f'<p class="it">{rich(p["it"])}</p>' if p.get('it') else ''}<p>{rich(p['p'])}</p></div></article>''' for i, p in enumerate(x['pains']))
  quote = ''
  if x.get('quote'):
    quote = f'<div class="pull"><p>“{rich(x["quote"]["text"])}”</p><div class="who">{esc(x["quote"]["who"])}</div></div>'
  opp = ''
  if x.get('opportunity'):
    opp = f'<div class="sec"><div class="label">{esc(x.get("opportunity_label", "The opportunity" if pg.lang == "en" else "La oportunidad"))}</div><p class="lede" style="margin-top:12px">{rich(x["opportunity"])}</p></div>'
  body = f'''  <h1>{rich(x['title'])}</h1>
  <p class="lede">{rich(x['lede'])}</p>
  {stats}
  <div class="sec">
    <div class="label">{esc(x.get('pains_label', 'The challenge' if pg.lang == 'en' else 'El reto'))}</div>
    <h2>{rich(x['pains_title'])}</h2>
    {f'<figure class="fx-ill"><img src="{data_uri(os.path.join(T, "assets", "illustrations", x["illustration"] + ".webp"))}" alt=""></figure>' if x.get('illustration') else ''}
    <div class="cards">{pains}</div>
  </div>
  {quote}
  {opp}'''
  pg.add('context', u['context'], body)

# Small icons for the chat mockup (sources, suggestions). Keys are lowercase source names.
_I = lambda d: f'<svg viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{d}</svg>'
MK_ICONS = {
  'google drive': '<svg viewBox="0 0 87.3 78" aria-hidden="true"><path d="m6.6 66.85 3.85 6.65c.8 1.4 1.95 2.5 3.3 3.3l13.75-23.8h-27.5c0 1.55.4 3.1 1.2 4.5z" fill="#0066da"/><path d="m43.65 25-13.75-23.8c-1.35.8-2.5 1.9-3.3 3.3l-25.4 44a9.06 9.06 0 0 0 -1.2 4.5h27.5z" fill="#00ac47"/><path d="m73.55 76.8c1.35-.8 2.5-1.9 3.3-3.3l1.6-2.75 7.65-13.25c.8-1.4 1.2-2.95 1.2-4.5h-27.502l5.852 11.5z" fill="#ea4335"/><path d="m43.65 25 13.75-23.8c-1.35-.8-2.9-1.2-4.5-1.2h-18.5c-1.6 0-3.15.45-4.5 1.2z" fill="#00832d"/><path d="m59.8 53h-32.3l-13.75 23.8c1.35.8 2.9 1.2 4.5 1.2h50.8c1.6 0 3.15-.45 4.5-1.2z" fill="#2684fc"/><path d="m73.4 26.5-12.7-22c-.8-1.4-1.95-2.5-3.3-3.3l-13.75 23.8 16.15 28h27.45c0-1.55-.4-3.1-1.2-4.5z" fill="#ffba00"/></svg>',
  'product catalog': _I('<path d="M3 4.5V9l7.5 7.5 6-6L9 3H4.5A1.5 1.5 0 0 0 3 4.5z" fill="#F6EEFB" stroke="#7A12B5"/><circle cx="6.5" cy="6.5" r="1.2" fill="#7A12B5" stroke="none"/>'),
  'meeting notes': _I('<rect x="3" y="4" width="14" height="13" rx="2" fill="#FFF1E8" stroke="#E2622F"/><path d="M3 8h14M7 2.5v3M13 2.5v3" stroke="#E2622F"/>'),
  'meetings': _I('<rect x="3" y="4" width="14" height="13" rx="2"/><path d="M3 8h14M7 2.5v3M13 2.5v3"/>'),
  'okrs': _I('<circle cx="10" cy="10" r="7" fill="#FDEAF3" stroke="#D63384"/><circle cx="10" cy="10" r="3.5" stroke="#D63384"/><circle cx="10" cy="10" r="1" fill="#D63384" stroke="none"/>'),
  'goals': _I('<circle cx="10" cy="10" r="7"/><circle cx="10" cy="10" r="3.5"/>'),
  'team boards': _I('<rect x="2.5" y="3.5" width="4" height="13" rx="1" fill="#EAF2FF" stroke="#2F6FDE"/><rect x="8" y="3.5" width="4" height="9" rx="1" fill="#EAF2FF" stroke="#2F6FDE"/><rect x="13.5" y="3.5" width="4" height="11" rx="1" fill="#EAF2FF" stroke="#2F6FDE"/>'),
  'team': _I('<circle cx="7" cy="7" r="2.6"/><circle cx="14" cy="8" r="2.1"/><path d="M2.5 16c.6-2.6 2.4-4 4.5-4s3.9 1.4 4.5 4M12 13.3c2.2-.4 4.4.8 5 2.7"/>'),
  'ask': _I('<path d="M4 15.5 3 18l2.7-1A8 8 0 1 0 4 15.5z"/><path d="M8 9h4M8 12h2.5"/>'),
  'doc': _I('<path d="M5 2.5h6.5L15.5 6.5v11h-10.5z"/><path d="M11.5 2.5v4h4"/>'),
}

# Notion-style dashboard for the Goal section (same look as the approved Trolley cockpit). Static SVG, illustrative.
DB_COL = {'purple': '#750FB4', 'magenta': '#EF53D4', 'orange': '#FF673E', 'amber': '#E8A317', 'grey': '#B9B6B0', 'green': '#1C7C54'}
DB_IC = {
  'bars': '<path d="M5 20V10M10 20V4M15 20v-7M20 20v-4"/>',
  'donut': '<path d="M12 3a9 9 0 1 0 9 9h-9z"/><path d="M15 3.5A9 9 0 0 1 20.5 9H15z"/>',
  'line': '<path d="M3 3v18h18"/><path d="M7 15l4-4 3 3 6-6"/>',
  'list': '<path d="M8 6h13M8 12h13M8 18h13M3 6h.01M3 12h.01M3 18h.01"/>',
  'check': '<path d="M20 6 9 17l-5-5"/>',
  'users': '<circle cx="9" cy="8" r="3.5"/><path d="M2.5 20c.6-3.4 3.3-5.5 6.5-5.5s5.9 2.1 6.5 5.5M16 4.8a3.5 3.5 0 0 1 0 6.4M18 14.8c1.9.8 3.1 2.6 3.5 5.2"/>',
  'dash': '<rect x="3" y="3" width="18" height="18" rx="3"/><path d="M7 15l3-3 3 2 4-5"/>',
  'plane': '<path d="M2 16l20-8-6 12-3-5-5-1z"/>',
}
def _dbi(k):
  return f'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{DB_IC.get(k, DB_IC["dash"])}</svg>'

def _db_bars(w):
  items = w['items']; W, H, L, B, T = 240, 150, 26, 124, 10
  mx = max(v for _, v, *_ in items) or 1
  step = 10 if mx <= 40 else 20
  top = -(-mx // step) * step
  g = ''
  for v in range(0, top + 1, step):
    y = B - v / top * (B - T)
    g += f'<line class="gl" x1="{L}" x2="{W}" y1="{y:.1f}" y2="{y:.1f}"/><text class="ax" x="{L-6}" y="{y+3:.1f}" text-anchor="end">{v}</text>'
  bw = (W - L) / len(items)
  for i, it in enumerate(items):
    lab, v = it[0], it[1]; col = DB_COL.get(it[2] if len(it) > 2 else 'purple', it[2] if len(it) > 2 else '#750FB4')
    x = L + i * bw + bw / 2; h = v / top * (B - T)
    g += f'<rect x="{x-10:.1f}" width="20" y="{B-h:.1f}" height="{h:.1f}" rx="3" fill="{col}"/><text class="ax" x="{x:.1f}" y="{H-6}" text-anchor="middle">{esc(lab)}</text>'
  return f'<svg class="ch" viewBox="0 0 {W} {H}" role="img" aria-label="{esc(w["title"])}">{g}</svg>'

def _db_donut(w):
  segs = w['segments']; tot = sum(v for _, v, _ in segs) or 1; off = 0; circ = ''
  for lab, v, c in segs:
    pct = v / tot * 100; col = DB_COL.get(c, c)
    circ += f'<circle cx="60" cy="60" r="46" fill="none" stroke="{col}" stroke-width="8" pathLength="100" stroke-dasharray="{pct:.2f} {100-pct:.2f}" stroke-dashoffset="{-off:.2f}" transform="rotate(-90 60 60)"/>'
    off += pct
  lg = ''.join(f'<span><i style="background:{DB_COL.get(c, c)}"></i>{esc(lab)}</span>' for lab, _, c in segs)
  return (f'<svg class="ch" viewBox="0 0 120 120" style="max-width:140px;margin:4px auto 0" role="img" aria-label="{esc(w["title"])}">'
          f'<circle cx="60" cy="60" r="46" fill="none" stroke="#F1F0EE" stroke-width="8"/>{circ}'
          f'<text class="dn-t" x="60" y="63" text-anchor="middle">{esc(w.get("center", ""))}</text><text class="dn-s" x="60" y="79" text-anchor="middle">{esc(w.get("center_label", ""))}</text></svg>'
          f'<div class="cp-lg">{lg}</div>')

def _db_list(w):
  pills = {'ok': 'p-ok', 'pen': 'p-pen', 'rev': 'p-rev', 'plan': 'p-plan'}
  rows = ''
  for it in w['items']:
    av = f'<span class="av" style="background:{DB_COL.get(it.get("color", "purple"), it.get("color", "#750FB4"))}">{esc(it.get("who", "")[:2])}</span>' if it.get('who') else f'<span class="ic">{_dbi(it.get("icon", "plane"))}</span>'
    pill = f'<span class="pill {pills.get(it.get("status", "ok"), "p-ok")}">{esc(it["pill"])}</span>' if it.get('pill') else ''
    rows += f'<li>{av}<span class="t">{rich(it["t"])}<small>{rich(it.get("s", ""))}</small></span>{pill}</li>'
  return f'<ul class="ap">{rows}</ul>'

def dashboard(d, lang):
  if not d:
    return ''
  def widget(w):
    body = {'bars': _db_bars, 'donut': _db_donut, 'list': _db_list}[w['type']](w)
    return f'<div class="cp-w"><h5>{_dbi(w.get("icon", "dash"))}{rich(w["title"])}</h5><div class="cp-c">{body}</div></div>'
  rows = ''.join(f'<div class="cp-g {"r1" if len(r) == 3 else "r2"}">{"".join(widget(w) for w in r)}</div>' for r in d['rows'])
  views = ''.join(f'<span class="{"on" if i == 0 else ""}">{_dbi(v.get("icon", "dash")) if isinstance(v, dict) else ""}{rich(v["t"] if isinstance(v, dict) else v)}</span>' for i, v in enumerate(d.get('views', [])))
  crumb = ' / '.join(esc(c) for c in d.get('crumb', []))
  foot = ''
  if d.get('foot'):
    f = d['foot']
    foot = f'<div class="cp-foot"><span>{rich(f["label"])}</span><span class="cp-bar"><i style="width:{int(f["pct"])}%"></i></span><b>{int(f["pct"])}%</b><span class="cp-fn">{rich(f.get("note", ""))}</span></div>'
  cap = d.get('caption') or ('Illustrative view.' if lang == 'en' else 'Vista ilustrativa.')
  return (f'<div class="cp"><div class="cp-win"><div class="cp-dots"><i></i><i></i><i></i></div><div class="cp-tab">{esc(d["title"])}</div></div>'
          f'<div class="cp-crumb">{crumb} / <b>{esc(d["title"])}</b><span class="r">···</span></div>'
          f'<div class="cp-main"><h4 class="cp-h">{esc(d["title"])}</h4><div class="cp-views">{views}</div>{rows}</div>{foot}</div>'
          f'<p class="cap">{rich(cap)}</p>')

def mockups(ms, lang):
  # Simple Notion-like windows that show what the client gets, in their context. Illustrative.
  if not ms:
    return ''
  def win(m):
    t = m.get('type')
    if t == 'ask':
      body = (f'<div class="mk-q"><span class="mk-ai">✦</span>{rich(m["q"])}</div>'
              f'<div class="mk-a">{rich(m["a"])}</div>' + (f'<div class="mk-src">{rich(m["source"])}</div>' if m.get('source') else ''))
    elif t == 'notes':
      body = f'<div class="mk-t">{rich(m["title"])}</div><ul class="mk-l">' + ''.join(f'<li>{rich(i)}</li>' for i in m.get('items', [])) + '</ul>'
    elif t == 'progress':
      body = (f'<div class="mk-t">{rich(m["title"])}</div>' + ''.join(
        f'<div class="mk-r"><span>{rich(r["k"])}</span><span class="mk-bar"><i style="width:{int(r["v"])}%"></i></span><b>{int(r["v"])}%</b></div>' for r in m.get('rows', [])))
    elif t == 'chat':
      face = f'<img class="mk-face" src="{data_uri(os.path.join(T, "assets", "illustrations", "notion-ai-face.webp"))}" alt="">'
      def ico(name):
        return f'<span class="mk-ico">{MK_ICONS.get(str(name).lower(), MK_ICONS["doc"])}</span>'
      def chip(x):
        # A source can be a plain name or {"t": "Document title", "icon": "google drive"}; shown as a link chip.
        if isinstance(x, dict):
          return f'<span class="mk-chip mk-link">{ico(x.get("icon", "doc"))}{rich(x["t"])}<span class="mk-arr">↗</span></span>'
        return f'<span class="mk-chip">{ico(x)}{rich(x)}</span>'
      srcs = ''.join(chip(x) for x in m.get('sources', []))
      rows = ''.join(f'<div class="mk-row">{ico(x.get("icon", "ask") if isinstance(x, dict) else "ask")}<span>{rich(x["q"] if isinstance(x, dict) else x)}</span></div>' for x in m.get('suggestions', []))
      reads = ''.join(f'<span class="mk-rd" title="{esc(x)}">{ico(x)}</span>' for x in m.get('reads', []))
      tl = m.get('try_label') or ('Try asking' if lang == 'en' else 'Prueba preguntando')
      ph = 'Ask Notion AI' if lang == 'en' else 'Pregúntale a Notion AI'
      rl = 'Reads from' if lang == 'en' else 'Lee desde'
      body = (f'<div class="mk-chat"><div class="mk-msg me">{rich(m["q"])}</div>'
              f'<div class="mk-msg ai">{face}<div><div>{rich(m["a"])}</div>' + (f'<div class="mk-srcs">{srcs}</div>' if srcs else '') + '</div></div></div>'
              + (f'<div class="mk-home"><div class="mk-home-h">{tl}</div>{rows}</div>' if rows else '')
              + f'<div class="mk-in"><div class="mk-ph">{ph}</div><div class="mk-ibar"><span class="mk-plus">+</span>'
              + (f'<span class="mk-rl">{rl}</span><span class="mk-rds">{reads}</span>' if reads else '')
              + '<span class="mk-send">↑</span></div></div>')
    else:
      return ''
    return f'<div class="mk-w"><div class="mk-top"><i></i><i></i><i></i><span>{rich(m.get("label", ""))}</span></div><div class="mk-b">{body}</div></div>'
  cap = 'Illustrative example' if lang == 'en' else 'Ejemplo ilustrativo'
  return f'<div class="mk{" one" if len(ms) == 1 else ""}">{"".join(win(m) for m in ms)}</div><p class="mk-cap">{cap}</p>'

def sec_focus(pg, P):
  u, f = pg.u, P['focus']
  li = lambda xs: ''.join(f'<li>{rich(v)}</li>' for v in xs)
  if f.get('benefits'):
    ico = lambda x: f'<img class="bn-i" src="{data_uri(os.path.join(T, "assets", "icons", x["icon"] + ".png"))}" alt="">' if x.get('icon') else ''
    cards = ''.join(f'<div class="bn-c">{ico(x)}<h3>{rich(x["h"])}</h3><p>{rich(x["p"])}</p></div>' for x in f['benefits'])
    grid = f'<div class="bn">{cards}</div>'
  else:
    grid = f'''<div class="fx">
    <div class="fx-c"><div class="k">{rich(f.get('asked_label') or u['asked'])}</div><ul>{li(f['asked'])}</ul></div>
    <div class="fx-c on"><div class="k">{rich(f.get('recommend_label') or u['recommend'])}</div><ul>{li(f['recommend'])}</ul></div>
  </div>'''
  ill = f'<figure class="fx-ill"><img src="{data_uri(os.path.join(T, "assets", "illustrations", f["illustration"] + ".webp"))}" alt=""></figure>' if f.get('illustration') else ''
  body = f'''  <h1>{rich(f['title'])}</h1>
  <p class="lede">{rich(f['statement'])}</p>
  {ill}
  {mockups(f.get('mockups'), pg.lang)}
  {dashboard(f.get('dashboard'), pg.lang)}
  {grid}
  {f'<p class="note" style="margin-top:18px">{rich(f["why"])}</p>' if f.get('why') else ''}'''
  pg.add('focus', f.get('nav') or u['focus'], body)

def sp_body(u, ph, dl):
  # Deliverables can be plain strings (classic list) or {"h": short title, "p": detail}.
  # With titles: a compact grid of titles, "Your part" on one line, details behind a toggle.
  items = ph.get('deliverables', [])
  you = ph.get('you_do', [])
  vis = ''
  if ph.get('visual'):
    svg = read(os.path.join(T, 'visuals', ph['visual'] + '.svg'))
    vis = f'<figure class="sp-vis">{svg}<figcaption>{u["illustrative"]}</figcaption></figure>'
  elif ph.get('illustration'):
    vis = f'<figure class="sp-ill"><img src="{data_uri(os.path.join(T, "assets", "illustrations", ph["illustration"] + ".webp"))}" alt=""></figure>'
  if items and all(isinstance(d, dict) for d in items):
    gets = ''.join((f'<li tabindex="0"><span class="sp-ck">✓</span><span class="sp-h">{rich(d["h"])}</span><span class="tip" role="tooltip">{rich(d["p"])}</span></li>' if d.get('p')
                    else f'<li><span class="sp-ck">✓</span><span class="sp-h">{rich(d["h"])}</span></li>') for d in items)
    youh = (f'<div class="sp-you2"><span class="sp-you-k">{u["your_part"]}</span>' + ''.join(f'<span class="yp">{rich(y)}</span>' for y in you) + '</div>') if you else ''
    co = ph.get('callout')
    coh = ''
    if co:
      ico = lambda x: f'<img class="co-i" src="{data_uri(os.path.join(T, "assets", "icons", x["icon"] + ".png"))}" alt="">' if x.get('icon') else ''
      asks = ''.join(f'<li>{ico(x)}<span class="co-q">{rich(x["q"])}</span><span class="co-a">{rich(x["a"])}</span></li>' for x in co.get('items', []))
      coh = (f'<div class="sp-co"><div class="sp-co-k">{rich(co.get("label", ""))}</div><h4>{rich(co["title"])}</h4>'
             + (f'<p>{rich(co["lede"])}</p>' if co.get('lede') else '') + f'<ul>{asks}</ul>'
             + (f'<div class="sp-co-note">{rich(co["note"])}</div>' if co.get('note') else '') + '</div>')
    right = f'<ul class="sp-gets">{gets}</ul>{coh}{youh}'
    return f'<div class="sp-body sp-v2{" has-vis" if vis else ""}">{vis}<div>{right}</div></div>'
  youl = ''.join(f'<li>{rich(d)}</li>' for d in you)
  left = (f'<ul class="sp-dl">{dl}</ul>' if dl else '') + (f'<div class="sp-you"><div class="sp-you-k">{u["your_part"]}</div><ul>{youl}</ul></div>' if youl else '')
  if not vis:
    return f'<div class="sp-body">{left}</div>'
  return f'<div class="sp-body has-vis"><div>{left}</div>{vis}</div>'

def sec_proposal(pg, P):
  u, pr, cur = pg.u, P['proposal'], P['proposal'].get('currency', 'USD')
  tag_lbl = {'essential': u['essential'], 'recommended': u['recommended'], 'optional': u['optional']}
  cards = []
  for i, ph in enumerate(pr['phases']):
    tag = ph.get('tag', 'essential')
    # Every phase is part of the fixed price. The tag only says how important it is.
    toggle = f'<span class="sp-lock">✓ {u["included_tag"]}</span>'
    dl = ''.join(f'<li>{rich(d if isinstance(d, str) else d["h"])}</li>' for d in ph.get('deliverables', []))
    wk = ph.get('weeks')
    cards.append(f'''<article class="sp" data-id="{esc(ph['id'])}" data-price="{ph['price']}" data-weeks="{wk or 0}" data-name="{esc(ph['name'])}">
      <div class="sp-h">
        <div class="sp-n">{i+1:02d}</div>
        <div class="sp-t"><span class="sp-tag t-{tag}">{tag_lbl[tag]}</span><h3>{esc(ph['name'])}</h3>{f'<p>{rich(ph["summary"])}</p>' if ph.get('summary') else ''}</div>
        <div class="sp-p"><div class="sp-amt">{fmt_money(ph['price'], cur)}</div><div class="sp-wk">{esc(ph.get('duration') or (f'{wk} {u["weeks"] if wk != 1 else u["week"]}' if wk else ''))}</div>{toggle}</div>
      </div>
      {sp_body(u, ph, dl)}
    </article>''')
  pay = P['payment']
  summary = f'''<div class="sp-sum" data-cur="{esc(cur)}" data-pct="{pay.get('deposit_pct', 50)}" data-wk="{esc(u['weeks'])}">
      <div><div class="k">{u['total']}</div><div class="v" data-sp-total></div></div>
      <div><div class="k">{u['duration']}</div><div class="v" data-sp-weeks></div></div>
      <p>{rich(pay.get('schedule', ''))}</p>
    </div>'''
  inc = ''.join(f'<li><span class="ok">✓</span><span>{rich(v)}</span></li>' for v in pr.get('included', []))
  exc = ''.join(f'<div>{rich(v)}</div>' for v in pr.get('excluded', []))
  ie = ''
  if inc or exc:
    ie = f'''<div class="sec"><div class="ie">
      <div><div class="label">{u['included']}</div><ul class="check">{inc}</ul></div>
      <div><div class="label lx">{u['excluded']}</div><div class="excl">{exc}</div></div>
    </div></div>'''
  ex = ''
  if pr.get('examples'):
    e = pr['examples']
    shots = ''.join(f'<figure class="ex-c ex-{i+1}"><img src="{data_uri(os.path.join(T, "assets", im["src"]))}" alt="{esc(im.get("alt", ""))}" loading="lazy"></figure>' for i, im in enumerate(e['images'][:3]))
    ex = f'''<div class="sec"><div class="label">{esc(e['label'])}</div>
    {f'<h2>{rich(e["title"])}</h2>' if e.get('title') else ''}
    <div class="ex ex-n{len(e['images'][:3])}"><div class="ex-stage">{shots}</div></div>
    {f'<p class="ex-cap">{rich(e["caption"])}</p>' if e.get('caption') else ''}</div>'''
  gu = f'<div class="pp" style="margin-top:28px"><span class="ncp" role="img" aria-label="{u["partner"]}"></span><p><b>{u["guarantee"]}.</b> {rich(pr["guarantee"])}</p></div>' if pr.get('guarantee') else ''
  body = f'''  <h1>{rich(pr['title'])}</h1>
  <p class="lede">{rich(pr['intro'])}</p>
  <div class="sec-sm">
    <div class="label">{u['build_scope']}</div>
    <div class="sps{' wide' if any(ph.get('visual') for ph in pr['phases']) else ''}">{''.join(cards)}</div>
    {summary}
  </div>
  {ex}
  {ie}
  {gu}'''
  pg.add('proposal', u['proposal'], body)

def sec_about(pg, P, team, company):
  u = pg.u
  tm = ''
  for t in P['prepared_by'] + [x for x in P.get('team', []) if x not in P['prepared_by']]:
    m = team[t]
    tm += (f'<div class="tm"><div class="av" style="background:var(--{m["color"]})"><img src="{data_uri(os.path.join(T, "assets", m["photo"]))}" alt="{esc(m["name"])}" style="width:100%;height:100%;border-radius:50%;object-fit:cover;display:block"></div>'
           f'<h3>{esc(m["name"])}</h3><div class="role">{esc(m["role"][pg.lang])}</div></div>')
  if P.get('clients'):
    lib = json.loads(read(os.path.join(ROOT, 'data', 'clients.json')))
    logos = ''.join(
      f'<a class="clc" href="{esc(c["url"])}" target="_blank" rel="noopener"><div class="clc-logo"><img src="{data_uri(os.path.join(T, "assets", c["logo"]))}" alt="{esc(c["name"])}"></div>'
      f'<div class="clc-meta"><i>{u["we_did"]}</i><b>{esc(c["what"][pg.lang])}</b><span>{esc(c["where"][pg.lang])}</span></div></a>'
      for c in (lib[k] for k in P['clients']))
    logos_cls = 'clcs'
  else:
    logos = ''.join(f'<div class="cl"><span>{esc(u["client_logo"] if c["name"] == "Client logo" else c["name"])}</span></div>' for c in company['clients'])
    logos_cls = 'cls'
  body = f'''  <h1>{rich(P.get('about_title', 'Assigned team<br><em>for this project.</em>' if pg.lang == 'en' else 'Equipo asignado<br><em>para este proyecto.</em>'))}</h1>
  <div class="team">{tm}</div>
  <div class="ncpc"><span class="ncp" role="img" aria-label="{u['partner']}"></span><div><h3>{u['partner']}</h3><p>{u['partner_text']}</p></div></div>
  <div class="sec"><div class="label">{u['clients']}</div><div class="{logos_cls}">{logos}</div></div>'''
  pg.add('about', u['about'], body)

def sec_start(pg, P, company):
  u, pay = pg.u, P['payment']
  nx = ''.join(f'<li><div class="when">{esc(s["when"])}</div><div><h3>{esc(s["h"])}</h3><p>{rich(s.get("p", ""))}</p></div></li>' for s in P.get('next_steps', []))
  row = lambda k, v: f'<div><dt>{esc(k)}</dt><dd>{esc(v)}</dd><button type="button" class="acc-copy">{u["copy"]}</button></div>'
  accts = company['bank_accounts']
  tabs = ''.join(f'<button type="button" class="{"on" if i == 0 else ""}" data-bank="{a["id"]}">{esc(a["label"][pg.lang])}</button>' for i, a in enumerate(accts))
  banks = ''.join(f'<div class="acc-panel" data-bank="{a["id"]}"{"" if i == 0 else " hidden"}><dl class="acc-bank" style="margin:0">' + ''.join(row(k, v) for k, v in a['rows']) + '</dl></div>' for i, a in enumerate(accts))
  card = company.get('card')
  if card:
    tabs += f'<button type="button" data-bank="card">{esc(card["label"][pg.lang])}</button>'
    btn = (f'<a class="acc-btn" href="{esc(pay["stripe_url"])}" target="_blank" rel="noopener">{u["pay_card"]}</a>' if pay.get('stripe_url')
           else f'<p>{u["card_soon"]}</p>')
    banks += (f'<div class="acc-panel acc-stripe" data-bank="card" hidden><div class="k">{u["card_amount"].format(pct=card["fee_pct"])}</div>'
              f'<div class="amt2" data-acc-card></div><p>{u["card_text"]}</p>{btn}</div>')
  terms = '<ul>' + ''.join(f'<li><b>{esc(k)}.</b> {esc(v)}</li>' for k, v in company['terms'][pg.lang]) + (f'<li><b>{"Payment" if pg.lang == "en" else "Pago"}.</b> {rich(pay.get("schedule", ""))}</li>') + '</ul>'
  demo = f'<span class="demo">{u["demo"]}</span>' if company.get('demo') else ''
  acc = read(os.path.join(ROOT, 'components', 'accept', 'accept.html'))
  fill = {
    'proposal_id': P['slug'], 'first_step_name': u['scope_selected'],
    'deposit_amount': '<span data-acc-dep></span>', 'deposit_label': f'<span data-acc-dlabel></span>',
    'first_step_detail': f'<ul class="acc-items" data-acc-items></ul>', 'terms_html': terms,
    'accepted_scope_html': f'<div class="acc-step acc-scope-card"><h3>{u["accepted_scope"]}</h3><ul class="acc-items" data-acc-items></ul></div>',
    'bank_html': f'<div class="acc-tabs">{tabs}</div>{banks}', 'demo_badge': demo,
  }
  for k, v in fill.items():
    acc = acc.replace('{{' + k + '}}', v)
  # translate the fixed strings in the component
  for en_s, key in [('Accept proposal →', 'accept_btn'), ("You're accepting", 'accepting'), ('Full name', 'name'),
                    ('>Email<', 'email'), ('I accept this proposal and the', 'i_accept'), ('terms and conditions', 'terms'),
                    ('Read the terms', 'read_terms'), ('Accept and see payment details', 'submit'), ('Send the deposit', 'send_deposit'),
                    ('We take it from there', 'from_there'),
                    ('As soon as we receive your payment, we email you the next steps, including the link to book your kickoff.', 'from_there_text'),
                    ('Reset (test only)', 'reset')]:
    v = u[key]
    if en_s.startswith('>'):
      acc = acc.replace(en_s, f'>{v}<')
    else:
      acc = acc.replace(en_s, v)
  acc = acc.replace('<div class="label">Start</div>\n  <h2>Ready to <em>start?</em></h2>\n', '')
  acc = acc.replace('<div class="acc"', f'<div class="acc" data-fee="{(company.get("card") or {}).get("fee_pct", 0)}" data-api="{esc(P.get("accept_api", "/api/accept"))}" data-lang="{pg.lang}"', 1)
  h1 = f'''<h1>{rich(P.get('closing', 'Ready to build <em>your Eureka moment?</em>' if pg.lang == 'en' else '¿Listos para construir <em>tu momento Eureka?</em>'))}</h1>'''
  if P.get('closing_illustration'):
    h1 = f'<div class="st-close">{h1}<img src="{data_uri(os.path.join(T, "assets", "illustrations", P["closing_illustration"] + ".webp"))}" alt=""></div>'
  body = f'''  {h1}
  <p class="lede">{u['valid']} <b>{esc(fmt_date(P['valid_until'], pg.lang))}</b>. {u['starts']}: <b>{esc(P.get('start', ''))}</b>.</p>
  {f'<div class="sec-sm"><div class="label">{u["next"]}</div><ul class="next">{nx}</ul></div>' if nx else ''}
  {acc}'''
  pg.add('start', u['start'], body)

# ---------- page ----------
def build(slug):
  folder = os.path.join(ROOT, 'proposals', slug)
  P = json.loads(read(os.path.join(folder, 'proposal.json')))
  P['slug'] = slug
  lang = P.get('lang', 'en')
  team = json.loads(read(os.path.join(ROOT, 'data', 'team.json')))
  company = json.loads(read(os.path.join(ROOT, 'data', 'company.json')))
  pg = Page(P, lang)
  sec_cover(pg, P, team)
  sec_context(pg, P)
  if P.get('focus'):
    sec_focus(pg, P)
  sec_proposal(pg, P)
  sec_about(pg, P, team, company)
  sec_start(pg, P, company)

  css = read(os.path.join(T, 'design.css')) + '\n' + read(os.path.join(T, 'proposal.css')) + '\n' + read(os.path.join(ROOT, 'components', 'accept', 'accept.css'))
  logo = read(os.path.join(T, 'assets', 'logo.svg'))
  strings = {k: UI[lang][k] for k in ('total', 'accepted_by', 'on', 'emailed', 'err_name', 'err_email', 'err_terms', 'weeks', 'week', 'on_accept', 'deposit')}
  title = f'{"Proposal" if lang == "en" else "Propuesta"} · Eureka × {P["client"]["company"]}'
  out = f'''<!DOCTYPE html>
<html lang="{lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="robots" content="noindex,nofollow">
<title>{esc(title)}</title>
<style>
{css}
</style>
</head>
<body>

<header class="top">
  <div class="top-in">
    <div class="brand">{logo}<span class="sep"></span><span class="who">{UI[lang]['proposal_for']} {esc(P['client']['company'])}</span></div>
    <nav class="nav" id="nav" aria-label="Sections"></nav>
  </div>
</header>

<main class="wrap">
{chr(10).join(pg.sections)}
</main>

<footer class="foot">{logo}<span>Notion Certified Consulting Partner</span><span class="r">eureka.ceo</span></footer>

<script>
{read(os.path.join(T, 'nav.js'))}
</script>
<script>
window.EUREKA_UI = {json.dumps(strings, ensure_ascii=False)};
{read(os.path.join(T, 'scope.js'))}
</script>
<script>
{read(os.path.join(ROOT, 'components', 'accept', 'accept.js'))}
</script>
</body>
</html>
'''
  left = re.findall(r'\{\{\w+\}\}', out)
  if left:
    sys.exit(f'Unfilled placeholders: {left}')
  with open(os.path.join(folder, 'index.html'), 'w', encoding='utf-8') as f:
    f.write(out)
  # Data for /api/accept (prices are recomputed on the server; bank details and kickoff link go in the email)
  api_dir = os.path.join(ROOT, 'proposals', 'api', '_proposals')
  os.makedirs(api_dir, exist_ok=True)
  server = {
    'slug': slug, 'lang': lang, 'company': P['client']['company'], 'currency': P['proposal'].get('currency', 'USD'),
    'deposit_pct': P['payment'].get('deposit_pct', 50),
    'phases': [{'id': ph['id'], 'name': ph['name'], 'price': ph['price'], 'tag': ph.get('tag', 'essential'),
} for ph in P['proposal']['phases']],
    'bank_accounts': [{'label': a['label'][lang], 'rows': a['rows']} for a in company['bank_accounts']],
    'notion_page_id': P.get('notion_page_id'),
    'card_fee_pct': (company.get('card') or {}).get('fee_pct'), 'stripe_url': P['payment'].get('stripe_url'), 'url': f'https://proposals.eureka.ceo/{slug}',
  }
  with open(os.path.join(api_dir, f'{slug}.json'), 'w', encoding='utf-8') as f:
    json.dump(server, f, ensure_ascii=False, indent=2)
  print(f'built proposals/{slug}/index.html ({len(out)//1024} KB)')

if __name__ == '__main__':
  if len(sys.argv) < 2:
    sys.exit(__doc__)
  if sys.argv[1] == '--all':
    for s in sorted(os.listdir(os.path.join(ROOT, 'proposals'))):
      if os.path.exists(os.path.join(ROOT, 'proposals', s, 'proposal.json')):
        build(s)
  else:
    build(sys.argv[1])
