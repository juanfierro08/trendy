# 🎯 Trendy Radar

Monitor automatizado y 100% gratuito que se ejecuta en **GitHub Actions** cada 10 minutos para detectar la salida del **Calendario de Adviento** en la tienda [Trendy Shop](https://www.maquillajetrendyshop.com) (VTEX).

Cuenta con un panel de estado visual público servido a través de **GitHub Pages**:
👉 **[https://juanfierro08.github.io/trendy/](https://juanfierro08.github.io/trendy/)**

---

## 🔑 1. Configurar los 3 Secrets en GitHub

Para recibir la alerta por correo cuando aparezca el producto:

1. Ve a tu repositorio en GitHub: [https://github.com/juanfierro08/trendy](https://github.com/juanfierro08/trendy)
2. Entra a **Settings** > **Secrets and variables** > **Actions**.
3. Haz clic en **New repository secret** y crea estos 3 secretos:

| Secret | Descripción |
| :--- | :--- |
| `GMAIL_USER` | Tu correo de Gmail remitente (ej: `tu_correo@gmail.com`). |
| `GMAIL_APP_PASSWORD` | Tu contraseña de aplicación de Google de 16 caracteres (sin espacios). |
| `ALERT_RECIPIENT_EMAIL` | Correo donde recibirás la notificación (puede ser el mismo `GMAIL_USER`). |

---

## 🌐 2. Activar GitHub Pages (Panel Web Público)

Para que tu página de estado en vivo funcione:

1. En tu repositorio, entra a **Settings** > **Pages**.
2. En **Build and deployment** > **Source**, elige **Deploy from a branch**.
3. En **Branch**, selecciona `main` y en la carpeta elige `/docs`.
4. Haz clic en **Save**.

En 1 o 2 minutos tu dashboard estará visible en:
👉 `https://juanfierro08.github.io/trendy/`

---

## 🚀 3. Lanzar una Ejecución Manual

Puedes disparar una verificación en cualquier momento sin esperar al cron de 10 minutos:

1. En el repositorio, entra a la pestaña **Actions**.
2. En la barra lateral izquierda, selecciona el workflow **Trendy Radar Sentinel**.
3. Haz clic en el botón desplegable **Run workflow** > botón verde **Run workflow**.
4. Puedes abrir la ejecución para revisar el registro en tiempo real.

---

## ⚙️ Funcionamiento Automático

* **Frecuencia:** Se ejecuta cada 10 minutos (`cron: "*/10 * * * *"`).
* **Detección:** Si el calendario aún no está en tienda, registra el chequeo en `data/estado.json` y termina.
* **Alerta:** En el instante en que VTEX publique el producto, envía el correo con la ficha y enlace directo de compra, y marca `avisado: true` para nunca enviar correos duplicados.
* **Historial:** Mantiene las últimas 50 revisiones visibles tanto en `data/estado.json` como en el dashboard de GitHub Pages con hora de Colombia (`America/Bogota`).
