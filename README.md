# Motos Julio — web

Web estática de [motosjulio.es](https://www.motosjulio.es), migrada desde Hostinger Website Builder.
Se publica en Hostinger por Git (y en GitHub Pages para pruebas).

## Cómo funciona
- `_herramientas/catalogo/productos.json` es la fuente de la tienda: nombre, precio, categoría, descripción, fotos y estado de cada producto.
- `python3 _herramientas/catalogo.py alta ficha.json` da de alta un producto: optimiza las fotos (WebP), comprueba duplicados y lo apunta en el registro.
- `python3 _herramientas/publicar.py` regenera toda la web, la valida (`validar.py`) y solo la deja en la raíz si no hay errores.
- `python3 _herramientas/catalogo.py contador` muestra los productos subidos y los lotes de 30 (50 € cada uno).
- Textos legales y datos del titular: `_herramientas/legal.py`.

## Pendiente
- Rellenar titular y NIF en `_herramientas/legal.py` antes de publicar en motosjulio.es.
- Descargar a local las fotos de los productos antiguos (ahora se cargan desde `cdn.zyrosite.com`). Hay que hacerlo antes de dar de baja el constructor de Hostinger.
