from flask import Flask, request
import wave
import audioop

app = Flask(__name__)

@app.route('/convert', methods=['POST'])
def convert_ulaw_to_wave():


# Assuming you have an array of u-law encoded fragments
    ulaw_fragments = request.form
    #convert ulaw_fragment variable to a array
  
    print(type(ulaw_fragments))
    print(dict(ulaw_fragments)[""])
    # # Decode and combine u-law fragments into a single bytearray
    # combined_pcm_data = bytearray()
    # for ulaw_fragment in ulaw_fragments:
    #     pcm_fragment, _ = audioop.ulaw2lin(ulaw_fragment, 2)  # 2 is the sample width (16 bits)
    #     combined_pcm_data.extend(pcm_fragment)
    # print(combined_pcm_data)

    # # Now `combined_pcm_data` contains the PCM data from all the u-law fragments

    # # Save the combined PCM data to a WAV file
    # with wave.open('output.wav', 'wb') as wf:
    #     wf.setnchannels(1)  # Adjust based on the number of channels in your audio
    #     wf.setsampwidth(2)  # 2 bytes for 16-bit audio
    #     wf.setframerate(8000)  # Adjust based on the sample rate of your u-law audio
    #     wf.writeframes(combined_pcm_data)


    return 'Conversion successful'
    





if __name__ == '__main__':
    #run on port 5005
    app.run(host='localhost', port=5005)
