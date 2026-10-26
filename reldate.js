// Blog meta line: turn <time class="rel-date"> into "Updated 3 days ago" (always in
// days) in the page language. The static text keeps the full date for crawlers;
// style.css hides it until this has run.
(function () {
  var TPL = {
    en: 'Updated {d}', de: 'Aktualisiert {d}', es: 'Actualizado {d}',
    fr: 'Mis à jour {d}', ja: '{d}に更新', zh: '{d}更新'
  };
  var lang = document.documentElement.lang || 'en';
  var tpl = TPL[lang.slice(0, 2)] || TPL.en;
  var els = document.querySelectorAll('time.rel-date');
  if (!window.Intl || !Intl.RelativeTimeFormat) {
    els.forEach(function (el) { el.classList.add('rel-ready'); });
    return;
  }
  var rtf = new Intl.RelativeTimeFormat(lang, { numeric: 'auto' });

  var now = new Date();
  var today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
  els.forEach(function (el) {
    var p = (el.getAttribute('datetime') || '').split('-');
    el.classList.add('rel-ready');
    if (p.length !== 3) return;
    var then = new Date(+p[0], +p[1] - 1, +p[2]);
    var days = Math.max(0, Math.round((today - then) / 864e5));
    el.textContent = tpl.replace('{d}', rtf.format(-days, 'day'));
  });
})();
