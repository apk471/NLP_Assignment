import asyncio
from langdetect import detect
from googletrans import Translator


async def translate_to_english(text):
    try:
        translator = Translator()
        lang = detect(text) 
        if lang != "en":
            translated = await translator.translate(text, src=lang, dest="en")
            return translated.text, lang
        else:
            return text, "en"
    except Exception as e:
        print(f"Error during translation: {e}")
        return text, "en"
    

    
translated_text, detected_lang = asyncio.run(translate_to_english("ग्रेविटास'25 में कितने इवेंट हैं?"))
print(f"Translated Text: {translated_text}, Detected Language: {detected_lang}")