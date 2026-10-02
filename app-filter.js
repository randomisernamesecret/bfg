// Homepage "Available now" filter: All / Apps / Games.
(function() {
  var bar = document.querySelector('.app-filter');
  var grid = document.querySelector('.apps-grid');
  if (!bar || !grid) return;
  var cards = [].slice.call(grid.querySelectorAll('.app-card[data-kind]'));
  var buttons = [].slice.call(bar.querySelectorAll('button[data-kind]'));
  var thumb = bar.querySelector('.app-filter-thumb');
  var active = buttons[0];

  buttons.forEach(function(btn) {
    var kind = btn.getAttribute('data-kind');
    var n = cards.filter(function(c) { return kind === 'all' || c.getAttribute('data-kind') === kind; }).length;
    var count = btn.querySelector('.count');
    if (count) count.textContent = n;
  });

  function place() {
    thumb.style.setProperty('--x', active.offsetLeft + 'px');
    thumb.style.setProperty('--w', active.offsetWidth + 'px');
  }

  function apply(btn, animate) {
    active = btn;
    var kind = btn.getAttribute('data-kind');
    buttons.forEach(function(b) { b.setAttribute('aria-pressed', b === btn ? 'true' : 'false'); });
    var i = 0;
    cards.forEach(function(card) {
      var show = kind === 'all' || card.getAttribute('data-kind') === kind;
      card.hidden = !show;
      card.classList.remove('is-entering');
      if (show && animate) {
        card.style.setProperty('--i', i++);
        void card.offsetWidth;
        card.classList.add('is-entering');
      }
    });
    place();
  }

  buttons.forEach(function(btn) {
    btn.addEventListener('click', function() { if (btn !== active) apply(btn, true); });
  });

  bar.hidden = false;
  bar.classList.add('no-anim');
  apply(active, false);
  requestAnimationFrame(function() { requestAnimationFrame(function() { bar.classList.remove('no-anim'); }); });
  window.addEventListener('resize', place);
  if (document.fonts && document.fonts.ready) document.fonts.ready.then(place);
})();
