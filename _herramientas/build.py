#!/usr/bin/env python3
"""Genera la réplica estática de motosjulio.es a partir del HTML descargado.

Uso: python3 build.py OUT_DIR   (mejor: python3 publicar.py)
- Quita el JavaScript de Hostinger (Astro/Vue, analítica).
- Descarga a local las imágenes de assets.zyrosite.com y el CSS.
- Reconstruye los listados de la tienda (en el original se cargan por JS).
- Convierte enlaces absolutos en relativos (funciona en GitHub Pages y Hostinger).
"""
import hashlib, html, json, os, re, subprocess, sys
from urllib.parse import unquote

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, 'src')
OUT = sys.argv[1]
IMG_DIR = os.path.join(OUT, 'assets', 'img')
os.makedirs(IMG_DIR, exist_ok=True)
os.makedirs(os.path.join(OUT, 'assets', 'css'), exist_ok=True)
os.makedirs(os.path.join(OUT, 'assets', 'js'), exist_ok=True)

PAGES = {  # fichero fuente -> slug de salida ('' = portada)
    'index.html': '', 'tienda.html': 'tienda', 'motos-y-quads-segunda-mano.html': 'motos-y-quads-segunda-mano',
    'desguace-de-motos.html': 'desguace-de-motos', 'bicicletas.html': 'bicicletas', 'patines.html': 'patines',
    'contacto.html': 'contacto',
}
PLANTILLA_PRODUCTO = 'prod/adly-300.html'  # cabecera, pie y estilos de ficha

import legal

# ---------- imágenes ----------
local_cache = {}
CDN_PRODUCT = 'cdn.zyrosite.com/cdn-ecommerce/'


def fetch(url, dest):
    if os.path.exists(dest) and os.path.getsize(dest) > 0:
        return True
    r = subprocess.run(['curl', '-sSfL', '-m', '60', '-o', dest, url], capture_output=True)
    return r.returncode == 0 and os.path.exists(dest) and os.path.getsize(dest) > 0


def local_image(url):
    """Devuelve ruta local (relativa a la raíz) para una imagen de Hostinger, o la URL original si no se puede bajar."""
    url = html.unescape(url)
    if url in local_cache:
        return local_cache[url]
    res = url
    if 'assets.zyrosite.com' in url or CDN_PRODUCT in url:
        base = unquote(url.split('?')[0]).rstrip('/').split('/')[-1]
        stem, ext = os.path.splitext(base)
        m = re.search(r'cdn-cgi/image/([^/]+)/', url)
        params = m.group(1) if m else ''
        w = re.search(r'w=(\d+)', params); h = re.search(r'h=(\d+)', params)
        suffix = (f'-{w.group(1)}' if w else '') + (f'x{h.group(1)}' if h else '')
        if 'f=png' in params:
            ext = '.png'
        stem = re.sub(r'[^a-zA-Z0-9_-]+', '-', stem)
        name = f'{stem}{suffix}'
        existing = [f for f in os.listdir(IMG_DIR) if os.path.splitext(f)[0] == name]
        if existing:
            res = '/assets/img/' + existing[0]
        else:
            tmp = os.path.join(IMG_DIR, name + '.tmp')
            r = subprocess.run(['curl', '-sSfL', '-m', '60', '-H', 'Accept: image/webp,image/*;q=0.8', '-o', tmp, url], capture_output=True)
            if r.returncode == 0 and os.path.exists(tmp) and os.path.getsize(tmp) > 0:
                head = open(tmp, 'rb').read(16)
                kind = '.webp' if head[8:12] == b'WEBP' else '.png' if head[:4] == b'\x89PNG' else '.jpg' if head[:2] == b'\xff\xd8' else (ext or '.jpg')
                os.rename(tmp, os.path.join(IMG_DIR, name + kind))
                res = '/assets/img/' + name + kind
    local_cache[url] = res
    return res


def rel(path, depth):
    """'/x' -> ruta relativa según profundidad de la página."""
    prefix = '../' * depth if depth else './'
    p = path.lstrip('/')
    return prefix + p if p else prefix


# ---------- productos (fuente: catalogo/productos.json) ----------
ROOT = os.path.dirname(HERE)
CATALOGO = json.load(open(os.path.join(HERE, 'catalogo', 'productos.json'), encoding='utf-8'))
CATEGORIES = [(c['id'], c['nombre']) for c in CATALOGO['categorias'] if not c.get('oculta')]
CAT_NAMES = {c['id']: c['nombre'] for c in CATALOGO['categorias']}
products = [p for p in CATALOGO['productos'] if p.get('estado') != 'baja']
# los fijados (p. ej. campañas) van siempre primero, en su orden; luego el resto
products = [p for p in products if p.get('fijado')] + [p for p in products if not p.get('fijado')]
for i, p in enumerate(products):
    p['order'] = i
TEL = '+34607749877'

LISTS = {  # página -> categoría que muestra por defecto ('' = todas)
    'tienda': '',
    'motos-y-quads-segunda-mano': 'motos,quads',
    'bicicletas': 'bicicletas',
    'patines': 'patines',
    'desguace-de-motos': 'desguace',
}
CAT_PAGE = {'bicicletas': 'bicicletas', 'patines': 'patines', 'desguace': 'desguace-de-motos'}


def fmt_price(v):
    return 'Consultar precio' if v is None else '€' + f'{v:.2f}'


def img_url(path, depth, thumb=False):
    """Ruta pública de una imagen del catálogo (URL remota o ruta del repo)."""
    if path.startswith('http'):
        return path
    if thumb:
        t = re.sub(r'\.webp$', '-600.webp', path)
        if os.path.exists(os.path.join(ROOT, t)):
            path = t
    return rel('/' + path, depth)


def badge_for(p):
    return {'agotado': 'Agotado', 'vendido': 'Vendido', 'reservado': 'Reservado'}.get(p.get('estado', ''), '') or p.get('etiqueta', '')


def product_grid(default, depth):
    wanted = set(default.split(',')) if default else None
    options = [('', 'Todos los productos')]
    for key, label in CATEGORIES:
        options.append((key, label))
        if key == 'motos' and default == 'motos,quads':
            options.append(('motos,quads', 'Motos y quads'))
    opts = ''.join(f'<option value="{k}"{" selected" if k == default else ""}>{l}</option>' for k, l in options)
    sorts = ''.join(f'<option value="{k}">{l}</option>' for k, l in [
        ('reciente', 'Más reciente'), ('precio-asc', 'Precio: de menor a mayor'),
        ('precio-desc', 'Precio: de mayor a menor'), ('nombre', 'Nombre: de la A a la Z')])
    cards, visible = [], 0
    for p in products:
        show = wanted is None or p['categoria'] in wanted
        visible += show
        b = badge_for(p)
        badge = f'<span class="mj-badge{" mj-badge--promo" if b and b == p.get("etiqueta") else ""}">{html.escape(b)}</span>' if b else ''
        cards.append(
            f'<a class="mj-card{" mj-card--fijado" if p.get("fijado") else ""}" href="{rel("/" + p["slug"] + "/", depth)}" data-cat="{p["categoria"]}" data-price="{"" if p["precio"] is None else p["precio"]}" '
            f'data-order="{p["order"]}" data-pinned="{1 if p.get("fijado") else 0}" data-name="{html.escape(p["nombre"].lower())}"{"" if show else " hidden"}>'
            f'<span class="mj-card__img">{badge}<img src="{img_url(p["imagenes"][0], depth, True)}" alt="{html.escape(p["nombre"])}" loading="lazy"></span>'
            f'<h6 class="mj-card__title">{html.escape(p["nombre"])}</h6>'
            f'<p class="mj-card__price">{fmt_price(p["precio"])}</p></a>')
    return (f'<div class="mj-shop" data-default="{default}">'
            f'<div class="mj-toolbar">'
            f'<label class="mj-field"><span class="mj-field__label">Navegar por:</span><span class="mj-select"><select data-mj-cat aria-label="Categoría">{opts}</select></span></label>'
            f'<label class="mj-field mj-field--sort"><span class="mj-field__label">Ordenar por:</span><span class="mj-select"><select data-mj-sort aria-label="Ordenar">{sorts}</select></span></label>'
            f'</div>'
            f'<p class="mj-count" data-mj-count>{visible} {"producto" if visible == 1 else "productos"}</p>'
            f'<div class="mj-grid">{"".join(cards)}</div>'
            f'<div class="mj-empty"{"" if visible == 0 else " hidden"}><svg width="48" height="48" viewBox="0 0 48 48" fill="none"><rect width="48" height="48" rx="8" fill="currentColor" fill-opacity="0.08"/></svg>'
            f'<h6>No hay productos disponibles</h6><p>Llámanos al <a href="tel:{TEL}">607 749 877</a> y te informamos.</p></div>'
            f'</div>')


def description_html(text):
    out = []
    for line in text.split('\n'):
        line = line.strip()
        out.append(f'<p>{html.escape(line)}</p>' if line else '<p></p>')
    return ''.join(out)


def gallery_html(p, depth):
    imgs = p['imagenes']
    alt = html.escape(p['nombre'])
    main = img_url(imgs[0], depth)
    arrows = ('<button class="product-carousel__slider-button product-carousel__slider-button--left" aria-label="Foto anterior"><span class="product-carousel__arrow product-carousel__arrow--left"></span></button>'
              '<button class="product-carousel__slider-button product-carousel__slider-button--right" aria-label="Foto siguiente"><span class="product-carousel__arrow product-carousel__arrow--right"></span></button>') if len(imgs) > 1 else ''
    thumbs = ''.join(
        f'<button class="{"product-carousel__image-list-element--active " if i == 0 else ""}product-carousel__image-list-element" aria-label="Foto {i + 1}">'
        f'<img class="product-carousel__image ecommerce-product-image" style="object-fit:cover;" loading="lazy" src="{img_url(u, depth, True)}" data-full="{img_url(u, depth)}" alt="{alt} - foto {i + 1}" width="64" height="64"></button>'
        for i, u in enumerate(imgs))
    dots = ''.join(f'<button class="product-carousel__dot-button" aria-label="Foto {i + 1}"><span class="{"product-carousel__dot--active " if i == 0 else ""}product-carousel__dot"></span></button>' for i in range(len(imgs)))
    lists = (f'<div class="product-carousel__image-list"><div class="">{thumbs}</div></div>'
             f'<div class="product-carousel__dots-wrapper">{dots}</div>') if len(imgs) > 1 else ''
    return ('<div class="product-content-layout__gallery"><div class="product-carousel" style="--image-max-width:600px;--image-max-width-small:64px;--image-object-fit:cover;--image-border-radius:0%;--arrow-color:rgb(0, 0, 0);--thumbnail-arrow-color:rgb(0, 0, 0);">'
            f'<div class="product-carousel__image-wrapper product-carousel__image-wrapper--portrait">{arrows}'
            f'<img class="product-carousel__image product-carousel__main-image ecommerce-product-image" style="object-fit:cover;" loading="eager" src="{main}" alt="{alt}" width="600" height="800"></div>'
            f'{lists}</div></div>')


def balanced_end(s, start, tag):
    """Índice justo después del cierre de la etiqueta que empieza en start."""
    depth, i = 0, start
    pat = re.compile(r'<(/?)' + tag + r'\b[^>]*?(/?)>')
    for m in pat.finditer(s, start):
        if m.group(1):
            depth -= 1
        elif not m.group(2):
            depth += 1
        if depth == 0:
            return m.end()
    raise ValueError('sin cierre')


def remove_element(s, elem_id):
    """Quita el layout-element de Hostinger que contiene el componente con ese id."""
    i = s.find(f'id="{elem_id}"')
    if i < 0:
        return s
    start = s.rfind('<div class="layout-element', 0, i)
    return s[:start] + s[balanced_end(s, start, 'div'):]


def remove_section(s, sec_id):
    i = s.find(f'<section id="{sec_id}"')
    if i < 0:
        return s
    return s[:i] + s[balanced_end(s, i, 'section'):]


def legal_footer(depth):
    r = rel('/', depth)
    return ('<footer class="mj-legal-bar"><div class="mj-legal-bar__inner">'
            '<p>© 2026 Motos Julio · Miguelturra (Ciudad Real)</p>'
            f'<nav aria-label="Información legal"><a href="{r}aviso-legal/">Aviso legal</a>'
            f'<a href="{r}politica-de-privacidad/">Política de privacidad</a>'
            f'<a href="{r}politica-de-cookies/">Política de cookies</a></nav></div></footer>')


# ---------- procesado de páginas ----------
def process(src, slug):
    s = open(os.path.join(SRC, src), encoding='utf-8').read()
    props_txt = html.unescape(s)
    depth = 1 if slug else 0
    # 1) scripts: fuera todo salvo JSON-LD
    s = re.sub(r'<script(?![^>]*application/ld\+json)[^>]*>.*?</script>', '', s, flags=re.S)
    # 2) islas de Astro -> desenvolver
    s = re.sub(r'<astro-island[^>]*>', '', s)
    s = s.replace('</astro-island>', '')
    s = re.sub(r'<template data-astro-template[^>]*>.*?</template>', '', s, flags=re.S)
    # 3) head: limpiar
    s = re.sub(r'<meta name="generator"[^>]*>', '', s)
    s = re.sub(r'<link[^>]*(traffic\.txt|cdn\.zyrosite\.com/u1/google-fonts|rel="preconnect")[^>]*>', '', s)
    s = re.sub(r'<link rel="stylesheet" href="/_astro[^"]*">',
               f'<link rel="stylesheet" href="{rel("/assets/css/fonts.css", depth)}"><link rel="stylesheet" href="{rel("/assets/css/site.css", depth)}"><link rel="stylesheet" href="{rel("/assets/css/extra.css", depth)}">', s)
    # 4) animaciones que dependen de JS -> visibles
    s = s.replace('transition--root-hidden', '')
    # 5) <template> de imágenes de producto -> imágenes reales
    s = re.sub(r'<template>(<img[^>]*>)</template>', r'\1', s)
    s = s.replace(' ecommerce-product-image--loading', '')
    # 6) imágenes de Hostinger -> locales
    def img_attr(m):
        attr, val = m.group(1), m.group(2)
        if attr == 'srcset':
            parts = []
            for part in re.split(r',\s*(?=https?://)', val):
                bits = part.strip().split(' ')
                u = local_image(bits[0])
                if u.startswith('/'):
                    u = rel(u, depth)
                parts.append(' '.join([u] + bits[1:]))
            return f'{attr}="{", ".join(parts)}"'
        u = local_image(val)
        if u.startswith('/'):
            u = rel(u, depth)
        return f'{attr}="{u}"'
    s = re.sub(r'(src|srcset|href)="(https://(?:assets|cdn)\.zyrosite\.com/(?:cdn-cgi|A852|cdn-ecommerce)[^"]*)"', img_attr, s)
    s = re.sub(r'url\((https://assets\.zyrosite\.com/[^)]*)\)', lambda m: f'url({rel(local_image(m.group(1)), depth)})', s)
    # 7) enlaces internos absolutos -> relativos con barra final
    def link(m):
        path = m.group(1)
        if path == '/':
            return f'href="{rel("/", depth)}"'
        return f'href="{rel(path.rstrip("/") + "/", depth)}"'
    s = re.sub(r'href="(/[a-z0-9-]*/?)"', link, s)
    # 8) listados de tienda
    if slug in LISTS:
        s = re.sub(r'(<div class="block-product-list__content-container"[^>]*>)',
                   lambda m: m.group(1) + product_grid(LISTS[slug], depth), s, count=1)
    # 9) ficha de producto: botón de llamada real, sin selector de cantidad
    if src.startswith('prod/'):
        s = re.sub(r'<div class="block-product__quantity-wrapper".*?</span><!---->\s*</div>', '', s, flags=re.S)
        s = re.sub(r'(<button class="grid-button[^"]*block-product__button--primary"[^>]*>Llama al 607749877)</button>', r'\1</a>', s)
        s = re.sub(r'<button (class="grid-button[^"]*block-product__button--primary")',
                   r'<a href="tel:+34607749877" \1', s)
    # 10) formulario de contacto
    s = re.sub(r'<form name="Contact form"([^>]*)>', r'<form name="Contact form" action="' + rel('/contacto.php', depth) + r'" method="post"\1>', s)
    for fid, fname, extra in [('Nombre', 'nombre', 'required'), ('Apellidos', 'apellidos', 'required'),
                              ('Correo electrónico', 'email', 'required'), ('Mensaje', 'mensaje', 'required')]:
        s = s.replace(f'id="{fid}" placeholder', f'id="{fid}" name="{fname}" {extra} placeholder')
    s = s.replace('id="Correo electrónico" name="email" required placeholder="Tu correo electrónico" type="text"',
                  'id="Correo electrónico" name="email" required placeholder="Tu correo electrónico" type="email"')
    s = s.replace('<button type="submit" name="submit" class="grid-button grid-button--primary form__button"',
                  '<div class="mj-consent"><label><input type="checkbox" name="privacidad" value="1" required> '
                  f'He leído y acepto la <a href="{rel("/politica-de-privacidad/", depth)}" target="_blank">política de privacidad</a>.</label>'
                  f'<p>{html.escape(legal.FORM_INFO)}<a href="{rel("/politica-de-privacidad/", depth)}" target="_blank">Más información</a>.</p></div>'
                  '<button type="submit" name="submit" class="grid-button grid-button--primary form__button"')
    s = s.replace('</form>', '<input type="text" name="web" class="mj-hp" tabindex="-1" autocomplete="off" aria-hidden="true"></form>')
    # 10b) mapas de Google: el src venía vacío y lo rellenaba el JS
    def map_src(m):
        mid = m.group(1)
        pm = re.search(r'"' + re.escape(mid) + r'":\[0,\{"type":\[0,"GridMap"\].*?"src":\[0,"([^"]+)"', props_txt, re.S)
        src_url = html.escape(pm.group(1)) if pm else ''
        consent = ('<div class="mj-map-consent"><button type="button" class="mj-map-consent__btn">Ver mapa</button>'
                   f'<p>Al cargar el mapa, Google puede usar cookies. <a href="{rel("/politica-de-cookies/", depth)}">Más info</a></p></div>')
        return (m.group(0).replace('src=""', f'data-src="{src_url}" title="Mapa de Google Maps"', 1)
                .replace('grid-map--loading', 'mj-map') + consent)
    s = re.sub(r'<div class="grid-map grid-map--loading[^"]*" id="([^"]+)".*?</iframe>', map_src, s, flags=re.S)
    # 10c) el taller de Hellín está cerrado
    if slug == 'contacto':
        for eid in ('zv_9ft', 'zVMx8q', 'zlua80', 'zsK_Jw', 'zaxdkq', 'z-Tyxf'):
            s = remove_element(s, eid)
        s = s.replace('Hellín', '').replace('Hellin', '')
    # 10d) barra legal bajo el pie
    s = s.replace('</main>', legal_footer(depth) + '</main>', 1)
    # 11) JS propio
    s = s.replace('</body>', f'<script src="{rel("/assets/js/main.js", depth)}" defer></script></body>')
    s = s.replace('<head>', "<head><script>document.documentElement.classList.add('mj-js')</script>", 1)
    return s


def write_page(slug, s):
    dest = os.path.join(OUT, slug, 'index.html') if slug else os.path.join(OUT, 'index.html')
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    open(dest, 'w', encoding='utf-8').write(s)


for src, slug in PAGES.items():
    write_page(slug, process(src, slug))


# ---------- fichas de producto (desde el catálogo) ----------
def replace_block(s, marker, new):
    i = s.find(marker)
    i = s.rfind('<div', 0, i + 1)
    return s[:i] + new + s[balanced_end(s, i, 'div'):]


TEMPLATE = process(PLANTILLA_PRODUCTO, 'plantilla')
TEMPLATE = TEMPLATE.replace('item-content-wrapper--active ', '')
SITE = 'https://www.motosjulio.es'


def set_meta(s, key, val):
    attr = 'property' if key.startswith('og:') else 'name'
    tag = f'<meta {attr}="{key}" content="{html.escape(val, quote=True)}">'
    pat = re.compile(r'<meta\b[^>]*\b(?:name|property)="' + re.escape(key) + r'"[^>]*>')
    if pat.search(s):
        return pat.sub(lambda m: tag, s, count=1)
    return s.replace('</head>', tag + '</head>', 1)


def render_product(p):
    s = TEMPLATE
    name = html.escape(p['nombre'])
    cat_id = p['categoria']
    first = re.sub(r'\s+', ' ', p['descripcion']).strip()
    desc = html.escape((first[:152] + '…') if len(first) > 155 else first)
    title = f'{name} | Motos Julio'
    s = re.sub(r'<title>[^<]*</title>', f'<title>{title}</title>', s)
    first_img = p['imagenes'][0] if p['imagenes'][0].startswith('http') else f'{SITE}/{p["imagenes"][0]}'
    url = f'{SITE}/{p["slug"]}'
    for key, val in [('description', desc), ('og:title', title), ('twitter:title', title),
                     ('og:description', desc), ('twitter:description', desc), ('og:url', url),
                     ('og:image', first_img), ('twitter:image', first_img),
                     ('og:image:alt', name), ('twitter:image:alt', name)]:
        s = set_meta(s, key, val)
    s = re.sub(r'(<link rel="canonical" href=")[^"]*', lambda m: m.group(1) + url, s)
    ld = {'@context': 'https://schema.org', '@type': 'Product', 'name': p['nombre'],
          'description': first, 'image': [u if u.startswith('http') else f'{SITE}/{u}' for u in p['imagenes']],
          'category': CAT_NAMES.get(cat_id, ''), 'url': f'{SITE}/{p["slug"]}',
          'offers': {'@type': 'Offer', 'priceCurrency': 'EUR', 'itemCondition': 'https://schema.org/UsedCondition',
                     'availability': 'https://schema.org/' + ('InStock' if p.get('estado', 'disponible') == 'disponible' else 'OutOfStock')}}
    if p['precio'] is not None:
        ld['offers']['price'] = f'{p["precio"]:.2f}'
    s = re.sub(r'<script type="application/ld\+json">.*?</script>', '', s, flags=re.S)
    s = s.replace('</head>', '<script type="application/ld+json">' + json.dumps(ld, ensure_ascii=False) + '</script></head>', 1)
    # galería
    s = replace_block(s, '<div class="product-content-layout__gallery', gallery_html(p, 1))
    # textos
    if cat_id in CAT_NAMES and cat_id != 'otros':
        back = rel('/' + CAT_PAGE[cat_id] + '/', 1) if cat_id in CAT_PAGE else rel('/tienda/', 1) + '?categoria=' + cat_id
        crumb = (f'<nav class="mj-breadcrumb" aria-label="Estás en"><a href="{rel("/tienda/", 1)}">Tienda</a><span>/</span>'
                 f'<a href="{back}">{html.escape(CAT_NAMES[cat_id])}</a></nav>')
    else:
        crumb = f'<nav class="mj-breadcrumb" aria-label="Estás en"><a href="{rel("/tienda/", 1)}">Tienda</a></nav>'
    s = re.sub(r'(<h1 class="block-product__title"[^>]*>).*?(</h1>)', lambda m: crumb + m.group(1) + name + m.group(2), s, count=1, flags=re.S)
    sub = html.escape(p.get('subtitulo', ''))
    s = re.sub(r'(<h2 class="block-product__subtitle"[^>]*>).*?(</h2>)', (lambda m: m.group(1) + sub + m.group(2)) if sub else '', s, count=1, flags=re.S)
    b = badge_for(p)
    price = fmt_price(p['precio']) + (f' <span class="mj-badge mj-badge--inline{" mj-badge--promo" if b == p.get("etiqueta") else ""}">{html.escape(b)}</span>' if b else '')
    s = re.sub(r'(<span class="block-product__price[^"]*"[^>]*>).*?(</span>)', lambda m: m.group(1) + price + m.group(2), s, count=1, flags=re.S)
    s = re.sub(r'(<div class="block-product__description[^"]*"[^>]*>).*?(</div>)', lambda m: m.group(1) + description_html(p['descripcion']) + m.group(2), s, count=1, flags=re.S)
    s = s.replace('../plantilla/', f'../{p["slug"]}/')
    return s


for p in products:
    write_page(p['slug'], render_product(p))

# ---------- páginas legales (misma cabecera y pie que Contacto) ----------
base = open(os.path.join(OUT, 'contacto', 'index.html'), encoding='utf-8').read()
for sec in ('z3UMuY', 'z-nrvp'):
    base = remove_section(base, sec)
base = base.replace('item-content-wrapper--active ', '')
base = re.sub(r'<script type="application/ld\+json">.*?</script>', '', base, flags=re.S)
for lslug, (ltitle, ldesc, lbody) in legal.PAGES.items():
    page = base
    page = re.sub(r'<title>[^<]*</title>', f'<title>{ltitle}</title>', page)
    page = re.sub(r'(<meta (?:name|property)="(?:twitter:|og:)?title" content=")[^"]*', lambda m: m.group(1) + ltitle, page)
    page = re.sub(r'(<meta (?:name|property)="(?:twitter:|og:)?description" content=")[^"]*', lambda m: m.group(1) + ldesc, page)
    page = page.replace('https://www.motosjulio.es/contacto', 'https://www.motosjulio.es/' + lslug)
    body = lbody.replace('{root}', '../')
    section = f'<section class="block mj-legal-page"><div class="mj-legal-page__inner">{body}</div></section>'
    page = page.replace('<section id="zU8U5s"', section + '<section id="zU8U5s"', 1)
    os.makedirs(os.path.join(OUT, lslug), exist_ok=True)
    open(os.path.join(OUT, lslug, 'index.html'), 'w', encoding='utf-8').write(page)

# CSS original (sin dependencias externas salvo data: URIs)
css = open(os.path.join(SRC, 'site.css'), encoding='utf-8').read()
open(os.path.join(OUT, 'assets', 'css', 'site.css'), 'w', encoding='utf-8').write(css)

remote = sorted({u for u, v in local_cache.items() if v == u})
print(f'Páginas: {len(PAGES) + len(products) + len(legal.PAGES)} | productos: {len(products)} | imágenes locales: {sum(1 for u,v in local_cache.items() if v!=u)} | remotas: {len(remote)}')
for u in remote[:50]:
    print('  remota:', u[:120])
