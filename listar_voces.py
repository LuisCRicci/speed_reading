import pyttsx3

engine = pyttsx3.init()
voices = engine.getProperty('voices')

print("Voces instaladas en el sistema:\n")
for idx, voice in enumerate(voices):
    print(f"{idx+1}. Nombre: {voice.name}")
    print(f"   ID: {voice.id}")
    print(f"   Idioma: {voice.languages}")
    print(f"   Género: {voice.gender}")
    print(f"   Edad: {voice.age}")
    print("-" * 40)