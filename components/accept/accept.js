/* Accept proposal.
   - Reads the chosen scope from the scope builder (window.EUREKA_SCOPE) when present.
   - Saves the acceptance in the browser, so a returning client sees the payment step.
   - Posts the acceptance to data-api (default /api/accept), which emails the client and the team.
     If the endpoint isn't there (local file, preview), the page still works. */
(function(){
  var el=document.getElementById('accept'); if(!el) return;
  var U=window.EUREKA_UI||{}, lang=el.dataset.lang||'en';
  var key='eureka-accept:'+el.dataset.key, form=el.querySelector('form'), err=el.querySelector('.acc-err');
  function t(k,d){return U[k]||d}
  function load(){try{return JSON.parse(localStorage.getItem(key)||'null')}catch(e){return null}}
  function save(v){try{localStorage.setItem(key,JSON.stringify(v))}catch(e){}}
  function clear(){try{localStorage.removeItem(key)}catch(e){}}
  function money(c,n){return c+' '+Math.round(n).toLocaleString('en-US')}
  function scope(){return window.EUREKA_SCOPE?window.EUREKA_SCOPE():null}
  function paint(s){
    if(!s) return;
    var dep=money(s.currency,s.deposit);
    [].forEach.call(el.querySelectorAll('[data-acc-dep]'),function(x){x.textContent=dep});
    [].forEach.call(el.querySelectorAll('[data-acc-dlabel]'),function(x){x.textContent=s.pct+'% '+t('on_accept','when you accept')+' · '+t('total','Total')+' '+money(s.currency,s.total)});
    [].forEach.call(el.querySelectorAll('[data-acc-scope]'),function(x){x.textContent=s.items.map(function(i){return i.name}).join(' · ')});
  }
  function done(a){
    var d=new Date(a.at);
    el.querySelector('.acc-ok span').textContent=t('accepted_by','Accepted by')+' '+a.name+', '+a.role+', '+t('on','on')+' '+d.toLocaleDateString(lang==='es'?'es-CO':'en-US',{month:'long',day:'numeric',year:'numeric'})+'.';
    if(a.scope){paint(a.scope); if(window.EUREKA_SCOPE_LOCK) window.EUREKA_SCOPE_LOCK(a.scope.items.map(function(i){return i.id}))}
    var m=el.querySelector('.acc-mail');
    if(m){m.hidden=!a.emailed; m.textContent=t('emailed','We also sent these details to')+' '+a.email+'.'}
    el.classList.remove('open'); el.classList.add('done');
  }
  document.addEventListener('scope:change',function(e){if(!el.classList.contains('done')) paint(e.detail)});
  paint(scope());
  el.querySelector('[data-acc-open]').addEventListener('click',function(){el.classList.add('open');el.querySelector('#acc-name').focus()});
  el.querySelector('[data-acc-terms]').addEventListener('click',function(e){e.preventDefault();el.querySelector('#acc-terms').open=true});
  // No real form submit: some embedded viewers block it, so the button calls accept() directly.
  form.addEventListener('submit',function(e){e.preventDefault();accept()});
  el.querySelector('[data-acc-submit]').addEventListener('click',accept);
  form.addEventListener('keydown',function(e){if(e.key==='Enter'&&e.target.tagName==='INPUT'){e.preventDefault();accept()}});
  function accept(){
    var f=form.elements, name=f.name.value.trim(), role=f.role.value.trim(), email=f.email.value.trim();
    if(!name||!role) return err.textContent=t('err_name','Please add your name and role.');
    if(!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email)) return err.textContent=t('err_email','Please add a valid email.');
    if(!f.terms.checked) return err.textContent=t('err_terms','Please accept the terms to continue.');
    err.textContent='';
    var a={name:name,role:role,email:email,at:new Date().toISOString(),scope:scope(),emailed:false};
    save(a); done(a);
    el.scrollIntoView({behavior:'smooth',block:'start'});
    send(a);
  }
  function send(a){
    var api=el.dataset.api; if(!api||location.protocol==='file:') return;
    var body={proposal:el.dataset.key,name:a.name,role:a.role,email:a.email,at:a.at,items:a.scope?a.scope.items.map(function(i){return i.id}):null};
    try{
      fetch(api,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)})
        .then(function(r){return r.ok?r.json():null})
        .then(function(j){if(j&&j.emailed){a.emailed=true;save(a);done(a)}})
        .catch(function(){});
    }catch(e){}
  }
  [].forEach.call(el.querySelectorAll('.acc-tabs button'),function(b){
    b.addEventListener('click',function(){
      [].forEach.call(el.querySelectorAll('.acc-tabs button'),function(x){x.classList.toggle('on',x===b)});
      [].forEach.call(el.querySelectorAll('.acc-bank'),function(x){x.hidden=x.dataset.bank!==b.dataset.bank});
    });
  });
  el.addEventListener('click',function(e){
    var c=e.target.closest('.acc-copy'); if(!c) return;
    var v=c.parentNode.querySelector('dd').textContent, lbl=c.textContent;
    (navigator.clipboard?navigator.clipboard.writeText(v):Promise.reject()).then(function(){c.textContent='✓';setTimeout(function(){c.textContent=lbl},1500)},function(){});
  });
  el.querySelector('[data-acc-reset]').addEventListener('click',function(){
    clear();el.classList.remove('done');form.reset();
    if(window.EUREKA_SCOPE_UNLOCK) window.EUREKA_SCOPE_UNLOCK();
    paint(scope());
  });
  var a=load(); if(a) done(a);
})();
