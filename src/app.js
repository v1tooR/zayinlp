(() => {
  'use strict';

  /* ---------------------------------------------------------
     Config vinda da página (cidade atual, telefones, cidades)
     --------------------------------------------------------- */
  const Z = window.ZAYIN || {};
  const CITY = Z.city || null;                 // null na página geral
  const CITIES = Z.cities || [];
  const DEFAULT_PHONE = Z.defaultPhone || '5512997067659';
  const PAGE_PHONE = (CITY && CITY.phone) || DEFAULT_PHONE;

  const $ = (s, r = document) => r.querySelector(s);
  const $$ = (s, r = document) => Array.from(r.querySelectorAll(s));
  const clamp = (v, a, b) => Math.min(b, Math.max(a, v));
  const fmt = n => Number(n).toLocaleString('pt-BR');
  const wa = (phone, text) => `https://wa.me/${phone}?text=${encodeURIComponent(text)}`;
  const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
  const finePointer = matchMedia('(pointer: fine)').matches;

  /* ---------------------------------------------------------
     Catálogo (exemplo — edite livremente, sem preços)
     type: hiwall | pisoteto | cassete
     --------------------------------------------------------- */
  const PRODUCTS = [
    { type: 'hiwall',   brand: 'Elgin',   line: 'Eco Inverter II',     btu: 9000,  mode: 'frio',   feats: ['Inverter', 'Wi-Fi'] },
    { type: 'hiwall',   brand: 'Midea',   line: 'AI Ecomaster',        btu: 9000,  mode: 'frio',   feats: ['Inverter', 'Wi-Fi'] },
    { type: 'hiwall',   brand: 'Elgin',   line: 'Eco Inverter II',     btu: 12000, mode: 'quente', feats: ['Inverter', 'Wi-Fi'] },
    { type: 'hiwall',   brand: 'LG',      line: 'Dual Inverter Voice', btu: 12000, mode: 'frio',   feats: ['Inverter', 'Wi-Fi'] },
    { type: 'pisoteto', brand: 'Elgin',   line: 'Piso Teto Inverter',  btu: 36000, mode: 'frio',   feats: ['Inverter'] },
    { type: 'cassete',  brand: 'Samsung', line: 'Cassete WindFree',    btu: 36000, mode: 'frio',   feats: ['Inverter', '360°'] },
    { type: 'hiwall',   brand: 'Samsung', line: 'WindFree',            btu: 12000, mode: 'frio',   feats: ['Inverter', 'Wi-Fi'] },
    { type: 'hiwall',   brand: 'Midea',   line: 'AI Ecomaster',        btu: 12000, mode: 'quente', feats: ['Inverter', 'Wi-Fi'] },
    { type: 'hiwall',   brand: 'Elgin',   line: 'Eco Inverter II',     btu: 18000, mode: 'frio',   feats: ['Inverter', 'Wi-Fi'] },
    { type: 'hiwall',   brand: 'LG',      line: 'Dual Inverter Voice', btu: 18000, mode: 'quente', feats: ['Inverter', 'Wi-Fi'] },
    { type: 'hiwall',   brand: 'Elgin',   line: 'Eco Inverter II',     btu: 24000, mode: 'quente', feats: ['Inverter', 'Wi-Fi'] },
    { type: 'hiwall',   brand: 'Samsung', line: 'WindFree',            btu: 24000, mode: 'frio',   feats: ['Inverter', 'Wi-Fi'] },
    { type: 'cassete',  brand: 'Elgin',   line: 'Cassete Inverter',    btu: 24000, mode: 'frio',   feats: ['Inverter'] },
    { type: 'hiwall',   brand: 'Gree',    line: 'G-Top Inverter',      btu: 30000, mode: 'frio',   feats: ['Inverter'] },
    { type: 'pisoteto', brand: 'Midea',   line: 'Piso Teto Inverter',  btu: 30000, mode: 'frio',   feats: ['Inverter'] },
    { type: 'pisoteto', brand: 'Gree',    line: 'Piso Teto Inverter',  btu: 36000, mode: 'quente', feats: ['Inverter'] },
    { type: 'pisoteto', brand: 'LG',      line: 'Piso Teto Inverter',  btu: 48000, mode: 'quente', feats: ['Inverter'] },
    { type: 'cassete',  brand: 'LG',      line: 'Cassete Inverter',    btu: 48000, mode: 'quente', feats: ['Inverter'] },
    { type: 'pisoteto', brand: 'Elgin',   line: 'Piso Teto Inverter',  btu: 60000, mode: 'frio',   feats: ['Inverter'] },
    { type: 'cassete',  brand: 'Midea',   line: 'Cassete Inverter',    btu: 60000, mode: 'frio',   feats: ['Inverter'] },
  ];
  const TYPE_FULL = { hiwall: 'Split Hi-Wall', pisoteto: 'Split Piso Teto', cassete: 'Split Cassete' };
  const TYPE_SHORT = { hiwall: 'Hi-wall', pisoteto: 'Piso teto', cassete: 'Cassete' };
  const MODE = { frio: 'Só frio', quente: 'Quente e frio' };
  const SIZES = [9000, 12000, 18000, 24000, 30000, 36000, 48000, 60000];

  /* ---------------------------------------------------------
     Links de WhatsApp com mensagem pronta
     --------------------------------------------------------- */
  $$('[data-wa]').forEach(a => {
    a.href = wa(a.dataset.waPhone || PAGE_PHONE, a.dataset.wa);
    a.target = '_blank';
    a.rel = 'noopener';
  });

  // Abrindo o arquivo direto do computador: /jacarei/ -> /jacarei/index.html
  if (location.protocol === 'file:') {
    $$('a[href]').forEach(a => {
      const h = a.getAttribute('href');
      if (h && !/^(https?:|#|mailto:|tel:)/.test(h) && h.endsWith('/')) a.setAttribute('href', h + 'index.html');
    });
  }

  /* ---------------------------------------------------------
     Header, menu da cidade, drawer, nav ativa
     --------------------------------------------------------- */
  const header = $('.header');
  const onScrollHeader = () => header.classList.toggle('is-scrolled', scrollY > 8);
  onScrollHeader();

  const cityBtn = $('.city-btn');
  const cityMenu = $('#cityMenu');
  const setCityMenu = open => {
    cityBtn.setAttribute('aria-expanded', String(open));
    cityMenu.classList.toggle('is-open', open);
  };
  cityBtn.addEventListener('click', e => { e.stopPropagation(); setCityMenu(!cityMenu.classList.contains('is-open')); });
  document.addEventListener('click', e => { if (!cityMenu.contains(e.target)) setCityMenu(false); });

  const drawer = $('#drawer');
  const menuBtn = $('.menu-toggle');
  const setDrawer = open => {
    drawer.classList.toggle('is-open', open);
    menuBtn.setAttribute('aria-expanded', String(open));
    menuBtn.setAttribute('aria-label', open ? 'Fechar menu' : 'Abrir menu');
    menuBtn.querySelector('use').setAttribute('href', open ? '#i-close' : '#i-menu');
    document.body.style.overflow = open ? 'hidden' : '';
  };
  menuBtn.addEventListener('click', () => setDrawer(!drawer.classList.contains('is-open')));
  $$('a', drawer).forEach(a => a.addEventListener('click', () => setDrawer(false)));
  document.addEventListener('keydown', e => {
    if (e.key === 'Escape') { setCityMenu(false); setDrawer(false); }
  });

  const navLinks = $$('.nav a');
  const navIO = new IntersectionObserver(entries => {
    entries.forEach(en => {
      if (!en.isIntersecting) return;
      navLinks.forEach(l => l.classList.toggle('is-active', l.getAttribute('href') === '#' + en.target.id));
    });
  }, { rootMargin: '-45% 0px -50% 0px' });
  ['servicos', 'aparelhos', 'garantia', 'cidades', 'duvidas'].forEach(id => { const el = document.getElementById(id); if (el) navIO.observe(el); });

  /* ---------------------------------------------------------
     Hero: o aparelho liga e o ambiente esfria
     --------------------------------------------------------- */
  const hero = $('.hero');
  const room = $('.room');
  const tempOut = $('#temp');
  const unitTemp = $('#unitTemp');
  let mode = 'cool';
  let setpoint = 23;
  let shown = 32;

  const coolFor = (t, m) => m === 'cool' ? clamp((30 - t) / 7, 0, 1) : clamp(1 - (t - 16) / 10, 0, 1) * 0.45;
  const paintTemp = t => {
    const v = Math.round(t);
    tempOut.textContent = v;
    unitTemp.textContent = v + '°';
  };

  function introTemp() {
    const from = 32, to = setpoint, dur = 2200, t0 = performance.now();
    const step = now => {
      const k = clamp((now - t0) / dur, 0, 1);
      const e = 1 - Math.pow(1 - k, 3);
      shown = from + (to - from) * e;
      paintTemp(shown);
      room.style.setProperty('--cool', (coolFor(shown, 'cool')).toFixed(3));
      if (k < 1) requestAnimationFrame(step);
      else room.classList.add('is-live');
    };
    requestAnimationFrame(step);
  }

  function applySetpoint() {
    shown = setpoint;
    paintTemp(setpoint);
    room.style.setProperty('--cool', coolFor(setpoint, mode).toFixed(3));
  }

  $$('.steppers button').forEach(b => b.addEventListener('click', () => {
    room.classList.add('is-live');
    setpoint = clamp(setpoint + Number(b.dataset.step), 16, 30);
    applySetpoint();
  }));
  $$('.modes button').forEach(b => b.addEventListener('click', () => {
    mode = b.dataset.mode;
    room.dataset.mode = mode;
    room.classList.add('is-live');
    $$('.modes button').forEach(x => x.setAttribute('aria-pressed', String(x === b)));
    setpoint = mode === 'cool' ? 23 : 27;
    applySetpoint();
  }));

  const start = () => {
    hero.classList.add('is-ready');
    if (reduce) {
      room.classList.add('is-on', 'is-live');
      applySetpoint();
      return;
    }
    setTimeout(() => { room.classList.add('is-on'); introTemp(); }, 650);
  };
  if (document.fonts && document.fonts.ready) {
    Promise.race([document.fonts.ready, new Promise(r => setTimeout(r, 900))]).then(start);
  } else start();

  if (!finePointer) { const h = $('#remoteHint'); if (h) h.textContent = 'Toque e arraste sobre o fluxo de ar'; }

  /* partículas de ar que desviam do cursor */
  const canvas = $('canvas', room);
  const ctx = canvas.getContext('2d');
  let W = 0, H = 0, ventY = 0, ventX0 = 0, ventX1 = 0;
  let parts = [];
  let px = -9999, py = -9999;
  let running = false, inView = true, raf = 0, acc = 0;

  function sizeCanvas() {
    const r = room.getBoundingClientRect();
    const u = $('.unit', room).getBoundingClientRect();
    const dpr = Math.min(window.devicePixelRatio || 1, 2);
    W = r.width; H = r.height;
    canvas.width = Math.round(W * dpr);
    canvas.height = Math.round(H * dpr);
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    ventY = u.bottom - r.top - u.height * 0.1;
    ventX0 = u.left - r.left + u.width * 0.1;
    ventX1 = u.right - r.left - u.width * 0.1;
  }

  function spawn() {
    const x = ventX0 + Math.random() * (ventX1 - ventX0);
    const spread = (x - W / 2) / W;
    parts.push({
      x, y: ventY + Math.random() * 6,
      vx: spread * 1.3 + (Math.random() - 0.5) * 0.25,
      vy: 0.7 + Math.random() * 1.1,
      life: 0, max: 110 + Math.random() * 90,
      ph: Math.random() * 6.28, len: 7 + Math.random() * 12,
    });
  }

  function frame() {
    if (!running) return;
    ctx.clearRect(0, 0, W, H);
    if (room.classList.contains('is-on')) {
      const rate = mode === 'cool' ? 0.25 + Math.max(0, 28 - shown) * 0.07 : 0.25 + Math.max(0, shown - 18) * 0.05;
      acc += rate * (W / 520);
      while (acc >= 1) { spawn(); acc -= 1; }
    }
    const rgb = mode === 'cool' ? '33,140,210' : '232,138,20';
    ctx.lineWidth = 1.8;
    ctx.lineCap = 'round';
    for (let i = parts.length - 1; i >= 0; i--) {
      const p = parts[i];
      p.life++; p.ph += 0.045;
      let ax = Math.sin(p.ph) * 0.025, ay = 0;
      const dx = p.x - px, dy = p.y - py, d2 = dx * dx + dy * dy;
      if (d2 < 10000) {
        const d = Math.sqrt(d2) || 1, f = (1 - d / 100) * 0.85;
        ax += (dx / d) * f; ay += (dy / d) * f;
      }
      p.vx = (p.vx + ax) * 0.985;
      p.vy = (p.vy + ay) * 0.99 + 0.004;
      p.x += p.vx; p.y += p.vy;
      const t = p.life / p.max;
      if (t >= 1 || p.y > H + 10 || p.x < -20 || p.x > W + 20) { parts.splice(i, 1); continue; }
      const a = Math.sin(Math.PI * t) * 0.55;
      const sp = Math.hypot(p.vx, p.vy) || 1;
      ctx.strokeStyle = `rgba(${rgb},${a.toFixed(3)})`;
      ctx.beginPath();
      ctx.moveTo(p.x, p.y);
      ctx.lineTo(p.x - (p.vx / sp) * p.len, p.y - (p.vy / sp) * p.len);
      ctx.stroke();
    }
    if (parts.length > 420) parts.splice(0, parts.length - 420);
    raf = requestAnimationFrame(frame);
  }
  const setRunning = on => {
    if (reduce) return;
    if (on && !running) { running = true; raf = requestAnimationFrame(frame); }
    if (!on && running) { running = false; cancelAnimationFrame(raf); }
  };

  if (!reduce) {
    sizeCanvas();
    new ResizeObserver(sizeCanvas).observe(room);
    new IntersectionObserver(([en]) => { inView = en.isIntersecting; setRunning(inView && !document.hidden); }).observe(room);
    document.addEventListener('visibilitychange', () => setRunning(inView && !document.hidden));
    room.addEventListener('pointermove', e => {
      const r = room.getBoundingClientRect();
      px = e.clientX - r.left; py = e.clientY - r.top;
    });
    room.addEventListener('pointerleave', () => { px = py = -9999; });
    setRunning(true);
  }

  /* botões magnéticos (só mouse) */
  if (finePointer && !reduce) {
    $$('.magnetic').forEach(el => {
      el.addEventListener('pointermove', e => {
        const r = el.getBoundingClientRect();
        const x = (e.clientX - r.left - r.width / 2) / r.width;
        const y = (e.clientY - r.top - r.height / 2) / r.height;
        el.style.transform = `translate(${(x * 8).toFixed(1)}px, ${(y * 6).toFixed(1)}px)`;
      });
      el.addEventListener('pointerleave', () => { el.style.transform = ''; });
    });
  }

  /* ---------------------------------------------------------
     Scroll: faixa, cano de cobre, revelações, barra flutuante
     --------------------------------------------------------- */
  const band = $('.band');
  const track = $('.band-track');
  const steps = $('.steps');
  const stepItems = $$('.step');
  const waFloat = $('.wa-float');
  const mbar = $('.mbar');
  const isVertical = () => matchMedia('(max-width: 860px)').matches;

  let ticking = false;
  function onScroll() {
    if (ticking) return;
    ticking = true;
    requestAnimationFrame(() => {
      ticking = false;
      onScrollHeader();
      const vh = innerHeight;

      if (!reduce) {
        const br = band.getBoundingClientRect();
        if (br.bottom > 0 && br.top < vh) {
          const p = clamp((vh - br.top) / (vh + br.height), 0, 1);
          const max = Math.min(track.scrollWidth - band.clientWidth, band.clientWidth * 0.9);
          track.style.transform = `translate3d(${(-p * max).toFixed(1)}px,0,0)`;
        }
      }

      const sr = steps.getBoundingClientRect();
      const p = reduce ? 1 : clamp((vh * 0.78 - sr.top) / (sr.height * (isVertical() ? 1 : 0.9) + vh * 0.15), 0, 1);
      steps.style.setProperty('--p', p.toFixed(3));
      stepItems.forEach((s, i) => s.classList.toggle('is-lit', p >= (i / (stepItems.length - 1)) * 0.97));

      const past = scrollY > vh * 0.55;
      waFloat.classList.toggle('is-shown', past);
      mbar.classList.toggle('is-shown', past);
    });
  }
  addEventListener('scroll', onScroll, { passive: true });
  addEventListener('resize', onScroll);
  onScroll();

  const revealIO = new IntersectionObserver(entries => {
    entries.forEach(en => {
      if (en.isIntersecting) { en.target.classList.add('is-in'); revealIO.unobserve(en.target); }
    });
  }, { threshold: 0.12, rootMargin: '0px 0px -6% 0px' });
  $$('[data-reveal], .w-row').forEach(el => revealIO.observe(el));

  /* ---------------------------------------------------------
     Montador de orçamento
     --------------------------------------------------------- */
  const form = $('#builder');
  const bubble = $('#b-bubble');
  const send = $('#b-send');
  const bPhone = $('#b-phone');
  const qtdOut = $('#qtd');
  let qtd = 1;
  const SVC = {
    instalar: 'Instalação de aparelho que já tenho',
    comprar: 'Compra e instalação de aparelho',
    manutencao: 'Manutenção preventiva',
    higienizacao: 'Higienização',
    infra: 'Infraestrutura para obra',
  };
  const TIPO = { hiwall: 'Split hi-wall (parede)', pisoteto: 'Split piso teto', cassete: 'Split cassete', 'nao-sei': 'ainda não sei o tipo' };

  function builderMessage() {
    const fd = new FormData(form);
    const svc = fd.get('svc');
    const tipo = fd.get('tipo');
    const btu = Number(fd.get('btu'));
    const citySlug = fd.get('cidade');
    const c = CITIES.find(x => x.slug === citySlug);
    const cityName = c ? c.name : (citySlug === 'litoral' ? 'Litoral Norte' : 'outra cidade');
    const nome = String(fd.get('nome') || '').trim().slice(0, 40);
    const lines = [
      `Olá, vim do seu site e quero um orçamento.${nome ? ` Meu nome é ${nome}.` : ''}`,
      `Serviço: ${SVC[svc]}`,
      `Aparelho: ${TIPO[tipo]}`,
    ];
    if (svc !== 'infra') lines.push(`Capacidade: ${btu ? fmt(btu) + ' BTUs' : 'preciso de ajuda para escolher'}`);
    lines.push(`Quantidade: ${qtd} ${qtd > 1 ? 'aparelhos' : 'aparelho'}`);
    lines.push(`Cidade: ${cityName}`);
    return { text: lines.join('\n'), phone: (c && c.phone) || DEFAULT_PHONE, label: (c && c.phoneLabel) || Z.defaultPhoneLabel };
  }

  function updateBuilder(pulse) {
    const { text, phone, label } = builderMessage();
    const now = new Date();
    bubble.textContent = text;
    const time = document.createElement('time');
    time.textContent = `${String(now.getHours()).padStart(2, '0')}:${String(now.getMinutes()).padStart(2, '0')}`;
    bubble.appendChild(time);
    send.href = wa(phone, text);
    bPhone.textContent = `WhatsApp ${label}`;
    if (pulse && !reduce) {
      bubble.classList.remove('pulse');
      void bubble.offsetWidth;
      bubble.classList.add('pulse');
    }
  }
  form.addEventListener('input', () => updateBuilder(true));
  form.addEventListener('change', () => updateBuilder(true));
  $$('[data-qtd]').forEach(b => b.addEventListener('click', () => {
    qtd = clamp(qtd + Number(b.dataset.qtd), 1, 20);
    qtdOut.textContent = qtd;
    updateBuilder(true);
  }));
  updateBuilder(false);

  /* ---------------------------------------------------------
     Catálogo: filtros, cards e mensagem por aparelho
     --------------------------------------------------------- */
  const grid = $('#products');
  const note = $('#f-note');
  const moreBtn = $('#moreBtn');
  const fBrand = $('#f-brand');
  const fBtu = $('#f-btu');
  const PAGE = 8;
  const state = { type: 'all', brand: 'all', btu: 'all', limit: PAGE };

  [...new Set(PRODUCTS.map(p => p.brand))].sort().forEach(b => fBrand.add(new Option(b, b)));
  SIZES.forEach(s => fBtu.add(new Option(`${fmt(s)} BTUs`, String(s))));

  const art = {
    hiwall: `<svg viewBox="0 0 240 120" aria-hidden="true"><ellipse cx="120" cy="104" rx="92" ry="6" fill="#062B52" opacity=".07"/><rect x="18" y="26" width="204" height="60" rx="18" fill="#fff" stroke="#C9DAEA" stroke-width="1.5"/><path d="M36 33h168" stroke="#F3F7FB" stroke-width="3" stroke-linecap="round"/><path d="M14 72h212" stroke="#E4ECF4" stroke-width="1.2"/><rect x="30" y="74" width="180" height="10" rx="4" fill="#0A2A4A"/><path d="M26 76h188a4 4 0 0 1 4 4v1a8 8 0 0 1-8 8H30a8 8 0 0 1-8-8v-1a4 4 0 0 1 4-4Z" fill="#F4F8FB" stroke="#C9DAEA" stroke-width="1.2" transform="translate(0 4) scale(1 .7)" transform-origin="120 76"/><rect x="170" y="44" width="30" height="13" rx="4" fill="#062B52"/><rect x="176" y="49" width="12" height="3" rx="1.5" fill="#5EC8F2"/><circle cx="163" cy="50.5" r="2" fill="#1FAF5B"/><path d="M60 100c-2-4 2-6 0-10M120 104c-2-4 2-6 0-10M180 100c-2-4 2-6 0-10" stroke="#5EC8F2" stroke-width="2" fill="none" stroke-linecap="round" opacity=".8"/></svg>`,
    pisoteto: `<svg viewBox="0 0 240 120" aria-hidden="true"><ellipse cx="120" cy="108" rx="100" ry="6" fill="#062B52" opacity=".07"/><path d="M22 20h196l8 10H14Z" fill="#E6EEF6" stroke="#C9DAEA" stroke-width="1.2"/><rect x="14" y="30" width="212" height="66" rx="10" fill="#fff" stroke="#C9DAEA" stroke-width="1.5"/><rect x="26" y="40" width="130" height="30" rx="5" fill="#F2F6FA"/><path d="M30 46h122M30 52h122M30 58h122M30 64h122" stroke="#D8E3EE" stroke-width="1.2"/><rect x="172" y="44" width="36" height="14" rx="4" fill="#062B52"/><rect x="178" y="49" width="16" height="3.5" rx="1.75" fill="#5EC8F2"/><rect x="24" y="76" width="192" height="12" rx="5" fill="#0A2A4A"/><path d="M24 78h192v4a6 6 0 0 1-6 6H30a6 6 0 0 1-6-6Z" fill="#F4F8FB" stroke="#C9DAEA" stroke-width="1.1" transform="translate(0 3) scale(1 .75)" transform-origin="120 78"/></svg>`,
    cassete: `<svg viewBox="0 0 240 120" aria-hidden="true"><path d="M20 12h200" stroke="#C9DAEA" stroke-width="1.5" stroke-dasharray="4 5"/><rect x="66" y="10" width="108" height="100" rx="14" fill="#fff" stroke="#C9DAEA" stroke-width="1.5"/><rect x="80" y="20" width="80" height="9" rx="4.5" fill="#0A2A4A"/><rect x="80" y="91" width="80" height="9" rx="4.5" fill="#0A2A4A"/><rect x="74" y="35" width="9" height="50" rx="4.5" fill="#0A2A4A"/><rect x="157" y="35" width="9" height="50" rx="4.5" fill="#0A2A4A"/><rect x="93" y="38" width="54" height="44" rx="6" fill="#F2F6FA" stroke="#D8E3EE"/><path d="M99 46h42M99 52h42M99 58h42M99 64h42M99 70h42M99 76h42" stroke="#D8E3EE" stroke-width="1.2"/><circle cx="150" cy="87" r="2" fill="#1FAF5B"/><path d="M50 60c-6-3-6 3-12 0M190 60c6-3 6 3 12 0M50 76c-6-3-6 3-12 0M190 76c6-3 6 3 12 0" stroke="#5EC8F2" stroke-width="2" fill="none" stroke-linecap="round" opacity=".8"/></svg>`,
  };

  const productText = (p, withInstall) =>
    `Olá, vim do seu site, quero fazer um orçamento do ${TYPE_FULL[p.type]} ${p.brand} ${p.line} de ${fmt(p.btu)} BTUs (${MODE[p.mode].toLowerCase()})${withInstall ? ', com instalação' : ''}.${CITY ? ` Estou em ${CITY.name}.` : ''}`;

  const filtered = () => PRODUCTS.filter(p =>
    (state.type === 'all' || p.type === state.type) &&
    (state.brand === 'all' || p.brand === state.brand) &&
    (state.btu === 'all' || p.btu === Number(state.btu)));

  function card(p, i, animate) {
    const feats = p.feats.map(f => `<li>${f}</li>`).join('') + `<li class="${p.mode === 'quente' ? 'hot' : ''}">${MODE[p.mode]}</li>`;
    const id = `inst-${i}`;
    return `<article class="product${animate ? ' is-enter' : ''}" style="--d:${animate ? Math.min(i, 8) * 0.05 : 0}s" data-i="${PRODUCTS.indexOf(p)}">
      <div class="p-art"><span class="tag-type">${TYPE_SHORT[p.type]}</span>${art[p.type]}</div>
      <div class="p-body">
        <span class="p-brand">${p.brand}</span>
        <h3 class="p-name">${p.line}</h3>
        <p class="p-btu"><b>${fmt(p.btu)}</b><span>BTUs</span></p>
        <ul class="p-feats">${feats}</ul>
        <div class="p-install"><label class="switch" for="${id}"><input type="checkbox" id="${id}" checked><span class="track"></span>Incluir instalação</label></div>
        <a class="btn btn-wa btn-block" href="${wa(PAGE_PHONE, productText(p, true))}" target="_blank" rel="noopener">
          <svg aria-hidden="true"><use href="#i-wa"/></svg>Pedir orçamento
        </a>
      </div>
    </article>`;
  }

  function render(animate = true) {
    const list = filtered();
    const visible = list.slice(0, state.limit);
    if (!list.length) {
      const tipo = state.type === 'all' ? 'ar-condicionado' : TYPE_FULL[state.type];
      const marca = state.brand === 'all' ? '' : ` ${state.brand}`;
      const cap = state.btu === 'all' ? '' : ` de ${fmt(state.btu)} BTUs`;
      const txt = `Olá, vim do seu site e procuro um ${tipo}${marca}${cap}. Vocês têm?${CITY ? ` Estou em ${CITY.name}.` : ''}`;
      grid.innerHTML = `<div class="empty"><h3>Nenhum aparelho com esses filtros</h3><p>Trabalhamos com outros modelos além dos listados. Peça pelo WhatsApp o que você procura ou limpe os filtros.</p><a class="btn btn-wa" href="${wa(PAGE_PHONE, txt)}" target="_blank" rel="noopener"><svg aria-hidden="true"><use href="#i-wa"/></svg>Pedir esse modelo</a></div>`;
    } else {
      grid.innerHTML = visible.map((p, i) => card(p, i, animate && !reduce)).join('');
    }
    const active = state.type !== 'all' || state.brand !== 'all' || state.btu !== 'all';
    note.innerHTML = list.length
      ? `Mostrando ${visible.length} de ${list.length} ${list.length > 1 ? 'aparelhos' : 'aparelho'}.${active ? ' <button type="button" id="clearF">Limpar filtros</button>' : ''}`
      : (active ? '<button type="button" id="clearF">Limpar filtros</button>' : '');
    moreBtn.parentElement.style.display = list.length > visible.length ? '' : 'none';
    const clear = $('#clearF');
    if (clear) clear.addEventListener('click', () => setFilters({ type: 'all', brand: 'all', btu: 'all' }));
  }

  function setFilters(next) {
    Object.assign(state, next, { limit: PAGE });
    $$('#f-type button').forEach(b => b.setAttribute('aria-pressed', String(b.dataset.type === state.type)));
    fBrand.value = state.brand;
    fBtu.value = String(state.btu);
    render();
  }

  $$('#f-type button').forEach(b => b.addEventListener('click', () => setFilters({ type: b.dataset.type })));
  fBrand.addEventListener('change', () => setFilters({ brand: fBrand.value }));
  fBtu.addEventListener('change', () => setFilters({ btu: fBtu.value }));
  moreBtn.addEventListener('click', () => {
    const before = state.limit;
    state.limit += PAGE;
    render(false);
    const first = grid.children[before];
    if (first) $$('.product', grid).slice(before).forEach((el, i) => { if (!reduce) { el.classList.add('is-enter'); el.style.setProperty('--d', `${i * 0.05}s`); } });
  });
  grid.addEventListener('change', e => {
    if (!e.target.matches('.p-install input')) return;
    const art = e.target.closest('.product');
    const p = PRODUCTS[Number(art.dataset.i)];
    $('.btn', art).href = wa(PAGE_PHONE, productText(p, e.target.checked));
  });
  render(false);

  /* ---------------------------------------------------------
     Calculadora de BTU
     --------------------------------------------------------- */
  const calc = $('#calc');
  const calcToggle = $('#calcToggle');
  const area = $('#c-area');
  const areaOut = $('#c-area-o');
  const sun = $('#c-sun');
  const cOut = $('#c-out');
  const apply = $('#c-apply');
  const cv = { p: 2, e: 1 };
  let recommended = 12000;

  calcToggle.addEventListener('click', () => {
    const open = !calc.classList.contains('is-open');
    calc.classList.toggle('is-open', open);
    calcToggle.setAttribute('aria-expanded', String(open));
  });

  function compute() {
    const a = Number(area.value);
    area.style.setProperty('--fill', `${((a - area.min) / (area.max - area.min)) * 100}%`);
    areaOut.textContent = `${a} m²`;
    const raw = a * (sun.checked ? 800 : 600) + Math.max(0, cv.p - 1) * 600 + cv.e * 600;
    const size = SIZES.find(s => s >= raw);
    if (size) {
      recommended = size;
      cOut.innerHTML = `${fmt(size)}<em>BTUs</em>`;
      apply.textContent = `Ver aparelhos de ${fmt(size)} BTUs`;
    } else {
      recommended = 0;
      cOut.innerHTML = `+60 mil<em>BTUs</em>`;
      apply.textContent = 'Falar sobre um projeto';
    }
    $('#c-p').textContent = cv.p;
    $('#c-e').textContent = cv.e;
  }
  area.addEventListener('input', compute);
  sun.addEventListener('change', compute);
  $$('[data-c]').forEach(b => b.addEventListener('click', () => {
    const k = b.dataset.c;
    cv[k] = clamp(cv[k] + Number(b.dataset.d), k === 'p' ? 1 : 0, k === 'p' ? 20 : 10);
    compute();
  }));
  apply.addEventListener('click', () => {
    if (!recommended) {
      window.open(wa(PAGE_PHONE, `Olá, vim do seu site. Tenho um ambiente de ${area.value} m² e preciso de mais de 60.000 BTUs. Podem me ajudar com um projeto?${CITY ? ` Estou em ${CITY.name}.` : ''}`), '_blank', 'noopener');
      return;
    }
    setFilters({ type: 'all', brand: 'all', btu: String(recommended) });
    grid.scrollIntoView({ behavior: reduce ? 'auto' : 'smooth', block: 'start' });
  });
  compute();

  /* ano no rodapé */
  const y = $('#year');
  if (y) y.textContent = new Date().getFullYear();
})();
