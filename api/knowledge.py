from flask import Blueprint, request, jsonify, current_app, url_for
from flask_jwt_extended import jwt_required
from flask_cors import cross_origin
from models import DocumentKnowledge, Website, Text, KnowledgeBase
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_community.document_loaders import Docx2txtLoader
from langchain_community.document_loaders import TextLoader
from utils.provider import generate_kb_from_document, generate_kb_from_url,  tiktoken_text_split, tiktoken_doc_split 
from utils.scraper import scrape_url
import uuid
import os
from werkzeug.utils import secure_filename
import json


knowledge_blueprint = Blueprint('lknowledge_blueprintueprint', __name__)

@knowledge_blueprint.route('/upload_document', methods=['POST'])
@jwt_required()
def upload_document():
    try:
        name = request.form['name']
        files = request.files.getlist('files')
        qas_json = request.form['qa']
        urls_json = request.form['urls']
        user_id = request.form["userID"]
        if name is None or user_id is None:
            return jsonify({"error":"Unauthorized request!"}), 405
        print("name >>>", name)
        print("files >>>", len(files))
        print("qas >>>", urls_json)

        unique_id = str(uuid.uuid4())
        new_knowledge = KnowledgeBase(name=name, unique_id=unique_id, user_id=user_id)
        new_knowledge.save()

        if urls_json:
            urls = json.loads(urls_json)
            for url in urls:
                print(url['url'])
                new_website = Website(url=url["url"], unique_id=unique_id)
                new_website.save()
                # save_from_url(new_website.id, url)
                print(new_website.id)
                text = scrape_url(url["url"])
                chunks = tiktoken_text_split(text)
                type_of_knowledge = 'url'
                print("website >>>", chunks)

                generate_kb_from_url(chunks, unique_id, new_website.id, type_of_knowledge)

        for file in files:
            # Process each file (e.g., saving or using it)
            file.save('uploads/' + file.filename)
            file_path = 'uploads/' + file.filename
            filename = file.filename
            extension = os.path.splitext(secure_filename(file.filename))[1]
            loader = None
            # print("extension is >>>>", extension)
            if extension.lower() == ".pdf":
                loader = PyMuPDFLoader(file_path)
            elif extension.lower() == ".txt":
                loader = TextLoader(file_path, encoding='utf-8')
            elif extension.lower() == ".docx" or extension.lower() == ".doc":
                loader = Docx2txtLoader(file_path)
            data = loader.load()

            chunks = tiktoken_doc_split(data)
            new_doc = DocumentKnowledge(filename=filename, type=extension, unique_id=unique_id)
            new_doc.save()
            type_of_knowledge = 'pdf'
            generate_kb_from_document(chunks, unique_id, new_doc.id, type_of_knowledge)
            
            # After processing is done, delete the file
            if os.path.exists(file_path):
                os.remove(file_path)
                print(f"Deleted file: {file_path}")
            else:
                print(f"The file does not exist: {file_path}")
                print("Doc ID >>> ", new_doc.id)

        if qas_json:
            qas = json.loads(qas_json)
            for qa in qas:
                new_qa = Text(question=qa["question"], answer=qa["answer"], unique_id=unique_id)
                new_qa.save()
                text = f"Question: {qa['question']} Answer: {qa['answer']}"
                chunks = tiktoken_text_split(text)
                type_of_knowledge = 'qa'
                generate_kb_from_url(chunks, unique_id, new_qa.id, type_of_knowledge)

                print("QA ID>>>", new_qa.id)

        return {'status': 'success', 'message': f'Received {len(files)} files with name {name}'}
    except Exception as e:
        print(str(e))
        return jsonify({'error': 'Error saving database!'}), 500

@knowledge_blueprint.route('/get_knowledge_bases',methods=['GET'])
@jwt_required()
def get_knowledgebases():
    try:
        user_id = request.args.get('userId')
        print("GOT it>>>")
        print(user_id)
        if not user_id:
            return jsonify({'error': 'user_id is required'}), 400

        bases = KnowledgeBase.query.filter_by(user_id=user_id).all()
        knowledge_bases_list = [base.json() for base in bases]
        return jsonify(knowledge_bases_list), 200
    except ValueError:
        # If the provided user_id cannot be converted to an integer, return an error
        return jsonify({'error': 'Invalid user_id format. It should be an integer.'}), 400

@knowledge_blueprint.route('/get_knowledge_base',methods=['GET'])
@jwt_required()
def get_knowledgebase():
    try:
        baseId = request.args.get('baseId')
        print("GOT it>>>")
        print(baseId)
        if not baseId:
            return jsonify({'error': 'baseId is required'}), 400

        base = KnowledgeBase.query.filter_by(id=baseId).first()
        websites = Website.query.filter_by(unique_id=base.unique_id).all()
        websites_list = [website.json() for website in websites]
        docs = DocumentKnowledge.query.filter_by(unique_id=base.unique_id).all()
        docs_list = [doc.json() for doc in docs]
        print(docs_list)
        texts = Text.query.filter_by(unique_id=base.unique_id).all()
        texts_list = [text.json() for text in texts]
        # Construct the response data dictionary
        data = {
            'base': base.json() if base else None,
            'websites': websites_list,
            'documents': docs_list,
            'texts': texts_list,
        }

        return jsonify(data), 200

    except Exception as e:
        # Handle exceptions properly too
        return jsonify({'error': str(e)}), 500

@knowledge_blueprint.route('/update_knowledge_base/', methods=['POST'])
@jwt_required()
def update_knowledge_base():
    try:
        unique_id = request.args.get('unique_id')
        # Retrieve the existing knowledge base entry using the provided unique_id
        knowledge_base_entry = KnowledgeBase.query.filter_by(unique_id=unique_id).first()
        if not knowledge_base_entry:
            return jsonify({"error": "Knowledge base entry not found."}), 404
       
        # Extract the relevant information from the form
        name = request.form.get('name')
        files = request.files.getlist('files')
        qas_json = request.form.get('qa')
        urls_json = request.form.get('urls')
        user_id = request.form.get("userID")
        # print("Requested Form data >>>>>",files)
        if user_id is None:
            return jsonify({"error": "Unauthorized request!"}), 405

        if name:
            knowledge_base_entry.name = name
            knowledge_base_entry.save()

        # Process URLs JSON if provided
        if urls_json:
            urls = json.loads(urls_json)
            for url in urls:
                # print(url['id'])
                if len(urls) > 0 and url['id'] != -1:
                    continue
                new_website = Website(url=url['url'], unique_id=unique_id)
                new_website.save()
                # save_from_url(new_website.id, url)
                print(new_website.id)
                text = scrape_url(url['url'])
                chunks = tiktoken_text_split(text)
                type_of_knowledge = 'url'
                generate_kb_from_url(chunks, unique_id, new_website.id, type_of_knowledge)
                      
        # Process uploaded files
        if len(files) > 0:
            for file in files:
                file.save('uploads/' + file.filename)
                file_path = 'uploads/' + file.filename
                filename = file.filename
                extension = os.path.splitext(secure_filename(file.filename))[1]
                loader = None
                # print("extension is >>>>", extension)
                if extension.lower() == ".pdf":
                    loader = PyMuPDFLoader(file_path)
                elif extension.lower() == ".txt":
                    loader = TextLoader(file_path, encoding='utf-8')
                data = loader.load()

                chunks = tiktoken_doc_split(data)
                new_doc = DocumentKnowledge(filename=filename, type=extension, unique_id=unique_id)
                new_doc.save()
                type_of_knowledge = 'pdf'
                generate_kb_from_document(chunks, unique_id, new_doc.id, type_of_knowledge)
                
                # After processing is done, delete the file
                if os.path.exists(file_path):
                    os.remove(file_path)
                    print(f"Deleted file: {file_path}")
                else:
                    print(f"The file does not exist: {file_path}")
                    print("Doc ID >>> ", new_doc.id)
            
        # Process Q&As if provided
        if qas_json:
            qas = json.loads(qas_json)
            print(qas)
            for qa in qas:
                if qa.get('id') is None:
                    new_qa = Text(question=qa["question"], answer=qa["answer"], unique_id=unique_id)
                    new_qa.save()
                    text = f"Question: {qa['question']} Answer: {qa['answer']}"
                    chunks = tiktoken_text_split(text)
                    type_of_knowledge = 'qa'
                    generate_kb_from_url(chunks, unique_id, new_qa.id, type_of_knowledge)

        return jsonify({'status': 'success', 'message': f'Updated knowledge base entry with unique_id {unique_id}'})
    except Exception as e:
        print("Error: ", str(e))
        return jsonify({'status':'error'}), 500

        
