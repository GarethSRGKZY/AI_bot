import sys
import os
import json
import pyaudio
import keyboard
import replicate
import wave
import pywhisper as whisper
from promptmaker import *

#CLI for unicode characters to terminal
sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf8', buffering=1)

with open('repkey.txt', 'r') as key_file:
    key = key_file.read().strip()

os.environ["REPLICATE_API_TOKEN"] = key
API_KEY = os.environ["REPLICATE_API_TOKEN"]

conversation = []
history = {"history": conversation}

mode = 0
total_char = 0
chat = ""
chat_now = ""
prev_chat = ""
is_Speaking = False
owner_name = "Gareth"
name = "Haru"

def record_audio():
    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 44100
    WAVE_OUTPUT_FILENAME = "input.wav"
    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)
    frames = []
    print("Recording...")
    while keyboard.is_pressed('RIGHT_SHIFT'):
        data = stream.read(CHUNK)
        frames.append(data)
    print("Stopped recording.")
    stream.stop_stream()
    stream.close()
    p.terminate()
    wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()
    transcribe_audio("input.wav")

def transcribe_audio(file):
    global chat_now
    try:
        model = whisper.load_model("base")
        transcript = model.transcribe(file)
        chat_now = transcript["text"]
        print(chat_now)
    except Exception as e:
        print("Error transcribing audio: {0}".format(e))
        return
    
    result = owner_name + " said:" + chat_now
    conversation.append({'role': 'user', 'content': result})
    ai_answer()

def ai_answer():
    global total_char, conversation, chat_now
    
    total_char = sum(len(d['content']) for d in conversation)
    
    while total_char > 4000:
        try:
            conversation.pop(2)
            total_char = sum(len(d['content']) for d in conversation)
        except Exception as e:
            print("Error removing old messages: {0}".format(e))

    with open("conversation.json", "w", encoding="utf-8") as f:
        json.dump(history, f, indent=4)

    with open('background/background.txt', 'r') as background:
        context = background.read().strip()

    pre_prompt = context
    prompt_input = chat_now

    output = replicate.run(
    "meta/llama-2-70b-chat:02e509c789964a7ea8736978a43525956ef40397be9033abf9fd2badfe68c9e3",
    input={
        "debug": False,
        "top_k": 50,
        "top_p": 1,
        "prompt": f"{prompt_input}",
        "temperature": 0.5,
        "system_prompt": f"{pre_prompt}",
        "max_new_tokens": 500,
        "min_new_tokens": -1
        }
    )
    message = ""

    for item in output:
        message += item
    
    print(message)
    conversation.append({'role': f'{name}', 'content': message})

if __name__ == "__main__":
    try:
        print("Press and hold right shift to record audio")
        while True:
            if keyboard.is_pressed('RIGHT_SHIFT'):
                record_audio()
    except KeyboardInterrupt:
        print("Stopped")