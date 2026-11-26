#!/usr/bin/env python3
"""Comprueba el catálogo y la web generada. Sale con código 1 si hay ERRORES.

Uso:
  python3 validar.py               -> valida catalogo/productos.json
  python3 validar.py --web CARPETA -> además valida la web generada en CARPETA
"""
import hashlib, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SLUG_RE = re.compile(r'^[a-z0-9]+(?:-[a-z0-9]+)*-?[0-9]*$')
PLACEHOLDER_RE = re.compile(r'\[[A-ZÁÉÍÓÚ /]{3,}\]|\bTODO\b|\bXXX\b|lorem ipsum|\?\?\?|\bPENDIENTE\b')
ESTADOS = {'disponible', 'agotado', 'reservado', 'vendido', 'baja'}


def validar_catalogo():
    errores, avisos = [], []
    data = json.load(open(os.path.join(HERE, 'catalogo', 'productos.json'), encoding='utf-8'))
    cats = {c['id'] for c in data['categorias']}
    vistos, hashes = set(), {}
    for i, p in enumerate(data['productos']):
        ref = p.get('slug') or f'producto #{i + 1}'
        for campo in ('slug', 'nombre', 'precio', 'categoria', 'descripcion', 'imagenes', 'estado'):
            if campo == 'precio' and campo in p and p[campo] is None:
                continue  # «Consultar precio»
            if campo not in p or p[campo] in ('', None, []):
                errores.append(f'{ref}: falta «{campo}»')
        if errores and errores[-1].startswith(ref + ': falta'):
            continue
        if not SLUG_RE.match(p['slug']):
            errores.append(f'{ref}: slug no válido (solo minúsculas, números y guiones)')
        if p['slug'] in vistos:
            errores.append(f'{ref}: slug repetido')
        vistos.add(p['slug'])
        if p['precio'] is None:
            avisos.append(f'{ref}: sin precio (se mostrará «Consultar precio»)')
        elif not isinstance(p['precio'], (int, float)) or p['precio'] <= 0:
            errores.append(f'{ref}: precio no válido ({p["precio"]!r})')
        elif p['precio'] > 50000:
            avisos.append(f'{ref}: precio muy alto ({p["precio"]} €), revísalo')
        if p['categoria'] not in cats:
            errores.append(f'{ref}: categoría «{p["categoria"]}» no existe ({", ".join(sorted(cats))})')
        if p['estado'] not in ESTADOS:
            errores.append(f'{ref}: estado «{p["estado"]}» no válido ({", ".join(sorted(ESTADOS))})')
        for campo in ('nombre', 'subtitulo', 'descripcion'):
            if PLACEHOLDER_RE.search(str(p.get(campo, ''))):
                errores.append(f'{ref}: «{campo}» contiene un marcador sin rellenar')
        if len(p['nombre']) > 90:
            avisos.append(f'{ref}: nombre muy largo ({len(p["nombre"])} caracteres)')
        if len(p['descripcion']) < 40:
            avisos.append(f'{ref}: descripción muy corta')
        for u in p['imagenes']:
            if u.startswith('http'):
                if p.get('origen') != 'hostinger':
                    errores.append(f'{ref}: imagen remota en un producto nuevo ({u})')
                continue
            f = os.path.join(ROOT, u)
            if not os.path.isfile(f):
                errores.append(f'{ref}: no existe la imagen {u}')
                continue
            h = hashlib.sha1(open(f, 'rb').read()).hexdigest()
            if h in hashes and hashes[h] != p['slug']:
                errores.append(f'{ref}: la imagen {u} es idéntica a una de «{hashes[h]}»')
            hashes[h] = p['slug']
            if not os.path.isfile(re.sub(r'\.webp$', '-600.webp', f)):
                avisos.append(f'{ref}: falta la miniatura de {u}')
    # productos casi idénticos (mismo nombre y precio)
    clave = {}
    for p in data['productos']:
        if p.get('estado') == 'baja':
            continue
        k = (p.get('nombre', '').lower().strip(), p.get('precio'))
        if k in clave:
            avisos.append(f'{p.get("slug")}: mismo nombre y precio que «{clave[k]}» (¿duplicado?)')
        clave[k] = p.get('slug')
    return data, errores, avisos


def validar_web(out, data):
    errores = []
    activos = [p for p in data['productos'] if p.get('estado') != 'baja']
    for p in activos:
        f = os.path.join(out, p['slug'], 'index.html')
        if not os.path.isfile(f):
            errores.append(f'web: falta la ficha de {p["slug"]}')
            continue
        s = open(f, encoding='utf-8').read()
        if 'tel:+34607749877' not in s:
            errores.append(f'web: la ficha de {p["slug"]} no tiene botón de llamada')
        if (f'{p["precio"]:.2f}' if p['precio'] is not None else 'Consultar precio') not in s:
            errores.append(f'web: la ficha de {p["slug"]} no muestra el precio')
        og = re.search(r'<meta[^>]*property="og:url"[^>]*content="([^"]+)"', s) or re.search(r'<meta[^>]*content="([^"]+)"[^>]*property="og:url"', s)
        if not og or not og.group(1).endswith('/' + p['slug']):
            errores.append(f'web: la ficha de {p["slug"]} tiene og:url incorrecto')
        for otro in activos:
            if otro is not p and f'{otro["nombre"]} | Motos Julio' in s and otro['nombre'] != p['nombre']:
                errores.append(f'web: la ficha de {p["slug"]} contiene metadatos de «{otro["slug"]}»')
    tienda = open(os.path.join(out, 'tienda', 'index.html'), encoding='utf-8').read()
    n = len(re.findall(r'class="mj-card[ "]', tienda))
    if n != len(activos):
        errores.append(f'web: la tienda muestra {n} productos y el catálogo tiene {len(activos)}')
    # enlaces e imágenes locales rotos en todas las páginas
    for lp in ('aviso-legal', 'politica-de-privacidad'):
        t = open(os.path.join(out, lp, 'index.html'), encoding='utf-8').read()
        for m in sorted(set(re.findall(r'\[(?:NIF|NOMBRE)[^\]]*\]', t))):
            print(f'AVISO   web: {lp} tiene sin rellenar {m} (obligatorio antes de publicar en motosjulio.es)')
    for dirpath, _, files in os.walk(out):
        for fn in files:
            if not fn.endswith('.html'):
                continue
            page = os.path.join(dirpath, fn)
            s = open(page, encoding='utf-8').read()
            if 'zyrosite.com' in s or 'hostinger.com' in s:
                errores.append(f'web: {os.path.relpath(page, out)} aún depende de Hostinger (zyrosite/hostinger)')
            for attr, url in re.findall(r'(href|src|data-full|data-src)="([^"#?]+)', s):
                if url.startswith(('http', 'mailto:', 'tel:', 'data:', '//')) or url.endswith('.php'):
                    continue
                target = os.path.normpath(os.path.join(dirpath, url))
                if url.endswith('/'):
                    target = os.path.join(target, 'index.html')
                if not os.path.exists(target) and not os.path.exists(target.replace(out, ROOT, 1)):
                    errores.append(f'web: {os.path.relpath(page, out)} enlaza a {url}, que no existe')
    return sorted(set(errores))


if __name__ == '__main__':
    data, errores, avisos = validar_catalogo()
    if '--web' in sys.argv:
        errores += validar_web(sys.argv[sys.argv.index('--web') + 1], data)
    for a in avisos:
        print('AVISO  ', a)
    for e in errores:
        print('ERROR  ', e)
    activos = sum(1 for p in data['productos'] if p.get('estado') != 'baja')
    print(f'\n{activos} productos activos · {len(errores)} errores · {len(avisos)} avisos')
    sys.exit(1 if errores else 0)
