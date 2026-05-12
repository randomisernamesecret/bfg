// Language persistence for bfgapps.co
// - When the user picks a language from the dropdown, we save it to localStorage.
// - On any page load, if a saved language is set AND the current page is a homepage
//   (root "/" or "/<locale>/"), we redirect to the saved-language homepage.
// - Sub-pages (/apps/*, /blog/*) are English-only — we never redirect those.
(function () {
  var STORAGE_KEY = 'bfg_lang';
  var LOCALES = ['en', 'de', 'es', 'fr', 'ja', 'zh-CN'];

  function localeHomeFor(code) {
    return code === 'en' ? '/' : '/' + code + '/';
  }

  // Detect the locale of the page we're on.
  function currentLocaleFromPath() {
    var path = window.location.pathname;
    var m = path.match(/^\/([a-z]{2}(?:-[A-Z]{2})?)\/(?:$|index\.html)/);
    if (m && LOCALES.indexOf(m[1]) !== -1) return m[1];
    if (path === '/' || path === '/index.html') return 'en';
    return null; // sub-page
  }

  // Are we on a locale homepage (one we might redirect)?
  function isHomePath() {
    var path = window.location.pathname;
    if (path === '/' || path === '/index.html') return true;
    return /^\/[a-z]{2}(?:-[A-Z]{2})?\/(?:index\.html)?$/.test(path);
  }

  // 1) Click-through: save the user's chosen language.
  document.addEventListener('click', function (e) {
    var a = e.target.closest && e.target.closest('a[data-lang]');
    if (!a) return;
    var code = a.getAttribute('data-lang');
    if (LOCALES.indexOf(code) === -1) return;
    try { localStorage.setItem(STORAGE_KEY, code); } catch (err) { /* private mode */ }
    // Let the browser follow the link as normal.
  });

  // 2) Load-time: redirect homepages to the user's saved language.
  var saved;
  try { saved = localStorage.getItem(STORAGE_KEY); } catch (err) { saved = null; }
  if (saved && LOCALES.indexOf(saved) !== -1) {
    var current = currentLocaleFromPath();
    if (isHomePath() && current !== saved) {
      window.location.replace(localeHomeFor(saved));
      return;
    }
  }
})();
