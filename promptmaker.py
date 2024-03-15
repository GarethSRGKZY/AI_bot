import json
import sys

sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf8', buffering=1)

def background(background_path):
    with open(background_path, 'r', encoding='utf-8') as f:
        context = f.read()
    return {"role": "user", "content": context}

def getPrompt():
    total_len = 0
    prompt = []
    prompt.append(background("background/background.txt"))
    prompt.append({"role": "system", "content": f"Below is the conversation history:\n"})

    with open("conversation.json", "r") as f:
        data = json.load(f)
    
    history = data["history"]
    for message in history[:-1]:
        prompt.append(message)

    prompt.append(
        {
            "role": "system",
            "content": f"Below is the latest conversation history:\n"
        }
    )

    prompt.append(history[-1])

    total_len = sum(len(d["content"]) for d in prompt)

    while total_len > 4000:
        try:
            prompt.pop(2)
            total_len = sum(len(d["content"]) for d in prompt)
        except:
            print("Prompt is too long")
    
    return prompt

if __name__ == "__main__":
    prompt = getPrompt()
    print(prompt)
    print(len(prompt))
