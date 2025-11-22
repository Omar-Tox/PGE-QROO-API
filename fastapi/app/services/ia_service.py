# ============================================================
#  app/services/ia_service.py
#  Motor de Interpretación - Adaptado para Horizontes Temporales
# ============================================================

import google.generativeai as genai
import yaml
import json
import re
from app.core.config import settings

genai.configure(api_key=settings.GEMINI_API_KEY)
MODEL_NAME = "gemini-2.5-flash" 

def _limpiar_json_respuesta(texto: str) -> dict:
    texto_limpio = re.sub(r"```json\n?|```", "", texto).strip()
    try:
        return json.loads(texto_limpio)
    except json.JSONDecodeError:
        return {
            "titulo": "Diagnóstico General",
            "resumen": texto_limpio,
            "nivel_alerta": "INFO",
            "acciones": []
        }

def _convertir_a_yaml_optimizado(datos_matematicos: dict) -> str:
    # Preparamos un resumen ejecutivo para la IA
    resumen = {
        "contexto_dependencia": datos_matematicos.get("contexto_analisis"),
        "resumen_proyeccion": datos_matematicos.get("resumen_proyeccion"),
        # Enviamos solo el primer y último mes de la proyección para dar contexto de inicio/fin
        "inicio_proyeccion": datos_matematicos.get("detalle_proyeccion", [])[0] if datos_matematicos.get("detalle_proyeccion") else None,
        "fin_proyeccion": datos_matematicos.get("detalle_proyeccion", [])[-1] if datos_matematicos.get("detalle_proyeccion") else None,
    }
    return yaml.dump(resumen, allow_unicode=True, default_flow_style=False)

def generar_analisis_ejecutivo(datos_matematicos: dict) -> dict:
    try:
        datos_yaml = _convertir_a_yaml_optimizado(datos_matematicos)
        
        # Extraer horizonte para personalizar el rol
        horizonte = datos_matematicos.get("resumen_proyeccion", {}).get("horizonte_meses", 6)
        tipo_planeacion = "Operativa (Corto Plazo)"
        if horizonte == 12: tipo_planeacion = "Presupuestal (Mediano Plazo)"
        if horizonte == 24: tipo_planeacion = "Estratégica de Infraestructura (Largo Plazo)"

        prompt = f"""
        Eres un Consultor Energético Gubernamental experto en Planeación {tipo_planeacion}.
        Ubicación: Quintana Roo, México (Clima cálido extremo, tarifas CFE altas).
        
        Analiza esta proyección matemática a {horizonte} meses (YAML):
        {datos_yaml}

        Tu misión: Generar una hoja de ruta basada en los datos proyectados y el horizonte de tiempo.
        
        SI ES 6 MESES: Enfócate en mantenimiento, ajustes de horarios y control de fugas de energía inmediatas.
        SI ES 12 MESES: Enfócate en presupuesto anual, sustitución de equipos viejos (aires acondicionados) y tarifas.
        SI ES 24 MESES: Enfócate en inversión de infraestructura (Paneles Solares, Subestaciones, Sensores IoT).

        FORMATO JSON OBLIGATORIO:
        {{
            "titulo": "Título estratégico (ej. 'Plan de Inversión 2025-2026')",
            "resumen_ejecutivo": "Análisis de la tendencia y el impacto financiero acumulado ({horizonte} meses).",
            "nivel_riesgo_presupuestal": "BAJO" | "MEDIO" | "ALTO",
            "acciones_estrategicas": [
                {{
                    "accion": "Nombre de la acción",
                    "plazo_implementacion": "Inmediato/3 meses/1 año",
                    "descripcion": "Detalle técnico justificando la inversión."
                }},
                {{ ... máx 3 acciones ...}}
            ]
        }}
        """

        model = genai.GenerativeModel(MODEL_NAME)
        response = model.generate_content(prompt, generation_config={"response_mime_type": "application/json"})
        
        return {
            "status": "success",
            "analisis_ia": _limpiar_json_respuesta(response.text),
            "modelo_usado": MODEL_NAME
        }

    except Exception as e:
        return {
            "status": "warning",
            "analisis_ia": { "titulo": "Error IA", "resumen": "No disponible.", "acciones": [] },
            "error_detalle": str(e)
        }