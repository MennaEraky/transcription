import streamlit as st
import os
import whisper
import moviepy.editor as mp
import speech_recognition as sr
import google.generativeai as genai
from youtube_transcript_api import YouTubeTranscriptApi
from pytube import YouTube
from dotenv import load_dotenv
import streamlit as st

# Load environment variables from .env
load_dotenv()

# Access API key
google_api_key = os.getenv("GOOGLE_API_KEY")

if not google_api_key:
    st.error("GOOGLE_API_KEY is missing. Please add it to your .env file or Streamlit secrets.")

# Load Whisper model
model = whisper.load_model("base")

# Gemini model for summarization
gemini = genai.GenerativeModel(model_name="gemini-1.5-flash")

def transcribe_audio(audio_path):
    """Transcribe audio using Whisper."""
    result = model.transcribe(audio_path)
    return result["text"]

def transcribe_youtube(video_url):
    """Extract transcript from a YouTube video."""
    try:
        video_id = video_url.split("v=")[1].split("&")[0]
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        return " ".join([line["text"] for line in transcript])
    except Exception as e:
        return str(e)

def summarize_text(text):
    """Summarize text using Gemini AI."""
    response = gemini.generate_content(f"Summarize this: {text}")
    return response.text if response.text else "Error in summarization"

def extract_audio(video_path, output_audio):
    """Extract audio from video and save as a WAV file."""
    video = mp.VideoFileClip(video_path)
    if video.audio is not None:
        video.audio.write_audiofile(output_audio)
        return output_audio
    return None

# Streamlit UI
st.title("🎤 YouTube & Video Transcriber")

option = st.radio("Choose Input Method:", ["YouTube Link", "Upload Video"])

if option == "YouTube Link":
    video_url = st.text_input("Enter YouTube URL:")
    if st.button("Transcribe YouTube Video") and video_url:
        transcript = transcribe_youtube(video_url)
        st.text_area("Transcript:", transcript, height=200)
        if st.button("Summarize Transcript"):
            summary = summarize_text(transcript)
            st.text_area("Summary:", summary, height=150)

elif option == "Upload Video":
    uploaded_file = st.file_uploader("Upload a Video File", type=["mp4", "mov", "avi"])
    if uploaded_file:
        temp_video_path = "temp_video.mp4"
        with open(temp_video_path, "wb") as f:
            f.write(uploaded_file.read())
        
        st.video(temp_video_path)
        audio_path = "temp_audio.wav"
        if extract_audio(temp_video_path, audio_path):
            transcript = transcribe_audio(audio_path)
            st.text_area("Transcript:", transcript, height=200)
            if st.button("Summarize Transcript"):
                summary = summarize_text(transcript)
                st.text_area("Summary:", summary, height=150)
        else:
            st.error("This video does not contain an audio stream.")
