from utils.vectorizor import upsertDocToIndex, upsertTextToIndex
from langchain.text_splitter import CharacterTextSplitter
from langchain.prompts import PromptTemplate
from langchain.memory import ConversationBufferMemory

def generate_kb_from_document(chunks, unique_id, doc_index, _type):
    try:
        upsertDocToIndex("aiana-knowledge-base", unique_id, doc_index, chunks, _type)
    except Exception as e:
        print("Generating the knoledgebase >>>" ,str(e))
        return - 1

def generate_kb_from_url(chunks, unique_id, doc_index, _type):
    try:
        upsertTextToIndex("aiana-knowledge-base", unique_id, doc_index, chunks, _type)
    except Exception as e:
        print("Generating the knoledgebase >>>" ,str(e))
        return - 1

def tiktoken_doc_split(text):
    text_splitter = CharacterTextSplitter(
                separator = "\n", chunk_size=1000, chunk_overlap=200, length_function = len,
            )
    chunks = text_splitter.split_documents(text)
    print("Chunks length >>>>", len(chunks))
    return chunks

def tiktoken_text_split(text):
    text_splitter = CharacterTextSplitter(
                separator = "\n", chunk_size=1000, chunk_overlap=200, length_function = len,
            )
    chunks = text_splitter.split_text(text)
    print("Chunks length >>>>", len(chunks))
    return chunks

def generate(user_id, bot_id, query):
    template = """Based on the context, generate the answer."""
        
    end = """Context: {context}
    Chat history: {chat_history}
    Human: {human_input}
    Your Response as Chatbot: """
    
    template += end
    
    prompt = PromptTemplate(
        input_variables=["chat_history", "human_input", "context"],
        template=template
    )

    memory = ConversationBufferMemory(memory_key="chat_history", input_key="human_input")

    

    
    