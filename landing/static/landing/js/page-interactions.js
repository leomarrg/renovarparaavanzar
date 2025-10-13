// ==========================================
// PAGE INTERACTIONS MODULE - VERSIÓN ACTUALIZADA
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
    // MOBILE MENU - ACTUALIZADO CON HAMBURGUESA A X
    // ==========================================
    
    function initMobileMenu() {
        const menuToggle = document.getElementById('menuToggle');
        const mobileMenu = document.getElementById('mobileMenu');
        
        if (!menuToggle || !mobileMenu) return;
        
        // Toggle menu con cambio de ícono
        menuToggle.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            
            // Toggle del menú
            mobileMenu.classList.toggle('active');
            
            // Cambiar el ícono de hamburguesa a X
            const span = menuToggle.querySelector('span');
            if (span) {
                if (mobileMenu.classList.contains('active')) {
                    span.textContent = '✕';
                    menuToggle.classList.add('active');
                } else {
                    span.textContent = '☰';
                    menuToggle.classList.remove('active');
                }
            }
        });
        
        // Cerrar menú al hacer click en un enlace
        document.querySelectorAll('.mobile-menu a').forEach(link => {
            link.addEventListener('click', function() {
                mobileMenu.classList.remove('active');
                
                // Volver al ícono de hamburguesa
                const span = menuToggle.querySelector('span');
                if (span) {
                    span.textContent = '☰';
                    menuToggle.classList.remove('active');
                }
            });
        });
        
        // Cerrar menú al hacer click fuera
        document.addEventListener('click', function(e) {
            if (!mobileMenu.contains(e.target) && !menuToggle.contains(e.target)) {
                if (mobileMenu.classList.contains('active')) {
                    mobileMenu.classList.remove('active');
                    
                    // Volver al ícono de hamburguesa
                    const span = menuToggle.querySelector('span');
                    if (span) {
                        span.textContent = '☰';
                        menuToggle.classList.remove('active');
                    }
                }
            }
        });
        
        // Cerrar menú al hacer scroll
        let lastScrollTop = 0;
        window.addEventListener('scroll', function() {
            const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
            
            // Si el scroll es significativo, cerrar el menú
            if (Math.abs(scrollTop - lastScrollTop) > 50) {
                if (mobileMenu.classList.contains('active')) {
                    mobileMenu.classList.remove('active');
                    
                    // Volver al ícono de hamburguesa
                    const span = menuToggle.querySelector('span');
                    if (span) {
                        span.textContent = '☰';
                        menuToggle.classList.remove('active');
                    }
                }
            }
            
            lastScrollTop = scrollTop;
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