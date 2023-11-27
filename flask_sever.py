from flask import Flask, request
import wave

app = Flask(__name__)

@app.route('/convert', methods=['POST'])
def convert_ulaw_to_wave():
    ulaw_data = request.stream.read()
    print(ulaw_data)

    # Convert ulaw data to wave format
    wave_data = convert_ulaw_to_wave()

    # Save wave data to a file
    with wave.open('output.wav', 'wb') as wave_file:
        wave_file.setnchannels(1)  # Mono
        wave_file.setsampwidth(2)  # 16-bit
        wave_file.setframerate(8000)  # Sample rate
        wave_file.writeframes(wave_data)

    return 'Conversion successful'



if __name__ == '__main__':
    #run on port 5005
    app.run(host='localhost', port=5005)
