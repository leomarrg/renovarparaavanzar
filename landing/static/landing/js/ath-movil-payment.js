// ===============================================
// ATH MÓVIL PAYMENT - IMPLEMENTACIÓN CORRECTA
// Siguiendo la documentación oficial de ATH Móvil
// ===============================================

// Debug Logger Visual
class VisualDebugger {
    constructor() {
        this.logs = [];
        this.createDebugPanel();
    }

    createDebugPanel() {
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

        const logsContainer = document.createElement('div');
        logsContainer.id = 'debug-logs';

        panel.appendChild(header);
        panel.appendChild(logsContainer);
        document.body.appendChild(panel);

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
            case 'ath':
                color = '#0ff';
                icon = '🏦';
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

        console.log(`[ATH] ${message}`, data || '');
    }
}

// Inicializar debugger
const debugger = new VisualDebugger();

// Estado global
let currentAmount = 0;
let athButtonInstance = null;

debugger.log('Script cargado', 'success');
debugger.log('Esperando DOMContentLoaded...', 'info');

// ===============================================
// INICIALIZACIÓN AL CARGAR LA PÁGINA
// ===============================================

document.addEventListener('DOMContentLoaded', function() {
    debugger.log('DOM completamente cargado', 'success');
    
    // Verificar disponibilidad de ATH Móvil
    if (typeof ATHM_Checkout === 'undefined') {
        debugger.log('❌ ATHM_Checkout NO disponible', 'error');
        debugger.log('Verifica que athmovil_base.js esté cargado', 'warning');
        return;
    }
    
    debugger.log('✅ ATHM_Checkout disponible', 'success');
    
    try {
        initializePaymentSystem();
        debugger.log('Sistema de pagos inicializado', 'success');
    } catch (error) {
        debugger.log('Error en inicialización', 'error', {
            message: error.message,
            stack: error.stack
        });
    }
});

// ===============================================
// INICIALIZAR SISTEMA DE PAGOS
// ===============================================

function initializePaymentSystem() {
    debugger.log('→ initializePaymentSystem()', 'function');
    
    // Configurar botones de monto predefinido
    setupAmountButtons();
    
    // Configurar input de monto personalizado
    setupCustomAmountInput();
    
    // Crear botón ATH inicial (deshabilitado hasta seleccionar monto)
    debugger.log('Botón ATH se creará al seleccionar monto', 'info');
}

// ===============================================
// CONFIGURAR BOTONES DE MONTO
// ===============================================

function setupAmountButtons() {
    debugger.log('→ setupAmountButtons()', 'function');
    
    const amountButtons = document.querySelectorAll('.amount-btn');
    debugger.log(`Encontrados ${amountButtons.length} botones de monto`, 'info');
    
    amountButtons.forEach((btn, index) => {
        const amount = parseFloat(btn.getAttribute('data-amount'));
        
        btn.addEventListener('click', function() {
            debugger.log(`Click en botón $${amount}`, 'info');
            
            // Remover selección previa
            document.querySelectorAll('.amount-btn').forEach(b => {
                b.classList.remove('active');
            });
            
            // Activar botón seleccionado
            this.classList.add('active');
            
            // Limpiar input personalizado
            const customInput = document.getElementById('customDonationAmount');
            if (customInput) {
                customInput.value = '';
            }
            
            // Actualizar monto y recrear botón ATH
            selectAmount(amount);
        });
    });
}

// ===============================================
// CONFIGURAR INPUT PERSONALIZADO
// ===============================================

function setupCustomAmountInput() {
    debugger.log('→ setupCustomAmountInput()', 'function');
    
    const customInput = document.getElementById('customDonationAmount');
    if (!customInput) {
        debugger.log('Input personalizado NO encontrado', 'warning');
        return;
    }
    
    customInput.addEventListener('input', function() {
        const value = parseFloat(this.value);
        
        if (value > 0) {
            debugger.log(`Input personalizado: $${value}`, 'info');
            
            // Desactivar botones predefinidos
            document.querySelectorAll('.amount-btn').forEach(btn => {
                btn.classList.remove('active');
            });
            
            // Actualizar monto
            selectAmount(value);
        }
    });
}

// ===============================================
// SELECCIONAR MONTO Y ACTUALIZAR BOTÓN ATH
// ===============================================

function selectAmount(amount) {
    debugger.log(`→ selectAmount($${amount})`, 'function');
    
    if (amount <= 0) {
        debugger.log('Monto inválido', 'error');
        return;
    }
    
    if (amount > 1500) {
        debugger.log('Monto excede límite de ATH ($1,500)', 'warning');
        showPaymentStatus('El monto máximo es $1,500', 'error');
        return;
    }
    
    currentAmount = amount;
    debugger.log('Monto actualizado', 'success', { currentAmount });
    
    // Mostrar monto seleccionado
    updateSelectedAmountDisplay(amount);
    
    // Recrear botón ATH con el nuevo monto
    createATHButton(amount);
}

// ===============================================
// ACTUALIZAR DISPLAY DE MONTO
// ===============================================

function updateSelectedAmountDisplay(amount) {
    debugger.log('→ updateSelectedAmountDisplay()', 'function');
    
    const displayDiv = document.getElementById('selectedAmountDisplay');
    const valueSpan = document.getElementById('selectedAmountValue');
    
    if (displayDiv && valueSpan) {
        valueSpan.textContent = amount.toFixed(2);
        displayDiv.style.display = 'block';
        debugger.log('Display actualizado', 'success');
    }
}

// ===============================================
// CREAR/RECREAR BOTÓN ATH MÓVIL
// ===============================================

function createATHButton(amount) {
    debugger.log('→ createATHButton()', 'function', { amount });
    
    const container = document.getElementById('ATHMovil_Checkout_Button_payment');
    if (!container) {
        debugger.log('Container NO encontrado', 'error');
        return;
    }
    
    // Limpiar contenedor
    container.innerHTML = '';
    debugger.log('Container limpiado', 'info');
    
    try {
        // Crear nueva instancia con el monto correcto
        athButtonInstance = new ATHM_Checkout({
            env: 'production',
            publicToken: 'a937f2e32a4e35ebd2c2850d204fd4dc4b515763',
            timeout: 600,
            theme: 'btn',
            lang: 'es',
            total: amount,
            subtotal: amount,
            tax: 0,
            metadata1: 'Donacion Campaña',
            metadata2: 'RenovarParaAvanzar',
            items: [{
                name: 'Donación Campaña',
                description: 'Apoyo a Renovar para Avanzar',
                quantity: 1,
                price: amount,
                tax: 0,
                metadata: 'Donacion'
            }]
        });
        
        debugger.log('Instancia ATHM_Checkout creada', 'ath', {
            amount: amount,
            publicToken: 'a937f2e...c4b515763'
        });
        
        // Obtener y agregar botón al DOM
        const buttonElement = athButtonInstance.getButton();
        container.appendChild(buttonElement);
        
        debugger.log('✅ Botón ATH renderizado correctamente', 'success');
        debugger.log('ATH manejará el flujo completo automáticamente', 'ath');
        
    } catch (error) {
        debugger.log('Error al crear botón ATH', 'error', {
            message: error.message,
            stack: error.stack
        });
        showPaymentStatus('Error al cargar el botón de pago', 'error');
    }
}

// ===============================================
// CALLBACKS REQUERIDOS POR ATH MÓVIL
// Estas funciones son llamadas automáticamente por ATH
// ===============================================

/**
 * authorizationATHM - Llamada cuando el pago se completa exitosamente
 */
async function authorizationATHM() {
    debugger.log('🎉 authorizationATHM() llamado por ATH', 'ath');
    debugger.log('El usuario completó el pago exitosamente', 'success');
    
    try {
        // Obtener datos de la transacción
        const response = await authorization();
        
        debugger.log('Respuesta de authorization()', 'ath', response);
        
        if (response.status === 'success') {
            const data = response.data;
            
            debugger.log('✅ Pago completado', 'success', {
                referenceNumber: data.referenceNumber,
                total: data.total,
                ecommerceStatus: data.ecommerceStatus
            });
            
            // Mostrar mensaje de éxito
            showPaymentStatus(
                `¡Donación de $${data.total} completada exitosamente! Gracias por tu apoyo.`,
                'success'
            );
            
            // Opcional: Guardar en tu backend
            try {
                await saveDonationToBackend(data);
            } catch (error) {
                debugger.log('Error al guardar en backend (no crítico)', 'warning', error);
            }
            
            // Redirigir a página de confirmación después de 3 segundos
            debugger.log('Redirigiendo en 3 segundos...', 'info');
            setTimeout(() => {
                window.location.href = '/donacion-confirmada/';
            }, 3000);
            
        } else {
            throw new Error('Respuesta de pago no exitosa');
        }
        
    } catch (error) {
        debugger.log('Error en authorizationATHM', 'error', {
            message: error.message,
            stack: error.stack
        });
        showPaymentStatus('Error al procesar el pago completado', 'error');
    }
}

/**
 * cancelATHM - Llamada cuando el usuario cancela el pago
 */
async function cancelATHM() {
    debugger.log('❌ cancelATHM() llamado por ATH', 'ath');
    debugger.log('El usuario canceló el pago', 'warning');
    
    try {
        const response = await findPaymentATHM();
        
        debugger.log('Respuesta de findPaymentATHM()', 'ath', response);
        
        showPaymentStatus(
            'El pago fue cancelado. Puedes intentar nuevamente.',
            'error'
        );
        
        // Opcional: Log en backend
        console.log('Pago cancelado:', response);
        
    } catch (error) {
        debugger.log('Error en cancelATHM', 'error', error);
    }
}

/**
 * expiredATHM - Llamada cuando el pago expira por timeout
 */
async function expiredATHM() {
    debugger.log('⏰ expiredATHM() llamado por ATH', 'ath');
    debugger.log('El pago expiró por timeout', 'warning');
    
    try {
        const response = await findPaymentATHM();
        
        debugger.log('Respuesta de findPaymentATHM()', 'ath', response);
        
        showPaymentStatus(
            'El tiempo para completar el pago expiró. Por favor intenta nuevamente.',
            'error'
        );
        
        // Opcional: Log en backend
        console.log('Pago expirado:', response);
        
    } catch (error) {
        debugger.log('Error en expiredATHM', 'error', error);
    }
}

// ===============================================
// FUNCIONES AUXILIARES
// ===============================================

/**
 * Mostrar estado del pago en la UI
 */
function showPaymentStatus(message, type) {
    debugger.log(`→ showPaymentStatus("${type}")`, 'function');
    
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

/**
 * Guardar donación en backend (opcional)
 */
async function saveDonationToBackend(paymentData) {
    debugger.log('→ saveDonationToBackend()', 'function');
    
    try {
        const response = await fetch('/api/save-donation/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({
                reference_number: paymentData.referenceNumber,
                amount: paymentData.total,
                transaction_date: paymentData.transactionDate,
                ecommerce_id: paymentData.ecommerceId,
                metadata1: paymentData.metadata1,
                metadata2: paymentData.metadata2
            })
        });
        
        if (response.ok) {
            debugger.log('Donación guardada en backend', 'success');
        } else {
            throw new Error('Error al guardar en backend');
        }
        
    } catch (error) {
        debugger.log('Error guardando en backend', 'error', error);
        // No lanzar error - esto no debe detener el flujo exitoso
    }
}

/**
 * Obtener CSRF token para Django
 */
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// ===============================================
// HACER CALLBACKS DISPONIBLES GLOBALMENTE
// ATH Móvil los necesita en el scope global
// ===============================================

window.authorizationATHM = authorizationATHM;
window.cancelATHM = cancelATHM;
window.expiredATHM = expiredATHM;

debugger.log('✅ Callbacks registrados globalmente', 'success');
debugger.log('Sistema listo - Selecciona un monto para comenzar', 'info');