import streamlit as st
import requests
import base64
from io import BytesIO
from PIL import Image

# --- Configuration ---
# IMPORTANT: In a real app, use st.secrets["GEMINI_API_KEY"] for security!
API_KEY = "AIzaSyDxlzYbOluOFAdt7-2EPM-BlhQ77ysHkQg" # Replace with your actual key or use Streamlit Secrets
API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-09-2025:generateContent"

# --- System Prompt (UPDATED for Clear Diagnosis) ---
SYSTEM_PROMPT = (
    "You are a highly skilled, board-certified electrophysiologist (cardiologist specializing in "
    "ECG analysis). Your task is to analyze the provided Electrocardiogram (ECG) scan image. "
    "Provide a detailed, structured report that includes:\n"
    "1. *ECG Metrics*: Estimate Heart Rate (BPM), Rhythm (Regular/Irregular), PR Interval, QRS Duration, and QT Interval.\n"
    "2. *Morphology Analysis*: Describe the P-waves, QRS complex, and T-waves in all visible leads.\n"
    "3. *Interpretation/Diagnosis*: Based on the visual evidence, provide a primary and secondary differential diagnosis of any possible diseases, abnormalities, or conditions.\n"
    "4. *Clear Diagnosis Statement: State in **one single sentence* whether the ECG is *Normal* or clearly state the *primary disease/condition* (e.g., 'The patient shows evidence of an acute Myocardial Infarction,' or 'The ECG is within normal limits').\n"
    "5. *Recommendation*: Suggest next steps (e.g., monitor, stress test, specific medication, follow-up).\n"
    "6. *Lifestyle Recommendations: Provide general, non-allergic **dietary suggestions* (e.g., Mediterranean diet elements, low sodium) and *light workout recommendations* (e.g., walking, stretching) suitable for general heart health. *IMPORTANT:* Do NOT mention specific food recommendations in this section. Instead, state: 'Lifestyle recommendations will be personalized based on user allergy and location input below.'\n"
    "Format the response using Markdown for clear readability. Start with the Interpretation/Diagnosis section."
)

# --- Helper Functions (analyze_ecg_with_gemini and image_to_base64 remain the same) ---
def image_to_base64(img_bytes):
    return base64.b64encode(img_bytes).decode('utf-8')

@st.cache_data(show_spinner=False)
def analyze_ecg_with_gemini(image_base64_data):
    # ... (API Payload and Request logic remains the same)
    payload = {
        "contents": [
            {
                "role": "user",
                "parts": [
                    {
                        "inlineData": {
                            "mimeType": "image/png",
                            "data": image_base64_data
                        }
                    },
                    {"text": "Analyze this ECG scan and provide a professional, structured electrophysiology report as instructed."}
                ]
            }
        ],
        "systemInstruction": {"parts": [{"text": SYSTEM_PROMPT}]}
    }

    headers = { "Content-Type": "application/json" }
    api_endpoint = API_URL
    if API_KEY:
        api_endpoint += f"?key={API_KEY}"

    try:
        response = requests.post(api_endpoint, headers=headers, json=payload)
        response.raise_for_status()
        result = response.json()
        generated_text = result.get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text', 'Analysis failed or no text generated.')
        return generated_text
    except requests.exceptions.RequestException as e:
        return f"🚨 *API Request Error*: Failed to connect to the model API. Details: {e}"
    except Exception as e:
        return f"🚨 *General Error*: An unexpected error occurred during processing. Details: {e}"

# NEW FUNCTION: Generate personalized lifestyle recommendations
def generate_personalized_recommendation(allergies, location):
    """Generates personalized food and doctor recommendations using the API."""
    
    # NEW PROMPT for personalized recommendations
    personalized_prompt = (
        f"Based on a general heart health analysis (assume the analysis found a condition that requires heart-healthy changes, unless otherwise noted), "
        f"provide personalized advice. The patient reports allergies to: '{allergies}' and is asking for local doctor recommendations near: '{location}'.\n\n"
        f"1. *Personalized Food Recommendations: Suggest specific heart-healthy foods (e.g., fish, vegetables, grains) while explicitly mentioning which common heart-healthy items they must **AVOID* due to their listed allergies. Be general about diet structure (e.g., Mediterranean) but give examples that are safe.\n"
        f"2. *Doctor Recommendation*: Based on the approximate location '{location}', recommend the name of one highly-rated cardiologist or electrophysiologist in that general area or state/region. If a specific doctor name cannot be found, recommend a top medical center or hospital specializing in cardiology in that area."
    )
    
    # Call the API with the new prompt
    payload = {
        "contents": [{"role": "user", "parts": [{"text": personalized_prompt}]}]
    }

    headers = { "Content-Type": "application/json" }
    api_endpoint = API_URL
    if API_KEY:
        api_endpoint += f"?key={API_KEY}"
        
    try:
        response = requests.post(api_endpoint, headers=headers, json=payload)
        response.raise_for_status()
        result = response.json()
        return result.get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text', 'Could not generate personalized advice.')
    except Exception as e:
        return f"Error generating personalized advice: {e}"


# --- Session State and Control Functions ---

# Function to run analysis and update session state
def run_analysis(file_bytes):
    if file_bytes is None:
        st.error("Please upload an image first.")
        return

    # Clear old personalized results before new analysis
    st.session_state['personalized_report'] = None
    
    with st.spinner('🔬 Performing professional electrophysiology analysis...'):
        image_base64 = image_to_base64(file_bytes)
        report = analyze_ecg_with_gemini(image_base64)
        st.session_state['analysis_report'] = report
        
def clear_results():
    st.session_state['analysis_report'] = None
    st.session_state['uploaded_file_data'] = None
    st.session_state['personalized_report'] = None
    st.session_state['allergies'] = ''
    st.session_state['location'] = ''
    analyze_ecg_with_gemini.clear() # Clear cache

# --- Streamlit UI Layout (Error-free, Cleaned up) ---

st.set_page_config(page_title="Cardiology Scan Analyst", layout="wide")

# Customized CSS (Remains the same attractive style)
st.markdown("""
<style>
/* Overall Page Styling with a subtle gradient */
.stApp {
    background: linear-gradient(135deg, #e3f2fd 10%, #ffffff 100%);
}

/* Customizing the main header */
.main-header-custom {
    font-size: 3.2em;
    font-weight: 900;
    color: #00897b;
    text-align: center;
    margin-bottom: 20px;
    padding: 15px 0;
    border-bottom: 6px solid #4db6ac;
    letter-spacing: 1.5px;
    text-shadow: 1px 1px 3px rgba(0, 0, 0, 0.1);
}

/* Styling the main upload and analysis button (Single button, high contrast) */
.stButton>button {
    background-color: #6a1b9a;
    color: white;
    border-radius: 15px;
    padding: 15px 30px;
    font-size: 1.3em;
    font-weight: bold;
    border: none;
    width: 100%; 
    box-shadow: 0 8px 15px rgba(0, 0, 0, 0.2);
    transition: background-color 0.3s, transform 0.2s, box-shadow 0.3s;
}
.stButton>button:hover {
    background-color: #4a148c;
    transform: translateY(-4px); 
    box-shadow: 0 10px 20px rgba(0, 0, 0, 0.3);
}

/* Info/Awaiting boxes (Clear and helpful feedback) */
.stAlert div[data-testid="stAlert"] {
    background-color: #e0f2f1;
    border-left: 6px solid #00897b;
    color: #004d40;
    font-size: 1.1em;
    padding: 20px;
    border-radius: 10px;
    box-shadow: 0 2px 5px rgba(0, 0, 0, 0.08);
}

/* Subheaders (Structured and clean) */
h2 {
    color: #00897b;
    border-bottom: 3px solid #b2dfdb; 
    padding-bottom: 10px;
    margin-top: 25px;
}

/* Report Section Headings (Visual Hierarchy) */
.stMarkdown h4 {
    color: #d81b60;
    border-left: 5px solid #00897b;
    padding-left: 10px;
    margin-top: 20px;
    font-weight: 600;
}
</style>
""", unsafe_allow_html=True)

# Main Title
st.markdown('<p class="main-header-custom">🫀 Cardiology Scan Analyst</p>', unsafe_allow_html=True)
st.markdown("<h4 style='text-align: center; color: #6a1b9a;'>*Upload your ECG scan for an immediate, detailed electrophysiology report.*</h4>", unsafe_allow_html=True)

# Initialize Session State
if 'analysis_report' not in st.session_state: st.session_state['analysis_report'] = None
if 'uploaded_file_data' not in st.session_state: st.session_state['uploaded_file_data'] = None
if 'personalized_report' not in st.session_state: st.session_state['personalized_report'] = None
if 'allergies' not in st.session_state: st.session_state['allergies'] = ''
if 'location' not in st.session_state: st.session_state['location'] = ''


# 1. File Uploader
uploaded_file = st.file_uploader(
    "1️⃣ Upload your 12-Lead ECG Image (PNG, JPG)", 
    type=["png", "jpg", "jpeg"],
    accept_multiple_files=False,
    on_change=clear_results, 
    key="file_uploader"
)

# Read file data
if uploaded_file:
    st.session_state['uploaded_file_data'] = uploaded_file.getvalue()
else:
    st.session_state['uploaded_file_data'] = None
    
analysis_col, results_col = st.columns([1, 2])

with analysis_col:
    st.markdown("---")
    st.markdown("### 2️⃣ Image Preview")
    
    # Display image preview
    if st.session_state['uploaded_file_data']:
        image = Image.open(BytesIO(st.session_state['uploaded_file_data']))
        st.image(image, caption="Uploaded ECG", use_container_width=True) 
    else:
        st.info("⬆️ Please upload an image to proceed.")

    st.markdown("---")
    
    # 3. Single Analyze Button (Conditional)
    if st.session_state['uploaded_file_data'] is not None:
        if st.session_state['analysis_report'] is None:
            st.button(
                "▶️ Generate Detailed Analysis", 
                on_click=run_analysis, 
                args=(st.session_state['uploaded_file_data'],)
            )
        else:
             st.success("✅ ECG Analysis Complete!")
             st.button(
                 "Clear All and Start New Analysis", 
                 key="clear_results", 
                 on_click=clear_results
             )
    else:
        st.button("Upload Image First", disabled=True)


with results_col:
    st.subheader("📝 Electrophysiology Analysis Report")
    
    # 4. Core Analysis Report Display
    if st.session_state['analysis_report']:
        st.markdown("---")
        st.markdown(st.session_state['analysis_report'])

        # --- Interactive Section for Personalized Advice ---
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("---")
        st.subheader("💡 Personalized Health Recommendations")
        
        st.info("To receive tailored advice, please answer the questions below:")
        
        # User input for allergies
        st.session_state['allergies'] = st.text_input(
            "❓ Do you have any food allergies (e.g., nuts, shellfish, gluten)?",
            value=st.session_state['allergies'],
            help="List all food allergies, separated by commas (e.g., peanuts, dairy, soy)."
        )
        
        # User input for doctor location
        st.session_state['location'] = st.text_input(
            "📍 Would you like a doctor recommendation? If yes, please provide your approximate location (City, State/Region, Country):",
            value=st.session_state['location'],
            help="Provide a general location for a relevant specialist recommendation."
        )

        # Button to generate personalized report
        if st.session_state['allergies'] or st.session_state['location']:
            if st.button("Generate Personalized Advice"):
                with st.spinner('✨ Generating tailored recommendations...'):
                    personalized_report = generate_personalized_recommendation(
                        st.session_state['allergies'],
                        st.session_state['location']
                    )
                    st.session_state['personalized_report'] = personalized_report
        
        # Display personalized report if generated
        if st.session_state['personalized_report']:
            st.markdown("---")
            st.markdown("### 📋 Tailored Advice")
            st.markdown(st.session_state['personalized_report'])
        
    else:
        st.info("The professional analysis report, including metrics, diagnosis, and personalized recommendations, will appear here after clicking 'Generate Detailed Analysis'.")
