from flask import Flask, Response,render_template
import pyaudio

app = Flask(__name__)


FORMAT = pyaudio.paInt16
CHANNELS = 2
RATE = 44100
CHUNK = 1024


audio1 = pyaudio.PyAudio()



def genHeader(sampleRate, bitsPerSample, channels):
    datasize = 2000*10**6
    o = bytes("RIFF",'ascii')                                               # (4byte) Marks file as RIFF
    o += (datasize + 36).to_bytes(4,'little')                               # (4byte) File size in bytes excluding this and RIFF marker
    o += bytes("WAVE",'ascii')                                              # (4byte) File type
    o += bytes("fmt ",'ascii')                                              # (4byte) Format Chunk Marker
    o += (16).to_bytes(4,'little')                                          # (4byte) Length of above format data
    o += (1).to_bytes(2,'little')                                           # (2byte) Format type (1 - PCM)
    o += (channels).to_bytes(2,'little')                                    # (2byte)
    o += (sampleRate).to_bytes(4,'little')                                  # (4byte)
    o += (sampleRate * channels * bitsPerSample // 8).to_bytes(4,'little')  # (4byte)
    o += (channels * bitsPerSample // 8).to_bytes(2,'little')               # (2byte)
    o += (bitsPerSample).to_bytes(2,'little')                               # (2byte)
    o += bytes("data",'ascii')                                              # (4byte) Data Chunk Marker
    o += (datasize).to_bytes(4,'little')                                    # (4byte) Data size in bytes
    return o


bitsPerSample = 16
wav_header = genHeader(RATE, bitsPerSample, CHANNELS)
stream = audio1.open(format=FORMAT, channels=CHANNELS,
                rate=RATE, input=True,input_device_index=0,
                frames_per_buffer=CHUNK)

info = audio1.get_host_api_info_by_index(0)
numdevices = info.get('deviceCount')
for i in range(0, numdevices):
  if (audio1.get_device_info_by_host_api_device_index(0,i).get('maxInputChannels')) > 0:
    print("Input Device id ", i, " - ", audio1.get_device_info_by_host_api_device_index(0, i).get('name'))

@app.route('/audio')
def audio():
    # start Recording
    def sound():
        #frames = []
        print("recording...")
        yield(wav_header)
        while True:
            audiodata = stream.read(CHUNK)
            yield(audiodata)

    return Response(sound())

@app.route('/')
def index():
    """Video streaming home page."""
    return render_template('index.html')


if __name__ == "__main__":
    app.run(host='0.0.0.0', threaded=True, port=8080)