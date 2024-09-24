from flask import Flask, request, jsonify
from flask_cors import CORS
from youtube_transcript_api import YouTubeTranscriptApi
from dotenv import load_dotenv
import os
import google.generativeai as genai

load_dotenv()

app = Flask(__name__)
CORS(app)   

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

prompt = """You are a YouTube video summarizer. You will be taking the transcript text
and summarizing the entire video and providing the important summary in points
within 10% words. Please provide the summary on the basis of the text that is given here:  """

def extract_transcript_details(youtube_video_url):
    try:
        video_id = youtube_video_url.split("=")[1]
        transcript_text = YouTubeTranscriptApi.get_transcript(video_id)
        transcript = " ".join([i["text"] for i in transcript_text])
        return transcript
    except Exception as e:
        raise e

def generate_gemini_content(transcript_text, prompt):
    model = genai.GenerativeModel("gemini-pro")
    response = model.generate_content(prompt + transcript_text)
    return response.text

@app.route('/extract-transcript', methods=['POST'])
def extract_transcript():
    data = request.json
    youtube_link = data['youtubeLink']
    print(f"Extracting transcript for: {youtube_link}")
    try:
        transcript = extract_transcript_details(youtube_link)
        return jsonify({"transcript": transcript})
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/generate-summary', methods=['POST'])
def generate_summary():
    data = request.json
    transcript_text = data['transcriptText']
    print(f"Generating summary for transcript: {transcript_text[:500]}...") 
    try:
        summary = generate_gemini_content(transcript_text, prompt)
        print(f"Summary: {summary}")
        return jsonify({"summary": summary})
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
