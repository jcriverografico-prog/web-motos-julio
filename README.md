# Motos Julio — web

Réplica estática de [motosjulio.es](https://www.motosjulio.es), migrada desde Hostinger Website Builder.

- HTML/CSS/JS sin dependencias: se publica tal cual (GitHub Pages para pruebas, Hostinger por Git en producción).
- `contacto.php`: envía el formulario a motosjulio@gmail.com (solo funciona en el hosting de Hostinger, no en GitHub Pages).
- `assets/productos.json`: listado de productos de la tienda.

## Regenerar la web
`python3 _herramientas/build.py _herramientas/src SALIDA && cp -r _herramientas/static/. SALIDA/` y copiar SALIDA a la raíz.
- Textos legales y datos del titular: `_herramientas/legal.py`.
- Categorías de productos: `CATEGORY_OVERRIDES` en `_herramientas/build.py`.

## Pendiente
- Rellenar titular y NIF en `_herramientas/legal.py` antes de publicar en motosjulio.es.
- Descargar a local las fotos de producto (ahora se cargan desde `cdn.zyrosite.com`). Hay que hacerlo antes de dar de baja el constructor de Hostinger.
