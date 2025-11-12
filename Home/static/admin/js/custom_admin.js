// Custom admin JavaScript
document.addEventListener('DOMContentLoaded', function() {
    // Add smooth animations to admin elements
    const tables = document.querySelectorAll('table');
    tables.forEach(table => {
        table.style.transition = 'all 0.3s ease';
    });
    
    // Add loading animation to forms
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function() {
            const submitBtn = form.querySelector('input[type="submit"]');
            if (submitBtn) {
                submitBtn.value = 'Processing...';
                submitBtn.style.opacity = '0.7';
            }
        });
    });
    
    // Enhanced search functionality
    const searchInput = document.querySelector('#searchbar');
    if (searchInput) {
        searchInput.addEventListener('focus', function() {
            this.style.borderColor = '#007bff';
            this.style.boxShadow = '0 0 0 0.2rem rgba(0,123,255,.25)';
        });
        
        searchInput.addEventListener('blur', function() {
            this.style.borderColor = '';
            this.style.boxShadow = '';
        });
    }
    
    // Add tooltips to action buttons
    const actionBtns = document.querySelectorAll('.button');
    actionBtns.forEach(btn => {
        btn.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-2px)';
        });
        
        btn.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
        });
    });
});