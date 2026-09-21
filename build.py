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
from pathlib import Path

ROOT = Path(__file__).parent
SRC = ROOT / "src"
DIST = ROOT / "dist"
DOMAIN = "https://zayinarcondicionado.com"

SJC_PHONE = ("5512997067659", "(12) 99706-7659")
JAC_PHONE = ("5512992019832", "(12) 99201-9832")

# ordem geográfica (oeste -> leste, pela Dutra)
CITIES = [
    {"slug": "mogidascruzes", "name": "Mogi das Cruzes", "short": "Mogi", "phone": SJC_PHONE},
    {"slug": "jacarei", "name": "Jacareí", "phone": JAC_PHONE},
    {"slug": "saojosedoscampos", "name": "São José dos Campos", "short": "SJC", "phone": SJC_PHONE},
    {"slug": "cacapava", "name": "Caçapava", "phone": SJC_PHONE},
    {"slug": "taubate", "name": "Taubaté", "phone": SJC_PHONE},
    {"slug": "pindamonhangaba", "name": "Pindamonhangaba", "short": "Pinda", "phone": SJC_PHONE},
]
BUILDER_ORDER = ["saojosedoscampos", "jacarei", "taubate", "pindamonhangaba", "mogidascruzes", "cacapava"]

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
         ["O serviço de instalação tem 6 meses de garantia.",
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
    ]
    if kind == "home":
        return [comprar] + items
    return items[:1] + [comprar] + items[1:]


def data_uri(path):
    return "data:image/webp;base64," + base64.b64encode(path.read_bytes()).decode()


def esc(s):
    return html.escape(s, quote=True)


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

    # caminhos relativos até a raiz do site
    depth = (1 if is_city else 0) + (0 if is_home else 1)
    root = root_prefix if root_prefix is not None else ("../" * depth or "./")
    home_href = f"{root}{cur}/" if is_city else root
    svc_href = f"{home_href}servicos/"
    home_prefix = "" if is_home else home_href
    svc_prefix = svc_href if is_home else ""

    if is_home:
        if is_city:
            title = f"Ar-Condicionado em {name}: Compra e Instalação com Garantia | Zayin"
            desc = (f"Compre seu ar-condicionado em {name} com instalação e garantia. Hi-wall, piso teto e cassete "
                    "das marcas líderes, com entrega rápida. Orçamento pelo WhatsApp.")
            canon = f"{DOMAIN}/{cur}/"
        else:
            title = "Zayin Ar Condicionado | Compra e instalação com garantia no Vale do Paraíba"
            desc = ("Compra e instalação de ar-condicionado com garantia e entrega rápida em São José dos Campos, Jacareí, "
                    "Taubaté, Pindamonhangaba, Caçapava, Mogi das Cruzes e Litoral Norte. Orçamento pelo WhatsApp.")
            canon = f"{DOMAIN}/"
        kicker = KICKER
    else:
        if is_city:
            title = f"Instalação de Ar-Condicionado em {name} com Garantia | Zayin"
            desc = (f"Instalação de ar-condicionado em {name} com 6 meses de garantia no serviço. Manutenção, "
                    "higienização e infraestrutura para obra. Orçamento pelo WhatsApp.")
            canon = f"{DOMAIN}/{cur}/servicos/"
            kicker = f"Serviços de ar-condicionado em {name}"
        else:
            title = "Serviços de Ar-Condicionado: Instalação, Manutenção e Higienização | Zayin"
            desc = ("Instalação de ar-condicionado com 6 meses de garantia, manutenção preventiva, higienização e "
                    "infraestrutura para obra no Vale do Paraíba, Mogi das Cruzes e Litoral Norte.")
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
        # home sem cidade fala do país; a página de serviços segue regional
        h1_city = "em todo o Brasil" if is_home else "no Vale do Paraíba"
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

    route = "\n      ".join(
        (f'<span class="stop" aria-current="page"><span class="dot"></span><b>{esc(c["name"])}</b><small>Você está aqui</small></span>'
         if c["slug"] == cur else
         f'<a class="stop" href="{root}{c["slug"]}/{same_kind}"><span class="dot"></span><b>{esc(c["name"])}</b><small>Ver página</small></a>')
        for c in CITIES
    )

    if is_home:
        nav = [("#aparelhos", "Aparelhos"), ("#marcas", "Marcas"), (svc_href, "Serviços"),
               ("#garantia", "Garantia"), ("#cidades", "Cidades"), ("#duvidas", "Dúvidas")]
        drawer = [("#aparelhos", "Aparelhos"), ("#marcas", "Marcas"), ("#instalacao", "Instalação"),
                  (svc_href, "Todos os serviços"), ("#garantia", "Garantia"), ("#cidades", "Cidades"), ("#duvidas", "Dúvidas")]
        mbar_alt = '<a class="btn btn-ghost" href="#aparelhos">Aparelhos</a>'
    else:
        nav = [(f"{home_href}#aparelhos", "Aparelhos"), ("#instalacao", "Instalação"), ("#outros-servicos", "Serviços"),
               ("#orcamento", "Orçamento"), ("#garantia", "Garantia"), ("#duvidas", "Dúvidas")]
        drawer = [(home_href, "Início"), (f"{home_href}#aparelhos", "Aparelhos"), ("#instalacao", "Instalação"),
                  ("#outros-servicos", "Outros serviços"), ("#orcamento", "Montar pedido"), ("#garantia", "Garantia"),
                  ("#cidades", "Cidades"), ("#duvidas", "Dúvidas")]
        mbar_alt = '<a class="btn btn-ghost" href="#orcamento">Montar pedido</a>'
    nav_html = "\n      ".join(f'<a href="{h}">{esc(t)}</a>' for h, t in nav)
    drawer_html = "\n  ".join(f'<a class="dl" href="{h}">{esc(t)}</a>' for h, t in drawer)

    # sem cidade na página, o montador não presume nenhuma: a pessoa escolhe
    opts = [] if cur else ['<option value="" selected>Selecione sua cidade</option>']
    opts += [f'<option value="{c}"{" selected" if c == cur else ""}>{esc(next(x["name"] for x in CITIES if x["slug"] == c))}</option>'
             for c in BUILDER_ORDER]
    opts += ['<option value="litoral">Litoral Norte</option>', '<option value="outra">Outra cidade</option>']
    city_options = "\n              ".join(opts)

    sjc_card = {
        "phone": SJC_PHONE,
        "cities": "São José dos Campos, Caçapava, Taubaté, Pindamonhangaba, Mogi das Cruzes e Litoral Norte",
        "current": is_city and cur != "jacarei",
        "msg": f"Olá, vim do seu site e quero fazer um orçamento.{msg_city if cur != 'jacarei' else ''}",
    }
    jac_card = {
        "phone": JAC_PHONE,
        "cities": "Jacareí",
        "current": cur == "jacarei",
        "msg": "Olá, vim do seu site e quero fazer um orçamento. Estou em Jacareí.",
    }
    cards = [jac_card, sjc_card] if cur == "jacarei" else [sjc_card, jac_card]
    contacts = "\n      ".join(
        f'''<div class="contact{" is-current" if k["current"] else ""}" data-reveal style="--d:{i * .1:.1f}s">
        <div><small>WhatsApp</small><b>{k["phone"][1]}</b><p>{esc(k["cities"])}</p></div>
        <a class="btn btn-wa btn-sm" data-wa="{esc(k["msg"])}" data-wa-phone="{k["phone"][0]}" href="#"><svg aria-hidden="true"><use href="#i-wa"/></svg>Chamar</a>
      </div>''' for i, k in enumerate(cards)
    )

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

    business = {
        "@type": "HVACBusiness",
        "name": "Zayin Ar Condicionado",
        "url": canon,
        "telephone": "+55 " + phone_label.replace("(", "").replace(")", ""),
        "description": desc,
        "slogan": "Autorizado a venda, instalação com garantia.",
        "areaServed": [c["name"] for c in CITIES] + ["Litoral Norte"],
        "brand": [{"@type": "Brand", "name": b["name"]} for b in brands],
        "sameAs": ["https://www.instagram.com/zayinarcondicionado/"],
    }
    graph = [business]
    if is_home:
        graph.append({
            "@type": "FAQPage",
            "mainEntity": [
                {"@type": "Question", "name": q,
                 "acceptedAnswer": {"@type": "Answer", "text": " ".join(ps)}}
                for q, ps in faqs
            ],
        })
    else:
        business["hasOfferCatalog"] = {
            "@type": "OfferCatalog",
            "name": "Serviços de ar-condicionado",
            "itemListElement": [{"@type": "Offer", "itemOffered": {"@type": "Service", "name": s}} for s in SERVICES],
        }
        home_abs = f"{DOMAIN}/{cur}/" if is_city else f"{DOMAIN}/"
        graph.append({
            "@type": "BreadcrumbList",
            "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": "Início", "item": home_abs},
                {"@type": "ListItem", "position": 2, "name": "Serviços", "item": canon},
            ],
        })
    jsonld = {"@context": "https://schema.org", "@graph": graph}

    page_cfg = {
        "kind": kind,
        "city": ({"slug": cur, "name": name, "phone": phone, "phoneLabel": phone_label} if is_city else None),
        "cities": [{"slug": c["slug"], "name": c["name"], "phone": c["phone"][0], "phoneLabel": c["phone"][1]} for c in CITIES],
        "brands": [{"slug": b["slug"], "name": b["name"], "ratio": b["ratio"]} for b in brands],
        "imgBase": f"{root}{PRODUCT_IMG_DIR}/",
        "defaultPhone": SJC_PHONE[0],
        "defaultPhoneLabel": SJC_PHONE[1],
    }

    main = include_parts((SRC / f"{'home' if is_home else 'servicos'}.html").read_text(encoding="utf-8"))
    tpl = (SRC / "layout.html").read_text(encoding="utf-8").replace("{{MAIN}}", main)
    repl = {
        "{{TITLE}}": esc(title),
        "{{DESC}}": esc(desc),
        "{{CANON}}": canon,
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
        "{{MBAR_ALT}}": mbar_alt,
        "{{PHONE_LABEL}}": phone_label,
        "{{CITY_MENU}}": city_menu,
        "{{ROUTE}}": route,
        "{{CITY_OPTIONS}}": city_options,
        "{{CONTACTS}}": contacts,
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
    for f in sorted(src.glob("hero*.*")):
        shutil.copyfile(f, dst / f.name)


def copy_product_images():
    src = ROOT / "assets" / "products"
    dst = DIST / PRODUCT_IMG_DIR
    dst.mkdir(parents=True, exist_ok=True)
    for f in sorted(src.glob("*.webp")):
        shutil.copyfile(f, dst / f.name)
    return len(list(src.glob("*.webp")))


def main():
    css = (SRC / "styles.css").read_text(encoding="utf-8")
    js = (SRC / "app.js").read_text(encoding="utf-8")
    logo = data_uri(ROOT / "assets" / "logo-color.webp")
    logo_w = data_uri(ROOT / "assets" / "logo-white.webp")
    brands = load_brands()
    print("ok", copy_product_images(), "fotos de aparelhos ->", DIST / PRODUCT_IMG_DIR)
    copy_video()
    for city in [None] + CITIES:
        base = DIST / city["slug"] if city else DIST
        write(base / "index.html", build_page(city, "home", css, js, logo, logo_w, brands))
        write(base / "servicos" / "index.html", build_page(city, "servicos", css, js, logo, logo_w, brands))
    # cópia da home na raiz do repositório, só para abrir no navegador (aponta para dist/)
    write(ROOT / "index.html", build_page(None, "home", css, js, logo, logo_w, brands, root_prefix="dist/"))


if __name__ == "__main__":
    main()
