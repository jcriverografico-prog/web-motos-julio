# Motos Julio — web

Réplica estática de [motosjulio.es](https://www.motosjulio.es), migrada desde Hostinger Website Builder.

- HTML/CSS/JS sin dependencias: se publica tal cual (GitHub Pages para pruebas, Hostinger por Git en producción).
- `contacto.php`: envía el formulario a motosjulio@gmail.com (solo funciona en el hosting de Hostinger, no en GitHub Pages).
- `assets/productos.json`: listado de productos de la tienda.

## Pendiente
- Descargar a local las fotos de producto (ahora se cargan desde `cdn.zyrosite.com`, el CDN de Hostinger). Hay que hacerlo antes de dar de baja el constructor.
- Confirmar qué productos van en cada categoría (patines y desguace están vacíos).
