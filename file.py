import wave
import audioop
import wave
import audioop

def convert_ulaw_to_wave(x):
    # Decode and combine u-law fragments into a single bytearray
    combined_pcm_data = bytearray()
    ulaw_data = bytes(x['data'])


    # Decode the u-law data to 16-bit linear PCM
    pcm_data = audioop.ulaw2lin(ulaw_data, 2)
   

    # Save the combined PCM data to a WAV file
    with wave.open('output.wav', 'wb') as wf:
        wf.setnchannels(1)  # Adjust based on the number of channels in your audio
        wf.setsampwidth(2)  # 2 bytes for 16-bit audio
        wf.setframerate(8000)  # Adjust based on the sample rate of your u-law audio
        wf.writeframes(pcm_data)
