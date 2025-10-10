// ===============================================
// ATH MÓVIL PAYMENT - SEGÚN DOCUMENTACIÓN OFICIAL
// GitHub: https://github.com/evertec/athmovil-javascript-api
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
athDebugger.log('Solución: Se recargará la página al cambiar monto', 'info');

// ===============================================
// INICIALIZACIÓN
// ===============================================

document.addEventListener('DOMContentLoaded', function() {
    athDebugger.log('DOM cargado', 'success');
    
    // Verificar si hay un monto en la URL
    const urlParams = new URLSearchParams(window.location.search);
    const urlAmount = urlParams.get('amount');
    
    if (urlAmount) {
        const amount = parseFloat(urlAmount);
        athDebugger.log(`Monto desde URL: $${amount}`, 'success');
        
        // Marcar el botón correspondiente como activo
        document.querySelectorAll('.amount-btn').forEach(btn => {
            if (parseFloat(btn.getAttribute('data-amount')) === amount) {
                btn.classList.add('active');
            }
        });
        
        // Actualizar display
        updateSelectedAmountDisplay(amount);
    }
    
    // Configurar botones
    setupAmountButtons();
    setupCustomAmountInput();
    
    athDebugger.log('Sistema inicializado', 'success');
});

// ===============================================
// CONFIGURAR BOTONES
// ===============================================

function setupAmountButtons() {
    athDebugger.log('→ setupAmountButtons()', 'function');
    
    const amountButtons = document.querySelectorAll('.amount-btn');
    athDebugger.log(`${amountButtons.length} botones encontrados`, 'info');
    
    amountButtons.forEach(btn => {
        btn.addEventListener('click', function() {
            const amount = parseFloat(this.getAttribute('data-amount'));
            athDebugger.log(`Click: $${amount}`, 'info');
            
            // Redirigir a la misma página con el monto en la URL
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
    
    // Agregar botón "Continuar" junto al input
    const wrapper = customInput.parentElement;
    let continueBtn = document.getElementById('customAmountContinue');
    
    if (!continueBtn) {
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
        `;
        wrapper.appendChild(continueBtn);
    }
    
    continueBtn.addEventListener('click', function() {
        const value = parseFloat(customInput.value);
        
        if (!value || value <= 0) {
            alert('Por favor ingresa un monto válido');
            return;
        }
        
        if (value > 1500) {
            alert('El monto máximo es $1,500');
            return;
        }
        
        athDebugger.log(`Monto personalizado: $${value}`, 'info');
        
        // Redirigir con el monto personalizado
        const currentUrl = window.location.pathname;
        window.location.href = `${currentUrl}?amount=${value}#donate`;
    });
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
// NOTA IMPORTANTE SOBRE ATH MÓVIL
// ===============================================

athDebugger.log('═══════════════════════════════', 'warning');
athDebugger.log('⚠️ LIMITACIÓN DE ATH MÓVIL:', 'warning');
athDebugger.log('El botón ATH se crea UNA SOLA VEZ al cargar', 'warning');
athDebugger.log('NO se puede cambiar el monto dinámicamente', 'warning');
athDebugger.log('Solución implementada: Recarga con URL param', 'warning');
athDebugger.log('═══════════════════════════════', 'warning');