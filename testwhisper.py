import pywhisper as whisper

model = whisper.load_model("base")
result = model.transcribe("input.wav")
print(result["text"])