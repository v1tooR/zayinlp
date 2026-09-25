#!/usr/bin/env python3
"""Gera a landing da Zayin: home + página de serviços, geral e por cidade.

Uso: python3 build.py  ->  dist/index.html, dist/servicos/index.html,
                           dist/<cidade>/index.html, dist/<cidade>/servicos/index.html
Edite CITIES / BRANDS / FAQ abaixo e rode de novo.
"""
import base64
import html
import json
import math
import re
import shutil
from datetime import date
from pathlib import Path
from urllib.parse import quote_plus

ROOT = Path(__file__).parent
SRC = ROOT / "src"
DIST = ROOT / "dist"
DOMAIN = "https://zayinarcondicionado.com.br"

SJC_PHONE = ("5512997067659", "(12) 99706-7659")
JAC_PHONE = ("5512992019832", "(12) 99201-9832")

# ordem geográfica (oeste -> leste, pela Dutra); lat/lng = centro da cidade, para o mapa
CITIES = [
    {"slug": "mogidascruzes", "name": "Mogi das Cruzes", "short": "Mogi", "phone": SJC_PHONE, "lat": -23.5227, "lng": -46.1883},
    {"slug": "jacarei", "name": "Jacareí", "phone": JAC_PHONE, "lat": -23.3053, "lng": -45.9658},
    {"slug": "saojosedoscampos", "name": "São José dos Campos", "short": "SJC", "phone": SJC_PHONE, "lat": -23.1896, "lng": -45.8841},
    {"slug": "cacapava", "name": "Caçapava", "phone": SJC_PHONE, "lat": -23.1017, "lng": -45.7069},
    {"slug": "taubate", "name": "Taubaté", "phone": SJC_PHONE, "lat": -23.0264, "lng": -45.5553},
    {"slug": "pindamonhangaba", "name": "Pindamonhangaba", "short": "Pinda", "phone": SJC_PHONE, "lat": -22.9246, "lng": -45.4613},
]
BUILDER_ORDER = ["saojosedoscampos", "jacarei", "taubate", "pindamonhangaba", "mogidascruzes", "cacapava"]
LITORAL = {"name": "Litoral Norte", "lat": -23.6203, "lng": -45.4131}  # ponto no mapa em Caraguatatuba

# unidades com perfil no Google (Perfil da Empresa / Google Meu Negócio).
# tip = lado do rótulo no mapa, para os dois não se encostarem na vista geral.
# Nota e número de avaliações conferidos em 22/09/2026: atualize aqui quando mudarem.
UNITS = [
    {"slug": "saojosedoscampos", "name": "São José dos Campos", "short": "SJC", "tip": "top", "phone": SJC_PHONE,
     "label": "Base operacional",
     "gname": "Zayin ar condicionado instalação manutenção venda e projetos",
     "addr": "R. Mario Campos, São José dos Campos - SP, 12221-750",
     "street": "R. Mario Campos", "locality": "São José dos Campos", "postal": "12221-750",
     "lat": -23.1669442, "lng": -45.8357906, "place_id": "ChIJrbxfjAdLzJQRSSlSiRFEZSE",
     "rating": 5.0, "reviews": 54,
     "serves": "São José dos Campos, Caçapava, Taubaté, Pindamonhangaba, Mogi das Cruzes e Litoral Norte"},
    {"slug": "jacarei", "name": "Jacareí", "short": "Jacareí", "tip": "left", "phone": JAC_PHONE,
     # escritório: recebe visita com hora marcada, então o botão convida a agendar
     "label": "Escritório", "visit": "Olá, vim do seu site e quero agendar uma visita ao escritório de Jacareí.",
     "gname": "Zayin Ar Condicionado Instalação Venda e Projetos (Jacareí)",
     "addr": "Espaço Ventura, R. Enéas de Mesquita, 145, sala 01, Jardim Mesquita, Jacareí - SP, 12327-690",
     "street": "R. Enéas de Mesquita, 145, sala 01 - Jardim Mesquita", "locality": "Jacareí", "postal": "12327-690",
     "lat": -23.2998325, "lng": -45.9664184, "place_id": "ChIJWQqN3DbLzZQRca5MLfaHHE8",
     "rating": 5.0, "reviews": 7,
     "serves": "Jacareí"},
]
for u in UNITS:
    q = quote_plus(u["gname"])
    u["gmaps"] = f"https://www.google.com/maps/search/?api=1&query={q}&query_place_id={u['place_id']}"
    u["route"] = f"https://www.google.com/maps/dir/?api=1&destination={q}&destination_place_id={u['place_id']}"

# avaliações do Google mostradas na seção de garantia (todas 5 estrelas), copiadas dos perfis em 23/09/2026.
# Texto como o cliente escreveu; nome só com a inicial do sobrenome; sem a foto de perfil (é pessoal).
# photo = foto que o cliente postou na avaliação (assets/photos/<photo>.webp); sem photo o card é só texto.
REVIEWS = [
    {"name": "Tatiane K.", "unit": "saojosedoscampos", "photo": "cliente-tatiane",
     "text": "Escolhi a Zayin ao acaso pelo Google, e tomei como base as avaliações dos clientes anteriores, portanto "
             "gostaria de deixar a minha opinião após o serviço executado. Primeiramente gostaria de falar do atendimento "
             "e atenção ao cliente, o Lucas foi meu primeiro contato e agradeço pela disposição em me atender com atenção. "
             "Os meninos que vieram para a instalação uma simpatia também, preço justo, cumprem o prazo e testam cada "
             "aparelho antes de finalizarem o serviço. Estão de parabéns e super indico"},
    {"name": "Hisashi H.", "unit": "saojosedoscampos", "photo": "cliente-hisashi",
     "text": "A instalação foi feita com bastante atenção pelo técnico, o valor também estáva dentro do esperado, "
             "material de cobre, eu tive uma boa experiência com a empresa."},
    {"name": "Clarisson O.", "unit": "saojosedoscampos",
     "text": "Instalaram meu ar-condicionado e ficou muito bom. Fizeram um serviço bem caprichado e organizado. "
             "Testaram tudo na hora e explicaram o funcionamento. Até agora está funcionando perfeito. Recomendo."},
    {"name": "Ricardo S.", "unit": "jacarei", "photo": "cliente-ricardo",
     "text": "Excelente atendimento e mão de obra especializada, very good!"},
    {"name": "Cleusa G.", "unit": "saojosedoscampos", "photo": "cliente-cleusa",
     "text": "Desde o início, só alegria. Empresa: organizada, profissional, responde rapidinho, muito foco no cliente. "
             "Instalação: nota 10. Colaboradores eficientes, prazo bem rápido, pessoal bastante conhecedor do assunto. Nota 10."},
    {"name": "Rafael B.", "unit": "saojosedoscampos",
     "text": "Escolhi eles devido a nota no Google e nao me arrepender. Foram extremamente atenciosos entendendo o que "
             "queria e produzeram e executaram um excelente serviço. Super bem feito e no capricho."},
    {"name": "Osvaldo J.", "unit": "saojosedoscampos", "photo": "cliente-osvaldo",
     "text": "Ótimo serviço, instalação muito bem feita, pontuais."},
    {"name": "Leonardo R.", "unit": "jacarei",
     "text": "Empresa de confiança, preco justo e qualidade. Instalaram 4 ar na minha casa, recomendadissimo!"},
    {"name": "Taislane S.", "unit": "saojosedoscampos", "photo": "cliente-taislane",
     "text": "O Lucas é muito atencioso e educado! Fez a instalação do meu ar condicionado e ficou ótimo! "
             "Super recomendo o serviço!"},
    {"name": "Adriano A.", "unit": "jacarei",
     "text": "Ótimos profissionais , deixa o local limpo e ótimo preço"},
]

for c in CITIES:
    # a cidade é atendida pela unidade do mesmo WhatsApp
    c["unit"] = next(u["slug"] for u in UNITS if u["phone"] == c["phone"])

# marcas da faixa de logos e dos cards (logo em assets/brands/<slug>.svg).
# O nome precisa ser igual ao campo "brand" do catálogo em src/app.js.
BRANDS = [
    {"slug": "samsung", "name": "Samsung"},
    {"slug": "lg", "name": "LG"},
    {"slug": "midea", "name": "Midea"},
    {"slug": "elgin", "name": "Elgin"},
    {"slug": "gree", "name": "Gree"},
    {"slug": "daikin", "name": "Daikin"},
]

# frase do destaque no topo da home: texto definido pela Zayin, não alterar
KICKER = "Autorizado a venda, instalação com garantia."

# fotos oficiais dos aparelhos (assets/products/*.webp -> dist/img/produtos/)
PRODUCT_IMG_DIR = "img/produtos"
# fotos da equipe e da unidade (assets/photos/*.webp -> dist/img/fotos/)
PHOTO_DIR = "img/fotos"

SERVICES = ["Instalação de ar-condicionado", "Manutenção preventiva", "Higienização de ar-condicionado",
            "Infraestrutura para ar-condicionado em obra"]


def faq_items(city, kind):
    onde = f"em {city['name']}" if city else "na sua cidade"
    comprar = ("Posso comprar o aparelho e a instalação juntos?",
               ["Sim. A Zayin é revenda autorizada: escolha o modelo no catálogo, peça o orçamento com instalação e receba o aparelho instalado, com garantia no serviço e garantia de fábrica no equipamento."])
    items = [
        ("Vocês instalam aparelho comprado em outra loja ou pela internet?",
         [f"Sim. A instalação é o principal serviço da Zayin {onde}. Mande pelo WhatsApp a marca, o modelo e a capacidade em BTUs do aparelho, e se possível fotos do local."]),
        ("Qual é a garantia da instalação?",
         ["A instalação tem garantia de serviço: se aparecer algum problema, a Zayin vai até o local e verifica.",
          "Nos aparelhos vendidos pela Zayin, a garantia é de 2 anos na evaporadora e de 10 anos na condensadora, conforme as condições de cada fabricante."]),
        ("Quanto custa para instalar?",
         ["O valor depende do tipo de aparelho, da capacidade, da distância entre as unidades e da infraestrutura do local. Envie essas informações pelo WhatsApp e receba o orçamento sem compromisso."]),
        ("Meu imóvel precisa ter infraestrutura pronta?",
         ["Não. Se o imóvel ainda não tem, a Zayin executa a infraestrutura, com passagem de tubulação e dreno, inclusive durante obra ou reforma."]),
        ("Vocês atendem empresas e comércios?",
         ["Sim. Instalamos e fazemos manutenção em aparelhos hi-wall, piso teto e cassete para lojas, escritórios, clínicas e outros espaços comerciais."]),
        ("Qual capacidade de BTUs eu preciso?",
         ["Use a calculadora na seção de aparelhos para ter uma estimativa pelo tamanho do ambiente. A equipe confirma a capacidade certa no orçamento."]),
        ("Quais cidades vocês atendem?",
         ["São José dos Campos, Jacareí, Taubaté, Pindamonhangaba, Caçapava, Mogi das Cruzes e o Litoral Norte."]),
        ("Onde ficam as unidades da Zayin?",
         [f"{u['name']}: {u['addr']}." for u in UNITS]),
    ]
    if kind == "home":
        return [comprar] + items
    return items[:1] + [comprar] + items[1:]


def data_uri(path):
    return "data:image/webp;base64," + base64.b64encode(path.read_bytes()).decode()


def esc(s):
    return html.escape(s, quote=True)


def nota(x):
    return f"{x:.1f}".replace(".", ",")


def google_totals():
    reviews = sum(u["reviews"] for u in UNITS)
    rating = sum(u["rating"] * u["reviews"] for u in UNITS) / reviews
    return nota(rating), reviews


GOOGLE_G = ('<svg viewBox="0 0 24 24" aria-hidden="true">'
            '<path fill="#4285F4" d="M23.49 12.27c0-.79-.07-1.54-.19-2.27H12v4.51h6.47c-.29 1.48-1.14 2.73-2.4 3.58v3h3.86c2.26-2.09 3.56-5.17 3.56-8.82z"/>'
            '<path fill="#34A853" d="M12 24c3.24 0 5.95-1.08 7.93-2.91l-3.86-3c-1.08.72-2.45 1.16-4.07 1.16-3.13 0-5.78-2.11-6.73-4.96H1.29v3.09C3.26 21.3 7.31 24 12 24z"/>'
            '<path fill="#FBBC05" d="M5.27 14.29c-.25-.72-.38-1.49-.38-2.29s.14-1.57.38-2.29V6.62H1.29C.47 8.24 0 10.06 0 12s.47 3.76 1.29 5.38l3.98-3.09z"/>'
            '<path fill="#EA4335" d="M12 4.75c1.77 0 3.35.61 4.6 1.8l3.42-3.42C17.95 1.19 15.24 0 12 0 7.31 0 3.26 2.7 1.29 6.62l3.98 3.09c.95-2.85 3.6-4.96 6.73-4.96z"/>'
            '</svg>')


def reviews_html(root, g_rating, g_reviews):
    """Bloco de avaliações do Google na seção de garantia: nota geral e carrossel de cards."""
    photos = f"{root}{PHOTO_DIR}/"
    short = {u["slug"]: u["short"] for u in UNITS}
    stars = ('<span class="stars" role="img" aria-label="5 estrelas">'
             + '<svg aria-hidden="true"><use href="#i-star"/></svg>' * 5 + '</span>')
    colors = ["#005094", "#062B52", "#0A7FB8", "#1F7A5C"]  # fundo do círculo com a inicial
    cards = []
    for i, r in enumerate(REVIEWS):
        img = ""
        if r.get("photo"):
            img = (f'<img class="rv-photo" src="{photos}{r["photo"]}.webp" alt="Ar-condicionado instalado pela Zayin, '
                   f'foto postada por {esc(r["name"])} na avaliação" data-full="{photos}{r["photo"]}-grande.webp" loading="lazy" width="600" height="800">')
        cards.append(f'''<article class="rv-card{" has-photo" if img else ""}">
          {img}<div class="rv-body">
            {stars}
            <p class="rv-text">{esc(r["text"])}</p>
            <div class="rv-who"><span class="rv-av" style="--c:{colors[i % len(colors)]}" aria-hidden="true">{esc(r["name"][0])}</span><div><b>{esc(r["name"])}</b><small>Unidade {esc(short[r["unit"]])}</small></div></div>
          </div>
        </article>''')
    cards_html = "\n        ".join(cards)
    return f'''<div class="rv" data-reveal>
      <div class="rv-head">
        <span class="rv-g">{GOOGLE_G}</span>
        <span class="rv-score"><b>{g_rating}</b>{stars}</span>
        <span class="rv-count">{g_reviews} avaliações<br>no Google</span>
      </div>
      <div class="rv-track" data-zoom tabindex="0" role="region" aria-label="Avaliações de clientes no Google">
        {cards_html}
      </div>
      <div class="rv-foot">
        <div class="rv-nav">
          <button class="rv-prev" type="button" aria-label="Avaliação anterior"><svg aria-hidden="true"><use href="#i-arrow"/></svg></button>
          <button class="rv-next" type="button" aria-label="Próxima avaliação"><svg aria-hidden="true"><use href="#i-arrow"/></svg></button>
        </div>
        <a class="rv-all" href="{esc(UNITS[0]["gmaps"])}" target="_blank" rel="noopener">Ver todas no Google<svg aria-hidden="true"><use href="#i-arrow"/></svg></a>
      </div>
    </div>'''


def unit_cards(cur, msg_city):
    """Cards das unidades ao lado do mapa: endereço, nota no Google, rota e WhatsApp."""
    units = sorted(UNITS, key=lambda u: u["slug"] != cur)  # a unidade da página vem primeiro
    out = []
    for u in units:
        # a unidade de SJC também atende as cidades sem unidade: a mensagem cita a cidade da página
        msg = "Olá, vim do seu site e quero fazer um orçamento."
        msg += " Estou em Jacareí." if u["slug"] == "jacarei" else (msg_city if cur != "jacarei" else "")
        btn, nocity = "WhatsApp", ""
        if u.get("visit"):
            btn, msg, nocity = "Agendar visita", u["visit"], " data-wa-nocity"
        stars = "".join('<svg aria-hidden="true"><use href="#i-star"/></svg>' for _ in range(round(u["rating"])))
        out.append(f'''<article class="unit{" is-current" if u["slug"] == cur else ""}" data-unit="{u["slug"]}">
          <div class="u-head">
            <span class="u-ico"><svg aria-hidden="true"><use href="#i-pin"/></svg></span>
            <div><small>{esc(u["label"])}</small><h3>{esc(u["name"])}</h3></div>
          </div>
          <p class="u-addr">{esc(u["addr"])}</p>
          <a class="u-rate" href="{esc(u["gmaps"])}" target="_blank" rel="noopener">
            <span class="stars">{stars}</span><b>{nota(u["rating"])}</b><span>{u["reviews"]} avaliações no Google</span>
          </a>
          <p class="u-serves"><b>WhatsApp {u["phone"][1]}</b>Atende {esc(u["serves"])}</p>
          <div class="u-actions">
            <a class="btn btn-wa btn-sm" data-wa="{esc(msg)}" data-wa-phone="{u["phone"][0]}"{nocity} href="#"><svg aria-hidden="true"><use href="#i-wa"/></svg>{btn}</a>
            <a class="btn btn-ghost btn-sm" href="{esc(u["route"])}" target="_blank" rel="noopener"><svg aria-hidden="true"><use href="#i-route"/></svg>Como chegar</a>
          </div>
        </article>''')
    return "\n        ".join(out)


def load_brands():
    """Lê os SVGs das marcas: vira <symbol> no sprite e tamanho equilibrado na faixa."""
    out = []
    for b in BRANDS:
        svg = (ROOT / "assets" / "brands" / f"{b['slug']}.svg").read_text(encoding="utf-8")
        vb = re.search(r'viewBox="([^"]+)"', svg).group(1)
        inner = re.sub(r"<!--.*?-->", "", svg.split(">", 1)[1].rsplit("</svg>", 1)[0], flags=re.S).strip()
        _, _, w, h = (float(v) for v in vb.split())
        ratio = w / h
        # mesma "área visual" para logos largos e compactos
        area = 2600
        out.append({**b, "vb": vb, "inner": inner, "ratio": round(ratio, 3),
                    "w": round(math.sqrt(area * ratio)), "h": round(math.sqrt(area / ratio))})
    return out


def include_parts(tpl):
    return re.sub(r"\{\{>\s*(\w+)\s*\}\}", lambda m: (SRC / "parts" / f"{m.group(1)}.html").read_text(encoding="utf-8"), tpl)


def build_page(city, kind, css, js, logo, logo_w, brands, root_prefix=None):
    is_city = city is not None
    is_home = kind == "home"
    name = city["name"] if is_city else None
    cur = city["slug"] if is_city else None
    phone, phone_label = city["phone"] if is_city else SJC_PHONE
    other_unit = next(u for u in UNITS if u["phone"] != (phone, phone_label))

    # caminhos relativos até a raiz do site
    depth = (1 if is_city else 0) + (0 if is_home else 1)
    root = root_prefix if root_prefix is not None else ("../" * depth or "./")
    home_href = f"{root}{cur}/" if is_city else root
    svc_href = f"{home_href}servicos/"
    home_prefix = "" if is_home else home_href
    svc_prefix = svc_href if is_home else ""

    if is_home:
        if is_city:
            title = f"Ar-condicionado em {name} | Zayin"
            desc = (f"Venda e instalação de ar-condicionado em {name}, com garantia. Modelos hi-wall, piso teto e "
                    "cassete das marcas líderes. Peça seu orçamento.")
            canon = f"{DOMAIN}/{cur}/"
        else:
            title = "Ar-condicionado no Vale do Paraíba | Zayin"
            desc = ("Venda e instalação de ar-condicionado com garantia no Vale do Paraíba, em Mogi das Cruzes e no "
                    "Litoral Norte. Peça seu orçamento.")
            canon = f"{DOMAIN}/"
        kicker = KICKER
    else:
        if is_city:
            title = f"Instalação de ar-condicionado em {name} | Zayin"
            desc = (f"Instalação de ar-condicionado em {name} com garantia de serviço. Manutenção, "
                    "higienização e infraestrutura para obra. Peça seu orçamento.")
            canon = f"{DOMAIN}/{cur}/servicos/"
            kicker = f"Serviços de ar-condicionado em {name}"
        else:
            title = "Instalação e manutenção de ar-condicionado | Zayin"
            desc = ("Instalação e manutenção de ar-condicionado com garantia no Vale do Paraíba, em Mogi das Cruzes "
                    "e no Litoral Norte. Peça seu orçamento.")
            canon = f"{DOMAIN}/servicos/"
            kicker = "Instalação, manutenção e higienização"

    if is_city:
        h1_city = f"em {name}"
        msg_city = f" Estou em {name}."
        city_btn = name
        city_btn_short = city.get("short", name)
        region = f"{name} e região"
        final_p = f"Chame a Zayin em {name} e receba seu orçamento pelo WhatsApp."
    else:
        h1_city = "no Vale do Paraíba"
        msg_city = ""
        city_btn = "Sua cidade"
        city_btn_short = "Sua cidade"
        region = "Vale do Paraíba, Mogi e litoral"
        final_p = "Chame a Zayin e receba seu orçamento pelo WhatsApp."

    # trocar de cidade mantém o tipo de página
    same_kind = "" if is_home else "servicos/"
    cur_attr = ' aria-current="page"'
    city_menu = "\n          ".join(
        f'<a href="{root}{c["slug"]}/{same_kind}"{cur_attr if c["slug"] == cur else ""}>{esc(c["name"])}</a>'
        for c in sorted(CITIES, key=lambda c: BUILDER_ORDER.index(c["slug"]))
    )

    # mapa das unidades: botões por cidade (sem cidade na página, começa mostrando todas)
    by_menu = sorted(CITIES, key=lambda c: BUILDER_ORDER.index(c["slug"]))
    loc_chips = "\n        ".join(
        [f'<button type="button" data-loc="all" aria-pressed="{str(not cur).lower()}">Todas as unidades</button>']
        + [f'<button type="button" data-loc="{c["slug"]}" aria-pressed="{str(c["slug"] == cur).lower()}">{esc(c["name"])}</button>'
           for c in by_menu]
    )
    unit_name = {u["slug"]: u["name"] for u in UNITS}
    resumo = " e ".join(f"{u['label'][:1].lower()}{u['label'][1:]} em {u['name']}" for u in UNITS)
    loc_notes = {"all": f"A Zayin tem {resumo}. Escolha uma cidade para ver no mapa."}
    for c in CITIES:
        if c["slug"] in unit_name:
            u = next(x for x in UNITS if x["slug"] == c["slug"])
            # na home só existe o mapa, então a nota traz o endereço; na de serviços ele está no card
            loc_notes[c["slug"]] = (f"{u['label']} da Zayin em {c['name']}: {u['addr']}." if is_home
                                    else f"{u['label']} da Zayin em {c['name']}. Endereço, rota e WhatsApp no card.")
        else:
            loc_notes[c["slug"]] = (f"Em {c['name']}, a equipe da Zayin vai até você. "
                                    f"O atendimento é pela unidade de {unit_name[c['unit']]}.")
    loc_note = loc_notes[cur or "all"]
    # os cards das unidades só na página de serviços: na home eles poluem, lá fica só o mapa
    units_html = "" if is_home else f'<div class="units">\n        {unit_cards(cur, msg_city)}\n        </div>'
    g_rating, g_reviews = google_totals()

    if is_home:
        nav = [("#aparelhos", "Aparelhos"), ("#marcas", "Marcas"), (svc_href, "Serviços"),
               ("#garantia", "Garantia"), ("#cidades", "Unidades"), ("#duvidas", "Dúvidas")]
        drawer = [("#aparelhos", "Aparelhos"), ("#marcas", "Marcas"), ("#instalacao", "Instalação"),
                  (svc_href, "Todos os serviços"), ("#garantia", "Garantia"), ("#cidades", "Unidades e mapa"),
                  (f"{svc_href}#sobre", "Sobre a Zayin"), ("#duvidas", "Dúvidas")]
    else:
        nav = [(f"{home_href}#aparelhos", "Aparelhos"), ("#instalacao", "Instalação"), ("#outros-servicos", "Serviços"),
               ("#orcamento", "Orçamento"), ("#garantia", "Garantia"), ("#duvidas", "Dúvidas")]
        drawer = [(home_href, "Início"), (f"{home_href}#aparelhos", "Aparelhos"), ("#instalacao", "Instalação"),
                  ("#outros-servicos", "Outros serviços"), ("#sobre", "Sobre a Zayin"), ("#orcamento", "Montar pedido"),
                  ("#garantia", "Garantia"), ("#cidades", "Unidades e mapa"), ("#duvidas", "Dúvidas")]
    nav_html = "\n      ".join(f'<a href="{h}">{esc(t)}</a>' for h, t in nav)
    drawer_html = "\n  ".join(f'<a class="dl" href="{h}">{esc(t)}</a>' for h, t in drawer)

    # sem cidade na página, o montador não presume nenhuma: a pessoa escolhe
    opts = [] if cur else ['<option value="" selected>Selecione sua cidade</option>']
    opts += [f'<option value="{c}"{" selected" if c == cur else ""}>{esc(next(x["name"] for x in CITIES if x["slug"] == c))}</option>'
             for c in BUILDER_ORDER]
    opts += ['<option value="litoral">Litoral Norte</option>', '<option value="outra">Outra cidade</option>']
    city_options = "\n              ".join(opts)

    footer_cities = "\n          ".join(
        f'<li><a href="{root}{c["slug"]}/">Ar-condicionado em {esc(c["name"])}</a></li>'
        for c in sorted(CITIES, key=lambda c: BUILDER_ORDER.index(c["slug"]))
    )

    brand_symbols = "\n  ".join(f'<symbol id="b-{b["slug"]}" viewBox="{b["vb"]}">{b["inner"]}</symbol>' for b in brands)
    brand_list = "\n      ".join(
        f'<li data-reveal style="--d:{i * .06:.2f}s"><button class="brand-btn" type="button" data-brand="{esc(b["name"])}" '
        f'aria-label="Ver aparelhos {esc(b["name"])}"><svg style="--w:{b["w"]}px;--h:{b["h"]}px" aria-hidden="true">'
        f'<use href="#b-{b["slug"]}"/></svg></button></li>'
        for i, b in enumerate(brands)
    )

    faqs = faq_items(city, kind)
    faq_html = "\n      ".join(
        f'<details><summary>{esc(q)}<span class="pm"><svg aria-hidden="true"><use href="#i-plus"/></svg></span></summary>'
        f'<div class="ans">{"".join(f"<p>{esc(p)}</p>" for p in ps)}</div></details>'
        for q, ps in faqs
    )

    organization_id = f"{DOMAIN}/#organization"
    website_id = f"{DOMAIN}/#website"
    webpage_id = f"{canon}#webpage"
    logo_url = f"{DOMAIN}/img/logo-color.webp"
    share_image = f"{DOMAIN}/img/fotos/tecnico-condensadora-1200.webp"
    organization = {
        "@type": "Organization",
        "@id": organization_id,
        "name": "Zayin Ar Condicionado",
        "url": f"{DOMAIN}/",
        "logo": {"@type": "ImageObject", "url": logo_url},
        "description": ("Venda, instalação, manutenção e higienização de ar-condicionado no Vale do Paraíba, "
                        "em Mogi das Cruzes e no Litoral Norte."),
        "slogan": "Autorizado a venda, instalação com garantia.",
        "brand": [{"@type": "Brand", "name": b["name"]} for b in brands],
        "sameAs": ["https://www.instagram.com/zayinarcondicionado/"],
        "contactPoint": [{
            "@type": "ContactPoint",
            "telephone": "+55" + u["phone"][0][2:],
            "contactType": "customer service",
            "areaServed": u["serves"],
            "availableLanguage": "pt-BR",
        } for u in UNITS],
    }
    locations = [{
            "@type": "HVACBusiness",
            "@id": f"{DOMAIN}/#{u['slug']}",
            "name": f"Zayin Ar Condicionado {u['name']}",
            "url": f"{DOMAIN}/{u['slug']}/servicos/",
            "image": share_image,
            "telephone": "+55" + u["phone"][0][2:],
            "parentOrganization": {"@id": organization_id},
            "address": {"@type": "PostalAddress", "streetAddress": u["street"], "addressLocality": u["locality"],
                        "addressRegion": "SP", "postalCode": u["postal"], "addressCountry": "BR"},
            "geo": {"@type": "GeoCoordinates", "latitude": u["lat"], "longitude": u["lng"]},
            "hasMap": u["gmaps"],
            "sameAs": [u["gmaps"]],
            "areaServed": u["serves"],
        } for u in UNITS]
    website = {
        "@type": "WebSite",
        "@id": website_id,
        "url": f"{DOMAIN}/",
        "name": "Zayin Ar Condicionado",
        "inLanguage": "pt-BR",
        "publisher": {"@id": organization_id},
    }
    webpage = {
        "@type": "WebPage",
        "@id": webpage_id,
        "url": canon,
        "name": title,
        "description": desc,
        "inLanguage": "pt-BR",
        "isPartOf": {"@id": website_id},
        "about": {"@id": organization_id},
        "primaryImageOfPage": {"@type": "ImageObject", "url": share_image},
    }
    graph = [organization, website, webpage, *locations]
    graph.append({
        "@type": "FAQPage",
        "@id": f"{canon}#faq",
        "url": canon,
        "inLanguage": "pt-BR",
        "mainEntity": [
            {"@type": "Question", "name": q,
             "acceptedAnswer": {"@type": "Answer", "text": " ".join(ps)}}
            for q, ps in faqs
        ],
    })
    if not is_home:
        webpage["mainEntity"] = {
            "@type": "OfferCatalog",
            "name": "Serviços de ar-condicionado",
            "itemListElement": [{
                "@type": "Offer",
                "itemOffered": {
                    "@type": "Service",
                    "name": s,
                    "provider": {"@id": organization_id},
                    "areaServed": name or "Vale do Paraíba, Mogi das Cruzes e Litoral Norte",
                },
            } for s in SERVICES],
        }
    if is_city or not is_home:
        home_abs = f"{DOMAIN}/"
        crumbs = [{"@type": "ListItem", "position": 1, "name": "Início", "item": home_abs}]
        if is_city:
            city_abs = f"{DOMAIN}/{cur}/"
            crumbs.append({"@type": "ListItem", "position": 2, "name": name, "item": city_abs})
        if not is_home:
            crumbs.append({"@type": "ListItem", "position": len(crumbs) + 1, "name": "Serviços", "item": canon})
        graph.append({
            "@type": "BreadcrumbList",
            "@id": f"{canon}#breadcrumb",
            "itemListElement": crumbs,
        })
    jsonld = {"@context": "https://schema.org", "@graph": graph}

    page_cfg = {
        "kind": kind,
        "city": ({"slug": cur, "name": name, "phone": phone, "phoneLabel": phone_label} if is_city else None),
        "cities": [{"slug": c["slug"], "name": c["name"], "phone": c["phone"][0], "phoneLabel": c["phone"][1],
                    "short": c.get("short", c["name"]), "lat": c["lat"], "lng": c["lng"], "unit": c["unit"],
                    "href": f"{root}{c['slug']}/{same_kind}"}
                   for c in CITIES],
        "units": [{"slug": u["slug"], "name": u["name"], "short": u["short"], "tip": u["tip"],
                   "lat": u["lat"], "lng": u["lng"], "gmaps": u["gmaps"]} for u in UNITS],
        "litoral": LITORAL,
        "locNotes": loc_notes,
        "brands": [{"slug": b["slug"], "name": b["name"], "ratio": b["ratio"]} for b in brands],
        "imgBase": f"{root}{PRODUCT_IMG_DIR}/",
        "defaultPhone": SJC_PHONE[0],
        "defaultPhoneLabel": SJC_PHONE[1],
    }

    # capa do vídeo do topo: é a primeira imagem que aparece, então já vem no <head>
    preload = (f'<link rel="preload" as="image" href="{root}video/fundo-poster.webp" media="(max-width: 900px)">\n'
               f'<link rel="preload" as="image" href="{root}video/hero-poster.webp" media="(min-width: 901px)">'
               if is_home else "")

    main = include_parts((SRC / f"{'home' if is_home else 'servicos'}.html").read_text(encoding="utf-8"))
    tpl = (SRC / "layout.html").read_text(encoding="utf-8").replace("{{MAIN}}", main)
    repl = {
        "{{TITLE}}": esc(title),
        "{{DESC}}": esc(desc),
        "{{CANON}}": canon,
        "{{OG_IMAGE}}": share_image,
        "{{KIND}}": kind,
        "{{KICKER}}": esc(kicker),
        # na home o header começa transparente, por cima do vídeo
        "{{HEADER_CLASS}}": " is-over" if is_home else "",
        "{{H1_CITY}}": esc(h1_city),
        "{{REGION}}": esc(region),
        "{{MSG_CITY}}": esc(msg_city),
        "{{CITY_BTN}}": esc(city_btn),
        "{{CITY_BTN_SHORT}}": esc(city_btn_short),
        "{{FINAL_P}}": esc(final_p),
        "{{ROOT}}": root,
        "{{HOME_HREF}}": home_href,
        "{{SVC_HREF}}": svc_href,
        "{{HOME_PREFIX}}": home_prefix,
        "{{SVC_PREFIX}}": svc_prefix,
        "{{NAV}}": nav_html,
        "{{DRAWER}}": drawer_html,
        "{{PHONE_LABEL}}": phone_label,
        "{{PHONE}}": phone,
        "{{OTHER_UNIT_NAME}}": esc(other_unit["name"]),
        "{{OTHER_PHONE}}": other_unit["phone"][0],
        "{{OTHER_PHONE_LABEL}}": other_unit["phone"][1],
        "{{CITY_MENU}}": city_menu,
        "{{LOC_CHIPS}}": loc_chips,
        "{{LOC_NOTE}}": esc(loc_note),
        "{{UNITS}}": units_html,
        "{{LOC_CLASS}}": " is-map-only" if is_home else "",
        "{{G_RATING}}": g_rating,
        "{{G_REVIEWS}}": str(g_reviews),
        "{{REVIEWS}}": reviews_html(root, g_rating, g_reviews),
        "{{PHOTOS}}": f"{root}{PHOTO_DIR}/",
        "{{PRELOAD}}": preload,
        "{{CITY_OPTIONS}}": city_options,
        "{{FOOTER_CITIES}}": footer_cities,
        "{{BRAND_SYMBOLS}}": brand_symbols,
        "{{BRAND_LIST}}": brand_list,
        "{{FAQ}}": faq_html,
        "{{JSONLD}}": json.dumps(jsonld, ensure_ascii=False).replace("</", "<\\/"),
        "{{CITY_JSON}}": json.dumps(page_cfg, ensure_ascii=False).replace("</", "<\\/"),
        "{{LOGO}}": logo,
        "{{LOGO_W}}": logo_w,
        "{{CSS}}": css,
        "{{JS}}": js,
    }
    # CSS/JS por último, para que placeholders dentro deles nunca sejam tocados
    order = [k for k in repl if k not in ("{{CSS}}", "{{JS}}")] + ["{{CSS}}", "{{JS}}"]
    for k in order:
        tpl = tpl.replace(k, repl[k])
    assert "{{" not in tpl.replace(css, "").replace(js, ""), "placeholder sem valor"
    return tpl


def write(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    print("ok", path, path.stat().st_size // 1024, "KB")


def copy_video():
    src = ROOT / "assets" / "video"
    dst = DIST / "video"
    dst.mkdir(parents=True, exist_ok=True)
    for f in sorted([*src.glob("*.mp4"), *src.glob("*.webp")]):
        shutil.copyfile(f, dst / f.name)


def copy_photos():
    src = ROOT / "assets" / "photos"
    dst = DIST / PHOTO_DIR
    dst.mkdir(parents=True, exist_ok=True)
    for f in sorted(src.glob("*.webp")):
        shutil.copyfile(f, dst / f.name)


def copy_product_images():
    src = ROOT / "assets" / "products"
    dst = DIST / PRODUCT_IMG_DIR
    dst.mkdir(parents=True, exist_ok=True)
    for f in sorted(src.glob("*.webp")):
        shutil.copyfile(f, dst / f.name)
    return len(list(src.glob("*.webp")))


def copy_branding():
    img = DIST / "img"
    img.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(ROOT / "assets" / "logo-color.webp", img / "logo-color.webp")
    shutil.copyfile(ROOT / "assets" / "logo-white.webp", img / "logo-white.webp")
    shutil.copyfile(ROOT / "favicon.svg", DIST / "favicon.svg")


def public_urls():
    urls = [f"{DOMAIN}/", f"{DOMAIN}/servicos/"]
    for city in CITIES:
        urls.extend((f"{DOMAIN}/{city['slug']}/", f"{DOMAIN}/{city['slug']}/servicos/"))
    return urls


def sitemap_xml():
    today = date.today().isoformat()
    items = "\n".join(
        f"  <url><loc>{esc(url)}</loc><lastmod>{today}</lastmod></url>"
        for url in public_urls()
    )
    return ("<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n"
            "<urlset xmlns=\"http://www.sitemaps.org/schemas/sitemap/0.9\">\n"
            f"{items}\n</urlset>\n")


def robots_txt():
    return f"User-agent: *\nAllow: /\n\nSitemap: {DOMAIN}/sitemap.xml\n"


def main():
    css = (SRC / "styles.css").read_text(encoding="utf-8")
    js = (SRC / "app.js").read_text(encoding="utf-8")
    logo = data_uri(ROOT / "assets" / "logo-color.webp")
    logo_w = data_uri(ROOT / "assets" / "logo-white.webp")
    brands = load_brands()
    print("ok", copy_product_images(), "fotos de aparelhos ->", DIST / PRODUCT_IMG_DIR)
    copy_video()
    copy_photos()
    copy_branding()
    for city in [None] + CITIES:
        base = DIST / city["slug"] if city else DIST
        write(base / "index.html", build_page(city, "home", css, js, logo, logo_w, brands))
        write(base / "servicos" / "index.html", build_page(city, "servicos", css, js, logo, logo_w, brands))
    # A Hostinger publica a raiz do repositório; o .htaccess encaminha os ativos e as rotas para dist/.
    write(ROOT / "index.html", build_page(None, "home", css, js, logo, logo_w, brands, root_prefix="./"))
    for base in (ROOT, DIST):
        write(base / "sitemap.xml", sitemap_xml())
        write(base / "robots.txt", robots_txt())


if __name__ == "__main__":
    main()
