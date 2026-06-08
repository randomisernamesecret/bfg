// Language persistence for bfgapps.co
// - When the user picks a language from the dropdown, we save it to localStorage.
// - On any page load, if a saved language is set AND the current page is a homepage
//   (root "/" or "/<locale>/"), we redirect to the saved-language homepage.
// - Sub-pages (/apps/*, /blog/*, /<loc>/blog/*) are not redirected — only
//   homepages are. We still keep the selected language visible and route Home /
//   Blog links back to that locale's homepage.
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
    // Any path under a locale prefix (/de/, /de/apps/x/, /de/blog/x) is that
    // locale — this keeps the preference correct on localized sub-pages too.
    var m = path.match(/^\/([a-z]{2}(?:-[A-Z]{2})?)\//);
    if (m && normaliseLocale(m[1])) return m[1];
    if (path === '/' || path === '/index.html') return 'en';
    return null; // English sub-page — don't clobber a saved preference
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
    // Anchors that exist on every locale homepage. Others (blog, faq,
    // transparency) only exist on the English page — leave links to them
    // alone so the click lands on /#section, not /<locale>/#section.
    var LOCAL_ANCHORS = ['#apps', '#blog'];
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
      // Anchor on the English homepage (/#apps, /#blog, /#faq, …).
      var anchorIdx = -1;
      if (href.indexOf('/#') === 0) anchorIdx = 1;
      else if (href.indexOf('/index.html#') === 0) anchorIdx = '/index.html'.length;
      if (anchorIdx > -1) {
        var anchor = href.slice(anchorIdx);
        if (LOCAL_ANCHORS.indexOf(anchor) !== -1) {
          a.setAttribute('href', home + anchor);
        }
        // else: keep the link pointing at the English homepage section.
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

  // 2) Load-time: redirect homepages to the user's saved language — except
  // when the URL points at an English-only section like #blog. In that case
  // we keep the user on the English home so the anchor actually resolves.
  var ENGLISH_ONLY_ANCHORS = ['#faq', '#transparency'];
  var saved = readSavedLocale();
  if (saved) {
    var current = currentLocaleFromPath();
    if (isHomePath() && current !== saved) {
      var hash = window.location.hash;
      if (ENGLISH_ONLY_ANCHORS.indexOf(hash) === -1) {
        window.location.replace(localeHomeFor(saved) + hash);
        return;
      }
    }
  }

  // 3) If the user lands directly on a localized homepage, make that the
  // selected language. On English-only subpages, keep the existing preference.
  var currentLocale = currentLocaleFromPath();
  if (currentLocale) saveLocale(currentLocale);

  // Swap app screenshots to the page's locale, falling back to the English asset
  // if a localized one doesn't exist. Uses the PAGE locale (not the saved
  // preference) so English pages keep English shots. Targets the numbered app
  // screenshots only (/assets/<slug>/NN.webp), not hero/card images.
  function localizeScreenshots() {
    var loc = currentLocaleFromPath();
    if (!loc || loc === 'en') return;
    document.querySelectorAll('img[src]').forEach(function (img) {
      var src = img.getAttribute('src');
      if (!src) return;
      var localized = null;
      // Only localize the app-page galleries + homepage hero strip
      // (/assets/<slug>/NN.webp). The homepage "Available Now" CARDS
      // (/assets/<slug>-hero.png) are bespoke per-app marketing art with no shared
      // composer, so they are NEVER swapped — every language shows the identical
      // English card, keeping the grid's zoom consistent across languages.
      var m = src.match(/^\/assets\/([^/]+)\/(\d+\.webp)$/);
      if (m) localized = '/assets/' + m[1] + '/' + loc + '/' + m[2];
      if (!localized) return;
      img.addEventListener('error', function onerr() {
        img.removeEventListener('error', onerr);
        img.src = src; // localized missing → fall back to English
      });
      img.src = localized;
    });
  }

  // 4) Reflect the effective language on every page, including English-only
  // app/privacy/support/blog pages.
  function onReady() {
    updateLanguageUI(effectiveLocale());
    localizeScreenshots();
  }
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', onReady);
  } else {
    onReady();
  }
})();
