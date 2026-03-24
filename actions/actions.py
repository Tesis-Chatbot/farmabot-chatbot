from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
import requests

class ActionVincularTicket(Action):
    def name(self) -> Text:
        return "action_vincular_ticket"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # 1. Obtener datos de la conversación
        folio = tracker.get_slot("folio")
        card = tracker.get_slot("card")
        store_id = 1  # Por ahora fijo, o podrías pedirlo

        # 2. Llamar a tu FastAPI
        # Asegúrate de que tu backend esté corriendo en este puerto
        url = "http://127.0.0.1:8000/loyalty/vincular-ticket"
        payload = {
            "folio": int(folio),
            "store_id": store_id,
            "card": int(card)
        }

        try:
            response = requests.post(url, json=payload)
            if response.status_code == 200:
                data = response.json()
                dispatcher.utter_message(text=f"✅ ¡Operación exitosa! El ticket {folio} ya tiene sus puntos.")
            else:
                error_detail = response.json().get("detail", "Error desconocido")
                dispatcher.utter_message(text=f"❌ No se pudo vincular: {error_detail}")
        except Exception as e:
            dispatcher.utter_message(text=f"⚠️ Error de conexión con el servidor: {str(e)}")

        return []