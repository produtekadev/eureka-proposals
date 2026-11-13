/* Scope builder: optional phases can be switched off; totals and deposit update.
   Exposes window.EUREKA_SCOPE() -> {items, total, weeks, deposit, currency, pct} for the accept block. */
(function(){
  var sum=document.querySelector('.sp-sum'); if(!sum) return;
  var cur=sum.dataset.cur, pct=+sum.dataset.pct, U=window.EUREKA_UI||{};
  function money(n){return cur+' '+Math.round(n).toLocaleString('en-US')}
  function state(){
    var items=[],off=[],total=0,weeks=0;
    [].forEach.call(document.querySelectorAll('.sp'),function(c){
      var cb=c.querySelector('input[data-sp]'), on=!cb||cb.checked;
      c.classList.toggle('off',!on);
      var it={id:c.dataset.id,name:c.dataset.name,price:+c.dataset.price,n:c.querySelector('.sp-n').textContent};
      if(on){items.push(it);total+=it.price;weeks+=+c.dataset.weeks}else off.push(it);
    });
    return {items:items,off:off,total:total,weeks:weeks,deposit:total*pct/100,currency:cur,pct:pct};
  }
  function render(){
    var s=state();
    sum.querySelector('[data-sp-total]').textContent=money(s.total);
    sum.querySelector('[data-sp-weeks]').textContent=s.weeks?s.weeks+' '+(s.weeks===1?(U.week||'week'):(U.weeks||'weeks')):'–';
    sum.querySelector('[data-sp-dep]').textContent=money(s.deposit);
    document.dispatchEvent(new CustomEvent('scope:change',{detail:s}));
  }
  window.EUREKA_SCOPE=state;
  window.EUREKA_SCOPE_LOCK=function(ids){
    [].forEach.call(document.querySelectorAll('input[data-sp]'),function(cb){
      if(ids) cb.checked=ids.indexOf(cb.dataset.sp)>-1;
      cb.disabled=true;
    });
    render();
  };
  window.EUREKA_SCOPE_UNLOCK=function(){[].forEach.call(document.querySelectorAll('input[data-sp]'),function(cb){cb.disabled=false})};
  document.addEventListener('change',function(e){if(e.target.matches&&e.target.matches('input[data-sp]')) render()});
  render();
})();
