# Sistema de Diagnóstico Digital - Dipromasters

Este es un sistema completo de diagnóstico y auditoría digital desarrollado para la agencia de marketing **Dipromasters**. Diseñado para actuar como una potente herramienta de prospección y ventas, el sistema analiza el perfil de TikTok, el sitio web y la reputación en Google Reviews de un cliente potencial, calcula el dinero perdido mensualmente y genera un reporte en PDF junto con guiones de venta altamente efectivos.

---

## Características del Sistema

1. **Captura de Leads (Formulario de 6 campos):** Nombre, email, teléfono, TikTok URL, Web URL, y Google Maps (nombre del negocio/ciudad).
2. **Auditoría Automatizada e Híbrida:**
   - **Sitio Web (Real):** Rastreos HTTPS/SSL, velocidad de carga real, diseño responsivo, presencia de WhatsApp y formularios.
   - **TikTok y Google Reviews (Simulado Inteligente):** Generación de datos estables y realistas basados en hash determinista (siempre devuelve el mismo resultado para el mismo negocio) para evitar fallas por bloqueos de APIs.
3. **Puntuación y Fórmulas Financieras:**
   - Puntuación Global (0-100 pts) dividida en TikTok (40), Web (35) y Google Reviews (25).
   - Cálculo del dinero perdido en base a fallas de conversión y optimización.
4. **Clasificación de Perfiles de Clientes:** 🌱 Principiante Digital, 🚀 Estancado con Potencial, 🏆 Competidor Fuerte, 😴 Inactivo con Audiencia, 🤫 Fantasma Digital, y 🔗 Desconectado Digital.
5. **Dashboard del Cliente:** Resultados gráficos con semáforos, comparativa con 3 competidores locales y plan de acción recomendado.
6. **Descarga de Reporte PDF:** Un PDF profesional de 4 páginas con la marca de Dipromasters generado dinámicamente con ReportLab.
7. **Portal Interno de la Agencia (CRM):**
   - Tabla de leads con cambio de estado AJAX (Nuevo, Contactado, Cerrado, Descartado).
   - Cronología de notas de seguimiento comercial para cada cliente.
   - Visualización de guiones de venta específicos para cada perfil de cliente con datos integrados.
   - Exportación de la base de datos de leads a formato Excel (CSV).
8. **Notificaciones y Alertas:**
   - Telegram Bot API integrado para enviar alertas instantáneas del lead al equipo de ventas.
   - Sistema SMTP de correo electrónico para enviar el reporte PDF directamente al cliente.
   - Fallback de Simulación: Si no hay credenciales configuradas, la consola de Flask imprimirá el contenido exacto de los correos y mensajes enviados.

---

## Estructura del Código

- `app.py`: El servidor web Flask y enrutador de las vistas y endpoints AJAX.
- `database.py`: Creación y control de la base de datos SQLite (`dipromasters.db`).
- `analyzer.py`: Lógica para realizar las peticiones de raspado web y cálculos matemáticos.
- `pdf_generator.py`: Plantilla y motor ReportLab para la compilación del reporte PDF de 4 páginas.
- `notifier.py`: Manejo de las conexiones con Telegram API y SMTP.
- `templates/`: Plantillas HTML5 organizadas con layouts estructurados.
- `static/css/style.css`: Hojas de estilos modernas usando la paleta de colores de Dipromasters y efectos interactivos.

---

## Instrucciones de Instalación y Ejecución

Sigue estos pasos para instalar y ejecutar el proyecto en tu máquina local:

### 1. Clonar o acceder al directorio del proyecto
Asegúrate de que estás en la carpeta del proyecto:
```bash
cd "C:\Users\Andrea Ramirez\.gemini\antigravity\scratch\dipromasters-diagnostico"
```

### 2. Configurar el Entorno Virtual (Recomendado)
Crea y activa un entorno virtual de Python para mantener limpias las dependencias:

**En Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 3. Instalar Dependencias
Instala todas las librerías necesarias con `pip`:
```bash
pip install -r requirements.txt
```

### 4. Configurar Variables de Entorno (Opcional)
Si deseas activar el envío real de correos electrónicos y notificaciones de Telegram, crea un archivo `.env` en la raíz del proyecto y añade tus credenciales correspondientes:
```env
# Configuración del Bot de Telegram (Para notificaciones al equipo de ventas)
TELEGRAM_BOT_TOKEN=tu_token_de_telegram
TELEGRAM_CHAT_ID=tu_chat_id_o_canal

# Configuración SMTP (Para el envío de correos al cliente)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=tu_correo@gmail.com
SMTP_PASSWORD=tu_contraseña_de_aplicacion
EMAIL_FROM=contacto@dipromasters.com
```
*Si no creas el archivo `.env`, el sistema ejecutará el **Modo de Depuración**, imprimiendo los correos en la consola para que verifiques que el flujo comercial está completo.*

### 5. Ejecutar la Aplicación
Corre el servidor de Flask:
```bash
python app.py
```

Abre tu navegador e ingresa a:
- **Cliente:** `http://127.0.0.1:5000/` (Formulario e informes)
- **Agencia:** `http://127.0.0.1:5000/agency` (Panel de ventas interno)

---

## Pruebas y Verificación

Para probar el flujo completo:
1. Entra a la página principal y rellena el formulario de 6 campos. Puedes ingresar URLs ficticias u omitir el sitio web/TikTok para probar diferentes perfiles.
2. Después de enviar, se activará la simulación de carga detallada.
3. Serás redirigido al dashboard con los resultados y las pérdidas mensuales calculadas.
4. Presiona "Descargar PDF" para generar y guardar el reporte en tu computadora.
5. Accede a `http://127.0.0.1:5000/agency` para ver cómo se registró el lead en el panel comercial.
6. Abre el panel de notas para añadir anotaciones y cambia su estado.
7. Abre el botón "Guion" para ver cómo hablarle al cliente en base al dinero que está perdiendo.

---

## Guía de Despliegue en Render.com

Para subir este proyecto a producción en Render, sigue estos pasos:

1. **Crear Repositorio en GitHub:**
   - Sube todos los archivos del proyecto a un repositorio privado o público en GitHub.
2. **Conectar en Render.com:**
   - Crea una cuenta gratuita en **Render.com**.
   - Haz clic en **New +** y selecciona **Web Service**.
   - Conecta tu cuenta de GitHub y selecciona el repositorio de este proyecto.
3. **Configurar el Web Service:**
   - **Name:** `dipromasters-diagnostico` (o el nombre que prefieras).
   - **Environment:** `Python`
   - **Branch:** `main` (o la rama donde tengas el código).
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn app:app`
4. **Variables de Entorno (Opcional):**
   - En la pestaña **Environment** de tu servicio en Render, puedes agregar variables como `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`, `SMTP_SERVER`, `SMTP_USER`, `SMTP_PASSWORD` y `EMAIL_FROM` para activar el envío real de notificaciones y correos.
5. **Base de Datos en Producción (Nota):**
   - Dado que el plan gratuito de Render reinicia el sistema de archivos temporal una vez al día, la base de datos local SQLite (`dipromasters.db`) se restablecerá periódicamente.
   - Para producción a largo plazo, puedes conectar un disco persistente (de pago en Render) o modificar `database.py` para conectarte a una base de datos PostgreSQL externa (como las gratuitas en Render, Supabase o Neon.tech).

