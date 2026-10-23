# 🎯 Trendy Radar • Sentinel VTEX

Monitor automatizado y 100% gratuito que se ejecuta en **GitHub Actions** cada 10 minutos para detectar cuándo sale a la venta el **Calendario de Adviento** en la tienda [Trendy Shop](https://www.maquillajetrendyshop.com) (VTEX).

Cuenta con un panel de estado visual público servido a través de **GitHub Pages**:
👉 **[https://juanfierro08.github.io/trendy/](https://juanfierro08.github.io/trendy/)**

---

## 🔍 Palabras Clave Vigiladas en VTEX

Para asegurar al 100% que la alerta llegue sin importar cómo titulen el producto en la tienda, el monitor consulta todas estas variaciones:
* `adviento`
* `calendario de adviento`
* `calendario adviento`
* `calendario`
* `coalendario`
* `preventa adviento`
* `caja adviento`
* `calendario trendy`
* `preventa`
* `pre venta`
* `navidad`
* `edicion especial adviento`

---

## 🔑 1. Configurar los 3 Secrets en GitHub

Para recibir la alerta por correo cuando aparezca el producto:

1. Ve a tu repositorio en GitHub: [https://github.com/juanfierro08/trendy](https://github.com/juanfierro08/trendy)
2. Entra a **Settings** > **Secrets and variables** > **Actions**.
3. Haz clic en **New repository secret** y añade estos 3 secretos:

| Secret | Descripción |
| :--- | :--- |
| `GMAIL_USER` | Tu correo de Gmail remitente (ej: `tu_correo@gmail.com`). |
| `GMAIL_APP_PASSWORD` | Tu contraseña de aplicación de Google de 16 letras (sin espacios). |
| `ALERT_RECIPIENT_EMAIL` | Correo donde recibirás la notificación (puede ser el mismo `GMAIL_USER`). |

---

## 🧪 2. Cómo Hacer Pruebas y Verificar que Lleguen los Correos

Puedes probar el envío de correos y la detección en cualquier momento desde **GitHub Actions**:

1. En tu repositorio, entra a la pestaña **[Actions](https://github.com/juanfierro08/trendy/actions)**.
2. En la barra lateral izquierda, selecciona **Trendy Radar Sentinel**.
3. Haz clic en el botón desplegable **Run workflow**.
4. En el campo **"Selecciona la acción a ejecutar"**, puedes elegir:
   * **`check`**: Realiza la revisión normal de la tienda.
   * **`test_email`**: Envía un correo real de prueba a tu Gmail para verificar que las credenciales funcionan al 100%.
   * **`simulate`**: Simula que el Calendario de Adviento apareció, envía la alerta real con foto y precio a tu Gmail y cambia el panel a verde.
   * **`reset`**: Vuelve a poner el estado en *"no disponible"* para re-armar el radar tras las pruebas.
5. Haz clic en el botón verde **Run workflow**.

Además, en la página web [https://juanfierro08.github.io/trendy/](https://juanfierro08.github.io/trendy/) tienes un botón para previsualizar el panel en verde con sonido de alerta.

---

## 🌐 3. Activar GitHub Pages (Panel Web Público)

Para que tu página de estado en vivo funcione:

1. En tu repositorio, entra a **Settings** > **Pages**.
2. En **Build and deployment** > **Source**, elige **Deploy from a branch**.
3. En **Branch**, selecciona `main` y en la carpeta elige `/docs`.
4. Haz clic en **Save**.

En 1 o 2 minutos tu dashboard estará visible en:
👉 `https://juanfierro08.github.io/trendy/`

---

## ⚙️ Funcionamiento Automático

* **Frecuencia:** Se ejecuta cada 10 minutos (`cron: "*/10 * * * *"`).
* **Detección:** Si el calendario aún no está en tienda, registra el chequeo en `data/estado.json` y termina.
* **Alerta:** En el instante en que VTEX publique el producto, envía el correo con la ficha y enlace directo de compra, y marca `avisado: true` para nunca enviar correos duplicados.
* **Historial:** Mantiene las últimas 50 revisiones visibles tanto en `data/estado.json` como en el dashboard de GitHub Pages con hora de Colombia (`America/Bogota`).
