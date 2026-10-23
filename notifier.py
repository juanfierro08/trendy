import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime
from typing import List, Dict
import config

def format_cop_price(val) -> str:
    """Formatea un precio numérico a moneda colombiana (COP)."""
    try:
        num = float(val)
        return f"${num:,.0f} COP".replace(",", ".")
    except (ValueError, TypeError):
        return "Consultar precio"

def send_alert(products: List[Dict]):
    """
    Envía la alerta por correo electrónico usando Gmail SMTP_SSL (puerto 465).
    Si el envío falla, lanza una excepción para que el workflow de GitHub Actions falle.
    """
    if not products:
        print("[Notifier] No hay productos para notificar.")
        return

    gmail_user, gmail_app_password, recipient = config.get_email_credentials()
    now_str = datetime.now().strftime("%d/%m/%Y %I:%M:%S %p")
    subject = "¡El calendario de Adviento de Trendy ya salió! 🎁"

    # Construir listado en texto plano y HTML
    items_plain = []
    items_html = []

    for p in products:
        name = p.get("productName", "Calendario de Adviento")
        price = format_cop_price(p.get("price"))
        link = p.get("link", config.VTEX_BASE_URL)
        items_plain.append(f"- {name}\n  Precio: {price}\n  Enlace directo: {link}")

        items_html.append(f"""
        <div style="background-color: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 16px; margin-bottom: 16px;">
            <h2 style="margin: 0 0 8px 0; color: #0f172a; font-size: 18px;">{name}</h2>
            <p style="margin: 0 0 12px 0; color: #db2777; font-size: 20px; font-weight: bold;">{price}</p>
            <a href="{link}" target="_blank" style="display: inline-block; background-color: #ec4899; color: #ffffff; text-decoration: none; padding: 10px 20px; border-radius: 6px; font-weight: bold; font-size: 14px;">
                ¡Comprar ahora en Trendy Shop! &rarr;
            </a>
        </div>
        """)

    body_plain = (
        f"¡ALERTA DE TRENDY SHOP!\n\n"
        f"El calendario de Adviento ya se encuentra disponible en la tienda:\n\n"
        f"{chr(10).join(items_plain)}\n\n"
        f"Hora de detección: {now_str}\n"
    )

    body_html = f"""
    <!DOCTYPE html>
    <html lang="es">
    <head><meta charset="utf-8"></head>
    <body style="font-family: Arial, sans-serif; background-color: #ffffff; color: #334155; margin: 0; padding: 20px;">
        <div style="max-width: 600px; margin: 0 auto; border: 1px solid #e2e8f0; border-radius: 12px; padding: 24px;">
            <div style="border-bottom: 2px solid #ec4899; padding-bottom: 12px; margin-bottom: 20px;">
                <h1 style="color: #ec4899; margin: 0; font-size: 24px;">✨ ¡El calendario de Adviento ya salió! ✨</h1>
                <p style="color: #64748b; margin: 6px 0 0 0; font-size: 13px;">Detección automática en maquillajetrendyshop.com</p>
            </div>
            {"".join(items_html)}
            <p style="color: #94a3b8; font-size: 12px; margin-top: 24px;">
                Detección registrada el: {now_str} UTC por GitHub Actions (Trendy Radar).
            </p>
        </div>
    </body>
    </html>
    """

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = f"Trendy Radar <{gmail_user}>"
    msg["To"] = recipient
    msg.attach(MIMEText(body_plain, "plain", "utf-8"))
    msg.attach(MIMEText(body_html, "html", "utf-8"))

    print(f"[Notifier] Conectando a smtp.gmail.com:465 (SSL) con usuario {gmail_user}...")
    server = smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=20)
    try:
        server.login(gmail_user, gmail_app_password)
        server.sendmail(gmail_user, [recipient], msg.as_string())
        print(f"[Notifier] ¡Correo de alerta enviado exitosamente a {recipient}!")
    finally:
        server.quit()
