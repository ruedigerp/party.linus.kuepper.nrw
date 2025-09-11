document.addEventListener('DOMContentLoaded', function() {
    const burgerMenu = document.getElementById('burgerMenu');
    const navMenu = document.getElementById('navMenu');
    const menuOverlay = document.getElementById('menuOverlay');
    
    // Burger Menu Toggle
    if (burgerMenu) {
        burgerMenu.addEventListener('click', function() {
            this.classList.toggle('active');
            navMenu.classList.toggle('active');
            menuOverlay.classList.toggle('active');
        });
    }
    
    // Overlay schließt Menü
    if (menuOverlay) {
        menuOverlay.addEventListener('click', function() {
            burgerMenu.classList.remove('active');
            navMenu.classList.remove('active');
            this.classList.remove('active');
        });
    }
    
    // Mobile Dropdown Toggle
    const dropdownLinks = document.querySelectorAll('.has-dropdown > a');
    
    dropdownLinks.forEach(function(link) {
        link.addEventListener('click', function(e) {
            // Nur auf Mobile
            if (window.innerWidth <= 768) {
                const href = this.getAttribute('href');
                
                // Wenn der Link eine echte URL hat (nicht # oder leer), dann navigiere normal
                if (href && href !== '#' && href.trim() !== '') {
                    // Lasse das normale Klickverhalten zu (Navigation zur Seite)
                    return;
                }

                // Ansonsten verhindere Navigation und zeige Dropdown
                e.preventDefault();
                e.stopPropagation();
                
                const parentLi = this.parentElement;
                const allDropdowns = document.querySelectorAll('.has-dropdown');
                
                // Schließe alle anderen
                allDropdowns.forEach(function(dropdown) {
                    if (dropdown !== parentLi) {
                        dropdown.classList.remove('active');
                    }
                });
                
                // Toggle current
                parentLi.classList.toggle('active');
            }
        });
    });
});