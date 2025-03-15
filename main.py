from datetime import datetime
from flask import Flask, request, Response, jsonify
from flask_cors import CORS 
import json
import requests


def extractprompt(messages):
    user_messages = [msg["content"] for msg in messages if msg.get("role") == "user"]
    return user_messages[-1] if user_messages else None



def glider_AI(user_prompt: str, system_prompt: str, model_name: str, stream: bool = False):
    models = {
        "deepseek-r1": "deepseek-ai/DeepSeek-R1",
        "Lama_3.1_70_3b": "chat-llama-3-1-70b",
        "Lama_3.1_8b": "chat-llama-3-1-8b",
        "Lama_3.2_3b": "chat-llama-3-2-3b"
    }

    url = "https://glider.so/api/chat"
    current_time = datetime.utcnow().isoformat()
    
    payload = {
        "messages": [
            {
                "role": "system",
                "content": system_prompt,
                "id": "system-adbb88b5-7f0c-4ad2-a5ea-aa755f34b127",
                "chatId": "adbb88b5-7f0c-4ad2-a5ea-aa755f34b127",
                "createdOn": current_time,
                "model": None
            },
            {
                "role": "user",
                "content": user_prompt,
                "id": "f3974f85-0147-497a-9e9e-321f8d6e9548",
                "chatId": "adbb88b5-7f0c-4ad2-a5ea-aa755f34b127",
                "createdOn": current_time,
                "model": None
            }
        ],
        "model": models[model_name]
    }

    headers = {
        "accept": "*/*",
        "accept-encoding": "gzip, deflate, br, zstd",
        "accept-language": "en-US,en;q=0.9,hi;q=0.8,ca;q=0.7",
        "cache-control": "no-cache",
        "content-type": "text/plain;charset=UTF-8",
        "origin": "https://glider.so",
        "pragma": "no-cache",
        "priority": "u=1, i",
        "referer": f"https://glider.so/?model={models[model_name]}",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "user-agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1"
    }

    response = requests.post(url, json=payload, headers=headers, stream=stream)
    
    if stream:
        # When streaming, yield each token as a data chunk
        try:
            for line in response.iter_lines():
                if line:
                    decoded_line = line.decode('utf-8')
                    if decoded_line.startswith('data: '):
                        json_str = decoded_line[6:]
                        if json_str.strip() == '[DONE]':
                            break
                        try:
                            data = json.loads(json_str)
                            if data.get('choices') and data['choices'][0].get('delta'):
                                token = data['choices'][0]['delta'].get('content', '')
                                yield f"data: {json.dumps({'choices': [{'delta': {'content': token}, 'index': 0, 'finish_reason': None}]})}\n\n"
                        except json.JSONDecodeError:
                            continue
        except requests.RequestException as e:
            yield f"data: {json.dumps({'error': f'Request error: {e}'})}\n\n"
    else:
        # Otherwise, accumulate the full content and yield it once
        content = ""
        for line in response.iter_lines():
            if line:
                decoded_line = line.decode('utf-8')
                if decoded_line.startswith('data: '):
                    json_str = decoded_line[6:]
                    if json_str.strip() == '[DONE]':
                        break
                    try:
                        data = json.loads(json_str)
                        if 'choices' in data and len(data['choices']) > 0:
                            delta = data['choices'][0]['delta']
                            if 'content' in delta and delta['content']:
                                content += delta['content']
                    except json.JSONDecodeError:
                        continue
        yield content

def Duck_Duck_GO_AI(user_prompt: str, system_prompt: str, model_name: str, stream: bool = False):
    models = {
        "o3-mini": "o3-mini",
        "gpt-4o-mini": "gpt-4o-mini",
        "Llama-3.3-70B": "meta-llama/Llama-3.3-70B-Instruct-Turbo",
        "Mistral-Small-24B": "mistralai/Mistral-Small-24B-Instruct-2501",
        "claude-3-haiku": "claude-3-haiku-20240307"
    }
    
    if model_name not in models:
        raise ValueError(f"Invalid model name. Available models: {', '.join(models.keys())}")
    
    url = "https://duckduckgo.com/duckchat/v1/chat"
    
    messages = []
    if system_prompt and system_prompt.lower() != "null":
        messages.append({"role": "system", "content": system_prompt.strip()})
    messages.append({"role": "user", "content": user_prompt.strip()})
    
    payload = {
        "model": models[model_name],
        "messages": messages
    }
    
    headers = {
        "accept": "text/event-stream",
        "content-type": "application/json",
        "origin": "https://duckduckgo.com",
        "referer": "https://duckduckgo.com/",
        "user-agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1",
        "x-vqd-4": "4-160660798361061570846998069616167908400" ,# Update this token if expired
        "x-vqd-hash-1":"eyJzZXJ2ZXJfaGFzaGVzIjpbIlZaOVQ1SnV4R3R3WlFiOHo0eGQ3VXg3WC90YXEwcy8waEQ3UmRsSksrSnM9IiwicUI4VzJ0cGUyVUN6a21GTWFyVXpXTGQxQWxLdUY1cEFuZHIraXpKVFdQWT0iXSwiY2xpZW50X2hhc2hlcyI6WyJHS3YxSzNQUXVKRmZOY3pRdlprK0N2MWV3U3R1OHdSMXdKamNDTUFzVm1vPSIsIlpWQzlqUWlxSEJwWHZHdWdoaFlIWHJrTFVIVzg3UnlDVkMzWmFhekRZR0E9Il0sInNpZ25hbHMiOnt9fQ=="
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers, stream=True)
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        yield f"data: {json.dumps({'error': f'HTTP Error: {e.response.status_code} - {e.response.text}'})}\n\n"
        return
    except requests.RequestException as e:
        yield f"data: {json.dumps({'error': str(e)})}\n\n"
        return
    
    if stream:
        try:
            for line in response.iter_lines():
                if line:
                    decoded_line = line.decode('utf-8')
                    if decoded_line.startswith('data: '):
                        json_str = decoded_line[6:]
                        if json_str.strip() == '[DONE]':
                            break
                        try:
                            data = json.loads(json_str)
                            if "message" in data:
                                chunk = data["message"]
                                yield f"data: {json.dumps({'choices': [{'delta': {'content': chunk}, 'index': 0, 'finish_reason': None}]})}\n\n"
                        except json.JSONDecodeError:
                            continue
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
    else:
        full_response = ""
        try:
            for line in response.iter_lines():
                if line:
                    decoded_line = line.decode('utf-8')
                    if decoded_line.startswith('data: '):
                        json_str = decoded_line[6:]
                        if json_str.strip() == '[DONE]':
                            break
                        try:
                            data = json.loads(json_str)
                            if "message" in data:
                                full_response += data["message"]
                        except json.JSONDecodeError:
                            continue
        except Exception as e:
            full_response = f"Error during processing: {str(e)}"
        yield full_response

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

@app.route("/v1/chat/completions", methods=["POST"])
def chat_completions():
    try:
        data = request.get_json()
        messages = data.get("messages", [])
        model = data.get("model", "")

        if not messages:
            return jsonify({"error": "No messages provided"}), 400

        # Simplified message processing
        user_prompt = extractprompt(messages)

        # Model routing
        glider_models = {
        "deepseek-r1": "deepseek-ai/DeepSeek-R1",
        "Lama_3.1_70_3b": "chat-llama-3-1-70b",
        "Lama_3.1_8b": "chat-llama-3-1-8b",
        "Lama_3.2_3b": "chat-llama-3-2-3b"
    }
        duck_models = {
        "o3-mini": "o3-mini",
        "gpt-4o-mini": "gpt-4o-mini",
        "Llama-3.3-70B": "meta-llama/Llama-3.3-70B-Instruct-Turbo",
        "Mistral-Small-24B": "mistralai/Mistral-Small-24B-Instruct-2501",
        "claude-3-haiku": "claude-3-haiku-20240307"
    }
        stream = True
        if model in glider_models:
            generator = glider_AI(user_prompt, "", model, stream)
        elif model in duck_models:
            generator = Duck_Duck_GO_AI(user_prompt, "", model, stream)
        else:
            return jsonify({"error": f"Model {model} not supported"}), 400

        if stream:
            def generate():
                for chunk in generator:
                    yield chunk
                yield "data: [DONE]\n\n"
            return Response(generate(), mimetype="text/event-stream")
        else:
            return jsonify({
                "choices": [{
                    "message": {"content": "".join(generator)}
                }]
            })

    except Exception as e:
        app.logger.error(f"Server error: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route("/", methods=["POST"])
def chat_completions_stream():
    return jsonify({"error": "server is not working"})

if __name__ == "__main__":
    app.run(host="0.0.0.0",port=os.getenv("PORT", default=5000), debug=True)
