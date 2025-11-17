from flask import Flask, jsonify, request
from flask_cors import CORS
import os
from paddleocr import PaddleOCR
from indic_transliteration import sanscript
from indic_transliteration.sanscript import SchemeMap, SCHEMES, transliterate

scheme_map = SchemeMap(SCHEMES[sanscript.DEVANAGARI], SCHEMES[sanscript.ITRANS])
ocr = PaddleOCR(use_textline_orientation=True, lang='hi')

# 1. Create the app and enable CORS
app = Flask(__name__)
CORS(app) 

UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# --- NEW UPLOAD ROUTE ---
@app.route("/api/upload", methods=['POST'])
def upload_image():
    # 1. Check if the 'image' file is in the request
	if 'image' not in request.files:
		return jsonify({"error": "No file part"}), 400

	file = request.files['image']

    # 2. If the user does not select a file, the browser submits an
    #    empty file without a filename.
	if file.filename == '':
		return jsonify({"error": "No selected file"}), 400

	if file:
        # 3. Save the file to the 'uploads' folder
		filepath = os.path.join(UPLOAD_FOLDER, file.filename)
		file.save(filepath)
        
		# easyOCR
		fileText = ocr.predict(filepath)[0]['rec_texts']
		fileText = ' '.join(fileText)
		tText = transliterate(fileText, scheme_map=scheme_map)

        # 4. Send a success response
		return jsonify({
			"rText": fileText,
			"tText": f"{tText}"
		})

# Run the app
if __name__ == "__main__":
    app.run(debug=True)
