#!/usr/bin/env python3
"""Descarga las fotos de los productos que siguen en el CDN de Hostinger y las guarda
en assets/productos/<slug>/ (WebP + miniatura), actualizando productos.json.
Se puede ejecutar varias veces: solo procesa las imágenes que aún son remotas."""
import io, json, os, subprocess, sys

from PIL import Image, ImageOps

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
CAT_FILE = os.path.join(HERE, 'catalogo', 'productos.json')
sys.path.insert(0, HERE)
from catalogo import MAX_LADO, MINI, CALIDAD, guardar  # noqa: E402

data = json.load(open(CAT_FILE, encoding='utf-8'))
fallos = 0
for p in data['productos']:
    nuevas = []
    for i, u in enumerate(p['imagenes']):
        if not u.startswith('http'):
            nuevas.append(u)
            continue
        r = subprocess.run(['curl', '-sSfL', '-m', '90', u], capture_output=True)
        try:
            img = ImageOps.exif_transpose(Image.open(io.BytesIO(r.stdout))).convert('RGB')
        except Exception as e:
            print(f'ERROR   {p["slug"]}: no se pudo descargar {u} ({e})')
            nuevas.append(u)
            fallos += 1
            continue
        destino = f'assets/productos/{p["slug"]}/{i + 1:02d}.webp'
        os.makedirs(os.path.join(ROOT, os.path.dirname(destino)), exist_ok=True)
        g = img.copy(); g.thumbnail((MAX_LADO, MAX_LADO), Image.LANCZOS)
        g.save(os.path.join(ROOT, destino), 'WEBP', quality=CALIDAD, method=6)
        m = img.copy(); m.thumbnail((MINI, MINI * 2), Image.LANCZOS)
        m.save(os.path.join(ROOT, destino.replace('.webp', '-600.webp')), 'WEBP', quality=78, method=6)
        print(f'OK      {p["slug"]}: {destino} ({img.width}×{img.height})')
        nuevas.append(destino)
    p['imagenes'] = nuevas
guardar(data)
print(f'\nTerminado · {fallos} fallos')
sys.exit(1 if fallos else 0)
