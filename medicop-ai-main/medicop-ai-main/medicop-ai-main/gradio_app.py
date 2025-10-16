import os
import gradio as gr
from brain_of_the_doctor import encode_image, analyze_image_with_query
from voice_of_the_patient import transcribe_with_groq
from voice_of_the_doctor import text_to_speech_with_gtts  # Using gTTS

system_prompt = """You have to act as a professional doctor..."""

conversation_history = []

def process_inputs(audio_filepath, image_filepath):
    if audio_filepath is None:
        return "No audio", "No audio file found", "final.mp3", conversation_history

    speech_to_text_output = transcribe_with_groq(
        GROQ_API_KEY=os.environ.get("GROQ_API_KEY"),
        audio_filepath=audio_filepath,
        stt_model="whisper-large-v3"
    )

    if image_filepath:
        doctor_response = analyze_image_with_query(
            query=system_prompt + speech_to_text_output,
            encoded_image=encode_image(image_filepath),
            model="meta-llama/llama-4-scout-17b-16e-instruct"
        )
    else:
        doctor_response = "No image provided to analyze."

    voice_of_doctor = text_to_speech_with_gtts(
        input_text=doctor_response,
        output_filepath="final.mp3"
    )

    conversation_history.append(("👤: " + speech_to_text_output, "🩺: " + doctor_response))

    return speech_to_text_output, doctor_response, "final.mp3", conversation_history

def reset_chat():
    conversation_history.clear()
    return "", "", "final.mp3", []

# --------------------------- UI Layout ---------------------------

with gr.Blocks(css="""
body { background-color: #0f172a; color: #ffffff; font-family: 'Segoe UI', sans-serif; }
.gr-button { background: linear-gradient(to right, #38bdf8, #2563eb); color: white; font-weight: bold; border-radius: 6px; }
""") as demo:
    
    gr.Markdown("<h1 style='text-align:center;'>🩺 AI Doctor with Vision & Voice</h1>")
    gr.Markdown("<p style='text-align:center;'>Describe your symptoms and upload a photo. The AI Doctor will respond with expert advice and voice.</p>")

    with gr.Row():
        with gr.Column(scale=1):
            gr.Image(value="https://cdn-icons-png.flaticon.com/512/3774/3774299.png", label="👨‍⚕️ Doctor", interactive=False)
        with gr.Column(scale=2):
            audio_input = gr.Audio(sources=["microphone"], type="filepath", label="🎙️ Speak Your Symptoms")
            image_input = gr.Image(type="filepath", label="📷 Upload Medical Image")
            submit_btn = gr.Button("🧠 Get Diagnosis")
            new_chat_btn = gr.Button("🧼 New Chat")

    with gr.Row():
        output_text = gr.Textbox(label="📝 Transcribed Speech")
        doctor_text = gr.Textbox(label="👨‍⚕️ Doctor's Diagnosis")
        voice_output = gr.Audio(label="🔊 Voice Response")

    chatbox = gr.Chatbot(label="💬 Chat History", height=300)

    submit_btn.click(
        fn=process_inputs,
        inputs=[audio_input, image_input],
        outputs=[output_text, doctor_text, voice_output, chatbox]
    )

    new_chat_btn.click(
        fn=reset_chat,
        inputs=[],
        outputs=[output_text, doctor_text, voice_output, chatbox]
    )

demo.launch(debug=True)
