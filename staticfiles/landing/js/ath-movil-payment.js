// ==========================================
// ATH MÓVIL PAYMENT MODULE
// Maneja donaciones con ATH Móvil
// ==========================================

console.log('🚀 Configurando ATH Móvil Payment Button');
    
    // ==========================================
    // VARIABLES GLOBALES
    // ==========================================
    let selectedDonationAmount = 0;
    let userPhoneNumber = "";
    
    // ==========================================
    // CONFIGURACIÓN DE ATH MÓVIL (OBJETO GLOBAL)
    // ==========================================
    
    // Detectar ambiente automáticamente
    const isLocalhost = window.location.hostname === 'localhost' || 
                       window.location.hostname === '127.0.0.1' ||
                       window.location.hostname.includes('192.168.');
    
    console.log('🌍 Ambiente detectado:', isLocalhost ? 'DESARROLLO (localhost)' : 'PRODUCCIÓN');
    console.log('🌍 Hostname:', window.location.hostname);
    
    const ATHM_Checkout = {
        env: 'production', // ATH Móvil solo acepta 'production'
        publicToken: 'a937f2e32a4e35ebd2c2850d204fd4dc4b515763',
        timeout: 600,
        theme: 'btn',
        lang: 'es',
        total: 1.00,
        subtotal: 1.00,
        tax: 0,
        metadata1: isLocalhost ? 'TEST - Donacion Campaña' : 'Donacion Campaña',
        metadata2: isLocalhost ? 'TEST - RenovarParaAvanzar' : 'RenovarParaAvanzar',
        items: [{
            "name": isLocalhost ? "TEST - Donación Campaña" : "Donación Campaña",
            "description": "Donación para Renovar para Avanzar",
            "quantity": "1",
            "price": "1.00",
            "tax": "0",
            "metadata": "donacion"
        }],
        phoneNumber: "" // Se llenará dinámicamente
    };
    
    if (isLocalhost) {
        console.warn('⚠️ ATENCIÓN: Estás en LOCALHOST');
        console.warn('⚠️ Para probar ATH Móvil necesitas:');
        console.warn('   1. Un token de SANDBOX (diferente al de producción)');
        console.warn('   2. O hacer las pruebas en un servidor público (no localhost)');
        console.warn('   3. Las transacciones reales NO funcionarán en localhost');
        
        // Mostrar advertencia visual en la página
        setTimeout(() => {
            const paymentStatus = document.getElementById('paymentStatusDonation');
            if (paymentStatus) {
                paymentStatus.style.display = 'block';
                paymentStatus.className = 'payment-status';
                paymentStatus.style.background = '#FFF3CD';
                paymentStatus.style.border = '2px solid #FFC107';
                paymentStatus.style.color = '#856404';
                paymentStatus.innerHTML = `
                    <i class="fas fa-exclamation-triangle" style="font-size: 2rem; display: block; margin-bottom: 15px; color: #FFC107;"></i>
                    <h3 style="margin: 10px 0; color: #856404;">Modo de Desarrollo - Localhost</h3>
                    <p style="margin: 10px 0;">El botón de ATH Móvil NO funcionará en localhost por razones de seguridad.</p>
                    <p style="margin: 10px 0; font-size: 0.9rem;"><strong>Opciones para probar:</strong></p>
                    <ul style="text-align: left; margin: 10px auto; max-width: 400px; font-size: 0.9rem;">
                        <li>Usar <strong>ngrok</strong> para crear un túnel público</li>
                        <li>Desplegar en <strong>Railway.app</strong> o <strong>Render</strong></li>
                        <li>Solicitar credenciales de <strong>sandbox</strong> a ATH Móvil</li>
                    </ul>
                    <button onclick="this.parentElement.style.display='none'" 
                            style="margin-top: 15px; background: #FFC107; color: #856404; border: none; padding: 10px 20px; border-radius: 5px; cursor: pointer; font-weight: bold;">
                        Entendido
                    </button>
                `;
            }
        }, 3000);
    }
    
    // ==========================================
    // FUNCIONES DE CALLBACK REQUERIDAS
    // ==========================================
    
    async function authorizationATHM() {
        console.log('✅ authorizationATHM llamada - Usuario confirmó en ATH Móvil');
        const paymentStatus = document.getElementById('paymentStatusDonation');
        
        try {
            // Mostrar que estamos procesando
            paymentStatus.style.display = 'block';
            paymentStatus.className = 'payment-status processing';
            paymentStatus.innerHTML = `
                <i class="fas fa-spinner fa-spin" style="font-size: 3rem; display: block; margin-bottom: 15px; color: #2563EB;"></i>
                <h3 style="margin: 10px 0; color: #1E40AF;">Procesando tu donación...</h3>
                <p>Por favor espera mientras verificamos el pago.</p>
            `;
            paymentStatus.scrollIntoView({ behavior: 'smooth', block: 'center' });
            
            console.log('🔄 Llamando a authorization()...');
            const responseAuth = await authorization();
            console.log('📦 Respuesta de authorization():', responseAuth);
            
            if (responseAuth && responseAuth.status === 'success') {
                const data = responseAuth.data;
                console.log('✅ Pago completado exitosamente');
                console.log('📋 Datos del pago:', data);
                
                paymentStatus.style.display = 'block';
                paymentStatus.className = 'payment-status success';
                paymentStatus.innerHTML = `
                    <i class="fas fa-check-circle" style="font-size: 3rem; display: block; margin-bottom: 15px; color: #059669;"></i>
                    <h3 style="margin: 10px 0; color: #065F46;">¡Donación Exitosa!</h3>
                    <p style="margin: 15px 0; font-size: 1.2rem;">
                        Gracias por tu donación de <strong>${data.total.toFixed(2)}</strong>
                    </p>
                    ${data.referenceNumber ? `
                        <p style="font-size: 0.9rem; opacity: 0.8; margin: 10px 0;">
                            Referencia: <strong>${data.referenceNumber}</strong>
                        </p>
                    ` : ''}
                    ${data.dailyTransactionId ? `
                        <p style="font-size: 0.9rem; opacity: 0.8; margin: 5px 0;">
                            ID Transacción: <strong>${data.dailyTransactionId}</strong>
                        </p>
                    ` : ''}
                    <div style="margin-top: 20px;">
                        <a href="#register" style="background: #4DB6AC; color: white; padding: 12px 30px; border-radius: 8px; text-decoration: none; margin: 5px; display: inline-block;">Registrarme</a>
                        <button onclick="location.reload()" style="background: white; color: #4DB6AC; border: 2px solid #4DB6AC; padding: 12px 30px; border-radius: 8px; margin: 5px; cursor: pointer;">Donar Nuevamente</button>
                    </div>
                `;
                paymentStatus.scrollIntoView({ behavior: 'smooth', block: 'center' });
            } else {
                console.error('❌ Respuesta sin éxito:', responseAuth);
                throw new Error(responseAuth?.message || 'Error desconocido en la autorización');
            }
        } catch (error) {
            console.error('❌ Error en authorizationATHM:', error);
            paymentStatus.style.display = 'block';
            paymentStatus.className = 'payment-status error';
            paymentStatus.innerHTML = `
                <i class="fas fa-exclamation-circle" style="font-size: 2.5rem; display: block; margin-bottom: 15px;"></i>
                <h3>Error al procesar la donación</h3>
                <p>Hubo un problema al verificar tu pago. Por favor contacta al soporte.</p>
                <p style="font-size: 0.8rem; opacity: 0.7; margin-top: 10px;">${error.message}</p>
                <button onclick="location.reload()" style="margin-top: 15px; background: #DC2626; color: white; border: none; padding: 10px 20px; border-radius: 5px; cursor: pointer;">Intentar de nuevo</button>
            `;
            paymentStatus.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }
    }
    
    async function cancelATHM() {
        console.log('⚠️ cancelATHM llamada - Usuario canceló el pago');
        const paymentStatus = document.getElementById('paymentStatusDonation');
        
        try {
            console.log('🔄 Llamando a findPaymentATHM()...');
            const responseCancel = await findPaymentATHM();
            console.log('📦 Respuesta de cancelación:', responseCancel);
        } catch (error) {
            console.error('Error obteniendo info de cancelación:', error);
        }
        
        paymentStatus.style.display = 'block';
        paymentStatus.className = 'payment-status error';
        paymentStatus.innerHTML = `
            <i class="fas fa-times-circle" style="font-size: 2.5rem; display: block; margin-bottom: 15px; color: #DC2626;"></i>
            <h3 style="margin: 10px 0; color: #991B1B;">Donación Cancelada</h3>
            <p>No te preocupes, puedes intentar de nuevo cuando desees.</p>
            <button onclick="this.parentElement.style.display='none'" 
                    style="margin-top: 15px; background: #DC2626; color: white; border: none; padding: 10px 20px; border-radius: 5px; cursor: pointer;">
                Cerrar
            </button>
        `;
        paymentStatus.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }
    
    async function expiredATHM() {
        console.log('⏱️ expiredATHM llamada - El pago expiró');
        const paymentStatus = document.getElementById('paymentStatusDonation');
        
        try {
            console.log('🔄 Llamando a findPaymentATHM()...');
            const responseExpired = await findPaymentATHM();
            console.log('📦 Respuesta de expiración:', responseExpired);
        } catch (error) {
            console.error('Error obteniendo info de expiración:', error);
        }
        
        paymentStatus.style.display = 'block';
        paymentStatus.className = 'payment-status error';
        paymentStatus.innerHTML = `
            <i class="fas fa-clock" style="font-size: 2.5rem; display: block; margin-bottom: 15px; color: #F59E0B;"></i>
            <h3 style="margin: 10px 0; color: #92400E;">Tiempo Expirado</h3>
            <p>El tiempo para completar la donación expiró. Por favor intenta de nuevo.</p>
            <button onclick="location.reload()" 
                    style="margin-top: 15px; background: #F59E0B; color: white; border: none; padding: 10px 20px; border-radius: 5px; cursor: pointer;">
                Intentar de nuevo
            </button>
        `;
        paymentStatus.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }
    
    // ==========================================
    // FUNCIONES AUXILIARES
    // ==========================================
    
    function showError(message) {
        const paymentStatus = document.getElementById('paymentStatusDonation');
        paymentStatus.style.display = 'block';
        paymentStatus.className = 'payment-status error';
        paymentStatus.innerHTML = `
            <i class="fas fa-exclamation-circle" style="font-size: 2.5rem; display: block; margin-bottom: 15px;"></i>
            <h3>Error</h3>
            <p>${message}</p>
        `;
        paymentStatus.scrollIntoView({ behavior: 'smooth', block: 'center' });
        setTimeout(() => { paymentStatus.style.display = 'none'; }, 8000);
    }
    
    function updateATHMCheckout() {
        console.log('🔄 Actualizando ATHM_Checkout con monto:', selectedDonationAmount);
        
        // Asegurar que el monto sea válido
        if (selectedDonationAmount < 1) {
            console.warn('⚠️ Monto menor a $1, usando mínimo de $1');
            selectedDonationAmount = 1;
        }
        
        if (selectedDonationAmount > 1500) {
            console.warn('⚠️ Monto mayor a $1500, usando máximo de $1500');
            selectedDonationAmount = 1500;
        }
        
        // Redondear a 2 decimales
        selectedDonationAmount = Math.round(selectedDonationAmount * 100) / 100;
        
        ATHM_Checkout.total = selectedDonationAmount;
        ATHM_Checkout.subtotal = selectedDonationAmount;
        ATHM_Checkout.tax = 0;
        ATHM_Checkout.phoneNumber = userPhoneNumber; // Agregar teléfono
        ATHM_Checkout.items = [{
            "name": "Donación Campaña",
            "description": "Donación para Renovar para Avanzar",
            "quantity": "1",
            "price": selectedDonationAmount.toFixed(2),
            "tax": "0",
            "metadata": "donacion"
        }];
        
        console.log('✅ ATHM_Checkout actualizado:', {
            total: ATHM_Checkout.total,
            subtotal: ATHM_Checkout.subtotal,
            phoneNumber: ATHM_Checkout.phoneNumber,
            items: ATHM_Checkout.items
        });
    }
    
    function updateDonateButton() {
        const amountDisplay = document.getElementById('selectedAmountDisplay');
        const amountValue = document.getElementById('selectedAmountValue');
        
        if (selectedDonationAmount > 0) {
            amountDisplay.style.display = 'block';
            amountValue.textContent = selectedDonationAmount.toFixed(2);
            updateATHMCheckout();
        } else {
            amountDisplay.style.display = 'none';
        }
    }
    
    // ==========================================
    // INICIALIZACIÓN
    // ==========================================
    
    window.addEventListener('load', function() {
        console.log('✅ Página cargada - Verificando botón ATH Móvil');
        console.log('📋 ATHM_Checkout inicial:', ATHM_Checkout);
        
        // Interceptar errores de ATH Móvil
        const originalFetch = window.fetch;
        window.fetch = function(...args) {
            const url = args[0];
            const options = args[1] || {};
            
            console.log('🌐 Fetch interceptado:', url);
            if (options.body) {
                try {
                    const bodyData = JSON.parse(options.body);
                    console.log('📤 Datos enviados:', bodyData);
                } catch (e) {
                    console.log('📤 Body:', options.body);
                }
            }
            
            return originalFetch.apply(this, args)
                .then(response => {
                    console.log('📥 Respuesta recibida:', response.status, response.statusText);
                    
                    // Clonar la respuesta para poder leerla sin consumirla
                    const clonedResponse = response.clone();
                    
                    if (url.includes('athmovil.com')) {
                        clonedResponse.json().then(data => {
                            console.log('📦 Datos de respuesta ATH:', data);
                            
                            if (!response.ok) {
                                console.error('❌ Error en ATH Móvil:', response.status, data);
                                showError(`Error: ${data.message || 'Error al procesar el pago'}`);
                            }
                        }).catch(err => {
                            console.log('No se pudo parsear JSON de respuesta:', err);
                        });
                    }
                    
                    return response;
                })
                .catch(error => {
                    console.error('❌ Error de red:', error);
                    showError('Error de conexión. Por favor verifica tu internet.');
                    throw error;
                });
        };
        
        // Verificar que el contenedor existe
        const buttonContainer = document.getElementById('ATHMovil_Checkout_Button_payment');
        if (buttonContainer) {
            console.log('✅ Contenedor encontrado');
            
            // Esperar a que el botón se renderice
            setTimeout(() => {
                const button = buttonContainer.querySelector('button, a, div[role="button"]');
                if (button) {
                    console.log('✅ Botón ATH Móvil renderizado correctamente');
                    console.log('🎨 Botón HTML:', button.outerHTML.substring(0, 200));
                    
                    // Interceptar el click para validar monto Y teléfono
                    const originalClick = button.onclick;
                    button.onclick = function(e) {
                        console.log('🖱️ Click en botón ATH Móvil');
                        console.log('💰 Monto actual:', selectedDonationAmount);
                        console.log('📞 Teléfono actual:', userPhoneNumber);
                        console.log('📋 ATHM_Checkout actual:', {
                            env: ATHM_Checkout.env,
                            publicToken: ATHM_Checkout.publicToken.substring(0, 20) + '...',
                            total: ATHM_Checkout.total,
                            subtotal: ATHM_Checkout.subtotal,
                            tax: ATHM_Checkout.tax,
                            phoneNumber: ATHM_Checkout.phoneNumber,
                            items: ATHM_Checkout.items
                        });
                        
                        // Validar monto
                        if (selectedDonationAmount <= 0) {
                            e.preventDefault();
                            e.stopPropagation();
                            alert('Por favor selecciona un monto de donación primero');
                            document.getElementById('selectedAmountDisplay')?.scrollIntoView({ behavior: 'smooth', block: 'center' });
                            return false;
                        }
                        
                        if (selectedDonationAmount < 1) {
                            e.preventDefault();
                            e.stopPropagation();
                            alert('El monto mínimo de donación es $1.00');
                            return false;
                        }
                        
                        // Validar teléfono
                        const phoneInput = document.getElementById('donationPhoneNumber');
                        if (phoneInput) {
                            const phone = phoneInput.value.replace(/\D/g, '');
                            
                            if (!phone || phone.length < 10) {
                                e.preventDefault();
                                e.stopPropagation();
                                alert('Por favor ingresa tu número de teléfono de ATH Móvil (10 dígitos)');
                                phoneInput.focus();
                                phoneInput.scrollIntoView({ behavior: 'smooth', block: 'center' });
                                return false;
                            }
                            
                            userPhoneNumber = phone;
                            console.log('✅ Teléfono válido:', userPhoneNumber);
                        }
                        
                        console.log('✅ Validaciones pasadas. Procesando pago...');
                        console.log('💰 Monto:', selectedDonationAmount);
                        console.log('📞 Teléfono:', userPhoneNumber);
                        
                        updateATHMCheckout();
                        
                        console.log('📋 ATHM_Checkout después de actualizar:', {
                            total: ATHM_Checkout.total,
                            subtotal: ATHM_Checkout.subtotal,
                            phoneNumber: ATHM_Checkout.phoneNumber,
                            items: ATHM_Checkout.items
                        });
                        
                        if (originalClick) {
                            return originalClick.call(this, e);
                        }
                    };
                    
                } else {
                    console.error('❌ Botón no encontrado después de 2 segundos');
                    console.log('Contenido del contenedor:', buttonContainer.innerHTML);
                }
            }, 2000);
        } else {
            console.error('❌ Contenedor ATHMovil_Checkout_Button_payment no encontrado');
        }
    });
    
    // ==========================================
    // EVENT LISTENERS PARA MONTOS
    // ==========================================
    
    document.addEventListener('DOMContentLoaded', function() {
        console.log('✅ DOM listo - Configurando botones de monto');
        
        // Botones de monto predefinido
        document.querySelectorAll('.amount-btn').forEach(btn => {
            btn.addEventListener('click', function() {
                console.log('💰 Botón de monto clickeado');
                
                // Remover selección previa
                document.querySelectorAll('.amount-btn').forEach(b => {
                    b.classList.remove('active');
                    b.style.background = '#E8F0EE';
                    b.style.borderColor = '#D1E5E0';
                    const val = b.querySelector('.amount-value');
                    const lbl = b.querySelector('.amount-label');
                    if (val) val.style.color = '#377e7c';
                    if (lbl) lbl.style.color = '#718096';
                });
                
                // Seleccionar nuevo
                this.classList.add('active');
                this.style.background = '#4DB6AC';
                this.style.borderColor = '#4DB6AC';
                const val = this.querySelector('.amount-value');
                const lbl = this.querySelector('.amount-label');
                if (val) val.style.color = 'white';
                if (lbl) lbl.style.color = 'white';
                
                selectedDonationAmount = parseFloat(this.dataset.amount);
                document.getElementById('customDonationAmount').value = '';
                updateDonateButton();
                
                console.log('✅ Monto seleccionado:', selectedDonationAmount);
            });
        });

        // Input personalizado
        const customInput = document.getElementById('customDonationAmount');
        if (customInput) {
            customInput.addEventListener('input', function() {
                console.log('💰 Monto personalizado ingresado');
                
                // Remover selección de botones
                document.querySelectorAll('.amount-btn').forEach(b => {
                    b.classList.remove('active');
                    b.style.background = '#E8F0EE';
                    b.style.borderColor = '#D1E5E0';
                    const val = b.querySelector('.amount-value');
                    const lbl = b.querySelector('.amount-label');
                    if (val) val.style.color = '#377e7c';
                    if (lbl) lbl.style.color = '#718096';
                });
                
                const value = parseFloat(this.value);
                if (value >= 1 && value <= 1500) {
                    selectedDonationAmount = value;
                    updateDonateButton();
                    console.log('✅ Monto personalizado válido:', selectedDonationAmount);
                } else if (value > 1500) {
                    this.value = 1500;
                    selectedDonationAmount = 1500;
                    updateDonateButton();
                    alert('El monto máximo es $1,500');
                } else {
                    selectedDonationAmount = 0;
                    updateDonateButton();
                }
            });
        }
    });
    
    console.log('✅ Script ATH Móvil configurado completamente');