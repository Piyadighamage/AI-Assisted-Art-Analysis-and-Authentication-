from flask import Flask, render_template, request, jsonify, url_for
from werkzeug.utils import secure_filename
import os
import uuid
from PIL import Image
import numpy as np
from models.predictor import ArtAnalyzer
import json

app = Flask(__name__)
app.config.from_object('config.Config')

# Initialize the art analyzer
art_analyzer = ArtAnalyzer()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze_artwork():
    try:
        if 'artwork' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['artwork']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if file and allowed_file(file.filename):
            # Generate unique filename
            filename = str(uuid.uuid4()) + '.' + file.filename.rsplit('.', 1)[1].lower()
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            # Analyze the image
            results = art_analyzer.analyze_image(filepath)
            
            # Add image URL to results
            results['image_url'] = url_for('static', filename=f'uploads/{filename}')
            
            return jsonify(results)
        
        return jsonify({'error': 'Invalid file type'}), 400
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/results')
def results():
    return render_template('results.html')

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

if __name__ == '__main__':
    # Create upload directory if it doesn't exist
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    app.run(debug=True)