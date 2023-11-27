from flask import Flask, request
import wave
import audioop

app = Flask(__name__)

@app.route('/convert', methods=['POST'])
def convert_ulaw_to_wave():
    try:
        ulaw_data = b''
        chunks = request.iter_chunks()
        for chunk in chunks:
            ulaw_data += chunk

        # make ulaw ready to be written to a file
        wave_data = audioop.ulaw2lin(ulaw_data, 2)

        # Save wave data to a file
        with wave.open('output.wav', 'wb') as wave_file:
            wave_file.setnchannels(1)  # Mono
            wave_file.setsampwidth(1)  # 16-bit
            wave_file.setframerate(8000)  # Sample rate
            wave_file.writeframes(wave_data)

        return 'Conversion successful'
    except Exception as e:
        return f'Conversion failed: {str(e)}'




if __name__ == '__main__':
    #run on port 5005
    app.run(host='localhost', port=5005)
