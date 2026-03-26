function getPreferred() {
  var saved = localStorage.getItem('theme');
  if (saved) return saved;
  return window.matchMedia('(prefers-color-scheme: light)').matches ? 'light' : 'dark';
}
function applyTheme(t) {
  document.documentElement.setAttribute('data-theme', t);
  var btn = document.querySelector('.theme-toggle');
  if (btn) btn.textContent = t === 'dark' ? 'Light' : 'Dark';
}
function toggleTheme() {
  var current = document.documentElement.getAttribute('data-theme') || getPreferred();
  var next = current === 'dark' ? 'light' : 'dark';
  localStorage.setItem('theme', next);
  applyTheme(next);
}
applyTheme(getPreferred());
document.addEventListener('DOMContentLoaded', function() {
  var btn = document.querySelector('.theme-toggle');
  if (btn) btn.addEventListener('click', toggleTheme);
});
