/* Site is dark-only. The light/dark toggle has been removed — keep the
   document on the dark theme and remove any leftover toggle button. */
(function () {
  document.documentElement.setAttribute('data-theme', 'dark');
  try { localStorage.setItem('theme', 'dark'); } catch (e) {}
  document.addEventListener('DOMContentLoaded', function () {
    var btn = document.querySelector('.theme-toggle');
    if (btn) btn.remove();
  });
})();
