from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import os
import base64

app = Flask(__name__)
CORS(app, supports_credentials=True, origins='*')  

drawings_dir = "drawings"
os.makedirs(drawings_dir, exist_ok=True)  

@app.route('/api/save-drawing', methods=['POST'])
def save_drawing():
    data = request.json
    if not data or 'drawing' not in data:
        return jsonify({"error": "No drawing data provided"}), 400

    drawing_data = data['drawing']
    file_name = data.get('filename', 'drawing.png')
    file_path = os.path.join(drawings_dir, file_name)

    try:
     
        if drawing_data.startswith("data:image"):
         
            header, encoded = drawing_data.split(',', 1)
            decoded_data = base64.b64decode(encoded)
            
      
            with open(file_path, 'wb') as f:
                f.write(decoded_data)

        return jsonify({"message": "Drawing saved successfully", "path": file_path}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/drawings/<filename>', methods=['GET'])
def get_drawing(filename):
    return send_from_directory(drawings_dir, filename)



if __name__ == '__main__':
    app.run(port=8887)
