# Asistente Virtual para Soporte de Farmacias (Proyecto de Titulación)

Este proyecto es un chatbot basado en la arquitectura de Rasa Open Source, diseñado para automatizar la vinculación de tickets de compra con tarjetas de lealtad en una cadena de farmacias.

## Características
- NLP Nativo: Procesamiento de lenguaje natural para entender folios y números de tarjeta.
- Integración con API: Conexión mediante un Action Server a una API de FastAPI para validación de datos.
- Flujos de Conversación: Manejo de saludos, despedidas y procesos de registro de puntos.
## Requisitos Técnicos
Para replicar este entorno, se requiere:
- Python: 3.9.13 (Versión recomendada para estabilidad de dependencias).
- Rasa: 3.6.15
- Sistema Operativo: Windows (Requiere Microsoft C++ Build Tools).

## Instalación y Configuración
1. Clonar el repositorio:
```bash
git clone https://github.com/Tesis-Chatbot/farmabot-chatbot.git
cd farmabot-chatbot
```
2. Crear y activar el entorno virtual:
```bash
python -m venv venv
.\venv\Scripts\activate
```
3. Instalar dependencias:
```bash
pip install --upgrade pip
pip install setuptools==65.5.0
pip install -r requirements.txt
```

## Estructura del Proyecto
/data: Contiene los archivos nlu.yml (ejemplos de entrenamiento) y stories.yml (flujos).

/actions: Código en Python (actions.py) para la lógica de negocio.

domain.yml: Definición del universo del bot (intents, entities, slots).

config.yml: Configuración del pipeline de IA (DIETClassifier, Tokenizers).
