document.addEventListener('DOMContentLoaded', function() {
  var hamburger = document.querySelector('.nav-hamburger');
  var navLinks = document.querySelector('.nav-links');

  // Hamburger toggle
  if (hamburger && navLinks) {
    hamburger.setAttribute('aria-expanded', 'false');
    hamburger.addEventListener('click', function() {
      var isOpen = navLinks.classList.toggle('open');
      hamburger.textContent = isOpen ? '✕' : '☰';
      hamburger.setAttribute('aria-expanded', isOpen ? 'true' : 'false');
    });
  }

  // All dropdowns — apps menu, language picker, anything else marked
  // `.nav-dropdown`. Each opens on click of its `> a`, closes on outside
  // click and Escape. Selector originally targeted only the first dropdown;
  // this version handles N.
  var dropdowns = document.querySelectorAll('.nav-dropdown');
  dropdowns.forEach(function(dropdown) {
    var link = dropdown.querySelector(':scope > a');
    var menu = dropdown.querySelector(':scope > .nav-dropdown-menu');
    if (!link || !menu) return;

    link.setAttribute('aria-expanded', 'false');
    link.setAttribute('aria-haspopup', 'true');

    link.addEventListener('click', function(e) {
      e.preventDefault();
      // Close sibling dropdowns first.
      dropdowns.forEach(function(other) {
        if (other !== dropdown) {
          other.classList.remove('open');
          var otherLink = other.querySelector(':scope > a');
          if (otherLink) otherLink.setAttribute('aria-expanded', 'false');
        }
      });
      var isOpen = dropdown.classList.toggle('open');
      link.setAttribute('aria-expanded', isOpen ? 'true' : 'false');
    });

    link.addEventListener('keydown', function(e) {
      if (e.key === 'Enter' || e.key === ' ') {
        e.preventDefault();
        var isOpen = dropdown.classList.toggle('open');
        link.setAttribute('aria-expanded', isOpen ? 'true' : 'false');
        if (isOpen) {
          var first = menu.querySelector('a');
          if (first) first.focus();
        }
      }
      if (e.key === 'Escape') {
        dropdown.classList.remove('open');
        link.setAttribute('aria-expanded', 'false');
      }
    });

    menu.addEventListener('keydown', function(e) {
      if (e.key === 'Escape') {
        dropdown.classList.remove('open');
        link.setAttribute('aria-expanded', 'false');
        link.focus();
      }
    });
  });

  // Single outside-click handler closes all open dropdowns.
  document.addEventListener('click', function(e) {
    dropdowns.forEach(function(dropdown) {
      if (!dropdown.contains(e.target)) {
        dropdown.classList.remove('open');
        var link = dropdown.querySelector(':scope > a');
        if (link) link.setAttribute('aria-expanded', 'false');
      }
    });
  });

  // Language selector: highlight current locale in the dropdown by reading
  // the URL prefix. Purely cosmetic — the links themselves do the routing.
  var langDropdown = document.querySelector('.lang-dropdown');
  if (langDropdown) {
    var path = window.location.pathname;
    var match = path.match(/^\/([a-z]{2}(?:-[A-Z]{2})?)\//);
    var current = match ? match[1] : 'en';
    var label = langDropdown.querySelector(':scope > a');
    if (label) label.textContent = current.toUpperCase();
  }
});
