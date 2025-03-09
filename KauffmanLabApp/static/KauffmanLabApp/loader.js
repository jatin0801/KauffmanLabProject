document.addEventListener('DOMContentLoaded', function() {
    const loader = document.getElementById('loader-wrapper');
    
    // Hide loader when page is loaded
    window.addEventListener('load', function() {
        loader.classList.add('loaded');
        setTimeout(function() {
            loader.style.display = 'none';
        }, 300);
    });
    
    // Show loader when clicking on internal links
    document.addEventListener('click', function(event) {
        // Check if clicked element is a link
        let target = event.target;
        while (target && target.tagName !== 'A') {
            target = target.parentNode;
            if (!target) return;
        }
        
        // If it's an internal link (not external or target="_blank")
        if (target && 
            target.hostname === window.location.hostname && 
            !target.hasAttribute('download') && 
            target.getAttribute('target') !== '_blank') {
            loader.classList.remove('loaded');
            loader.style.display = 'flex';
        }
    });
    
    // Show loader for form submissions
    document.addEventListener('submit', function(event) {
        loader.classList.remove('loaded');
        loader.style.display = 'flex';
    });
    
    // Intercept AJAX requests (jQuery)
    if (typeof jQuery !== 'undefined') {
        $(document).ajaxStart(function() {
            loader.classList.remove('loaded');
            loader.style.display = 'flex';
        });
        
        $(document).ajaxStop(function() {
            loader.classList.add('loaded');
            setTimeout(function() {
                loader.style.display = 'none';
            }, 300);
        });
    }
    // Handle browser back/forward navigation
    window.addEventListener('pageshow', function(event) {
      // This event fires when page is shown, including from back/forward cache
      // The persisted property is true if the page was restored from cache
      if (event.persisted) {
          // Hide loader if coming from back/forward navigation
          loader.classList.add('loaded');
          setTimeout(function() {
              loader.style.display = 'none';
          }, 300);
      }
  });
  
  // Listen for history navigation events
  window.addEventListener('popstate', function() {
      // Hide loader when navigating with browser back/forward buttons
      loader.classList.add('loaded');
      setTimeout(function() {
          loader.style.display = 'none';
      }, 300);
  });
});