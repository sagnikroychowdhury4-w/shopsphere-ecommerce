
let current=1, totalPages=1;
async function loadStats(){
  const r=await fetch('/stats'); const s=await r.json();
  document.getElementById('stats').innerHTML=`<div class="stat"><b>${Number(s.products).toLocaleString()}</b>Products</div><div class="stat"><b>${Number(s.reviews).toLocaleString()}</b>Reviews</div><div class="stat"><b>${s.avg_rating}</b>Avg rating</div>`;
}
async function loadReviews(page=1){
  current=page;
  const params=new URLSearchParams({page,limit:12});
  const q=document.getElementById('search').value.trim();
  const rating=document.getElementById('rating').value;
  const sentiment=document.getElementById('sentiment').value;
  if(q) params.set('q',q); if(rating) params.set('rating',rating); if(sentiment) params.set('sentiment',sentiment);
  const r=await fetch('/reviews?'+params); const data=await r.json(); totalPages=data.pages;
  document.getElementById('reviews').innerHTML=data.items.map(x=>`
    <article class="card">
      <div class="top"><div><div class="product">${x.name}</div><div class="brand">${x.brand}</div></div><div class="stars">${'★'.repeat(x.reviews_rating)}${'☆'.repeat(5-x.reviews_rating)}</div></div>
      <div class="title">${x.reviews_title}</div><div class="body">${x.reviews_text}</div>
      <div class="meta"><span>${x.reviews_username} · ${x.reviews_date}</span><span class="pill">${x.sentiment}</span></div>
    </article>`).join('');
  document.getElementById('page').textContent=`Page ${data.page} of ${data.pages}`;
  document.getElementById('prev').disabled=current<=1; document.getElementById('next').disabled=current>=totalPages;
}
document.getElementById('prev').onclick=()=>loadReviews(current-1);
document.getElementById('next').onclick=()=>loadReviews(current+1);
loadStats(); loadReviews();
