// ==========================================
// PAGE INTERACTIONS MODULE
// Maneja loader, menu, scroll y animaciones
// ==========================================

(function() {
    'use strict';
    
    // ==========================================
    // PAGE LOADER
    // ==========================================
    
    function initPageLoader() {
        const pageLoader = document.getElementById('loader');
        
        if (!pageLoader) return;
        
        window.addEventListener('load', function() {
            setTimeout(function() {
                pageLoader.classList.add('hidden');
            }, 500);
        });
    }
    
    // ==========================================
    // MOBILE MENU
    // ==========================================
    
    function initMobileMenu() {
        const menuToggle = document.getElementById('menuToggle');
        const mobileMenu = document.getElementById('mobileMenu');
        
        if (!menuToggle || !mobileMenu) return;
        
        menuToggle.addEventListener('click', function() {
            mobileMenu.classList.toggle('active');
        });
        
        // Close mobile menu when clicking on a link
        document.querySelectorAll('.mobile-menu a').forEach(link => {
            link.addEventListener('click', function() {
                mobileMenu.classList.remove('active');
            });
        });
    }
    
    // ==========================================
    // HEADER SCROLL EFFECT
    // ==========================================
    
    function initHeaderScroll() {
        const header = document.getElementById('header');
        
        if (!header) return;
        
        window.addEventListener('scroll', function() {
            if (window.scrollY > 50) {
                header.classList.add('scrolled');
            } else {
                header.classList.remove('scrolled');
            }
        });
    }
    
    // ==========================================
    // SMOOTH SCROLLING
    // ==========================================
    
    function initSmoothScrolling() {
        const header = document.getElementById('header');
        
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', function (e) {
                e.preventDefault();
                const target = document.querySelector(this.getAttribute('href'));
                
                if (target) {
                    const headerHeight = header ? header.offsetHeight : 0;
                    const targetPosition = target.getBoundingClientRect().top + window.scrollY - headerHeight;
                    
                    window.scrollTo({
                        top: targetPosition,
                        behavior: 'smooth'
                    });
                }
            });
        });
    }
    
    // ==========================================
    // ANIMATE ON SCROLL
    // ==========================================
    
    function initAnimateOnScroll() {
        const observerOptions = {
            threshold: 0.1,
            rootMargin: '0px 0px -100px 0px'
        };
        
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('animated');
                }
            });
        }, observerOptions);
        
        document.querySelectorAll('.animate-on-scroll').forEach(el => {
            observer.observe(el);
        });
    }
    
    // ==========================================
    // INITIALIZATION
    // ==========================================
    
    function init() {
        initPageLoader();
        initMobileMenu();
        initHeaderScroll();
        initSmoothScrolling();
        initAnimateOnScroll();
    }
    
    // Auto-initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
    
})();