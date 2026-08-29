const tg = window.Telegram?.WebApp || {};
const API_BASE = window.location.origin;
let state = {};
let currentUser = {};

function showToast(msg) {
  const toast = document.getElementById('toast');
  toast.textContent = msg;
  toast.classList.add('show');
  setTimeout(() => toast.classList.remove('show'), 3000);
}

async function api(endpoint, method = 'GET', body = null) {
  const headers = {
    'Content-Type': 'application/json',
    'X-Telegram-Init-Data': tg.initData || ''
  };
  const options = { method, headers };
  if (body) options.body = JSON.stringify(body);
  try {
    const res = await fetch(`${API_BASE}${endpoint}`, options);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return await res.json();
  } catch (e) {
    showToast(`Ошибка: ${e.message}`);
    throw e;
  }
}

async function loadState() {
  try {
    const data = await api('/api/state');
    state = data;
    currentUser = data.user;
    updateUI();
  } catch (e) {
    console.error('Failed to load state:', e);
  }
}

function updateUI() {
  // Заголовок
  const hello = document.getElementById('hello');
  const tonBalance = document.getElementById('tonBalance');
  const avatar = document.getElementById('avatar');
  const profileName = document.getElementById('profileName');
  const username = document.getElementById('username');
  
  if (hello) hello.textContent = currentUser.first_name || 'Player';
  if (tonBalance) tonBalance.textContent = (state.stats?.ton_nano || 0) / 1e9;
  if (avatar) avatar.textContent = (currentUser.first_name || 'P')[0].toUpperCase();
  if (profileName) profileName.textContent = currentUser.first_name || 'Player';
  if (username) username.textContent = currentUser.username ? `@${currentUser.username}` : 'Telegram';
  
  // Статистика профиля
  document.getElementById('profileTon').textContent = ((state.stats?.ton_nano || 0) / 1e9).toFixed(2);
  document.getElementById('profileOwned').textContent = (state.inventory?.length || 0);
  document.getElementById('profileUpgraded').textContent = (state.stats?.upgraded || 0);
  
  // Маркет
  const marketCount = document.getElementById('marketCount');
  if (marketCount) marketCount.textContent = (state.market?.length || 0);
  
  // Инвентарь
  const invCount = document.getElementById('invCount');
  if (invCount) invCount.textContent = (state.inventory?.length || 0);
  
  // Цены
  if (state.config) {
    const buyStarsBtn = document.getElementById('buyStarsBtn');
    const buyTonBtn = document.getElementById('buyTonBtn');
    if (buyStarsBtn) buyStarsBtn.textContent = `Купить · ${state.config.price_stars} ⭐`;
    if (buyTonBtn) buyTonBtn.textContent = `Купить · ${state.config.price_ton.toFixed(2)} TON`;
  }
}

function switchPage(pageName) {
  document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
  document.getElementById(pageName)?.classList.add('active');
  
  document.querySelectorAll('.nav button').forEach(btn => btn.classList.remove('active'));
  document.querySelector(`[data-page="${pageName}"]`)?.classList.add('active');
}

// Инициализация
if (tg.ready) tg.ready();

document.querySelectorAll('[data-page]').forEach(btn => {
  btn.addEventListener('click', () => switchPage(btn.dataset.page));
});

// Загрузка данных при открытии
window.addEventListener('load', loadState);
