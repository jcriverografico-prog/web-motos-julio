#!/usr/bin/env python3
"""Gestión del catálogo de Motos Julio.

  alta FICHA.json [--simular] [--forzar]  Da de alta un producto (ver formato abajo).
  estado SLUG ESTADO                      disponible | reservado | vendido | agotado
  baja SLUG                               Lo quita de la web (se conserva en el registro).
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
  "estado": "disponible"                             (opcional)
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


def fallo(msg):
    print('ERROR  ', msg)
    sys.exit(1)


def alta(ficha_path, simular=False, forzar=False):
    data = cargar()
    f = json.load(open(ficha_path, encoding='utf-8'))
    cats = {c['id'] for c in data['categorias']}
    errores = []
    for campo in ('nombre', 'precio', 'categoria', 'descripcion', 'imagenes'):
        if not f.get(campo):
            errores.append(f'falta «{campo}»')
    if errores:
        fallo('; '.join(errores))
    try:
        precio = leer_precio(f['precio'])
    except ValueError:
        fallo(f'precio no válido: {f["precio"]!r}')
    if precio <= 0:
        fallo('el precio debe ser mayor que 0')
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
        'precio': round(precio, 2), 'categoria': f['categoria'], 'descripcion': f['descripcion'].strip(),
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

    data['productos'].insert(0, producto)  # el más reciente, primero
    guardar(data)
    nuevo = not os.path.exists(REGISTRO)
    with open(REGISTRO, 'a', encoding='utf-8', newline='') as fh:
        w = csv.writer(fh)
        if nuevo:
            w.writerow(['fecha', 'slug', 'nombre', 'categoria', 'precio', 'fotos'])
        w.writerow([producto['alta'], slug, producto['nombre'], producto['categoria'], producto['precio'], len(rutas)])
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
        print(f'{p["estado"]:<11} {p["categoria"]:<11} {p["precio"]:>9.2f} €  {p["slug"]}')


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
    elif cmd == 'contador':
        contador()
    elif cmd == 'cobrado' and len(a) == 2:
        cobrado(int(a[1]))
    elif cmd == 'lista':
        lista()
    else:
        print(__doc__); sys.exit(1)
