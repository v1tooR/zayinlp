#!/usr/bin/env python3
"""Gera a landing da Zayin: index + uma página por cidade.

Uso: python3 build.py  ->  dist/index.html, dist/<cidade>/index.html
Edite CITIES / FAQ abaixo e rode de novo.
"""
import base64
import html
import json
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


def faq_items(city):
    onde = f"em {city['name']}" if city else "na sua cidade"
    return [
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


def data_uri(path):
    return "data:image/webp;base64," + base64.b64encode(path.read_bytes()).decode()


def esc(s):
    return html.escape(s, quote=True)


def build_page(city, css, js, logo, logo_w):
    is_city = city is not None
    base = "../" if is_city else "./"
    name = city["name"] if is_city else None
    phone, phone_label = city["phone"] if is_city else SJC_PHONE

    if is_city:
        title = f"Instalação de Ar-Condicionado em {name} com Garantia | Zayin"
        desc = (f"Instalação de ar-condicionado em {name} com 6 meses de garantia no serviço. "
                "Revenda autorizada de hi-wall, piso teto e cassete. Orçamento pelo WhatsApp.")
        canon = f"{DOMAIN}/{city['slug']}/"
        kicker = f"Ar-condicionado em {name} e região"
        h1_city = f"em {name}"
        msg_city = f" Estou em {name}."
        city_btn = name
        city_btn_short = city.get("short", name)
        final_p = f"Chame a Zayin em {name} e receba seu orçamento pelo WhatsApp."
    else:
        title = "Zayin Ar Condicionado | Instalação com garantia no Vale do Paraíba"
        desc = ("Venda e instalação de ar-condicionado com garantia em São José dos Campos, Jacareí, Taubaté, "
                "Pindamonhangaba, Caçapava, Mogi das Cruzes e Litoral Norte. Orçamento pelo WhatsApp.")
        canon = f"{DOMAIN}/"
        kicker = "Ar-condicionado no Vale do Paraíba, Mogi e litoral"
        h1_city = "no Vale do Paraíba"
        msg_city = ""
        city_btn = "Sua cidade"
        city_btn_short = "Cidade"
        final_p = "Chame a Zayin e receba seu orçamento pelo WhatsApp."

    cur = city["slug"] if is_city else None

    cur_attr = ' aria-current="page"'
    city_menu = "\n          ".join(
        f'<a href="{base}{c["slug"]}/"{cur_attr if c["slug"] == cur else ""}>{esc(c["name"])}</a>'
        for c in sorted(CITIES, key=lambda c: BUILDER_ORDER.index(c["slug"]))
    )

    route = "\n      ".join(
        (f'<span class="stop" aria-current="page"><span class="dot"></span><b>{esc(c["name"])}</b><small>Você está aqui</small></span>'
         if c["slug"] == cur else
         f'<a class="stop" href="{base}{c["slug"]}/"><span class="dot"></span><b>{esc(c["name"])}</b><small>Ver página</small></a>')
        for c in CITIES
    )

    sel = cur or "saojosedoscampos"
    opts = [f'<option value="{c}"{" selected" if c == sel else ""}>{esc(next(x["name"] for x in CITIES if x["slug"] == c))}</option>'
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
        f'<li><a href="{base}{c["slug"]}/">Ar-condicionado em {esc(c["name"])}</a></li>'
        for c in sorted(CITIES, key=lambda c: BUILDER_ORDER.index(c["slug"]))
    )

    faqs = faq_items(city)
    faq_html = "\n      ".join(
        f'<details><summary>{esc(q)}<span class="pm"><svg aria-hidden="true"><use href="#i-plus"/></svg></span></summary>'
        f'<div class="ans">{"".join(f"<p>{esc(p)}</p>" for p in ps)}</div></details>'
        for q, ps in faqs
    )

    jsonld = {
        "@context": "https://schema.org",
        "@graph": [
            {
                "@type": "HVACBusiness",
                "name": "Zayin Ar Condicionado",
                "url": canon,
                "telephone": "+55 " + phone_label.replace("(", "").replace(")", ""),
                "description": desc,
                "slogan": "Autorizado a venda, instalação com garantia.",
                "areaServed": [c["name"] for c in CITIES] + ["Litoral Norte"],
                "sameAs": ["https://www.instagram.com/zayinarcondicionado/"],
            },
            {
                "@type": "FAQPage",
                "mainEntity": [
                    {"@type": "Question", "name": q,
                     "acceptedAnswer": {"@type": "Answer", "text": " ".join(ps)}}
                    for q, ps in faqs
                ],
            },
        ],
    }

    page_cfg = {
        "city": ({"slug": cur, "name": name, "phone": phone, "phoneLabel": phone_label} if is_city else None),
        "cities": [{"slug": c["slug"], "name": c["name"], "phone": c["phone"][0], "phoneLabel": c["phone"][1]} for c in CITIES],
        "defaultPhone": SJC_PHONE[0],
        "defaultPhoneLabel": SJC_PHONE[1],
    }

    tpl = (SRC / "page.html").read_text(encoding="utf-8")
    repl = {
        "{{TITLE}}": esc(title),
        "{{DESC}}": esc(desc),
        "{{CANON}}": canon,
        "{{KICKER}}": esc(kicker),
        "{{H1_CITY}}": esc(h1_city),
        "{{MSG_CITY}}": esc(msg_city),
        "{{CITY_BTN}}": esc(city_btn),
        "{{CITY_BTN_SHORT}}": esc(city_btn_short),
        "{{FINAL_P}}": esc(final_p),
        "{{BASE}}": base,
        "{{HOME_HREF}}": "",
        "{{PHONE_LABEL}}": phone_label,
        "{{CITY_MENU}}": city_menu,
        "{{ROUTE}}": route,
        "{{CITY_OPTIONS}}": city_options,
        "{{CONTACTS}}": contacts,
        "{{FOOTER_CITIES}}": footer_cities,
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


def main():
    css = (SRC / "styles.css").read_text(encoding="utf-8")
    js = (SRC / "app.js").read_text(encoding="utf-8")
    logo = data_uri(ROOT / "assets" / "logo-color.webp")
    logo_w = data_uri(ROOT / "assets" / "logo-white.webp")
    DIST.mkdir(exist_ok=True)
    out = DIST / "index.html"
    out.write_text(build_page(None, css, js, logo, logo_w), encoding="utf-8")
    print("ok", out, out.stat().st_size // 1024, "KB")
    for c in CITIES:
        d = DIST / c["slug"]
        d.mkdir(exist_ok=True)
        f = d / "index.html"
        f.write_text(build_page(c, css, js, logo, logo_w), encoding="utf-8")
        print("ok", f, f.stat().st_size // 1024, "KB")


if __name__ == "__main__":
    main()
