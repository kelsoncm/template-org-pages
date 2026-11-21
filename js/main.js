// Alternância de tema claro/escuro, lembrada por visitante (localStorage é só conveniência).
(function () {
  var root = document.documentElement;
  var KEY = 'theme';

  function stored() {
    try { return localStorage.getItem(KEY); } catch (e) { return null; }
  }

  function current() {
    var theme = root.getAttribute('data-theme');
    if (theme) { return theme; }
    return window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
  }

  // O botão mostra a ação que executa: no tema escuro oferece o claro, e vice-versa.
  function render() {
    var buttons = document.querySelectorAll('[data-theme-toggle]');
    var dark = current() === 'dark';
    for (var i = 0; i < buttons.length; i++) {
      var label = buttons[i].getAttribute(dark ? 'data-label-to-light' : 'data-label-to-dark');
      if (label) { buttons[i].textContent = label; } // sem o atributo (HTML antigo em cache), mantém o texto atual
    }
  }

  var saved = stored();
  if (saved === 'light' || saved === 'dark') { root.setAttribute('data-theme', saved); }

  document.addEventListener('DOMContentLoaded', function () {
    render();
    document.addEventListener('click', function (event) {
      var button = event.target.closest && event.target.closest('[data-theme-toggle]');
      if (!button) { return; }
      var next = current() === 'dark' ? 'light' : 'dark';
      root.setAttribute('data-theme', next);
      try { localStorage.setItem(KEY, next); } catch (e) { /* armazenamento indisponível */ }
      render();
    });
  });
})();
