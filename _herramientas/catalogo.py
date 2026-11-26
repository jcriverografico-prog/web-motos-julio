#!/usr/bin/env python3
"""Gestión del catálogo de Motos Julio.

  alta FICHA.json [--simular] [--forzar]  Da de alta un producto (ver formato abajo).
  estado SLUG ESTADO                      disponible | reservado | vendido | agotado
  baja SLUG                               Lo quita de la web (se conserva en el registro).
  fijar SLUG / soltar SLUG                Fija (o suelta) un producto al principio de la tienda.
  fotos SLUG RUTA [RUTA…] [--simular]     Añade fotos a un producto existente (no cuenta como producto nuevo).
  registrar SLUG [SLUG…]                  Apunta en el contador productos ya publicados (sin crear ficha).
  contador                                Productos subidos, lotes de 30 y importe.
  cobrado N                               Marca N lotes como cobrados.
  lista                                   Lista el catálogo.

FICHA.json (una por producto):
{
  "nombre": "Quad Yamaha Raptor 700",
  "subtitulo": "Revisado y con garantía",          (opcional)
  "precio": 6500,
  "categoria": "quads",                              bicicletas | desguace | motos | patines | quads | otros
  "descripcion": "Línea 1\\nLínea 2\\n\\n• Punto",
  "imagenes": ["/ruta/foto1.jpg", "/ruta/foto2.jpg"], (la primera es la portada)
  "estado": "disponible",                            (opcional)
  "etiqueta": "Black Friday",                        (opcional: cinta sobre la foto)
  "fijado": true                                     (opcional: siempre el primero de la tienda)
  Precio desconocido a propósito: "precio": "consultar"  -> «Consultar precio»
  Horquilla de precios: "precio": {"desde": 280, "hasta": 850}  (o "280-850") -> «Desde €280.00 hasta €850.00»
}
"""
import csv, datetime, json, os, re, sys, unicodedata

from PIL import Image, ImageOps

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
CAT_FILE = os.path.join(HERE, 'catalogo', 'productos.json')
REGISTRO = os.path.join(HERE, 'catalogo', 'registro.csv')
COBROS = os.path.join(HERE, 'catalogo', 'cobros.csv')
LOTE, PRECIO_LOTE = 30, 50
MAX_LADO, MINI, CALIDAD = 1600, 600, 82


def cargar():
    return json.load(open(CAT_FILE, encoding='utf-8'))


def guardar(data):
    tmp = CAT_FILE + '.tmp'
    json.dump(data, open(tmp, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
    os.replace(tmp, CAT_FILE)


def slugify(texto):
    t = unicodedata.normalize('NFKD', texto).encode('ascii', 'ignore').decode().lower()
    t = re.sub(r'[^a-z0-9]+', '-', t).strip('-')
    return re.sub(r'-{2,}', '-', t)[:70].strip('-')


def ahash(img):
    g = ImageOps.exif_transpose(img).convert('L').resize((16, 16), Image.LANCZOS)
    px = list(g.tobytes())
    media = sum(px) / len(px)
    return sum(1 << i for i, v in enumerate(px) if v > media)


def distancia(a, b):
    return bin(a ^ b).count('1')


def hashes_existentes():
    base = os.path.join(ROOT, 'assets', 'productos')
    res = []
    if os.path.isdir(base):
        for slug in os.listdir(base):
            for f in os.listdir(os.path.join(base, slug)):
                if f.endswith('-600.webp'):
                    res.append((slug, ahash(Image.open(os.path.join(base, slug, f)))))
    return res


def leer_registro():
    if not os.path.exists(REGISTRO):
        return []
    return list(csv.DictReader(open(REGISTRO, encoding='utf-8')))


def leer_precio(v):
    if isinstance(v, (int, float)):
        return float(v)
    t = str(v).replace('€', '').replace(' ', '').strip()
    if ',' in t and '.' in t:          # 1.250,50
        t = t.replace('.', '').replace(',', '.')
    elif ',' in t:                     # 1250,50
        t = t.replace(',', '.')
    elif re.fullmatch(r'\d{1,3}(\.\d{3})+', t):  # 1.250
        t = t.replace('.', '')
    return float(t)


def leer_precio_campo(v):
    """número | "consultar" | "280-850" | {"desde": 280, "hasta": 850}"""
    if str(v).lower() == 'consultar':
        return None
    if isinstance(v, dict):
        d, h = leer_precio(v['desde']), leer_precio(v['hasta'])
    elif isinstance(v, str) and re.fullmatch(r'\s*[\d.,€ ]+\s*-\s*[\d.,€ ]+\s*', v):
        d, h = (leer_precio(x) for x in v.split('-'))
    else:
        n = leer_precio(v)
        if n <= 0:
            raise ValueError
        return round(n, 2)
    if not (0 < d < h):
        raise ValueError
    return {'desde': round(d, 2), 'hasta': round(h, 2)}


def fallo(msg):
    print('ERROR  ', msg)
    sys.exit(1)


def alta(ficha_path, simular=False, forzar=False):
    data = cargar()
    f = json.load(open(ficha_path, encoding='utf-8'))
    cats = {c['id'] for c in data['categorias']}
    errores = []
    for campo in ('nombre', 'precio', 'categoria', 'descripcion', 'imagenes'):
        if not f.get(campo) and not (campo == 'precio' and str(f.get('precio')).lower() == 'consultar'):
            errores.append(f'falta «{campo}»')
    if errores:
        fallo('; '.join(errores))
    try:
        precio = leer_precio_campo(f['precio'])
    except (ValueError, KeyError, TypeError):
        fallo(f'precio no válido: {f["precio"]!r}')
    if f['categoria'] not in cats:
        fallo(f'categoría «{f["categoria"]}» no existe ({", ".join(sorted(cats))})')
    estado = f.get('estado', 'disponible')
    if estado not in {'disponible', 'reservado', 'vendido', 'agotado'}:
        fallo(f'estado no válido: {estado}')
    for ruta in f['imagenes']:
        if not os.path.isfile(ruta):
            fallo(f'no encuentro la imagen {ruta}')

    # slug único
    base = slugify(f['nombre']) or 'producto'
    usados = {p['slug'] for p in data['productos']}
    slug, n = base, 2
    while slug in usados or os.path.exists(os.path.join(ROOT, slug)) or os.path.exists(os.path.join(HERE, 'src', slug + '.html')):
        slug, n = f'{base}-{n}', n + 1

    # fotos: tamaño mínimo y duplicados
    existentes = hashes_existentes()
    propios = []
    for ruta in f['imagenes']:
        img = Image.open(ruta)
        w, h = ImageOps.exif_transpose(img).size
        if min(w, h) < 500:
            fallo(f'{os.path.basename(ruta)} es demasiado pequeña ({w}×{h}); mínimo 500 px de lado')
        hsh = ahash(img)
        for s2, h2 in existentes:
            if distancia(hsh, h2) <= 6 and not forzar:
                fallo(f'{os.path.basename(ruta)} se parece mucho a una foto de «{s2}». '
                      '¿Producto repetido? Si no lo es, repite con --forzar.')
        for r2, h2 in propios:
            if distancia(hsh, h2) <= 2:
                print(f'AVISO   {os.path.basename(ruta)} parece la misma foto que {os.path.basename(r2)}')
        propios.append((ruta, hsh))

    rutas = [f'assets/productos/{slug}/{i + 1:02d}.webp' for i in range(len(f['imagenes']))]
    producto = {
        'slug': slug, 'nombre': f['nombre'].strip(), 'subtitulo': f.get('subtitulo', '').strip(),
        'precio': precio, 'categoria': f['categoria'], 'descripcion': f['descripcion'].strip(),
        'imagenes': rutas, 'estado': estado, 'origen': 'nuevo',
        'alta': datetime.date.today().isoformat(),
    }
    print(json.dumps(producto, ensure_ascii=False, indent=2))
    if simular:
        print('\n(simulación: no se ha guardado nada)')
        return

    carpeta = os.path.join(ROOT, 'assets', 'productos', slug)
    os.makedirs(carpeta, exist_ok=True)
    for ruta, destino in zip(f['imagenes'], rutas):
        img = ImageOps.exif_transpose(Image.open(ruta)).convert('RGB')
        grande = img.copy(); grande.thumbnail((MAX_LADO, MAX_LADO), Image.LANCZOS)
        grande.save(os.path.join(ROOT, destino), 'WEBP', quality=CALIDAD, method=6)
        mini = img.copy(); mini.thumbnail((MINI, MINI * 2), Image.LANCZOS)
        mini.save(os.path.join(ROOT, destino.replace('.webp', '-600.webp')), 'WEBP', quality=78, method=6)

    for k in ('etiqueta', 'fijado'):
        if f.get(k):
            producto[k] = f[k]
    data['productos'].insert(0, producto)  # el más reciente, primero (los fijados se ordenan solos al publicar)
    guardar(data)
    nuevo = not os.path.exists(REGISTRO)
    with open(REGISTRO, 'a', encoding='utf-8', newline='') as fh:
        w = csv.writer(fh)
        if nuevo:
            w.writerow(['fecha', 'slug', 'nombre', 'categoria', 'precio', 'fotos'])
        v = producto['precio']
        w.writerow([producto['alta'], slug, producto['nombre'], producto['categoria'], 'consultar' if v is None else (f'{v["desde"]}-{v["hasta"]}' if isinstance(v, dict) else v), len(rutas)])
    print(f'\nAlta guardada: {slug}')
    contador()


def cambiar_estado(slug, estado):
    data = cargar()
    p = next((p for p in data['productos'] if p['slug'] == slug), None)
    if not p:
        fallo(f'no existe el producto {slug}')
    if estado not in {'disponible', 'reservado', 'vendido', 'agotado', 'baja'}:
        fallo(f'estado no válido: {estado}')
    p['estado'] = estado
    guardar(data)
    print(f'{slug}: {estado}')


def fijar(slug, valor):
    data = cargar()
    p = next((p for p in data['productos'] if p['slug'] == slug), None)
    if not p:
        fallo(f'no existe el producto {slug}')
    if valor:
        p['fijado'] = True
    else:
        p.pop('fijado', None)
    guardar(data)
    print(f'{slug}: {"fijado" if valor else "sin fijar"}')


def guardar_foto(ruta, destino):
    img = ImageOps.exif_transpose(Image.open(ruta)).convert('RGB')
    os.makedirs(os.path.join(ROOT, os.path.dirname(destino)), exist_ok=True)
    g = img.copy(); g.thumbnail((MAX_LADO, MAX_LADO), Image.LANCZOS)
    g.save(os.path.join(ROOT, destino), 'WEBP', quality=CALIDAD, method=6)
    m = img.copy(); m.thumbnail((MINI, MINI * 2), Image.LANCZOS)
    m.save(os.path.join(ROOT, destino.replace('.webp', '-600.webp')), 'WEBP', quality=78, method=6)


def anadir_fotos(slug, rutas, simular=False):
    data = cargar()
    p = next((p for p in data['productos'] if p['slug'] == slug), None)
    if not p:
        fallo(f'no existe el producto {slug}')
    existentes = hashes_existentes()
    for ruta in rutas:
        if not os.path.isfile(ruta):
            fallo(f'no encuentro la imagen {ruta}')
        img = Image.open(ruta)
        w, h = ImageOps.exif_transpose(img).size
        if min(w, h) < 500:
            fallo(f'{os.path.basename(ruta)} es demasiado pequeña ({w}×{h})')
        hsh = ahash(img)
        for s2, h2 in existentes:
            if distancia(hsh, h2) <= 6:
                fallo(f'{os.path.basename(ruta)} se parece mucho a una foto de «{s2}»')
    n = len(p['imagenes'])
    nuevas = [f'assets/productos/{slug}/{n + i + 1:02d}.webp' for i in range(len(rutas))]
    print(f'{slug}: {n} fotos -> {n + len(nuevas)}')
    if simular:
        print('(simulación: no se ha guardado nada)')
        return
    for ruta, destino in zip(rutas, nuevas):
        guardar_foto(ruta, destino)
    p['imagenes'] += nuevas
    guardar(data)


def registrar(slugs):
    data = cargar()
    por_slug = {p['slug']: p for p in data['productos']}
    ya = {r['slug'] for r in leer_registro()}
    for slug in slugs:
        if slug not in por_slug:
            fallo(f'no existe el producto {slug}')
        if slug in ya:
            fallo(f'{slug} ya está en el registro')
    nuevo = not os.path.exists(REGISTRO)
    hoy = datetime.date.today().isoformat()
    with open(REGISTRO, 'a', encoding='utf-8', newline='') as fh:
        w = csv.writer(fh)
        if nuevo:
            w.writerow(['fecha', 'slug', 'nombre', 'categoria', 'precio', 'fotos'])
        for slug in slugs:
            p = por_slug[slug]
            v = p['precio']
            w.writerow([p.get('alta') or hoy, slug, p['nombre'], p['categoria'], 'consultar' if v is None else (f'{v["desde"]}-{v["hasta"]}' if isinstance(v, dict) else v), len(p['imagenes'])])
            print(f'Registrado: {p["nombre"]}')
    contador()


def contador():
    filas = leer_registro()
    total = len(filas)
    lotes = total // LOTE
    cobrados = sum(int(r['lotes']) for r in csv.DictReader(open(COBROS, encoding='utf-8'))) if os.path.exists(COBROS) else 0
    pendientes = lotes - cobrados
    faltan = LOTE - total % LOTE
    print(f'Productos subidos: {total}')
    print(f'Lotes completos de {LOTE}: {lotes}  ({lotes * PRECIO_LOTE} €)')
    print(f'Lotes cobrados: {cobrados}  ·  Pendiente de cobro: {pendientes} lote(s) = {pendientes * PRECIO_LOTE} €')
    print(f'Siguiente lote: {total % LOTE}/{LOTE} (faltan {faltan})')


def cobrado(n):
    filas = leer_registro()
    lotes = len(filas) // LOTE
    ya = sum(int(r['lotes']) for r in csv.DictReader(open(COBROS, encoding='utf-8'))) if os.path.exists(COBROS) else 0
    if ya + n > lotes:
        fallo(f'solo hay {lotes - ya} lote(s) pendiente(s) de cobro')
    nuevo = not os.path.exists(COBROS)
    with open(COBROS, 'a', encoding='utf-8', newline='') as fh:
        w = csv.writer(fh)
        if nuevo:
            w.writerow(['fecha', 'lotes', 'importe'])
        w.writerow([datetime.date.today().isoformat(), n, n * PRECIO_LOTE])
    contador()


def lista():
    for p in cargar()['productos']:
        v = p['precio']
        pr = 'consultar' if v is None else (f'{v["desde"]:.0f}-{v["hasta"]:.0f} €' if isinstance(v, dict) else f'{v:.2f} €')
        print(f'{"📌 " if p.get("fijado") else "   "}{p["estado"]:<11} {p["categoria"]:<11} {pr:>12}  {p["slug"]}')


if __name__ == '__main__':
    a = sys.argv[1:]
    if not a:
        print(__doc__); sys.exit(0)
    cmd = a[0]
    if cmd == 'alta' and len(a) >= 2:
        alta(a[1], '--simular' in a, '--forzar' in a)
    elif cmd == 'estado' and len(a) == 3:
        cambiar_estado(a[1], a[2])
    elif cmd == 'baja' and len(a) == 2:
        cambiar_estado(a[1], 'baja')
    elif cmd in ('fijar', 'soltar') and len(a) == 2:
        fijar(a[1], cmd == 'fijar')
    elif cmd == 'fotos' and len(a) >= 3:
        anadir_fotos(a[1], [x for x in a[2:] if x != '--simular'], '--simular' in a)
    elif cmd == 'registrar' and len(a) >= 2:
        registrar(a[1:])
    elif cmd == 'contador':
        contador()
    elif cmd == 'cobrado' and len(a) == 2:
        cobrado(int(a[1]))
    elif cmd == 'lista':
        lista()
    else:
        print(__doc__); sys.exit(1)
