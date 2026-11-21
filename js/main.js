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

  function render() {
    var buttons = document.querySelectorAll('[data-theme-toggle]');
    for (var i = 0; i < buttons.length; i++) {
      var dark = current() === 'dark';
      buttons[i].textContent = dark ? buttons[i].getAttribute('data-label-dark') : buttons[i].getAttribute('data-label-light');
      buttons[i].setAttribute('aria-pressed', dark ? 'true' : 'false');
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
