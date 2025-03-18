from flask import Flask, render_template, request, jsonify, send_file
from pathlib import Path
import os
import sys

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from screenshotcc_interface.screenshotCC import SingleFrameProcessor, ProcessingConfig
import base64
from PIL import Image
import io

app = Flask(__name__)

# Get the project root directory
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Initialize the screenshot processor with absolute paths
config = ProcessingConfig(
    model_path=os.path.join(PROJECT_ROOT, "weights/icon_detect/model.pt"),
    caption_model_path=os.path.join(PROJECT_ROOT, "weights/icon_caption_florence"),
    output_dir=os.path.join(PROJECT_ROOT, "output")
)
processor = SingleFrameProcessor(config)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/capture', methods=['POST'])
def capture():
    try:
        # Get the file prefix from the request
        data = request.get_json()
        prefix = data.get('prefix', '')
        
        if not prefix:
            return jsonify({
                'success': False,
                'error': 'File prefix is required'
            }), 400

        # Process the screenshot with the given prefix
        results = processor.capture_and_process_frame(file_prefix=prefix)
        
        # Check if there was an error in processing
        if 'error' in results:
            return jsonify({
                'success': False,
                'error': results['error']
            }), 500
        
        # Read the processed image
        with open(results['labeled_image_path'], 'rb') as img_file:
            img_data = base64.b64encode(img_file.read()).decode('utf-8')
        
        # Read the CSV data
        with open(results['csv_path'], 'r') as csv_file:
            csv_data = csv_file.read()
        
        return jsonify({
            'success': True,
            'image': img_data,
            'csv': csv_data,
            'processing_time': results['processing_time']
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000) 