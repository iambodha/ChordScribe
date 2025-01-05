# base_layout.py
import deepl
from functools import lru_cache
import json
import os

# Base layout in English
base_layout = {
    'a': 'a', 'b': 'b', 'c': 'c', 'd': 'd', 'e': 'e',
    'f': 'f', 'g': 'g', 'h': 'h', 'i': 'i', 'j': 'j',
    'k': 'k', 'l': 'l', 'm': 'm', 'n': 'n', 'o': 'o',
    'p': 'p', 'q': 'q', 'r': 'r', 's': 's', 't': 't',
    'u': 'u', 'v': 'v', 'w': 'w', 'x': 'x', 'y': 'y', 'z': 'z'
}

# Initialize DeepL Translator
translator = deepl.Translator("65822198-b187-4415-88a5-b9296fd1eff3:fx")

# Define sample words to detect unique characters for each language
sample_words = ["example", "keyboard", "translate", "character", "layout"]

# Cache file path
CACHE_FILE = "layout_cache.json"

def load_cache():
    """Load cached translations from file."""
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_cache(cache):
    """Save translations cache to file."""
    with open(CACHE_FILE, 'w', encoding='utf-8') as f:
        json.dump(cache, f, ensure_ascii=False, indent=2)

@lru_cache(maxsize=None)
def batch_translate(language_code):
    """Batch translate all sample words at once and cache the results."""
    cache = load_cache()
    cache_key = f"{language_code}_{'_'.join(sample_words)}"
    
    if cache_key in cache:
        return cache[cache_key]
    
    try:
        # Translate all words at once
        translations = translator.translate_text(
            sample_words,
            target_lang=language_code
        )
        
        # Store translated texts
        result = [t.text for t in translations]
        cache[cache_key] = result
        save_cache(cache)
        return result
    
    except Exception as e:
        print(f"Translation error for {language_code}: {e}")
        return sample_words  # Fallback to original words on error

def get_unique_characters(language_code):
    """Get unique characters from translated words in a target language."""
    translations = batch_translate(language_code)
    # Use set comprehension for better performance
    return {char for word in translations for char in word if char.isalpha()}

def generate_layout(language_code):
    """Generate a keyboard layout for a specific language using detected characters."""
    layout = base_layout.copy()
    unique_chars = get_unique_characters(language_code)
    
    # Add unique characters to the layout
    layout.update({char: char for char in unique_chars if char not in layout})
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

def generate_all_layouts():
    """Generate all layouts with progress tracking."""
    all_layouts = {}
    total = len(language_codes)
    
    for i, code in enumerate(language_codes, 1):
        print(f"Generating layout {i}/{total}: {code}")
        all_layouts[code] = generate_layout(code)
    
    return all_layouts

# Generate layouts only when needed
layouts = {}

def print_language_menu():
    """Display the available languages menu."""
    print("\nAvailable languages:")
    print("0. Generate All Layouts")
    for i, code in enumerate(language_codes, 1):
        print(f"{i}. {code}")
    print("\nQ. Quit")

def get_user_choice():
    """Get and validate user input."""
    while True:
        choice = input("\nEnter your choice (0-31, or Q to quit): ").strip().upper()
        if choice == 'Q':
            return None
        try:
            choice = int(choice)
            if 0 <= choice <= len(language_codes):
                return choice
        except ValueError:
            pass
        print("Invalid choice. Please try again.")

def interactive_mode():
    """Run the program in interactive mode."""
    while True:
        print("\n=== Keyboard Layout Generator ===")
        print_language_menu()
        
        choice = get_user_choice()
        if choice is None:
            print("Goodbye!")
            break
            
        if choice == 0:
            # Generate all layouts
            layouts = generate_all_layouts()
            save_option = input("\nWould you like to save the results to a file? (y/n): ").lower()
            if save_option == 'y':
                filename = input("Enter filename (default: layouts_output.txt): ").strip() or "layouts_output.txt"
                with open(filename, 'w', encoding='utf-8') as f:
                    for lang_code, layout in layouts.items():
                        f.write(f"\nGenerated layout for {lang_code}:\n")
                        f.write(" ".join(f"{k}:{v}" for k, v in layout.items()) + "\n")
                print(f"\nResults saved to {filename}")
        else:
            # Generate specific layout
            selected_code = language_codes[choice - 1]
            print(f"\nGenerating layout for {selected_code}...")
            layout = generate_layout(selected_code)
            print(f"\nGenerated layout for {selected_code}:")
            print(" ".join(f"{k}:{v}" for k, v in layout.items()))
            
        input("\nPress Enter to continue...")

if __name__ == "__main__":
    try:
        interactive_mode()
    except KeyboardInterrupt:
        print("\nProgram terminated by user.")
    except Exception as e:
        print(f"\nAn error occurred: {e}")
