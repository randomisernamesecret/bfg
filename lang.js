// Language persistence for bfgapps.co
// - When the user picks a language from the dropdown, we save it to localStorage.
// - On any page load, if a saved language is set AND the current page is a homepage
//   (root "/" or "/<locale>/"), we redirect to the saved-language homepage.
// - Sub-pages (/apps/*, /blog/*) are English-only, so we do not redirect them.
//   We still keep the selected language visible and route Home / Blog links back
//   to that locale's homepage.
(function () {
  var STORAGE_KEY = 'bfg_lang';
  var LOCALES = ['en', 'de', 'es', 'fr', 'ja', 'zh-CN'];

  function localeHomeFor(code) {
    return code === 'en' ? '/' : '/' + code + '/';
  }

  function normaliseLocale(code) {
    return LOCALES.indexOf(code) !== -1 ? code : null;
  }

  function readSavedLocale() {
    try { return normaliseLocale(localStorage.getItem(STORAGE_KEY)); } catch (err) { return null; }
  }

  function saveLocale(code) {
    if (!normaliseLocale(code)) return;
    try { localStorage.setItem(STORAGE_KEY, code); } catch (err) { /* private mode */ }
  }

  // Detect the locale of the page we're on.
  function currentLocaleFromPath() {
    var path = window.location.pathname;
    var m = path.match(/^\/([a-z]{2}(?:-[A-Z]{2})?)\/(?:$|index\.html)/);
    if (m && normaliseLocale(m[1])) return m[1];
    if (path === '/' || path === '/index.html') return 'en';
    return null; // sub-page
  }

  // Are we on a locale homepage (one we might redirect)?
  function isHomePath() {
    var path = window.location.pathname;
    if (path === '/' || path === '/index.html') return true;
    return /^\/[a-z]{2}(?:-[A-Z]{2})?\/(?:index\.html)?$/.test(path);
  }

  function effectiveLocale() {
    return currentLocaleFromPath() || readSavedLocale() || 'en';
  }

  function updateLanguageUI(code) {
    var label = document.querySelector('.lang-dropdown > a');
    if (label) label.textContent = code.toUpperCase();

    var home = localeHomeFor(code);
    // Pages that have a translated copy under /<locale>/<path>/. We rewrite
    // English links to /foo/ → /<locale>/foo/ when the user has a non-EN locale.
    var LOCALIZED_PATHS = ['/about/'];
    document.querySelectorAll('a[href]').forEach(function (a) {
      if (a.hasAttribute('data-lang')) return;
      var href = a.getAttribute('href');
      if (!href) return;
      // Plain home link.
      if (href === '/' || href === '/index.html') {
        a.setAttribute('href', home);
        return;
      }
      // Any anchor on the English homepage (/#apps, /#blog, /#faq, …).
      var anchorIdx = -1;
      if (href.indexOf('/#') === 0) anchorIdx = 1;
      else if (href.indexOf('/index.html#') === 0) anchorIdx = '/index.html'.length;
      if (anchorIdx > -1) {
        a.setAttribute('href', home + href.slice(anchorIdx));
        return;
      }
      // Pages that exist in every locale: rewrite their root-relative links.
      if (code !== 'en' && LOCALIZED_PATHS.indexOf(href) !== -1) {
        a.setAttribute('href', home.replace(/\/$/, '') + href);
      }
    });
  }

  // 1) Click-through: save the user's chosen language.
  document.addEventListener('click', function (e) {
    var a = e.target.closest && e.target.closest('a[data-lang]');
    if (!a) return;
    var code = a.getAttribute('data-lang');
    if (!normaliseLocale(code)) return;
    saveLocale(code);
    // Let the browser follow the link as normal.
  });

  // 2) Load-time: redirect homepages to the user's saved language.
  var saved = readSavedLocale();
  if (saved) {
    var current = currentLocaleFromPath();
    if (isHomePath() && current !== saved) {
      window.location.replace(localeHomeFor(saved));
      return;
    }
  }

  // 3) If the user lands directly on a localized homepage, make that the
  // selected language. On English-only subpages, keep the existing preference.
  var currentLocale = currentLocaleFromPath();
  if (currentLocale) saveLocale(currentLocale);

  // 4) Reflect the effective language on every page, including English-only
  // app/privacy/support/blog pages.
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function () {
      updateLanguageUI(effectiveLocale());
    });
  } else {
    updateLanguageUI(effectiveLocale());
  }
})();
