import os
import json
from pathlib import Path
import openai
from dotenv import load_dotenv

load_dotenv()

def read_transcript(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

def get_fabric_prompt(transcript):
    # Cargamos el prompt pattern de Fabric para resúmenes
    fabric_path = Path("fabric/patterns/summarize/basic.json")
    with open(fabric_path, 'r') as f:
        pattern = json.load(f)
    
    # Insertamos la transcripción en el prompt
    prompt = pattern["prompt"].replace("{{INPUT}}", transcript)
    return prompt

def generate_summary(transcript):
    prompt = get_fabric_prompt(transcript)
    
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that summarizes content."},
            {"role": "user", "content": prompt}
        ]
    )
    
    return response.choices[0].message.content

def main():
    # Crear directorio para sumarios si no existe
    os.makedirs('summaries', exist_ok=True)
    
    # Procesar cada transcripción
    transcript_dir = Path('transcripts')
    for transcript_file in transcript_dir.glob('*.txt'):
        transcript = read_transcript(transcript_file)
        summary = generate_summary(transcript)
        
        # Guardar el resumen
        summary_path = Path('summaries') / f"summary_{transcript_file.stem}.txt"
        with open(summary_path, 'w', encoding='utf-8') as f:
            f.write(summary)

if __name__ == "__main__":
    main()