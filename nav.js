document.addEventListener('DOMContentLoaded', function() {
  var hamburger = document.querySelector('.nav-hamburger');
  var navLinks = document.querySelector('.nav-links');
  var dropdown = document.querySelector('.nav-dropdown');
  var dropdownLink = dropdown ? dropdown.querySelector(':scope > a') : null;

  if (hamburger && navLinks) {
    hamburger.addEventListener('click', function() {
      navLinks.classList.toggle('open');
      hamburger.textContent = navLinks.classList.contains('open') ? '\u2715' : '\u2630';
    });
  }

  // Mobile: toggle dropdown on tap
  if (dropdownLink && window.innerWidth <= 700) {
    dropdownLink.addEventListener('click', function(e) {
      if (window.innerWidth <= 700) {
        e.preventDefault();
        dropdown.classList.toggle('open');
      }
    });
  }
});
