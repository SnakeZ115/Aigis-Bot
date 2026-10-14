# 🛡️ Aigis — Asistente Personal IA para Windows vía Discord

**Aigis** es una asistente de inteligencia artificial personal (estilo Jarvis) diseñada para controlar y supervisar tu computadora Windows mediante mensajes de Discord, impulsada por tu propio modelo local de lenguaje (**Qwen3:8b** u otros) a través de **Ollama**.

---

## ⚡ Características Principales

* 🔒 **Seguridad Absoluta (Whitelist por ID):** Solo responderá y ejecutará acciones si el mensaje proviene de tu ID de Discord (`DISCORD_OWNER_ID`). Nadie más puede darle órdenes.
* 🧠 **Modelo Local con Function Calling:** Utiliza tu modelo local (ej. `qwen3:8b` en Ollama) para razonar el lenguaje natural y ejecutar herramientas del sistema de forma precisa.
* ⏰ **Apagado y Tareas Programadas:** Entiende comandos como *"apaga la PC en 20 minutos"* o *"cancela el apagado"* mediante un planificador interno asíncrono.
* 📊 **Diagnóstico del Sistema:** Muestra uso de CPU, RAM, espacio libre en disco, estado de la batería y tiempo de actividad (*uptime*).
* 📸 **Captura de Pantalla:** Toma una captura del escritorio y te la envía al chat de Discord.
* 🚀 **Lanzador y Cierre de Programas:** Abre o cierra aplicaciones (Chrome, Spotify, Bloc de notas, etc.).
* 🔕 **Ejecución Silenciosa y de Arranque:** Incluye scripts para correr en segundo plano sin ventanas de consola visibles y arrancar automáticamente con Windows.

---

## 📁 Estructura del Proyecto

```text
Aigis-Bot/
├── .env.example              # Plantilla de variables de configuración
├── .gitignore                # Reglas de exclusión para Git
├── requirements.txt          # Dependencias de Python
├── config.py                 # Validador y cargador de configuración
├── main.py                   # Punto de entrada principal
│
├── core/
│   ├── bot.py                # Cliente de Discord y manejo de eventos/mensajes
│   ├── security.py           # Filtro de autenticación estricta por Discord User ID
│   ├── brain.py              # Integración con Ollama (System Prompt y Tool Calling)
│   └── scheduler.py          # Planificador de tareas en segundo plano (APScheduler)
│
├── tools/                    # Capacidades del sistema ejecutables por Aigis
│   ├── __init__.py           # Registro y esquemas JSON para Ollama Function Calling
│   ├── system_tools.py       # Apagado diferido/inmediato, reinicio, suspensión y métricas
│   ├── app_tools.py          # Abrir, listar y cerrar aplicaciones de Windows
│   └── util_tools.py         # Capturas de pantalla e inspección de tareas pendientes
│
├── scripts/
│   ├── start_aigis.bat       # Lanzador en modo consola (útil para pruebas y desarrollo)
│   ├── run_background.vbs    # Lanzador silencioso (sin ventana de consola)
│   └── install_autostart.bat # Script para activar/desactivar el inicio automático en Windows
│
└── README.md
```

---

## 🛠️ Requisitos Previos

1. **Python 3.10 o superior** instalado en Windows (marcando la casilla *"Add python.exe to PATH"*).
2. **Ollama** instalado y corriendo con tu modelo descargado:
   ```cmd
   ollama pull qwen3:8b
   ```
   *(O el modelo que utilices, por ejemplo `qwen2.5:8b`, `llama3.1:8b`, etc.)*
3. **Bot de Discord:**
   * Crea una aplicación en el [Discord Developer Portal](https://discord.com/developers/applications).
   * En la sección **Bot**:
     * Crea el bot y copia su **Token**.
     * En **Privileged Gateway Intents**, activa obligatoriamente:
       * ✅ **Message Content Intent** (necesario para leer los mensajes).
   * En **OAuth2 -> URL Generator**:
     * Scopes: `bot`
     * Bot Permissions: `Send Messages`, `Read Message History`, `Attach Files`, `View Channels`.
     * Usa la URL generada para invitar al bot a tu servidor o habla con él directamente por Mensaje Directo (DM).

---

## 🚀 Instalación y Configuración

### 1. Clonar y preparar entorno virtual

Abre una terminal en la carpeta del proyecto y ejecuta:

```cmd
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configurar variables de entorno (`.env`)

Copia el archivo `.env.example` y renómbralo a `.env`:

```cmd
copy .env.example .env
```

Abre `.env` en tu editor de texto y completa:

```env
# Token del bot copiado desde Discord Developer Portal
DISCORD_BOT_TOKEN=tu_token_aqui

# Tu ID personal de Discord (Modo desarrollador -> clic derecho en tu perfil -> Copiar ID de usuario)
DISCORD_OWNER_ID=123456789012345678

# Configuración de Ollama
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=qwen3:8b
```

---

## 💻 Formas de Ejecución

### Opción A: Modo Desarrollo (Con ventana y logs)
Ideal para probar que todo funcione correctamente y ver los logs en vivo:
* Doble clic en `scripts\start_aigis.bat` o:
  ```cmd
  python main.py
  ```

### Opción B: Modo Silencioso en Segundo Plano
Ejecuta el bot sin que aparezca ninguna ventana negra de consola:
* Doble clic en `scripts\run_background.vbs`

Para detener Aigis cuando está en segundo plano, abre el **Administrador de Tareas** y finaliza el proceso `pythonw.exe`.

### Opción C: Inicio Automático con Windows
Para que Aigis siempre esté activa desde que enciendes la computadora:
1. Haz doble clic en `scripts\install_autostart.bat`.
2. Presiona `1` para registrar el acceso directo en la carpeta de inicio de tu usuario (`shell:startup`).
3. *(Si algún día deseas quitarla, simplemente ejecuta el mismo script y presiona `2`).*

---

## 💬 Ejemplos de Interacción en Discord

Puedes hablarle por **Mensaje Directo (DM)** o en cualquier servidor mencionándola (`@Aigis`):

| Petición del usuario | Acción de Aigis |
| :--- | :--- |
| *"Aigis, apaga la pc en 20 mins"* | Programa el apagado para dentro de 20 minutos y confirma la hora exacta. |
| *"Cancela el apagado"* | Cancela la tarea programada y cualquier temporizador de Windows. |
| *"¿Cómo está la computadora?"* | Consulta CPU, RAM disponible, disco y batería, resumiéndolos. |
| *"Toma una captura de pantalla"* | Captura tu escritorio y envía la imagen adjunta en el chat. |
| *"Abre spotify"* / *"Abre chrome"* | Inicia la aplicación en Windows. |
| *"¿Qué tareas tienes pendientes?"* | Lista tareas programadas y su hora de ejecución. |

---

## 🔧 ¿Cómo agregar nuevas herramientas?

1. Crea tu función en un archivo dentro de `tools/` (ej. `tools/media_tools.py`).
2. Agrega la descripción de la herramienta en `tools/__init__.py` dentro de la lista `TOOL_DEFINITIONS` (usando el formato de esquema estándar de herramientas).
3. Añade la función al diccionario `TOOL_FUNCTIONS` en `tools/__init__.py`.

Aigis y Qwen la detectarán y comenzarán a usarla automáticamente.
