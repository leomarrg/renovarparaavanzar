#!/bin/bash
# Script para programar envío de emails UNA VEZ a las 9am hora Puerto Rico usando 'at'

echo "Configurando envío programado UNA VEZ a las 9am hora Puerto Rico..."

# Directorio del proyecto
PROJECT_DIR="/home/ubuntu/renovarparaavanzar"
PYTHON_PATH=$(which python3)
VENV_PYTHON="$PROJECT_DIR/venv/bin/python"

# Verificar si existe virtualenv
if [ -f "$VENV_PYTHON" ]; then
    PYTHON_CMD="$VENV_PYTHON"
    echo "Usando Python del virtualenv: $VENV_PYTHON"
else
    PYTHON_CMD="$PYTHON_PATH"
    echo "Usando Python del sistema: $PYTHON_PATH"
fi

# Instalar 'at' si no está instalado
if ! command -v at &> /dev/null; then
    echo "Instalando 'at' daemon..."
    sudo apt-get update
    sudo apt-get install -y at
    sudo systemctl enable atd
    sudo systemctl start atd
fi

# Crear directorio de logs
LOG_DIR="$PROJECT_DIR/logs"
mkdir -p $LOG_DIR
LOG_FILE="$LOG_DIR/email_$(date +%Y%m%d).log"

# Crear script temporal que se ejecutará
TEMP_SCRIPT="/tmp/send_emails_temp.sh"
cat > $TEMP_SCRIPT << 'EOF'
#!/bin/bash
cd /home/ubuntu/renovarparaavanzar
source venv/bin/activate 2>/dev/null || true
python send_email_sendgrid.py --offset 2500 --limit 4500 --batch-size 500 --pause 600 --email-type fechas_votacion
EOF

chmod +x $TEMP_SCRIPT

# Programar para las 9am hora Puerto Rico = 1pm UTC (13:00)
echo "Programando ejecución para mañana a las 9:00 AM hora Puerto Rico (13:00 UTC)..."
echo "$TEMP_SCRIPT >> $LOG_FILE 2>&1" | at 13:00 tomorrow

echo ""
echo "✅ Envío programado exitosamente!"
echo ""
echo "Detalles:"
echo "  - Fecha: Viernes 21 de noviembre 2024"
echo "  - Hora: 9:00 AM Puerto Rico (13:00 UTC)"
echo "  - Offset: 2500"
echo "  - Limit: 4500 (enviará hasta registro 7000)"
echo "  - Template: fechas_votacion"
echo "  - Log: $LOG_FILE"
echo ""
echo "Tareas programadas:"
atq
echo ""
echo "Para ver detalles de una tarea:"
echo "  at -c <job_number>"
echo ""
echo "Para cancelar:"
echo "  atrm <job_number>"
echo ""
echo "Para ver logs cuando se ejecute:"
echo "  tail -f $LOG_FILE"
