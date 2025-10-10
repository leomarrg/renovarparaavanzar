// ===============================================
// ATH MÓVIL PAYMENT - OFFICIAL IMPLEMENTATION
// Based on: https://github.com/evertec/athmovil-javascript-api
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
            <strong style="color: #0ff;">🔍 ATH DEBUG</strong>
            <button id="clear-debug" style="background: #f00; color: #fff; border: none; padding: 2px 8px; cursor: pointer; border-radius: 3px;">X</button>
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
        const logsContainer = document.getElementById('debug-logs');
        if (!logsContainer) return;
        
        const logElement = document.createElement('div');
        
        let color = '#0f0';
        let icon = 'ℹ️';
        
        switch(type) {
            case 'success': color = '#0f0'; icon = '✅'; break;
            case 'error': color = '#f00'; icon = '❌'; break;
            case 'warning': color = '#ff0'; icon = '⚠️'; break;
            case 'ath': color = '#0ff'; icon = '🏦'; break;
            case 'function': color = '#f0f'; icon = '⚙️'; break;
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

const athDebugger = new VisualDebugger();

athDebugger.log('Script cargado', 'success');
athDebugger.log('⚠️ NOTA: ATH Móvil NO soporta cambio dinámico de monto', 'warning');

// ===============================================
// CONFIGURAR ATHM_Checkout SEGÚN EL MONTO EN URL
// ===============================================

// Obtener monto de la URL
const urlParams = new URLSearchParams(window.location.search);
const urlAmount = urlParams.get('amount');
const selectedAmount = urlAmount ? parseFloat(urlAmount) : 0;

athDebugger.log(`Monto detectado: $${selectedAmount}`, selectedAmount > 0 ? 'success' : 'warning');

// ===============================================
// DEFINIR ATHM_Checkout GLOBALMENTE
// Según documentación oficial de ATH Móvil
// ===============================================

const ATHM_Checkout = {
    env: 'production',
    publicToken: 'TU_PUBLIC_TOKEN_AQUI', // ⚠️ REEMPLAZA CON TU TOKEN REAL
    timeout: 600,
    theme: 'btn',
    lang: 'es',
    total: selectedAmount,
    subtotal: selectedAmount,
    tax: 0,
    metadata1: 'Donacion Campaña',
    metadata2: `Monto: $${selectedAmount}`,
    items: [
        {
            name: "Donación",
            description: "Apoyo a la campaña",
            quantity: 1,
            price: selectedAmount,
            tax: 0,
            metadata: "Donacion"
        }
    ],
    phoneNumber: ""
};

athDebugger.log('ATHM_Checkout configurado', 'ath', {
    total: ATHM_Checkout.total,
    publicToken: ATHM_Checkout.publicToken.substring(0, 10) + '...'
});

// ===============================================
// CALLBACKS OBLIGATORIOS (Documentación Oficial)
// ===============================================

/**
 * Se ejecuta cuando el pago es autorizado exitosamente
 */
async function authorizationATHM() {
    athDebugger.log('→ authorizationATHM() - PAGO AUTORIZADO ✅', 'success');
    
    try {
        const responseAuth = await authorization();
        athDebugger.log('Respuesta de autorización:', 'success', responseAuth);
        
        // Mostrar mensaje de éxito
        showPaymentStatus('success', '¡Donación exitosa! Gracias por tu apoyo.');
        
        // Aquí puedes enviar los datos a tu servidor Django
        // sendPaymentToServer(responseAuth);
        
    } catch (error) {
        athDebugger.log('Error en autorización', 'error', error);
        showPaymentStatus('error', 'Hubo un error al procesar el pago.');
    }
}

/**
 * Se ejecuta cuando el usuario cancela el pago
 */
async function cancelATHM() {
    athDebugger.log('→ cancelATHM() - PAGO CANCELADO ❌', 'warning');
    
    try {
        const responseCancel = await findPaymentATHM();
        athDebugger.log('Pago cancelado:', 'warning', responseCancel);
        
        showPaymentStatus('error', 'El pago fue cancelado.');
        
    } catch (error) {
        athDebugger.log('Error al verificar cancelación', 'error', error);
    }
}

/**
 * Se ejecuta cuando el pago expira por timeout
 */
async function expiredATHM() {
    athDebugger.log('→ expiredATHM() - PAGO EXPIRADO ⏱️', 'warning');
    
    try {
        const responseExpired = await findPaymentATHM();
        athDebugger.log('Pago expirado:', 'warning', responseExpired);
        
        showPaymentStatus('error', 'El tiempo para completar el pago expiró.');
        
    } catch (error) {
        athDebugger.log('Error al verificar expiración', 'error', error);
    }
}

// ===============================================
// FUNCIONES DE UI
// ===============================================

function showPaymentStatus(type, message) {
    const statusDiv = document.getElementById('paymentStatusDonation');
    if (!statusDiv) {
        athDebugger.log('Elemento paymentStatusDonation no encontrado', 'warning');
        return;
    }
    
    statusDiv.className = 'payment-status ' + type;
    statusDiv.textContent = message;
    statusDiv.style.display = 'block';
    
    // Scroll hacia el mensaje
    statusDiv.scrollIntoView({ behavior: 'smooth', block: 'center' });
    
    athDebugger.log(`Estado mostrado: ${type} - ${message}`, 'info');
}

function updateSelectedAmountDisplay(amount) {
    const displayDiv = document.getElementById('selectedAmountDisplay');
    const valueSpan = document.getElementById('selectedAmountValue');
    
    if (displayDiv && valueSpan) {
        valueSpan.textContent = amount.toFixed(2);
        displayDiv.style.display = 'block';
        athDebugger.log('Display actualizado', 'success');
    }
}

// ===============================================
// CONFIGURAR BOTONES DE SELECCIÓN DE MONTO
// ===============================================

function setupAmountButtons() {
    athDebugger.log('→ setupAmountButtons()', 'function');
    
    const amountButtons = document.querySelectorAll('.amount-btn');
    athDebugger.log(`${amountButtons.length} botones encontrados`, 'info');
    
    amountButtons.forEach(btn => {
        btn.addEventListener('click', function() {
            const amount = parseFloat(this.getAttribute('data-amount'));
            athDebugger.log(`Click en botón: $${amount}`, 'info');
            
            // Redirigir con el nuevo monto
            const currentUrl = window.location.pathname;
            window.location.href = `${currentUrl}?amount=${amount}#donate`;
        });
    });
}

function setupCustomAmountInput() {
    athDebugger.log('→ setupCustomAmountInput()', 'function');
    
    const customInput = document.getElementById('customDonationAmount');
    if (!customInput) {
        athDebugger.log('Input personalizado NO encontrado', 'warning');
        return;
    }
    
    // Verificar si ya existe el botón
    let continueBtn = document.getElementById('customAmountContinue');
    
    if (!continueBtn) {
        // Crear botón "Continuar"
        const wrapper = customInput.parentElement;
        continueBtn = document.createElement('button');
        continueBtn.id = 'customAmountContinue';
        continueBtn.textContent = 'Continuar';
        continueBtn.style.cssText = `
            margin-top: 10px;
            padding: 12px 30px;
            background: #4DB6AC;
            color: white;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-weight: 600;
            font-size: 1rem;
            transition: all 0.3s ease;
        `;
        continueBtn.onmouseover = function() {
            this.style.background = '#3d9d94';
        };
        continueBtn.onmouseout = function() {
            this.style.background = '#4DB6AC';
        };
        wrapper.appendChild(continueBtn);
    }
    
    continueBtn.addEventListener('click', function() {
        const value = parseFloat(customInput.value);
        
        if (!value || value <= 0) {
            alert('Por favor ingresa un monto válido mayor a $0');
            return;
        }
        
        if (value < 1) {
            alert('El monto mínimo es $1.00');
            return;
        }
        
        if (value > 1500) {
            alert('El monto máximo es $1,500.00');
            return;
        }
        
        athDebugger.log(`Monto personalizado: $${value}`, 'info');
        
        // Redirigir con el monto personalizado
        const currentUrl = window.location.pathname;
        window.location.href = `${currentUrl}?amount=${value}#donate`;
    });
}

// ===============================================
// INICIALIZACIÓN AL CARGAR EL DOM
// ===============================================

document.addEventListener('DOMContentLoaded', function() {
    athDebugger.log('DOM cargado', 'success');
    
    // Marcar botón activo si hay monto en URL
    if (selectedAmount > 0) {
        document.querySelectorAll('.amount-btn').forEach(btn => {
            if (parseFloat(btn.getAttribute('data-amount')) === selectedAmount) {
                btn.classList.add('active');
            }
        });
        
        updateSelectedAmountDisplay(selectedAmount);
        athDebugger.log('Botón de monto marcado como activo', 'success');
    }
    
    // Configurar botones
    setupAmountButtons();
    setupCustomAmountInput();
    
    athDebugger.log('Sistema inicializado ✅', 'success');
});

// ===============================================
// NOTAS IMPORTANTES
// ===============================================

athDebugger.log('═══════════════════════════════', 'warning');
athDebugger.log('📋 INSTRUCCIONES:', 'warning');
athDebugger.log('1. Reemplaza TU_PUBLIC_TOKEN_AQUI', 'warning');
athDebugger.log('2. El script athmovil_base.js crea el botón automáticamente', 'warning');
athDebugger.log('3. Para cambiar monto, se recarga la página', 'warning');
athDebugger.log('═══════════════════════════════', 'warning');