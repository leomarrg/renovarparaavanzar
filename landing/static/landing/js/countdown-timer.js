// ==========================================
// COUNTDOWN TIMER MODULE
// Maneja el temporizador de cuenta regresiva
// ==========================================

(function() {
    'use strict';
    
    // ==========================================
    // COUNTDOWN UPDATE FUNCTION
    // ==========================================
    
    function updateCountdown(countdownUrl) {
        fetch(countdownUrl)
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(data => {
                if (data.ended) {
                    // Si las elecciones terminaron
                    const countdownEl = document.getElementById('countdown');
                    if (countdownEl) {
                        countdownEl.innerHTML = `
                            <h3 style="color: var(--teal-primary);">${data.message}</h3>
                        `;
                    }
                } else {
                    // Actualizar countdown principal (footer)
                    const days = document.getElementById('days');
                    const hours = document.getElementById('hours');
                    const minutes = document.getElementById('minutes');
                    const seconds = document.getElementById('seconds');
                    
                    if (days) days.textContent = String(data.days).padStart(2, '0');
                    if (hours) hours.textContent = String(data.hours).padStart(2, '0');
                    if (minutes) minutes.textContent = String(data.minutes).padStart(2, '0');
                    if (seconds) seconds.textContent = String(data.seconds).padStart(2, '0');
                    
                    // Actualizar countdown mini si existe
                    const daysMini = document.getElementById('days-mini');
                    const hoursMini = document.getElementById('hours-mini');
                    const minutesMini = document.getElementById('minutes-mini');
                    const secondsMini = document.getElementById('seconds-mini');
                    
                    if (daysMini) daysMini.textContent = String(data.days).padStart(2, '0');
                    if (hoursMini) hoursMini.textContent = String(data.hours).padStart(2, '0');
                    if (minutesMini) minutesMini.textContent = String(data.minutes).padStart(2, '0');
                    if (secondsMini) secondsMini.textContent = String(data.seconds).padStart(2, '0');
                }
            })
            .catch(error => {
                console.error('Error updating countdown:', error);
                // Opcional: mostrar mensaje de error al usuario
            });
    }
    
    // ==========================================
    // INITIALIZATION
    // ==========================================
    
    function init() {
        const countdownEl = document.getElementById('countdown');
        
        if (!countdownEl) {
            console.warn('Countdown element not found');
            return;
        }
        
        const countdownUrl = countdownEl.dataset.countdownUrl;
        
        if (!countdownUrl) {
            console.error('Countdown URL not defined. Add data-countdown-url attribute to countdown element.');
            return;
        }
        
        // Actualizar inmediatamente
        updateCountdown(countdownUrl);
        
        // Actualizar cada segundo
        setInterval(() => updateCountdown(countdownUrl), 1000);
    }
    
    // Auto-initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
    
})();