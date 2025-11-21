@echo off
cd "c:\Users\Leomar\Documents\Proyectos\renovarparaavanzar"
python send_email_sendgrid.py --offset 2500 --limit 3000 --batch-size 500 --pause 600 --email-type liderazgo_resultados
pause
