// Interacciones que antes hacía el JavaScript de Hostinger.
(function () {
  // Animación de entrada de los bloques (igual que en Hostinger)
  document.documentElement.classList.add('mj-js');
  var anim = document.querySelectorAll('.transition, [data-animation-role]');
  function activate(el) {
    el.setAttribute('data-animation-state', 'active');
    if (el.getAttribute('data-animation-role') === 'image' || el.tagName === 'IMG') el.classList.add('loaded');
  }
  if ('IntersectionObserver' in window) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) { if (en.isIntersecting) { activate(en.target); io.unobserve(en.target); } });
    }, { rootMargin: '0px 0px -5% 0px' });
    anim.forEach(function (el) { io.observe(el); });
  } else {
    anim.forEach(activate);
  }

  // Menú móvil
  document.querySelectorAll('.burger').forEach(function (btn) {
    btn.addEventListener('click', function () {
      var header = btn.closest('.block-header-layout-mobile');
      var dd = header && header.querySelector('.block-header-layout-mobile__dropdown');
      btn.classList.toggle('burger--open');
      if (dd) dd.classList.toggle('block-header-layout-mobile__dropdown--open');
    });
  });

  // Galería de la ficha de producto
  document.querySelectorAll('.product-carousel').forEach(function (car) {
    var main = car.querySelector('.product-carousel__main-image');
    var thumbs = Array.prototype.slice.call(car.querySelectorAll('.product-carousel__image-list-element'));
    var dots = Array.prototype.slice.call(car.querySelectorAll('.product-carousel__dot'));
    var srcs = thumbs.map(function (t) { var i = t.querySelector('img'); return i && i.getAttribute('src'); }).filter(Boolean);
    if (!main || srcs.length < 2) {
      car.querySelectorAll('.product-carousel__slider-button, .product-carousel__dots-wrapper').forEach(function (e) { e.style.display = 'none'; });
      return;
    }
    var idx = 0;
    function show(i) {
      idx = (i + srcs.length) % srcs.length;
      main.setAttribute('src', srcs[idx]);
      main.removeAttribute('srcset');
      thumbs.forEach(function (t, k) { t.classList.toggle('product-carousel__image-list-element--active', k === idx); });
      dots.forEach(function (d, k) { d.classList.toggle('product-carousel__dot--active', k === idx); });
    }
    thumbs.forEach(function (t, k) { t.addEventListener('click', function () { show(k); }); });
    car.querySelectorAll('.product-carousel__dot-button').forEach(function (d, k) { d.addEventListener('click', function () { show(k); }); });
    var l = car.querySelector('.product-carousel__slider-button--left');
    var r = car.querySelector('.product-carousel__slider-button--right');
    if (l) l.addEventListener('click', function () { show(idx - 1); });
    if (r) r.addEventListener('click', function () { show(idx + 1); });
  });

  // Aviso tras enviar el formulario (contacto.php redirige con ?enviado=1 o ?error=1)
  var q = location.search;
  var form = document.querySelector('form[name="Contact form"]');
  if (form && /[?&](enviado|error)=1/.test(q)) {
    var ok = /enviado=1/.test(q);
    var msg = document.createElement('p');
    msg.className = 'mj-form-msg ' + (ok ? 'mj-form-msg--ok' : 'mj-form-msg--error');
    msg.textContent = ok ? '¡Gracias! Hemos recibido tu mensaje y te responderemos pronto.'
                         : 'No se ha podido enviar el mensaje. Llámanos al 607 749 877.';
    form.parentNode.insertBefore(msg, form);
  }
})();
