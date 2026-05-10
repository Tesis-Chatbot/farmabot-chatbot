from typing import Any, Text, Dict, List, Optional
from rasa_sdk import Action, Tracker, FormValidationAction
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.types import DomainDict
import requests
import re

class ActionVincularTicket(Action):
    def name(self) -> Text:
        return "action_vincular_ticket"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # Obtener slots (ya validados por el form)
        folio_raw = tracker.get_slot("folio")
        tarjeta_raw = tracker.get_slot("tarjeta")
        sucursal_raw = tracker.get_slot("sucursal")

        print(f"--- INTENTO DE VINCULACIÓN ---")
        print(f"Folio: {folio_raw}")
        print(f"Tarjeta: {tarjeta_raw}")
        print(f"Sucursal: {sucursal_raw}")

        try:
            folio_clean = re.sub(r'\D', '', str(folio_raw))
            tarjeta_clean = re.sub(r'\D', '', str(tarjeta_raw))
            store_id = int(re.sub(r'\D', '', str(sucursal_raw)))

            payload = {
                "folio": int(folio_clean),
                "store_id": store_id,
                "card": int(tarjeta_clean)
            }

            print(f"Payload: {payload}")

            response = requests.post(
                "http://127.0.0.1:8000/loyalty/vincular-ticket",
                json=payload,
                timeout=10
            )

            if response.status_code == 200:
                dispatcher.utter_message(
                    text=f"✅ ¡Vinculación exitosa!\n"
                         f"• Ticket: {folio_clean}\n"
                         f"• Tarjeta: {tarjeta_clean}\n"
                         f"• Sucursal: {store_id}"
                )
            else:
                error = response.json().get("detail", "Error desconocido")
                dispatcher.utter_message(text=f"❌ No se pudo vincular: {error}")

        except Exception as e:
            print(f"ERROR: {str(e)}")
            dispatcher.utter_message(text="⚠️ Error al procesar la vinculación.")

        return []


class ActionConsultarPromociones(Action):
    def name(self) -> Text:
        return "action_consultar_promociones"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        producto = next(tracker.get_latest_entity_values("producto"), None)
        url = "http://127.0.0.1:8000/medicamentos?store_id=1"

        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                productos = response.json()
                con_promo = [p for p in productos if len(p.get("promociones", [])) > 0]

                if not con_promo:
                    dispatcher.utter_message(
                        text="Por el momento no tenemos promociones activas en esta sucursal."
                    )
                    return []

                # Si preguntan por un producto específico
                if producto:
                    producto_encontrado = None
                    for p in con_promo:
                        if producto.lower() in p['name'].lower():
                            producto_encontrado = p
                            break

                    if producto_encontrado:
                        mensaje = f"✅ ¡Sí! {producto_encontrado['name']} está en promoción:\n\n"
                        for promo in producto_encontrado["promociones"]:
                            if promo['tipo'] == 'Porcentaje de descuento':
                                mensaje += f"📌 {float(promo['valor']) * 100:.0f}% de descuento\n"
                            else:
                                mensaje += f"📌 {promo['tipo']}: {promo['valor']}\n"
                    else:
                        mensaje = f"❌ Lo siento, {producto} NO está en nuestras promociones actuales.\n\n"
                        mensaje += "Medicamentos en oferta:\n"
                        for p in con_promo[:5]:
                            mensaje += f"• {p['name']}\n"

                    dispatcher.utter_message(text=mensaje)
                    return []

                # Mostrar todas las promociones
                mensaje = "🎉 Estas son nuestras promociones actuales:\n\n"
                for p in con_promo:
                    mensaje += f"🔹 {p['name']}\n"
                    for promo in p["promociones"]:
                        if promo['tipo'] == 'Porcentaje de descuento':
                            porcentaje = float(promo['valor']) * 100
                            mensaje += f"   📌 {porcentaje:.0f}% de descuento\n"
                        else:
                            mensaje += f"   📌 {promo['tipo']}: {promo['valor']}\n"
                    mensaje += "\n"

                mensaje += "¿Te interesa algún medicamento en particular?"
                dispatcher.utter_message(text=mensaje)
            else:
                dispatcher.utter_message(
                    text="No pude consultar las promociones. Inténtalo más tarde."
                )
        except Exception as e:
            print(f"ERROR EN PROMOS: {str(e)}")
            dispatcher.utter_message(
                text="⚠️ Error de conexión al consultar el catálogo."
            )

        return []





class ValidateVincularTicketForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_vincular_ticket_form"

    def validate_folio(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validar folio."""
        if slot_value and re.search(r'\d{5,20}', str(slot_value)):
            return {"folio": slot_value}
        dispatcher.utter_message(text="❌ El folio no parece válido. Debe contener entre 5 y 20 dígitos.")
        return {"folio": None}

    def validate_tarjeta(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validar tarjeta."""
        if slot_value and re.search(r'\d{5,20}', str(slot_value)):
            return {"tarjeta": slot_value}
        dispatcher.utter_message(text="❌ La tarjeta no parece válida. Debe contener entre 5 y 20 dígitos.")
        return {"tarjeta": None}

    def validate_sucursal(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validar sucursal."""
        try:
            sucursal = int(re.sub(r'\D', '', str(slot_value)))
            if 1 <= sucursal <= 99:
                return {"sucursal": str(sucursal)}
        except:
            pass
        dispatcher.utter_message(text="❌ Por favor indica un número de sucursal válido (1-99).")
        return {"sucursal": None}