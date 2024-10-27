import deepl

translator = deepl.Translator("65822198-b187-4415-88a5-b9296fd1eff3:fx")  # Replace with actual API key

abbreviations = {
    "ex": "example",
    "btw": "by the way",
    "asap": "as soon as possible"
}

def translate_text(text, target_language):
    """Translate text dynamically using DeepL API"""
    try:
        result = translator.translate_text(text, target_lang=target_language)
        return result.text
    except deepl.DeepLException as e:
        print(f"Translation error: {e}")
        return text

def expand_abbreviation(abbreviation, target_language):
    """Expand and translate an abbreviation based on user's language choice"""
    expansion = abbreviations.get(abbreviation, abbreviation)
    return translate_text(expansion, target_language)
