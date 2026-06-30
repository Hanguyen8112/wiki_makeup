const P={};
document.querySelectorAll('.page').forEach(p=>P[p.id.replace('p-','')]=p);
function go(id){
  document.querySelectorAll('.page').forEach(p=>p.classList.remove('active'));
  if(P[id]) P[id].classList.add('active');
  document.querySelectorAll('.nav-item').forEach(b=>b.classList.toggle('active',b.getAttribute('onclick')===`go('${id}')`));
  if(window.innerWidth<=780) closeSB();
  window.scrollTo(0,0);
}
function tCat(btn){btn.classList.toggle('open');btn.nextElementSibling.classList.toggle('open');}
function toggleSidebar(){document.getElementById('sidebar').classList.toggle('open');document.getElementById('overlay').classList.toggle('show');}
function closeSB(){document.getElementById('sidebar').classList.remove('open');document.getElementById('overlay').classList.remove('show');}
