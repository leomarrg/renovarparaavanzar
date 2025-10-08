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
            .then(response => response.json())
            .then(data => {
                const countdownEl = document.getElementById('countdown');
                if (!countdownEl) return;
                
                if (data.ended) {
                    countdownEl.innerHTML = `
                        <h3 style="color: var(--teal-primary);">${data.message}</h3>
                    `;
                } else {
                    const days = document.getElementById('days');
                    const hours = document.getElementById('hours');
                    const minutes = document.getElementById('minutes');
                    const seconds = document.getElementById('seconds');
                    
                    if (days) days.textContent = String(data.days).padStart(2, '0');
                    if (hours) hours.textContent = String(data.hours).padStart(2, '0');
                    if (minutes) minutes.textContent = String(data.minutes).padStart(2, '0');
                    if (seconds) seconds.textContent = String(data.seconds).padStart(2, '0');
                }
            })
            .catch(error => console.error('Error updating countdown:', error));
    }
    
    // ==========================================
    // INITIALIZATION
    // ==========================================
    
    function init() {
        const countdownEl = document.getElementById('countdown');
        
        if (!countdownEl) return;
        
        // La URL debe ser pasada desde Django
        const countdownUrl = countdownEl.dataset.countdownUrl;
        
        if (countdownUrl) {
            // Update countdown every second
            setInterval(() => updateCountdown(countdownUrl), 1000);
        }
    }
    
    // Auto-initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
    
})();