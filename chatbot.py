import gradio as gr
from gradio import ChatMessage
import time
import json
import os
import requests

# Set file path
SETTINGS_FILE = "settings.json"

# Load settings
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

# Validate API configuration
def validate_api(api_url, api_key):
    import re
    # Check if API URL is valid
    if not api_url:
        return "❌ API URL is required"
    # Basic URL validation
    url_pattern = re.compile(r'^https?://[\w\-]+(\.[\w\-]+)+([\w\-\.,@?^=%&:/~\+#]*[\w\-\@?^=%&/~\+#])?$')
    if not url_pattern.match(api_url):
        return "❌ Invalid API URL format"
    # Check if API key is provided
    if not api_key:
        return "❌ API Key is required"
    return "✅ API configuration is valid"

def get_model_list(base_url, api_key):
    """
    输入 Base URL 和 API Key，返回模型 ID 列表
    """
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

# Check available models from API
def check_available_models(api_url, api_key):
    # Validate API first
    validation_result = validate_api(api_url, api_key)
    if "❌" in validation_result:
        return gr.update(choices=[]), validation_result
    
    # Get model list using the new function
    model_list = get_model_list(api_url, api_key)
    
    # Check if the result is an error message (string) or successful list
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

# Save settings
def save_settings(model, temperature, top_p, max_length, system_prompt, api_url, api_key):
    # Validate API first
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



# [User Replacement Area: Connect to actual LLM API here]
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

def predict(message, history, model=None, temperature=0.0, top_p=0.0, max_length=1024, system_prompt="You are a professional, friendly AI assistant"):
    """Connect to actual LLM API for generating responses"""
    if not message:
        return history, ""

    history = list(history)

    if not model:
        history.append({"role": "assistant", "content": "⚠️ Please select a model in Advanced Settings first."})
        return history, ""

    history.append({"role": "user", "content": message})

    settings = load_settings()
    api_url = settings.get("api_url", "")
    api_key = settings.get("api_key", "")

    if not api_url or not api_key:
        history.append({"role": "assistant", "content": "⚠️ API URL and Key are required. Please configure them in Advanced Settings."})
        return history, ""

    api_url = api_url.rstrip('/')
    if not api_url.endswith('/chat/completions'):
        api_url = api_url + "/chat/completions"

    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})

    for msg in history[:-1]:
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

    history.append({"role": "assistant", "content": response_content})

    return history, ""

def handle_undo(history, undo_data: gr.UndoData):
    index = undo_data.index
    if index > 0 and index <= len(history):
        prev_msg = history[index - 1]
        if isinstance(prev_msg, dict) and prev_msg.get("role") == "user":
            content = prev_msg.get("content", "")
            if isinstance(content, list):
                text_parts = []
                files = []
                for item in content:
                    if isinstance(item, dict):
                        if item.get("type") == "text":
                            text_parts.append(item.get("text", ""))
                        elif item.get("type") == "file":
                            files.append(item)
                user_msg = "\n".join(text_parts)
                new_history = history[:index - 1]
                if files and user_msg:
                    new_content = [{"type": "text", "text": user_msg}] + files
                    new_history.append({"role": "user", "content": new_content})
                    return new_history, ""
                elif user_msg:
                    return new_history, user_msg
                else:
                    return new_history, ""
            else:
                user_msg = str(content) if content else ""
            new_history = history[:index - 1]
            return new_history, user_msg
    raw_value = undo_data.value if undo_data.value else ""
    if isinstance(raw_value, list):
        text_parts = []
        for item in raw_value:
            if isinstance(item, dict) and item.get("type") == "text":
                text_parts.append(item.get("text", ""))
        user_msg = "\n".join(text_parts)
    else:
        user_msg = str(raw_value) if raw_value else ""
    new_history = history[:index]
    return new_history, user_msg

def handle_retry(history, retry_data: gr.RetryData, model, temperature, top_p, max_length, system_prompt):
    index = retry_data.index
    content = history[index]['content']
    if isinstance(content, list):
        previous_prompt = ""
        for item in content:
            if isinstance(item, dict) and item.get("type") == "text":
                previous_prompt = item.get("text", "")
                break
    else:
        previous_prompt = content

    new_history = history[:index]
    new_history.append({"role": "user", "content": previous_prompt})
    yield new_history, ""

    new_history.append({"role": "assistant", "content": "⏳ Retrying..."})
    yield new_history, ""

    result = predict(previous_prompt, new_history[:-1], model, temperature, top_p, max_length, system_prompt)
    yield result[0], ""

def handle_edit(history, edit_data: gr.EditData):
    new_history = history[:edit_data.index]
    if new_history and isinstance(new_history[-1], dict) and new_history[-1].get("role") == "assistant":
        new_history.pop()
    return new_history

def handle_like(data: gr.LikeData):
    pass

def send_message(message, history, model, temperature, top_p, max_length, system_prompt):
    if not message:
        return history, ""
    
    history.append({"role": "user", "content": message})
    yield history, ""
    
    result = predict(message, history[:-1], model, temperature, top_p, max_length, system_prompt)
    yield result[0], ""

# Create Gradio interface
with gr.Blocks(title="PsyClaw") as demo:
    # 1️⃣ Top Header Area
    with gr.Row(elem_id="header", equal_height=True):
        gr.Markdown("# PsyClaw", elem_id="main-title")
    
    # 2️⃣ Chat History Area (Core Area)
    chatbot = gr.Chatbot(
        elem_id="chatbot",
        label="Chat History",
        height=500,
        avatar_images=("user", "assistant"),
        placeholder="💬 Start your conversation～",
        allow_tags=False,
        editable=True
    )
    
    # 3️⃣ Input Control Area (Horizontal Compact Layout)
    with gr.Column(elem_id="input-area"):
        with gr.Row():
            message_input = gr.Textbox(
                label="Input Message",
                placeholder="Enter message... (Press Enter to send, Shift+Enter for new line)",
                # lines=3,
                max_lines=10,
                elem_id="message-input",
                scale=8
            )
            file_upload = gr.File(
                label="Upload",
                elem_id="file-upload",
                scale=5
            )
        with gr.Row():
            send_btn = gr.Button("📤 Send", elem_id="send-button")
    
    # Load initial settings
    initial_settings = load_settings()
    
    # 4️⃣ Advanced Settings Panel (Collapsible)
    with gr.Accordion("⚙️ Advanced Settings", open=False, elem_id="advanced-settings"):
        # API Configuration Section
        gr.Markdown("### API Configuration")
        api_url_input = gr.Textbox(
            label="API URL",
            value=initial_settings["api_url"],
            placeholder="Enter API URL, e.g.: https://api.openai.com/v1/chat/completions",
            elem_id="api-url-input"
        )
        api_key_input = gr.Textbox(
            label="API Key",
            value=initial_settings["api_key"],
            type="password",
            placeholder="Enter API key",
            elem_id="api-key-input"
        )
        
        # Check API configuration button
        check_api_btn = gr.Button("Check", elem_id="check-api-button")
        save_status = gr.Markdown("", elem_id="save-status")
        
        # Model Configuration
        gr.Markdown("### Model Configuration")
        model_dropdown = gr.Dropdown(
            label="Model Selection",
            choices=[],
            value=initial_settings["model"],
            elem_id="model-select"
        )
        
        # Model Parameters
        gr.Markdown("### Generation Parameters")
        temperature_slider = gr.Slider(
            label="Temperature (Creativity)",
            minimum=0.0,
            maximum=1.0,
            step=0.1,
            value=initial_settings["temperature"],
            elem_id="temperature-slider"
        )
        top_p_slider = gr.Slider(
            label="Top-p (Sampling Range)",
            minimum=0.0,
            maximum=1.0,
            step=0.05,
            value=initial_settings["top_p"],
            elem_id="top-p-slider"
        )
        max_length_slider = gr.Slider(
            label="Max Generation Length",
            minimum=128,
            maximum=4096,
            step=128,
            value=initial_settings["max_length"],
            elem_id="max-length-slider"
        )
        system_prompt_input = gr.Textbox(
            label="System Prompt",
            value=initial_settings["system_prompt"],
            lines=3,
            placeholder="Enter system prompt to guide AI behavior and style",
            elem_id="system-prompt-input"
        )
    
    # 5️⃣ Status Feedback Layer
    status_message = gr.Markdown("", elem_id="status-message")

    # Key interaction logic

    # Bind events
    send_event = send_btn.click(
        send_message,
        inputs=[message_input, chatbot, model_dropdown, temperature_slider, top_p_slider, max_length_slider, system_prompt_input],
        outputs=[chatbot, message_input]
    )

    # Enter key to send message
    message_input.submit(
        send_message,
        inputs=[message_input, chatbot, model_dropdown, temperature_slider, top_p_slider, max_length_slider, system_prompt_input],
        outputs=[chatbot, message_input]
    )

    # Auto-check API configuration on page load
    demo.load(
        check_available_models,
        inputs=[api_url_input, api_key_input],
        outputs=[model_dropdown, save_status]
    )
    

    
    # File upload (placeholder)
    def handle_upload(file):
        if file is None:
            return ""
        return f"File uploaded: {file.name}"

    file_upload.upload(
        handle_upload,
        inputs=[file_upload],
        outputs=[status_message]
    )

    # Check API configuration and update model list
    check_api_btn.click(
        check_available_models,
        inputs=[api_url_input, api_key_input],
        outputs=[model_dropdown, save_status]
    )

    chatbot.undo(handle_undo, chatbot, [chatbot, message_input])
    chatbot.retry(handle_retry, [chatbot, model_dropdown, temperature_slider, top_p_slider, max_length_slider, system_prompt_input], [chatbot, message_input])
    chatbot.like(handle_like, None, None)
    chatbot.edit(handle_edit, chatbot, chatbot)

# Launch the application
demo.launch(share=False)