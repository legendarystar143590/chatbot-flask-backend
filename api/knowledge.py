from flask import Blueprint, request, jsonify, current_app, url_for
from flask_cors import cross_origin
from models import Document, Website, Text, KnowledgeBase
import uuid
import os
from werkzeug.utils import secure_filename
import json


knowledge_blueprint = Blueprint('lknowledge_blueprintueprint', __name__)

@knowledge_blueprint.route('/upload_document', methods=['POST'])
def upload_document():
    name = request.form['name']
    files = request.files.getlist('files')
    qas_json = request.form['qa']
    urls_json = request.form['urls']
    user_id = request.form["userID"]
    if name is None or user_id is None:
        return jsonify({"error":"Unauthorized request!"}), 405
    print("name >>>", name)
    print("files >>>", len(files))
    print("qas >>>", qas_json)
    print("website >>>", urls_json)

    unique_id = str(uuid.uuid4())
    new_knowledge = KnowledgeBase(name=name, unique_id=unique_id, user_id=user_id)
    new_knowledge.save()

    if urls_json:
        urls = json.loads(urls_json)
        for url in urls:
            new_website = Website(url=url, unique_id=unique_id)
            new_website.save()
            # save_from_url(new_website.id, url)
            print(new_website.id)

    for file in files:
        # Process each file (e.g., saving or using it)
        file.save('uploads/' + file.filename)
        filename = file.filename
        extension = os.path.splitext(secure_filename(file.filename))[1]
        new_doc = Document(filename=filename, type=extension, unique_id=unique_id)
        new_doc.save()

        print("Doc ID >>> ", new_doc.id)

    if qas_json:
        qas = json.loads(qas_json)
        for qa in qas:
            new_qa = Text(question=qa["question"], answer=qa["answer"], unique_id=unique_id)
            new_qa.save()

            print("QA ID>>>", new_qa.id)

    return {'status': 'success', 'message': f'Received {len(files)} files with name {name}'}
