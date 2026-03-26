document.querySelectorAll('.blog-filters button').forEach(function(btn) {
  btn.addEventListener('click', function() {
    document.querySelectorAll('.blog-filters button').forEach(function(b) { b.classList.remove('active'); });
    btn.classList.add('active');
    var filter = btn.getAttribute('data-filter');
    document.querySelectorAll('.blog-list li').forEach(function(li) {
      li.style.display = (filter === 'all' || li.getAttribute('data-cat') === filter) ? '' : 'none';
    });
  });
});
