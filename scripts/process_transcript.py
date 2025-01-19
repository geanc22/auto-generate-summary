import os
from pathlib import Path
from openai import OpenAI
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

def get_prompt():
    """Retorna el prompt para el resumen"""
    system_prompt = """Eres un asistente experto en crear resúmenes claros y precisos en español. 
    Mantienes la esencia y los detalles importantes del contenido original mientras presentas la información 
    de manera estructurada y fácil de entender."""
    
    user_prompt_template = """Por favor, proporciona un resumen completo y estructurado que:
    1. Capture los puntos principales y las ideas clave
    2. Mantenga el contexto y los matices importantes
    3. Sea claro y bien estructurado
    4. Preserve cualquier detalle crítico o elementos de acción

    El resumen debe estar organizado en las siguientes secciones:
    - Puntos Principales
    - Detalles Importantes
    - Conclusiones o Acciones

    Todo el resumen debe estar en español.
    """
    return system_prompt, user_prompt_template

def generate_summary_with_model(model_client, transcript, is_groq=False):
    """Genera el resumen usando el modelo especificado"""
    system_prompt, user_prompt_template = get_prompt()
    
    formatted_prompt = f"""
    {user_prompt_template}

    CONTENIDO A RESUMIR:
    {transcript}
    """
    
    if is_groq:
        response = model_client.chat.completions.create(
            model="mixtral-8x7b-32768",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": formatted_prompt}
            ]
        )
    else:
        response = model_client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": formatted_prompt}
            ]
        )
    
    return response.choices[0].message.content

def process_transcript(transcript):
    """Procesa la transcripción usando el modelo disponible"""
    try:
        if os.getenv('GROQ_API_KEY'):
            client = Groq(api_key=os.getenv('GROQ_API_KEY'))
            return generate_summary_with_model(client, transcript, is_groq=True)
    except Exception as e:
        print(f"Error con Groq: {e}")
    
    if os.getenv('OPENAI_API_KEY'):
        client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        return generate_summary_with_model(client, transcript)
    
    raise Exception("No se encontró ninguna API key válida (Groq o OpenAI)")

def main():
    if not os.path.exists('transcripts'):
        print("Error: No se encuentra el directorio 'transcripts'")
        return
    
    os.makedirs('summaries', exist_ok=True)
    
    transcript_dir = Path('transcripts')
    for transcript_file in transcript_dir.glob('*.txt'):
        print(f"Procesando: {transcript_file}")
        
        with open(transcript_file, 'r', encoding='utf-8') as f:
            transcript = f.read()
        
        summary = process_transcript(transcript)
        
        summary_path = Path('summaries') / f"summary_{transcript_file.stem}.txt"
        with open(summary_path, 'w', encoding='utf-8') as f:
            f.write(summary)
        
        print(f"Resumen guardado en: {summary_path}")

if __name__ == "__main__":
    main()