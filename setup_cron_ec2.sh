#!/bin/bash
# Script para configurar cron job en EC2 que ejecute a las 9am hora Puerto Rico

echo "Configurando cron job para envío de emails a las 9am hora Puerto Rico..."

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

# Crear archivo de log para cron
LOG_DIR="$PROJECT_DIR/logs"
mkdir -p $LOG_DIR
CRON_LOG="$LOG_DIR/cron_email.log"

# Crear entrada de cron
# 0 9 * * * = Todos los días a las 9:00 AM
# EC2 en us-east-1 usa UTC, Puerto Rico es UTC-4
# 9am PR = 1pm UTC (13:00 UTC)
CRON_ENTRY="0 13 * * * cd $PROJECT_DIR && $PYTHON_CMD send_email_sendgrid.py --offset 2500 --limit 3000 --batch-size 500 --pause 600 --email-type liderazgo_resultados >> $CRON_LOG 2>&1"

# Backup del crontab actual
echo "Haciendo backup del crontab actual..."
crontab -l > /tmp/crontab_backup_$(date +%Y%m%d_%H%M%S).txt 2>/dev/null

# Agregar nueva entrada (eliminar duplicados primero)
echo "Agregando entrada al crontab..."
(crontab -l 2>/dev/null | grep -v "send_email_sendgrid.py"; echo "$CRON_ENTRY") | crontab -

echo ""
echo "✅ Cron job configurado exitosamente!"
echo ""
echo "Detalles:"
echo "  - Se ejecutará a las 9:00 AM hora Puerto Rico (1:00 PM UTC)"
echo "  - Offset: 2500"
echo "  - Limit: 3000"
echo "  - Template: liderazgo_resultados"
echo "  - Log: $CRON_LOG"
echo ""
echo "Crontab actual:"
crontab -l
echo ""
echo "Para ver logs en tiempo real:"
echo "  tail -f $CRON_LOG"
echo ""
echo "Para eliminar el cron job:"
echo "  crontab -e"
echo "  (eliminar la línea con send_email_sendgrid.py)"
