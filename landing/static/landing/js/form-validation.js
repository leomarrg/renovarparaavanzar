// ==========================================
// FORM VALIDATION MODULE
// Maneja validación de formularios y campos
// ==========================================

(function() {
    'use strict';
    
    // ==========================================
    // DOCTOR FIELDS TOGGLE
    // ==========================================
    
    function initDoctorFieldsToggle() {
        const doctorYes = document.getElementById('doctor_yes');
        const doctorNo = document.getElementById('doctor_no');
        const doctorFields = document.getElementById('doctorFields');
        const yearsInput = document.getElementById('years');
        const specialtyInput = document.getElementById('specialty');
        const serviceLocationInput = document.getElementById('service_location');
        const licensedYes = document.getElementById('licensed_yes');
        const licensedNo = document.getElementById('licensed_no');
        
        if (!doctorYes || !doctorNo) return;
        
        doctorNo.addEventListener('change', function() {
            if (this.checked) {
                if (doctorFields) doctorFields.style.display = 'none';
                
                // Limpiar y deshabilitar campos
                if (yearsInput) {
                    yearsInput.value = '';
                    yearsInput.disabled = true;
                    yearsInput.removeAttribute('required');
                }
                if (specialtyInput) {
                    specialtyInput.value = '';
                    specialtyInput.disabled = true;
                    specialtyInput.removeAttribute('required');
                }
                if (serviceLocationInput) {
                    serviceLocationInput.value = '';
                    serviceLocationInput.disabled = true;
                    serviceLocationInput.removeAttribute('required');
                }
                if (licensedYes) {
                    licensedYes.checked = false;
                    licensedYes.disabled = true;
                    licensedYes.removeAttribute('required');
                }
                if (licensedNo) {
                    licensedNo.checked = false;
                    licensedNo.disabled = true;
                    licensedNo.removeAttribute('required');
                }
            }
        });

        doctorYes.addEventListener('change', function() {
            if (this.checked) {
                if (doctorFields) doctorFields.style.display = 'block';
                
                // Habilitar campos
                if (yearsInput) yearsInput.disabled = false;
                if (specialtyInput) specialtyInput.disabled = false;
                if (serviceLocationInput) serviceLocationInput.disabled = false;
                if (licensedYes) {
                    licensedYes.disabled = false;
                    licensedYes.setAttribute('required', 'required');
                }
                if (licensedNo) licensedNo.disabled = false;
            }
        });
    }
    
    // ==========================================
    // YEARS INPUT VALIDATION
    // ==========================================
    
    function initYearsValidation() {
        const yearsInput = document.getElementById('years');
        
        if (!yearsInput) return;
        
        yearsInput.addEventListener('input', function(e) {
            this.value = this.value.replace(/[^0-9]/g, '');
            if (parseInt(this.value) > 70) {
                this.value = '70';
            }
        });
    }
    
    // ==========================================
    // EMAIL VALIDATION
    // ==========================================
    
    const commonDomains = {
        'gmail.com': ['gmai.com', 'gmial.com', 'gmail.co', 'gmail.cm', 'gmail.con'],
        'hotmail.com': ['hotmai.com', 'hotmial.com', 'hotmail.co', 'hotmail.cm'],
        'yahoo.com': ['yaho.com', 'yahoo.co', 'yahoo.cm', 'yahooo.com'],
        'outlook.com': ['outlok.com', 'outlook.co', 'outlook.cm'],
        'icloud.com': ['iclod.com', 'icloud.co', 'icloud.cm']
    };
    
    function findCorrectDomain(typo) {
        for (const [correct, typos] of Object.entries(commonDomains)) {
            if (typos.includes(typo.toLowerCase())) {
                return correct;
            }
        }
        return null;
    }
    
    function validateEmailDomain(email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        
        if (!email || !email.includes('@')) {
            return null;
        }
        
        const parts = email.split('@');
        if (parts.length !== 2) {
            return { type: 'error', message: 'Formato de email inválido' };
        }
        
        const domain = parts[1].toLowerCase();
        
        if (!domain || domain === '.' || domain.startsWith('.')) {
            return { type: 'error', message: 'El dominio del email está incompleto' };
        }
        
        if (!domain.includes('.')) {
            return { type: 'error', message: 'Falta la extensión del dominio (ej: .com)' };
        }
        
        if (domain.includes('..')) {
            return { type: 'error', message: 'El dominio contiene puntos duplicados' };
        }
        
        const correctDomain = findCorrectDomain(domain);
        if (correctDomain) {
            return { 
                type: 'warning', 
                message: `¿Quisiste decir ${parts[0]}@${correctDomain}?`,
                suggestion: `${parts[0]}@${correctDomain}`
            };
        }
        
        if (emailRegex.test(email)) {
            return { type: 'success', message: '✓ Email válido' };
        }
        
        return null;
    }
    
    function showValidation(result, emailValidation) {
        if (!emailValidation) return;
        
        if (!result) {
            emailValidation.classList.remove('show', 'error', 'warning', 'success');
            return;
        }
        
        emailValidation.innerHTML = result.message;
        
        if (result.suggestion) {
            emailValidation.style.cursor = 'pointer';
            emailValidation.onclick = () => {
                const emailInput = document.getElementById('email');
                if (emailInput) {
                    emailInput.value = result.suggestion;
                    validateEmail();
                }
            };
        } else {
            emailValidation.style.cursor = 'default';
            emailValidation.onclick = null;
        }
        
        emailValidation.classList.remove('error', 'warning', 'success');
        emailValidation.classList.add('show', result.type);
    }
    
    function validateEmail() {
        const emailInput = document.getElementById('email');
        const emailValidation = document.getElementById('emailValidation');
        
        if (!emailInput) return;
        
        const email = emailInput.value;
        const result = validateEmailDomain(email);
        showValidation(result, emailValidation);
    }
    
    function initEmailValidation() {
        const emailInput = document.getElementById('email');
        const emailValidation = document.getElementById('emailValidation');
        let validationTimeout;
        
        if (!emailInput) return;
        
        emailInput.addEventListener('input', (e) => {
            clearTimeout(validationTimeout);
            if (e.target.value.includes('@')) {
                validationTimeout = setTimeout(() => {
                    validateEmail();
                }, 500);
            } else if (emailValidation) {
                emailValidation.classList.remove('show');
            }
        });
        
        emailInput.addEventListener('blur', () => {
            if (emailInput.value) {
                validateEmail();
            }
        });
    }
    
    // ==========================================
    // PHONE FORMATTING
    // ==========================================
    
    function initPhoneFormatting() {
        const phoneInput = document.getElementById('phone');
        
        if (!phoneInput) return;
        
        phoneInput.addEventListener('input', (e) => {
            let value = e.target.value.replace(/\D/g, '');
            if (value.length > 0) {
                if (value.length <= 3) {
                    value = `(${value}`;
                } else if (value.length <= 6) {
                    value = `(${value.slice(0, 3)}) ${value.slice(3)}`;
                } else {
                    value = `(${value.slice(0, 3)}) ${value.slice(3, 6)}-${value.slice(6, 10)}`;
                }
            }
            e.target.value = value;
        });
    }
    
    // ==========================================
    // FORM SUBMIT VALIDATION
    // ==========================================
    
    function initFormSubmitValidation() {
        const registerForm = document.getElementById('registerForm');
        const emailInput = document.getElementById('email');
        
        if (!registerForm || !emailInput) return;
        
        registerForm.addEventListener('submit', (e) => {
            const email = emailInput.value;
            const validation = validateEmailDomain(email);
            
            if (validation && validation.type === 'error') {
                e.preventDefault();
                emailInput.focus();
                const emailValidation = document.getElementById('emailValidation');
                showValidation(validation, emailValidation);
                return false;
            }
            
            if (validation && validation.type === 'warning') {
                const proceed = confirm(`Posible error en el email. ${validation.message}\n\n¿Deseas continuar?`);
                if (!proceed) {
                    e.preventDefault();
                    emailInput.focus();
                    return false;
                }
            }
        });
    }
    
    // ==========================================
    // INITIALIZATION
    // ==========================================
    
    function init() {
        initDoctorFieldsToggle();
        initYearsValidation();
        initEmailValidation();
        initPhoneFormatting();
        initFormSubmitValidation();
    }
    
    // Auto-initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
    
})();