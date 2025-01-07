import os
import json
from pathlib import Path
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

def read_transcript(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

def get_summary_prompt(transcript):
    # Prompt personalizado basado en el estilo de Fabric
    prompt = f"""
Given this transcript, please provide a comprehensive summary that:
1. Captures the main points and key insights
2. Maintains important context and nuance
3. Is clear and well-structured
4. Preserves any critical details or action items

Transcript:
{transcript}

Please provide the summary:"""
    return prompt

def generate_summary(transcript):
    client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that creates clear, accurate, and comprehensive summaries while maintaining the original context and key details."},
            {"role": "user", "content": get_summary_prompt(transcript)}
        ]
    )
    
    return response.choices[0].message.content

def main():
    # Verificar que existe el directorio de transcripciones
    if not os.path.exists('transcripts'):
        print("Error: No se encuentra el directorio 'transcripts'")
        return
    
    # Crear directorio para sumarios si no existe
    os.makedirs('summaries', exist_ok=True)
    
    # Procesar cada transcripción
    transcript_dir = Path('transcripts')
    for transcript_file in transcript_dir.glob('*.txt'):
        print(f"Procesando: {transcript_file}")
        transcript = read_transcript(transcript_file)
        summary = generate_summary(transcript)
        
        # Guardar el resumen
        summary_path = Path('summaries') / f"summary_{transcript_file.stem}.txt"
        with open(summary_path, 'w', encoding='utf-8') as f:
            f.write(summary)
        print(f"Resumen guardado en: {summary_path}")

if __name__ == "__main__":
    main()