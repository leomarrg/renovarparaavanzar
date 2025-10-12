// ==========================================
// MESSAGES HANDLER MODULE
// Maneja mensajes de Django (success, error, etc.)
// ==========================================

(function() {
    'use strict';
    
    // ==========================================
    // MESSAGE DISPLAY FUNCTIONS
    // ==========================================
    
    function showSuccessMessage(message, duration = 30000) {
        const successMsg = document.createElement('div');
        successMsg.className = 'success-message show';
        
        let timeLeft = duration / 1000;
        const timeDisplay = document.createElement('div');
        timeDisplay.className = 'time-remaining';
        timeDisplay.textContent = `Este mensaje se ocultará en ${timeLeft} segundos`;
        
        successMsg.innerHTML = `
            <i class="fas fa-check-circle"></i>
            <p>${message}</p>
        `;
        successMsg.appendChild(timeDisplay);
        
        const registerForm = document.getElementById('registerForm');
        if (registerForm) {
            registerForm.parentElement.insertBefore(successMsg, registerForm);
            
            setTimeout(() => {
                successMsg.scrollIntoView({ behavior: 'smooth', block: 'center' });
            }, 100);
            
            const countdown = setInterval(() => {
                timeLeft--;
                if (timeLeft > 0) {
                    timeDisplay.textContent = `Este mensaje se ocultará en ${timeLeft} segundos`;
                } else {
                    clearInterval(countdown);
                }
            }, 1000);
            
            setTimeout(() => {
                successMsg.classList.remove('show');
                setTimeout(() => successMsg.remove(), 500);
            }, duration);
        }
    }
    
    function showErrorMessage(message) {
        alert(message);
    }
    
    function showInfoMessage(message) {
        alert(message);
    }
    
    // ==========================================
    // PROCESS DJANGO MESSAGES
    // ==========================================
    
    function processDjangoMessages() {
        // Este objeto será inyectado por Django mediante el template
        if (typeof window.djangoMessages === 'undefined') {
            return;
        }
        
        window.djangoMessages.forEach(msg => {
            switch(msg.level) {
                case 'success':
                    showSuccessMessage(msg.message);
                    break;
                case 'error':
                    showErrorMessage(msg.message);
                    break;
                case 'info':
                    showInfoMessage(msg.message);
                    break;
                case 'warning':
                    showInfoMessage(msg.message);
                    break;
                default:
                    console.log('Mensaje:', msg.message);
            }
        });
    }
    
    // ==========================================
    // INITIALIZATION
    // ==========================================
    
    function init() {
        processDjangoMessages();
    }
    
    // Auto-initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
    
})();