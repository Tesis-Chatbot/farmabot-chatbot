from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
import requests
import re  # Necesario para limpiar los números


class ActionVincularTicket(Action):
    def name(self) -> Text:
        return "action_vincular_ticket"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # 1. Obtener datos de los slots
        folio_raw = tracker.get_slot("folio")
        tarjeta_raw = tracker.get_slot("tarjeta")

        # LOG de depuración: Esto aparecerá en la terminal de 'rasa run actions'
        print(f"--- INTENTO DE VINCULACIÓN ---")
        print(f"DEBUG: Folio recibido: {folio_raw}")
        print(f"DEBUG: Tarjeta recibida: {tarjeta_raw}")

        # 2. Validación de presencia de datos
        if not folio_raw or not tarjeta_raw:
            dispatcher.utter_message(
                text="⚠️ Lo siento, no pude identificar el folio o la tarjeta. Por favor, asegúrate de escribirlos claramente.")
            return []

        try:
            # 3. Limpieza de datos (Extraer solo números)
            # Esto evita el error de NoneType o de texto mezclado con números
            folio_clean = re.sub(r'\D', '', str(folio_raw))
            tarjeta_clean = re.sub(r'\D', '', str(tarjeta_raw))

            if not folio_clean or not tarjeta_clean:
                raise ValueError("Los datos no contienen números válidos")

            # 4. Preparar la petición al FastAPI
            store_id = 1
            url = "http://127.0.0.1:8000/loyalty/vincular-ticket"

            payload = {
                "folio": int(folio_clean),
                "store_id": store_id,
                "card": int(tarjeta_clean)
            }

            # 5. Llamada al backend
            response = requests.post(url, json=payload, timeout=10)

            if response.status_code == 200:
                dispatcher.utter_message(
                    text=f"✅ ¡Operación exitosa! El ticket {folio_clean} ha sido vinculado a tu tarjeta.")
            else:
                error_detail = response.json().get("detail", "Error desconocido en el servidor")
                dispatcher.utter_message(text=f"❌ No se pudo vincular: {error_detail}")

        except ValueError:
            dispatcher.utter_message(text="❌ Los números de folio o tarjeta no parecen válidos. Inténtalo de nuevo.")
        except Exception as e:
            print(f"ERROR CRÍTICO: {str(e)}")
            dispatcher.utter_message(text=f"⚠️ Hubo un error de conexión con el sistema central.")

        return []


class ActionConsultarPromociones(Action):
    def name(self) -> Text:
        return "action_consultar_promociones"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        url = "http://127.0.0.1:8000/medicamentos?store_id=1"

        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                productos = response.json()
                # Filtrar solo productos con promociones vigentes
                con_promo = [p for p in productos if len(p.get("promociones", [])) > 0]

                if not con_promo:
                    dispatcher.utter_message(text="Por el momento no tenemos promociones activas en esta sucursal.")
                else:
                    mensaje = "🎉 **Estas son nuestras promociones actuales:**\n\n"
                    for p in con_promo:
                        for promo in p["promociones"]:
                            mensaje += f"• **{p['name']}**: {promo['tipo']} ({promo['valor']})\n"
                    dispatcher.utter_message(text=mensaje)
            else:
                dispatcher.utter_message(text="No pude consultar las promociones. Inténtalo más tarde.")
        except Exception as e:
            print(f"ERROR EN PROMOS: {str(e)}")
            dispatcher.utter_message(text="⚠️ Error de conexión al consultar el catálogo.")

        return []