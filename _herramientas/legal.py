# Textos legales de motosjulio.es (LSSI-CE, RGPD/LOPDGDD y cookies).
# Rellena los datos del titular en TITULAR antes de publicar en el dominio definitivo.

TITULAR = {
    'nombre': 'Julio López Sánchez',
    'nif': '[NIF/CIF]',
    'comercial': 'Motos Julio',
    'domicilio': 'C/ San Juan de Ávila, 31, Bajo, 13170 Miguelturra (Ciudad Real), España',
    'email': 'motosjulio@gmail.com',
    'telefono': '926 24 06 88 / 607 749 877',
    'dominio': 'www.motosjulio.es',
}
ACTUALIZADO = '26 de noviembre de 2026'


def _t(s):
    return s.format(**TITULAR)


AVISO_LEGAL = _t('''
<h1>Aviso legal</h1>
<p class="mj-legal-updated">Última actualización: ''' + ACTUALIZADO + '''</p>

<h2>1. Datos identificativos</h2>
<p>En cumplimiento del artículo 10 de la Ley 34/2002, de 11 de julio, de Servicios de la Sociedad de la Información y de Comercio Electrónico (LSSI-CE), se informa de los datos del titular de este sitio web:</p>
<ul>
<li><strong>Titular:</strong> {nombre}</li>
<li><strong>Nombre comercial:</strong> {comercial}</li>
<li><strong>NIF/CIF:</strong> {nif}</li>
<li><strong>Domicilio:</strong> {domicilio}</li>
<li><strong>Correo electrónico:</strong> <a href="mailto:{email}">{email}</a></li>
<li><strong>Teléfono:</strong> {telefono}</li>
<li><strong>Sitio web:</strong> {dominio}</li>
</ul>

<h2>2. Objeto</h2>
<p>Este sitio web ofrece información sobre la actividad de {comercial}: compraventa de motos, quads y bicicletas de segunda mano, venta de piezas de desguace, alquiler de box para particulares y venta de patinetes eléctricos y otros artículos. El acceso y uso del sitio atribuye la condición de usuario e implica la aceptación de este aviso legal.</p>

<h2>3. Productos, precios y disponibilidad</h2>
<p>Los productos y precios publicados tienen carácter informativo y pueden variar o dejar de estar disponibles sin previo aviso. Este sitio web no permite realizar compras ni pagos en línea: cualquier compra, reserva o alquiler se formaliza directamente con {comercial}, por teléfono o en el establecimiento, donde se informará de las condiciones, la garantía aplicable y el precio final.</p>

<h2>4. Condiciones de uso</h2>
<p>El usuario se compromete a hacer un uso adecuado de los contenidos y a no emplearlos para actividades ilícitas o contrarias a la buena fe, ni para dañar los sistemas del titular o de terceros.</p>

<h2>5. Propiedad intelectual e industrial</h2>
<p>Los textos, fotografías, logotipos y demás contenidos de este sitio son propiedad del titular o se usan con autorización de sus propietarios. Queda prohibida su reproducción, distribución o transformación sin autorización expresa, salvo para uso personal y privado.</p>

<h2>6. Responsabilidad</h2>
<p>El titular no se hace responsable de los daños derivados de interrupciones del servicio, errores en los contenidos o virus que no se deban a su actuación. Tampoco responde de los contenidos de sitios de terceros a los que se pueda acceder mediante enlaces, como redes sociales o Google Maps.</p>

<h2>7. Protección de datos y cookies</h2>
<p>El tratamiento de datos personales se rige por la <a href="{{root}}politica-de-privacidad/">Política de privacidad</a> y el uso de cookies, por la <a href="{{root}}politica-de-cookies/">Política de cookies</a>.</p>

<h2>8. Legislación aplicable</h2>
<p>Este aviso legal se rige por la legislación española. Para cualquier controversia, las partes se someten a los juzgados y tribunales que correspondan conforme a la normativa vigente, en particular la de consumidores y usuarios.</p>
''')

PRIVACIDAD = _t('''
<h1>Política de privacidad</h1>
<p class="mj-legal-updated">Última actualización: ''' + ACTUALIZADO + '''</p>

<h2>1. Responsable del tratamiento</h2>
<ul>
<li><strong>Responsable:</strong> {nombre} ({comercial})</li>
<li><strong>NIF/CIF:</strong> {nif}</li>
<li><strong>Domicilio:</strong> {domicilio}</li>
<li><strong>Correo electrónico:</strong> <a href="mailto:{email}">{email}</a></li>
<li><strong>Teléfono:</strong> {telefono}</li>
</ul>

<h2>2. Qué datos tratamos y para qué</h2>
<p>Cuando nos escribes mediante el formulario de contacto, por correo electrónico o por teléfono, tratamos tu nombre, apellidos, correo electrónico, teléfono (si nos lo facilitas) y el contenido de tu mensaje con la única finalidad de <strong>responder a tu consulta</strong> y, en su caso, gestionar la compra, reserva o alquiler que nos solicites.</p>
<p>No usamos tus datos para enviarte publicidad ni para elaborar perfiles, y no tomamos decisiones automatizadas.</p>

<h2>3. Base legal</h2>
<ul>
<li><strong>Consentimiento</strong> (art. 6.1.a RGPD), que das al enviar el formulario marcando la casilla de aceptación. Puedes retirarlo en cualquier momento.</li>
<li><strong>Aplicación de medidas precontractuales o ejecución de un contrato</strong> (art. 6.1.b RGPD), cuando la consulta se refiere a la compra, reserva o alquiler de un producto o servicio.</li>
</ul>

<h2>4. Cuánto tiempo conservamos los datos</h2>
<p>Conservamos los datos el tiempo necesario para atender tu consulta. Si llega a formalizarse una operación, los conservaremos durante los plazos que exige la normativa fiscal y mercantil.</p>

<h2>5. Destinatarios</h2>
<p>No cedemos tus datos a terceros salvo obligación legal. Para prestar el servicio intervienen como encargados del tratamiento:</p>
<ul>
<li><strong>Hostinger International Ltd.</strong>, proveedor de alojamiento web, con servidores en la Unión Europea.</li>
<li><strong>Google Ireland Ltd.</strong>, proveedor del correo electrónico (Gmail) al que llegan los mensajes del formulario. Google puede tratar datos en Estados Unidos, al amparo del Marco de Privacidad de Datos UE-EE. UU. y de cláusulas contractuales tipo.</li>
</ul>

<h2>6. Tus derechos</h2>
<p>Puedes ejercer los derechos de acceso, rectificación, supresión, oposición, limitación del tratamiento y portabilidad escribiendo a <a href="mailto:{email}">{email}</a> o dirigiéndote a nuestro domicilio, indicando el derecho que ejerces. Si consideras que no hemos atendido correctamente tu solicitud, puedes presentar una reclamación ante la Agencia Española de Protección de Datos (<a href="https://www.aepd.es" target="_blank" rel="noopener">www.aepd.es</a>).</p>

<h2>7. Seguridad</h2>
<p>Aplicamos medidas técnicas y organizativas razonables para proteger tus datos frente a pérdida, uso indebido o acceso no autorizado. El sitio web se sirve mediante conexión cifrada (HTTPS).</p>
''')

COOKIES = _t('''
<h1>Política de cookies</h1>
<p class="mj-legal-updated">Última actualización: ''' + ACTUALIZADO + '''</p>

<h2>1. ¿Qué son las cookies?</h2>
<p>Las cookies son pequeños archivos que un sitio web guarda en tu navegador para recordar información sobre tu visita.</p>

<h2>2. Cookies que usa este sitio</h2>
<p><strong>Este sitio web no instala cookies propias ni utiliza herramientas de analítica o publicidad.</strong> Las fuentes tipográficas y las imágenes se sirven desde nuestro propio servidor, por lo que al navegar no se envían datos a terceros para esos fines.</p>

<h2>3. Contenido de terceros: Google Maps</h2>
<p>En el pie de página y en la página de contacto puedes ver un mapa de Google Maps con nuestra ubicación. El mapa <strong>solo se carga si pulsas «Ver mapa»</strong>. A partir de ese momento, Google puede instalar cookies y tratar datos de tu navegación conforme a su propia política: <a href="https://policies.google.com/technologies/cookies" target="_blank" rel="noopener">policies.google.com/technologies/cookies</a>.</p>
<p>Lo mismo ocurre si sigues los enlaces a nuestras redes sociales (Facebook e Instagram): al salir de este sitio se aplican las políticas de esas plataformas.</p>

<h2>4. Cómo gestionar o eliminar cookies</h2>
<p>Puedes bloquear o eliminar las cookies desde la configuración de tu navegador:</p>
<ul>
<li><a href="https://support.google.com/chrome/answer/95647" target="_blank" rel="noopener">Google Chrome</a></li>
<li><a href="https://support.mozilla.org/es/kb/Borrar%20cookies" target="_blank" rel="noopener">Mozilla Firefox</a></li>
<li><a href="https://support.apple.com/es-es/guide/safari/sfri11471/mac" target="_blank" rel="noopener">Safari</a></li>
<li><a href="https://support.microsoft.com/es-es/microsoft-edge" target="_blank" rel="noopener">Microsoft Edge</a></li>
</ul>

<h2>5. Cambios</h2>
<p>Si en el futuro incorporamos herramientas que utilicen cookies, actualizaremos esta política y, cuando sea necesario, te pediremos consentimiento antes de instalarlas.</p>
''')

PAGES = {
    'aviso-legal': ('Aviso legal | Motos Julio', 'Aviso legal de Motos Julio, compraventa de motos, quads y bicicletas de segunda mano en Miguelturra (Ciudad Real).', AVISO_LEGAL),
    'politica-de-privacidad': ('Política de privacidad | Motos Julio', 'Cómo trata Motos Julio los datos personales de quienes contactan a través de la web.', PRIVACIDAD),
    'politica-de-cookies': ('Política de cookies | Motos Julio', 'Información sobre el uso de cookies en motosjulio.es.', COOKIES),
}

FORM_INFO = _t('Responsable: {nombre} ({comercial}). Finalidad: responder a tu consulta. '
               'Derechos: acceso, rectificación, supresión y otros, escribiendo a {email}. ')
