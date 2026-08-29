(() => {
 const tg=window.Telegram?.WebApp;if(tg){tg.ready();tg.expand()}
 const initData=tg?.initData||"";let state=null,traits=null,sellingId=null,invFilter="all";
 const $=id=>document.getElementById(id);const headers=()=>({"Content-Type":"application/json","X-Telegram-Init-Data":initData});
 const esc=s=>String(s??"").replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#039;"}[c]));
 let tt;function toast(m){const e=$("toast");e.textContent=m;e.classList.add("show");clearTimeout(tt);tt=setTimeout(()=>e.classList.remove("show"),2200)}
 function haptic(t="light"){try{tg?.HapticFeedback?.impactOccurred(t)}catch{}}
 async function api(path,opt={}){const r=await fetch(path,{...opt,headers:{...headers(),...(opt.headers||{})}});let d={};try{d=await r.json()}catch{}if(!r.ok)throw new Error(d.detail||"Ошибка");return d}

 const modelPalettes={
  glitch:["#48f0db","#ff4f9c","#774dff","#d9fffb"],secret:["#8c2947","#d89bad","#2e1924","#fff1f4"],teasing:["#ff88a8","#ea4678","#a71b59","#fff1f7"],
  zombie:["#82a66c","#b9d49a","#70536f","#e8f6cf"],acid:["#b9ff4b","#45da70","#251a48","#eeffc0"],comics:["#ffda36","#fb4b7d","#4e62e6","#fff0a7"],
  frost:["#d8f6ff","#6cbde7","#4e6eb0","#ffffff"],fire:["#ffcc45","#f35b32","#8d1730","#fff0a4"],melon:["#ff899b","#ffc75d","#438f64","#fff0b3"],
  neon:["#ff43b6","#784dff","#34e8c1","#fdf2ff"],pop:["#ff4e98","#ffdb39","#3678ff","#fff0aa"],punk:["#e93d7d","#7b39d4","#17131f","#f9cce2"],
  red:["#ff304e","#bd1639","#42111f","#ffd6df"],sweet:["#ff9cc4","#ff5ca0","#8c4ae6","#fff3fa"],coral:["#ff8a68","#e34f79","#34b9b8","#fff1d8"],
  devil:["#e83a53","#661634","#131018","#ffc5d0"],metal:["#c4c9d3","#747b88","#2b3037","#f8fbff"],galaxy:["#cb55ff","#5b36c8","#151b50","#e6ccff"],
  gold:["#ffd46a","#e7952f","#7b4024","#fff1b5"],voltage:["#5dfde8","#4d63ff","#1f214b","#ffffff"],leopard:["#dc9f48","#71452a","#261e1a","#ffe2a8"],
  lizard:["#6ad57b","#288b67","#173b34","#e8ffd8"],minimal:["#ee668e","#a62b55","#ebe5e8","#fff"],night:["#9356f1","#4a2b84","#171328","#eadcff"],
  padme:["#e9b8af","#b95f70","#503542","#fff1ec"],succubus:["#dc3169","#66214d","#241127","#ffd0e1"],berry:["#e85081","#922757","#42162e","#ffd7e5"],
  vampire:["#de244b","#75152f","#161116","#ffd0d9"],avatar:["#5db6ff","#5660dc","#1a2b54","#e5f3ff"],cold:["#bce9ff","#62a6d2","#44588a","#fff"],
  daring:["#ff666f","#c42d55","#6e1836","#ffe3e5"],femme:["#e36a94","#89315b","#20141c","#ffe0ec"],glamour:["#f595c8","#d54798","#722b6f","#fff1fb"],
  glossy:["#ff617f","#d92e62","#85183e","#fff0f4"],summer:["#ff805d","#ec4667","#7a2549","#fff0da"],hypnotic:["#8c63ff","#ec55bc","#35d4d0","#f1e9ff"],
  lady:["#b84b88","#5c275f","#17131c","#f6d7ea"],manga:["#ff90aa","#f25278","#52306e","#fff0f4"],morticia:["#b84269","#41243e","#141217","#e6c8d2"],
  mystique:["#7b5de7","#3f4eb1","#17244c","#d9d9ff"],pepe:["#70dc69","#e64b79","#2c7646","#e7ffd6"],mamba:["#f45bbf","#8c39a5","#311a53","#ffd8f7"],
  queen:["#e35e90","#9d356d","#e1b65a","#fff0bc"],rainbow:["#ff5c70","#704cff","#35d2b4","#fff"],sour:["#b4e54f","#5baa53","#963a63","#f5ffba"],
  mint:["#76e4b7","#38a986","#8a3e6a","#e2fff2"],sunset:["#ff9560","#dc4e80","#6a3d8d","#ffe6c7"],coil:["#e86d61","#8f3a77","#3f275a","#ffd8d0"],
  snake:["#67c779","#347c55","#dd668f","#e4ffd9"],velvet:["#c63d74","#722351","#2f1328","#ffd7e8"],base:["#ff7399","#c72e66","#8b204d","#fff2f6"]
 };

 function sharpTongueSVG(style="base",large=false){
   const p=modelPalettes[style]||modelPalettes.base;
   // Distinct decorative overlays for model groups
   const fx={
    glitch:`<g opacity=".8"><rect x="72" y="100" width="54" height="7" fill="${p[3]}"/><rect x="188" y="126" width="46" height="6" fill="${p[2]}"/><rect x="130" y="174" width="62" height="5" fill="${p[3]}"/></g>`,
    galaxy:`<g fill="${p[3]}"><circle cx="93" cy="93" r="4"/><circle cx="218" cy="103" r="3"/><circle cx="148" cy="64" r="2.5"/></g>`,
    voltage:`<path d="M204 72l-18 27 17-2-21 34" fill="none" stroke="${p[3]}" stroke-width="7" stroke-linecap="round" stroke-linejoin="round"/>`,
    leopard:`<g fill="${p[2]}" opacity=".75"><ellipse cx="107" cy="101" rx="8" ry="5"/><ellipse cx="194" cy="91" rx="9" ry="5"/><ellipse cx="226" cy="126" rx="7" ry="4"/></g>`,
    vampire:`<path d="M112 131l13 22 9-24M188 130l-11 23-10-24" fill="${p[3]}" opacity=".92"/>`,
    rainbow:`<path d="M77 82q81-53 164 0" fill="none" stroke="${p[3]}" stroke-width="7" opacity=".55"/><path d="M84 91q74-45 150 0" fill="none" stroke="${p[0]}" stroke-width="5" opacity=".7"/>`,
    pepe:`<g><ellipse cx="101" cy="104" rx="17" ry="12" fill="#fff"/><ellipse cx="219" cy="104" rx="17" ry="12" fill="#fff"/><circle cx="104" cy="106" r="6" fill="#1b2c20"/><circle cx="216" cy="106" r="6" fill="#1b2c20"/></g>`
   }[style]||"";
   return `<svg viewBox="0 0 320 250" aria-hidden="true">
    <ellipse cx="160" cy="222" rx="87" ry="13" fill="rgba(0,0,0,.18)"/>
    <g class="lips-core">
      <path d="M47 112 C86 62 118 73 160 91 C202 73 235 62 273 112 C240 141 208 151 160 149 C112 151 80 141 47 112Z" fill="${p[0]}"/>
      <path d="M48 116 C91 137 121 137 160 128 C199 137 230 137 272 116 C246 174 211 191 160 190 C109 191 73 174 48 116Z" fill="${p[1]}"/>
      <path d="M159 132 C181 137 208 137 222 128 C218 180 204 216 175 229 C151 237 129 218 132 193 C137 164 143 145 159 132Z" fill="${p[0]}"/>
      <path d="M171 155 C170 184 165 207 157 225" fill="none" stroke="${p[2]}" stroke-width="5" opacity=".46" stroke-linecap="round"/>
      <path d="M97 100 C119 87 141 91 157 98" fill="none" stroke="${p[3]}" stroke-width="7" opacity=".52" stroke-linecap="round"/>
      ${fx}
    </g>
   </svg>`;
 }

 function pat(icon){return `${icon}　${icon}　${icon}<br>　${icon}　${icon}<br>${icon}　${icon}　${icon}`}

 function collectibleHTML(item,{badge=true}={}){
   const upgraded=!!item.collectible_no;
   const c1=upgraded?(item.backdrop_c1||"#261839"):"#2b1a35";
   const c2=upgraded?(item.backdrop_c2||"#7c4f9c"):"#6e3b7c";
   const icon=upgraded?(item.pattern_icon||"✦"):"✦";
   const style=upgraded?(item.model_style||"base"):"base";
   const num=upgraded?`#${item.collectible_no}`:"BASE";
   const model=upgraded?(item.model||"Sharp Tongue"):"Sharp Tongue";
   return `<div class="collectible-shell" style="--bg1:${c1};--bg2:${c2}">
     <div class="collectible-bg"></div><div class="collectible-aurora"></div>
     <div class="pattern-field">${pat(icon)}</div>
     ${badge?`<span class="num-badge">${num}</span>${upgraded?`<span class="model-badge">${esc(model)}</span>`:""}`:""}
     <div class="collectible-art">${sharpTongueSVG(style)}</div>
     <div class="shine-sweep"></div>
   </div>`;
 }

 function attrs(i){return i.collectible_no?`<div class="attrs">${esc(i.model)} · ${esc(i.backdrop)} · ${esc(i.pattern)}</div>`:`<div class="attrs">Не улучшен · 1 бесплатный roll</div>`}
 function inventoryCard(i){
   let acts="";
   if(i.listed) acts=`<button class="card-btn ghost cancel-btn" data-id="${i.id}">Снять · ${Number(i.listing_price_ton).toFixed(3)} TON</button>`;
   else{if(!i.upgrade_used)acts+=`<button class="card-btn upgrade-btn" data-id="${i.id}">✨ Улучшить</button>`;acts+=`<button class="card-btn ghost sell-btn" data-id="${i.id}" data-label="${i.collectible_no?"#"+i.collectible_no:"обычный"}">Продать</button>`}
   return `<article class="gift-card">${collectibleHTML(i)}<div class="card-body"><h3>Sharp Tongue ${i.collectible_no?"#"+i.collectible_no:""}</h3>${attrs(i)}<div class="actions">${acts}</div></div></article>`;
 }
 function marketCard(i){
   const mine=i.seller_id===state.user.id;
   return `<article class="gift-card">${collectibleHTML(i)}<div class="card-body"><h3>Sharp Tongue ${i.collectible_no?"#"+i.collectible_no:""}</h3>${attrs(i)}<div class="price">${Number(i.price_ton).toFixed(3)} TON</div><div class="actions">${mine?`<button class="card-btn ghost cancel-btn" data-id="${i.gift_id}">Снять лот</button>`:`<button class="card-btn buy-market-btn" data-listing="${i.listing_id}">Купить</button>`}</div></div></article>`;
 }

 function filteredInventory(){const a=state.inventory;if(invFilter==="upgraded")return a.filter(x=>x.collectible_no);if(invFilter==="base")return a.filter(x=>!x.collectible_no);return a}
 function filteredMarket(){let a=[...state.market];const q=$("marketSearch").value.trim().toLowerCase();if(q)a=a.filter(x=>String(x.collectible_no||"").includes(q.replace("#",""))||String(x.model||"").toLowerCase().includes(q));const s=$("marketSort").value;if(s==="cheap")a.sort((x,y)=>x.price_ton_nano-y.price_ton_nano);if(s==="expensive")a.sort((x,y)=>y.price_ton_nano-x.price_ton_nano);return a}
 function renderInventory(){const a=filteredInventory();$("inventoryGrid").innerHTML=a.map(inventoryCard).join("");$("inventoryEmpty").classList.toggle("hidden",a.length>0);bindDynamic()}
 function renderMarket(){const a=filteredMarket();$("marketGrid").innerHTML=a.map(marketCard).join("");$("marketEmpty").classList.toggle("hidden",a.length>0);$("marketCount").textContent=a.length;bindDynamic()}
 function render(){
   const {user,stats,config}=state;
   $("hello").textContent=`${user.first_name||"Player"} · Sharp Tongue`; $("tonBalance").textContent=Number(stats.ton).toFixed(2);
   $("supplyText").textContent=`${stats.minted}`;$("shopSupplyMini").textContent="∞ шт.";
   $("buyStarsBtn").textContent=`Купить · ${config.price_stars} ⭐`;$("buyTonBtn").textContent=`Купить · ${Number(config.price_ton).toFixed(2)} TON`;
   $("shopVisual").outerHTML = collectibleHTML({collectible_no:null,model_style:"base"},{badge:false}).replace('class="collectible-shell"','id="shopVisual" class="collectible-shell"');
   $("invCount").textContent=state.inventory.length;$("profileName").textContent=user.first_name||user.username||"Player";$("username").textContent=user.username?`@${user.username}`:`ID ${user.id}`;$("avatar").textContent=(user.first_name||"S")[0].toUpperCase();$("profileTon").textContent=Number(stats.ton).toFixed(2);$("profileOwned").textContent=stats.owned;$("profileUpgraded").textContent=stats.upgraded;renderInventory();renderMarket();
 }
 async function refresh(){try{state=await api("/api/state");render()}catch(e){toast(e.message)}}

 function bindDynamic(){
  document.querySelectorAll(".upgrade-btn").forEach(b=>b.onclick=async()=>{b.disabled=true;haptic("medium");try{
   const r=await api("/api/upgrade",{method:"POST",body:JSON.stringify({gift_id:+b.dataset.id})});
   $("revealNumber").textContent=`#${r.collectible_no}`;$("revealModel").textContent=`${r.model.name} · ${r.model.weight}%`;$("revealBackdrop").textContent=`${r.backdrop.name} · ${r.backdrop.weight}%`;$("revealPattern").textContent=`${r.pattern.name} · ${r.pattern.weight}%`;
   $("revealVisual").innerHTML=collectibleHTML({collectible_no:r.collectible_no,model:r.model.name,model_style:r.model.style,backdrop_c1:r.backdrop.colors[0],backdrop_c2:r.backdrop.colors[1],pattern_icon:r.pattern.icon},{badge:false});
   $("upgradeOverlay").classList.remove("hidden");try{tg?.HapticFeedback?.notificationOccurred("success")}catch{}await refresh()
  }catch(e){toast(e.message);b.disabled=false}});
  document.querySelectorAll(".sell-btn").forEach(b=>b.onclick=()=>{sellingId=+b.dataset.id;$("sellTitle").textContent=`Продать Sharp Tongue ${b.dataset.label}`;$("sellSheet").classList.remove("hidden")});
  document.querySelectorAll(".cancel-btn").forEach(b=>b.onclick=async()=>{try{await api("/api/cancel",{method:"POST",body:JSON.stringify({gift_id:+b.dataset.id})});toast("Лот снят");await refresh()}catch(e){toast(e.message)}});
  document.querySelectorAll(".buy-market-btn").forEach(b=>b.onclick=async()=>{try{const r=await api("/api/buy",{method:"POST",body:JSON.stringify({listing_id:+b.dataset.listing})});toast(r.message);await refresh()}catch(e){toast(e.message)}});
 }
 document.querySelectorAll(".nav button").forEach(b=>b.onclick=()=>{document.querySelectorAll(".nav button").forEach(x=>x.classList.toggle("active",x===b));document.querySelectorAll(".page").forEach(p=>p.classList.toggle("active",p.id===b.dataset.page));haptic()});
 document.querySelectorAll(".seg").forEach(b=>b.onclick=()=>{invFilter=b.dataset.inv;document.querySelectorAll(".seg").forEach(x=>x.classList.toggle("active",x===b));renderInventory()});
 $("marketSearch").addEventListener("input",renderMarket);$("marketSort").addEventListener("change",renderMarket);
 $("buyStarsBtn").onclick=async()=>{const b=$("buyStarsBtn");b.disabled=true;try{const r=await api("/api/create-invoice",{method:"POST",body:"{}"});if(!tg?.openInvoice)throw new Error("Оплата Stars работает внутри Telegram");tg.openInvoice(r.invoice_link,status=>{b.disabled=false;if(status==="paid"){toast("Оплачено 15 ⭐");setTimeout(refresh,700);setTimeout(refresh,2200)}else if(status==="cancelled")toast("Отменено");else if(status==="failed")toast("Ошибка оплаты")})}catch(e){b.disabled=false;toast(e.message)}};
 $("buyTonBtn").onclick=async()=>{const b=$("buyTonBtn");b.disabled=true;haptic("medium");try{const r=await api("/api/buy-gift-ton",{method:"POST",body:"{}"});toast("Куплено за 0.15 TON");try{tg?.HapticFeedback?.notificationOccurred("success")}catch{}await refresh();document.querySelector('[data-page="inventory"]').click()}catch(e){toast(e.message)}finally{b.disabled=false}};
 $("confirmSell").onclick=async()=>{const ton=Number($("sellPrice").value);if(!Number.isFinite(ton)||ton<0.001||ton>1000)return toast("Цена: 0.001–1000 TON");const price_ton_nano=Math.round(ton*1000000000);try{await api("/api/list",{method:"POST",body:JSON.stringify({gift_id:sellingId,price_ton_nano})});$("sellSheet").classList.add("hidden");toast("Выставлено за TON");await refresh()}catch(e){toast(e.message)}};
 $("cancelSell").onclick=()=>$("sellSheet").classList.add("hidden");$("closeReveal").onclick=()=>$("upgradeOverlay").classList.add("hidden");
 async function loadTraits(){if(!traits)traits=await api("/api/traits");renderTraitTab("models")}
 function renderTraitTab(k){document.querySelectorAll(".trait-tab").forEach(b=>b.classList.toggle("active",b.dataset.trait===k));$("traitList").innerHTML=traits[k].map(x=>`<div class="trait-row"><b>${esc(x.icon?x.icon+" ":"")}${esc(x.name)}</b><small>${x.weight}%</small></div>`).join("")}
 $("openTraits").onclick=async()=>{try{await loadTraits();$("traitsSheet").classList.remove("hidden")}catch(e){toast(e.message)}};$("closeTraits").onclick=()=>$("traitsSheet").classList.add("hidden");document.querySelectorAll(".trait-tab").forEach(b=>b.onclick=()=>renderTraitTab(b.dataset.trait));
 refresh();
})();
