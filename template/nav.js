(function(){
  var pages=[].slice.call(document.querySelectorAll('.page'));
  var nav=document.getElementById('nav');
  pages.forEach(function(p,i){
    var b=document.createElement('button');
    b.innerHTML='<i>'+p.dataset.n+'</i>'+p.dataset.name;
    b.onclick=function(){show(i)};
    nav.appendChild(b);
  });
  var btns=[].slice.call(nav.children);
  function pagerHTML(i){
    var h='';
    if(i>0){var p=pages[i-1];h+='<a href="#'+p.id+'" data-go="'+(i-1)+'"><div class="k">← Previous</div><div class="t"><i>'+p.dataset.n+'</i>'+p.dataset.name+'</div></a>';}
    if(i<pages.length-1){var n=pages[i+1];h+='<a class="nx" href="#'+n.id+'" data-go="'+(i+1)+'"><div class="k">Next →</div><div class="t"><i>'+n.dataset.n+'</i>'+n.dataset.name+'</div></a>';}
    return h;
  }
  pages.forEach(function(p,i){
    var pg=p.querySelector('.pager'); if(!pg) return;
    pg.innerHTML=pagerHTML(i);
    [].forEach.call(pg.querySelectorAll('a'),function(a){a.onclick=function(e){e.preventDefault();show(+a.dataset.go)}});
  });
  var cur=-1;
  function show(i){
    if(i<0||i>=pages.length) return;
    cur=i;
    pages.forEach(function(p,j){p.classList.toggle('on',j===i)});
    btns.forEach(function(b,j){b.classList.toggle('on',j===i)});
    if(history.replaceState) history.replaceState(null,'','#'+pages[i].id);
    window.scrollTo(0,0);
    var ab=btns[i]; if(ab&&ab.scrollIntoView) ab.scrollIntoView({block:'nearest',inline:'center'});
  }
  document.addEventListener('keydown',function(e){
    if(e.target.closest&&e.target.closest('input,textarea')) return;
    if(e.key==='ArrowRight') show(cur+1);
    if(e.key==='ArrowLeft') show(cur-1);
  });
  function fromHash(){
    var h=location.hash.slice(1), idx=0;
    pages.forEach(function(p,i){if(p.id===h) idx=i});
    if(idx!==cur) show(idx);
  }
  window.addEventListener('hashchange',fromHash);
  fromHash();

})();
