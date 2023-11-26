from flask import Flask, request, jsonify
from datetime import datetime
import nemo.collections.asr as nemo_asr
import requests
import tempfile
import os
import json
app = Flask(__name__)

# Load the Hindi ASR model
asr_model_hi = nemo_asr.models.EncDecCTCModelBPE.from_pretrained(model_name="stt_hi_conformer_ctc_medium")

# Load the English ASR model
asr_model_en = nemo_asr.models.EncDecRNNTBPEModel.from_pretrained("nvidia/stt_en_conformer_transducer_xlarge")

def load_audio_from_stream(stream):
    # Create a temporary directory to store the audio file
    temp_dir = tempfile.mkdtemp()
    local_file_path = os.path.join(temp_dir, "temp_audio.wav")

    # Write the audio content to the temporary file
    with open(local_file_path, "wb") as temp_file:
        for chunk in stream.iter_content(chunk_size=1024):
            temp_file.write(chunk)

    return local_file_path

@app.route('/transcribe_hi', methods=['POST'])
def transcribe_hi():
    if 'audiofile' not in request.files:
        return jsonify({'error': 'No audio file provided'}), 400

    audiofile = load_audio_from_stream(request.files['audiofile'])

    try:
        # Transcribe the Hindi audio file
        transcription = asr_model_hi.transcribe([audiofile])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

    # Prepare the response JSON
    response_data = {
        'data_time': datetime.now().isoformat(),
        'transcribe': transcription[0]
    }

    return json.dumps(response_data, ensure_ascii=False)

@app.route('/transcribe_en', methods=['POST'])
def transcribe_en():
    if 'audiofile' not in request.files:
        return jsonify({'error': 'No audio file provided'}), 400

    audiofile = load_audio_from_stream(request.files['audiofile'])

    try:
        # Transcribe the English audio file
        transcription = asr_model_en.transcribe([audiofile])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

    # Prepare the response JSON
    response_data = {
        'data_time': datetime.now().isoformat(),
        'transcribe': transcription[0]
    }

    return jsonify(response_data)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002)
