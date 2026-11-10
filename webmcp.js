// Tools for AI agents that browse this site (WebMCP). Does nothing in browsers without the API.
(function () {
  var mc = navigator.modelContext;
  if (!mc || typeof mc.registerTool !== 'function') return;
  var cache = null;
  function load() {
    if (!cache) cache = fetch('/apps.json').then(function (r) { return r.json(); });
    return cache;
  }
  function reply(obj) {
    return { content: [{ type: 'text', text: JSON.stringify(obj) }] };
  }
  function brief(a) {
    return { name: a.name, slug: a.slug, category: a.category, platforms: a.platforms, summary: a.summary,
             priceModel: a.priceModel, url: a.url, appStoreUrl: a.appStoreUrl };
  }
  function register(tool) {
    try { mc.registerTool(tool); } catch (e) { /* older drafts of the API */ }
  }
  register({
    name: 'search_bfg_apps',
    description: 'Search the Blue Flame Games app catalogue. Returns matching apps with devices, price model and App Store link.',
    inputSchema: {
      type: 'object',
      properties: {
        query: { type: 'string', description: 'Words to look for, such as "piano", "rain alerts" or "kids drawing". Leave empty to list every app.' },
        platform: { type: 'string', enum: ['iPhone', 'iPad', 'Mac', 'Apple Watch'], description: 'Only apps for this device.' }
      }
    },
    execute: function (input) {
      input = input || {};
      return load().then(function (d) {
        var words = String(input.query || '').toLowerCase().split(/\s+/).filter(Boolean);
        var out = d.apps.filter(function (a) {
          if (input.platform && a.platforms.indexOf(input.platform) < 0) return false;
          var hay = [a.name, a.category, a.summary, a.audience].join(' ').toLowerCase();
          return words.every(function (w) { return hay.indexOf(w) >= 0; });
        }).map(brief);
        return reply({ count: out.length, apps: out });
      });
    }
  });
  register({
    name: 'get_bfg_app',
    description: 'Get the full catalogue entry for one Blue Flame Games app: summary, audience, devices, price model, privacy facts and links.',
    inputSchema: {
      type: 'object',
      properties: { slug: { type: 'string', description: 'The app slug from search_bfg_apps, such as "keystrike".' } },
      required: ['slug']
    },
    execute: function (input) {
      return load().then(function (d) {
        var s = String((input || {}).slug || '').toLowerCase();
        var a = d.apps.filter(function (x) { return x.slug === s || x.shortName.toLowerCase() === s; })[0];
        return reply(a || { error: 'No app with that slug. Use search_bfg_apps first.' });
      });
    }
  });
})();
