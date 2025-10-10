// ===============================================
// ATH MÓVIL PAYMENT INTEGRATION CON DEBUG VISUAL
// ===============================================

// Debug Logger Visual
class VisualDebugger {
    constructor() {
        this.logs = [];
        this.createDebugPanel();
    }

    createDebugPanel() {
        // Crear panel de debug
        const panel = document.createElement('div');
        panel.id = 'ath-debug-panel';
        panel.style.cssText = `
            position: fixed;
            bottom: 20px;
            right: 20px;
            width: 400px;
            max-height: 500px;
            background: rgba(0, 0, 0, 0.95);
            color: #0f0;
            font-family: 'Courier New', monospace;
            font-size: 12px;
            padding: 15px;
            border-radius: 10px;
            z-index: 99999;
            overflow-y: auto;
            box-shadow: 0 4px 20px rgba(0,0,0,0.5);
            border: 2px solid #0f0;
        `;

        // Header
        const header = document.createElement('div');
        header.style.cssText = `
            display: flex;
            justify-content: space-between;
            margin-bottom: 10px;
            padding-bottom: 10px;
            border-bottom: 1px solid #0f0;
        `;
        header.innerHTML = `
            <strong style="color: #0ff;">🔍 ATH MÓVIL DEBUG</strong>
            <button id="clear-debug" style="background: #f00; color: #fff; border: none; padding: 2px 8px; cursor: pointer; border-radius: 3px;">Clear</button>
        `;

        // Logs container
        const logsContainer = document.createElement('div');
        logsContainer.id = 'debug-logs';

        panel.appendChild(header);
        panel.appendChild(logsContainer);
        document.body.appendChild(panel);

        // Clear button
        document.getElementById('clear-debug').addEventListener('click', () => {
            this.logs = [];
            logsContainer.innerHTML = '';
        });
    }

    log(message, type = 'info', data = null) {
        const timestamp = new Date().toLocaleTimeString();
        const logEntry = { timestamp, message, type, data };
        this.logs.push(logEntry);

        const logsContainer = document.getElementById('debug-logs');
        const logElement = document.createElement('div');
        
        let color = '#0f0';
        let icon = 'ℹ️';
        
        switch(type) {
            case 'success':
                color = '#0f0';
                icon = '✅';
                break;
            case 'error':
                color = '#f00';
                icon = '❌';
                break;
            case 'warning':
                color = '#ff0';
                icon = '⚠️';
                break;
            case 'api':
                color = '#0ff';
                icon = '🌐';
                break;
            case 'function':
                color = '#f0f';
                icon = '⚙️';
                break;
        }

        logElement.style.cssText = `
            margin-bottom: 8px;
            padding: 5px;
            border-left: 3px solid ${color};
            background: rgba(255,255,255,0.05);
        `;

        let html = `
            <div style="color: #888; font-size: 10px;">[${timestamp}]</div>
            <div style="color: ${color};">${icon} ${message}</div>
        `;

        if (data) {
            html += `<pre style="color: #aaa; font-size: 10px; margin: 5px 0 0 0; overflow-x: auto;">${JSON.stringify(data, null, 2)}</pre>`;
        }

        logElement.innerHTML = html;
        logsContainer.appendChild(logElement);
        logsContainer.scrollTop = logsContainer.scrollHeight;

        // También log en consola
        console.log(`[ATH] ${message}`, data || '');
    }
}

// Inicializar debugger
const debugger = new VisualDebugger();

// Estado global del pago
let paymentState = {
    selectedAmount: null,
    ecommerceId: null,
    phoneNumber: null,
    checkInterval: null,
    attempts: 0,
    maxAttempts: 120
};

// ===============================================
// INICIALIZACIÓN
// ===============================================

debugger.log('Script cargado', 'success');
debugger.log('Esperando DOMContentLoaded...', 'info');

document.addEventListener('DOMContentLoaded', function() {
    debugger.log('DOM completamente cargado', 'success');
    debugger.log('Iniciando configuración de ATH Móvil...', 'function');
    
    try {
        initializeATHMovil();
        debugger.log('Inicialización exitosa', 'success');
    } catch (error) {
        debugger.log('Error en inicialización', 'error', {
            message: error.message,
            stack: error.stack
        });
    }
});

// ===============================================
// FUNCIÓN PRINCIPAL DE INICIALIZACIÓN
// ===============================================

function initializeATHMovil() {
    debugger.log('→ Ejecutando initializeATHMovil()', 'function');
    
    // Verificar si ATH Móvil está disponible
    if (typeof ATHM_Checkout === 'undefined') {
        debugger.log('ATHM_Checkout NO disponible', 'error');
        return;
    }
    debugger.log('ATHM_Checkout disponible ✓', 'success');

    // Configurar botones de monto
    setupAmountButtons();
    
    // Configurar input personalizado
    setupCustomInput();
    
    // Renderizar botón de ATH Móvil
    renderATHButton();
}

// ===============================================
// CONFIGURACIÓN DE BOTONES DE MONTO
// ===============================================

function setupAmountButtons() {
    debugger.log('→ Ejecutando setupAmountButtons()', 'function');
    
    const amountButtons = document.querySelectorAll('.amount-btn');
    debugger.log(`Encontrados ${amountButtons.length} botones de monto`, 'info');
    
    amountButtons.forEach((btn, index) => {
        const amount = btn.getAttribute('data-amount');
        debugger.log(`Configurando botón #${index + 1}: $${amount}`, 'info');
        
        btn.addEventListener('click', function() {
            handleAmountSelection(this);
        });
    });
}

function handleAmountSelection(button) {
    const amount = parseFloat(button.getAttribute('data-amount'));
    debugger.log(`→ handleAmountSelection() - Monto: $${amount}`, 'function', { amount });
    
    // Remover selección previa
    document.querySelectorAll('.amount-btn').forEach(b => {
        b.classList.remove('active');
    });
    
    // Activar botón seleccionado
    button.classList.add('active');
    
    // Limpiar input personalizado
    const customInput = document.getElementById('customDonationAmount');
    if (customInput) {
        customInput.value = '';
    }
    
    // Actualizar estado
    paymentState.selectedAmount = amount;
    debugger.log('Estado actualizado', 'success', { 
        selectedAmount: paymentState.selectedAmount 
    });
    
    // Mostrar monto seleccionado
    updateSelectedAmountDisplay(amount);
}

// ===============================================
// CONFIGURACIÓN DE INPUT PERSONALIZADO
// ===============================================

function setupCustomInput() {
    debugger.log('→ Ejecutando setupCustomInput()', 'function');
    
    const customInput = document.getElementById('customDonationAmount');
    if (!customInput) {
        debugger.log('Input personalizado NO encontrado', 'warning');
        return;
    }
    
    debugger.log('Input personalizado encontrado ✓', 'success');
    
    customInput.addEventListener('input', function() {
        const value = parseFloat(this.value);
        debugger.log(`Input personalizado: $${value}`, 'info');
        
        if (value > 0) {
            // Desactivar botones predefinidos
            document.querySelectorAll('.amount-btn').forEach(btn => {
                btn.classList.remove('active');
            });
            
            paymentState.selectedAmount = value;
            updateSelectedAmountDisplay(value);
            debugger.log('Monto personalizado establecido', 'success', { amount: value });
        }
    });
}

// ===============================================
// ACTUALIZAR DISPLAY DE MONTO SELECCIONADO
// ===============================================

function updateSelectedAmountDisplay(amount) {
    debugger.log('→ updateSelectedAmountDisplay()', 'function', { amount });
    
    const displayDiv = document.getElementById('selectedAmountDisplay');
    const valueSpan = document.getElementById('selectedAmountValue');
    
    if (displayDiv && valueSpan) {
        valueSpan.textContent = amount.toFixed(2);
        displayDiv.style.display = 'block';
        debugger.log('Display actualizado y visible', 'success');
    }
}

// ===============================================
// RENDERIZAR BOTÓN DE ATH MÓVIL
// ===============================================

function renderATHButton() {
    debugger.log('→ Ejecutando renderATHButton()', 'function');
    
    const container = document.getElementById('ATHMovil_Checkout_Button_payment');
    if (!container) {
        debugger.log('Container del botón NO encontrado', 'error');
        return;
    }
    
    debugger.log('Container encontrado ✓', 'success');
    
    try {
        const buttonInstance = new ATHM_Checkout({
            publicToken: "a937f2e32a4e35ebd2c2850d204fd4dc4b515763",
            timeout: 600,
            theme: "btn",
            lang: "es",
            total: 0
        });
        
        debugger.log('Instancia de ATHM_Checkout creada', 'success');
        
        const buttonElement = buttonInstance.getButton();
        container.innerHTML = '';
        container.appendChild(buttonElement);
        
        debugger.log('Botón renderizado en el DOM', 'success');
        
        // Configurar evento onClick
        buttonElement.addEventListener('click', handleATHButtonClick);
        debugger.log('Event listener onClick configurado', 'success');
        
    } catch (error) {
        debugger.log('Error al renderizar botón', 'error', {
            message: error.message,
            stack: error.stack
        });
    }
}

// ===============================================
// MANEJO DE CLICK EN BOTÓN ATH MÓVIL
// ===============================================

function handleATHButtonClick(e) {
    e.preventDefault();
    debugger.log('→ handleATHButtonClick() - Click detectado', 'function');
    
    // Validar monto
    if (!paymentState.selectedAmount || paymentState.selectedAmount <= 0) {
        debugger.log('Monto no seleccionado', 'warning');
        showPaymentStatus('Por favor selecciona un monto de donación', 'error');
        return;
    }
    
    debugger.log('Validación de monto exitosa', 'success', {
        amount: paymentState.selectedAmount
    });
    
    // Iniciar proceso de pago
    initiatePayment();
}

// ===============================================
// INICIAR PROCESO DE PAGO
// ===============================================

async function initiatePayment() {
    debugger.log('→ initiatePayment() - Iniciando proceso...', 'function');
    
    showPaymentStatus('Procesando tu solicitud...', 'processing');
    
    try {
        debugger.log('Preparando datos del pago', 'info', {
            amount: paymentState.selectedAmount
        });
        
        const paymentData = {
            amount: paymentState.selectedAmount,
            metadata1: 'Donacion Campaña',
            metadata2: 'RenovarParaAvanzar'
        };
        
        debugger.log('Llamando a API: /api/ath/payment/', 'api', paymentData);
        
        const response = await fetch('/api/ath/payment/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(paymentData)
        });
        
        debugger.log('Respuesta recibida', 'api', {
            status: response.status,
            ok: response.ok
        });
        
        const data = await response.json();
        debugger.log('Datos parseados', 'success', data);
        
        if (data.status === 'success' && data.data) {
            paymentState.ecommerceId = data.data.ecommerceId;
            debugger.log('EcommerceId obtenido', 'success', {
                ecommerceId: paymentState.ecommerceId
            });
            
            requestPhoneNumber();
        } else {
            throw new Error(data.message || 'Error al crear el pago');
        }
        
    } catch (error) {
        debugger.log('Error en initiatePayment', 'error', {
            message: error.message,
            stack: error.stack
        });
        showPaymentStatus('Error al procesar el pago. Intenta nuevamente.', 'error');
    }
}

// ===============================================
// SOLICITAR NÚMERO DE TELÉFONO
// ===============================================

function requestPhoneNumber() {
    debugger.log('→ requestPhoneNumber()', 'function');
    
    const phoneNumber = prompt('Ingresa tu número de teléfono ATH Móvil\n(Ej: 7871234567)');
    
    if (!phoneNumber) {
        debugger.log('Usuario canceló entrada de teléfono', 'warning');
        showPaymentStatus('Pago cancelado', 'error');
        return;
    }
    
    const cleanPhone = phoneNumber.replace(/\D/g, '');
    debugger.log('Teléfono ingresado', 'info', {
        original: phoneNumber,
        cleaned: cleanPhone,
        length: cleanPhone.length
    });
    
    if (cleanPhone.length !== 10) {
        debugger.log('Formato de teléfono inválido', 'warning');
        alert('Por favor ingresa un número de teléfono válido (10 dígitos)');
        requestPhoneNumber();
        return;
    }
    
    paymentState.phoneNumber = cleanPhone;
    debugger.log('Teléfono validado', 'success', {
        phoneNumber: cleanPhone
    });
    
    updatePhoneNumber(cleanPhone);
}

// ===============================================
// ACTUALIZAR NÚMERO DE TELÉFONO
// ===============================================

async function updatePhoneNumber(phoneNumber) {
    debugger.log('→ updatePhoneNumber()', 'function', { phoneNumber });
    
    try {
        const updateData = {
            ecommerceId: paymentState.ecommerceId,
            phoneNumber: phoneNumber
        };
        
        debugger.log('Llamando a API: /api/ath/update-phone/', 'api', updateData);
        
        const response = await fetch('/api/ath/update-phone/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(updateData)
        });
        
        debugger.log('Respuesta recibida', 'api', {
            status: response.status
        });
        
        const data = await response.json();
        debugger.log('Datos parseados', 'success', data);
        
        if (data.status === 'success') {
            debugger.log('Teléfono actualizado exitosamente', 'success');
            showPaymentStatus('Abre tu app ATH Móvil y confirma el pago', 'processing');
            startPaymentCheck();
        } else {
            throw new Error('Error al actualizar teléfono');
        }
        
    } catch (error) {
        debugger.log('Error en updatePhoneNumber', 'error', {
            message: error.message
        });
        showPaymentStatus('Error al procesar. Intenta nuevamente.', 'error');
    }
}

// ===============================================
// INICIAR VERIFICACIÓN DE PAGO
// ===============================================

function startPaymentCheck() {
    debugger.log('→ startPaymentCheck() - Iniciando polling...', 'function');
    
    paymentState.attempts = 0;
    
    paymentState.checkInterval = setInterval(() => {
        paymentState.attempts++;
        debugger.log(`Intento de verificación #${paymentState.attempts}/${paymentState.maxAttempts}`, 'info');
        
        checkPaymentStatus();
        
        if (paymentState.attempts >= paymentState.maxAttempts) {
            debugger.log('Máximo de intentos alcanzado', 'warning');
            clearInterval(paymentState.checkInterval);
            showPaymentStatus('Tiempo de espera agotado. Verifica tu app ATH Móvil.', 'error');
        }
    }, 3000);
    
    debugger.log('Polling configurado (cada 3 segundos)', 'success');
}

// ===============================================
// VERIFICAR ESTADO DEL PAGO
// ===============================================

async function checkPaymentStatus() {
    debugger.log('→ checkPaymentStatus()', 'function');
    
    try {
        const checkData = {
            ecommerceId: paymentState.ecommerceId
        };
        
        const response = await fetch('/api/ath/find-payment/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(checkData)
        });
        
        const data = await response.json();
        
        if (data.status === 'completed') {
            debugger.log('¡Pago completado!', 'success', data);
            clearInterval(paymentState.checkInterval);
            handlePaymentSuccess(data);
        } else if (data.status === 'cancelled' || data.status === 'expired') {
            debugger.log('Pago cancelado/expirado', 'warning', data);
            clearInterval(paymentState.checkInterval);
            showPaymentStatus('El pago fue cancelado o expiró', 'error');
        }
        
    } catch (error) {
        debugger.log('Error en checkPaymentStatus', 'error', {
            message: error.message
        });
    }
}

// ===============================================
// MANEJAR PAGO EXITOSO
// ===============================================

function handlePaymentSuccess(data) {
    debugger.log('→ handlePaymentSuccess()', 'function', data);
    
    showPaymentStatus('¡Donación completada exitosamente! Gracias por tu apoyo.', 'success');
    
    setTimeout(() => {
        debugger.log('Redirigiendo a confirmación...', 'info');
        window.location.href = '/donacion-confirmada/';
    }, 3000);
}

// ===============================================
// MOSTRAR ESTADO DEL PAGO
// ===============================================

function showPaymentStatus(message, type) {
    debugger.log(`→ showPaymentStatus("${message}", "${type}")`, 'function');
    
    const statusDiv = document.getElementById('paymentStatusDonation');
    if (!statusDiv) {
        debugger.log('StatusDiv NO encontrado', 'warning');
        return;
    }
    
    statusDiv.className = `payment-status ${type}`;
    
    let icon = '';
    switch(type) {
        case 'success':
            icon = '✅';
            break;
        case 'error':
            icon = '❌';
            break;
        case 'processing':
            icon = '⏳';
            break;
    }
    
    statusDiv.innerHTML = `
        <div style="font-size: 2rem; margin-bottom: 10px;">${icon}</div>
        <div style="font-size: 1.1rem; font-weight: 600;">${message}</div>
    `;
    
    statusDiv.style.display = 'block';
    debugger.log('Estado mostrado en UI', 'success');
}

debugger.log('Script completamente cargado ✓', 'success');