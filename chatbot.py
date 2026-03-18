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
        "model": "gpt-4o",
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
    # 自动处理 URL 拼接，确保指向 /models 路径
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
        # 发送 GET 请求
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status() # 检查 HTTP 状态码
        
        data = response.json()
        
        # 提取数据中每个模型的 'id' 字段
        models = [model.get('id') for model in data.get('data', [])]
        return models
        
    except requests.exceptions.RequestException as e:
        return f"请求失败: {e}"
    except Exception as e:
        return f"解析失败: {e}"

# Check available models from API
def check_available_models(api_url, api_key):
    # Validate API first
    validation_result = validate_api(api_url, api_key)
    if "❌" in validation_result:
        return gr.update(choices=["gpt-4o", "claude-3-5", "Local Model"]), validation_result
    
    # Get model list using the new function
    model_list = get_model_list(api_url, api_key)
    
    # Check if the result is an error message (string) or successful list
    if isinstance(model_list, str):
        # It's an error message
        return gr.update(choices=["gpt-4o", "claude-3-5", "Local Model"]), f"❌ {model_list}"
    elif isinstance(model_list, list) and len(model_list) > 0:
        # Successfully got model list
        return gr.update(choices=model_list), f"✅ Found {len(model_list)} available models"
    else:
        # Empty list or unexpected result
        return gr.update(choices=["gpt-4o", "claude-3-5", "Local Model"]), "⚠️ No models found or unexpected response format"

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
def predict(message, history, model="gpt-4o", temperature=0.0, top_p=0.0, max_length=1024, system_prompt="You are a professional, friendly AI assistant"):
    """Placeholder function to simulate LLM response"""
    # Simulate thinking process
    thinking_response = ChatMessage(
        content="",
        metadata={"status": "pending"}
    )
    yield thinking_response
    
    # Simulate generation process
    response_content = """
    This is a simulated AI response. In actual implementation, a real LLM API would be called here.
    
    You can adjust the response style based on the following settings:
    - Model: {model}
    - Temperature: {temperature}
    - Top-p: {top_p}
    - Max length: {max_length}
    - System prompt: {system_prompt}
    """.format(model=model, temperature=temperature, top_p=top_p, max_length=max_length, system_prompt=system_prompt)
    
    # Simulate streaming output
    for i in range(0, len(response_content), 5):
        time.sleep(0.05)
        thinking_response.content = response_content[:i+5]
        thinking_response.metadata["status"] = "done" if i+5 >= len(response_content) else "pending"
        yield thinking_response

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
        allow_tags=False
    )
    
    # 3️⃣ Input Control Area (Horizontal Compact Layout)
    with gr.Column(elem_id="input-area"):
        with gr.Row():
            message_input = gr.Textbox(
                label="Input Message",
                placeholder="Enter message... (Press Enter to send, Shift+Enter for new line)",
                lines=3,
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
            choices=["gpt-4o", "claude-3-5", "Local Model"],
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
        predict,
        inputs=[message_input, chatbot, model_dropdown, temperature_slider, top_p_slider, max_length_slider, system_prompt_input],
        outputs=[chatbot]
    )
    
    # Enter key to send message
    message_input.submit(
        predict,
        inputs=[message_input, chatbot, model_dropdown, temperature_slider, top_p_slider, max_length_slider, system_prompt_input],
        outputs=[chatbot]
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
    

    


# Launch the application
demo.launch(share=False)