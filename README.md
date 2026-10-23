# 🎯 Trendy Radar (GitHub Actions)

Monitor automatizado y 100% gratuito que se ejecuta en **GitHub Actions** cada 10 minutos para detectar cuándo sale a la venta el **Calendario de Adviento** en la tienda [Trendy Shop](https://www.maquillajetrendyshop.com) (VTEX).

Cuando el producto aparece en el catálogo, envía una alerta inmediata a tu correo electrónico vía Gmail SMTP y guarda el estado en `data/estado.json` para **no enviar correos repetidos**.

---

## 🔑 1. Configurar Secrets en GitHub

Para que GitHub Actions pueda enviarte correos con tu cuenta de Gmail:

1. Ve a tu repositorio en GitHub.
2. Haz clic en **Settings** > **Secrets and variables** > **Actions**.
3. Haz clic en **New repository secret** y añade los siguientes 3 secretos:

| Secret | Valor |
| :--- | :--- |
| `GMAIL_USER` | Tu dirección de Gmail (ej: `tu_correo@gmail.com`). |
| `GMAIL_APP_PASSWORD` | Tu contraseña de aplicación de Google de 16 caracteres (generada en tu cuenta de Google con verificación en dos pasos). |
| `ALERT_RECIPIENT_EMAIL` | El correo donde quieres recibir la alerta (puede ser el mismo `GMAIL_USER`). |

---

## 🚀 2. Cómo Probar o Lanzar una Ejecución Manual

No tienes que esperar los 10 minutos para comprobar que funcione:

1. En tu repositorio de GitHub, entra a la pestaña **Actions**.
2. En la barra lateral izquierda, selecciona el workflow **Trendy Radar Sentinel**.
3. Haz clic en el botón desplegable **Run workflow** y presiona el botón verde **Run workflow**.
4. Haz clic en la ejecución iniciada para ver los logs en tiempo real (`[Consulta] Buscando término: 'adviento'...`).

---

## ⏱️ 3. Funcionamiento Automático

* El workflow corre solo cada **10 minutos** (`cron: "*/10 * * * *"`).
* Si el producto aún no está en tienda, el chequeo dura menos de 10 segundos y termina.
* En el instante en que VTEX publique el producto, recibirás un correo de alta prioridad con el enlace directo para comprarlo.
* El archivo `data/estado.json` se actualizará automáticamente a `avisado: true` en el repositorio para no volver a enviar correos.
