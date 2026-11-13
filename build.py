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
    'valid': 'Proposal valid until', 'starts': 'Projected start',
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
    'scope_selected': 'Scope and investment', 'client_logo': 'Client logo', 'we_did': 'What we did', 'accepted_scope': 'Accepted scope',
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
    'valid': 'Propuesta válida hasta', 'starts': 'Inicio proyectado',
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
    'scope_selected': 'Alcance e inversión', 'client_logo': 'Logo de cliente', 'we_did': 'Qué hicimos', 'accepted_scope': 'Alcance aceptado',
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
  if glance:
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
    <div class="cards">{pains}</div>
  </div>
  {quote}
  {opp}'''
  pg.add('context', u['context'], body)

def sec_focus(pg, P):
  u, f = pg.u, P['focus']
  li = lambda xs: ''.join(f'<li>{rich(v)}</li>' for v in xs)
  body = f'''  <h1>{rich(f['title'])}</h1>
  <p class="lede">{rich(f['statement'])}</p>
  <div class="fx">
    <div class="fx-c"><div class="k">{u['asked']}</div><ul>{li(f['asked'])}</ul></div>
    <div class="fx-c on"><div class="k">{u['recommend']}</div><ul>{li(f['recommend'])}</ul></div>
  </div>
  {f'<p class="note" style="margin-top:18px">{rich(f["why"])}</p>' if f.get('why') else ''}'''
  pg.add('focus', u['focus'], body)

def sec_proposal(pg, P):
  u, pr, cur = pg.u, P['proposal'], P['proposal'].get('currency', 'USD')
  tag_lbl = {'essential': u['essential'], 'recommended': u['recommended'], 'optional': u['optional']}
  cards = []
  for i, ph in enumerate(pr['phases']):
    tag = ph.get('tag', 'essential')
    # Every phase is part of the fixed price. The tag only says how important it is.
    toggle = f'<span class="sp-lock">✓ {u["included_tag"]}</span>'
    dl = ''.join(f'<li>{rich(d)}</li>' for d in ph.get('deliverables', []))
    wk = ph.get('weeks')
    cards.append(f'''<article class="sp" data-id="{esc(ph['id'])}" data-price="{ph['price']}" data-weeks="{wk or 0}" data-name="{esc(ph['name'])}">
      <div class="sp-h">
        <div class="sp-n">{i+1:02d}</div>
        <div class="sp-t"><span class="sp-tag t-{tag}">{tag_lbl[tag]}</span><h3>{esc(ph['name'])}</h3>{f'<p>{rich(ph["summary"])}</p>' if ph.get('summary') else ''}</div>
        <div class="sp-p"><div class="sp-amt">{fmt_money(ph['price'], cur)}</div><div class="sp-wk">{esc(ph.get('duration') or (f'{wk} {u["weeks"] if wk != 1 else u["week"]}' if wk else ''))}</div>{toggle}</div>
      </div>
      {f'<ul class="sp-dl">{dl}</ul>' if dl else ''}
    </article>''')
  pay = P['payment']
  summary = f'''<div class="sp-sum" data-cur="{esc(cur)}" data-pct="{pay.get('deposit_pct', 50)}" data-wk="{esc(u['weeks'])}">
      <div><div class="k">{u['total']}</div><div class="v" data-sp-total></div></div>
      <div><div class="k">{u['duration']}</div><div class="v" data-sp-weeks></div></div>
      <div><div class="k">{u['deposit']} {u['on_accept']}</div><div class="v" data-sp-dep></div></div>
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
  gu = f'<div class="pp" style="margin-top:28px"><span class="ncp" role="img" aria-label="{u["partner"]}"></span><p><b>{u["guarantee"]}.</b> {rich(pr["guarantee"])}</p></div>' if pr.get('guarantee') else ''
  body = f'''  <h1>{rich(pr['title'])}</h1>
  <p class="lede">{rich(pr['intro'])}</p>
  <div class="sec-sm">
    <div class="label">{u['build_scope']}</div>
    <div class="sps">{''.join(cards)}</div>
    {summary}
  </div>
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
  body = f'''  <h1>{rich(P.get('closing', 'Ready to build <em>your Eureka moment?</em>' if pg.lang == 'en' else '¿Listos para construir <em>tu momento Eureka?</em>'))}</h1>
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
