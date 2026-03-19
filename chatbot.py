import gradio as gr
import time
import json
import os
import requests

SETTINGS_FILE = "settings.json"

def load_settings():
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            pass
    return {
        "model": None,
        "temperature": 0.0,
        "top_p": 0.0,
        "max_length": 1024,
        "system_prompt": "You are a professional, friendly AI assistant",
        "api_url": "",
        "api_key": ""
    }

def validate_api(api_url, api_key):
    import re
    if not api_url:
        return "❌ API URL is required"
    url_pattern = re.compile(r'^https?://[\w\-]+(\.[\w\-]+)+([\w\-\.,@?^=%&:/~\+#]*[\w\-\@?^=%&/~\+#])?$')
    if not url_pattern.match(api_url):
        return "❌ Invalid API URL format"
    if not api_key:
        return "❌ API Key is required"
    return "✅ API configuration is valid"

def get_model_list(base_url, api_key):
    base_url = base_url.rstrip('/')
    if not base_url.endswith('/models'):
        url = f"{base_url}/models"
    else:
        url = base_url

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        all_models = [model.get('id') for model in data.get('data', [])]
        return all_models
    except requests.exceptions.RequestException as e:
        return f"请求失败: {e}"
    except Exception as e:
        return f"解析失败: {e}"

def check_available_models(api_url, api_key):
    validation_result = validate_api(api_url, api_key)
    if "❌" in validation_result:
        return gr.update(choices=[]), validation_result

    model_list = get_model_list(api_url, api_key)

    if isinstance(model_list, str):
        return gr.update(choices=[]), f"❌ {model_list}"
    elif isinstance(model_list, list) and len(model_list) > 0:
        priority_models = ["qwen3.5-flash", "qwen3.5-plus"]
        default_model = None
        for pm in priority_models:
            if pm in model_list:
                default_model = pm
                break
        if default_model is None and len(model_list) > 0:
            default_model = model_list[0]
        return gr.update(choices=model_list, value=default_model), f"✅ Found {len(model_list)} available models"
    else:
        return gr.update(choices=[]), "⚠️ No models found or unexpected response format"

def save_settings(model, temperature, top_p, max_length, system_prompt, api_url, api_key):
    validation_result = validate_api(api_url, api_key)
    if "❌" in validation_result:
        return validation_result

    settings = load_settings()
    settings.update({
        "model": model,
        "temperature": temperature,
        "top_p": top_p,
        "max_length": max_length,
        "system_prompt": system_prompt,
        "api_url": api_url,
        "api_key": api_key
    })
    with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
        json.dump(settings, f, indent=2, ensure_ascii=False)
    return "✅ Settings saved successfully"

def _validate_message(msg):
    if isinstance(msg, dict):
        role = msg.get("role")
        content = msg.get("content")
        if isinstance(role, str) and role in ("system", "user", "assistant") and isinstance(content, str):
            return {"role": role, "content": content}
    elif hasattr(msg, "role") and hasattr(msg, "content"):
        role = getattr(msg, "role", None)
        content = getattr(msg, "content", None)
        if isinstance(role, str) and role in ("system", "user", "assistant") and isinstance(content, str):
            return {"role": role, "content": content}
    return None

def predict(message, history, model, temperature, top_p, max_length, system_prompt):
    """ChatInterface compatible predict function"""
    if not message:
        return ""

    if not model:
        return "⚠️ Please select a model in Advanced Settings first."

    settings = load_settings()
    api_url = settings.get("api_url", "")
    api_key = settings.get("api_key", "")

    if not api_url or not api_key:
        return "⚠️ API URL and Key are required. Please configure them in Advanced Settings."

    api_url = api_url.rstrip('/')
    if not api_url.endswith('/chat/completions'):
        api_url = api_url + "/chat/completions"

    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})

    for msg in history:
        validated = _validate_message(msg)
        if validated:
            messages.append(validated)

    messages.append({"role": "user", "content": message})

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "top_p": top_p,
        "max_tokens": max_length
    }

    try:
        response = requests.post(api_url, headers=headers, json=payload, timeout=60)
        response.raise_for_status()
        result = response.json()

        if "choices" in result and len(result["choices"]) > 0:
            response_content = result["choices"][0]["message"]["content"]
        else:
            response_content = "⚠️ Unexpected response format from API"

    except requests.exceptions.RequestException as e:
        response_content = f"❌ API request failed: {str(e)}"
    except Exception as e:
        response_content = f"❌ Error processing response: {str(e)}"

    return response_content

with gr.Blocks(title="PsyClaw") as demo:
    gr.Markdown("# PsyClaw")

    initial_settings = load_settings()

    with gr.Accordion("⚙️ Advanced Settings", open=False):
        gr.Markdown("### API Configuration")
        api_url_input = gr.Textbox(
            label="API URL",
            value=initial_settings["api_url"],
            placeholder="Enter API URL, e.g.: https://api.openai.com/v1/chat/completions"
        )
        api_key_input = gr.Textbox(
            label="API Key",
            value=initial_settings["api_key"],
            type="password",
            placeholder="Enter API key"
        )

        check_api_btn = gr.Button("Check")
        save_status = gr.Markdown("")

        gr.Markdown("### Model Configuration")
        model_dropdown = gr.Dropdown(
            label="Model Selection",
            choices=[],
            allow_custom_value=True
        )

        gr.Markdown("### Generation Parameters")
        temperature_slider = gr.Slider(
            label="Temperature (Creativity)",
            minimum=0.0,
            maximum=1.0,
            step=0.1,
            value=initial_settings["temperature"]
        )
        top_p_slider = gr.Slider(
            label="Top-p (Sampling Range)",
            minimum=0.0,
            maximum=1.0,
            step=0.05,
            value=initial_settings["top_p"]
        )
        max_length_slider = gr.Slider(
            label="Max Generation Length",
            minimum=128,
            maximum=4096,
            step=128,
            value=initial_settings["max_length"]
        )
        system_prompt_input = gr.Textbox(
            label="System Prompt",
            value=initial_settings["system_prompt"],
            lines=3,
            placeholder="Enter system prompt to guide AI behavior and style"
        )

    gr.Markdown("---")
    gr.Markdown("### Chat Interface")
    chat_interface = gr.ChatInterface(
        fn=predict,
        additional_inputs=[
            model_dropdown,
            temperature_slider,
            top_p_slider,
            max_length_slider,
            system_prompt_input
        ]
    )

    gr.Markdown("---")
    status_message = gr.Markdown("")

    demo.load(
        check_available_models,
        inputs=[api_url_input, api_key_input],
        outputs=[model_dropdown, save_status]
    )

    check_api_btn.click(
        check_available_models,
        inputs=[api_url_input, api_key_input],
        outputs=[model_dropdown, save_status]
    )

demo.launch(share=False)
