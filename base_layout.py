# base_layout.py
import deepl

# Base layout in English
base_layout = {
    'a': 'a', 'b': 'b', 'c': 'c', 'd': 'd', 'e': 'e',
    'f': 'f', 'g': 'g', 'h': 'h', 'i': 'i', 'j': 'j',
    'k': 'k', 'l': 'l', 'm': 'm', 'n': 'n', 'o': 'o',
    'p': 'p', 'q': 'q', 'r': 'r', 's': 's', 't': 't',
    'u': 'u', 'v': 'v', 'w': 'w', 'x': 'x', 'y': 'y', 'z': 'z'
}

# Initialize DeepL Translator
translator = deepl.Translator("65822198-b187-4415-88a5-b9296fd1eff3:fx")  # Replace with actual API key

# Define sample words to detect unique characters for each language
sample_words = ["example", "keyboard", "translate", "character", "layout"]

def get_unique_characters(language_code):
    """Get unique characters from translated words in a target language."""
    unique_chars = set()

    for word in sample_words:
        translated = translator.translate_text(word, target_lang=language_code).text
        unique_chars.update(translated)  # Add each character in the translated word

    return unique_chars

def generate_layout(language_code):
    """Generate a keyboard layout for a specific language using detected characters."""
    layout = base_layout.copy()
    unique_chars = get_unique_characters(language_code)

    # Add unique characters to the layout
    for char in unique_chars:
        if char not in layout.values():
            layout[char] = char

    return layout

# Compile layouts for specific languages
# List of language codes for all layouts you want to support
language_codes = [
    "BG",       # Bulgarian
    "CS",       # Czech
    "DA",       # Danish
    "DE",       # German
    "EL",       # Greek
    "EN-GB",    # English (British)
    "EN-US",    # English (American)
    "ES",       # Spanish
    "ET",       # Estonian
    "FI",       # Finnish
    "FR",       # French
    "HU",       # Hungarian
    "ID",       # Indonesian
    "IT",       # Italian
    "JA",       # Japanese
    "KO",       # Korean
    "LT",       # Lithuanian
    "LV",       # Latvian
    "NB",       # Norwegian (Bokmål)
    "NL",       # Dutch
    "PL",       # Polish
    "PT-PT",    # Portuguese (Portugal)
    "PT-BR",    # Portuguese (Brazil)
    "RO",       # Romanian
    "RU",       # Russian
    "SK",       # Slovak
    "SL",       # Slovenian
    "SV",       # Swedish
    "TR",       # Turkish
    "UK",       # Ukrainian
    "ZH",       # Chinese (Simplified)
]

# Automatically generate layouts for each language in the list
layouts = {code: generate_layout(code) for code in language_codes}

# Test output for the generated layouts
if __name__ == "__main__":
    for lang_code, layout in layouts.items():
        print(f"\nGenerated layout for {lang_code}:")
        print(" ".join(f"{k}:{v}" for k, v in layout.items()))
