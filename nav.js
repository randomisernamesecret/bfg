document.addEventListener('DOMContentLoaded', function() {
  var hamburger = document.querySelector('.nav-hamburger');
  var navLinks = document.querySelector('.nav-links');
  var dropdown = document.querySelector('.nav-dropdown');
  var dropdownLink = dropdown ? dropdown.querySelector(':scope > a') : null;
  var dropdownMenu = dropdown ? dropdown.querySelector('.nav-dropdown-menu') : null;

  // Hamburger toggle
  if (hamburger && navLinks) {
    hamburger.setAttribute('aria-expanded', 'false');
    hamburger.addEventListener('click', function() {
      var isOpen = navLinks.classList.toggle('open');
      hamburger.textContent = isOpen ? '\u2715' : '\u2630';
      hamburger.setAttribute('aria-expanded', isOpen ? 'true' : 'false');
    });
  }

  // Dropdown: works on click for both mobile and desktop (not just hover)
  if (dropdownLink && dropdown) {
    dropdownLink.setAttribute('aria-expanded', 'false');
    dropdownLink.setAttribute('aria-haspopup', 'true');

    dropdownLink.addEventListener('click', function(e) {
      e.preventDefault();
      var isOpen = dropdown.classList.toggle('open');
      dropdownLink.setAttribute('aria-expanded', isOpen ? 'true' : 'false');
    });

    // Keyboard: Enter/Space opens, Escape closes
    dropdownLink.addEventListener('keydown', function(e) {
      if (e.key === 'Enter' || e.key === ' ') {
        e.preventDefault();
        var isOpen = dropdown.classList.toggle('open');
        dropdownLink.setAttribute('aria-expanded', isOpen ? 'true' : 'false');
        if (isOpen && dropdownMenu) {
          var first = dropdownMenu.querySelector('a');
          if (first) first.focus();
        }
      }
      if (e.key === 'Escape') {
        dropdown.classList.remove('open');
        dropdownLink.setAttribute('aria-expanded', 'false');
      }
    });

    // Close dropdown when clicking outside
    document.addEventListener('click', function(e) {
      if (!dropdown.contains(e.target)) {
        dropdown.classList.remove('open');
        dropdownLink.setAttribute('aria-expanded', 'false');
      }
    });

    // Escape key closes from anywhere inside dropdown
    if (dropdownMenu) {
      dropdownMenu.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
          dropdown.classList.remove('open');
          dropdownLink.setAttribute('aria-expanded', 'false');
          dropdownLink.focus();
        }
      });
    }
  }
});
