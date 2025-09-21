import pyttsx3

engine = pyttsx3.init()
voices = engine.getProperty('voices')

print("Voces en español disponibles:\n")
for idx, voice in enumerate(voices):
    # Buscar 'spanish', 'es', 'español' en el nombre, id o languages
    if ('spanish' in voice.name.lower() or
        'es' in voice.id.lower() or
        any('es' in str(lang).lower() or 'spanish' in str(lang).lower() for lang in getattr(voice, 'languages', [])) or
        'español' in voice.name.lower()):
        print(f"{idx+1}. Nombre: {voice.name}")
        print(f"   ID: {voice.id}")
        print(f"   Idioma: {voice.languages}")
        print(f"   Género: {voice.gender}")
        print(f"   Edad: {voice.age}")
        print("-" * 40)