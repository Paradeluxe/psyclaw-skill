import gradio as gr
from gradio import ChatMessage
import time
import json
import os

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
        "api_key": "",
        "saved_settings": {}
    }

# Save settings
def save_settings(model, temperature, top_p, max_length, system_prompt, api_url, api_key):
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
    return "Settings saved"

# Save as preset
def save_as_preset(preset_name, model, temperature, top_p, max_length, system_prompt, api_url, api_key):
    settings = load_settings()
    settings["saved_settings"][preset_name] = {
        "model": model,
        "temperature": temperature,
        "top_p": top_p,
        "max_length": max_length,
        "system_prompt": system_prompt,
        "api_url": api_url,
        "api_key": api_key
    }
    with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
        json.dump(settings, f, indent=2, ensure_ascii=False)
    return f"Preset '{preset_name}' saved"

# Load preset
def load_preset(preset_name):
    settings = load_settings()
    if preset_name in settings["saved_settings"]:
        preset = settings["saved_settings"][preset_name]
        return (
            preset["model"],
            preset["temperature"],
            preset["top_p"],
            preset["max_length"],
            preset["system_prompt"],
            preset["api_url"],
            preset["api_key"]
        )
    return None

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
        # Organize settings with tabs
        with gr.Tabs():
            # Preset Management tab
            with gr.Tab("Preset Management"):
                gr.Markdown("### Preset Configuration")
                preset_dropdown = gr.Dropdown(
                    label="Select Preset",
                    choices=["Default"] + list(initial_settings["saved_settings"].keys()),
                    value="Default",
                    elem_id="preset-select"
                )
                gr.Markdown("### Model Configuration")
                model_dropdown = gr.Dropdown(
                    label="Model Selection",
                    choices=["gpt-4o", "claude-3-5", "Local Model"],
                    value=initial_settings["model"],
                    elem_id="model-select"
                )
                gr.Markdown("### Save Preset")
                with gr.Row():
                    preset_name_input = gr.Textbox(
                        label="Preset Name",
                        placeholder="Enter preset name",
                        elem_id="preset-name-input"
                    )
                    save_preset_btn = gr.Button("💾 Save as Preset", elem_id="save-preset-button")
            
            # API Settings tab
            with gr.Tab("API Settings"):
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
            
            # Model Parameters tab
            with gr.Tab("Model Parameters"):
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
        
        # Save settings button (below all tabs)
        with gr.Row():
            save_btn = gr.Button("💾 Save Settings", elem_id="save-button")
        save_status = gr.Markdown("", elem_id="save-status")
    
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

    # Save settings
    save_btn.click(
        save_settings,
        inputs=[model_dropdown, temperature_slider, top_p_slider, max_length_slider, system_prompt_input, api_url_input, api_key_input],
        outputs=[save_status]
    )
    
    # Save as preset
    save_preset_btn.click(
        save_as_preset,
        inputs=[preset_name_input, model_dropdown, temperature_slider, top_p_slider, max_length_slider, system_prompt_input, api_url_input, api_key_input],
        outputs=[save_status]
    )
    
    # Load preset
    def update_preset_choices():
        settings = load_settings()
        return gr.Dropdown.update(
            choices=["Default"] + list(settings["saved_settings"].keys())
        )
    
    def load_selected_preset(preset_name):
        if preset_name == "Default":
            settings = load_settings()
            return (
                settings["model"],
                settings["temperature"],
                settings["top_p"],
                settings["max_length"],
                settings["system_prompt"],
                settings["api_url"],
                settings["api_key"]
            )
        else:
            result = load_preset(preset_name)
            if result:
                return result
            else:
                # If preset doesn't exist, return current values
                return (
                    model_dropdown.value,
                    temperature_slider.value,
                    top_p_slider.value,
                    max_length_slider.value,
                    system_prompt_input.value,
                    api_url_input.value,
                    api_key_input.value
                )
    
    # Update preset dropdown after saving preset
    save_preset_btn.click(
        update_preset_choices,
        inputs=[],
        outputs=[preset_dropdown]
    )
    
    # Load settings when preset is selected
    preset_dropdown.change(
        load_selected_preset,
        inputs=[preset_dropdown],
        outputs=[model_dropdown, temperature_slider, top_p_slider, max_length_slider, system_prompt_input, api_url_input, api_key_input]
    )

# Launch the application
demo.launch(share=False)