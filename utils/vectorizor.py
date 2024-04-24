
import openai
from pinecone import Pinecone, ServerlessSpec
# from openai import OpenAI
import time
from uuid import uuid4
# from langchain.vectorstores import Pinecone
from langchain_openai import OpenAIEmbeddings
from pinecone import Pinecone, ServerlessSpec
# from langchain.sql_database import SQLDatabase
from models import KnowledgeBase
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


        

