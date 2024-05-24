  
def get_language_code(language_name):
    # Dictionary mapping full language names to ISO 639-1 codes
    languages = {
        'English': 'en',
        'French': 'fr',
        'Spanish': 'es',
        'German': 'de',
        'Chinese': 'zh',
        'Dutch':'nl',
        # Add more languages as needed
    }

    # Return the language code, defaulting to 'en' if not found
    return languages.get(language_name, 'en')

def get_language_name(language_code):
    # Dictionary mapping ISO 639-1 codes to full language names
    codes_to_languages = {
        'en': 'English',
        'fr': 'French',
        'es': 'Spanish',
        'de': 'German',
        'zh': 'Chinese',
        'nl': 'Dutch',
        # Add more mappings as needed
    }

    # Return the full language name, defaulting to 'English' if the code is not found
    return codes_to_languages.get(language_code, 'English')
    