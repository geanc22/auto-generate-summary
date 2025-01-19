import os
import json
import yaml
from pathlib import Path
from openai import OpenAI
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

# Configuración de rutas de Fabric
FABRIC_DIR = "./fabric"
FABRIC_PATTERNS_DIR = os.path.join(FABRIC_DIR, "patterns")
FABRIC_PROMPTS_DIR = os.path.join(FABRIC_DIR, "prompts")

def load_fabric_config():
    """Carga la configuración base de Fabric"""
    config_path = os.path.join(FABRIC_DIR, "config/config.yaml")
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

def load_fabric_pattern(pattern_name="summarize"):
    """Carga un patrón específico de Fabric"""
    pattern_path = os.path.join(FABRIC_PATTERNS_DIR, f"{pattern_name}/pattern.yaml")
    with open(pattern_path, 'r') as f:
        return yaml.safe_load(f)

def get_fabric_prompt(transcript):
    """Construye el prompt usando el estilo de Fabric"""
    pattern = load_fabric_pattern("summarize")
    
    # Obtener los componentes del prompt de Fabric
    system_prompt = pattern.get('system_prompt', '')
    user_prompt = pattern.get('prompt', '')
    
    # Personalizar para español
    system_prompt_es = """Eres un asistente experto en crear resúmenes claros y precisos en español. 
    Mantienes la esencia y los detalles importantes del contenido original mientras presentas la información 
    de manera estructurada y fácil de entender."""
    
    # Combinar con el formato de Fabric
    formatted_prompt = f"""
    {user_prompt}

    INSTRUCCIONES ADICIONALES:
    - El resumen debe estar en español
    - Mantén el formato y estructura de Fabric
    - Incluye secciones claramente definidas
    - Destaca los puntos clave y conclusiones

    CONTENIDO A RESUMIR:
    {transcript}
    """
    
    return system_prompt_es, formatted_prompt

def generate_summary_with_fabric(model_client, transcript, is_groq=False):
    """Genera el resumen usando el estilo Fabric"""
    system_prompt, user_prompt = get_fabric_prompt(transcript)
    
    if is_groq:
        response = model_client.chat.completions.create(
            model="mixtral-8x7b-32768",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
        )
    else:
        response = model_client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
        )
    
    return response.choices[0].message.content

def process_with_fabric(transcript):
    """Procesa la transcripción usando el pipeline de Fabric"""
    try:
        if os.getenv('GROQ_API_KEY'):
            client = Groq(api_key=os.getenv('GROQ_API_KEY'))
            return generate_summary_with_fabric(client, transcript, is_groq=True)
    except Exception as e:
        print(f"Error con Groq: {e}")
    
    if os.getenv('OPENAI_API_KEY'):
        client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        return generate_summary_with_fabric(client, transcript)
    
    raise Exception("No se encontró ninguna API key válida (Groq o OpenAI)")

def main():
    if not os.path.exists(FABRIC_DIR):
        print("Error: No se encuentra el directorio de Fabric")
        return
    
    if not os.path.exists('transcripts'):
        print("Error: No se encuentra el directorio 'transcripts'")
        return
    
    os.makedirs('summaries', exist_ok=True)
    
    # Cargar configuración de Fabric
    fabric_config = load_fabric_config()
    
    # Procesar transcripciones
    transcript_dir = Path('transcripts')
    for transcript_file in transcript_dir.glob('*.txt'):
        print(f"Procesando: {transcript_file}")
        
        # Leer y procesar con Fabric
        with open(transcript_file, 'r', encoding='utf-8') as f:
            transcript = f.read()
        
        summary = process_with_fabric(transcript)
        
        # Guardar con formato Fabric
        summary_path = Path('summaries') / f"summary_{transcript_file.stem}.txt"
        with open(summary_path, 'w', encoding='utf-8') as f:
            f.write(summary)
        
        print(f"Resumen guardado en: {summary_path}")

if __name__ == "__main__":
    main()