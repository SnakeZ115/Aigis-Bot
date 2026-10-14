"""
Cerebro y lógica de razonamiento para Aigis.
Interactúa con el modelo local a través de la API de Ollama,
procesa intenciones y coordina la ejecución de herramientas (Function Calling).
"""
import json
from typing import Any
import ollama
from config import config, logger
from tools import TOOL_DEFINITIONS, execute_tool

SYSTEM_PROMPT = f"""Eres {config.assistant_name}, una asistente de inteligencia artificial personal avanzada y leal, inspirada en una interfaz tipo Jarvis.
Tu objetivo es ayudar a tu usuario a controlar y supervisar su computadora Windows a través de Discord.

Instrucciones de comportamiento:
1. Sé concisa, respetuosa, precisa y eficiente. No des respuestas innecesariamente largas.
2. Tienes acceso a herramientas directas del sistema. Si el usuario te pide una acción (apagar la PC en X minutos, abrir un programa, tomar captura de pantalla, ver el estado de la RAM/CPU, etc.), USA LA HERRAMIENTA CORRESPONDIENTE en vez de sólo describir cómo hacerlo.
3. Si el usuario pide apagar la PC en cierto tiempo (ej: "apaga la pc en 20 mins"), llama a 'schedule_shutdown' con minutes=20.
4. Si el usuario pide cancelar un apagado, llama a 'cancel_shutdown'.
5. Si el usuario pide saber el estado del sistema, llama a 'get_system_status' y resume los datos amigablemente.
6. Si el usuario te pide tomar captura de pantalla, llama a 'take_screenshot'.
7. Responde en el mismo idioma en el que te habla el usuario (generalmente español).
"""


class AigisBrain:
    def __init__(self):
        self.client = ollama.AsyncClient(host=config.ollama_host)
        self.model = config.ollama_model
        # Historial de conversación en memoria (últimos intercambios)
        self.conversation_history: list[dict[str, Any]] = [
            {"role": "system", "content": SYSTEM_PROMPT}
        ]
        self.max_history_length = 15

    async def check_connection(self) -> bool:
        """Verifica si Ollama está respondiendo y si el modelo está disponible."""
        try:
            models_response = await self.client.list()
            available_models = [m.model for m in models_response.models]
            logger.info("Ollama conectado. Modelos disponibles: %s", available_models)

            # Verificar si el modelo configurado existe
            base_model_name = self.model.split(":")[0]
            found = any(self.model in m or base_model_name in m for m in available_models)
            if not found:
                logger.warning(
                    "El modelo '%s' no se encontró explícitamente en Ollama. Asegúrate de haber ejecutado 'ollama pull %s'.",
                    self.model,
                    self.model,
                )
            return True
        except Exception as e:
            logger.error("No se pudo conectar con Ollama en %s: %s", config.ollama_host, e)
            return False

    async def think_and_reply(self, user_message: str) -> dict[str, Any]:
        """
        Envía el mensaje al modelo local, procesa tool calls si existen, y genera la respuesta final.
        Retorna un diccionario con:
        {
            "reply_text": str,
            "attachment_path": str | None,
            "tools_used": list[str]
        }
        """
        # Añadir mensaje del usuario al historial
        self.conversation_history.append({"role": "user", "content": user_message})

        # Limitar historial para no saturar la ventana de contexto
        if len(self.conversation_history) > self.max_history_length:
            # Preservar el prompt de sistema inicial
            self.conversation_history = [self.conversation_history[0]] + self.conversation_history[-10:]

        tools_executed = []
        attachment_path = None

        try:
            response = await self.client.chat(
                model=self.model,
                messages=self.conversation_history,
                tools=TOOL_DEFINITIONS,
                options={"temperature": config.ollama_temperature},
            )

            assistant_msg = response.message

            # Si el modelo decidió llamar a una o más herramientas
            if assistant_msg.tool_calls:
                # Registrar mensaje del asistente con los tool calls
                self.conversation_history.append(assistant_msg)

                for tool_call in assistant_msg.tool_calls:
                    fn_name = tool_call.function.name
                    fn_args = tool_call.function.arguments or {}
                    tools_executed.append(fn_name)

                    # Ejecutar la herramienta física en el sistema
                    tool_output = execute_tool(fn_name, fn_args)

                    # Manejo especial si la herramienta produjo una captura de pantalla
                    if fn_name == "take_screenshot" and isinstance(tool_output, dict):
                        if tool_output.get("success") and tool_output.get("filepath"):
                            attachment_path = tool_output.get("filepath")

                    # Serializar respuesta de la herramienta para el historial
                    tool_content = (
                        json.dumps(tool_output, ensure_ascii=False)
                        if isinstance(tool_output, (dict, list))
                        else str(tool_output)
                    )

                    self.conversation_history.append({
                        "role": "tool",
                        "content": tool_content,
                    })

                # Segunda llamada al modelo para que redacte su respuesta con el resultado de las herramientas
                final_response = await self.client.chat(
                    model=self.model,
                    messages=self.conversation_history,
                    options={"temperature": config.ollama_temperature},
                )
                reply_text = final_response.message.content or "Acción completada."
                self.conversation_history.append({"role": "assistant", "content": reply_text})
            else:
                reply_text = assistant_msg.content or "No tengo una respuesta para eso."
                self.conversation_history.append({"role": "assistant", "content": reply_text})

            return {
                "reply_text": reply_text,
                "attachment_path": attachment_path,
                "tools_used": tools_executed,
            }

        except Exception as e:
            logger.error("Error al procesar mensaje con Ollama: %s", e)
            return {
                "reply_text": f"⚠️ Error de comunicación con mi núcleo de IA (Ollama): {str(e)}",
                "attachment_path": None,
                "tools_used": [],
            }


brain = AigisBrain()
