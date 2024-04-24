from utils.vectorizor import upsertDataToIndex
from langchain.text_splitter import CharacterTextSplitter

def generate_kb_from_document(chunks, unique_id, doc_index):
    try:
        upsertDataToIndex("aiana-knowledge-base", unique_id, doc_index, chunks)
    except Exception as e:
        print("Generating the knoledgebase >>>" ,str(e))
        return - 1

def tiktoken_split(text):
    text_splitter = CharacterTextSplitter(
                separator = "\n", chunk_size=1000, chunk_overlap=200, length_function = len,
            )
    chunks = text_splitter.split_documents(text)
    print("Chunks length >>>>", len(chunks))
    return chunks

