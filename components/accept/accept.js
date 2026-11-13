/* Accept proposal. Saves acceptance in this browser only (demo).
   TODO: post acceptance to an endpoint that updates Notion and notifies Slack. */
(function(){
  var el=document.getElementById('accept'); if(!el) return;
  var key='eureka-accept:'+el.dataset.key, form=el.querySelector('form'), err=el.querySelector('.acc-err');
  function load(){try{return JSON.parse(localStorage.getItem(key)||'null')}catch(e){return null}}
  function save(v){try{localStorage.setItem(key,JSON.stringify(v))}catch(e){}}
  function clear(){try{localStorage.removeItem(key)}catch(e){}}
  function done(a){
    var d=new Date(a.at);
    el.querySelector('.acc-ok span').textContent='Accepted by '+a.name+', '+a.role+', on '+d.toLocaleDateString('en-US',{month:'long',day:'numeric',year:'numeric'})+'.';
    el.classList.remove('open'); el.classList.add('done');
  }
  el.querySelector('[data-acc-open]').addEventListener('click',function(){el.classList.add('open');el.querySelector('#acc-name').focus()});
  el.querySelector('[data-acc-terms]').addEventListener('click',function(e){e.preventDefault();el.querySelector('#acc-terms').open=true});
  form.addEventListener('submit',function(e){
    e.preventDefault();
    var f=form.elements, name=f.name.value.trim(), role=f.role.value.trim(), email=f.email.value.trim();
    if(!name||!role) return err.textContent='Please add your name and role.';
    if(!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email)) return err.textContent='Please add a valid email.';
    if(!f.terms.checked) return err.textContent='Please accept the terms to continue.';
    err.textContent='';
    var a={name:name,role:role,email:email,at:new Date().toISOString()};
    save(a); done(a);
    el.scrollIntoView({behavior:'smooth',block:'start'});
  });
  [].forEach.call(el.querySelectorAll('.acc-tabs button'),function(b){
    b.addEventListener('click',function(){
      [].forEach.call(el.querySelectorAll('.acc-tabs button'),function(x){x.classList.toggle('on',x===b)});
      [].forEach.call(el.querySelectorAll('.acc-bank'),function(x){x.hidden=x.dataset.bank!==b.dataset.bank});
    });
  });
  el.addEventListener('click',function(e){
    var c=e.target.closest('.acc-copy'); if(!c) return;
    var v=c.parentNode.querySelector('dd').textContent;
    (navigator.clipboard?navigator.clipboard.writeText(v):Promise.reject()).then(function(){c.textContent='Copied';setTimeout(function(){c.textContent='Copy'},1500)},function(){});
  });
  el.querySelector('[data-acc-reset]').addEventListener('click',function(){clear();el.classList.remove('done');form.reset()});
  var a=load(); if(a) done(a);
})();
