"""Servicio de envío de correo SMTP (recuperación de contraseña)."""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.core.config import SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASSWORD, SMTP_FROM, FRONTEND_URL


def send_email(to_email: str, subject: str, body_html: str) -> dict:
    """Envía un correo mediante SMTP. Devuelve {'ok': True} o {'ok': False, 'error': '...'}."""
    if not SMTP_USER or not SMTP_PASSWORD:
        print(f"[EMAIL SIMULADO] Para: {to_email}\nAsunto: {subject}\n")
        return {"ok": True, "error": None}

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = SMTP_FROM
    msg["To"] = to_email

    part = MIMEText(body_html, "html")
    msg.attach(part)

    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=10) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.send_message(msg)
        return {"ok": True, "error": None}
    except smtplib.SMTPAuthenticationError as exc:
        return {"ok": False, "error": "Error de autenticación SMTP. Verifica tu contraseña de aplicación de Gmail."}
    except smtplib.SMTPConnectError as exc:
        return {"ok": False, "error": "No se pudo conectar al servidor SMTP de Gmail."}
    except Exception as exc:
        return {"ok": False, "error": f"No se pudo enviar el correo: {str(exc)}"}


def build_reset_password_html(code: str, email: str) -> str:
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
      <meta charset="utf-8">
      <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background-color: #FFAA00; color: white; padding: 20px; text-align: center; border-radius: 8px 8px 0 0; }}
        .content {{ background-color: #f9f9f9; padding: 20px; border-radius: 0 0 8px 8px; }}
        .code {{ font-size: 32px; font-weight: bold; color: #FFAA00; text-align: center; padding: 20px; background: #fff; border: 2px dashed #FFAA00; border-radius: 8px; letter-spacing: 8px; }}
        .footer {{ text-align: center; margin-top: 20px; font-size: 12px; color: #666; }}
        .expires {{ color: #d32f2f; font-weight: bold; }}
      </style>
    </head>
    <body>
      <div class="container">
        <div class="header">
          <h2>Todomotortaller</h2>
        </div>
        <div class="content">
          <p>Hola,</p>
          <p>Recibimos una solicitud para restablecer la contraseña de tu cuenta <strong>{email}</strong>.</p>
          <p>Tu código de verificación es:</p>
          <div class="code">{code}</div>
          <p class="expires">Este código expira en 10 minutos.</p>
          <p>Si no solicitaste este cambio, ignora este correo. Tu contraseña no será modificada.</p>
        </div>
        <div class="footer">
          © 2026 Todomotortaller — Sistema de Seguimiento para Motos
        </div>
      </div>
    </body>
    </html>
    """
