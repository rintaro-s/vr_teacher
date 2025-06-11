import requests
import base64
import json

def send_image_prompt_to_lmstudio():
    # 画像をbase64エンコード
    with open("./image.png", "rb") as image_file:
        image_data = base64.b64encode(image_file.read()).decode('utf-8')
    
    # リクエストデータ
    data = {
        "model": "gemma-3-12b-it",
        "messages": [
            {
                "role": "system",
                "content": "You are a helpful assistant that can analyze images."
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "この画像について説明してください。"
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{image_data}"
                        }
                    }
                ]
            }
        ],
        "temperature": 0.7,
        "max_tokens": -1,
        "stream": False
    }
    
    # LMStudioへリクエスト送信
    response = requests.post(
        "http://localhost:1234/v1/chat/completions",
        headers={"Content-Type": "application/json"},
        json=data
    )
    
    # レスポンス表示
    if response.status_code == 200:
        result = response.json()
        print(result["choices"][0]["message"]["content"])
    else:
        print(f"Error: {response.status_code}")
        print(response.text)

if __name__ == "__main__":
    send_image_prompt_to_lmstudio()