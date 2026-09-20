(() => {
  'use strict';

  /* ---------------------------------------------------------
     Config vinda da página (tipo de página, cidade, telefones, marcas)
     --------------------------------------------------------- */
  const Z = window.ZAYIN || {};
  const CITY = Z.city || null;                 // null na página geral
  const CITIES = Z.cities || [];
  const DEFAULT_PHONE = Z.defaultPhone || '5512997067659';
  const PAGE_PHONE = (CITY && CITY.phone) || DEFAULT_PHONE;
  const BRANDS = Object.fromEntries((Z.brands || []).map(b => [b.name, b]));
  const IMG = Z.imgBase || 'img/produtos/';

  const $ = (s, r = document) => r.querySelector(s);
  const $$ = (s, r = document) => Array.from(r.querySelectorAll(s));
  const clamp = (v, a, b) => Math.min(b, Math.max(a, v));
  const fmt = n => Number(n).toLocaleString('pt-BR');
  const wa = (phone, text) => `https://wa.me/${phone}?text=${encodeURIComponent(text)}`;
  const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
  const finePointer = matchMedia('(pointer: fine)').matches;

  /* ---------------------------------------------------------
     Catálogo — modelos reais das marcas, sem preço.
     type: hiwall | pisoteto | cassete · mode: frio | quente (vazio = não divulgado)
     brand: precisa bater com o nome em BRANDS do build.py para mostrar o logo
     img: arquivo em assets/products/<img>.webp (foto oficial do fabricante)
     Fontes de cada modelo: assets/products/FONTES.md
     --------------------------------------------------------- */
  const PRODUCTS = [
    { type: 'hiwall',    brand: 'Elgin',     line: 'Eco Inverter 3 Wi-Fi',               btu:   9000, mode: 'frio',    code: 'ELG-45HJFI09C2WG',     img: 'elgin-hiwall-9000',            feats: ['Inverter', 'Wi-Fi'] },
    { type: 'hiwall',    brand: 'LG',        line: 'Dual Inverter Voice AI',             btu:   9000, mode: 'frio',    code: 'S3-Q09AA31A',          img: 'lg-hiwall-9000',               feats: ['Inverter', 'Wi-Fi'] },
    { type: 'hiwall',    brand: 'Midea',     line: 'AI Ecomaster',                       btu:   9000, mode: 'frio',    code: '42EFVCA09M8',          img: 'midea-hiwall-9000',            feats: ['Inverter', 'Wi-Fi'] },
    { type: 'hiwall',    brand: 'Samsung',   line: 'WindFree AI Pro',                    btu:   9000, mode: 'quente',  code: '',                     img: 'samsung-hiwall-9000-qf',       feats: ['Inverter', 'Wi-Fi'] },
    { type: 'hiwall',    brand: 'Elgin',     line: 'Eco Inverter 3 Wi-Fi',               btu:  12000, mode: 'frio',    code: 'ELG-45HJFI12C2WG',     img: 'elgin-hiwall-12000',           feats: ['Inverter', 'Wi-Fi'] },
    { type: 'hiwall',    brand: 'Gree',      line: 'G-Classic Inverter',                 btu:  12000, mode: 'frio',    code: '',                     img: 'gree-hiwall-12000',            feats: ['Inverter'] },
    { type: 'hiwall',    brand: 'LG',        line: 'Dual Inverter Voice +AI',            btu:  12000, mode: 'quente',  code: 'S3-W12JA33B',          img: 'lg-hiwall-12000-qf',           feats: ['Inverter', 'Wi-Fi'] },
    { type: 'hiwall',    brand: 'Midea',     line: 'AI Ecomaster',                       btu:  12000, mode: 'frio',    code: '42EFVCA12M8',          img: 'midea-hiwall-12000',           feats: ['Inverter', 'Wi-Fi'] },
    { type: 'hiwall',    brand: 'Samsung',   line: 'WindFree AI Pro',                    btu:  12000, mode: 'frio',    code: 'AR60H12D1AWNAZ',       img: 'samsung-hiwall-12000',         feats: ['Inverter', 'Wi-Fi'] },
    { type: 'hiwall',    brand: 'Elgin',     line: 'Eco Inverter 3 Wi-Fi',               btu:  18000, mode: 'frio',    code: 'ELG-45HJFI18C2WG',     img: 'elgin-hiwall-18000',           feats: ['Inverter', 'Wi-Fi'] },
    { type: 'hiwall',    brand: 'LG',        line: 'Dual Inverter Voice AI',             btu:  18000, mode: 'frio',    code: 'S3-Q18KL31B',          img: 'lg-hiwall-18000',              feats: ['Inverter', 'Wi-Fi'] },
    { type: 'hiwall',    brand: 'Midea',     line: 'AI Ecomaster',                       btu:  18000, mode: 'frio',    code: '42EZVCA18M5',          img: 'midea-hiwall-18000',           feats: ['Inverter', 'Wi-Fi'] },
    { type: 'hiwall',    brand: 'Samsung',   line: 'WindFree AI',                        btu:  18000, mode: 'frio',    code: 'AR60F18D1AWNAZ',       img: 'samsung-hiwall-18000',         feats: ['Inverter', 'Wi-Fi'] },
    { type: 'hiwall',    brand: 'Samsung',   line: 'WindFree AI',                        btu:  18000, mode: 'quente',  code: 'AR60F18C1AWNAZ',       img: 'samsung-hiwall-18000-qf',      feats: ['Inverter', 'Wi-Fi'] },
    { type: 'cassete',   brand: 'Samsung',   line: 'Cassete 4 vias WindFree',            btu:  18000, mode: '',        code: 'AC018HE4DKG/AZ',       img: 'samsung-cassete-18000',        feats: ['Inverter', 'Wi-Fi'] },
    { type: 'hiwall',    brand: 'Elgin',     line: 'Eco Inverter 3 Wi-Fi',               btu:  24000, mode: 'quente',  code: 'ELG-45HJQI24C2WG',     img: 'elgin-hiwall-24000-qf',        feats: ['Inverter', 'Wi-Fi'] },
    { type: 'hiwall',    brand: 'Gree',      line: 'G-Classic Inverter',                 btu:  24000, mode: 'quente',  code: '',                     img: 'gree-hiwall-24000-qf',         feats: ['Inverter'] },
    { type: 'hiwall',    brand: 'LG',        line: 'Dual Inverter Voice AI',             btu:  24000, mode: 'frio',    code: 'S3-Q24K231B',          img: 'lg-hiwall-24000',              feats: ['Inverter', 'Wi-Fi'] },
    { type: 'hiwall',    brand: 'Midea',     line: 'AI Ecomaster',                       btu:  24000, mode: 'quente',  code: '42EZVQA24M5',          img: 'midea-hiwall-24000-qf',        feats: ['Inverter', 'Wi-Fi'] },
    { type: 'hiwall',    brand: 'Samsung',   line: 'WindFree AI Pro',                    btu:  24000, mode: 'quente',  code: '',                     img: 'samsung-hiwall-24000-qf',      feats: ['Inverter', 'Wi-Fi'] },
    { type: 'hiwall',    brand: 'Samsung',   line: 'Digital Inverter Ultra Connect AI',  btu:  24000, mode: 'frio',    code: 'AR50F24D1AHNAZ',        img: 'samsung-hiwall-24000',         feats: ['Inverter', 'Wi-Fi'] },
    { type: 'cassete',   brand: 'Elgin',     line: 'Cassete Eco Inverter',               btu:  24000, mode: 'quente',  code: 'ELG-45KVQC24C2NACA',   img: 'elgin-cassete-24000-qf',       feats: ['Inverter'] },
    { type: 'cassete',   brand: 'Midea',     line: 'Cassete 4 vias Inverter',            btu:  24000, mode: 'frio',    code: '40KVQF24M5',           img: 'midea-cassete-24000',          feats: ['Inverter'] },
    { type: 'hiwall',    brand: 'Elgin',     line: 'Eco Inverter 3 Wi-Fi',               btu:  30000, mode: 'frio',    code: 'ELG-45HJFI30C2WG',     img: 'elgin-hiwall-30000',           feats: ['Inverter', 'Wi-Fi'] },
    { type: 'hiwall',    brand: 'Midea',     line: 'XtremeSave',                         btu:  30000, mode: 'quente',  code: '42AGVQC30M5',          img: 'midea-hiwall-30000-qf',        feats: ['Inverter', 'Wi-Fi'] },
    { type: 'pisoteto',  brand: 'Elgin',     line: 'Piso Teto Eco Inverter',             btu:  36000, mode: 'frio',    code: 'ELG-45PVFC36C2DAVA',   img: 'elgin-pisoteto-36000',         feats: ['Inverter'] },
    { type: 'pisoteto',  brand: 'Gree',      line: 'G-Prime Inverter Compact',           btu:  36000, mode: '',        code: '',                     img: 'gree-pisoteto-36000',          feats: ['Inverter'] },
    { type: 'pisoteto',  brand: 'Midea',     line: 'Split Teto Inverter',                btu:  36000, mode: 'frio',    code: '42ZQVD36M5',           img: 'midea-pisoteto-36000',         feats: ['Inverter'] },
    { type: 'cassete',   brand: 'Elgin',     line: 'Cassete Eco Inverter',               btu:  36000, mode: 'quente',  code: 'ELG-45KVFC36C2NAVA',   img: 'elgin-cassete-36000-qf',       feats: ['Inverter'] },
    { type: 'cassete',   brand: 'Gree',      line: 'G-Prime Inverter Plus',              btu:  36000, mode: '',        code: '',                     img: 'gree-cassete-36000',           feats: ['Inverter'] },
    { type: 'cassete',   brand: 'Samsung',   line: 'Cassete 4 vias WindFree',            btu:  36000, mode: 'quente',  code: 'AC036HE4DKG/AZ',       img: 'samsung-cassete-36000-qf',     feats: ['Inverter', 'Wi-Fi'] },
    { type: 'cassete',   brand: 'Elgin',     line: 'Cassete Eco Inverter',               btu:  48000, mode: 'frio',    code: 'ELG-45KVFC48C2NAVA',   img: 'elgin-cassete-48000',          feats: ['Inverter'] },
    { type: 'pisoteto',  brand: 'Midea',     line: 'Split Teto Inverter',                btu:  60000, mode: 'frio',    code: '42ZQVD60M5',           img: 'midea-pisoteto-60000',         feats: ['Inverter'] },
  ];
  const TYPE_FULL = { hiwall: 'Split Hi-Wall', pisoteto: 'Split Piso Teto', cassete: 'Split Cassete' };
  const TYPE_SHORT = { hiwall: 'Hi-wall', pisoteto: 'Piso teto', cassete: 'Cassete' };
  const MODE = { frio: 'Só frio', quente: 'Quente e frio' };
  const SIZES = [9000, 12000, 18000, 24000, 30000, 36000, 48000, 60000];

  /* ---------------------------------------------------------
     Links de WhatsApp com mensagem pronta
     --------------------------------------------------------- */
  // sem cidade escolhida, a mensagem termina com "Minha cidade:" para a pessoa completar no WhatsApp
  const CITY_ASK = CITY ? '' : '\nMinha cidade: ';
  $$('[data-wa]').forEach(a => {
    const text = a.dataset.wa + (/Estou em /.test(a.dataset.wa) ? '' : CITY_ASK);
    a.href = wa(a.dataset.waPhone || PAGE_PHONE, text);
    a.target = '_blank';
    a.rel = 'noopener';
  });

  // Abrindo o arquivo direto do computador: /jacarei/ -> /jacarei/index.html (mantendo a âncora)
  if (location.protocol === 'file:') {
    $$('a[href]').forEach(a => {
      const h = a.getAttribute('href');
      if (!h || /^(https?:|#|mailto:|tel:)/.test(h)) return;
      const m = h.match(/^([^#]*\/)(#.*)?$/);
      if (m) a.setAttribute('href', `${m[1]}index.html${m[2] || ''}`);
    });
  }

  /* ---------------------------------------------------------
     Header, menu da cidade, drawer, nav ativa
     --------------------------------------------------------- */
  // na home o header fica transparente sobre o vídeo e ganha fundo assim que a página rola
  const header = $('.header');
  const overHero = header.classList.contains('is-over');
  let menuOpen = false;
  const onScrollHeader = () => {
    const scrolled = scrollY > 16;
    header.classList.toggle('is-scrolled', scrolled);
    if (overHero) header.classList.toggle('is-over', !scrolled && !menuOpen);
  };
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
    menuOpen = open;
    header.classList.toggle('is-menu', open);
    onScrollHeader();
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

  const navLinks = $$('.nav a[href^="#"]');
  const navIO = new IntersectionObserver(entries => {
    entries.forEach(en => {
      if (!en.isIntersecting) return;
      navLinks.forEach(l => l.classList.toggle('is-active', l.getAttribute('href') === '#' + en.target.id));
    });
  }, { rootMargin: '-45% 0px -50% 0px' });
  navLinks.forEach(l => { const el = document.getElementById(l.getAttribute('href').slice(1)); if (el) navIO.observe(el); });

  /* ---------------------------------------------------------
     Hero: entrada + vídeo de fundo
     --------------------------------------------------------- */
  const hero = $('.hero');
  const start = () => { header.classList.add('is-ready'); if (hero) hero.classList.add('is-ready'); };
  if (document.fonts && document.fonts.ready) {
    Promise.race([document.fonts.ready, new Promise(r => setTimeout(r, 900))]).then(start);
  } else start();

  // vídeo de fundo: o aparelho "liga" uma vez e fica parado no último quadro;
  // volta a tocar quando a pessoa sobe de novo até o topo
  const hv = $('.hv-video');
  if (hv && !reduce) {
    let ended = false;
    const play = () => { const pr = hv.play(); if (pr && pr.catch) pr.catch(() => {}); };
    hv.addEventListener('ended', () => { ended = true; });
    const begin = () => { hv.preload = 'auto'; play(); };
    if (document.readyState === 'complete') begin(); else addEventListener('load', begin, { once: true });
    new IntersectionObserver(([en]) => {
      if (en.isIntersecting && ended) { ended = false; hv.currentTime = 0; play(); }
    }, { threshold: 0.5 }).observe(hv);
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
     Scroll: faixa, cano de cobre, barra flutuante
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

      if (band && !reduce) {
        const br = band.getBoundingClientRect();
        if (br.bottom > 0 && br.top < vh) {
          const p = clamp((vh - br.top) / (vh + br.height), 0, 1);
          const max = Math.min(track.scrollWidth - band.clientWidth, band.clientWidth * 0.9);
          track.style.transform = `translate3d(${(-p * max).toFixed(1)}px,0,0)`;
        }
      }

      if (steps) {
        const sr = steps.getBoundingClientRect();
        const p = reduce ? 1 : clamp((vh * 0.78 - sr.top) / (sr.height * (isVertical() ? 1 : 0.9) + vh * 0.15), 0, 1);
        steps.style.setProperty('--p', p.toFixed(3));
        stepItems.forEach((s, i) => s.classList.toggle('is-lit', p >= (i / (stepItems.length - 1)) * 0.97));
      }

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
     Montador de orçamento (página de serviços)
     --------------------------------------------------------- */
  const form = $('#builder');
  if (form) {
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

    const builderMessage = () => {
      const fd = new FormData(form);
      const svc = fd.get('svc');
      const tipo = fd.get('tipo');
      const btu = Number(fd.get('btu'));
      const citySlug = fd.get('cidade');
      const c = CITIES.find(x => x.slug === citySlug);
      const cityName = c ? c.name : ({ litoral: 'Litoral Norte', outra: 'outra cidade' }[citySlug] || '');
      const nome = String(fd.get('nome') || '').trim().slice(0, 40);
      const lines = [
        `Olá, vim do seu site e quero um orçamento.${nome ? ` Meu nome é ${nome}.` : ''}`,
        `Serviço: ${SVC[svc]}`,
        `Aparelho: ${TIPO[tipo]}`,
      ];
      if (svc !== 'infra') lines.push(`Capacidade: ${btu ? fmt(btu) + ' BTUs' : 'preciso de ajuda para escolher'}`);
      lines.push(`Quantidade: ${qtd} ${qtd > 1 ? 'aparelhos' : 'aparelho'}`);
      lines.push(cityName ? `Cidade: ${cityName}` : 'Minha cidade: ');
      return { text: lines.join('\n'), phone: (c && c.phone) || DEFAULT_PHONE, label: (c && c.phoneLabel) || Z.defaultPhoneLabel };
    };

    const updateBuilder = pulse => {
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
    };
    form.addEventListener('input', () => updateBuilder(true));
    form.addEventListener('change', () => updateBuilder(true));
    $$('[data-qtd]').forEach(b => b.addEventListener('click', () => {
      qtd = clamp(qtd + Number(b.dataset.qtd), 1, 20);
      qtdOut.textContent = qtd;
      updateBuilder(true);
    }));
    updateBuilder(false);
  }

  /* ---------------------------------------------------------
     Catálogo: filtros, marcas, cards e mensagem por aparelho (home)
     --------------------------------------------------------- */
  const grid = $('#products');
  if (grid) {
    const note = $('#f-note');
    const moreBtn = $('#moreBtn');
    const fBrand = $('#f-brand');
    const fBtu = $('#f-btu');
    const brandBtns = $$('.brand-btn');
    const PAGE = 12;                                   // 4x3 no computador, 2x6 no celular
    const state = { type: 'all', brand: 'all', btu: 'all', limit: PAGE };

    [...new Set(PRODUCTS.map(p => p.brand))].sort().forEach(b => fBrand.add(new Option(b, b)));
    SIZES.forEach(s => fBtu.add(new Option(`${fmt(s)} BTUs`, String(s))));

    // logo da marca no card, com a mesma "área visual" para logos largos e compactos
    const brandMark = name => {
      const b = BRANDS[name];
      if (!b) return `<span class="p-brand">${name}</span>`;
      const w = Math.round(Math.sqrt(520 * b.ratio)), h = Math.round(Math.sqrt(520 / b.ratio));
      return `<span class="p-brand"><svg width="${w}" height="${h}" role="img" aria-label="${b.name}"><use href="#b-${b.slug}"/></svg></span>`;
    };

    // "Split Cassete Samsung Cassete 4 vias" fica repetitivo: só cita o tipo quando o modelo não o traz
    const fullName = p => {
      const semTipo = p.line.toLowerCase().includes(TYPE_SHORT[p.type].toLowerCase().replace('-', ''))
        || p.line.toLowerCase().includes(TYPE_SHORT[p.type].toLowerCase());
      return `${semTipo ? '' : TYPE_FULL[p.type] + ' '}${p.brand} ${p.line}`;
    };

    const productText = (p, withInstall) =>
      `Olá, vim do seu site, quero fazer um orçamento do ${fullName(p)}${p.code ? ` (${p.code})` : ''} de ${fmt(p.btu)} BTUs${p.mode ? ` (${MODE[p.mode].toLowerCase()})` : ''}${withInstall ? ', com instalação' : ''}.${CITY ? ` Estou em ${CITY.name}.` : CITY_ASK}`;

    // abertura do catálogo: começa pelos hi-wall mais vendidos e já mostra piso teto e cassete
    const DESTAQUE = [
      'samsung-hiwall-12000', 'lg-hiwall-9000', 'elgin-pisoteto-36000', 'midea-cassete-24000',
      'midea-hiwall-12000', 'elgin-hiwall-9000', 'samsung-cassete-36000-qf', 'midea-pisoteto-60000',
      'lg-hiwall-12000-qf', 'elgin-hiwall-18000', 'gree-cassete-36000', 'gree-pisoteto-36000',
    ];
    const rank = p => { const i = DESTAQUE.indexOf(p.img); return i < 0 ? DESTAQUE.length : i; };
    const isFiltered = () => state.type !== 'all' || state.brand !== 'all' || state.btu !== 'all';

    const filtered = () => {
      const list = PRODUCTS.filter(p =>
        (state.type === 'all' || p.type === state.type) &&
        (state.brand === 'all' || p.brand === state.brand) &&
        (state.btu === 'all' || p.btu === Number(state.btu)));
      return isFiltered() ? list : list.slice().sort((a, b) => rank(a) - rank(b));
    };

    const card = (p, i, animate) => {
      // todos são inverter: o selo não ajuda a escolher, então o card mostra só o que diferencia
      const feats = p.feats.filter(f => f !== 'Inverter').map(f => `<li>${f}</li>`).join('')
        + (p.mode ? `<li class="${p.mode === 'quente' ? 'hot' : ''}">${MODE[p.mode]}</li>` : '');
      const alt = `${fullName(p)} de ${fmt(p.btu)} BTUs`;
      return `<article class="product${animate ? ' is-enter' : ''}" style="--d:${animate ? Math.min(i, 8) * 0.05 : 0}s" data-i="${PRODUCTS.indexOf(p)}">
        <div class="p-art">
          <span class="tag-type">${TYPE_SHORT[p.type]}</span>
          <img src="${IMG}${p.img}.webp" alt="${alt}" width="640" height="480" loading="lazy" decoding="async">
        </div>
        <div class="p-body">
          ${brandMark(p.brand)}
          <h3 class="p-name">${p.line}</h3>
          ${p.code ? `<p class="p-code">${p.code}</p>` : ''}
          <p class="p-btu"><b>${fmt(p.btu)}</b><span>BTUs</span></p>
          <ul class="p-feats">${feats}</ul>
          <button type="button" class="p-inst" aria-pressed="true"><span class="box"><svg aria-hidden="true"><use href="#i-tick"/></svg></span>Com instalação</button>
          <a class="btn btn-wa btn-block" href="${wa(PAGE_PHONE, productText(p, true))}" target="_blank" rel="noopener">
            <svg aria-hidden="true"><use href="#i-wa"/></svg><span class="t-full">Pedir orçamento</span><span class="t-short">Orçamento</span>
          </a>
        </div>
      </article>`;
    };

    const render = (animate = true) => {
      const list = filtered();
      const visible = list.slice(0, state.limit);
      if (!list.length) {
        const tipo = state.type === 'all' ? 'ar-condicionado' : TYPE_FULL[state.type];
        const marca = state.brand === 'all' ? '' : ` ${state.brand}`;
        const cap = state.btu === 'all' ? '' : ` de ${fmt(state.btu)} BTUs`;
        const txt = `Olá, vim do seu site e procuro um ${tipo}${marca}${cap}. Vocês têm?${CITY ? ` Estou em ${CITY.name}.` : CITY_ASK}`;
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
    };

    const setFilters = next => {
      Object.assign(state, next, { limit: PAGE });
      $$('#f-type button').forEach(b => b.setAttribute('aria-pressed', String(b.dataset.type === state.type)));
      brandBtns.forEach(b => b.setAttribute('aria-pressed', String(b.dataset.brand === state.brand)));
      fBrand.value = state.brand;
      fBtu.value = String(state.btu);
      render();
    };

    $$('#f-type button').forEach(b => b.addEventListener('click', () => setFilters({ type: b.dataset.type })));
    fBrand.addEventListener('change', () => setFilters({ brand: fBrand.value }));
    fBtu.addEventListener('change', () => setFilters({ btu: fBtu.value }));

    // faixa de logos: toca na marca -> catálogo filtrado por ela
    brandBtns.forEach(b => {
      b.setAttribute('aria-pressed', 'false');
      b.addEventListener('click', () => {
        const again = state.brand === b.dataset.brand;
        setFilters({ type: 'all', btu: 'all', brand: again ? 'all' : b.dataset.brand });
        if (!again) $('#aparelhos .toolbar').scrollIntoView({ behavior: reduce ? 'auto' : 'smooth', block: 'start' });
      });
    });

    moreBtn.addEventListener('click', () => {
      const before = state.limit;
      state.limit += PAGE;
      render(false);
      if (!reduce) $$('.product', grid).slice(before).forEach((el, i) => { el.classList.add('is-enter'); el.style.setProperty('--d', `${i * 0.05}s`); });
    });
    // "Com instalação" liga/desliga e a mensagem do WhatsApp acompanha
    grid.addEventListener('click', e => {
      const inst = e.target.closest('.p-inst');
      if (!inst) return;
      const on = inst.getAttribute('aria-pressed') !== 'true';
      inst.setAttribute('aria-pressed', String(on));
      const item = inst.closest('.product');
      $('.btn', item).href = wa(PAGE_PHONE, productText(PRODUCTS[Number(item.dataset.i)], on));
    });
    render(false);

    /* Calculadora de BTU */
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

    const compute = () => {
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
    };
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
  }

  /* diferenciais: pontinhos do carrossel no celular acompanham o arraste */
  const perkGrid = $('.perk-grid');
  const perkDots = $$('.perk-dots i');
  if (perkGrid && perkDots.length) {
    const syncDots = () => {
      const max = perkGrid.scrollWidth - perkGrid.clientWidth;
      const i = max > 0 ? Math.round((perkGrid.scrollLeft / max) * (perkDots.length - 1)) : 0;
      perkDots.forEach((d, k) => d.classList.toggle('is-on', k === i));
    };
    perkGrid.addEventListener('scroll', () => requestAnimationFrame(syncDots), { passive: true });
  }

  /* ano no rodapé */
  const y = $('#year');
  if (y) y.textContent = new Date().getFullYear();
})();
