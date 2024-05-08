
import openai
from pinecone import Pinecone, ServerlessSpec
# from openai import OpenAI
import time
from uuid import uuid4
# from langchain.vectorstores import Pinecone
from langchain_openai import OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from langchain.chat_models import ChatOpenAI
from langchain.chains.question_answering import load_qa_chain
from langchain.memory import ConversationBufferMemory

from pinecone import Pinecone, ServerlessSpec
# from langchain.sql_database import SQLDatabase
from models import KnowledgeBase, Conversation, get_latest_three_conversations_by_bot
# from langchain import LargeLanguageModel
import os
import base64
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_ENVIRONMENT = os.getenv("PINECONE_ENVIRONMENT")
PINECONE_INDEX_DIMENSION = int(os.getenv("PINECONE_INDEX_DIMENSION", "3072"))
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL")

print(OPENAI_API_KEY)
print(EMBEDDING_MODEL)
print(PINECONE_INDEX_DIMENSION)

pc = Pinecone(api_key=PINECONE_API_KEY)

# Create a new index with name
def createIndex(index_name):
    dimension = 3072
    model == EMBEDDING_MODEL
    try:
        pc.create_index(
            name=index_name,
            dimension=dimension,
            metric="cosine",
            spec=ServerlessSpec(
                cloud="aws",
                region="eu-west-1"
            )
        )

        indexmodel(index_name=index_name, model=model).save()
    except Exception as e:
        print("Error in createIndex()", str(e))
        pass

#  Delete an index with name
def deleteIndex(index_name):
    try:
        if index_name in pc.list_indexes().names():
            pc.delete_index(index_name)
        else:
            print("There is no such an index to delete")
    except Exception as e:
        print("Error in deleteIndex()", str(e))
        pass

# Upsert Doc into index with 
def upsertDocToIndex(index_name, collection_name, doc_index, chunks, _type):
    try:
        
        embeddings = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY, model=EMBEDDING_MODEL)
        vectors = []

        for chunk in chunks:
            chunk.metadata['collection_name'] = collection_name
            chunk.metadata['doc_index'] = doc_index
            chunk.metadata['type']= _type
            metadata = {"collection_name": collection_name, "doc_index": doc_index, "type":_type}
            
            s_vector = {}
            s_vector['id'] = str(doc_index)
            s_vector['values'] = embeddings.embed_query(chunk.page_content)
            s_vector['metadata'] = metadata

            vectors.append(s_vector)

        p_index = pc.Index(index_name)
        p_index.upsert(vectors=vectors)
    except Exception as e:
        print("Error in upsertDataToIndex()", str(e))
        pass

# Upsert Text into index with 
def upsertTextToIndex(index_name, collection_name, doc_index, chunks, _type):
    try:
        
        embeddings = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY, model=EMBEDDING_MODEL)
        vectors = []

        for chunk in chunks:
            metadata = {"collection_name": collection_name, "doc_index": doc_index, "type":_type}
            
            s_vector = {}
            s_vector['id'] = str(doc_index)
            s_vector['values'] = embeddings.embed_query(chunk)
            s_vector['metadata'] = metadata

            vectors.append(s_vector)

        p_index = pc.Index(index_name)
        p_index.upsert(vectors=vectors)
    except Exception as e:
        print("Error in upsertDataToIndex()", str(e))
        pass

def get_answer(bot_id, query, knowledge_base):
    try:
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
        embeddings = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY, model=EMBEDDING_MODEL)
        docsearch = PineconeVectorStore.from_existing_index(
                index_name=PINECONE_INDEX_NAME, embedding=embeddings)
                
        condition = {"collection_name": knowledge_base}
        
        docs = docsearch.similarity_search(query, k=8, filter=condition)

        llm = ChatOpenAI(temperature=0.7, model="gpt-3.5-turbo-0125", openai_api_key=OPENAI_API_KEY, streaming=True)
        memory = ConversationBufferMemory(memory_key="chat_history", input_key="human_input")
        stuff_chain = load_qa_chain(llm, chain_type="stuff", prompt=prompt, memory=memory)
        latest_chat_history = get_latest_three_conversations_by_bot(bot_id)
        reduce_chat_history = ""
        for index, record in enumerate(latest_chat_history):
            if index < 4:
                print("Query => ", record.query)
                print("Answer => ", record.response)
                stuff_chain.memory.save_context({'human_input': record.query}, {'output': record.response})
                reduce_chat_history += f"Human: {record.query}\nBot: {record.response}\n"
                reduce_chain.memory.save_context({'human_input': record.query}, {'output': record.response})
            else:
                record.delete()
        output = stuff_chain({"input_documents": docs, "human_input": query}, return_only_outputs=False)
        new_conv = Conversation(bot_id, query, output["output_text"])
        new_conv.save()
        return output["output_text"]
    except Exception as e:
        print(str(e))
        return "Network error"