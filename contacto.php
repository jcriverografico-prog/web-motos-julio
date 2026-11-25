<?php
// Envío del formulario de contacto de motosjulio.es (funciona en el hosting de Hostinger).
// En GitHub Pages no se ejecuta PHP: allí el formulario no envía.

$destino = 'motosjulio@gmail.com';
$volver  = './contacto/';

if ($_SERVER['REQUEST_METHOD'] !== 'POST') { header('Location: ' . $volver); exit; }

// Campo trampa anti-spam: si viene relleno, es un bot.
if (!empty($_POST['web'])) { header('Location: ' . $volver . '?enviado=1'); exit; }

function limpio($v) { return trim(str_replace(["\r", "\n"], ' ', strip_tags((string)$v))); }

$nombre    = limpio($_POST['nombre'] ?? '');
$apellidos = limpio($_POST['apellidos'] ?? '');
$email     = filter_var(trim($_POST['email'] ?? ''), FILTER_VALIDATE_EMAIL);
$mensaje   = trim(strip_tags((string)($_POST['mensaje'] ?? '')));

if ($nombre === '' || $apellidos === '' || !$email || $mensaje === '') {
    header('Location: ' . $volver . '?error=1'); exit;
}

$asunto  = 'Nuevo mensaje desde la web - ' . $nombre . ' ' . $apellidos;
$cuerpo  = "Nombre: $nombre $apellidos\nCorreo: $email\n\nMensaje:\n$mensaje\n";
$cabeceras = [
    'From: Web Motos Julio <no-reply@motosjulio.es>',
    'Reply-To: ' . $email,
    'Content-Type: text/plain; charset=UTF-8',
];

$ok = mail($destino, '=?UTF-8?B?' . base64_encode($asunto) . '?=', $cuerpo, implode("\r\n", $cabeceras));
header('Location: ' . $volver . ($ok ? '?enviado=1' : '?error=1'));
exit;
