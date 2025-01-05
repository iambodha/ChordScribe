import nltk
from nltk.corpus import words

nltk.download('words')
english_words = set(words.words())

def generate_chord(word, max_length):
    seen = set()
    shorthand = []

    for letter in word:
        if letter not in seen:
            shorthand.append(letter)
            seen.add(letter)
        if len(shorthand) == max_length:
            break

    result = ''.join(shorthand)

    if result in english_words:
        for letter in word:
            if letter not in shorthand:
                result = result[:-1] + letter
                break
        
        if result in english_words:
            result = result[1:] + result[0]

    return result

def create_chords(word_list):
    chords = {}
    used_chords = set()

    for word in word_list:
        max_length = 2  # Start with 2-character shortcuts
        while max_length <= len(word):
            chord = generate_chord(word, max_length)

            if chord not in used_chords:
                chords[word] = chord
                used_chords.add(chord)
                break

            max_length += 1

        # If no chord was assigned, assign a fallback chord
        if word not in chords:
            chords[word] = word[:max_length]
            used_chords.add(word[:max_length])

    return chords

# Example usage
word_list = ["little", "thought", "apple", "banana", "orange"]
result = create_chords(word_list)
print(result)
