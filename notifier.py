import os
import requests
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from dotenv import load_dotenv

load_dotenv()

# Configuración de Telegram (opcional)
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

# Configuración de Email SMTP (opcional)
SMTP_SERVER = os.getenv('SMTP_SERVER')
SMTP_PORT = os.getenv('SMTP_PORT', '587')
SMTP_USER = os.getenv('SMTP_USER')
SMTP_PASSWORD = os.getenv('SMTP_PASSWORD')
EMAIL_FROM = os.getenv('EMAIL_FROM', 'contacto@dipromasters.com')

def send_telegram_notification(diagnostic_data):
    """Envia notificación al equipo de ventas por Telegram."""
    lead = diagnostic_data['lead_info']
    tk = diagnostic_data['tiktok_metrics']
    web = diagnostic_data['web_metrics']
    google = diagnostic_data['google_metrics']
    glob = diagnostic_data['global_metrics']
    
    score = glob['score']
    status_emoji = "🔴" if score < 40 else ("🟠" if score < 60 else ("🟡" if score < 80 else "🟢"))
    
    msg = (
        f"🚨 *NUEVO DIAGNÓSTICO DIGITAL - DIPROMASTERS* 🚨\n\n"
        f"👤 *Cliente:* {lead['nombre']}\n"
        f"📧 *Email:* {lead['email']}\n"
        f"📞 *Teléfono:* {lead['telefono']}\n"
        f"🏢 *Negocio/GMB:* {lead['google_maps_term']}\n\n"
        f"{status_emoji} *Puntuación Global:* {score}/100\n"
        f"💰 *Dinero Perdido:* ${glob['money_lost_total']}/mes\n"
        f"  ├─ TikTok: ${tk['money_lost']}/mes\n"
        f"  ├─ Web: ${web['money_lost']}/mes\n"
        f"  └─ Reseñas GMB: ${google['money_lost']}/mes\n\n"
        f"🎯 *Perfil Clasificado:* {lead['perfil']}\n\n"
        f"🔗 *Enlaces:* \n"
        f"  ├─ TikTok: {lead['tiktok_url'] or 'No provisto'}\n"
        f"  ├─ Web: {lead['web_url'] or 'No provisto'}\n"
        f"  └─ Google Maps: {lead['google_maps_term']}\n\n"
        f"⚠️ *Acción:* Póngase en contacto dentro de las siguientes 24 horas."
    )
    
    if TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        try:
            res = requests.post(url, json={
                'chat_id': TELEGRAM_CHAT_ID,
                'text': msg,
                'parse_mode': 'Markdown'
            }, timeout=5)
            if res.status_code == 200:
                print("[Notifier] Telegram notification sent successfully.")
                return True
            else:
                print(f"[Notifier] Telegram returned error code {res.status_code}: {res.text}")
        except Exception as e:
            print(f"[Notifier] Failed to send Telegram message: {str(e)}")
            
    # Imprimir en consola siempre (modo depuración/fallback)
    print("\n--- SIMULACIÓN TELEGRAM BOT NOTIFICATION ---")
    print(msg)
    print("--------------------------------------------\n")
    return False

def send_client_email(diagnostic_data, pdf_path, dashboard_url):
    """Envía el correo electrónico con el resumen y el PDF adjunto."""
    lead = diagnostic_data['lead_info']
    glob = diagnostic_data['global_metrics']
    score = glob['score']
    money_lost = glob['money_lost_total']
    
    score_color = "#E74C3C" if score < 40 else ("#F39C12" if score < 60 else ("#4A90D9" if score < 80 else "#2ECC71"))
    score_text = "Crítico" if score < 40 else ("Preocupante" if score < 60 else ("Mejorable" if score < 80 else "Excelente"))
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            body {{ font-family: 'Inter', Arial, sans-serif; background-color: #F7F9FC; color: #1A2332; margin: 0; padding: 20px; }}
            .container {{ max-width: 600px; background: #ffffff; margin: 0 auto; border-radius: 12px; border: 1px solid #E1E8ED; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }}
            .header {{ background-color: #272B8B; padding: 30px; text-align: center; color: white; }}
            .header h1 {{ margin: 0; font-size: 24px; letter-spacing: 1px; }}
            .header p {{ margin: 5px 0 0 0; color: #F58220; font-weight: bold; }}
            .body {{ padding: 30px; line-height: 1.6; }}
            .score-box {{ text-align: center; background: #F7F9FC; border-radius: 8px; padding: 20px; margin: 20px 0; border-left: 4px solid {score_color}; }}
            .score-num {{ font-size: 48px; font-weight: bold; color: {score_color}; margin: 0; }}
            .lost-box {{ text-align: center; background: #FDEDEC; border-radius: 8px; padding: 20px; margin: 20px 0; border: 1px solid #FADBD8; }}
            .lost-val {{ font-size: 36px; font-weight: bold; color: #E74C3C; margin: 0; }}
            .btn {{ display: inline-block; background-color: #F58220; color: #ffffff; padding: 14px 28px; text-decoration: none; border-radius: 30px; font-weight: bold; margin-top: 15px; text-align: center; box-shadow: 0 4px 6px rgba(245,130,32,0.3); }}
            .footer {{ background: #1A2332; text-align: center; padding: 20px; color: #5A6C7D; font-size: 12px; }}
            .footer a {{ color: #4A90D9; text-decoration: none; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>DIPROMASTERS</h1>
                <p>Agencia de Marketing & Aceleración Digital</p>
            </div>
            <div class="body">
                <p>Hola, <strong>{lead['nombre']}</strong>,</p>
                <p>¡Hemos finalizado el diagnóstico digital de tu negocio! Analizamos minuciosamente tu presencia en <strong>TikTok</strong>, tu <strong>Sitio Web</strong> y tus <strong>Reseñas en Google</strong>.</p>
                
                <div class="score-box">
                    <p style="margin: 0; font-size: 14px; text-transform: uppercase; color: #5A6C7D; letter-spacing: 0.5px;">Tu Puntuación Global</p>
                    <div class="score-num">{score}/100</div>
                    <p style="margin: 5px 0 0 0; font-weight: bold;">Estado: {score_text}</p>
                </div>
                
                <div class="lost-box">
                    <p style="margin: 0; font-size: 14px; text-transform: uppercase; color: #78281F; letter-spacing: 0.5px;">Pérdida de Dinero Estimada</p>
                    <div class="lost-val">${money_lost} USD / mes</div>
                    <p style="margin: 5px 0 0 0; color: #78281F; font-size: 13px;">Este es el costo de oportunidad estimado debido a fallas en optimización, conversión y reputación local.</p>
                </div>
                
                <p>Hemos adjuntado a este correo un <strong>Reporte Completo en PDF</strong> con el desglose detallado de todos los errores encontrados, la comparativa con tus principales competidores y un plan de acción priorizado paso a paso.</p>
                
                <div style="text-align: center;">
                    <a href="{dashboard_url}" class="btn">Ver Dashboard Interactivo</a>
                </div>
                
                <p style="margin-top: 25px;">Para ayudarte a solucionar estas fugas de ingresos, te invitamos a agendar una sesión estratégica sin costo de 15 minutos con uno de nuestros consultores de crecimiento digital.</p>
            </div>
            <div class="footer">
                &copy; 2026 Dipromasters. Todos los derechos reservados.<br>
                ¿Quieres acelerar tu negocio? <a href="https://dipromasters.com">Visita nuestra web</a>
            </div>
        </div>
    </body>
    </html>
    """
    
    # Check if SMTP configuration is provided
    if SMTP_SERVER and SMTP_USER and SMTP_PASSWORD:
        msg = MIMEMultipart()
        msg['From'] = EMAIL_FROM
        msg['To'] = lead['email']
        msg['Subject'] = f"Diagnóstico Digital Dipromasters: {lead['nombre']} - Puntuación: {score}/100"
        
        msg.attach(MIMEText(html_content, 'html'))
        
        # Attach PDF
        if pdf_path and os.path.exists(pdf_path):
            filename = os.path.basename(pdf_path)
            try:
                with open(pdf_path, 'rb') as attachment:
                    part = MIMEBase('application', 'octet-stream')
                    part.set_payload(attachment.read())
                    encoders.encode_base64(part)
                    part.add_header('Content-Disposition', f"attachment; filename= {filename}")
                    msg.attach(part)
            except Exception as e:
                print(f"[Notifier] Failed to attach PDF to email: {str(e)}")
                
        try:
            server = smtplib.SMTP(SMTP_SERVER, int(SMTP_PORT))
            server.starttls()
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.send_message(msg)
            server.quit()
            print(f"[Notifier] Email successfully sent to {lead['email']}.")
            return True
        except Exception as e:
            print(f"[Notifier] SMTP Error: {str(e)}")
            
    # Imprimir en consola siempre (modo simulación)
    print("\n--- SIMULACIÓN SMTP EMAIL ---")
    print(f"De: {EMAIL_FROM}")
    print(f"Para: {lead['email']}")
    print(f"Asunto: Diagnóstico Digital Dipromasters: {lead['nombre']} - Puntuación: {score}/100")
    print(f"PDF Adjunto: {pdf_path}")
    print(f"Dashboard Enlace: {dashboard_url}")
    print("Contenido (Texto):")
    print(f"Hola {lead['nombre']}. Tu puntuación es {score}/100. Estás perdiendo ${money_lost} USD al mes.")
    print("-----------------------------\n")
    return False
