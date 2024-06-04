from spire.doc import *
from spire.doc.common import *

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

def extract_text_from_docx(file_path):
    # Create a Document object
    document = Document()
    # Load a Word document
    document.LoadFromFile(file_path)

    # Extract the text of the document
    document_text = document.GetText()
    print(document_text)
    return document_text

# def extract_text_from_doc(file_path):
#     text = docx2txt.process(file_path)
#     return text
    