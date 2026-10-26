// Blog meta line: turn <time class="rel-date"> into "Updated 3 days ago" in the
// page language. The static text keeps the full date for crawlers and no-JS.
(function () {
  var TPL = {
    en: { updated: 'Updated {d}', published: 'Published {d}' },
    de: { updated: 'Aktualisiert {d}', published: 'Veröffentlicht {d}' },
    es: { updated: 'Actualizado {d}', published: 'Publicado {d}' },
    fr: { updated: 'Mis à jour {d}', published: 'Publié {d}' },
    ja: { updated: '{d}に更新', published: '{d}に公開' },
    zh: { updated: '{d}更新', published: '{d}发布' }
  };
  var lang = document.documentElement.lang || 'en';
  var tpl = TPL[lang.slice(0, 2)] || TPL.en;
  if (!window.Intl || !Intl.RelativeTimeFormat) return;
  var rtf = new Intl.RelativeTimeFormat(lang, { numeric: 'auto' });

  function relative(days) {
    if (days < 7) return rtf.format(-days, 'day');
    if (days < 31) return rtf.format(-Math.floor(days / 7), 'week');
    if (days < 365) return rtf.format(-Math.floor(days / 30.44), 'month');
    return rtf.format(-Math.floor(days / 365.25), 'year');
  }

  var now = new Date();
  var today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
  document.querySelectorAll('time.rel-date').forEach(function (el) {
    var p = (el.getAttribute('datetime') || '').split('-');
    if (p.length !== 3) return;
    var then = new Date(+p[0], +p[1] - 1, +p[2]);
    var days = Math.max(0, Math.round((today - then) / 864e5));
    el.title = el.textContent;
    el.textContent = (tpl[el.dataset.kind] || tpl.updated).replace('{d}', relative(days));
  });
})();
