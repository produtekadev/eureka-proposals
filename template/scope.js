/* Scope summary: adds up every phase (all are part of the fixed price) and fills the totals box.
   Exposes window.EUREKA_SCOPE() -> {items, total, weeks, deposit, currency, pct} for the accept block. */
(function(){
  var sum=document.querySelector('.sp-sum'); if(!sum) return;
  var cur=sum.dataset.cur, pct=+sum.dataset.pct, U=window.EUREKA_UI||{};
  function money(n){return cur+' '+Math.round(n).toLocaleString('en-US')}
  function state(){
    var items=[],total=0,weeks=0;
    [].forEach.call(document.querySelectorAll('.sp'),function(c){
      var it={id:c.dataset.id,name:c.dataset.name,price:+c.dataset.price,n:c.querySelector('.sp-n').textContent};
      items.push(it);total+=it.price;weeks+=+c.dataset.weeks;
    });
    return {items:items,total:total,weeks:weeks,deposit:total*pct/100,currency:cur,pct:pct};
  }
  var s=state();
  sum.querySelector('[data-sp-total]').textContent=money(s.total);
  sum.querySelector('[data-sp-weeks]').textContent=s.weeks?s.weeks+' '+(s.weeks===1?(U.week||'week'):(U.weeks||'weeks')):'–';
  sum.querySelector('[data-sp-dep]').textContent=money(s.deposit);
  window.EUREKA_SCOPE=state;
})();
