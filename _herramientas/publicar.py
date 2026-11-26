#!/usr/bin/env python3
"""Regenera la web desde el catálogo, la valida y la deja en la raíz del repo.

Uso: python3 _herramientas/publicar.py
No hace commit ni push: eso se hace después de revisar.
Si la validación falla, la raíz del repo NO se toca.
"""
import os, shutil, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
CONSERVAR = {'.git', '_herramientas', 'README.md', '.nojekyll', '.gitignore'}
CONSERVAR_ASSETS = {'productos'}  # assets/productos: fotos subidas con catalogo.py


def run(cmd):
    r = subprocess.run(cmd, cwd=HERE)
    if r.returncode:
        sys.exit(r.returncode)


tmp = tempfile.mkdtemp(prefix='mj-web-')
# caché de imágenes ya descargadas (evita volver a bajarlas de Hostinger)
if os.path.isdir(os.path.join(ROOT, 'assets', 'img')):
    shutil.copytree(os.path.join(ROOT, 'assets', 'img'), os.path.join(tmp, 'assets', 'img'))
run([sys.executable, os.path.join(HERE, 'build.py'), tmp])
shutil.copytree(os.path.join(HERE, 'static'), tmp, dirs_exist_ok=True)
run([sys.executable, os.path.join(HERE, 'validar.py'), '--web', tmp])

# sustituir la web de la raíz por la nueva
for name in os.listdir(ROOT):
    if name in CONSERVAR:
        continue
    path = os.path.join(ROOT, name)
    if name == 'assets':
        for sub in os.listdir(path):
            if sub not in CONSERVAR_ASSETS:
                p = os.path.join(path, sub)
                shutil.rmtree(p) if os.path.isdir(p) else os.remove(p)
        continue
    shutil.rmtree(path) if os.path.isdir(path) else os.remove(path)
shutil.copytree(tmp, ROOT, dirs_exist_ok=True)
shutil.rmtree(tmp)
print('Web regenerada en la raíz del repositorio. Revisa y haz commit.')
