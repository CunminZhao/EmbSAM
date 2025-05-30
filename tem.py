import sounddevice as sd
import whisper
import numpy as np

# Load Whisper model
model = whisper.load_model("base")
samplerate = 16000
duration = 6  # seconds per chunk

# Name of VB-Cable Output device
target_device_name = "CABLE Output"
device_index = None

# Find the matching device index
for i, dev in enumerate(sd.query_devices()):
    if target_device_name.lower() in dev['name'].lower():
        device_index = i
        print(f"🎧 Using device: {dev['name']} (index {i})")
        break

if device_index is None:
    raise RuntimeError("❌ 'CABLE Output' not found. Make sure VB-Cable is installed and system routing is set.")

print("🟢 Listening to system sound... Press Ctrl+C to stop.")

try:
    while True:
        # Record a short audio block
        audio = sd.rec(int(duration * samplerate), samplerate=samplerate,
                       channels=1, device=device_index)
        sd.wait()
        audio = np.squeeze(audio)

        # Transcribe using Whisper (English only)
        result = model.transcribe(audio, language='en', fp16=False)
        # result = model.transcribe(audio, language='zh', fp16=False)

        text = result['text'].strip()
        if text:
            print("📝", text)

except KeyboardInterrupt:
    print("\n🛑 Stopped.")
