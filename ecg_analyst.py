import streamlit as st
import requests
import base64
from io import BytesIO
from PIL import Image

# --- Configuration ---
# NOTE: Replace this with your actual Gemini API Key (or use Streamlit Secrets)
# WARNING: Storing API keys directly in the code is insecure for production apps.
API_KEY = "" # Your API Key goes here if needed.
API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-09-2025:generateContent"

# Set a helpful system instruction to guide the model's behavior
SYSTEM_PROMPT = (
    "You are a highly skilled, board-certified electrophysiologist (cardiologist specializing in "
    "ECG analysis). Your task is to analyze the provided Electrocardiogram (ECG) scan image. "
    "Provide a detailed, structured report that includes:\n"
    "1. *ECG Metrics*: Estimate Heart Rate (BPM), Rhythm (Regular/Irregular), PR Interval, QRS Duration, and QT Interval.\n"
    "2. *Morphology Analysis*: Describe the P-waves, QRS complex, and T-waves in all visible leads.\n"
    "3. *Interpretation/Diagnosis*: Based on the visual evidence, provide a primary and secondary differential diagnosis of any possible diseases, abnormalities, or conditions.\n"
    "4. *Recommendation & Lifestyle Advice*: Suggest next steps (e.g., monitor, stress test, specific medication) AND provide tailored lifestyle and dietary recommendations, especially if an underlying heart condition is suspected.\n"
    "Format the response using Markdown for clear readability, starting with the Interpretation/Diagnosis section."
)


def image_to_base64(img_bytes):
    """Converts image bytes to base64 string for the API payload."""
    return base64.b64encode(img_bytes).decode('utf-8')


def analyze_ecg_with_gemini(image_base64_data):
    """Calls the Gemini API to analyze the ECG image."""
    
    # Construct the multimodal payload
    payload = {
        "contents": [
            {
                "role": "user",
                "parts": [
                    {
                        "inlineData": {
                            "mimeType": "image/png",  # Assuming PNG/JPEG, but PNG is safer
                            "data": image_base64_data
                        }
                    },
                    {
                        "text": "Analyze this ECG scan and provide a professional, structured report as instructed."
                    }
                ]
            }
        ],
        # Include system instruction to guide the output format and content
        "systemInstruction": {
            "parts": [{"text": SYSTEM_PROMPT}]
        }
    }

    headers = {
        "Content-Type": "application/json"
    }

    # Prepare the API endpoint, including the key if available
    api_endpoint = API_URL
    if API_KEY:
        api_endpoint += f"?key={API_KEY}"

    try:
        # Use requests for the Python backend environment of Streamlit
        response = requests.post(api_endpoint, headers=headers, json=payload)
        response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
        
        result = response.json()
        
        # Extract the generated text
        generated_text = result.get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text', 'Analysis failed or no text generated.')
        return generated_text

    except requests.exceptions.RequestException as e:
        return f"🚨 API Request Error: Failed to connect to the Gemini API. Please check your API key and network connection. Details: {e}"
    except Exception as e:
        return f"🚨 General Error: An unexpected error occurred during processing. Details: {e}"


# --- Streamlit UI Layout ---
st.set_page_config(page_title="Gemini ECG Analyst", layout="wide")

st.markdown("""
<style>
.main-header {
    font-size: 2.5em;
    font-weight: 700;
    color: #4B0082; /* Deep Indigo */
    text-align: center;
    margin-bottom: 20px;
}
.stButton>button {
    background-color: #8A2BE2; /* Blue Violet */
    color: white;
    border-radius: 12px;
    padding: 10px 20px;
    font-size: 1.1em;
    transition: background-color 0.3s;
}
.stButton>button:hover {
    background-color: #6A5ACD; /* Slate Blue */
}
</style>
""", unsafe_allow_html=True)

st.markdown('<p class="main-header">🩺 Gemini ECG Scan Analyst</p>', unsafe_allow_html=True)
st.markdown("Upload an ECG image to get a detailed, AI-driven analysis of rhythm, morphology, and potential cardiac conditions.")

# File Uploader
uploaded_file = st.file_uploader(
    "Upload an ECG Image (PNG, JPG)", 
    type=["png", "jpg", "jpeg"],
    accept_multiple_files=False
)

analysis_col, results_col = st.columns([1, 2])

with analysis_col:
    if uploaded_file is not None:
        # Read the file bytes
        file_bytes = uploaded_file.read()

        # Display the uploaded image
        st.subheader("Uploaded ECG Scan")
        image = Image.open(BytesIO(file_bytes))
        st.image(image, caption="Uploaded ECG", use_column_width=True)

        # Analysis Button
        if st.button("Analyze ECG with Gemini AI"):
            
            # Convert image to base64
            image_base64 = image_to_base64(file_bytes)

            with st.spinner('Analyzing the ECG image... This may take a moment.'):
                # Call the analysis function
                analysis_report = analyze_ecg_with_gemini(image_base64)
            
            # Store the result in session state
            st.session_state['analysis_report'] = analysis_report
            st.session_state['uploaded_file'] = uploaded_file.name
    
    else:
        # Display an empty placeholder if no file is uploaded
        st.info("Awaiting ECG file upload...")


with results_col:
    st.subheader("AI Analysis Report")
    if 'analysis_report' in st.session_state:
        st.markdown("---")
        # Display the generated report
        st.markdown(st.session_state['analysis_report'])
    else:
        st.info("The analysis report will appear here after you upload and analyze an ECG scan.")
