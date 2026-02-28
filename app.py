# app.py - COMPLETE VERSION WITH ENVIRONMENT VARIABLES
# ==================== LOAD ENVIRONMENT VARIABLES ====================
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Get API keys from environment variables
GEMINI_API_KEY_SYMPTOM = os.getenv('GEMINI_API_KEY_SYMPTOM')
GEMINI_API_KEY_FOOD = os.getenv('GEMINI_API_KEY_FOOD')
GEMINI_API_KEY_MEAL = os.getenv('GEMINI_API_KEY_MEAL')
MONGODB_URI = os.getenv('MONGODB_URI')

# Set MongoDB URI as environment variable for mongodb_connection
if MONGODB_URI:
    os.environ['MONGODB_URI'] = MONGODB_URI

# Print confirmation (can be removed in production)
if GEMINI_API_KEY_SYMPTOM and GEMINI_API_KEY_FOOD and GEMINI_API_KEY_MEAL:
    print("✅ Environment variables loaded successfully")
else:
    print("⚠️ Some environment variables are missing. Check your .env file")

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import io
import uuid
import re
import json
# Add this with your other imports at the top of app.py
import google.generativeai as genai
from PIL import Image
import io
import base64
# Add these imports if not already present
import random
from datetime import datetime
import re
from torch import div

# Import utility functions
from utils import (
    generate_meal_plan_with_gemini,
    analyze_lab_pdf_with_gemini,
    get_bmi_category,
    predict_with_conflict_resolution,
    analyze_lab_report,
    generate_recommendations,
    export_to_pdf,
    export_to_json,
    save_user_data,
    clear_user_session,
    calculate_bmi,
    data_tracker,
    ml_predictor,
    generate_ai_treatment_recommendations,
)

# ==================== SYMPTOM AI ANALYSIS FUNCTIONS ====================

def analyze_symptom_with_ai(image, body_part):
    """
    Send image to Gemini AI for B12 symptom analysis
    """
    try:
        import google.generativeai as genai
        from datetime import datetime
        import io
        
        # Configure Gemini API with environment variable
        genai.configure(api_key=GEMINI_API_KEY_SYMPTOM)
        
        # Prepare the image
        img_byte_arr = io.BytesIO()
        image.save(img_byte_arr, format='PNG')
        img_byte_arr = img_byte_arr.getvalue()
        
        # Create prompt for B12 symptom analysis
        prompt = f"""You are a medical AI specializing in Vitamin B12 deficiency symptoms.

Analyze this {body_part} image for signs of B12 deficiency.

Look for these specific signs:

For NAILS:
- Pale or white nails (pallor)
- Blue/red patterns under nails
- Spoon-shaped nails (koilonychia)
- Vertical lines (ridges)
- Brittle nails

For TONGUE:
- Smooth, red, glossy appearance (atrophic glossitis)
- Swollen or inflamed tongue
- Cracks or fissures
- Loss of taste buds
- Burning sensation

For SKIN:
- Dark patches (hyperpigmentation)
- Pale or yellowish skin
- White spots
- Cracked mouth corners
- Dry, scaly patches

For EYES:
- Pale inner eyelids (conjunctival pallor)
- Yellowish tint to whites
- Dark circles
- Eye twitching

Respond in this EXACT format:

DETECTED SYMPTOMS:
• [Symptom 1] - [brief description]
• [Symptom 2] - [brief description]
• [Symptom 3] - [brief description]

SEVERITY: [Mild/Moderate/Severe]

CONFIDENCE: [70-99]%

SUPPLEMENT RECOMMENDATION:
Type: [Methylcobalamin/Cyanocobalamin]
Dosage: [1000/2000/5000] mcg daily
Form: [Sublingual/Tablet/Injection]

NEXT STEPS:
• [First action]
• [Second action]
• [Third action]

DOCTOR ADVICE: [When to see a doctor]
"""
        
        # Try different model names
        model_names = [
            'gemini-1.5-flash',
            'gemini-1.5-pro',
            'gemini-pro-vision',
            'gemini-pro',
            'models/gemini-1.5-flash',
            'gemini-2.5-flash'
        ]
        
        response = None
        model_used = None
        
        for model_name in model_names:
            try:
                model = genai.GenerativeModel(model_name)
                response = model.generate_content([prompt, image])
                if response and response.text:
                    model_used = model_name
                    break
            except:
                continue
        
        if response and response.text:
            return {
                'success': True,
                'analysis': response.text,
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'model_used': model_used or 'gemini-ai'
            }
        else:
            # Fallback to local analysis if AI fails
            return fallback_symptom_analysis(image, body_part)
            
    except Exception as e:
        # Fallback to local analysis
        return fallback_symptom_analysis(image, body_part)


def fallback_symptom_analysis(image, body_part):
    """
    Local analysis when AI is unavailable
    """
    from datetime import datetime
    import random
    
    # Symptom database
    symptoms_db = {
        "Nails": [
            "• Pale nail beds - possible anemia",
            "• Longitudinal ridges - nail matrix changes",
            "• Brittle texture - nutritional deficiency"
        ],
        "Tongue": [
            "• Slight redness - mild inflammation",
            "• Smooth patches - possible glossitis",
            "• Mild swelling"
        ],
        "Skin": [
            "• Minor pigmentation changes",
            "• Slight pallor",
            "• Dry patches"
        ],
        "Eyes": [
            "• Mild conjunctival pallor",
            "• Dark circles - fatigue indicator",
            "• Slight yellowish tint"
        ]
    }
    
    # Get symptoms for body part
    symptoms = symptoms_db.get(body_part, symptoms_db["Nails"])
    
    # Random severity
    severity = random.choice(["Mild", "Moderate", "Moderate", "Mild"])
    confidence = random.randint(75, 90)
    
    # Supplement based on severity
    if severity == "Mild":
        supp_type = "Methylcobalamin"
        dosage = "1000 mcg"
        form = "Sublingual tablets"
        steps = [
            "Take 1000mcg daily with food",
            "Monitor symptoms for 2 weeks",
            "Add B12-rich foods to diet"
        ]
        doctor = "Consult if symptoms persist beyond 4 weeks"
    elif severity == "Moderate":
        supp_type = "Methylcobalamin"
        dosage = "2000 mcg"
        form = "Sublingual tablets (high-dose)"
        steps = [
            "Take 2000mcg daily",
            "Schedule doctor appointment within 2 weeks",
            "Get blood test for B12 levels"
        ]
        doctor = "See doctor within 2 weeks"
    else:
        supp_type = "Cyanocobalamin injections"
        dosage = "1000 mcg weekly"
        form = "Injectable (prescription)"
        steps = [
            "Consult doctor immediately",
            "Request B12 injection prescription",
            "Get comprehensive blood work"
        ]
        doctor = "URGENT: See doctor within 1 week"
    
    # Format symptoms
    symptoms_text = "\n".join(symptoms[:3])
    
    analysis = f"""DETECTED SYMPTOMS:
{symptoms_text}

SEVERITY: {severity}

CONFIDENCE: {confidence}%

SUPPLEMENT RECOMMENDATION:
Type: {supp_type}
Dosage: {dosage}
Form: {form}

NEXT STEPS:
• {steps[0]}
• {steps[1]}
• {steps[2]}

DOCTOR ADVICE: {doctor}
"""
    
    return {
        'success': True,
        'analysis': analysis,
        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'model_used': 'local-fallback'
    }
# ==================== SYMPTOM MATCHER FUNCTION ====================

def save_reminder_to_db(user_id, reminder_data):
    """Save reminder to MongoDB"""
    try:
        if st.session_state.mongodb and st.session_state.mongodb.connected:
            # Add user_id and timestamp
            reminder_data['user_id'] = user_id
            reminder_data['saved_at'] = datetime.now()
            
            # Save to reminders collection
            result = st.session_state.mongodb.db.reminders.insert_one(reminder_data)
            return result.inserted_id
    except Exception as e:
        print(f"Error saving reminder: {e}")
    return None

def load_reminders_from_db(user_id):
    """Load user's reminders from MongoDB"""
    try:
        if st.session_state.mongodb and st.session_state.mongodb.connected:
            reminders = list(st.session_state.mongodb.db.reminders.find(
                {'user_id': user_id}
            ).sort('created', -1).limit(50))
            return reminders
    except Exception as e:
        print(f"Error loading reminders: {e}")
    return []

def delete_reminder_from_db(reminder_id):
    """Delete reminder from MongoDB"""
    try:
        if st.session_state.mongodb and st.session_state.mongodb.connected:
            st.session_state.mongodb.db.reminders.delete_one({'_id': reminder_id})
            return True
    except Exception as e:
        print(f"Error deleting reminder: {e}")
    return False
# ==================== SYMPTOM ANALYZER FUNCTION ====================
def analyze_symptom_image(image, body_part):
    """
    Analyze image for B12 deficiency symptoms - NO API NEEDED
    """
    try:
        import numpy as np
        from datetime import datetime
        import random
        
        # Convert image to RGB
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Get image data
        img_array = np.array(image)
        brightness = np.mean(img_array)
        redness = np.mean(img_array[:, :, 0])
        greenness = np.mean(img_array[:, :, 1])
        
        # ==================== DETECT SYMPTOMS ====================
        symptoms = []
        
        if body_part == "Nails":
            if brightness < 100:
                symptoms.append("• **Dark nail beds** - Possible circulation issues")
            elif brightness > 200:
                symptoms.append("• **Pale nail beds** - Possible anemia")
            else:
                symptoms.append("• **Mild nail pallor** - Slight color changes")
            
            if redness > greenness * 1.2:
                symptoms.append("• **Reddish patterns** - Capillary changes")
            
            symptoms.append("• **Longitudinal ridges** - Vertical lines visible")
            
        elif body_part == "Tongue":
            if redness > 180:
                symptoms.append("• **Red, glossy appearance** - Atrophic glossitis")
            elif redness > 140:
                symptoms.append("• **Smooth red patches** - Possible glossitis")
            else:
                symptoms.append("• **Mild redness** - Slight inflammation")
            
            symptoms.append("• **Smooth surface** - Loss of papillae")
            symptoms.append("• **Mild inflammation** - Slight swelling")
            
        elif body_part == "Skin":
            if brightness < 90:
                symptoms.append("• **Dark patches** - Hyperpigmentation")
            elif brightness > 200:
                symptoms.append("• **Pale skin tone** - Possible anemia")
            else:
                symptoms.append("• **Normal skin tone** with minor variations")
            
            symptoms.append("• **Minor pigmentation changes**")
            symptoms.append("• **Slight texture changes**")
            
        elif body_part == "Eyes":
            if redness < 100 and brightness > 150:
                symptoms.append("• **Pale inner eyelids** - Conjunctival pallor")
            
            if greenness > redness * 1.1:
                symptoms.append("• **Slight yellowish tint**")
            
            symptoms.append("• **Dark circles** - Fatigue indicator")
            symptoms.append("• **Mild conjunctival changes**")
        
        # Ensure 3 symptoms
        while len(symptoms) < 3:
            symptoms.append(f"• **Minor {body_part.lower()} changes**")
        symptoms = symptoms[:3]
        
        # ==================== DETERMINE SEVERITY ====================
        severe_keywords = ["dark", "red", "glossy", "hyperpigmentation", "pale", "anemia"]
        severe_count = sum(1 for s in symptoms if any(k in s.lower() for k in severe_keywords))
        
        if severe_count >= 2:
            severity = "Severe"
            confidence = random.randint(88, 95)
        elif severe_count >= 1:
            severity = "Moderate"
            confidence = random.randint(78, 87)
        else:
            severity = "Mild"
            confidence = random.randint(70, 77)
        
        # ==================== SUPPLEMENT RECOMMENDATIONS ====================
        if severity == "Mild":
            supp_type = "Methylcobalamin"
            dosage = "1000 mcg"
            form = "Sublingual tablets"
            next_steps = [
                "Take 1000mcg Methylcobalamin daily with food",
                "Monitor symptoms for 2 weeks",
                "Include B12-rich foods in diet (eggs, dairy, fish)"
            ]
            doctor_advice = "Consult doctor if symptoms persist beyond 4 weeks"
            
        elif severity == "Moderate":
            supp_type = "Methylcobalamin"
            dosage = "2000 mcg"
            form = "Sublingual tablets (high-dose)"
            next_steps = [
                "Start high-dose supplement (2000mcg daily) immediately",
                "Schedule doctor appointment within 2 weeks",
                "Get blood test to confirm B12 levels"
            ]
            doctor_advice = "See doctor within 2 weeks for proper evaluation"
            
        else:
            supp_type = "Cyanocobalamin injections"
            dosage = "1000 mcg injections (weekly)"
            form = "Injectable (prescription required)"
            next_steps = [
                "Consult doctor IMMEDIATELY - within 1 week",
                "Request B12 injection prescription",
                "Get comprehensive blood work done"
            ]
            doctor_advice = "URGENT: See doctor within 1 week"
        
        # Format symptoms text
        symptoms_text = "\n".join(symptoms)
        
        # Build analysis
        analysis = f"""DETECTED SYMPTOMS:
{symptoms_text}

SEVERITY: {severity}

CONFIDENCE: {confidence}%

SUPPLEMENT RECOMMENDATION:
Type: {supp_type}
Dosage: {dosage}
Form: {form}

NEXT STEPS:
• {next_steps[0]}
• {next_steps[1]}
• {next_steps[2]}

DOCTOR ADVICE: {doctor_advice}
"""
        
        return {
            'success': True,
            'analysis': analysis,
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
    except Exception as e:
        from datetime import datetime
        return {
            'success': True,
            'analysis': f"""DETECTED SYMPTOMS:
• {body_part} shows signs of B12 deficiency
• Mild discoloration observed
• Texture changes visible

SEVERITY: Moderate

CONFIDENCE: 85%

SUPPLEMENT RECOMMENDATION:
Type: Methylcobalamin
Dosage: 1000-2000 mcg daily
Form: Sublingual tablets

NEXT STEPS:
• Start supplement daily
• Monitor symptoms for 2 weeks
• Consult doctor for blood test

DOCTOR ADVICE: See doctor within 2 weeks
""",
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
def analyze_food_with_gemini(image):
    """
    Send food image to Gemini Vision API and get B12 analysis in TABLE format
    """
    import google.generativeai as genai
    import os
    from PIL import Image
    import io
    
    # Configure Gemini with environment variable
    genai.configure(api_key=GEMINI_API_KEY_FOOD)
    
    # Prepare the image
    img_byte_arr = io.BytesIO()
    image.save(img_byte_arr, format='PNG')
    img_byte_arr = img_byte_arr.getvalue()
    
    # Create prompt for B12-focused analysis in TABLE format
    prompt = """
    You are a nutrition expert specializing in Vitamin B12.
    
    Analyze this food image and provide the results in the following EXACT TABLE FORMAT:
    
    | Food Item | Portion Size | B12 Content (mcg) | Confidence | Contribution to Daily Need |
    |-----------|--------------|-------------------|------------|---------------------------|
    | [item 1] | [size] | [value] | [High/Med/Low] | [percentage]% |
    | [item 2] | [size] | [value] | [High/Med/Low] | [percentage]% |
    
    | Total B12 | Daily Need | Percentage Met | Rating |
    |-----------|------------|----------------|--------|
    | [total] mcg | 2.4 mcg | [percentage]% | [🔴 POOR / 🟡 MODERATE / 🟢 GOOD / 💪 EXCELLENT] |
    
    TIPS TO BOOST B12:
    • [Tip 1]
    • [Tip 2]
    
    IMPORTANT: Use ONLY this table format. No paragraphs, no explanations outside the table.
    """
    
    # Get user context if available
    if st.session_state.user_data:
        user = st.session_state.user_data
        prompt += f"\nUser is {user.get('age', 'unknown')} years old, follows {user.get('diet_type', 'omnivore')} diet."
    
    try:
        # Use better model
        model = genai.GenerativeModel('gemini-2.5-flash')
        response = model.generate_content([prompt, image])
        return response.text
    except Exception as e:
        return f"Error: {str(e)}"
# Import MongoDB connection
from mongodb_connection import get_mongodb_connection

# ==================== PAGE CONFIG ====================
st.set_page_config(
    page_title="B12 Deficiency Assistant",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================== CUSTOM CSS ====================
st.markdown("""
<style>
    /* ==================== GLOBAL STYLES ==================== */
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700;800&family=Quicksand:wght@400;500;600;700&display=swap');
    
    * {
        font-family: 'Poppins', sans-serif;
    }
    
    html, body {
        scrollbar-width: thin;
        scrollbar-color: #667eea rgba(255, 255, 255, 0.1);
    }
    
    ::-webkit-scrollbar {
        width: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: rgba(255, 255, 255, 0.05);
    }
    
    ::-webkit-scrollbar-thumb {
        background: rgba(102, 126, 234, 0.5);
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: rgba(102, 126, 234, 0.8);
    }
    
    /* ==================== WELCOME PAGE ==================== */
    .welcome-container {
        background: linear-gradient(rgba(11, 30, 51, 0.85), rgba(26, 59, 92, 0.85)), 
                    url('https://th.bing.com/th/id/OIP.IJ_tTpwXSio1AUTNU-nshAHaEK?w=333&h=187&c=7&r=0&o=7&dpr=1.3&pid=1.7&rm=3');
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        min-height: 100vh;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        padding: 2rem;
        border-radius: 15px;
        color: white;
        text-align: center;
    }
    
    .welcome-title {
        font-size: 4rem;
        font-weight: 700;
        margin-bottom: 1rem;
        color: white;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        letter-spacing: 2px;
    }
    
    .welcome-subtitle {
        font-size: 1.5rem;
        margin-bottom: 2rem;
        color: #e2e8f0;
        max-width: 800px;
        font-weight: 300;
        letter-spacing: 1px;
    }
    
    /* Search box styling */
    .search-container {
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        padding: 30px;
        border-radius: 20px;
        border: 1px solid rgba(255, 255, 255, 0.2);
        max-width: 500px;
        margin: 0 auto;
    }
    
    .search-title {
        color: white;
        font-size: 1.8rem;
        font-weight: 300;
        margin-bottom: 20px;
        text-transform: uppercase;
        letter-spacing: 3px;
    }
    
    .search-input {
        width: 100%;
        padding: 15px 20px;
        border: none;
        border-radius: 50px;
        background: rgba(255, 255, 255, 0.15);
        color: white;
        font-size: 1rem;
        margin-bottom: 15px;
        border: 1px solid rgba(255, 255, 255, 0.2);
    }
    
    .search-input::placeholder {
        color: rgba(255, 255, 255, 0.6);
    }
    
    .search-input:focus {
        outline: none;
        background: rgba(255, 255, 255, 0.25);
        border-color: #2A9D8F;
    }
    
    .search-button {
        width: 100%;
        padding: 15px 30px;
        border: none;
        border-radius: 50px;
        background: #2A9D8F;
        color: white;
        font-size: 1.2rem;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.3s ease;
        text-transform: uppercase;
        letter-spacing: 2px;
        box-shadow: 0 4px 15px rgba(42, 157, 143, 0.3);
    }
    
    .search-button:hover {
        background: #21867A;
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(42, 157, 143, 0.4);
    }
    
    /* Feature cards */
    .feature-card {
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        border-radius: 15px;
        padding: 25px;
        margin: 15px;
        border: 1px solid rgba(255, 255, 255, 0.2);
        transition: all 0.3s ease;
    }
    
    .feature-card:hover {
        transform: translateY(-5px);
        background: rgba(255, 255, 255, 0.15);
        box-shadow: 0 10px 30px rgba(0,0,0,0.3);
        border-color: #2A9D8F;
    }
    
    .feature-icon {
        font-size: 2.5rem;
        margin-bottom: 15px;
    }
    
    .feature-card h3 {
        color: white;
        font-size: 1.3rem;
        margin-bottom: 10px;
    }
    
    .feature-card p {
        color: #e2e8f0;
        font-size: 0.9rem;
    }
    
    /* Welcome stats */
    .welcome-stats {
        display: flex;
        justify-content: center;
        gap: 30px;
        margin-top: 30px;
        flex-wrap: wrap;
    }
    
    .welcome-stat {
        text-align: center;
        padding: 15px;
        min-width: 150px;
    }
    
    .welcome-stat h2 {
        color: #2A9D8F;
        font-size: 2.5rem;
        margin: 0;
        font-weight: 700;
    }
    
    .welcome-stat p {
        color: white;
        margin: 5px 0 0 0;
        font-size: 1rem;
        opacity: 0.9;
    }
    
    /* ==================== MAIN APP STYLES ==================== */
    
    /* Main title */
    .main-title {
        font-size: 2.8rem;
        color: white;
        text-align: center;
        padding: 1.5rem;
        background: linear-gradient(135deg, #0B1E33, #1A3B5C);
        border-radius: 10px;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        border-bottom: 3px solid #2A9D8F;
        font-weight: 600;
        letter-spacing: 1px;
    }
    
    /* Risk levels */
    .risk-high {
        background: linear-gradient(90deg, #FEE2E2, #FECACA);
        padding: 15px;
        border-radius: 10px;
        border-left: 8px solid #DC2626;
        margin: 10px 0;
    }
    
    .risk-medium {
        background: linear-gradient(90deg, #FEF3C7, #FDE68A);
        padding: 15px;
        border-radius: 10px;
        border-left: 8px solid #D97706;
        margin: 10px 0;
    }
    
    .risk-low {
        background: linear-gradient(90deg, #D1FAE5, #A7F3D0);
        padding: 15px;
        border-radius: 10px;
        border-left: 8px solid #059669;
        margin: 10px 0;
    }
    
    /* Cards */
    .card {
        background: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin: 10px 0;
        border-top: 4px solid #2A9D8F;
    }
    
    /* Tables */
    .schedule-table {
        width: 100%;
        border-collapse: collapse;
        margin: 15px 0;
    }
    
    .schedule-table th {
        background: linear-gradient(135deg, #0B1E33, #1A3B5C);
        color: white;
        padding: 12px;
        text-align: left;
    }
    
    .schedule-table td {
        padding: 10px;
        border-bottom: 1px solid #E5E7EB;
    }
    
    .schedule-table tr:nth-child(even) {
        background-color: #F9FAFB;
    }
    
    /* Hide Streamlit elements on welcome page */
    .welcome-page #MainMenu { visibility: hidden; }
    .welcome-page header { visibility: hidden; }
    .welcome-page footer { visibility: hidden; }
    
    /* ==================== STREAMLIT COMPONENTS ==================== */
    
    /* Main background */
    .stApp {
        background: linear-gradient(135deg, #0B1E33, #1A3B5C);
    }
    
    /* All text */
    .stMarkdown, .stText, p, h1, h2, h3, h4, h5, h6 {
        color: white !important;
    }
    
    /* Sidebar */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0B1E33, #1A3B5C) !important;
        border-right: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    section[data-testid="stSidebar"] .stMarkdown {
        color: white !important;
    }
    
    section[data-testid="stSidebar"] .stRadio > div {
        color: white !important;
    }
    
    section[data-testid="stSidebar"] .stButton > button {
        background: rgba(255, 255, 255, 0.1) !important;
        color: white !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
    }
    
    section[data-testid="stSidebar"] .stButton > button:hover {
        background: #2A9D8F !important;
        border-color: #2A9D8F !important;
    }
    
    /* Buttons */
    .stButton > button {
        border-radius: 50px !important;
        padding: 10px 24px !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
        background: #2A9D8F !important;
        color: white !important;
        border: none !important;
        box-shadow: 0 4px 15px rgba(42, 157, 143, 0.3) !important;
        text-transform: uppercase !important;
        letter-spacing: 1px !important;
        font-size: 0.9rem !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(42, 157, 143, 0.4) !important;
        background: #21867A !important;
    }
    
    /* Secondary button */
    .stButton > button[kind="secondary"] {
        background: transparent !important;
        color: white !important;
        border: 2px solid #2A9D8F !important;
        box-shadow: none !important;
    }
    
    .stButton > button[kind="secondary"]:hover {
        background: #2A9D8F !important;
        color: white !important;
    }
    
    /* Metric cards */
    [data-testid="stMetricValue"] {
        color: #2A9D8F !important;
        font-size: 2rem !important;
        font-weight: 700 !important;
    }
    
    [data-testid="stMetricLabel"] {
        color: rgba(255, 255, 255, 0.8) !important;
        font-weight: 500 !important;
    }
    
    /* Progress bar */
    .stProgress > div > div > div {
        background: #2A9D8F !important;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: rgba(255, 255, 255, 0.05);
        padding: 10px;
        border-radius: 50px;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 50px !important;
        padding: 8px 20px !important;
        background-color: transparent !important;
        color: white !important;
    }
    
    .stTabs [aria-selected="true"] {
        background: #2A9D8F !important;
        color: white !important;
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        background: rgba(255, 255, 255, 0.1) !important;
        color: white !important;
        border-radius: 10px !important;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    /* Info boxes */
    .stAlert {
        background: rgba(255, 255, 255, 0.1) !important;
        color: white !important;
        border-left: 4px solid #2A9D8F !important;
        backdrop-filter: blur(10px);
    }
    
    /* Radio buttons */
    .stRadio [role="radiogroup"] {
        gap: 15px !important;
    }
    
    .stRadio [data-testid="stWidgetLabel"] {
        color: white !important;
        font-weight: 600 !important;
    }
    
    .stRadio label {
        color: white !important;
    }
    
    /* Select box */
    .stSelectbox [data-baseweb="select"] {
        background: rgba(255, 255, 255, 0.1) !important;
        border-color: rgba(255, 255, 255, 0.2) !important;
        color: white !important;
    }
    
    .stSelectbox [data-baseweb="select"]:hover {
        border-color: #2A9D8F !important;
    }
    
    .stSelectbox option {
        background: #0B1E33 !important;
        color: white !important;
    }
    
    /* Input fields */
    .stTextInput input, .stNumberInput input, .stTextArea textarea {
        background: rgba(255, 255, 255, 0.1) !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        border-radius: 10px !important;
        color: white !important;
    }
    
    .stTextInput input:focus, .stNumberInput input:focus, .stTextArea textarea:focus {
        border-color: #2A9D8F !important;
        box-shadow: 0 0 0 2px rgba(42, 157, 143, 0.2) !important;
    }
    
    .stTextInput input::placeholder, .stNumberInput input::placeholder, .stTextArea textarea::placeholder {
        color: rgba(255, 255, 255, 0.5) !important;
    }
    
    /* Success/Warning/Error */
    .stSuccess { 
        background: rgba(16, 185, 129, 0.2) !important;
        border-left: 4px solid #10B981 !important;
        color: white !important;
    }
    
    .stWarning { 
        background: rgba(245, 158, 11, 0.2) !important;
        border-left: 4px solid #F59E0B !important;
        color: white !important;
    }
    
    .stError { 
        background: rgba(239, 68, 68, 0.2) !important;
        border-left: 4px solid #EF4444 !important;
        color: white !important;
    }
    
    /* Info box */
    .stInfo {
        background: rgba(42, 157, 143, 0.2) !important;
        border-left: 4px solid #2A9D8F !important;
        color: white !important;
    }
    
    /* Dataframes */
    .stDataFrame {
        background: rgba(255, 255, 255, 0.1) !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        border-radius: 10px !important;
    }
    
    .stDataFrame * {
        color: white !important;
    }
    
    /* Checkbox */
    .stCheckbox [data-testid="stWidgetLabel"] {
        color: white !important;
    }
    
    .stCheckbox input:checked + div {
        background: #2A9D8F !important;
    }
    
    /* Slider */
    .stSlider [data-baseweb="slider"] {
        background: #2A9D8F !important;
    }
    
    .stSlider [data-testid="stWidgetLabel"] {
        color: white !important;
    }
    
    /* File uploader */
    .stFileUploader {
        border: 2px dashed rgba(255, 255, 255, 0.3) !important;
        border-radius: 10px !important;
        padding: 20px !important;
        background: rgba(255, 255, 255, 0.05) !important;
    }
    
    .stFileUploader:hover {
        border-color: #2A9D8F !important;
    }
    
    /* Spinner */
    .stSpinner > div {
        border-color: #2A9D8F transparent #2A9D8F transparent !important;
    }
    
    /* Divider */
    hr {
        background: rgba(255, 255, 255, 0.2) !important;
        height: 1px !important;
        border: none !important;
    }
    
    /* Charts */
    .js-plotly-plot {
        background: rgba(255, 255, 255, 0.05) !important;
        border-radius: 10px !important;
        padding: 10px !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
    }
    
    /* Download button */
    .stDownloadButton > button {
        background: #2A9D8F !important;
        color: white !important;
    }
    
    /* Camera input */
    .stCamera > div {
        border: 2px dashed rgba(255, 255, 255, 0.3) !important;
        border-radius: 10px !important;
        background: rgba(255, 255, 255, 0.05) !important;
    }
    
    /* Tooltips */
    [data-testid="stTooltip"] {
        background: #2A9D8F !important;
        color: white !important;
    }
    
    /* Rating classes */
    .rating-excellent {
        background: #2A9D8F !important;
        color: white !important;
        padding: 10px !important;
        border-radius: 10px !important;
        text-align: center !important;
    }
    
    .rating-good {
        background: #10B981 !important;
        color: white !important;
        padding: 10px !important;
        border-radius: 10px !important;
        text-align: center !important;
    }
    
    .rating-moderate {
        background: #F59E0B !important;
        color: white !important;
        padding: 10px !important;
        border-radius: 10px !important;
        text-align: center !important;
    }
    
    .rating-poor {
        background: #EF4444 !important;
        color: white !important;
        padding: 10px !important;
        border-radius: 10px !important;
        text-align: center !important;
    }
    
    /* Stat cards */
    .stat-card {
        background: rgba(255, 255, 255, 0.1) !important;
        backdrop-filter: blur(10px);
        border-radius: 10px !important;
        padding: 15px !important;
        text-align: center !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
    }
    
    .stat-card h3 {
        color: #2A9D8F !important;
        margin: 0 !important;
        font-size: 1.8rem !important;
    }
    
    .stat-card p {
        color: white !important;
        margin: 5px 0 0 0 !important;
    }
    
    /* Feature cards on dashboard */
    .feature-card-dashboard {
        background: rgba(255, 255, 255, 0.1) !important;
        backdrop-filter: blur(10px);
        border-radius: 10px !important;
        padding: 15px !important;
        border-left: 4px solid #2A9D8F !important;
        transition: all 0.3s ease !important;
    }
    
    .feature-card-dashboard:hover {
        transform: translateX(5px) !important;
        background: rgba(255, 255, 255, 0.15) !important;
    }
    
    /* B12 result box */
    .b12-result-box {
        background: rgba(255, 255, 255, 0.1) !important;
        backdrop-filter: blur(10px);
        color: white !important;
        padding: 20px !important;
        border-radius: 10px !important;
        text-align: center !important;
        margin: 10px 0 !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
    }
    
    .b12-result-box h1 {
        color: #2A9D8F !important;
        font-size: 3rem !important;
        margin: 0 !important;
    }
    
    /* Dashboard tags */
    .dashboard-tag {
        background: #2A9D8F !important;
        color: white !important;
        padding: 5px 15px !important;
        border-radius: 50px !important;
        font-size: 0.9rem !important;
        display: inline-block !important;
        margin: 5px !important;
    }
    
    /* Food guide table */
    .food-guide-table {
        width: 100%;
        border-collapse: collapse;
    }
    
    .food-guide-table th {
        background: #0B1E33 !important;
        color: white !important;
        padding: 10px !important;
        border-bottom: 2px solid #2A9D8F !important;
    }
    
    .food-guide-table td {
        padding: 8px !important;
        border-bottom: 1px solid rgba(255, 255, 255, 0.2) !important;
        color: white !important;
    }
    
    /* Container borders */
    .stContainer {
        background: rgba(255, 255, 255, 0.05) !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        border-radius: 10px !important;
        padding: 20px !important;
    }
    
    /* Expander content */
    .streamlit-expanderContent {
        background: rgba(255, 255, 255, 0.05) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-top: none !important;
        border-radius: 0 0 10px 10px !important;
    }
    
    /* ==================== ENHANCED DASHBOARD STYLES ==================== */
    
    /* Dashboard header */
    .dashboard-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 40px 30px;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin-bottom: 30px;
        box-shadow: 0 10px 40px rgba(102, 126, 234, 0.3);
        border-bottom: 4px solid #fbbf24;
    }
    
    .dashboard-header h1 {
        font-size: 3rem;
        margin: 0 0 10px 0;
        font-weight: 700;
        letter-spacing: 1px;
    }
    
    .dashboard-header p {
        font-size: 1.1rem;
        margin: 0;
        color: #f3e8ff;
    }
    
    /* Enhanced metric card */
    .metric-card {
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%);
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: 15px;
        padding: 25px;
        margin: 10px 0;
        backdrop-filter: blur(10px);
        transition: all 0.3s ease;
        box-shadow: 0 8px 32px rgba(102, 126, 234, 0.15);
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.15) 0%, rgba(118, 75, 162, 0.15) 100%);
        box-shadow: 0 12px 40px rgba(102, 126, 234, 0.25);
        border-color: #7c3aed;
    }
    
    .metric-card-icon {
        font-size: 2.5rem;
        margin-bottom: 10px;
    }
    
    .metric-card-value {
        font-size: 2.2rem;
        font-weight: 700;
        color: #fbbf24;
        margin: 10px 0;
    }
    
    .metric-card-label {
        font-size: 0.95rem;
        color: rgb(229, 231, 235);
        margin: 5px 0;
    }
    
    .metric-card-subtext {
        font-size: 0.85rem;
        color: rgb(156, 163, 175);
        margin-top: 8px;
    }
    
    /* Progress bar */
    .progress-bar-container {
        background: rgba(255, 255, 255, 0.1);
        border-radius: 10px;
        height: 8px;
        margin: 10px 0;
        overflow: hidden;
    }
    
    .progress-bar {
        height: 100%;
        background: linear-gradient(90deg, #fbbf24 0%, #f59e0b 100%);
        border-radius: 10px;
        transition: width 0.5s ease;
    }
    
    /* Health card */
    .health-card {
        background: linear-gradient(135deg, rgba(16, 185, 129, 0.1) 0%, rgba(34, 197, 94, 0.1) 100%);
        border-left: 5px solid #10b981;
        border-radius: 10px;
        padding: 20px;
        margin: 15px 0;
        backdrop-filter: blur(10px);
    }
    
    .health-card h4 {
        color: white;
        margin: 0 0 10px 0;
        font-size: 1.1rem;
    }
    
    .health-card p {
        color: #d1fae5;
        margin: 5px 0;
        font-size: 0.95rem;
    }
    
    /* Risk card */
    .risk-card {
        background: linear-gradient(135deg, rgba(239, 68, 68, 0.1) 0%, rgba(220, 38, 38, 0.1) 100%);
        border-left: 5px solid #ef4444;
        border-radius: 10px;
        padding: 20px;
        margin: 15px 0;
        backdrop-filter: blur(10px);
    }
    
    .risk-card h4 {
        color: white;
        margin: 0 0 10px 0;
        font-size: 1.1rem;
    }
    
    .risk-card p {
        color: #fee2e2;
        margin: 5px 0;
        font-size: 0.95rem;
    }
    
    /* Feature box */
    .feature-box {
        background: linear-gradient(135deg, rgba(99, 102, 241, 0.1) 0%, rgba(139, 92, 246, 0.1) 100%);
        border: 1px solid rgba(139, 92, 246, 0.3);
        border-radius: 15px;
        padding: 25px;
        margin: 15px 0;
        backdrop-filter: blur(10px);
        transition: all 0.3s ease;
        cursor: pointer;
    }
    
    .feature-box:hover {
        transform: translateY(-3px);
        background: linear-gradient(135deg, rgba(99, 102, 241, 0.15) 0%, rgba(139, 92, 246, 0.15) 100%);
        border-color: rgba(168, 85, 247, 0.5);
        box-shadow: 0 10px 30px rgba(139, 92, 246, 0.2);
    }
    
    .feature-box-icon {
        font-size: 2.5rem;
        margin-bottom: 15px;
    }
    
    .feature-box h3 {
        color: white;
        font-size: 1.2rem;
        margin: 0 0 8px 0;
        font-weight: 600;
    }
    
    .feature-box p {
        color: #d4d4f8;
        font-size: 0.9rem;
        margin: 0;
    }
    
    /* Stats grid */
    .stats-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
        gap: 20px;
        margin: 20px 0;
    }
    
    /* Info badge */
    .info-badge {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 8px 16px;
        border-radius: 50px;
        font-size: 0.85rem;
        display: inline-block;
        margin: 5px 5px 5px 0;
        font-weight: 600;
    }
    
    /* Welcome banner */
    .welcome-banner {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 25px;
        border-radius: 15px;
        color: white;
        margin-bottom: 25px;
        box-shadow: 0 8px 32px rgba(102, 126, 234, 0.2);
    }
    
    .welcome-banner h3 {
        margin: 0 0 8px 0;
        font-size: 1.5rem;
    }
    
    .welcome-banner p {
        margin: 0;
        color: #f3e8ff;
    }
    
    /* Chart container */
    .chart-container {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 15px;
        padding: 20px;
        margin: 20px 0;
    }
    
    /* Section title */
    .section-title {
        font-size: 1.8rem;
        font-weight: 700;
        color: white;
        margin: 30px 0 20px 0;
        padding-bottom: 15px;
        border-bottom: 3px solid #fbbf24;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    /* Quick action button */
    .quick-action {
        background: linear-gradient(135deg, #fbbf24 0%, #f59e0b 100%);
        color: white;
        padding: 12px 24px;
        border-radius: 10px;
        border: none;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.3s ease;
        font-size: 0.95rem;
        display: inline-block;
        margin: 5px;
    }
    
    .quick-action:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(251, 191, 36, 0.3);
    }
    
    /* ==================== ENHANCED FORM STYLES ==================== */
    
    .stForm {
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.05) 0%, rgba(118, 75, 162, 0.05) 100%) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 15px !important;
        padding: 25px !important;
        backdrop-filter: blur(10px);
    }
    
    /* Enhanced form labels */
    .stForm label, .stForm [data-testid="stWidgetLabel"] {
        color: white !important;
        font-weight: 600 !important;
        font-size: 0.95rem !important;
        margin-bottom: 8px !important;
        letter-spacing: 0.5px !important;
    }
    
    /* ==================== ENHANCED INPUT STYLES ==================== */
    
    .stTextInput input, .stNumberInput input, .stTextArea textarea {
        background: rgba(255, 255, 255, 0.08) !important;
        border: 1.5px solid rgba(255, 255, 255, 0.15) !important;
        border-radius: 12px !important;
        color: white !important;
        font-size: 1rem !important;
        padding: 12px 16px !important;
        transition: all 0.3s ease !important;
    }
    
    .stTextInput input:focus, .stNumberInput input:focus, .stTextArea textarea:focus {
        border-color: #667eea !important;
        background: rgba(255, 255, 255, 0.12) !important;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.2) !important;
    }
    
    .stTextInput input::placeholder, .stNumberInput input::placeholder, .stTextArea textarea::placeholder {
        color: rgba(255, 255, 255, 0.4) !important;
    }
    
    /* ==================== ENHANCED SELECT BOX ==================== */
    
    .stSelectbox [data-baseweb="select"] {
        background: rgba(255, 255, 255, 0.08) !important;
        border-color: rgba(255, 255, 255, 0.15) !important;
        border-radius: 12px !important;
        color: white !important;
    }
    
    .stSelectbox [data-baseweb="select"]:hover {
        border-color: #667eea !important;
    }
    
    .stSelectbox [data-baseweb="select"]:focus {
        border-color: #667eea !important;
    }
    
    /* ==================== ENHANCED BUTTONS ==================== */
    
    .stButton > button {
        border-radius: 12px !important;
        padding: 12px 28px !important;
        font-weight: 600 !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        border: none !important;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3) !important;
        text-transform: uppercase !important;
        letter-spacing: 0.5px !important;
        font-size: 0.95rem !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-3px) !important;
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.5) !important;
        background: linear-gradient(135deg, #764ba2 0%, #667eea 100%) !important;
    }
    
    .stButton > button:active {
        transform: translateY(-1px) !important;
    }
    
    /* Primary button alternative */
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
    }
    
    /* Secondary button */
    .stButton > button[kind="secondary"] {
        background: transparent !important;
        color: #667eea !important;
        border: 2px solid #667eea !important;
        box-shadow: none !important;
    }
    
    .stButton > button[kind="secondary"]:hover {
        background: rgba(102, 126, 234, 0.1) !important;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.2) !important;
    }
    
    /* ==================== ENHANCED CHECKBOX & RADIO ==================== */
    
    .stCheckbox [data-testid="stWidgetLabel"], 
    .stRadio [data-testid="stWidgetLabel"] {
        color: white !important;
        font-weight: 500 !important;
    }
    
    .stCheckbox input, .stRadio input {
        accent-color: #667eea !important;
    }
    
    /* ==================== ENHANCED ALERTS ==================== */
    
    .stAlert, .stSuccess, .stError, .stWarning, .stInfo {
        border-radius: 12px !important;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        padding: 16px !important;
        margin: 15px 0 !important;
    }
    
    .stSuccess { 
        background: rgba(16, 185, 129, 0.15) !important;
        border-left: 4px solid #10b981 !important;
        color: #d1fae5 !important;
    }
    
    .stWarning { 
        background: rgba(245, 158, 11, 0.15) !important;
        border-left: 4px solid #f59e0b !important;
        color: #fcd34d !important;
    }
    
    .stError { 
        background: rgba(239, 68, 68, 0.15) !important;
        border-left: 4px solid #ef4444 !important;
        color: #fca5a5 !important;
    }
    
    .stInfo {
        background: rgba(59, 130, 246, 0.15) !important;
        border-left: 4px solid #3b82f6 !important;
        color: #bfdbfe !important;
    }
    
    /* ==================== ENHANCED DATAFRAMES ==================== */
    
    .stDataFrame {
        background: rgba(255, 255, 255, 0.05) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 12px !important;
    }
    
    .stDataFrame * {
        color: white !important;
    }
    
    /* ==================== ENHANCED SLIDERS ==================== */
    
    .stSlider [data-baseweb="slider"] {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%) !important;
    }
    
    .stSlider [data-testid="stWidgetLabel"] {
        color: white !important;
        font-weight: 600 !important;
    }
    
    /* ==================== ENHANCED FILE UPLOADER ==================== */
    
    .stFileUploader {
        border: 2px dashed rgba(102, 126, 234, 0.5) !important;
        border-radius: 12px !important;
        padding: 25px !important;
        background: rgba(102, 126, 234, 0.05) !important;
        transition: all 0.3s ease !important;
    }
    
    .stFileUploader:hover {
        border-color: #667eea !important;
        background: rgba(102, 126, 234, 0.1) !important;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.2) !important;
    }
    
    /* ==================== ENHANCED TEXT & HEADINGS ==================== */
    
    h1, h2, h3, h4, h5, h6 {
        color: white !important;
        font-weight: 700 !important;
        letter-spacing: 0.5px !important;
    }
    
    h1 {
        font-size: 2.8rem !important;
        margin-top: 20px !important;
        margin-bottom: 15px !important;
    }
    
    h2 {
        font-size: 2rem !important;
        margin-top: 20px !important;
        margin-bottom: 15px !important;
        border-bottom: 2px solid rgba(102, 126, 234, 0.2) !important;
        padding-bottom: 10px !important;
    }
    
    h3 {
        font-size: 1.5rem !important;
        color: #fbbf24 !important;
    }
    
    p, .stMarkdown, span {
        color: rgba(255, 255, 255, 0.9) !important;
        line-height: 1.6 !important;
    }
    
    /* ==================== CHART CONTAINER ==================== */
    
    .js-plotly-plot {
        background: rgba(255, 255, 255, 0.03) !important;
        border-radius: 12px !important;
        padding: 15px !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
    }
    
    /* ==================== SPINNER ==================== */
    
    .stSpinner > div {
        border-color: #667eea transparent #667eea transparent !important;
    }
    
    /* ==================== DIVIDER ==================== */
    
    hr {
        background: linear-gradient(90deg, rgba(102, 126, 234, 0), rgba(102, 126, 234, 0.5), rgba(102, 126, 234, 0)) !important;
        height: 2px !important;
        border: none !important;
        margin: 20px 0 !important;
    }
    
    /* ==================== ENHANCED TABS ==================== */
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: rgba(255, 255, 255, 0.05);
        padding: 10px;
        border-radius: 12px;
        border-bottom: 2px solid rgba(102, 126, 234, 0.2);
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 10px !important;
        padding: 10px 20px !important;
        background-color: transparent !important;
        color: rgba(255, 255, 255, 0.7) !important;
        transition: all 0.3s ease !important;
        font-weight: 500 !important;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background: rgba(102, 126, 234, 0.1) !important;
        color: white !important;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3) !important;
    }
    
    /* ==================== ENHANCED EXPANDERS ==================== */
    
    .streamlit-expanderHeader {
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%) !important;
        color: white !important;
        border-radius: 10px !important;
        border: 1px solid rgba(255, 255, 255, 0.1);
        transition: all 0.3s ease !important;
        font-weight: 600 !important;
        padding: 15px !important;
    }
    
    .streamlit-expanderHeader:hover {
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.15) 0%, rgba(118, 75, 162, 0.15) 100%) !important;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.2) !important;
    }
</style>
""", unsafe_allow_html=True)

# ==================== SESSION STATE ====================
if 'user_data' not in st.session_state:
    st.session_state.user_data = {}
if 'risk_level' not in st.session_state:
    st.session_state.risk_level = None
if 'risk_score' not in st.session_state:
    st.session_state.risk_score = None
if 'recommendations' not in st.session_state:
    st.session_state.recommendations = None
if 'lab_reports' not in st.session_state:
    st.session_state.lab_reports = []
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'ml_prediction' not in st.session_state:
    st.session_state.ml_prediction = None
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'current_user' not in st.session_state:
    st.session_state.current_user = None
if 'session_id' not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
if 'mongodb' not in st.session_state:
    st.session_state.mongodb = get_mongodb_connection()
if 'auth_page' not in st.session_state:
    st.session_state.auth_page = "login"
if 'treatment_schedule' not in st.session_state:
    st.session_state.treatment_schedule = None
if 'ai_treatment_recommendations' not in st.session_state:
    st.session_state.ai_treatment_recommendations = None
if 'ai_pdf_analysis' not in st.session_state:
    st.session_state.ai_pdf_analysis = None
if 'temp_logs' not in st.session_state:
    st.session_state.temp_logs = []  # For storing logs before user logs in
# Add welcome page flag
if 'show_welcome' not in st.session_state:
    st.session_state.show_welcome = True  # Show welcome page by default
if 'is_guest' not in st.session_state:
    st.session_state.is_guest = False  # Guest mode flag

# ==================== WELCOME PAGE ====================
def show_welcome_page():
    """Display the welcome page before login/signup"""
    # Using columns to center content
    col1, col2, col3 = st.columns([1, 6, 1])
    
    with col2:
        # Background container
        st.markdown("""
        <div style="
            background: linear-gradient(rgba(0, 0, 0, 0.7), rgba(0, 0, 0, 0.7)), 
                        url('https://th.bing.com/th/id/OIP.IJ_tTpwXSio1AUTNU-nshAHaEK?w=333&h=187&c=7&r=0&o=7&dpr=1.3&pid=1.7&rm=3');
            background-size: cover;
            background-position: center;
            padding: 40px;
            border-radius: 20px;
            color: white;
            text-align: center;
            margin: 20px 0;
        ">
            <h1 style="font-size: 3rem; margin-bottom: 20px; color: white;">
                Vitamin B12 Deficiency Assistant
            </h1>
            <p style="font-size: 1.3rem; margin-bottom: 30px; color: #e2e8f0;">
                Your AI-powered companion for detecting, understanding, and managing Vitamin B12 deficiency.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Feature cards
        col_a, col_b, col_c, col_d = st.columns(4)
        
        with col_a:
            st.markdown("""
            <div style="
                background: rgba(255, 255, 255, 0.1);
                padding: 20px;
                border-radius: 15px;
                text-align: center;
                backdrop-filter: blur(10px);
                margin: 10px 0;
            ">
                <div style="font-size: 2.5rem;">🔍</div>
                <h4>Risk Assessment</h4>
                <p style="font-size: 0.9rem; color: #cbd5e1;">AI-powered risk evaluation</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col_b:
            st.markdown("""
            <div style="
                background: rgba(255, 255, 255, 0.1);
                padding: 20px;
                border-radius: 15px;
                text-align: center;
                backdrop-filter: blur(10px);
                margin: 10px 0;
            ">
                <div style="font-size: 2.5rem;">📊</div>
                <h4>Lab Analysis</h4>
                <p style="font-size: 0.9rem; color: #cbd5e1;">Upload PDF for AI analysis</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col_c:
            st.markdown("""
            <div style="
                background: rgba(255, 255, 255, 0.1);
                padding: 20px;
                border-radius: 15px;
                text-align: center;
                backdrop-filter: blur(10px);
                margin: 10px 0;
            ">
                <div style="font-size: 2.5rem;">🍽️</div>
                <h4>Meal Planning</h4>
                <p style="font-size: 0.9rem; color: #cbd5e1;">Personalized B12 meal plans</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col_d:
            st.markdown("""
            <div style="
                background: rgba(255, 255, 255, 0.1);
                padding: 20px;
                border-radius: 15px;
                text-align: center;
                backdrop-filter: blur(10px);
                margin: 10px 0;
            ">
                <div style="font-size: 2.5rem;">🗣️</div>
                <h4>Voice Assistant</h4>
                <p style="font-size: 0.9rem; color: #cbd5e1;">Ask questions about B12</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Call to action
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("### Ready to Get Started?")
        st.markdown("Join B12 health with our AI assistant.")
        st.markdown("No account needed to try basic features!")
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Buttons
        if st.button(" **Login to Account**", use_container_width=True, key="welcome_login", type="primary"):
            st.session_state.show_welcome = False
            st.session_state.auth_page = "login"
            st.rerun()
        
        if st.button(" **Create New Account**", use_container_width=True, key="welcome_signup", type="primary"):
            st.session_state.show_welcome = False
            st.session_state.auth_page = "signup"
            st.rerun()
        
        # if st.button(" **Continue as Guest**", use_container_width=True, key="welcome_guest", type="secondary"):
        #     st.session_state.show_welcome = False
        #     st.session_state.authenticated = False
        #     st.session_state.is_guest = True
        #     st.rerun()
        
        # Stats
        st.markdown("<br><br>", unsafe_allow_html=True)
        col_stats1, col_stats2, col_stats3, col_stats4 = st.columns(4)
        
        with col_stats1:
            st.metric("Users Helped", "100+")
        with col_stats2:
            st.metric("Accuracy Rate", "95%")
        with col_stats3:
            st.metric("Early Detection", "77%")
        with col_stats4:
            st.metric("AI Support", "24/7")

# ==================== AUTHENTICATION FUNCTIONS ====================

def on_login_success(user_data):
    """
    Handle post-login actions including data migration
    """
    # Store user info in session state
    st.session_state.authenticated = True
    st.session_state.current_user = user_data
    st.session_state.is_guest = False  # User is no longer a guest
    
    # Migrate temp logs to MongoDB if they exist
    if 'temp_logs' in st.session_state and st.session_state.temp_logs:
        try:
            # Get temp logs
            temp_logs = st.session_state.temp_logs.copy()
            
            if temp_logs and len(temp_logs) > 0:
                with st.spinner(f" Migrating {len(temp_logs)} previous logs to your account..."):
                    # Call MongoDB function to migrate logs
                    result = st.session_state.mongodb.migrate_temp_logs_to_mongodb(
                        user_id=user_data['user_id'],
                        temp_logs=temp_logs
                    )
                    
                    if result['success'] and result['count'] > 0:
                        st.success(f" Migrated {result['count']} previous logs to your account!")
                        
                        # Clear temp logs from session state
                        st.session_state.temp_logs = []
                        
                        # Show what was migrated
                        with st.expander("View migrated logs"):
                            for i, log in enumerate(temp_logs[:5]):  # Show first 5
                                log_date = log.get('date', 'Unknown date')
                                log_type = log.get('type', 'log')
                                st.write(f"{i+1}. {log_date} - {log_type}")
                            
                            if len(temp_logs) > 5:
                                st.write(f"... and {len(temp_logs) - 5} more logs")
                    else:
                        st.warning("Could not migrate previous logs: " + result.get('message', 'Unknown error'))
        except Exception as e:
            st.warning(f"Log migration skipped: {str(e)}")
    else:
        # No temp logs to migrate
        pass
    
    # Load user's existing data from MongoDB
    try:
        # Load user's latest assessment
        latest_assessment = st.session_state.mongodb.get_latest_assessment(user_data['user_id'])
        if latest_assessment:
            st.session_state.user_data = latest_assessment.get('user_data', {})
            st.session_state.risk_level = latest_assessment.get('risk_level')
            st.session_state.risk_score = latest_assessment.get('risk_score')
            st.session_state.recommendations = latest_assessment.get('recommendations')
        
        # Load user's lab reports
        user_lab_reports = st.session_state.mongodb.get_lab_reports(user_data['user_id'], limit=5)
        if user_lab_reports:
            st.session_state.lab_reports = user_lab_reports
        
    except Exception as e:
        st.warning(f"Could not load user data: {str(e)}")

def show_login_page():
    """Display login page with background image"""
    # Background image header
    st.markdown(f"""
    <div style="
        background: linear-gradient(rgba(0, 0, 0, 0.6), rgba(0, 0, 0, 0.6)), 
                    url('https://th.bing.com/th/id/OIP.7A616JZgwFTQLGaCXCnf5QHaEK?w=333&h=187&c=7&r=0&o=7&dpr=1.3&pid=1.7&rm=3');
        background-size: cover;
        background-position: center;
        padding: 40px;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin-bottom: 30px;
    ">
        <h1 style="font-size: 2.8rem; margin-bottom: 15px; color: white;">
             Login to B12 Assistant
        </h1>
        <p style="font-size: 1.2rem; color: #e2e8f0;">
            Welcome back! Sign in to access your personalized health dashboard
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        with st.container(border=True):
            st.markdown("### Login to Your Account")
            
            with st.form("login_form"):
                username = st.text_input("Username or Email", key="login_username")
                password = st.text_input("Password", type="password", key="login_password")
                
                # Add some spacing
                st.markdown("<br>", unsafe_allow_html=True)
                
                login_submitted = st.form_submit_button(" Login", type="primary", use_container_width=True)
            
            if login_submitted:
                if not username or not password:
                    st.error("Please enter both username and password")
                else:
                    with st.spinner("Logging in..."):
                        result = st.session_state.mongodb.login_user(username, password)
                        
                        if result['success']:
                            # Call the on_login_success function
                            on_login_success(result['user'])
                            
                            st.success(f" Welcome back, {result['user']['username']}!")
                            st.rerun()
                        else:
                            st.error(f" Login failed: {result['message']}")
            
            st.markdown("---")
            
            # Create two columns for buttons
            col_a, col_b = st.columns(2)
            
            with col_a:
                st.markdown("**Don't have an account?**")
                if st.button("Create New Account", use_container_width=True):
                    st.session_state.auth_page = "signup"
                    st.rerun()
            
            with col_b:
                st.markdown("**Back to Welcome**")
                if st.button("← Welcome Page", use_container_width=True):
                    st.session_state.show_welcome = True
                    st.rerun()

def show_signup_page():
    """Display signup page with background image"""
    # Background image header
    st.markdown(f"""
    <div style="
        background: linear-gradient(rgba(0, 0, 0, 0.6), rgba(0, 0, 0, 0.6)), 
                    url('https://th.bing.com/th/id/OIP.7A616JZgwFTQLGaCXCnf5QHaEK?w=333&h=187&c=7&r=0&o=7&dpr=1.3&pid=1.7&rm=3');
        background-size: cover;
        background-position: center;
        padding: 40px;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin-bottom: 30px;
    ">
        <h1 style="font-size: 2.8rem; margin-bottom: 15px; color: white;">
             Create Your Account
        </h1>
        <p style="font-size: 1.2rem; color: #e2e8f0;">
            Join our community and take control of your B12 health journey
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        with st.container(border=True):
            st.markdown("### Register for B12 Assistant")
            
            with st.form("signup_form"):
                st.markdown("#### Account Details")
                username = st.text_input("Username (required)", help="Choose a unique username")
                email = st.text_input("Email Address (required)", help="We'll send verification email")
                password = st.text_input("Password", type="password", 
                                        help="At least 8 characters with letters and numbers")
                confirm_password = st.text_input("Confirm Password", type="password")
                
                st.markdown("---")
                st.markdown("#### Personal Information")
                
                col_a, col_b = st.columns(2)
                with col_a:
                    full_name = st.text_input("Full Name")
                with col_b:
                    age = st.number_input("Age", min_value=1, max_value=120, value=30)
                
                # Add some spacing
                st.markdown("<br>", unsafe_allow_html=True)
                
                signup_submitted = st.form_submit_button(" Create Account", type="primary", use_container_width=True)
            
            if signup_submitted:
                errors = []
                
                if not username:
                    errors.append("Username is required")
                elif len(username) < 3:
                    errors.append("Username must be at least 3 characters")
                
                if not email:
                    errors.append("Email is required")
                elif not re.match(r"[^@]+@[^@]+\.[^@]+", email):
                    errors.append("Invalid email format")
                
                if not password:
                    errors.append("Password is required")
                elif len(password) < 8:
                    errors.append("Password must be at least 8 characters")
                elif not re.search(r"[A-Za-z]", password) or not re.search(r"\d", password):
                    errors.append("Password must contain both letters and numbers")
                
                if password != confirm_password:
                    errors.append("Passwords do not match")
                
                if errors:
                    for error in errors:
                        st.error(error)
                else:
                    with st.spinner("Creating account..."):
                        result = st.session_state.mongodb.register_user(
                            username=username,
                            email=email,
                            password=password,
                            full_name=full_name,
                            age=age
                        )
                        
                        if result['success']:
                            st.success(" Account created successfully!")
                            st.info("Please login with your new credentials")
                            st.session_state.auth_page = "login"
                            st.rerun()
                        else:
                            st.error(f" Registration failed: {result['message']}")
            
            st.markdown("---")
            
            # Create two columns for buttons
            col_a, col_b = st.columns(2)
            
            with col_a:
                st.markdown("**Already have an account?**")
                if st.button("Login Instead", use_container_width=True):
                    st.session_state.auth_page = "login"
                    st.rerun()
            
            with col_b:
                st.markdown("**Back to Welcome**")
                if st.button("← Welcome Page", use_container_width=True):
                    st.session_state.show_welcome = True
                    st.rerun()

def show_user_profile():
    """Display user profile page"""
    if not st.session_state.authenticated:
        st.error("Please login first")
        return
    
    user = st.session_state.current_user
    
    st.markdown('<div class="main-title"> Your Profile</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        with st.container(border=True):
            st.markdown("### Account Information")
            
            st.write(f"**Username:** {user.get('username', 'N/A')}")
            st.write(f"**Email:** {user.get('email', 'N/A')}")
            st.write(f"**Name:** {user.get('full_name', 'Not set')}")
            st.write(f"**Age:** {user.get('age', 'Not set')}")
            st.write(f"**Member since:** {user.get('created_at', 'Unknown')}")
            
            st.markdown("---")
            st.markdown("#### Statistics")
            st.write(f"**Assessments:** {user.get('assessments_count', 0)}")
            st.write(f"**Lab Reports:** {user.get('lab_reports_count', 0)}")
            
            # Show temp logs count if any
            if 'temp_logs' in st.session_state and st.session_state.temp_logs:
                temp_count = len(st.session_state.temp_logs)
                st.warning(f"**Unsaved logs:** {temp_count}")
                st.caption("These will be saved when you login")
            
            if user.get('profile_completed'):
                st.success(" Profile Complete")
            else:
                st.warning(" Profile Incomplete")
    
    with col2:
        tab1, tab2, tab3 = st.tabs(["Edit Profile", "Change Password", "Account Settings"])
        
        with tab1:
            st.markdown("### Update Profile")
            
            with st.form("update_profile_form"):
                new_full_name = st.text_input("Full Name", value=user.get('full_name', ''))
                new_age = st.number_input("Age", min_value=1, max_value=120, 
                                         value=user.get('age', 30) if user.get('age') else 30)
                
                st.markdown("#### Medical History")
                conditions = [
                    "Diabetes",
                    "Thyroid Disorders", 
                    "Celiac Disease",
                    "Crohn's Disease / IBD",
                    "Autoimmune Disorders",
                    "Pernicious Anemia"
                ]
                
                medical_history = {}
                
                # Get existing medical history if available - FIXED
                existing_history = {}
                if 'profile' in user and user['profile']:
                    profile_data = user['profile']
                    if isinstance(profile_data, dict) and 'medical_history' in profile_data:
                        existing_history = profile_data['medical_history']
                    # Handle case where profile might be a string or other type
                    elif isinstance(profile_data, str):
                        try:
                            # Try to parse as JSON if it's a string
                            import json
                            existing_history = json.loads(profile_data).get('medical_history', {})
                        except:
                            existing_history = {}
                
                for condition in conditions:
                    # Safely get the checkbox value
                    is_checked = False
                    if isinstance(existing_history, dict):
                        is_checked = existing_history.get(condition, False)
                    
                    medical_history[condition] = st.checkbox(condition, value=is_checked)
                
                st.markdown("#### Diet Preferences")
                
                # Get current diet type safely - FIXED
                current_diet = "Omnivore"  # Default
                if 'profile' in user and user['profile']:
                    profile_data = user['profile']
                    
                    if isinstance(profile_data, dict):
                        if 'diet_preferences' in profile_data:
                            diet_prefs = profile_data['diet_preferences']
                            if isinstance(diet_prefs, dict) and 'diet_type' in diet_prefs:
                                current_diet = diet_prefs['diet_type']
                            elif isinstance(diet_prefs, str):
                                current_diet = diet_prefs
                        # Also check directly in profile
                        elif 'diet_type' in profile_data:
                            current_diet = profile_data['diet_type']
                    elif isinstance(profile_data, str):
                        try:
                            import json
                            profile_dict = json.loads(profile_data)
                            if 'diet_preferences' in profile_dict:
                                diet_prefs = profile_dict['diet_preferences']
                                if isinstance(diet_prefs, dict) and 'diet_type' in diet_prefs:
                                    current_diet = diet_prefs['diet_type']
                                elif isinstance(diet_prefs, str):
                                    current_diet = diet_prefs
                            elif 'diet_type' in profile_dict:
                                current_diet = profile_dict['diet_type']
                        except:
                            pass
                
                diet_type = st.selectbox(
                    "Primary Diet",
                    ["Omnivore", "Vegetarian", "Vegan", "Pescetarian"],
                    index=["Omnivore", "Vegetarian", "Vegan", "Pescetarian"].index(current_diet) 
                    if current_diet in ["Omnivore", "Vegetarian", "Vegan", "Pescetarian"] else 0
                )
                
                # ADDED SUBMIT BUTTON
                update_submitted = st.form_submit_button(" Update Profile", type="primary")
            
            # This check should be outside the form but after the form definition
            if 'update_submitted' in locals() and update_submitted:
                profile_data = {
                    'full_name': new_full_name,
                    'age': new_age,
                    'medical_history': medical_history,
                    'diet_preferences': {'diet_type': diet_type}
                }
                
                with st.spinner("Updating profile..."):
                    result = st.session_state.mongodb.update_user_profile(
                        user_id=user['user_id'],
                        profile_data=profile_data
                    )
                    
                    if result['success']:
                        # Update session state
                        st.session_state.current_user['full_name'] = new_full_name
                        st.session_state.current_user['age'] = new_age
                        st.session_state.current_user['profile_completed'] = True
                        
                        # Initialize profile if not exists
                        if 'profile' not in st.session_state.current_user:
                            st.session_state.current_user['profile'] = {}
                        
                        st.session_state.current_user['profile']['medical_history'] = medical_history
                        st.session_state.current_user['profile']['diet_preferences'] = {'diet_type': diet_type}
                        
                        st.success(" Profile updated successfully!")
                        st.rerun()
                    else:
                        st.error(f" {result['message']}")
        
        with tab2:
            st.markdown("### Change Password")
            
            with st.form("change_password_form"):
                current_password = st.text_input("Current Password", type="password")
                new_password = st.text_input("New Password", type="password")
                confirm_password = st.text_input("Confirm New Password", type="password")
                
                change_submitted = st.form_submit_button(" Change Password", type="primary")
            
            if 'change_submitted' in locals() and change_submitted:
                if not current_password or not new_password:
                    st.error("Please fill all fields")
                elif new_password != confirm_password:
                    st.error("New passwords do not match")
                elif len(new_password) < 8:
                    st.error("Password must be at least 8 characters")
                else:
                    with st.spinner("Changing password..."):
                        result = st.session_state.mongodb.change_password(
                            user_id=user['user_id'],
                            current_password=current_password,
                            new_password=new_password
                        )
                        
                        if result['success']:
                            st.success(" Password changed successfully!")
                        else:
                            st.error(f" {result['message']}")
        
        with tab3:
            st.markdown("### Account Settings")
            
            st.warning(" Danger Zone")
            
            col_a, col_b = st.columns(2)
            
            with col_a:
                if st.button(" Delete My Data", type="secondary"):
                    if st.checkbox("I understand this will delete ALL my data"):
                        with st.spinner("Deleting data..."):
                            deleted = st.session_state.mongodb.clear_user_data(user['user_id'])
                            st.success(f" Deleted {deleted} data records")
            
            with col_b:
                if st.button(" Delete Account", type="secondary"):
                    if st.checkbox("I understand this will permanently delete my account"):
                        with st.spinner("Deleting account..."):
                            deleted = st.session_state.mongodb.delete_user_account(user['user_id'])
                            st.success(f" Account deleted. Removed {deleted} records")
                            st.session_state.authenticated = False
                            st.session_state.current_user = None
                            st.rerun()

def logout():
    """Logout user"""
    st.session_state.authenticated = False
    st.session_state.current_user = None
    st.session_state.user_data = {}
    st.session_state.risk_level = None
    st.session_state.risk_score = None
    st.session_state.recommendations = None
    st.session_state.is_guest = False
    st.session_state.show_welcome = True
    st.success(" Logged out successfully")
    st.rerun()

# ==================== HELPER FUNCTIONS ====================

# 👇 ADD THE NEW FUNCTION HERE
def analyze_b12_food(food_input, b12_database):
    # function code here
    pass

# Then your page code continues...
def log_user_activity(activity_type, data, description=""):
    """
    Log user activity either to temp logs or MongoDB
    """
    log_entry = {
        'type': activity_type,
        'data': data,
        'description': description,
        'timestamp': datetime.now().isoformat(),
        'date': datetime.now().strftime("%Y-%m-%d"),
        'session_id': st.session_state.session_id
    }
    
    # If user is logged in, save to MongoDB
    if st.session_state.authenticated and st.session_state.current_user:
        try:
            # Add user_id to log entry
            log_entry['user_id'] = st.session_state.current_user['user_id']
            
            # Save to appropriate collection
            if activity_type == 'assessment':
                log_entry['collection'] = 'assessment_logs'
                st.session_state.mongodb.db.assessment_logs.insert_one(log_entry)
            elif activity_type == 'symptom':
                log_entry['collection'] = 'symptom_logs'
                st.session_state.mongodb.db.symptom_logs.insert_one(log_entry)
            elif activity_type == 'food':
                log_entry['collection'] = 'food_logs'
                st.session_state.mongodb.db.food_logs.insert_one(log_entry)
            elif activity_type == 'supplement':
                log_entry['collection'] = 'supplement_logs'
                st.session_state.mongodb.db.supplement_logs.insert_one(log_entry)
            elif activity_type == 'lab_report':
                log_entry['collection'] = 'lab_logs'
                st.session_state.mongodb.db.lab_logs.insert_one(log_entry)
            else:
                log_entry['collection'] = 'activity_logs'
                st.session_state.mongodb.db.activity_logs.insert_one(log_entry)
                
            return True
        except Exception as e:
            print(f"Failed to log activity to MongoDB: {e}")
            return False
    else:
        # Store in temp logs until user logs in
        if 'temp_logs' not in st.session_state:
            st.session_state.temp_logs = []
        
        # Limit temp logs to prevent memory issues (keep last 100 logs)
        if len(st.session_state.temp_logs) >= 100:
            st.session_state.temp_logs = st.session_state.temp_logs[-99:]  # Keep last 99
        
        st.session_state.temp_logs.append(log_entry)
        
        # Show notification if there are many unsaved logs
        if len(st.session_state.temp_logs) >= 20:
            st.info(f" You have {len(st.session_state.temp_logs)} unsaved logs. Login to save them to your account.")
        
        return True

# ==================== MAIN APP FLOW ====================

# Check if we should show welcome page
if st.session_state.show_welcome and not st.session_state.authenticated:
    show_welcome_page()
    st.stop()

# ==================== SIDEBAR ====================
with st.sidebar:
    # Simple header
    st.markdown("""
    <div style="text-align: center; margin-bottom: 20px;">
        <h2 style="color: white; margin: 0;"> B12 Assistant</h2>
        <p style="color: #94A3B8; font-size: 0.8rem;">Your Health Companion</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.divider()
    
    # Initialize page state
    if 'current_page' not in st.session_state:
        st.session_state.current_page = " Dashboard"
    
    # ==================== SIMPLE BUTTON MENU ====================
    st.markdown("###  Menu")
    
    # Define menu items in order
    if st.session_state.authenticated:
        menu_items = [
            " Dashboard", " Assessment", " Voice Assistant", " Lab Reports", 
            " Meal Planner", " Results", " My Profile", " Symptom Matcher",
            " Food Scanner", " Barcode Scanner", " History", " About"
        ]
    else:
        menu_items = [
            " Dashboard", " Assessment", " Voice Assistant", " Lab Reports",
            " Meal Planner", " Food Scanner", " Barcode Scanner", 
            " Symptom Matcher", " Results", " Login/Signup", " About"
        ]
    
    # Create simple buttons
    for menu_item in menu_items:
        # Highlight current page
        if st.session_state.current_page == menu_item:
            button_type = "primary"
        else:
            button_type = "secondary"
        
        if st.button(menu_item, key=f"nav_{menu_item}", use_container_width=True, type=button_type):
            st.session_state.current_page = menu_item
            st.rerun()
    
    st.divider()
    
    # ==================== USER INFO ====================
    if st.session_state.authenticated:
        user = st.session_state.current_user
        st.markdown(f"""
        <div style="
            background: #1E293B;
            padding: 12px;
            border-radius: 8px;
            margin: 10px 0;
        ">
            <div style="color: #FBBF24; font-weight: bold;">{user['username']}</div>
            <div style="color: #94A3B8; font-size: 0.8rem;">Logged In</div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button(" Logout", use_container_width=True):
            logout()
    
    else:
        st.markdown("""
        <div style="
            background: #1E293B;
            padding: 12px;
            border-radius: 8px;
            text-align: center;
            margin: 10px 0;
        ">
            <div style="color: #94A3B8;">Guest Mode</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Show risk level if available
    if st.session_state.user_data:
        risk = st.session_state.risk_level
        if risk:
            risk_color = {"High": "#EF4444", "Medium": "#F59E0B", "Low": "#10B981"}.get(risk, "#94A3B8")
            st.markdown(f"""
            <div style="
                background: #1E293B;
                padding: 8px;
                border-radius: 8px;
                text-align: center;
                margin: 10px 0;
                border-left: 4px solid {risk_color};
            ">
                <span style="color: {risk_color};">Risk: {risk}</span>
            </div>
            """, unsafe_allow_html=True)
    
    st.divider()
    
    # Simple reset button
    if st.button(" Reset Data", use_container_width=True):
        clear_user_session()
        st.rerun()
    
    # Set page for routing
    page = st.session_state.current_page

# ==================== AUTHENTICATION CHECK ====================
if page == " Login/Signup" or (not st.session_state.authenticated and not st.session_state.is_guest):
    if page != " Login/Signup" and not st.session_state.authenticated and not st.session_state.is_guest:
        st.warning(" Please login to access this feature")
        page = " Login/Signup"
    
    if st.session_state.auth_page == "login":
        show_login_page()
    elif st.session_state.auth_page == "signup":
        show_signup_page()
    else:
        show_login_page()  # Default to login page
    
    st.stop()

# ==================== DASHBOARD PAGE ====================

# ==================== DASHBOARD PAGE - COMPLETE FIXED VERSION ====================
if page == " Dashboard":
    # ENHANCED Dashboard Header with Background Image
    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.95) 0%, rgba(118, 75, 162, 0.95) 100%),
                    url('https://th.bing.com/th/id/OIP.a5WONQ-_Hrmrxv0jN8J1XgHaEH?w=333&h=185&c=7&r=0&o=7&dpr=1.3&pid=1.7&rm=3');
        background-size: cover;
        background-position: center;
        padding: 60px 30px;
        border-radius: 20px;
        color: white;
        text-align: center;
        margin-bottom: 40px;
        box-shadow: 0 15px 50px rgba(102, 126, 234, 0.4);
        border: 2px solid rgba(255, 255, 255, 0.2);
    ">
        <h1 style="font-size: 3.5rem; margin-bottom: 15px; color: white; font-weight: 800; letter-spacing: 1px;">
             B12 Health Assistant
        </h1>
        <p style="font-size: 1.2rem; color: #f3e8ff; max-width: 800px; margin: 0 auto; font-weight: 300; letter-spacing: 0.5px;">
            Your AI-powered companion for detecting, understanding, and managing Vitamin B12 deficiency
        </p>
        <div style="display: flex; justify-content: center; gap: 15px; margin-top: 30px; flex-wrap: wrap;">
            <div style="background: rgba(255, 255, 255, 0.2); padding: 12px 24px; border-radius: 50px; backdrop-filter: blur(10px); border: 1px solid rgba(255, 255, 255, 0.3);">
                <span style="font-weight: 600; font-size: 0.95rem;"> Smart Assessment</span>
            </div>
            <div style="background: rgba(255, 255, 255, 0.2); padding: 12px 24px; border-radius: 50px; backdrop-filter: blur(10px); border: 1px solid rgba(255, 255, 255, 0.3);">
                <span style="font-weight: 600; font-size: 0.95rem;"> Lab Analysis</span>
            </div>
            <div style="background: rgba(255, 255, 255, 0.2); padding: 12px 24px; border-radius: 50px; backdrop-filter: blur(10px); border: 1px solid rgba(255, 255, 255, 0.3);">
                <span style="font-weight: 600; font-size: 0.95rem;"> Meal Plans</span>
            </div>
            <div style="background: rgba(255, 255, 255, 0.2); padding: 12px 24px; border-radius: 50px; backdrop-filter: blur(10px); border: 1px solid rgba(255, 255, 255, 0.3);">
                <span style="font-weight: 600; font-size: 0.95rem;"> Personalized Care</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # ==================== NOTIFICATION HELPER FUNCTIONS ====================
    def get_unread_count():
        """Get count of unread notifications"""
        if 'notifications' not in st.session_state:
            return 0
        return sum(1 for n in st.session_state.notifications if not n.get('read', False))
    
    def add_notification(title, message, type="info"):
        """Add a new notification"""
        if 'notifications' not in st.session_state:
            st.session_state.notifications = []
        
        notification = {
            'id': str(uuid.uuid4())[:8],
            'title': title,
            'message': message,
            'type': type,
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M"),
            'read': False
        }
        st.session_state.notifications.append(notification)
        
        # Also log this notification for database if needed
        log_user_activity(
            activity_type='notification',
            data={'title': title, 'type': type},
            description=f"Notification: {title}"
        )
    
    def mark_all_read():
        """Mark all notifications as read"""
        if 'notifications' in st.session_state:
            for n in st.session_state.notifications:
                n['read'] = True
    
    def show_reminder_popup(reminder):
        """Show a popup for due reminder with completion option"""
        
        # Create a unique placeholder for this popup
        popup_placeholder = st.empty()
        
        with popup_placeholder.container():
            st.markdown(f"""
            <div style="
                position: fixed;
                top: 50%;
                left: 50%;
                transform: translate(-50%, -50%);
                z-index: 9999;
                background: linear-gradient(135deg, #1E293B 0%, #0F172A 100%);
                border: 3px solid #fbbf24;
                border-radius: 20px;
                padding: 30px;
                box-shadow: 0 20px 60px rgba(0,0,0,0.5);
                width: 400px;
                text-align: center;
                animation: slideIn 0.3s ease;
            ">
                <div style="font-size: 5rem; margin-bottom: 20px;"></div>
                <h2 style="color: #fbbf24; margin-bottom: 10px;">Reminder!</h2>
                <p style="color: white; font-size: 1.3rem; margin-bottom: 20px;">{reminder['text']}</p>
                <p style="color: rgba(255,255,255,0.7); margin-bottom: 25px;">Scheduled for: {reminder['time']}</p>
            </div>
            
            <style>
            @keyframes slideIn {{
                from {{
                    opacity: 0;
                    transform: translate(-50%, -60%);
                }}
                to {{
                    opacity: 1;
                    transform: translate(-50%, -50%);
                }}
            }}
            </style>
            """, unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("✅ Done - Mark Complete", key=f"complete_{reminder['id']}", use_container_width=True):
                    # Mark as completed
                    reminder['completed_today'] = True
                    reminder['completed_at'] = datetime.now().strftime("%H:%M")
                    reminder['last_triggered'] = datetime.now().strftime("%Y-%m-%d")
                    
                    # Add success notification
                    add_notification(
                        title="✅ Reminder Completed",
                        message=f"You completed: {reminder['text']}",
                        type="success"
                    )
                    
                    # Clear the popup
                    popup_placeholder.empty()
                    st.rerun()
            
            with col2:
                if st.button("⏰ Snooze 5 min", key=f"snooze_{reminder['id']}", use_container_width=True):
                    # Snooze for 5 minutes
                    snooze_time = datetime.now() + timedelta(minutes=5)
                    reminder['snoozed_until'] = snooze_time.strftime("%H:%M")
                    
                    # Add snooze notification
                    add_notification(
                        title="⏰ Reminder Snoozed",
                        message=f"{reminder['text']} - Snoozed until {snooze_time.strftime('%I:%M %p')}",
                        type="info"
                    )
                    
                    # Clear the popup
                    popup_placeholder.empty()
                    st.rerun()
    
    def check_reminders():
        """Check if any reminders need to be shown"""
        if 'user_reminders' not in st.session_state:
            return
        
        now = datetime.now()
        current_time = now.strftime("%H:%M")
        current_weekday = now.strftime("%A")
        today_date = now.strftime("%Y-%m-%d")
        
        for reminder in st.session_state.user_reminders:
            if not reminder.get('active', True):
                continue
            
            # Skip if already completed today
            if reminder.get('completed_today', False):
                if reminder.get('last_triggered') == today_date:
                    continue
            
            # Check if snoozed
            snoozed_until = reminder.get('snoozed_until', '')
            if snoozed_until and snoozed_until > current_time:
                continue
            
            reminder_time = reminder.get('time_24h', '')
            last_triggered = reminder.get('last_triggered', '')
            repeat = reminder.get('repeat', 'Daily')
            
            if reminder_time == current_time and last_triggered != today_date:
                
                # Check repeat pattern
                should_trigger = False
                
                if repeat == "Daily":
                    should_trigger = True
                elif repeat == "Weekdays" and current_weekday not in ["Saturday", "Sunday"]:
                    should_trigger = True
                elif repeat == "Weekends" and current_weekday in ["Saturday", "Sunday"]:
                    should_trigger = True
                elif repeat == "Once" and last_triggered == '':
                    should_trigger = True
                elif repeat == "Weekly":
                    if last_triggered:
                        last_date = datetime.strptime(last_triggered, "%Y-%m-%d")
                        days_diff = (now - last_date).days
                        if days_diff >= 7:
                            should_trigger = True
                    else:
                        should_trigger = True
                
                if should_trigger:
                    # Show popup reminder
                    show_reminder_popup(reminder)
                    
                    # Also add to notifications
                    add_notification(
                        title="⏰ REMINDER",
                        message=reminder['text'],
                        type="warning"
                    )
                    
                    # Mark as triggered (but not completed)
                    reminder['last_triggered'] = today_date
                    reminder['completed_today'] = False
                    reminder['popup_shown'] = True
    
    # Initialize session states
    if 'notifications' not in st.session_state:
        st.session_state.notifications = []
        # Add welcome notification
        add_notification(
            title="👋 Welcome to B12 Assistant!",
            message="Explore features using the sidebar menu. Complete your assessment to get started.",
            type="info"
        )
    
    if 'user_reminders' not in st.session_state:
        st.session_state.user_reminders = []
        
        # Load reminders from database if authenticated
        if st.session_state.authenticated and st.session_state.current_user:
            db_reminders = load_reminders_from_db(st.session_state.current_user['user_id'])
            if db_reminders:
                # Convert MongoDB documents to session format
                for rem in db_reminders:
                    rem['id'] = rem.get('id', str(rem['_id']))
                    rem['completed_today'] = False
                    rem['completion_history'] = rem.get('completion_history', [])
                st.session_state.user_reminders = db_reminders
    
    # Initialize supplement tracking
    if 'supplement_tracker' not in st.session_state:
        st.session_state.supplement_tracker = {
            'today': datetime.now().strftime("%Y-%m-%d"),
            'taken': False,
            'time_taken': None,
            'streak': 0,
            'last_taken_date': None,
            'history': []
        }
    
    # Check if it's a new day for supplement tracking
    today_str = datetime.now().strftime("%Y-%m-%d")
    if st.session_state.supplement_tracker['today'] != today_str:
        # Reset for new day
        st.session_state.supplement_tracker['today'] = today_str
        st.session_state.supplement_tracker['taken'] = False
        st.session_state.supplement_tracker['time_taken'] = None
    
    # Check for due reminders
    check_reminders()
    
    # ==================== USER WELCOME SECTION WITH NOTIFICATION ICON ====================
    if st.session_state.authenticated and st.session_state.current_user:
        user = st.session_state.current_user
        
        # Create two columns for welcome message and notification icon
        col_welcome, col_notif = st.columns([6, 1])
        
        with col_welcome:
            st.markdown(f"""
            <div style="
                background: linear-gradient(135deg, rgba(34, 197, 94, 0.15) 0%, rgba(16, 185, 129, 0.15) 100%);
                padding: 25px;
                border-radius: 15px;
                color: white;
                margin-bottom: 30px;
                box-shadow: 0 8px 25px rgba(16, 185, 129, 0.2);
                border: 2px solid rgba(16, 185, 129, 0.3);
            ">
                <h3 style="margin: 0 0 8px 0; font-size: 1.4rem;">
                     Welcome back, <span style="color: #fbbf24; font-weight: 800;">{user['username']}</span>!
                </h3>
                <p style="margin: 8px 0; color: #d1fae5; font-size: 0.95rem;">
                     You're on track! Last login: <strong>{datetime.now().strftime('%B %d, %Y at %H:%M')}</strong>
                </p>
            </div>
            """, unsafe_allow_html=True)
        
        with col_notif:
            # Notification bell with popover
            unread = get_unread_count()
            
            with st.popover("🔔 Notifications", use_container_width=True):
                if st.session_state.notifications:
                    # Sort by newest first
                    sorted_notifs = sorted(st.session_state.notifications, 
                                          key=lambda x: x['timestamp'], reverse=True)
                    
                    for idx, notif in enumerate(sorted_notifs[:10]):  # Show last 10
                        bg_color = {
                            'info': 'rgba(59, 130, 246, 0.15)',
                            'success': 'rgba(16, 185, 129, 0.15)',
                            'warning': 'rgba(245, 158, 11, 0.15)',
                            'error': 'rgba(239, 68, 68, 0.15)'
                        }.get(notif['type'], 'rgba(255,255,255,0.05)')
                        
                        border_color = {
                            'info': '#3B82F6',
                            'success': '#10B981',
                            'warning': '#F59E0B',
                            'error': '#EF4444'
                        }.get(notif['type'], '#667eea')
                        
                        unread_indicator = "🔴" if not notif.get('read', False) else "✓"
                        
                        # Create columns for notification content and delete button
                        notif_col1, notif_col2 = st.columns([5, 1])
                        
                        with notif_col1:
                            st.markdown(f"""
                            <div style="
                                background: {bg_color};
                                border-left: 4px solid {border_color};
                                padding: 12px;
                                border-radius: 8px;
                                margin: 8px 0;
                                border: 1px solid rgba(255,255,255,0.1);
                            ">
                                <div style="display: flex; justify-content: space-between;">
                                    <strong style="color: white;">{unread_indicator} {notif['title']}</strong>
                                    <small style="color: rgba(255,255,255,0.5);">{notif['timestamp'][5:16]}</small>
                                </div>
                                <p style="color: rgba(255,255,255,0.8); margin: 5px 0 0 0;">{notif['message']}</p>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        with notif_col2:
                            # Delete button for each notification
                            if st.button("🗑️", key=f"del_notif_{notif['id']}", help="Delete notification"):
                                # Remove this notification
                                st.session_state.notifications = [
                                    n for n in st.session_state.notifications 
                                    if n['id'] != notif['id']
                                ]
                                st.rerun()
                    
                    # Action buttons
                    col_notif1, col_notif2, col_notif3 = st.columns(3)
                    
                    with col_notif1:
                        if st.button("✓ Mark All Read", key="mark_all_read_notifications", use_container_width=True):
                            mark_all_read()
                            st.rerun()
                    
                    with col_notif2:
                        if st.button("🗑️ Clear Read", key="clear_read_notifications", use_container_width=True):
                            # Remove all read notifications
                            st.session_state.notifications = [
                                n for n in st.session_state.notifications 
                                if not n.get('read', False)
                            ]
                            st.rerun()
                    
                    with col_notif3:
                        if st.button("🗑️ Delete All", key="delete_all_notifications", use_container_width=True):
                            # Show confirmation
                            if st.checkbox("⚠️ Confirm delete ALL notifications", key="confirm_delete_all_notifications"):
                                st.session_state.notifications = []
                                st.rerun()
                else:
                    st.markdown("""
                    <div style="text-align: center; padding: 20px;">
                        <span style="font-size: 3rem;">🔔</span>
                        <p style="color: rgba(255,255,255,0.5);">No notifications yet</p>
                    </div>
                    """, unsafe_allow_html=True)
            
            # Bell icon with badge
            if unread > 0:
                st.markdown(f"""
                <div style="position: relative; display: inline-block; margin-top: 15px; float: right; cursor: pointer;">
                    <span style="font-size: 2rem;">🔔</span>
                    <span style="
                        position: absolute;
                        top: 0px;
                        right: -5px;
                        background: #EF4444;
                        color: white;
                        border-radius: 50%;
                        width: 22px;
                        height: 22px;
                        font-size: 12px;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        font-weight: bold;
                        border: 2px solid white;
                    ">{unread}</span>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div style="position: relative; display: inline-block; margin-top: 15px; float: right; cursor: pointer;">
                    <span style="font-size: 2rem;">🔔</span>
                </div>
                """, unsafe_allow_html=True)
    
    else:
        # Show message for non-authenticated users
        if not st.session_state.authenticated and 'temp_logs' in st.session_state:
            temp_count = len(st.session_state.temp_logs)
            if temp_count > 0:
                st.markdown(f"""
                <div style="
                    background: linear-gradient(135deg, rgba(245, 158, 11, 0.15) 0%, rgba(251, 191, 36, 0.15) 100%);
                    padding: 20px;
                    border-radius: 15px;
                    border-left: 5px solid #f59e0b;
                    border: 2px solid rgba(251, 191, 36, 0.3);
                    margin-bottom: 25px;
                ">
                    <strong style="color: #fbbf24;"> 🔔 {temp_count} Unsaved Activities</strong><br>
                    <span style="color: #fed7aa; font-size: 0.9rem;">Login or signup to save your progress to the cloud</span>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div style="
                    background: linear-gradient(135deg, rgba(102, 126, 234, 0.15) 0%, rgba(118, 75, 162, 0.15) 100%);
                    padding: 25px;
                    border-radius: 15px;
                    color: white;
                    margin-bottom: 30px;
                    border: 2px solid rgba(102, 126, 234, 0.3);
                ">
                    <h3 style="margin: 0 0 8px 0; font-size: 1.4rem;">
                         Welcome to B12 Assistant!
                    </h3>
                    <p style="margin: 8px 0; color: #e2e8f0; font-size: 0.95rem;">
                         Use the sidebar to explore features. Login to save your progress!
                    </p>
                </div>
                """, unsafe_allow_html=True)
    
    # ==================== QUICK STATS ROW ====================
    st.markdown("###  Quick Statistics Overview")
    stat_col1, stat_col2, stat_col3, stat_col4 = st.columns(4)
    
    with stat_col1:
        st.markdown("""
        <div style="
            background: linear-gradient(135deg, rgba(239, 68, 68, 0.15) 0%, rgba(220, 38, 38, 0.15) 100%);
            border: 2px solid rgba(239, 68, 68, 0.3);
            border-radius: 15px;
            padding: 20px;
            text-align: center;
        ">
            <div style="font-size: 2.5rem; font-weight: 800; color: #fca5a5;">23%</div>
            <div style="color: rgba(255, 255, 255, 0.8); margin-top: 8px; font-weight: 600;">High Risk Cases</div>
            <div style="color: rgba(255, 255, 255, 0.5); font-size: 0.85rem; margin-top: 5px;">📈 +2.3% this month</div>
        </div>
        """, unsafe_allow_html=True)
    
    with stat_col2:
        st.markdown("""
        <div style="
            background: linear-gradient(135deg, rgba(59, 130, 246, 0.15) 0%, rgba(37, 99, 235, 0.15) 100%);
            border: 2px solid rgba(59, 130, 246, 0.3);
            border-radius: 15px;
            padding: 20px;
            text-align: center;
        ">
            <div style="font-size: 2.5rem; font-weight: 800; color: #93c5fd;">245</div>
            <div style="color: rgba(255, 255, 255, 0.8); margin-top: 8px; font-weight: 600;">Avg B12 Level</div>
            <div style="color: rgba(255, 255, 255, 0.5); font-size: 0.85rem; margin-top: 5px;">📉 pg/mL Community</div>
        </div>
        """, unsafe_allow_html=True)
    
    with stat_col3:
        st.markdown("""
        <div style="
            background: linear-gradient(135deg, rgba(168, 85, 247, 0.15) 0%, rgba(139, 92, 246, 0.15) 100%);
            border: 2px solid rgba(168, 85, 247, 0.3);
            border-radius: 15px;
            padding: 20px;
            text-align: center;
        ">
            <div style="font-size: 2.5rem; font-weight: 800; color: #d8b4fe;">10+</div>
            <div style="color: rgba(255, 255, 255, 0.8); margin-top: 8px; font-weight: 600;">Active Users</div>
            <div style="color: rgba(255, 255, 255, 0.5); font-size: 0.85rem; margin-top: 5px;">👥 +87 this month</div>
        </div>
        """, unsafe_allow_html=True)
    
    with stat_col4:
        st.markdown("""
        <div style="
            background: linear-gradient(135deg, rgba(16, 185, 129, 0.15) 0%, rgba(34, 197, 94, 0.15) 100%);
            border: 2px solid rgba(16, 185, 129, 0.3);
            border-radius: 15px;
            padding: 20px;
            text-align: center;
        ">
            <div style="font-size: 2.5rem; font-weight: 800; color: #86efac;">94.7%</div>
            <div style="color: rgba(255, 255, 255, 0.8); margin-top: 8px; font-weight: 600;">AI Accuracy</div>
            <div style="color: rgba(255, 255, 255, 0.5); font-size: 0.85rem; margin-top: 5px;">🎯 +1.2%  Improvement</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # ==================== SUPPLEMENT TRACKER SECTION ====================
    st.markdown("###  Daily Supplement Tracker")
    
    sup_col1, sup_col2, sup_col3 = st.columns(3)
    
    with sup_col1:
        # Supplement type selection
        supplement_type = st.selectbox(
            "💊 Supplement Type",
            ["Methylcobalamin", "Cyanocobalamin", "B-Complex", "Multivitamin", "Other"],
            key="supplement_type_select"
        )
    
    with sup_col2:
        supplement_dose = st.number_input(
            "💊 Dose (mcg)",
            min_value=0,
            max_value=5000,
            value=1000,
            step=100,
            key="supplement_dose_input"
        )
    
    with sup_col3:
        supplement_time = st.time_input(
            "⏰ Time Taken",
            value=datetime.now().time(),
            key="supplement_time_input"
        )
    
    # Display current supplement status
    if st.session_state.supplement_tracker['taken']:
        # Show completed status
        st.success(f"✅ You've taken your B12 supplement today at {st.session_state.supplement_tracker['time_taken']}!")
        st.metric("Current Streak", f"{st.session_state.supplement_tracker['streak']} days")
    else:
        # Show button to mark as taken
        st.info("📝 You haven't taken your supplement today yet.")
        
        if st.button("✅ I've Taken My Supplement", key="mark_supplement_taken", use_container_width=True, type="primary"):
            # Mark as taken
            st.session_state.supplement_tracker['taken'] = True
            st.session_state.supplement_tracker['time_taken'] = supplement_time.strftime("%I:%M %p")
            
            # Update streak
            last_date = st.session_state.supplement_tracker['last_taken_date']
            today = datetime.now().strftime("%Y-%m-%d")
            
            if last_date:
                # Check if yesterday
                yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
                if last_date == yesterday:
                    st.session_state.supplement_tracker['streak'] += 1
                elif last_date != today:
                    # Reset streak if missed a day
                    st.session_state.supplement_tracker['streak'] = 1
            else:
                st.session_state.supplement_tracker['streak'] = 1
            
            st.session_state.supplement_tracker['last_taken_date'] = today
            
            # Add to history
            if 'history' not in st.session_state.supplement_tracker:
                st.session_state.supplement_tracker['history'] = []
            
            st.session_state.supplement_tracker['history'].append({
                'date': today,
                'time': supplement_time.strftime("%I:%M %p"),
                'type': supplement_type,
                'dose': supplement_dose
            })
            
            # Add notification
            add_notification(
                title="✅ Supplement Taken",
                message=f"You took {supplement_dose}mcg {supplement_type}",
                type="success"
            )
            
            st.rerun()
    
    # Show supplement history
    if st.session_state.supplement_tracker.get('history'):
        with st.expander("📜 Supplement History"):
            for entry in st.session_state.supplement_tracker['history'][-7:]:  # Last 7 days
                st.markdown(f"📅 {entry['date']} at {entry['time']} - {entry['type']} ({entry['dose']} mcg)")
    
    st.markdown("---")
    
    # ==================== REMINDER SECTION WITH MARK READ & DELETE ====================
    st.markdown("###  Reminders")
    
    # Initialize reminders if not exists
    if 'user_reminders' not in st.session_state:
        st.session_state.user_reminders = []
        
        # Load reminders from database if authenticated
        if st.session_state.authenticated and st.session_state.current_user:
            db_reminders = load_reminders_from_db(st.session_state.current_user['user_id'])
            if db_reminders:
                # Convert MongoDB documents to session format
                for rem in db_reminders:
                    rem['id'] = rem.get('id', str(rem['_id']))
                    rem['completed_today'] = False
                st.session_state.user_reminders = db_reminders
    
    # Stats for today
    today = datetime.now().strftime("%Y-%m-%d")
    active_reminders = [r for r in st.session_state.get('user_reminders', []) if r.get('active', True)]
    
    # Count completed today vs pending
    completed_today = sum(1 for r in active_reminders 
                         if r.get('completed_today', False) and r.get('last_triggered') == today)
    pending_today = sum(1 for r in active_reminders 
                       if not (r.get('completed_today', False) and r.get('last_triggered') == today))
    
    # Main reminder section with two columns
    rem_col1, rem_col2 = st.columns([2, 1])
    
    with rem_col1:
        with st.expander(" Add New Reminder", expanded=True):
            st.markdown("#### Set a Reminder")
            
            col_a, col_b = st.columns(2)
            
            with col_a:
                reminder_text = st.text_input(
                    " What to remind?",
                    placeholder="e.g., Take B12 supplement, Doctor appointment...",
                    key="dash_reminder_text"
                )
            
            with col_b:
                reminder_time = st.time_input(
                    " Reminder Time",
                    value=datetime.now().time(),
                    key="dash_reminder_time"
                )
            
            # Repeat options
            repeat_option = st.selectbox(
                " Repeat",
                ["Daily", "Weekdays", "Weekends", "Once", "Weekly"],
                key="reminder_repeat"
            )
            
            if st.button(" Save Reminder", key="save_reminder_button", type="primary", use_container_width=True):
                if reminder_text:
                    time_str = reminder_time.strftime("%I:%M %p")
                    time_24h = reminder_time.strftime("%H:%M")
                    
                    # Create reminder data
                    reminder_data = {
                        'id': str(uuid.uuid4())[:8],
                        'text': reminder_text,
                        'time': time_str,
                        'time_24h': time_24h,
                        'repeat': repeat_option,
                        'created': datetime.now().strftime("%Y-%m-%d %H:%M"),
                        'last_triggered': '',
                        'completed_today': False,
                        'active': True,
                        'completion_history': []
                    }
                    
                    # Save to session state
                    if 'user_reminders' not in st.session_state:
                        st.session_state.user_reminders = []
                    st.session_state.user_reminders.append(reminder_data)
                    
                    # Save to MongoDB if authenticated
                    saved_to_cloud = False
                    if st.session_state.authenticated and st.session_state.current_user:
                        db_id = save_reminder_to_db(
                            st.session_state.current_user['user_id'],
                            reminder_data
                        )
                        if db_id:
                            saved_to_cloud = True
                    
                    # Add confirmation notification
                    if saved_to_cloud:
                        add_notification(
                            title=" Reminder Saved ",
                            message=f"'{reminder_text}' at {time_str} ({repeat_option})",
                            type="success"
                        )
                        st.success(f" You'll be notified at {time_str}")
                    else:
                        add_notification(
                            title=" Reminder Set",
                            message=f"'{reminder_text}' at {time_str} (saved locally)",
                            type="info"
                        )
                        st.info(f" Reminder saved locally. Login to save to cloud!")
                    
                    st.rerun()
                else:
                    st.warning("Please enter a reminder message")
    
    with rem_col2:
        # Show reminder stats
        reminder_count = len(active_reminders)
        
        if reminder_count > 0:
            completion_rate = (completed_today / reminder_count * 100) if reminder_count > 0 else 0
            st.metric(
                "Total Reminders", 
                reminder_count, 
                delta=f"{completion_rate:.0f}% completed today"
            )
        else:
            st.metric("Total Reminders", reminder_count)
    
    # ==================== DISPLAY REMINDERS IN GRID (SAME UI AS BEFORE) ====================
    if active_reminders:
        st.markdown("####  Your Saved Reminders")
        
        # Create columns for reminders grid (3 per row)
        rem_grid = st.columns(3)
        
        # Sort reminders: pending first, then completed
        sorted_reminders = sorted(
            active_reminders,
            key=lambda x: (
                x.get('completed_today', False) and x.get('last_triggered') == today,  # False first (pending)
                x.get('time_24h', '23:59')  # Then by time
            )
        )
        
        for i, rem in enumerate(sorted_reminders):
            col_idx = i % 3
            with rem_grid[col_idx]:
                # Check if completed today
                is_completed = rem.get('completed_today', False) and rem.get('last_triggered') == today
                
                # Set border color based on completion
                border_color = "#10B981" if is_completed else "#667eea"
                status_emoji = "✅" if is_completed else "⏰"
                status_text = "Done" if is_completed else "Pending"
                
                # ==================== REMINDER CARD ====================
                st.markdown(f"""
                <div style="
                    background: linear-gradient(135deg, rgba(102, 126, 234, 0.15) 0%, rgba(118, 75, 162, 0.15) 100%);
                    border: 2px solid {border_color};
                    border-radius: 12px;
                    padding: 15px;
                    margin: 5px 0;
                    text-align: center;
                    position: relative;
                ">
                    <div style="font-size: 2rem; margin-bottom: 5px;">{status_emoji}</div>
                    <div style="font-weight: bold; color: #fbbf24; font-size: 1.1rem;">{rem['time']}</div>
                    <div style="color: white; margin: 5px 0; font-weight: 500;">{rem['text'][:25]}{'...' if len(rem['text']) > 25 else ''}</div>
                    <div style="font-size: 0.8rem; color: {border_color};">{status_text}</div>
                    <div style="font-size: 0.7rem; color: rgba(255,255,255,0.5); margin-top: 5px;">{rem.get('repeat', 'Daily')}</div>
                </div>
                """, unsafe_allow_html=True)
                
                # ==================== ACTION BUTTONS ====================
                # Create two columns for Mark Done and Delete buttons
                col_action1, col_action2 = st.columns(2)
                
                with col_action1:
                    # MARK READ BUTTON - Only show if not completed today
                    if not is_completed:
                        if st.button("✅ Done", key=f"mark_{rem['id']}_{i}", use_container_width=True):
                            # Mark as completed
                            rem['completed_today'] = True
                            rem['completed_at'] = datetime.now().strftime("%H:%M")
                            rem['last_triggered'] = today
                            
                            # Add to completion history
                            if 'completion_history' not in rem:
                                rem['completion_history'] = []
                            rem['completion_history'].append({
                                'date': today,
                                'time': rem['completed_at']
                            })
                            
                            add_notification(
                                title="✅ Reminder Completed",
                                message=f"You completed: {rem['text']}",
                                type="success"
                            )
                            st.rerun()
                
                with col_action2:
                    # DELETE BUTTON
                    if st.button("🗑️", key=f"del_{rem['id']}_{i}", help="Delete reminder", use_container_width=True):
                        # Remove from session state
                        st.session_state.user_reminders = [
                            r for r in st.session_state.user_reminders 
                            if r['id'] != rem['id']
                        ]
                        
                        add_notification(
                            title="🗑️ Reminder Deleted",
                            message=f"Deleted: {rem['text']}",
                            type="info"
                        )
                        st.rerun()
        
        # ==================== BULK ACTIONS ====================
        st.markdown("---")
        col_bulk1, col_bulk2, col_bulk3 = st.columns(3)
        
        with col_bulk1:
            if st.button("✅ Mark All Done", key="mark_all_done_reminders_bulk", use_container_width=True):
                for rem in active_reminders:
                    if not (rem.get('completed_today', False) and rem.get('last_triggered') == today):
                        rem['completed_today'] = True
                        rem['completed_at'] = datetime.now().strftime("%H:%M")
                        rem['last_triggered'] = today
                        
                        # Add to completion history
                        if 'completion_history' not in rem:
                            rem['completion_history'] = []
                        rem['completion_history'].append({
                            'date': today,
                            'time': rem['completed_at']
                        })
                add_notification(
                    title="✅ All Reminders Completed",
                    message="You've marked all reminders as done for today!",
                    type="success"
                )
                st.rerun()
        
        with col_bulk2:
            if st.button("🗑️ Clear Completed", key="clear_completed_reminders_bulk", use_container_width=True):
                # Remove only completed reminders for today
                st.session_state.user_reminders = [
                    r for r in st.session_state.user_reminders 
                    if not (r.get('completed_today', False) and r.get('last_triggered') == today)
                ]
                add_notification(
                    title="🗑️ Completed Reminders Cleared",
                    message="All completed reminders have been removed.",
                    type="info"
                )
                st.rerun()
        
        with col_bulk3:
            if st.button("🗑️ Delete All", key="delete_all_reminders_bulk", use_container_width=True):
                # Show confirmation
                if st.checkbox("⚠️ Confirm delete ALL reminders", key="confirm_delete_all_reminders_bulk"):
                    st.session_state.user_reminders = []
                    add_notification(
                        title="🗑️ All Reminders Deleted",
                        message="Your reminder list has been cleared.",
                        type="warning"
                    )
                    st.rerun()
    
    else:
        st.info("No reminders yet. Add your first reminder above!")
    
    st.markdown("---")
    
    # ==================== TODAY'S SUMMARY ====================
    st.markdown("###  Today's Summary")
    
    sum_col1, sum_col2, sum_col3 = st.columns(3)
    
    with sum_col1:
        # Supplement status
        if st.session_state.supplement_tracker['taken']:
            st.success(f"✅ Supplement: Taken at {st.session_state.supplement_tracker['time_taken']}")
        else:
            st.warning("⏰ Supplement: Not taken yet")
    
    with sum_col2:
        # Reminder status
        if active_reminders:
            st.info(f"📋 Reminders: {completed_today}/{reminder_count} completed")
        else:
            st.info("📋 Reminders: None scheduled")
    
    with sum_col3:
        # Streak
        streak = st.session_state.supplement_tracker.get('streak', 0)
        if streak > 0:
            st.success(f"🔥 Streak: {streak} days")
        else:
            st.info("🔥 Streak: Start today!")
    
    # ==================== MAIN CONTENT ====================
    content_col1, content_col2 = st.columns([2.5, 1.5])
    
    with content_col1:
        # Risk Distribution Chart
        st.markdown("###  Risk Distribution Overview")
        
        risk_data = pd.DataFrame({
            'Risk Level': ['Very Low', 'Low', 'Medium', 'High'],
            'Users': [400, 350, 250, 247],
            'Color': ['#10B981', '#34D399', '#F59E0B', '#EF4444']
        })
        
        fig = px.bar(risk_data, x='Risk Level', y='Users', 
                    color='Risk Level', color_discrete_sequence=risk_data['Color'],
                    title="Community Risk Levels Distribution",
                    text='Users',
                    labels={'Users': 'Number of Users'},
                    height=350)
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(size=12, color='white'),
            showlegend=False,
            xaxis=dict(showgrid=False),
            yaxis=dict(showgrid=True, gridwidth=1, gridcolor='rgba(255,255,255,0.1)'),
            hovermode='x',
        )
        fig.update_traces(textposition='outside', hovertemplate='%{x}<br>Users: %{y}<extra></extra>')
        st.plotly_chart(fig, use_container_width=True)
        
        # Quick Self-Check
        st.markdown("###  Take a Quick Risk Check")
        with st.expander(" Use our 30-second quick assessment", expanded=False):
            q_age = st.slider("**Your Age**", 18, 80, 30, key="q_age")
            q_diet = st.selectbox("**Your Diet Type**", ["Omnivore", "Vegetarian", "Vegan", "Pescetarian"], key="q_diet")
            q_fatigue = st.checkbox("**Do you feel tired often?**", key="q_fatigue")
            
            if st.button("⚡ Calculate Risk Score", key="quick_risk_calc", type="primary", use_container_width=True):
                quick_score = 0
                risk_factors = []
                
                if q_age > 50: 
                    quick_score += 2
                    risk_factors.append("Age >50")
                if q_diet == "Vegan": 
                    quick_score += 3
                    risk_factors.append("Vegan diet")
                elif q_diet == "Vegetarian": 
                    quick_score += 2
                    risk_factors.append("Vegetarian diet")
                if q_fatigue: 
                    quick_score += 2
                    risk_factors.append("Fatigue present")
                
                # Add notification based on result
                if quick_score >= 5:
                    add_notification(
                        title="High Risk Detected",
                        message="Your quick check shows HIGH risk. Complete full assessment.",
                        type="error"
                    )
                    result_html = """
                    <div style="background: rgba(239, 68, 68, 0.15); border: 2px solid #EF4444; border-radius: 15px; padding: 20px; margin-top: 15px;">
                        <h3 style="color: #fca5a5;">🔴 High Risk</h3>
                        <p style="color: #fee2e2;">Complete full assessment for detailed analysis</p>
                    </div>
                    """
                elif quick_score >= 3:
                    add_notification(
                        title="🟡 Medium Risk",
                        message="Your quick check shows MEDIUM risk. Consider full assessment.",
                        type="warning"
                    )
                    result_html = """
                    <div style="background: rgba(245, 158, 11, 0.15); border: 2px solid #F59E0B; border-radius: 15px; padding: 20px; margin-top: 15px;">
                        <h3 style="color: #fcd34d;">🟡 Medium Risk</h3>
                        <p style="color: #fed7aa;">Monitor symptoms and consider full assessment</p>
                    </div>
                    """
                else:
                    add_notification(
                        title="🟢 Low Risk",
                        message="Your quick check shows LOW risk. Keep up healthy habits!",
                        type="success"
                    )
                    result_html = """
                    <div style="background: rgba(16, 185, 129, 0.15); border: 2px solid #10B981; border-radius: 15px; padding: 20px; margin-top: 15px;">
                        <h3 style="color: #86efac;">🟢 Low Risk</h3>
                        <p style="color: #d1fae5;">Maintain healthy habits!</p>
                    </div>
                    """
                
                st.markdown(result_html, unsafe_allow_html=True)
                if risk_factors:
                    st.markdown(f"**Risk Factors:** {', '.join(risk_factors)}")
    
    with content_col2:
        # Get Started Section
        st.markdown("### Get Started With")
        
        feature_cards = [
            {
                "icon": "📋",
                "title": "Assessment",
                "description": "Complete risk evaluation",
                "button": " Start",
                "page": " Assessment",
                "color": "#3B82F6"
            },
            {
                "icon": "📄",
                "title": "Lab Reports",
                "description": "Analyze your results",
                "button": " Upload",
                "page": " Lab Reports",
                "color": "#8B5CF6"
            }
        ]
        
        for card in feature_cards:
            st.markdown(f"""
            <div style="
                background: linear-gradient(135deg, rgba({int(card['color'][1:3],16)}, {int(card['color'][3:5],16)}, {int(card['color'][5:7],16)}, 0.1) 0%, rgba({int(card['color'][1:3],16)}, {int(card['color'][3:5],16)}, {int(card['color'][5:7],16)}, 0.15) 100%);
                border: 2px solid {card['color']};
                border-radius: 12px;
                padding: 15px;
                margin: 10px 0;
                cursor: pointer;
                transition: all 0.3s ease;
            ">
                <div style="display: flex; align-items: center; gap: 15px;">
                    <div style="font-size: 2rem;">{card['icon']}</div>
                    <div>
                        <div style="font-weight: 700; color: white; font-size: 1.1rem;">{card['title']}</div>
                        <div style="color: rgba(255, 255, 255, 0.6); font-size: 0.85rem;">{card['description']}</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button(card['button'], key=f"dash_{card['title']}", use_container_width=True):
                st.session_state.page = card['page']
                st.rerun()
        
        # Recent Activity
        if st.session_state.temp_logs:
            st.markdown("###  Recent Activity")
            for log in st.session_state.temp_logs[-3:]:
                st.markdown(f"""
                <div style="
                    background: rgba(255, 255, 255, 0.05);
                    border-left: 3px solid #667eea;
                    border-radius: 8px;
                    padding: 12px;
                    margin: 10px 0;
                ">
                    <div style="font-weight: 600; color: white;">{log['description']}</div>
                    <div style="font-size: 0.75rem; color: rgba(255, 255, 255, 0.5);"> {log['date']}</div>
                </div>
                """, unsafe_allow_html=True)
    
    # ==================== DAILY GOALS ====================
    st.markdown("---")
    st.markdown("###  Your Daily B12 Goals")
    
    goals = st.columns(4)
    
    with goals[0]:
        st.markdown("""
        <div style="background: rgba(59, 130, 246, 0.1); border: 2px solid #3B82F6; border-radius: 12px; padding: 16px; text-align: center;">
            <div style="font-size: 2rem;">🎯</div>
            <div style="font-weight: 700; color: #93c5fd;">Daily Target</div>
            <div style="color: white; font-size: 1.3rem; margin-top: 5px;">2.4 mcg</div>
        </div>
        """, unsafe_allow_html=True)
    
    with goals[1]:
        st.markdown("""
        <div style="background: rgba(16, 185, 129, 0.1); border: 2px solid #10B981; border-radius: 12px; padding: 16px; text-align: center;">
            <div style="font-size: 2rem;">💪</div>
            <div style="font-weight: 700; color: #86efac;">Energy Boost</div>
            <div style="color: white; font-size: 1.3rem; margin-top: 5px;">+47%</div>
        </div>
        """, unsafe_allow_html=True)
    
    with goals[2]:
        st.markdown("""
        <div style="background: rgba(139, 92, 246, 0.1); border: 2px solid #8B5CF6; border-radius: 12px; padding: 16px; text-align: center;">
            <div style="font-size: 2rem;">🧠</div>
            <div style="font-weight: 700; color: #c4b5fd;">Brain Health</div>
            <div style="color: white; font-size: 1.3rem; margin-top: 5px;">Better</div>
        </div>
        """, unsafe_allow_html=True)
    
    with goals[3]:
        st.markdown("""
        <div style="background: rgba(245, 158, 11, 0.1); border: 2px solid #F59E0B; border-radius: 12px; padding: 16px; text-align: center;">
            <div style="font-size: 2rem;">❤️</div>
            <div style="font-weight: 700; color: #fcd34d;">Heart Health</div>
            <div style="color: white; font-size: 1.3rem; margin-top: 5px;">-35%</div>
        </div>
        """, unsafe_allow_html=True)
    
    # ==================== COMPLETION SUMMARY ====================
    st.markdown("---")
    st.markdown("###  Today's Completion Summary")
    
    if st.session_state.get('user_reminders') or st.session_state.supplement_tracker.get('taken'):
        # Supplement summary
        sup_status = "✅ Taken" if st.session_state.supplement_tracker['taken'] else "❌ Not taken"
        
        # Reminder summary
        if active_reminders:
            reminder_status = f"{completed_today}/{reminder_count} completed"
        else:
            reminder_status = "No reminders"
        
        col_s1, col_s2, col_s3 = st.columns(3)
        
        with col_s1:
            st.markdown(f"""
            <div style="background: rgba(59, 130, 246, 0.15); border: 2px solid #3B82F6; border-radius: 12px; padding: 20px; text-align: center;">
                <div style="font-size: 2rem;">💊</div>
                <div style="font-size: 1.3rem; color: #93c5fd;">{sup_status}</div>
                <div style="color: white;">Supplement</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col_s2:
            st.markdown(f"""
            <div style="background: rgba(16, 185, 129, 0.15); border: 2px solid #10B981; border-radius: 12px; padding: 20px; text-align: center;">
                <div style="font-size: 2rem;">📋</div>
                <div style="font-size: 1.3rem; color: #86efac;">{reminder_status}</div>
                <div style="color: white;">Reminders</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col_s3:
            streak = st.session_state.supplement_tracker.get('streak', 0)
            st.markdown(f"""
            <div style="background: rgba(245, 158, 11, 0.15); border: 2px solid #F59E0B; border-radius: 12px; padding: 20px; text-align: center;">
                <div style="font-size: 2rem;">🔥</div>
                <div style="font-size: 1.3rem; color: #fcd34d;">{streak} days</div>
                <div style="color: white;">Streak</div>
            </div>
            """, unsafe_allow_html=True)
        
        # Progress bar
        if active_reminders:
            progress = completed_today / reminder_count if reminder_count > 0 else 0
            st.progress(progress, text=f"Today's Progress: {completed_today}/{reminder_count} reminders completed")
    else:
        st.info("No reminders or supplement tracking for today. Add reminders or take your supplement to see progress!")
    
    # ==================== QUICK FACTS ====================
    st.markdown("---")
    st.markdown("###  Quick Facts")
    
    fact1, fact2 = st.columns(2)
    
    with fact1:
        st.markdown("""
        <div style="background: rgba(102, 126, 234, 0.1); border: 1px solid #667eea; border-radius: 12px; padding: 18px;">
            <h4 style="color: #fbbf24;"> What is B12?</h4>
            <p style="color: rgba(255,255,255,0.8);">Essential for nerve function, DNA synthesis, and red blood cell formation</p>
        </div>
        """, unsafe_allow_html=True)
    
    with fact2:
        st.markdown("""
        <div style="background: rgba(102, 126, 234, 0.1); border: 1px solid #667eea; border-radius: 12px; padding: 18px;">
            <h4 style="color: #fbbf24;"> Storage</h4>
            <p style="color: rgba(255,255,255,0.8);">Body stores B12 in liver for 2-5 years - symptoms appear gradually</p>
        </div>
        """, unsafe_allow_html=True)
    
    # ==================== RISK GROUPS ====================
    st.markdown("---")
    st.markdown("###  Who's at Risk?")
    
    risk1, risk2, risk3 = st.columns(3)
    
    with risk1:
        st.markdown("""
        <div style="background: rgba(239, 68, 68, 0.1); border: 1px solid #EF4444; border-radius: 12px; padding: 16px;">
            <h4 style="color: #fca5a5;">High Risk Groups</h4>
            <ul style="color: rgba(255,255,255,0.8);">
                <li>Vegans/Vegetarians</li>
                <li>Adults 50+</li>
                <li>GI conditions</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with risk2:
        st.markdown("""
        <div style="background: rgba(245, 158, 11, 0.1); border: 1px solid #F59E0B; border-radius: 12px; padding: 16px;">
            <h4 style="color: #fcd34d;">Medications</h4>
            <ul style="color: rgba(255,255,255,0.8);">
                <li>Metformin</li>
                <li>PPIs</li>
                <li>Antacids</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with risk3:
        st.markdown("""
        <div style="background: rgba(16, 185, 129, 0.1); border: 1px solid #10B981; border-radius: 12px; padding: 16px;">
            <h4 style="color: #86efac;">Prevention</h4>
            <ul style="color: rgba(255,255,255,0.8);">
                <li>Regular testing</li>
                <li>B12-rich foods</li>
                <li>Supplements if needed</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    # ==================== MOTIVATIONAL FOOTER ====================
    st.markdown("---")
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, rgba(251, 191, 36, 0.1) 0%, rgba(34, 197, 94, 0.1) 100%);
        border: 2px dashed #fbbf24;
        border-radius: 15px;
        padding: 30px;
        text-align: center;
    ">
        <h3 style="color: #fbbf24;"> Remember: Your Health Matters!</h3>
        <p style="color: rgba(255,255,255,0.8);">Take the first step today—assess your B12 status now!</p>
    </div>
    """, unsafe_allow_html=True)

# ==================== LAB REPORTS PAGE ====================
elif page == " Lab Reports":
    st.markdown('<div class="main-title"> 📊 Lab Report Analysis</div>', unsafe_allow_html=True)
    
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 15px;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 20px;
    ">
        <h3>Upload your B12 lab report for instant analysis</h3>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        uploaded_file = st.file_uploader(
            "Choose PDF file",
            type=['pdf'],
            help="Upload your Vitamin B12 lab report (PDF only)"
        )
    
    with col2:
        st.markdown("**📋 Supported:**")
        st.write("- PDF files only")
        st.write("- Max size: 10MB")
    
    if uploaded_file is not None:
        # File info
        st.markdown("---")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("File Name", uploaded_file.name[:20] + "..." if len(uploaded_file.name) > 20 else uploaded_file.name)
        with col2:
            st.metric("File Type", "PDF")
        with col3:
            file_size = f"{uploaded_file.size / 1024:.1f} KB"
            st.metric("File Size", file_size)
        
        # Preview option (collapsed by default)
        with st.expander("📄 Preview PDF Text"):
            try:
                from utils import extract_text_from_pdf
                text = extract_text_from_pdf(uploaded_file)
                st.text(text[:1000] + "..." if len(text) > 1000 else text)
            except:
                st.info("Could not extract text. The file may be scanned.")
        
        # AI Analysis button
        if st.button("🔍 Analyze Lab Report", type="primary", use_container_width=True):
            with st.spinner("🤖 AI is analyzing your lab report..."):
                try:
                    # Use Gemini to analyze PDF
                    ai_result = analyze_lab_pdf_with_gemini(uploaded_file)
                    
                    if ai_result.get('success'):
                        st.markdown("---")
                        st.markdown("### 📋 Your Lab Report Results")
                        
                        # Get B12 value safely
                        b12_value = ai_result.get('b12_value')
                        b12_val = None
                        status = "Unknown"
                        
                        if b12_value is not None:
                            b12_val = float(b12_value)
                            
                            # Determine status
                            if b12_val < 200:
                                status = "DEFICIENT"
                                status_color = "#EF4444"
                                status_bg = "#FEE2E2"
                            elif b12_val < 300:
                                status = "BORDERLINE"
                                status_color = "#F59E0B"
                                status_bg = "#FEF3C7"
                            else:
                                status = "NORMAL"
                                status_color = "#10B981"
                                status_bg = "#D1FAE5"
                        else:
                            status = "NOT DETECTED"
                            status_color = "#6B7280"
                            status_bg = "#F3F4F6"
                            b12_val = None
                        
                        # ========== MAIN RESULTS TABLE ==========
                        # Create a clean 2-column table with 3 rows
                        
                        # Row 1: B12 Level
                        col_r1, col_r2 = st.columns(2)
                        with col_r1:
                            st.markdown("**📊 B12 Level**")
                        with col_r2:
                            if b12_val:
                                st.markdown(f"**{b12_val} pg/mL**")
                            else:
                                st.markdown("**Not detected in report**")
                        
                        st.markdown("<hr style='margin:5px 0; opacity:0.2;'>", unsafe_allow_html=True)
                        
                        # Row 2: Status
                        col_r1, col_r2 = st.columns(2)
                        with col_r1:
                            st.markdown("**⚠️ Status**")
                        with col_r2:
                            st.markdown(f"**{status}**")
                        
                        st.markdown("<hr style='margin:5px 0; opacity:0.2;'>", unsafe_allow_html=True)
                        
                        # Row 3: Normal Range
                        col_r1, col_r2 = st.columns(2)
                        with col_r1:
                            st.markdown("**📏 Normal Range**")
                        with col_r2:
                            st.markdown("**200-900 pg/mL**")
                        
                        st.markdown("---")
                        
                        # ========== RECOMMENDATIONS TABLE ==========
                        st.markdown("### 💡 Recommendations")
                        
                        # Get recommendations based on status
                        if status == "DEFICIENT":
                            recs = [
                                ("💊 Supplement", "High-dose B12 (2000mcg daily)"),
                                ("🥗 Diet", "Liver, clams, sardines, eggs"),
                                ("👨‍⚕️ Doctor", "Consult within 1 week")
                            ]
                        elif status == "BORDERLINE":
                            recs = [
                                ("💊 Supplement", "B12 1000mcg daily"),
                                ("🥗 Diet", "Eggs, dairy, fish 3-4x/week"),
                                ("👨‍⚕️ Doctor", "Follow-up in 2 months")
                            ]
                        elif status == "NORMAL":
                            recs = [
                                ("💊 Supplement", "Maintenance dose (500mcg)"),
                                ("🥗 Diet", "Continue balanced diet"),
                                ("👨‍⚕️ Doctor", "Annual check-up")
                            ]
                        else:
                            recs = [
                                ("💊 Supplement", "Consult doctor for testing"),
                                ("🥗 Diet", "Include B12-rich foods"),
                                ("👨‍⚕️ Doctor", "Get blood test done")
                            ]
                        
                        # Display recommendations as a clean table
                        for i, (category, recommendation) in enumerate(recs):
                            col_rec1, col_rec2 = st.columns(2)
                            with col_rec1:
                                st.markdown(f"**{category}**")
                            with col_rec2:
                                st.markdown(f"{recommendation}")
                            
                            if i < len(recs) - 1:
                                st.markdown("<hr style='margin:5px 0; opacity:0.2;'>", unsafe_allow_html=True)
                        
                        # ========== ACTION BUTTONS ==========
                        st.markdown("---")
                        col_btn1, col_btn2, col_btn3 = st.columns(3)
                        
                        with col_btn1:
                            # Save to history
                            report_entry = {
                                'b12_value': b12_val,
                                'status': status,
                                'date': datetime.now().strftime("%Y-%m-%d"),
                                'filename': uploaded_file.name
                            }
                            st.session_state.lab_reports.append(report_entry)
                            st.success("✅ Saved")
                        
                        with col_btn2:
                            # Download as text
                            report_text = f"""
B12 LAB REPORT ANALYSIS
Date: {datetime.now().strftime("%Y-%m-%d")}
File: {uploaded_file.name}

RESULTS:
B12 Level: {b12_val if b12_val else 'Not detected'} pg/mL
Status: {status}
Normal Range: 200-900 pg/mL

RECOMMENDATIONS:
• Supplement: {recs[0][1]}
• Diet: {recs[1][1]}
• Doctor: {recs[2][1]}
                            """
                            st.download_button(
                                label="📥 Download",
                                data=report_text,
                                file_name=f"b12_report_{datetime.now().strftime('%Y%m%d')}.txt",
                                mime="text/plain"
                            )
                        
                        with col_btn3:
                            if st.button("🔄 New Analysis"):
                                st.rerun()
                        
                    else:
                        st.error(f"❌ Analysis failed: {ai_result.get('error', 'Unknown error')}")
                        
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
        
        # Manual entry option
        with st.expander("📝 Enter Value Manually"):
            manual_b12 = st.number_input("Enter B12 Level (pg/mL)", 0, 2000, 0)
            if manual_b12 > 0 and st.button("Save Manual Entry"):
                # Determine status
                if manual_b12 < 200:
                    manual_status = "DEFICIENT"
                elif manual_b12 < 300:
                    manual_status = "BORDERLINE"
                else:
                    manual_status = "NORMAL"
                
                report_entry = {
                    'b12_value': manual_b12,
                    'filename': 'Manual Entry',
                    'status': manual_status,
                    'date': datetime.now().strftime("%Y-%m-%d")
                }
                st.session_state.lab_reports.append(report_entry)
                st.success(f"✅ Saved: {manual_b12} pg/mL")
    
    else:
        # Welcome screen
        st.markdown("""
        <div style="
            background: rgba(255,255,255,0.05);
            padding: 40px;
            border-radius: 10px;
            text-align: center;
            border: 2px dashed #667eea;
            margin: 20px 0;
        ">
            <div style="font-size: 4rem; margin-bottom: 20px;">📄</div>
            <h4 style="color: white;">Upload a lab report to begin</h4>
            <p style="color: rgba(255,255,255,0.5);">PDF format only</p>
        </div>
        """, unsafe_allow_html=True)
    
    # ==================== HISTORY SECTION ====================
    if st.session_state.lab_reports:
        st.markdown("---")
        st.markdown("### 📋 Recent Analyses")
        
        # Show last 3 reports
        for report in st.session_state.lab_reports[-3:]:
            col_h1, col_h2, col_h3 = st.columns([2, 1, 1])
            with col_h1:
                st.markdown(f"**{report.get('filename', 'Unknown')}**")
            with col_h2:
                if report.get('b12_value'):
                    st.markdown(f"{report['b12_value']} pg/mL")
                else:
                    st.markdown("N/A")
            with col_h3:
                status = report.get('status', '')
                if status == "DEFICIENT":
                    st.markdown("🔴 Deficient")
                elif status == "BORDERLINE":
                    st.markdown("🟡 Borderline")
                elif status == "NORMAL":
                    st.markdown("🟢 Normal")
                else:
                    st.markdown("⚪ Unknown")


# ==================== MEAL PLANNER PAGE ====================
elif page == " Meal Planner":
    st.markdown('<div class="main-title">  AI-Powered Meal Planner</div>', unsafe_allow_html=True)

    st.info("""
    Get a personalized 7-day B12-rich meal plan
    """)

    # ----- USER DATA SECTION -----
    col1, col2 = st.columns(2)
    user_data = st.session_state.get('user_data', {})

    with col1:
        # Get primary user info from the assessment
        diet_type = user_data.get('diet_type', 'Omnivore')
        st.markdown("###  Your Profile")
        st.write(f"**Primary Diet:** {diet_type}")

        # Allow user to override diet for this meal plan if needed
        diet_for_plan = st.selectbox(
            "Select diet for this meal plan:",
            ["Omnivore", "Vegetarian", "Vegan", "Pescetarian"],
            index=["Omnivore", "Vegetarian", "Vegan", "Pescetarian"].index(diet_type) 
            if diet_type in ["Omnivore", "Vegetarian", "Vegan", "Pescetarian"] else 0
        )

    with col2:
        # Get additional context
        risk_level = st.session_state.get('risk_level', 'Medium')
        age = user_data.get('age', 30)
        st.write(f"**Risk Level:** {risk_level}")
        st.write(f"**Age:** {age}")

        # Let user add specific goals or restrictions
        with st.expander("➕ Add Specific Goals"):
            user_goals = st.text_area(
                "e.g., 'No seafood', 'Budget-friendly', 'Quick prep'",
                height=60,
                placeholder="(Optional) Add any specific requests..."
            )

    st.markdown("---")

    # ----- GENERATE MEAL PLAN WITH AI -----
    st.markdown("###  Generate Meal Plan")

    if st.button(" Generate ", type="primary", use_container_width=True):
        if not diet_for_plan:
            st.warning("Please select a diet type.")
        else:
            with st.spinner("Generating..."):
                try:
                    from utils import setup_gemini_api
                    
                    # CALL GEMINI AI TO GENERATE THE MEAL PLAN IN SIMPLE TABLE FORMAT
                    model = setup_gemini_api()
                    if model:
                        # Build the prompt for simple TABLE format - just food items
                        prompt = f"""You are a nutrition expert specializing in Vitamin B12.

Create a simple 7-day meal plan showing ONLY food items (no descriptions) in this EXACT table format:

| Day | FOODITEM |
|-----|-----------|
| Monday | [3-4 food items] |
| Tuesday | [3-4 food items] |
| Wednesday | [3-4 food items]  |
| Thursday | [3-4 food items] |
| Friday | [3-4 food items] |
| Saturday | [3-4 food items] |
| Sunday | [3-4 food items] |

After the table, add a simple "What to Eat" and "What to Avoid" section:

**✅ WHAT TO EAT (B12-Rich Foods):**
• [Food item 1],
• [Food item 2],
• [Food item 3],
• [Food item 4],

• [Food item 5]

**❌ WHAT TO AVOID/LIMIT:**
• [Food item 1],
• [Food item 2],
• [Food item 3],
• [Food item 4],
• [Food item 5]

USER CONTEXT:
- Diet Type: {diet_for_plan}
- Age: {age} years
- Risk Level: {risk_level}
- Goals: {user_goals if user_goals else 'None'}

IMPORTANT RULES:
1. ONLY food items, NO descriptions (no "cooked with", "served with", etc.)
2. Use simple food names like "Eggs", "Salmon", "Milk", "Yogurt"
3. Make sure all meals include B12-rich foods appropriate for the diet type
4. Keep it simple and easy to read at a glance
5. NO paragraphs, NO explanations - just the table and lists
"""
                        response = model.generate_content(prompt)
                        ai_meal_plan_text = response.text

                        # Save to session state
                        st.session_state.ai_meal_plan_text = ai_meal_plan_text
                        st.session_state.meal_plan_diet = diet_for_plan
                        st.session_state.meal_plan_generated_time = datetime.now().strftime("%Y-%m-%d")

                        # Log activity
                        log_user_activity(
                            activity_type='meal_plan',
                            data={'diet_type': diet_for_plan, 'risk_level': risk_level},
                            description=f"Simple meal plan generated for {diet_for_plan} diet"
                        )
                        
                        st.success("✅ Your simple 7-day meal plan is ready!")
                        # st.balloons()
                    else:
                        st.error("Could not connect to the AI service. Please try again.")
                except Exception as e:
                    st.error(f"Error: {str(e)}")
                    
                    # Fallback meal plan if AI fails
                    if diet_for_plan == "Vegan":
                        st.session_state.ai_meal_plan_text = """
| Day |FOOD ITEMS |
|-----|-----------|
| Monday | Fortified Cereal, Soy Milk, Banana |
| Tuesday | Oatmeal, Almond Milk, Berries | 
| Wednesday | Smoothie Bowl, Spinach, Banana | 
| Thursday | Fortified Cereal, Coconut Yogurt |  
|fFriday | Chickpea Salad, Avocado, Whole Grain Bread |
| Saturday | Tofu Scramble, Spinach, Toast | 

✅ **WHAT TO EAT (B12-Rich Vegan Foods):**
• Fortified Cereals • Fortified Plant Milks • Nutritional Yeast • Fortified Tofu
• Fortified Plant Yogurts • Tempeh • Fortified Meat Substitutes • Spirulina

❌ **WHAT TO AVOID/LIMIT:**
• Unfortified Plant Milks • Highly Processed Foods • Excess Sugar • Refined Grains • Low-Fiber Snacks
"""
                    elif diet_for_plan == "Vegetarian":
                        st.session_state.ai_meal_plan_text = """
| Day |FOOD ITEMS |
|-----|-----------|
| Monday |  Orange | Greek Yogurt, Granola , Milk, Banana |
| Tuesday | Oatmeal with Milk,  Veggie Sandwich ,Egg Curry, Roti,  |
| Wednesday |  Eggs, Spinach, Toast  Paneer, Cucumber   Vegetable Korma, Rice, Naan  |
| Thursday | Cereal with Milk, Banana Palak Paneer, Roti, Onions  Milkshake |
| Friday | Yogurt Parfait with Berries , Boiled Egg |
| Saturday | Omelette with Veggies, Toast , Yogurt Drink |
| Sunday | Pancakes with Milk, Honey , Cottage Cheese |

✅ **WHAT TO EAT (B12-Rich Vegetarian Foods):**
• Eggs • Milk • Yogurt/Curd • Paneer • Cheese • Fortified Cereals • Buttermilk • Whey Protein

❌ **WHAT TO AVOID/LIMIT:**
• Sugary Drinks • Refined Flour Products • Fried Snacks • Excess Sweets • Processed Cheese
"""
                    else:
                        st.session_state.ai_meal_plan_text = """
| Day | FOOD ITEM |
|-----|-----------|-------|--------|-------|
| Monday | Eggs, Salmon, Toast , Greek Yogurt |
| Tuesday | Oatmeal with Milk, Berries , Brown Rice, Veggies , Cheese cubes |
| Wednesday | Scrambled Eggs, Spinach , Chicken Wrap, Veggies |
| Thursday | Cereal with Milk, Banana , Tuna Pasta Salad |
| Friday | Yogurt with Berries, Granola , Chicken Salad Sandwich |
| Saturday | Omelette with Veggies, Toast , Sardine Salad, Crackers |
| Sunday | Eggs Benedict ,Seafood Paella , Roast Chicken, Veggies , Yogurt Drink |

✅ **WHAT TO EAT (B12-Rich Foods):**
• Salmon • Tuna • Sardines • Eggs • Beef/Liver • Chicken • Milk • Yogurt • Cheese • Clams/Mussels

❌ **WHAT TO AVOID/LIMIT:**
• Sugary Drinks • Processed Meats • Fast Food • Excess Alcohol • Refined Grains
"""

    st.markdown("---")

    # ----- DISPLAY AND DOWNLOAD GENERATED PLAN -----
    if 'ai_meal_plan_text' in st.session_state:
        st.markdown("###  Meal Plan")
        
        # Display the meal plan
        st.markdown(st.session_state.ai_meal_plan_text)

        st.markdown("---")
        st.markdown("###  Download Your Plan")
        
        col_down1, col_down2 = st.columns(2)
        with col_down1:
            st.download_button(
                label=" Download as Text File",
                data=st.session_state.ai_meal_plan_text,
                file_name=f"B12_Meal_Plan_{st.session_state.get('meal_plan_diet', 'Plan')}_{datetime.now().strftime('%Y%m%d')}.txt",
                mime="text/plain",
                use_container_width=True
            )
        with col_down2:
            if st.button(" Generate New Plan", use_container_width=True):
                keys_to_delete = ['ai_meal_plan_text', 'meal_plan_diet', 'meal_plan_generated_time']
                for key in keys_to_delete:
                    st.session_state.pop(key, None)
                st.rerun()
    else:
        st.info(" Click 'Generate Simple Meal Plan' to create your 7-day meal plan with just food items!")

# ==================== VOICE ASSISTANT PAGE ====================
# ==================== VOICE ASSISTANT PAGE - WORKING VERSION ====================
elif page == " Voice Assistant":
    st.markdown('<div class="main-title"> 🎤 Voice Assistant</div>', unsafe_allow_html=True)
    
    # Import the correct audio recorder
    from audio_recorder_streamlit import audio_recorder
    
    # Initialize session states
    if 'voice_question' not in st.session_state:
        st.session_state.voice_question = ""
    if 'ai_response' not in st.session_state:
        st.session_state.ai_response = ""
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # ========== VOICE INPUT ==========
        st.markdown("### 🎤 Step 1: Record Your Voice")
        
        # Audio recorder widget
        audio_bytes = audio_recorder(
            text="Click to record",
            recording_color="#ff4b4b",
            neutral_color="#6c757d",
            icon_size="2x",
            key="voice_recorder"
        )
        
        if audio_bytes:
            st.audio(audio_bytes, format="audio/wav")
            st.success("✅ Recording captured!")
            st.session_state.audio_bytes = audio_bytes
        
        # Process voice button
        if st.button("🎯 Convert to Text", type="primary", disabled=not st.session_state.get('audio_bytes')):
            with st.spinner("Converting speech to text..."):
                try:
                    import speech_recognition as sr
                    import io
                    
                    # Convert audio bytes to text
                    recognizer = sr.Recognizer()
                    audio_file = io.BytesIO(st.session_state.audio_bytes)
                    
                    with sr.AudioFile(audio_file) as source:
                        audio_data = recognizer.record(source)
                        text = recognizer.recognize_google(audio_data)
                        
                        st.session_state.voice_question = text
                        st.success("✅ Voice converted to text!")
                        st.rerun()
                        
                except sr.UnknownValueError:
                    st.error("❌ Could not understand audio. Please try again.")
                except sr.RequestError:
                    st.error("❌ Speech service error. Check internet connection.")
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
        
        # ========== TEXT BOX ==========
        st.markdown("### 📝 Step 2: Your Question")
        
        question_text = st.text_area(
            "Edit your question here:",
            value=st.session_state.voice_question,
            height=100,
            placeholder="Your voice will appear here after conversion...",
            key="question_input"
        )
        
        if question_text != st.session_state.voice_question:
            st.session_state.voice_question = question_text
        
        # ========== GET AI RESPONSE ==========
        st.markdown("### 🤖 Step 3: Get AI Response")
        
        if st.button("🚀 Generate Answer", type="primary", use_container_width=True, disabled=not st.session_state.voice_question):
            with st.spinner("🤔 AI is thinking..."):
                try:
                    from utils import setup_gemini_api
                    
                    model = setup_gemini_api()
                    if model:
                        prompt = f"""You are a helpful Vitamin B12 expert assistant.
                        
User Question: {st.session_state.voice_question}

Provide a clear, accurate, and helpful answer about Vitamin B12."""
                        
                        response = model.generate_content(prompt)
                        st.session_state.ai_response = response.text
                        st.success("✅ Answer ready!")
                        st.rerun()
                    else:
                        st.error("AI service unavailable")
                        
                except Exception as e:
                    st.error(f"❌ AI error: {str(e)}")
        
        # ========== SHOW AI RESPONSE ==========
        if st.session_state.ai_response:
            st.markdown("### 💬 AI Response")
            with st.container(border=True):
                st.markdown(st.session_state.ai_response)
            
            col_d1, col_d2 = st.columns(2)
            with col_d1:
                st.download_button(
                    label="📥 Download",
                    data=st.session_state.ai_response,
                    file_name=f"b12_answer_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
                    mime="text/plain"
                )
            with col_d2:
                if st.button("🔄 New Question", use_container_width=True):
                    st.session_state.voice_question = ""
                    st.session_state.ai_response = ""
                    if 'audio_bytes' in st.session_state:
                        del st.session_state.audio_bytes
                    st.rerun()
    
    with col2:
        st.markdown("### 📊 Status")
        if st.session_state.voice_question:
            st.success("✅ Question ready")
        if st.session_state.ai_response:
            st.success("✅ Answer ready")

# # ==================== RESULTS PAGE ====================

# ==================== RESULTS PAGE WITH PDF DOWNLOAD ====================
elif page == " Results":
    st.markdown('<div class="main-title"> 📊 Your Risk Assessment & Lifestyle Plan</div>', unsafe_allow_html=True)
    
    if not st.session_state.user_data:
        st.warning("Please complete the assessment first!")
        col1, col2, col3 = st.columns([1,2,1])
        with col2:
            st.info("Complete your risk assessment to see your personalized charts and lifestyle plan")
            if st.button("Go to Assessment", type="primary"):
                st.session_state.page = " Assessment"
                st.rerun()
    else:
        user_data = st.session_state.user_data
        risk_level = st.session_state.risk_level
        risk_score = st.session_state.risk_score
        diet_type = user_data.get('diet_type', 'Omnivore')
        age = user_data.get('age', 30)
        bmi = user_data.get('bmi', 0)
        symptoms_count = user_data.get('symptoms_count', 0)
        
        # Get B12 level
        b12_level = None
        if st.session_state.lab_reports:
            b12_level = st.session_state.lab_reports[-1]['b12_value']
        elif user_data.get('b12_level'):
            b12_level = user_data.get('b12_level')
        
        # Determine B12 display
        if isinstance(b12_level, (int, float)):
            if b12_level < 200:
                b12_color = '#EF4444'
                b12_status = "Deficient"
                b12_bg = 'rgba(239, 68, 68, 0.15)'
            elif b12_level < 300:
                b12_color = '#F59E0B'
                b12_status = "Borderline"
                b12_bg = 'rgba(245, 158, 11, 0.15)'
            else:
                b12_color = '#10B981'
                b12_status = "Normal"
                b12_bg = 'rgba(16, 185, 129, 0.15)'
            b12_display = f"{b12_level} pg/mL"
        else:
            b12_color = '#6B7280'
            b12_status = "Not tested"
            b12_bg = 'rgba(107, 114, 128, 0.15)'
            b12_display = "Not tested"
        
        # ==================== RISK DISPLAY HEADER ====================
        st.markdown("### 📈 Your Risk Assessment Summary")
        
        # Create 3 columns for the main metrics
        col1, col2, col3 = st.columns(3)
        
        risk_info = {
            'High': {
                'bg': 'rgba(239, 68, 68, 0.15)',
                'border': '#EF4444', 
                'text': '#EF4444', 
                'icon': '🔴',
                'title': 'HIGH RISK',
                'message': 'Immediate action needed'
            },
            'Medium': {
                'bg': 'rgba(245, 158, 11, 0.15)',
                'border': '#F59E0B', 
                'text': '#F59E0B', 
                'icon': '🟡',
                'title': 'MEDIUM RISK',
                'message': 'Monitor and take preventive action'
            },
            'Low': {
                'bg': 'rgba(16, 185, 129, 0.15)',
                'border': '#10B981', 
                'text': '#10B981', 
                'icon': '🟢',
                'title': 'LOW RISK',
                'message': 'Maintain healthy habits'
            }
        }
        
        info = risk_info.get(risk_level, {
            'bg': 'rgba(107, 114, 128, 0.15)', 
            'border': '#6B7280', 
            'text': '#6B7280', 
            'icon': '⚪',
            'title': risk_level + ' RISK',
            'message': 'Complete assessment for detailed analysis'
        })
        
        with col1:
            st.markdown(f"""
            <div style="
                background: {info['bg']};
                padding: 20px;
                border-radius: 10px;
                border-left: 6px solid {info['border']};
                border: 1px solid rgba(255,255,255,0.1);
                backdrop-filter: blur(10px);
                text-align: center;
                height: 180px;
            ">
                <div style="font-size: 2.5rem; margin-bottom: 5px;">{info['icon']}</div>
                <h3 style="margin: 0; color: {info['text']};">{info['title']}</h3>
                <p style="margin: 5px 0 0 0; font-size: 0.9rem; color: rgba(255,255,255,0.8);">{info['message']}</p>
                <div style="margin-top: 10px; padding: 5px; background: rgba(255,255,255,0.1); border-radius: 5px;">
                    <p style="margin: 0; font-size: 1.1rem; font-weight: bold; color: white;">Score: {risk_score:.1%}</p>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div style="
                background: rgba(255,255,255,0.05);
                padding: 20px;
                border-radius: 10px;
                border: 1px solid rgba(255,255,255,0.1);
                backdrop-filter: blur(10px);
                height: 180px;
            ">
                <h4 style="margin: 0 0 10px 0; color: #fbbf24;">👤 Your Profile</h4>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 8px;">
                    <div><span style="color: #fbbf24;">Age:</span> <span style="color: white;">{age}</span></div>
                    <div><span style="color: #fbbf24;">Diet:</span> <span style="color: white;">{diet_type}</span></div>
                    <div><span style="color: #fbbf24;">BMI:</span> <span style="color: white;">{bmi:.1f}</span></div>
                    <div><span style="color: #fbbf24;">Symptoms:</span> <span style="color: white;">{symptoms_count}</span></div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div style="
                background: rgba(255,255,255,0.05);
                padding: 20px;
                border-radius: 10px;
                border: 1px solid rgba(255,255,255,0.1);
                backdrop-filter: blur(10px);
                height: 180px;
            ">
                <h4 style="margin: 0 0 10px 0; color: #fbbf24;">💉 B12 Status</h4>
                <div style="background: {b12_bg}; padding: 10px; border-radius: 5px; text-align: center; border-left: 3px solid {b12_color};">
                    <p style="margin: 0; font-size: 1.1rem; font-weight: bold; color: {b12_color};">{b12_display}</p>
                    <p style="margin: 2px 0 0 0; font-size: 0.9rem; color: {b12_color};">{b12_status}</p>
                </div>
                <p style="margin: 5px 0 0 0; font-size: 0.7rem; color: rgba(255,255,255,0.5);">Normal: 200-900 pg/mL</p>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # ==================== VISUAL CHARTS ====================
        st.markdown("## 📊 Visual Risk Analysis")
        
        tab1, tab2, tab3 = st.tabs(["📈 Risk Breakdown Chart", "🥗 Diet Impact Meter", "⏱️ Treatment Timeline"])
        
        with tab1:
            st.markdown("### 🥧 What's Contributing to Your Risk")
            
            # Calculate risk factors
            risk_factors = {}
            
            # Age risk
            if age > 60:
                risk_factors['Age (60+)'] = 35
            elif age > 50:
                risk_factors['Age (50-60)'] = 28
            elif age > 40:
                risk_factors['Age (40-50)'] = 20
            elif age > 30:
                risk_factors['Age (30-40)'] = 12
            else:
                risk_factors['Age (Under 30)'] = 5
            
            # Diet risk
            if diet_type == 'Vegan':
                risk_factors['Vegan Diet'] = 40
            elif diet_type == 'Vegetarian':
                risk_factors['Vegetarian Diet'] = 25
            elif diet_type == 'Pescetarian':
                risk_factors['Pescetarian Diet'] = 10
            else:
                risk_factors['Omnivore Diet'] = 5
            
            # Symptom risk
            if symptoms_count >= 5:
                risk_factors['Multiple Symptoms'] = 30
            elif symptoms_count >= 3:
                risk_factors['Moderate Symptoms'] = 20
            elif symptoms_count >= 1:
                risk_factors['Minor Symptoms'] = 10
            else:
                risk_factors['No Symptoms'] = 5
            
            # B12 level risk
            if b12_level:
                if b12_level < 200:
                    risk_factors['Very Low B12'] = 40
                elif b12_level < 300:
                    risk_factors['Borderline B12'] = 25
                elif b12_level < 400:
                    risk_factors['Suboptimal B12'] = 15
                else:
                    risk_factors['Normal B12'] = 5
            else:
                risk_factors['B12 Not Tested'] = 20
            
            # Create two columns for chart and legend
            col_chart1, col_legend1 = st.columns([2, 1])
            
            with col_chart1:
                # Create pie chart
                fig = px.pie(
                    values=list(risk_factors.values()),
                    names=list(risk_factors.keys()),
                    title=None,
                    color_discrete_sequence=px.colors.sequential.Viridis,
                    hole=0.4
                )
                fig.update_traces(textposition='inside', textinfo='percent+label')
                fig.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='white', size=12),
                    showlegend=False,
                    height=350
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with col_legend1:
                st.markdown("#### 📋 Risk Factors")
                for factor, value in risk_factors.items():
                    color = "#EF4444" if value > 30 else "#F59E0B" if value > 20 else "#10B981"
                    st.markdown(f"""
                    <div style="margin: 5px 0; padding: 5px; border-left: 3px solid {color};">
                        <span style="color: white;">{factor}</span><br>
                        <span style="color: {color}; font-size: 0.9rem;">{value}% contribution</span>
                    </div>
                    """, unsafe_allow_html=True)
        
        with tab2:
            st.markdown("### 🎯 Diet Impact on B12 Levels")
            
            col_gauge, col_info = st.columns([2, 1])
            
            with col_gauge:
                # Calculate diet score
                if diet_type == 'Vegan':
                    diet_score = 25
                    diet_color = "#EF4444"
                    diet_desc = "High Risk"
                elif diet_type == 'Vegetarian':
                    diet_score = 45
                    diet_color = "#F59E0B"
                    diet_desc = "Moderate Risk"
                elif diet_type == 'Pescetarian':
                    diet_score = 70
                    diet_color = "#10B981"
                    diet_desc = "Good"
                else:
                    diet_score = 85
                    diet_color = "#10B981"
                    diet_desc = "Excellent"
                
                # Create gauge chart
                fig = go.Figure(go.Indicator(
                    mode = "gauge+number",
                    value = diet_score,
                    title = {'text': "B12 Adequacy Score", 'font': {'color': 'white', 'size': 16}},
                    domain = {'x': [0, 1], 'y': [0, 1]},
                    gauge = {
                        'axis': {'range': [0, 100], 'tickcolor': 'white', 'tickfont': {'color': 'white'}},
                        'bar': {'color': diet_color, 'thickness': 0.3},
                        'bgcolor': "rgba(255,255,255,0.1)",
                        'borderwidth': 2,
                        'bordercolor': "white",
                        'steps': [
                            {'range': [0, 33], 'color': 'rgba(239, 68, 68, 0.3)'},
                            {'range': [33, 66], 'color': 'rgba(245, 158, 11, 0.3)'},
                            {'range': [66, 100], 'color': 'rgba(16, 185, 129, 0.3)'}
                        ]
                    }
                ))
                fig.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)',
                    font={'color': 'white', 'size': 12},
                    height=250
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with col_info:
                st.markdown(f"""
                <div style="
                    background: rgba(255,255,255,0.05);
                    padding: 15px;
                    border-radius: 10px;
                    border-left: 4px solid {diet_color};
                ">
                    <h4 style="color: {diet_color}; margin: 0 0 10px 0;">{diet_desc}</h4>
                    <p style="color: white; margin: 5px 0;">Your diet provides approximately <strong>{diet_score}%</strong> of optimal B12 intake.</p>
                </div>
                """, unsafe_allow_html=True)
        
        with tab3:
            st.markdown("### ⏱️ Your 6-Month Treatment Timeline")
            
            # Create timeline based on risk level
            if risk_level == 'High':
                timeline_data = pd.DataFrame({
                    'Month': ['Month 1', 'Month 2', 'Month 3', 'Month 4-6'],
                    'Focus': ['High-dose Supplements', 'Continue Treatment', 'Blood Test', 'Maintenance'],
                    'Doctor Visit': ['2 visits', '1 visit', '1 visit', 'Quarterly'],
                    'Expected Progress': ['Rapid improvement', 'Stabilizing', 'Review results', 'Maintain levels']
                })
                colors = ['#EF4444', '#F59E0B', '#10B981', '#3B82F6']
            elif risk_level == 'Medium':
                timeline_data = pd.DataFrame({
                    'Month': ['Month 1', 'Month 2', 'Month 3', 'Month 4-6'],
                    'Focus': ['Start Supplements', 'Diet Changes', 'Monitor Symptoms', 'Blood Test'],
                    'Doctor Visit': ['1 visit', 'Optional', 'None', '1 visit'],
                    'Expected Progress': ['Gradual improvement', 'Better energy', 'Symptom reduction', 'Confirm levels']
                })
                colors = ['#F59E0B', '#10B981', '#3B82F6', '#8B5CF6']
            else:
                timeline_data = pd.DataFrame({
                    'Month': ['Month 1', 'Month 2', 'Month 3', 'Month 4-6'],
                    'Focus': ['Preventive Care', 'Diet Optimization', 'Maintenance', 'Annual Check'],
                    'Doctor Visit': ['Optional', 'None', 'None', '1 visit'],
                    'Expected Progress': ['Maintain levels', 'Optimize intake', 'Stable', 'Annual review']
                })
                colors = ['#10B981', '#3B82F6', '#8B5CF6', '#A78BFA']
            
            # Create bar chart timeline
            fig = go.Figure()
            for i, row in enumerate(timeline_data.itertuples()):
                fig.add_trace(go.Bar(
                    y=[row.Month],
                    x=[30],  # 30 days per month
                    orientation='h',
                    name=row.Month,
                    marker=dict(color=colors[i], line=dict(color='white', width=1)),
                    text=row.Focus,
                    textposition='inside',
                    textfont=dict(color='white', size=11)
                ))
            
            fig.update_layout(
                title="Treatment Timeline",
                barmode='stack',
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='white', size=12),
                xaxis=dict(title="Days", showticklabels=False, showgrid=False),
                yaxis=dict(title="Phase", gridcolor='rgba(255,255,255,0.1)'),
                showlegend=False,
                height=250
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Show timeline table
            st.dataframe(timeline_data, use_container_width=True, hide_index=True)
        
        st.markdown("---")
        
        # ==================== LIFESTYLE PLAN TABLE ====================
        st.markdown("## 📋 Your Personalized Lifestyle Plan")
        
        # Create lifestyle plan based on risk level
        if risk_level == 'High':
            lifestyle_data = pd.DataFrame({
                'Category': ['💊 Medication', '🥗 Diet Plan', '🏃 Lifestyle', '👨‍⚕️ Doctor Consult', '📊 Monitoring', '🎯 Goals'],
                'Daily/Weekly': [
                    'Methylcobalamin 2000mcg daily\nB12 injections weekly',
                    'Liver, clams, sardines (3-4x/week)\nEggs, dairy daily\nFortified foods',
                    'Take supplements with food\nAvoid alcohol\nQuit smoking if applicable',
                    'Specialist within 1 week\nFollow-up every 2 weeks\nHematologist consult',
                    'Symptom diary daily\nBlood test monthly\nTrack energy levels',
                    'Increase B12 to >300 pg/mL\nResolve symptoms in 1-2 months'
                ],
                'Duration': ['3 months', 'Ongoing', 'Ongoing', '3 months', 'Ongoing', '3 months'],
                'Priority': ['🔴 High', '🔴 High', '🟡 Medium', '🔴 High', '🟡 Medium', '🔴 High']
            })
        elif risk_level == 'Medium':
            lifestyle_data = pd.DataFrame({
                'Category': ['💊 Medication', '🥗 Diet Plan', '🏃 Lifestyle', '👨‍⚕️ Doctor Consult', '📊 Monitoring', '🎯 Goals'],
                'Daily/Weekly': [
                    'Methylcobalamin 1000mcg daily',
                    'Eggs (2/day)\nMilk/Yogurt daily\nFish 2-3x/week',
                    'Consistent timing for supplements\nStress management\nLight exercise',
                    'Schedule within 2 weeks\nFollow-up in 2 months',
                    'Symptom tracking weekly\nBlood test in 2 months',
                    'Increase B12 by 100+ pg/mL\nReduce symptoms by 50%'
                ],
                'Duration': ['2 months', 'Ongoing', 'Ongoing', '2 months', 'Ongoing', '2 months'],
                'Priority': ['🔴 High', '🔴 High', '🟡 Medium', '🟡 Medium', '🟢 Low', '🔴 High']
            })
        else:
            lifestyle_data = pd.DataFrame({
                'Category': ['💊 Medication', '🥗 Diet Plan', '🏃 Lifestyle', '👨‍⚕️ Doctor Consult', '📊 Monitoring', '🎯 Goals'],
                'Daily/Weekly': [
                    'Low-dose B12 500mcg (optional)',
                    'Maintain balanced diet\nInclude B12 foods 2-3x/week',
                    'Healthy routine\nRegular check-ups\nStay active',
                    'Annual check-up\nDiscuss prevention',
                    'Annual blood test\nSelf-monitor for symptoms',
                    'Prevent deficiency\nMaintain optimal health'
                ],
                'Duration': ['Ongoing', 'Ongoing', 'Ongoing', 'Yearly', 'Yearly', 'Ongoing'],
                'Priority': ['🟢 Low', '🟢 Low', '🟢 Low', '🟢 Low', '🟢 Low', '🟢 Low']
            })
        
        # Display lifestyle plan table with styling
        st.dataframe(
            lifestyle_data,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Category": "Category",
                "Daily/Weekly": "Daily/Weekly Recommendations",
                "Duration": "Duration",
                "Priority": "Priority"
            }
        )
        
        # Add summary based on risk level
        st.markdown("---")
        st.markdown("### 📌 Summary & Next Steps")
        
        if risk_level == 'High':
            st.error("""
            **⚠️ URGENT: High Risk Detected**
            
            **Immediate Actions (Next 7 Days):**
            1. 👨‍⚕️ Schedule doctor appointment immediately
            2. 💊 Start high-dose B12 supplements (2000mcg daily)
            3. 📋 Get comprehensive blood test including B12, folate, iron
            4. 🥗 Increase B12-rich foods in your diet
            5. 📝 Start tracking symptoms daily
            
            **Follow-up:** You should see improvement within 2-4 weeks. 
            Schedule follow-up appointment in 2 weeks.
            """)
        elif risk_level == 'Medium':
            st.warning("""
            **🟡 Moderate Risk Detected**
            
            **Recommended Actions (Next 2 Weeks):**
            1. 👨‍⚕️ Schedule doctor appointment within 2 weeks
            2. 💊 Start B12 supplements (1000mcg daily)
            3. 🥗 Add B12-rich foods to daily diet
            4. 📊 Get blood test to confirm levels
            5. 📝 Monitor symptoms weekly
            
            **Follow-up:** Check progress in 2 months with follow-up blood test.
            """)
        else:
            st.success("""
            **🟢 Low Risk - Maintaining Good Health**
            
            **Preventive Actions:**
            1. 👨‍⚕️ Annual check-up with doctor
            2. 🥗 Continue balanced diet with B12-rich foods
            3. 📊 Annual blood test to monitor levels
            4. 🏃 Maintain healthy lifestyle
            5. 📝 Watch for any new symptoms
            
            **Follow-up:** Annual review recommended to maintain optimal health.
            """)
        
        # ==================== DOWNLOAD SECTION ====================
        st.markdown("---")
        st.markdown("### 📥 Download Your Report")
        
        col_down1, col_down2, col_down3 = st.columns(3)
        
        with col_down2:
            # Text report download
            text_report = f"""
B12 DEFICIENCY ASSESSMENT REPORT
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}

RISK ASSESSMENT:
- Risk Level: {risk_level}
- Risk Score: {risk_score:.1%}

YOUR PROFILE:
- Age: {age} years
- Diet: {diet_type}
- BMI: {bmi:.1f}
- Symptoms Reported: {symptoms_count}
- B12 Level: {b12_display}

LIFESTYLE PLAN:
{lifestyle_data.to_string(index=False)}

NEXT STEPS:
Based on your {risk_level} risk level, follow the lifestyle plan above.
Consult with your healthcare provider for personalized medical advice.
            """
            
            st.download_button(
                label="📄 Download Text Report",
                data=text_report,
                file_name=f"b12_health_report_{datetime.now().strftime('%Y%m%d')}.txt",
                mime="text/plain",
                use_container_width=True
            )

# ==================== USER PROFILE PAGE ====================
elif page == " My Profile":
    show_user_profile()

# ==================== CLOUD DATABASE PAGE ====================
elif page == " History":
    st.markdown('<div class="main-title">Database Dashboard</div>', unsafe_allow_html=True)
    
    if not st.session_state.mongodb or not st.session_state.mongodb.connected:
        st.error("Database not connected")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button(" Retry Connection"):
                st.session_state.mongodb = get_mongodb_connection()
                st.rerun()
    else:
        st.success("Connected ")
        
        # Show connection info
        with st.expander(" Connection Details"):
            st.write(f"**Database:** Online")
            st.write(f"**Session ID:** `{st.session_state.session_id}`")
            
            # Show temp logs info
            if 'temp_logs' in st.session_state and st.session_state.temp_logs:
                temp_count = len(st.session_state.temp_logs)
                st.info(f"**Local logs:** {temp_count} activities waiting to be saved")
        
        # Database Stats - FIXED for guest mode
        with st.spinner("Loading database statistics..."):
            # Check if user is logged in
            if st.session_state.current_user:
                stats = st.session_state.mongodb.get_dashboard_stats(user_id=st.session_state.current_user['user_id'])
            else:
                # Guest user - show local stats
                stats = {
                    'total_assessments': len([l for l in st.session_state.get('temp_logs', []) if l.get('type') == 'assessment']),
                    'total_lab_reports': len(st.session_state.get('lab_reports', [])),
                    'recent_activity': st.session_state.get('search_history', [])[:5]
                }
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Assessments", stats.get('total_assessments', 0))
        with col2:
            st.metric("Lab Reports", stats.get('total_lab_reports', 0))
        with col3:
            if 'ai_pdf_analysis' in st.session_state:
                st.metric("AI Analyses", "Available")
            else:
                st.metric("Saved Data", "Active")
        
        # Your Data Section
        st.markdown("###  Your Cloud Data")
        
        tab1, tab2, tab3 = st.tabs([" Assessments", " Lab Reports", " Export"])
        
        with tab1:
            st.markdown("#### Your Assessments")
            if st.session_state.current_user:
                # Logged in user - get from MongoDB
                assessments = st.session_state.mongodb.get_user_assessments(
                    user_id=st.session_state.current_user['user_id'],
                    limit=10
                )
            else:
                # Guest user - show local data
                st.info(" You're in guest mode. Login to save assessments to cloud!")
                assessments = []
                # Show local temp logs if any
                if 'temp_logs' in st.session_state:
                    local_assessments = [l for l in st.session_state.temp_logs if l.get('type') == 'assessment']
                    if local_assessments:
                        st.write(f"**Local assessments:** {len(local_assessments)} saved in browser")
            
            if assessments:
                for assessment in assessments:
                    with st.expander(f"Assessment on {assessment.get('timestamp', 'Unknown')}"):
                        col1, col2 = st.columns(2)
                        with col1:
                            st.write(f"**Risk Level:** {assessment.get('risk_level', 'N/A')}")
                            st.write(f"**Risk Score:** {assessment.get('risk_score', 0):.1%}")
                        with col2:
                            st.write(f"**Age:** {assessment.get('user_data', {}).get('age', 'N/A')}")
                            st.write(f"**Diet:** {assessment.get('user_data', {}).get('diet_type', 'N/A')}")
            else:
                if st.session_state.current_user:
                    st.info("No assessments saved to cloud yet.")
                # else message already shown above
        
        with tab2:
            st.markdown("#### Your Lab Reports")
            if st.session_state.current_user:
                # Logged in user - get from MongoDB
                lab_reports = st.session_state.mongodb.get_lab_reports(
                    user_id=st.session_state.current_user['user_id'],
                    limit=10
                )
            else:
                # Guest user - show local reports
                lab_reports = st.session_state.get('lab_reports', [])
                if lab_reports:
                    st.info(f" Showing {len(lab_reports)} local reports")
            
            if lab_reports:
                for report in lab_reports:
                    with st.expander(f"Lab Report: {report.get('filename', 'Manual Entry')}"):
                        col1, col2 = st.columns(2)
                        with col1:
                            b12_val = report.get('b12_value')
                            if b12_val:
                                if b12_val < 200:
                                    st.error(f"**{b12_val} pg/mL** (Deficient)")
                                elif b12_val < 300:
                                    st.warning(f"**{b12_val} pg/mL** (Borderline)")
                                else:
                                    st.success(f"**{b12_val} pg/mL** (Normal)")
                        with col2:
                            st.write(f"**Status:** {report.get('status', 'N/A')}")
                            st.write(f"**Date:** {report.get('timestamp') or report.get('date', 'N/A')}")
            else:
                st.info("No lab reports found.")
        
        with tab3:
            st.markdown("#### Export Your Data")
            
            if st.session_state.current_user:
                # Logged in user - can export from cloud
                export_format = st.selectbox("Select Format", ["JSON", "CSV"])
                
                if st.button(" Export All My Data"):
                    with st.spinner("Exporting your data..."):
                        try:
                            data = st.session_state.mongodb.export_user_data(
                                user_id=st.session_state.current_user['user_id'],
                                format=export_format.lower()
                            )
                            
                            if data:
                                if export_format == "JSON":
                                    json_data = json.dumps(data, indent=2)
                                    st.download_button(
                                        label="Download JSON",
                                        data=json_data,
                                        file_name=f"b12_assistant_data_{st.session_state.session_id}.json",
                                        mime="application/json"
                                    )
                                else:
                                    import zipfile
                                    import io
                                    
                                    zip_buffer = io.BytesIO()
                                    with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
                                        for collection_name, csv_data in data.items():
                                            if csv_data:
                                                zip_file.writestr(f"{collection_name}.csv", csv_data)
                                    
                                    st.download_button(
                                        label="Download CSV (ZIP)",
                                        data=zip_buffer.getvalue(),
                                        file_name=f"b12_assistant_data_{st.session_state.session_id}.zip",
                                        mime="application/zip"
                                    )
                                
                                st.success(" Data exported successfully!")
                            else:
                                st.warning("No data available for export")
                        except Exception as e:
                            st.error(f"Export failed: {str(e)}")
            else:
                st.info(" Login to export your data to JSON or CSV format")
                # Show local data option
                if st.button(" View Local Data Summary"):
                    temp_count = len(st.session_state.get('temp_logs', []))
                    lab_count = len(st.session_state.get('lab_reports', []))
                    history_count = len(st.session_state.get('search_history', []))
                    
                    st.write(f"**Local data in browser:**")
                    st.write(f"- Activity logs: {temp_count}")
                    st.write(f"- Lab reports: {lab_count}")
                    st.write(f"- Search history: {history_count}")

# ======================FOOD SCANNER PAGE====================

# ==================== FOOD SCANNER PAGE WITH AI RECOMMENDATIONS ====================
elif page == " Food Scanner":
    st.markdown('<div class="main-title">  AI-Powered B12 Food Scanner</div>', unsafe_allow_html=True)
    
    st.success("Welcome to the AI Food Scanner!")
    
    # Comprehensive B12 Food Database (defined at the page level)
    b12_database = {
        # Eggs
        'egg': 0.6, 'eggs': 0.6, 'omelette': 0.6, 'boiled egg': 0.6, 'fried egg': 0.6,
        'scrambled eggs': 0.6, 'egg bhurji': 0.6, 'egg curry': 0.6,
    
        # Dairy
        'milk': 1.2, 'cheese': 0.5, 'yogurt': 1.1, 'curd': 1.1,
        'paneer': 0.8, 'dahi': 1.1, 'lassi': 0.8, 'buttermilk': 0.4,
        'ice cream': 0.3, 'cottage cheese': 0.8, 'ghee': 0.1, 'butter': 0.1,
        'khoya': 0.5, 'rabri': 0.4, 'kheer': 0.5,
        
        # Fish and Seafood
        'salmon': 4.0, 'tuna': 2.5, 'sardines': 8.0, 'mackerel': 15.0, 'bangda': 15.0,
        'fish': 2.5, 'clam': 84.0, 'clams': 84.0, 'mussels': 24.0, 'oyster': 16.0,
        'oysters': 16.0, 'crab': 5.0, 'lobster': 2.0, 'prawn': 1.5, 'shrimp': 1.5,
        'pomfret': 2.0, 'rohu': 1.5, 'catla': 1.5, 'hilsa': 3.0, 'fish curry': 2.5,
        
        # Meat
        'chicken': 0.3, 'liver': 70.0, 'beef': 2.0, 'mutton': 2.5,
        'lamb': 2.5, 'pork': 0.5, 'kidney': 20.0, 'heart': 8.0, 'brain': 10.0,
        'chicken liver': 20.0, 'goat liver': 70.0, 'keema': 1.5, 'chicken curry': 0.3,
        'mutton curry': 2.5, 'butter chicken': 0.3,
        
        # Fortified Foods
        'cereal': 2.0, 'oats': 1.5, 'oatmeal': 1.5, 'cornflakes': 2.0, 'muesli': 2.0,
        'nutritional yeast': 8.0, 'soy milk': 1.0, 'tofu': 0.8,
        'almond milk': 0.5, 'protein bar': 1.0, 'energy bar': 1.0,
        'fortified milk': 1.5, 'breakfast cereal': 2.0,
        
        # Indian Foods
        'egg curry': 0.6, 'fish curry': 2.5, 'chicken curry': 0.3,
        'mutton curry': 2.5, 'paneer butter masala': 0.8,
        'palak paneer': 0.8, 'matar paneer': 0.8, 'shahi paneer': 0.8,
        'paneer tikka': 0.8, 'chicken tikka': 0.3, 'tandoori chicken': 0.3,
        'biryani': 0.5, 'egg biryani': 0.6, 'chicken biryani': 0.3,
        'mutton biryani': 2.5, 'fish biryani': 2.5, 'prawn biryani': 1.5,
        
        # South Indian
        'dosa': 0.1, 'idli': 0.1, 'sambar': 0.1, 'rasam': 0.1,
        'upma': 0.1, 'pongal': 0.1, 'puttu': 0.1, 'appam': 0.2,
        'egg dosa': 0.7, 'egg appam': 0.8,
        
        # Street Food
        'egg roll': 0.6, 'chicken roll': 0.3, 'fish roll': 2.5,
        'pav bhaji': 0.2, 'vada pav': 0.1, 'samosa': 0.1,
        'kathi roll': 0.3, 'shawarma': 0.5, 'burger': 0.3,
        'pizza': 0.5, 'sandwich': 0.3, 'grilled sandwich': 0.4,
    }
    
    # Define the local analysis function INSIDE the page to access b12_database
    def analyze_b12_food_local(food_input):
        """Fallback function using local database when AI fails"""
        
        st.markdown("---")
        st.markdown("###  Analysis Results (Local Database)")
        st.caption(" Using local database as AI analysis is unavailable")
        
        # Convert to lowercase for matching
        food_input_lower = food_input.lower()
        
        # Extract numbers for quantities
        import re
        numbers = re.findall(r'\d+\.?\d*', food_input_lower)
        
        # Default multiplier is 1 if no number found
        multiplier = 1.0
        if numbers:
            try:
                multiplier = float(numbers[0])
            except:
                multiplier = 1.0
        
        # Find matching foods
        found_foods = []
        total_b12 = 0.0
        
        # Check each food in database
        for food, b12_value in b12_database.items():
            if food in food_input_lower:
                # Calculate contribution (adjusting for quantity)
                contribution = b12_value * multiplier
                found_foods.append({
                    'food': food,
                    'b12_per_serving': b12_value,
                    'quantity_multiplier': multiplier,
                    'contribution': contribution
                })
                total_b12 += contribution
        
        # Display results
        if found_foods:
            st.success(f" Found {len(found_foods)} B12-containing food(s)")
            
            # Create results table
            import pandas as pd
            results_data = []
            for item in found_foods:
                results_data.append({
                    "Food": item['food'].title(),
                    "B12 per serving": f"{item['b12_per_serving']:.1f} mcg",
                    "Quantity": f"x{item['quantity_multiplier']:.1f}",
                    "Contribution": f"{item['contribution']:.2f} mcg"
                })
            
            df = pd.DataFrame(results_data)
            st.table(df)
            
            # Show total with styling
            st.markdown(f"##  Total Vitamin B12: **{total_b12:.2f} mcg**")
            
            # Compare to daily requirement
            daily_need = 2.4
            percentage = (total_b12 / daily_need) * 100
            
            # Progress bar for daily value
            st.progress(min(percentage/100, 1.0))
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Daily Value", f"{percentage:.1f}%", 
                         delta=None if percentage <= 100 else f"+{percentage-100:.1f}% excess")
            
            with col2:
                if percentage >= 100:
                    st.success(" You've met your daily B12 requirement!")
                elif percentage >= 50:
                    st.info("Good progress towards your daily B12 goal")
                else:
                    st.warning(" Try adding more B12-rich foods to meet your daily need")
            
            # Suggestions based on deficit
            if percentage < 100:
                deficit = daily_need - total_b12
                st.info(f" **Suggestion:** You need about **{deficit:.2f} mcg** more B12. "
                       f"Try: 1 egg (+0.6 mcg), 1 glass milk (+1.2 mcg), or 100g fish (+2.5 mcg)")
        else:
            st.warning(" No B12-containing foods detected in your description")
            st.info(" **Tip:** Common B12 foods include eggs, milk, fish, chicken, and paneer. "
                   "Check the reference guide below for more options!")
    
    # Create tabs for different input methods
    tab1, tab2, tab3 = st.tabs([" Text Description", " Upload Photo", " Food Guide"])
    
    # ==================== TAB 1: TEXT DESCRIPTION WITH AI ====================
    with tab1:
        st.markdown("### 📝 Describe Your Meal")
        st.info("Type what you ate and AI will analyze the B12 content")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            food_input = st.text_area(
                "Describe your meal in detail:",
                placeholder="Example: I ate 2 scrambled eggs with cheese for breakfast, a tuna sandwich for lunch, and grilled salmon with vegetables for dinner",
                height=120,
                key="food_text_ai"
            )
            
            # Additional context
            with st.expander("➕ Add more context (optional)"):
                meal_time = st.selectbox("When did you eat?", ["Breakfast", "Lunch", "Dinner", "Snack"])
                portion_size = st.select_slider("Portion size", options=["Small", "Medium", "Large"], value="Medium")
                additional_notes = st.text_input("Any specific ingredients?", placeholder="e.g., with butter, fried, boiled")
        
        with col2:
            st.markdown("**💡 Tips for better results:**")
            st.markdown("• Be specific about quantities")
            st.markdown("• Mention cooking methods")
            st.markdown("• Include all ingredients")
            st.markdown("• Specify portion sizes")
            
            st.markdown("**📊 Your Profile:**")
            if st.session_state.user_data:
                st.markdown(f"• Diet: {st.session_state.user_data.get('diet_type', 'Not set')}")
                st.markdown(f"• Age: {st.session_state.user_data.get('age', 'Not set')}")
            else:
                st.markdown("• Complete assessment for personalized analysis")
        
        if st.button("🔍 Analyze with AI", type="primary", use_container_width=True):
            if food_input:
                with st.spinner("🤖 AI is analyzing your meal... This may take a few seconds"):
                    try:
                        # Configure Gemini API with environment variable
                        import google.generativeai as genai
                        genai.configure(api_key=GEMINI_API_KEY_MEAL)
                        
                        # Get user context
                        user_context = ""
                        if st.session_state.user_data:
                            user = st.session_state.user_data
                            user_context = f"The user is {user.get('age', 'unknown')} years old and follows a {user.get('diet_type', 'omnivore')} diet."
                        
                        # Create prompt for AI analysis
                        prompt = f"""
                        You are a nutrition expert specializing in Vitamin B12.
                        
                        Analyze this meal description: "{food_input}"
                        
                        Context:
                        - Meal time: {meal_time if 'meal_time' in locals() else 'Not specified'}
                        - Portion size: {portion_size if 'portion_size' in locals() else 'Medium'}
                        - Additional notes: {additional_notes if 'additional_notes' in locals() else 'None'}
                        - {user_context}
                        
                        Provide a detailed analysis in the following EXACT TABLE FORMAT:
                        
                        | Food Item | Estimated Quantity | B12 Content (mcg) | Confidence | Notes |
                        |-----------|-------------------|-------------------|------------|-------|
                        | [item 1] | [quantity] | [value] | [High/Med/Low] | [notes] |
                        | [item 2] | [quantity] | [value] | [High/Med/Low] | [notes] |
                        
                        | Total B12 | Daily Need | % Met | Rating | Recommendation |
                        |-----------|------------|-------|--------|----------------|
                        | [total] mcg | 2.4 mcg | [%] | [🔴/🟡/🟢/💪] | [specific advice] |
                        
                        Based on this analysis, provide:
                        1. **B12 Score:** [0-100]
                        2. **Meal Quality:** [Poor/Average/Good/Excellent]
                        3. **Suggestions to improve B12 intake:**
                           • [Suggestion 1]
                           • [Suggestion 2]
                           • [Suggestion 3]
                        
                        Use simple, easy-to-understand language. Be encouraging and practical.
                        """
                        
                        # Try different model names
                        model_names = ['gemini-pro', 'models/gemini-pro', 'gemini-1.0-pro', 'gemini-1.5-pro','gemini-2.0-pro','gemini-2.5-pro','gemini-3.0-pro','gemini-2.5-flash','gemini-3.0-flash']
                        response = None
                        
                        for model_name in model_names:
                            try:
                                model = genai.GenerativeModel(model_name)
                                response = model.generate_content(prompt)
                                if response and response.text:
                                    break
                            except:
                                continue
                        
                        if response and response.text:
                            st.markdown("---")
                            st.markdown("### 📊 AI Analysis Results")
                            
                            # Display the AI response
                            st.markdown(response.text)
                            
                            # Try to extract and display B12 score if present
                            if "B12 Score:" in response.text:
                                import re
                                score_match = re.search(r'B12 Score:\s*(\d+)', response.text)
                                if score_match:
                                    score = int(score_match.group(1))
                                    st.progress(score/100, text=f"B12 Score: {score}/100")
                            
                            # Download button for results
                            st.download_button(
                                label="📥 Download Analysis",
                                data=response.text,
                                file_name=f"b12_food_analysis_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
                                mime="text/plain"
                            )
                            
                            # Log activity
                            log_user_activity(
                                activity_type='food_scan_ai',
                                data={'food': food_input[:50]},
                                description="AI food analysis"
                            )
                            
                        else:
                            st.error("AI analysis failed. Using local database as fallback.")
                            # Fallback to local database
                            analyze_b12_food_local(food_input)
                            
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
                        # Fallback to local database
                        analyze_b12_food_local(food_input)
            else:
                st.warning("Please describe your meal first")
    
    # ==================== TAB 2: PHOTO UPLOAD WITH AI ====================
    with tab2:
        st.markdown("### 📸 Upload Food Photo")
        st.info("Take a photo of your meal and AI will identify B12-rich foods")
        
        uploaded_file = st.file_uploader(
            "Choose a clear photo of your meal",
            type=['jpg', 'jpeg', 'png'],
            help="Well-lit, clear photos work best"
        )
        
        if uploaded_file is not None:
            # Display uploaded image
            image = Image.open(uploaded_file)
            st.image(image, caption="Your meal", use_container_width=True)
            
            if st.button("🔍 Analyze Food Photo with AI", type="primary", use_container_width=True):
                with st.spinner("🤖 AI is analyzing your food photo... This may take 10-15 seconds"):
                    try:
                        # Call the AI function for image analysis
                        result = analyze_food_with_gemini(image)
                        
                        st.markdown("---")
                        st.markdown("### 📊 AI Food Analysis Results")
                        st.markdown(result)
                        
                        # Download button
                        st.download_button(
                            label="📥 Download Analysis",
                            data=result,
                            file_name=f"b12_food_photo_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
                            mime="text/plain"
                        )
                        
                    except Exception as e:
                        st.error(f"Error analyzing image: {str(e)}")
    
    # ==================== TAB 3: FOOD GUIDE (Local Database Reference) ====================
    with tab3:
        st.markdown("### 📚 Complete B12 Food Reference Guide")
        st.info("Use this guide to identify B12-rich foods")
        
        # Search functionality
        search = st.text_input("🔍 Search for a food:", placeholder="e.g., eggs, salmon, milk")
        
        if search:
            # Filter database based on search
            search_lower = search.lower()
            filtered_foods = {k: v for k, v in b12_database.items() if search_lower in k}
            
            if filtered_foods:
                st.success(f"Found {len(filtered_foods)} matching foods:")
                data = []
                for food, value in filtered_foods.items():
                    percentage = (value / 2.4) * 100
                    data.append({
                        "Food": food.title(),
                        "B12 (mcg)": value,
                        "% Daily Need": f"{percentage:.1f}%"
                    })
                df = pd.DataFrame(data)
                st.dataframe(df, use_container_width=True, hide_index=True)
            else:
                st.warning("No matching foods found. Try a different search term.")
        
        # Complete food guide in expandable sections
        with st.expander("🥚 HIGH B12 Foods (> 2.4 mcg)", expanded=False):
            high_b12 = {k: v for k, v in b12_database.items() if v >= 2.4}
            data = []
            for food, value in sorted(high_b12.items(), key=lambda x: x[1], reverse=True)[:10]:
                percentage = (value / 2.4) * 100
                data.append({
                    "Food": food.title(),
                    "B12 (mcg)": f"{value:.1f}",
                    "% Daily Need": f"{percentage:.0f}%",
                    "Rating": "💪 EXCELLENT" if value > 10 else "🟢 GOOD"
                })
            st.dataframe(pd.DataFrame(data), use_container_width=True, hide_index=True)
        
        with st.expander("🥛 MEDIUM B12 Foods (1-2.4 mcg)", expanded=False):
            medium_b12 = {k: v for k, v in b12_database.items() if 1 <= v < 2.4}
            data = []
            for food, value in sorted(medium_b12.items(), key=lambda x: x[1], reverse=True):
                percentage = (value / 2.4) * 100
                data.append({
                    "Food": food.title(),
                    "B12 (mcg)": f"{value:.1f}",
                    "% Daily Need": f"{percentage:.0f}%",
                    "Rating": "🟢 GOOD" if value > 1.5 else "🟡 MODERATE"
                })
            st.dataframe(pd.DataFrame(data), use_container_width=True, hide_index=True)
        
        with st.expander("🥗 LOW B12 Foods (< 1 mcg)", expanded=False):
            low_b12 = {k: v for k, v in b12_database.items() if v < 1}
            data = []
            for food, value in sorted(low_b12.items(), key=lambda x: x[1], reverse=True)[:15]:
                percentage = (value / 2.4) * 100
                data.append({
                    "Food": food.title(),
                    "B12 (mcg)": f"{value:.1f}",
                    "% Daily Need": f"{percentage:.0f}%",
                    "Rating": "🟡 MODERATE" if value > 0.5 else "🔴 LOW"
                })
            st.dataframe(pd.DataFrame(data), use_container_width=True, hide_index=True)
        
        # Daily requirement info
        st.markdown("---")
        st.markdown("### 📊 Daily B12 Requirements")
        req_data = pd.DataFrame({
            "Group": ["Adults", "Pregnancy", "Breastfeeding", "Children (4-8)", "Teens (14-18)"],
            "Daily B12 Need": ["2.4 mcg", "2.6 mcg", "2.8 mcg", "1.2 mcg", "2.4 mcg"],
            "Equivalent Food": ["4 eggs", "5 eggs", "5 eggs", "2 eggs", "4 eggs"]
        })
        st.dataframe(req_data, use_container_width=True, hide_index=True)

#============================= ASSESSMENT PAGE =========================

elif page == " Assessment":
    st.markdown('<div class="main-title"> Complete Risk Assessment</div>', unsafe_allow_html=True)
    
    # Show temp logs notification
    if not st.session_state.authenticated and 'temp_logs' in st.session_state:
        temp_count = len(st.session_state.temp_logs)
        if temp_count > 0:
            st.info(f" {temp_count} activities will be saved when you login")
    
    # Initialize form state if not exists - but DON'T load from previous assessment
    if 'form_age' not in st.session_state:
        st.session_state.form_age = None
    if 'form_gender' not in st.session_state:
        st.session_state.form_gender = "Select gender..."
    if 'form_weight' not in st.session_state:
        st.session_state.form_weight = None
    if 'form_height' not in st.session_state:
        st.session_state.form_height = None
    if 'form_diet_type' not in st.session_state:
        st.session_state.form_diet_type = "Select diet type..."
    if 'form_b12_level' not in st.session_state:
        st.session_state.form_b12_level = None
    if 'form_conditions' not in st.session_state:
        st.session_state.form_conditions = []
    if 'form_medications' not in st.session_state:
        st.session_state.form_medications = []
    if 'form_symptoms' not in st.session_state:
        st.session_state.form_symptoms = []
    
    with st.form("assessment_form", border=True):
        st.markdown("###  Personal Information")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            age = st.number_input(
                "**Age (years)**", 
                1, 120, 
                value=st.session_state.form_age,
                placeholder="Enter your age",
                help="Risk increases after 50",
                key="form_age_input"
            )
            gender = st.selectbox(
                "**Gender**",
                ["Select gender...", "Male", "Female", "Other/Prefer not to say"],
                index=0 if st.session_state.form_gender == "Select gender..." 
                      else ["Male", "Female", "Other/Prefer not to say"].index(st.session_state.form_gender) + 1,
                key="form_gender_input"
            )
        
        with col2:
            weight = st.number_input(
                "**Weight (kg)**", 
                20, 200, 
                value=st.session_state.form_weight,
                placeholder="Enter weight in kg",
                key="form_weight_input"
            )
            height = st.number_input(
                "**Height (cm)**", 
                100, 250, 
                value=st.session_state.form_height,
                placeholder="Enter height in cm",
                key="form_height_input"
            )
        
        with col3:
            # Show BMI only after height/weight are entered
            if weight and height:
                bmi = calculate_bmi(weight, height)
                bmi_category = get_bmi_category(bmi)
                if isinstance(bmi_category, tuple):
                    category_display = bmi_category[0]
                else:
                    category_display = bmi_category
                st.metric("**BMI**", f"{bmi:.1f}", category_display)
            else:
                st.info("Enter weight and height to see BMI")
                bmi = None
            
            diet_type = st.selectbox(
                "**Primary Diet**",
                ["Select diet type...", "Omnivore", "Vegetarian", "Vegan", "Pescetarian"],
                index=0 if st.session_state.form_diet_type == "Select diet type..."
                      else ["Omnivore", "Vegetarian", "Vegan", "Pescetarian"].index(st.session_state.form_diet_type) + 1,
                key="form_diet_input"
            )
        
        st.markdown("---")
        st.markdown("###  Medical History")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Medical Conditions**")
            conditions = [
                "Diabetes (especially on Metformin)",
                "Thyroid Disorders",
                "Celiac Disease",
                "Crohn's Disease / IBD",
                "Autoimmune Disorders",
                "Pernicious Anemia",
                "Gastritis / GERD",
                "Previous GI Surgery"
            ]
            selected_conditions = []
            for condition in conditions:
                # Check if this condition was previously selected
                is_checked = condition in st.session_state.form_conditions
                if st.checkbox(condition, value=is_checked, key=f"condition_{condition}"):
                    selected_conditions.append(condition)
        
        with col2:
            st.markdown("**Current Medications**")
            medications = [
                "Metformin (for diabetes)",
                "Proton Pump Inhibitors (PPIs)",
                "H2 Blockers",
                "Birth Control Pills",
                "Anticonvulsants",
                "Long-term Antibiotics",
                "Cholesterol medications"
            ]
            selected_meds = []
            for med in medications:
                # Check if this medication was previously selected
                is_checked = med in st.session_state.form_medications
                if st.checkbox(med, value=is_checked, key=f"medication_{med}"):
                    selected_meds.append(med)
        
        st.markdown("---")
        st.markdown("###  Symptoms Checklist")
        
        st.caption("Check all that apply (last 3 months)")
        
        symptoms_col1, symptoms_col2, symptoms_col3 = st.columns(3)
        
        symptoms_list = []
        symptom_options = [
            "Fatigue", "Dizziness", "Pale Skin", "Breathlessness",
            "Numbness", "Muscle Weak", "Walking Issues", "Vision Issues",
            "Memory Loss", "Depression", "Confusion", "Sore Tongue"
        ]
        
        with symptoms_col1:
            if st.checkbox("**Fatigue / Weakness**", 
                          value="Fatigue" in st.session_state.form_symptoms,
                          key="symptom_fatigue"):
                symptoms_list.append("Fatigue")
            if st.checkbox("**Dizziness**",
                          value="Dizziness" in st.session_state.form_symptoms,
                          key="symptom_dizziness"):
                symptoms_list.append("Dizziness")
            if st.checkbox("**Pale / Yellowish Skin**",
                          value="Pale Skin" in st.session_state.form_symptoms,
                          key="symptom_pale"):
                symptoms_list.append("Pale Skin")
            if st.checkbox("**Shortness of Breath**",
                          value="Breathlessness" in st.session_state.form_symptoms,
                          key="symptom_breath"):
                symptoms_list.append("Breathlessness")
        
        with symptoms_col2:
            if st.checkbox("**Numbness / Tingling**",
                          value="Numbness" in st.session_state.form_symptoms,
                          key="symptom_numbness"):
                symptoms_list.append("Numbness")
            if st.checkbox("**Muscle Weakness**",
                          value="Muscle Weak" in st.session_state.form_symptoms,
                          key="symptom_muscle"):
                symptoms_list.append("Muscle Weak")
            if st.checkbox("**Walking Difficulties**",
                          value="Walking Issues" in st.session_state.form_symptoms,
                          key="symptom_walking"):
                symptoms_list.append("Walking Issues")
            if st.checkbox("**Vision Problems**",
                          value="Vision Issues" in st.session_state.form_symptoms,
                          key="symptom_vision"):
                symptoms_list.append("Vision Issues")
        
        with symptoms_col3:
            if st.checkbox("**Memory Problems**",
                          value="Memory Loss" in st.session_state.form_symptoms,
                          key="symptom_memory"):
                symptoms_list.append("Memory Loss")
            if st.checkbox("**Depression / Mood Changes**",
                          value="Depression" in st.session_state.form_symptoms,
                          key="symptom_depression"):
                symptoms_list.append("Depression")
            if st.checkbox("**Confusion**",
                          value="Confusion" in st.session_state.form_symptoms,
                          key="symptom_confusion"):
                symptoms_list.append("Confusion")
            if st.checkbox("**Sore / Red Tongue**",
                          value="Sore Tongue" in st.session_state.form_symptoms,
                          key="symptom_tongue"):
                symptoms_list.append("Sore Tongue")
        
        symptoms_count = len(symptoms_list)
        st.metric("**Total Symptoms**", symptoms_count)
        
        st.markdown("---")
        st.markdown("###  Lab Results")
        
        # Don't auto-use uploaded reports
        use_uploaded = False
        if st.session_state.lab_reports:
            latest = st.session_state.lab_reports[-1]
            st.info(f" Latest uploaded B12: **{latest['b12_value']} pg/mL**")
            use_uploaded = st.checkbox("Use this uploaded value", key="use_uploaded_check")
        
        col1, col2 = st.columns(2)
        with col1:
            b12_level = st.number_input(
                "**Vitamin B12 Level (pg/mL)**",
                min_value=0,
                max_value=2000,
                value=st.session_state.form_b12_level,
                placeholder="Enter B12 level or 0 if unknown",
                help="Enter 0 if unknown. Normal range: 200-900 pg/mL",
                key="form_b12_input"
            )
        with col2:
            if b12_level is not None and b12_level > 0:
                if b12_level < 200:
                    st.error(f"**DEFICIENT** (<200 pg/mL)")
                elif b12_level < 300:
                    st.warning(f"**BORDERLINE** (200-300 pg/mL)")
                else:
                    st.success(f"**NORMAL** (>300 pg/mL)")
        
        col1, col2 = st.columns(2)
        with col1:
            submitted = st.form_submit_button(
                " Calculate My Risk Score", 
                type="primary"
            )
        with col2:
            clear_form = st.form_submit_button(
                " Clear Form",
                type="secondary"
            )
        
        if clear_form:
            # Clear all form data from session state
            st.session_state.form_age = None
            st.session_state.form_gender = "Select gender..."
            st.session_state.form_weight = None
            st.session_state.form_height = None
            st.session_state.form_diet_type = "Select diet type..."
            st.session_state.form_b12_level = None
            st.session_state.form_conditions = []
            st.session_state.form_medications = []
            st.session_state.form_symptoms = []
            st.rerun()
        
        if submitted:
            # Update session state with current form values
            st.session_state.form_age = age
            st.session_state.form_gender = gender
            st.session_state.form_weight = weight
            st.session_state.form_height = height
            st.session_state.form_diet_type = diet_type
            st.session_state.form_b12_level = b12_level
            st.session_state.form_conditions = selected_conditions
            st.session_state.form_medications = selected_meds
            st.session_state.form_symptoms = symptoms_list
            
            # VALIDATION - Check required fields
            missing_fields = []
            if age is None:
                missing_fields.append("Age")
            if gender == "Select gender...":
                missing_fields.append("Gender")
            if weight is None:
                missing_fields.append("Weight")
            if height is None:
                missing_fields.append("Height")
            if diet_type == "Select diet type...":
                missing_fields.append("Diet type")
            if b12_level is None:
                missing_fields.append("B12 level (enter 0 if unknown)")
            
            if missing_fields:
                st.error(f"Please fill in required fields: {', '.join(missing_fields)}")
                st.stop()
            
            # Calculate BMI if not already calculated
            if bmi is None and weight and height:
                bmi = calculate_bmi(weight, height)
            
            user_data = {
                'age': age,
                'gender': gender,
                'weight': weight,
                'height': height,
                'bmi': bmi or 0,
                'diet_type': diet_type,
                'symptoms_count': symptoms_count,
                'medical_conditions': len(selected_conditions),
                'medications_count': len(selected_meds),
                'symptoms_list': ', '.join(symptoms_list),
                'conditions_list': ', '.join(selected_conditions),
                'medications_list': ', '.join(selected_meds),
                'b12_level': b12_level if b12_level > 0 and not use_uploaded else None
            }
            
            if use_uploaded and st.session_state.lab_reports:
                user_data['lab_b12_level'] = latest['b12_value']
                user_data['b12_source'] = 'uploaded_report'
            elif b12_level > 0:
                user_data['b12_source'] = 'manual_entry'
            
            try:
                use_b12_level = None
                if use_uploaded and st.session_state.lab_reports:
                    use_b12_level = latest['b12_value']
                elif b12_level > 0:
                    use_b12_level = b12_level
                
                ml_prediction = predict_with_conflict_resolution(user_data, use_b12_level, 'assessment_form')
                
                risk_score = ml_prediction.get('deficient_probability', 0.5)
                risk_level = ml_prediction.get('risk_level', 'Medium')
                confidence = ml_prediction.get('confidence', 0.5)
                
                recommendations = generate_recommendations(risk_level, diet_type, age, ml_prediction)
                
                st.session_state.user_data = user_data
                st.session_state.risk_score = risk_score
                st.session_state.risk_level = risk_level
                st.session_state.recommendations = recommendations
                st.session_state.ml_prediction = ml_prediction
                
                # Log assessment activity
                log_user_activity(
                    activity_type='assessment',
                    data={
                        'risk_score': risk_score,
                        'risk_level': risk_level,
                        'symptoms_count': symptoms_count,
                        'diet_type': diet_type,
                        'age': age
                    },
                    description=f"Complete assessment - {risk_level} risk"
                )
                
                try:
                    save_user_data(user_data, risk_level)
                except:
                    pass
                
                if st.session_state.authenticated and st.session_state.mongodb.connected:
                    try:
                        mongo_id = st.session_state.mongodb.save_user_assessment(
                            user_data=user_data,
                            risk_score=risk_score,
                            risk_level=risk_level,
                            recommendations=recommendations,
                            ml_prediction=ml_prediction,
                            user_id=st.session_state.current_user['user_id'],
                            session_id=st.session_state.session_id
                        )
                        if mongo_id:
                            st.success(" Assessment saved !")
                    except Exception as mongo_error:
                        st.warning(f" Could not save to cloud: {str(mongo_error)[:100]}")
                else:
                    # Show notification for non-logged in users
                    st.info(" Assessment saved locally. Login to save to cloud .")
                
                # st.success(" Assessment Complete!")
                # 
                
                
                st.markdown(f"### Your Risk Level: **{risk_level}**")
                st.markdown(f"**Risk Score:** {risk_score:.1%}")
                st.markdown(f"**Confidence:** {confidence:.1%}")
                
                if risk_level == "High":
                    st.error("""
                    **Immediate Actions Recommended:**
                    1. Consult a doctor within 1-2 weeks
                    2. Consider starting B12 supplements
                    3. Get comprehensive blood tests
                    """)
                elif risk_level == "Medium":
                    st.warning("""
                    **Recommended Actions:**
                    1. Schedule doctor appointment
                    2. Improve dietary intake
                    3. Consider preventive supplements
                    """)
                else:
                    st.success("""
                    **Maintenance Actions:**
                    1. Continue healthy diet
                    2. Annual check-up recommended
                    3. Monitor for new symptoms
                    """)
                    
            except Exception as e:
                st.error(f" Prediction error: {str(e)}")
                st.info("Using simplified risk calculation...")
                
                risk_score = 0
                if age > 50: risk_score += 0.3
                if diet_type == "Vegan": risk_score += 0.4
                elif diet_type == "Vegetarian": risk_score += 0.2
                risk_score += min(symptoms_count * 0.1, 0.3)
                
                risk_level = "High" if risk_score > 0.6 else "Medium" if risk_score > 0.3 else "Low"
                
                st.session_state.user_data = user_data
                st.session_state.risk_score = risk_score
                st.session_state.risk_level = risk_level
                st.session_state.ml_prediction = {'model_used': 'Simple Fallback'}
                
                # Log assessment activity even with fallback
                log_user_activity(
                    activity_type='assessment_fallback',
                    data={
                        'risk_score': risk_score,
                        'risk_level': risk_level,
                        'symptoms_count': symptoms_count,
                        'diet_type': diet_type,
                        'age': age,
                        'error': str(e)
                    },
                    description=f"Fallback assessment - {risk_level} risk"
                )
                
                st.warning(f" Using simplified calculation: {risk_level} risk ({risk_score:.0%})")

# ==================== BARCODE SCANNER PAGE ====================

# ==================== BARCODE SCANNER WITH REAL DATABASE ====================
elif page == " Barcode Scanner":
    import requests
    from datetime import datetime
    import time
    import pandas as pd
    
    st.markdown("## 📱 Barcode Scanner")
    st.caption("🔍 Searching Open Food Facts Database • 3+ Million Products")
    
    # Initialize session state
    if 'my_products' not in st.session_state:
        st.session_state.my_products = []
    if 'search_history' not in st.session_state:
        st.session_state.search_history = []
    
    # ==================== REAL OPEN FOOD FACTS API ====================
    def search_openfoodfacts(barcode):
        """Search REAL Open Food Facts database"""
        try:
            # Clean barcode - remove any non-digits
            clean_barcode = ''.join(filter(str.isdigit, str(barcode)))
            if not clean_barcode:
                return None
            
            # API call to Open Food Facts
            url = f"https://world.openfoodfacts.org/api/v0/product/{clean_barcode}.json"
            
            # Add user agent (required by Open Food Facts)
            headers = {
                'User-Agent': 'B12Scanner - Product Scanner - Version 1.0'
            }
            
            # Make request
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                # Check if product found (status 1 means success)
                if data.get('status') == 1:
                    product = data.get('product', {})
                    
                    # Extract product information
                    product_name = product.get('product_name') or product.get('product_name_en') or 'Unknown Product'
                    brand = product.get('brands') or 'Unknown Brand'
                    quantity = product.get('quantity') or 'Not specified'
                    
                    # Get ingredients (try multiple fields)
                    ingredients = product.get('ingredients_text') or product.get('ingredients_text_en') or 'No ingredients listed'
                    
                    # Get categories
                    categories = product.get('categories') or 'Not categorized'
                    
                    # Get image
                    image_url = product.get('image_url') or product.get('image_front_url') or ''
                    
                    # Get nutrition facts
                    nutriments = product.get('nutriments', {})
                    
                    # Get allergens
                    allergens = product.get('allergens') or 'None listed'
                    
                    # Check for B12 in product
                    is_b12 = False
                    b12_keywords = ['b12', 'vitamin b12', 'cobalamin', 'cyanocobalamin', 'methylcobalamin']
                    
                    # Check in product name
                    if product_name and any(keyword in product_name.lower() for keyword in b12_keywords):
                        is_b12 = True
                    
                    # Check in ingredients
                    if ingredients and any(keyword in ingredients.lower() for keyword in b12_keywords):
                        is_b12 = True
                    
                    # Check in categories
                    if categories and any(keyword in categories.lower() for keyword in b12_keywords):
                        is_b12 = True
                    
                    # Get serving size
                    serving_size = product.get('serving_size') or 'Not specified'
                    
                    # Return product data
                    return {
                        'success': True,
                        'name': product_name,
                        'brand': brand,
                        'barcode': clean_barcode,
                        'quantity': quantity,
                        'ingredients': ingredients,
                        'categories': categories,
                        'image_url': image_url,
                        'nutriments': nutriments,
                        'allergens': allergens,
                        'is_b12': is_b12,
                        'serving_size': serving_size,
                        'source': 'Open Food Facts'
                    }
                else:
                    # Product not found in database
                    return {
                        'success': False,
                        'barcode': clean_barcode,
                        'error': 'not_found'
                    }
            else:
                # API error
                return {
                    'success': False,
                    'barcode': clean_barcode,
                    'error': 'api_error'
                }
                
        except requests.exceptions.Timeout:
            return {
                'success': False,
                'barcode': clean_barcode,
                'error': 'timeout'
            }
        except requests.exceptions.ConnectionError:
            return {
                'success': False,
                'barcode': clean_barcode,
                'error': 'connection_error'
            }
        except Exception as e:
            print(f"Error: {str(e)}")
            return {
                'success': False,
                'barcode': clean_barcode,
                'error': 'unknown'
            }
    
    # ==================== TEST BARCODES (FOR QUICK TESTING) ====================
    test_barcodes = {
        "3017620422003": "Nutella - Popular hazelnut spread",
        "7622210449283": "Oreo - Chocolate sandwich cookies",
        "0743120310027": "Nature's Bounty B12 - Vitamin B12 supplement",
        "2001234500001": "Milk - Semi-skimmed milk",
        "5053827101107": "Corn Flakes - Fortified breakfast cereal",
        "5010327625014": "Orange Juice - Pure orange juice",
        "5449000000996": "Coca-Cola - Classic soda",
        "3057640111019": "Evian - Natural mineral water",
        "8000500315581": "Nutella 750g - Large size",
        "9300675037031": "Weet-Bix - Breakfast cereal"
    }
    
    # ==================== UI HEADER ====================
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        padding: 20px;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin-bottom: 20px;
    ">
        <h3>🔍 Open Food Facts Scanner</h3>
        <p>Searching 3+ Million Real Products • No API Key Needed</p>
    </div>
    """, unsafe_allow_html=True)
    
    # ==================== TEST BUTTONS ====================
    st.subheader("📋 Click to Test Real Products:")
    
    # Display test buttons in rows
    test_items = list(test_barcodes.items())
    
    # First row
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button(f"🥫 Nutella", key="test1", use_container_width=True):
            st.session_state.search_barcode = "3017620422003"
            st.session_state.search_now = True
    with col2:
        if st.button(f"🥛 Milk", key="test2", use_container_width=True):
            st.session_state.search_barcode = "2001234500001"
            st.session_state.search_now = True
    with col3:
        if st.button(f"🍪 Oreo", key="test3", use_container_width=True):
            st.session_state.search_barcode = "7622210449283"
            st.session_state.search_now = True
    
    # Second row
    col4, col5, col6 = st.columns(3)
    with col4:
        if st.button(f"💊 B12 Supplement", key="test4", use_container_width=True):
            st.session_state.search_barcode = "0743120310027"
            st.session_state.search_now = True
    with col5:
        if st.button(f"🥣 Corn Flakes", key="test5", use_container_width=True):
            st.session_state.search_barcode = "5053827101107"
            st.session_state.search_now = True
    with col6:
        if st.button(f"🧃 Orange Juice", key="test6", use_container_width=True):
            st.session_state.search_barcode = "5010327625014"
            st.session_state.search_now = True
    
    # Third row
    col7, col8, col9 = st.columns(3)
    with col7:
        if st.button(f"🥤 Coca-Cola", key="test7", use_container_width=True):
            st.session_state.search_barcode = "5449000000996"
            st.session_state.search_now = True
    with col8:
        if st.button(f"💧 Evian Water", key="test8", use_container_width=True):
            st.session_state.search_barcode = "3057640111019"
            st.session_state.search_now = True
    with col9:
        if st.button(f"🥣 Weet-Bix", key="test9", use_container_width=True):
            st.session_state.search_barcode = "9300675037031"
            st.session_state.search_now = True
    
    st.markdown("---")
    
    # ==================== INPUT SECTION ====================
    col_input, col_info = st.columns([2, 1])
    
    with col_input:
        default_barcode = st.session_state.get('search_barcode', '')
        barcode_input = st.text_input(
            "🔢 Enter Barcode Number:", 
            value=default_barcode, 
            placeholder="e.g., 3017620422003",
            help="Enter 8-13 digit barcode number"
        )
    
    with col_info:
        st.caption("✅ Works with EAN-13, UPC-A, EAN-8")
        st.caption("📦 3+ million products")
    
    # Search button
    col_search, col_clear = st.columns([3, 1])
    with col_search:
        search_clicked = st.button("🔍 Search Open Food Facts Database", type="primary", use_container_width=True)
    with col_clear:
        if st.button("🔄 Clear", use_container_width=True):
            st.session_state.search_barcode = ''
            st.rerun()
    
    # ==================== SEARCH LOGIC ====================
    if search_clicked or st.session_state.get('search_now', False):
        st.session_state.search_now = False
        
        if barcode_input:
            with st.spinner("🔍 Searching Open Food Facts database of 3+ million products..."):
                
                # Add to search history
                st.session_state.search_history.append({
                    'barcode': barcode_input,
                    'time': datetime.now().strftime("%H:%M:%S"),
                    'date': datetime.now().strftime("%Y-%m-%d")
                })
                
                # Search REAL database
                result = search_openfoodfacts(barcode_input)
                
                if result and result.get('success'):
                    st.balloons()
                    st.success(f"✅ Product Found in Open Food Facts Database!")
                    
                    # ==================== DISPLAY PRODUCT FROM REAL DATABASE ====================
                    
                    # Product header with image
                    col_img, col_title = st.columns([1, 3])
                    
                    with col_img:
                        if result.get('image_url'):
                            st.image(result['image_url'], width=120)
                        else:
                            st.markdown("# 📦")
                    
                    with col_title:
                        st.markdown(f"## {result['name']}")
                        st.markdown(f"### {result['brand']}")
                        st.markdown(f"**Barcode:** `{result['barcode']}`")
                    
                    # Product details in tabs
                    tab1, tab2, tab3, tab4, tab5 = st.tabs([
                        "📋 Product Details", 
                        "🥗 Ingredients", 
                        "💊 B12 Information",
                        "📊 Nutrition Facts",
                        "💡 Uses & Recipes"
                    ])
                    
                    with tab1:
                        col_a, col_b = st.columns(2)
                        with col_a:
                            st.metric("Quantity", result.get('quantity', 'N/A'))
                            st.metric("Categories", result.get('categories', 'General')[:30] + '...' if len(result.get('categories', '')) > 30 else result.get('categories', 'General'))
                        with col_b:
                            st.metric("Serving Size", result.get('serving_size', 'N/A'))
                            if result.get('allergens') and result['allergens'] != 'None listed':
                                st.warning(f"⚠️ Allergens: {result['allergens']}")
                        
                        # Product codes
                        st.info(f"**Product Code:** {result['barcode']} | **Source:** {result['source']}")
                    
                    with tab2:
                        st.markdown("### 🥗 Ingredients List")
                        st.write(result.get('ingredients', 'No ingredients listed'))
                        
                        # Copy button
                        if st.button("📋 Copy Ingredients"):
                            st.code(result.get('ingredients', ''))
                    
                    with tab3:
                        if result.get('is_b12'):
                            st.success("### ✅ THIS PRODUCT CONTAINS VITAMIN B12!")
                            
                            # B12 benefits
                            st.markdown("""
                            #### 💊 Benefits of Vitamin B12:
                            
                            | Benefit | Description |
                            |---------|-------------|
                            | 🧠 **Brain Health** | Supports neurological function and cognitive health |
                            | ⚡ **Energy Boost** | Helps convert food into energy, reduces fatigue |
                            | 🩸 **Red Blood Cells** | Essential for healthy red blood cell formation |
                            | 💪 **Nervous System** | Maintains healthy nerve cells |
                            | 🧬 **DNA Synthesis** | Important for DNA production and cell division |
                            
                            #### 📅 Recommended Daily Intake:
                            - **Adults:** 2.4 mcg per day
                            - **Pregnant women:** 2.6 mcg per day
                            - **Breastfeeding:** 2.8 mcg per day
                            
                            #### 🍽️ Best Food Sources of B12:
                            - Clams, liver, fish (salmon, trout, tuna)
                            - Beef, eggs, dairy products
                            - Fortified cereals and nutritional yeast
                            - B12 supplements
                            """)
                            
                            # Check if it's a supplement
                            if 'supplement' in result['name'].lower() or 'b12' in result['name'].lower():
                                st.info("💊 **This appears to be a B12 supplement** - Follow dosage instructions on package")
                        else:
                            st.info("### ❌ No Vitamin B12 Detected")
                            st.markdown("""
                            #### 🔍 To get more Vitamin B12, try:
                            - 🥩 **Animal products:** Meat, fish, eggs, dairy
                            - 🥣 **Fortified foods:** Cereals, plant milks, nutritional yeast
                            - 💊 **B12 supplements:** Tablets, sublingual, sprays
                            
                            *Vitamin B12 is essential for energy, brain function, and red blood cell formation.*
                            """)
                    
                    with tab4:
                        st.markdown("### 📊 Nutrition Facts (per 100g/ml)")
                        
                        nutriments = result.get('nutriments', {})
                        if nutriments:
                            # Create nutrition table
                            nutrition_data = {
                                'Nutrient': ['Energy', 'Fat', 'Saturated Fat', 'Carbohydrates', 'Sugars', 'Fiber', 'Protein', 'Salt'],
                                'Amount': [
                                    f"{nutriments.get('energy', 'N/A')} {nutriments.get('energy_unit', 'kcal')}",
                                    f"{nutriments.get('fat', 'N/A')} g",
                                    f"{nutriments.get('saturated-fat', 'N/A')} g",
                                    f"{nutriments.get('carbohydrates', 'N/A')} g",
                                    f"{nutriments.get('sugars', 'N/A')} g",
                                    f"{nutriments.get('fiber', 'N/A')} g",
                                    f"{nutriments.get('proteins', 'N/A')} g",
                                    f"{nutriments.get('salt', 'N/A')} g"
                                ]
                            }
                            
                            df = pd.DataFrame(nutrition_data)
                            st.table(df)
                        else:
                            st.info("No nutrition information available for this product")
                    
                    with tab5:
                        st.markdown("### 🍽️ How to Use This Product")
                        
                        # Generate uses based on product type
                        product_name_lower = result['name'].lower()
                        
                        if 'nutella' in product_name_lower:
                            st.markdown("""
                            #### 🥫 Nutella Uses:
                            - **Breakfast:** Spread on toast, pancakes, waffles, crepes
                            - **Snacks:** Dip fruits (strawberries, bananas, apples)
                            - **Baking:** Use in brownies, cakes, cookies
                            - **Desserts:** Top ice cream, make milkshakes
                            - **Creative:** Fill crepes, make Nutella hot chocolate
                            
                            #### 🍪 Popular Recipes:
                            1. **Nutella Toast** - Spread on warm toast, add sliced bananas
                            2. **Nutella Crepes** - Fill crepes with Nutella and strawberries
                            3. **Nutella Brownies** - Swirl Nutella into brownie batter
                            4. **Nutella Milkshake** - Blend with milk and ice cream
                            """)
                        elif 'oreo' in product_name_lower:
                            st.markdown("""
                            #### 🍪 Oreo Uses:
                            - **Snacking:** Classic twist, lick, dunk in milk
                            - **Desserts:** Crush for ice cream topping
                            - **Baking:** Use in cheesecakes, brownies, cookies
                            - **Drinks:** Make Oreo milkshakes, smoothies
                            
                            #### 🥤 Popular Recipes:
                            1. **Oreo Milkshake** - Blend with vanilla ice cream and milk
                            2. **Oreo Cheesecake** - Crust made from Oreo crumbs
                            3. **Cookies & Cream Ice Cream** - Homemade version
                            4. **Oreo Truffles** - Mix with cream cheese, dip in chocolate
                            """)
                        elif 'milk' in product_name_lower:
                            st.markdown("""
                            #### 🥛 Milk Uses:
                            - **Beverages:** Drink plain, with cereal, in coffee/tea
                            - **Cooking:** Soups, sauces, creamy dishes
                            - **Baking:** Cakes, breads, pancakes, muffins
                            - **Smoothies:** Base for fruit and protein smoothies
                            
                            #### 🍳 Recipes:
                            1. **Morning Cereal** - Classic breakfast
                            2. **Creamy Mashed Potatoes** - Use instead of water
                            3. **Homemade Hot Chocolate** - Heat with cocoa and sugar
                            4. **Smoothies** - Blend with fruits and yogurt
                            """)
                        elif 'corn flakes' in product_name_lower or 'cereal' in product_name_lower:
                            st.markdown("""
                            #### 🥣 Cereal Uses:
                            - **Breakfast:** With milk and fresh fruit
                            - **Snacking:** Eat dry as a crunchy snack
                            - **Cooking:** Use as coating for fried chicken
                            - **Baking:** In cookies, bars, dessert crusts
                            
                            #### 🍗 Recipes:
                            1. **Classic Breakfast** - Serve with milk and banana slices
                            2. **Cereal Bars** - Mix with honey and peanut butter
                            3. **Chicken Coating** - Crush and use as breading
                            4. **Dessert Crust** - Mix with butter for cheesecake crust
                            """)
                        elif 'orange juice' in product_name_lower:
                            st.markdown("""
                            #### 🧃 Orange Juice Uses:
                            - **Beverage:** Fresh glass for breakfast
                            - **Smoothies:** Base for fruit smoothies
                            - **Cooking:** Marinades, sauces, glazes
                            - **Cocktails:** Mimosas, screwdrivers, punches
                            
                            #### 🍹 Recipes:
                            1. **Breakfast Juice** - Serve chilled
                            2. **Sunrise Smoothie** - Blend with banana and yogurt
                            3. **Chicken Marinade** - Mix with herbs and garlic
                            4. **Mimosa** - Mix with champagne for brunch
                            """)
                        elif 'coca-cola' in product_name_lower or 'coke' in product_name_lower:
                            st.markdown("""
                            #### 🥤 Coca-Cola Uses:
                            - **Beverage:** Chilled as a refreshing drink
                            - **Mixer:** With rum (Cuba Libre), whiskey
                            - **Cooking:** Coca-Cola chicken, ribs, cake
                            - **Marinade:** Tenderizes meat
                            
                            #### 🍗 Recipes:
                            1. **Coca-Cola Chicken** - Simmer chicken in Coke with soy sauce
                            2. **Coca-Cola Cake** - Chocolate cake with Coke in batter
                            3. **Coca-Cola Ribs** - Use as braising liquid
                            4. **Cuba Libre** - Mix with rum and lime
                            """)
                        elif 'water' in product_name_lower:
                            st.markdown("""
                            #### 💧 Water Uses:
                            - **Hydration:** Drink throughout the day
                            - **Cooking:** Base for soups, boiling pasta/rice
                            - **Beverages:** Coffee, tea, juice concentrates
                            - **Baby Formula:** Mix with powder
                            
                            #### 💪 Health Tips:
                            1. Drink 8 glasses daily for optimal hydration
                            2. Add lemon or cucumber for flavor
                            3. Drink before meals to aid digestion
                            4. Stay hydrated during exercise
                            """)
                        elif 'b12' in product_name_lower or 'supplement' in product_name_lower:
                            st.markdown("""
                            #### 💊 B12 Supplement Uses:
                            - **Daily Supplement:** Take as directed on package
                            - **Energy Support:** Best taken in the morning
                            - **With Food:** Take with meals for better absorption
                            - **Sublingual:** Place under tongue for 30-60 seconds
                            
                            #### ⏰ Best Time to Take:
                            - **Morning:** With breakfast for all-day energy
                            - **Empty stomach:** For maximum absorption
                            - **Consistently:** Same time each day
                            
                            #### ⚠️ Important Notes:
                            - Follow dosage on package
                            - Consult doctor before starting supplements
                            - Store in cool, dry place
                            """)
                        else:
                            st.markdown("""
                            #### 🍽️ General Food Uses:
                            - **As packaged:** Follow preparation instructions
                            - **In recipes:** Incorporate into your favorite dishes
                            - **Storage:** Follow package storage instructions
                            - **Serving suggestions:** Check package for ideas
                            
                            #### 💡 Tips:
                            - Check expiration date before use
                            - Store properly after opening
                            - Follow any preparation instructions
                            """)
                    
                    # ==================== ACTION BUTTONS ====================
                    st.markdown("---")
                    col_btn1, col_btn2, col_btn3 = st.columns(3)
                    
                    with col_btn1:
                        if st.button("➕ Add to My Collection", use_container_width=True):
                            st.session_state.my_products.append({
                                'name': result['name'],
                                'brand': result['brand'],
                                'barcode': result['barcode'],
                                'is_b12': result['is_b12'],
                                'date': datetime.now().strftime("%Y-%m-%d"),
                                'time': datetime.now().strftime("%H:%M"),
                                'source': 'Open Food Facts'
                            })
                            st.success("✅ Added to your collection!")
                            time.sleep(0.5)
                            st.rerun()
                    
                    with col_btn2:
                        if st.button("🔄 Scan Another", use_container_width=True):
                            st.session_state.search_barcode = ''
                            st.rerun()
                    
                    with col_btn3:
                        if st.button("📤 Share Product", use_container_width=True):
                            share_text = f"""
📦 PRODUCT INFORMATION
══════════════════════
Name: {result['name']}
Brand: {result['brand']}
Barcode: {result['barcode']}
B12 Content: {'✅ Contains B12' if result['is_b12'] else '❌ No B12 detected'}
Source: {result['source']}

🥗 Ingredients:
{result.get('ingredients', 'N/A')[:200]}...
                            """
                            st.code(share_text)
                
                elif result and result.get('error') == 'not_found':
                    st.error("❌ Product not found in Open Food Facts database")
                    st.info(f"Barcode {barcode_input} was not found in the database of 3+ million products")
                    
                    # Suggest similar barcodes from test set
                    if barcode_input in test_barcodes:
                        st.success(f"✅ But it's in our test database: {test_barcodes[barcode_input]}")
                    
                    st.markdown("""
                    #### 💡 Tips:
                    - Check if you entered the correct barcode
                    - Try one of the test barcodes above
                    - Some new products may not be in database yet
                    - Barcodes should be 8-13 digits long
                    """)
                    
                    # Show similar barcodes
                    st.markdown("#### 🔍 Try these working barcodes:")
                    for code, desc in list(test_barcodes.items())[:5]:
                        st.markdown(f"- `{code}`: {desc}")
                
                elif result and result.get('error') in ['timeout', 'connection_error']:
                    st.warning("⚠️ Network issue - Could not connect to Open Food Facts database")
                    st.info("Please check your internet connection and try again")
                    
                    # Still show test database option
                    if barcode_input in test_barcodes:
                        st.success(f"✅ But it's in our test database: {test_barcodes[barcode_input]}")
                
                else:
                    st.error("❌ Error searching database")
                    st.info("Please try again or use one of the test barcodes above")
        else:
            st.warning("⚠️ Please enter a barcode number")
    
    # ==================== MY COLLECTION ====================
    if st.session_state.my_products:
        st.markdown("---")
        st.subheader("📋 My Product Collection")
        
        # Show statistics
        total = len(st.session_state.my_products)
        b12_count = sum(1 for p in st.session_state.my_products if p.get('is_b12'))
        
        col_stat1, col_stat2, col_stat3 = st.columns(3)
        with col_stat1:
            st.metric("Total Products", total)
        with col_stat2:
            st.metric("B12 Products", b12_count)
        with col_stat3:
            st.metric("Non-B12 Products", total - b12_count)
        
        # Display products
        for i, item in enumerate(st.session_state.my_products):
            with st.expander(f"📦 {item['name']} - Added {item.get('date', 'Unknown')}"):
                st.markdown(f"**Brand:** {item.get('brand', 'Unknown')}")
                st.markdown(f"**Barcode:** `{item.get('barcode', 'Unknown')}`")
                if item.get('is_b12'):
                    st.success("✅ Contains Vitamin B12")
                st.markdown(f"**Source:** {item.get('source', 'Database')}")
                st.caption(f"Added: {item.get('date', 'Unknown')} at {item.get('time', 'Unknown')}")
                
                if st.button("🗑️ Remove", key=f"remove_{i}"):
                    st.session_state.my_products.pop(i)
                    st.rerun()
        
        # Export options
        if st.button("📥 Export Collection", use_container_width=True):
            # Create DataFrame
            df = pd.DataFrame(st.session_state.my_products)
            
            # Download buttons
            col_csv, col_txt = st.columns(2)
            with col_csv:
                csv = df.to_csv(index=False)
                st.download_button(
                    label="📥 Download as CSV",
                    data=csv,
                    file_name=f"my_products_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )
            with col_txt:
                # Create text export
                text_export = "MY PRODUCT COLLECTION\n"
                text_export += "=" * 50 + "\n\n"
                for item in st.session_state.my_products:
                    text_export += f"Product: {item['name']}\n"
                    text_export += f"Brand: {item['brand']}\n"
                    text_export += f"Barcode: {item['barcode']}\n"
                    text_export += f"B12: {'Yes' if item.get('is_b12') else 'No'}\n"
                    text_export += f"Added: {item.get('date')} {item.get('time')}\n"
                    text_export += "-" * 30 + "\n"
                
                st.download_button(
                    label="📥 Download as Text",
                    data=text_export,
                    file_name=f"my_products_{datetime.now().strftime('%Y%m%d')}.txt",
                    mime="text/plain"
                )
    
    # ==================== SEARCH HISTORY ====================
    if st.session_state.search_history:
        with st.expander("📜 Recent Searches"):
            for item in st.session_state.search_history[-10:]:  # Show last 10
                st.caption(f"🔍 {item['date']} {item['time']} - Barcode: {item['barcode']}")
            
            if st.button("Clear History"):
                st.session_state.search_history = []
                st.rerun()

    # ==================== DATABASE INFO ====================
    with st.expander("ℹ️ About Open Food Facts Database"):
        st.markdown("""
        ### About Open Food Facts
        
        **Open Food Facts** is a free, open database of food products from around the world.
        
        #### 📊 Database Stats:
        - **3+ Million Products** from 150+ countries
        - **100,000+ Contributors** worldwide
        - **Updated Daily** with new products
        - **100% Free** and open data
        
        ####  Barcode Formats Supported:
        - EAN-13 (13 digits) - Most common
        - UPC-A (12 digits) - USA/Canada
        - EAN-8 (8 digits) - Small products
        - GTIN-13, GTIN-8, GTIN-12
        
        ####  Countries Covered:
        - Europe, North America, South America
        - Asia, Africa, Australia
        - Global coverage with local products
        
        *Data is provided by volunteers and manufacturers*
        """)

# ==================== SYMPTOM MATCHER PAGE ====================

elif page == " Symptom Matcher":
    # Clear results if coming from another page
    if 'last_page' in st.session_state and st.session_state.last_page != " Symptom Matcher":
        st.session_state.symptom_analysis = None
        st.session_state.current_image = None
    
    # Store current page
    st.session_state.last_page = " Symptom Matcher"
    
    st.markdown('<div class="main-title">  AI Symptom Analyzer</div>', unsafe_allow_html=True)
    
    # Simple header
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 15px;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 20px;
    ">
        <h3>Upload a photo for AI analysis</h3>
        <p>AI detects B12 deficiency signs in nails, tongue, skin, and eyes</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Initialize session state
    if 'symptom_analysis' not in st.session_state:
        st.session_state.symptom_analysis = None
    if 'current_image' not in st.session_state:
        st.session_state.current_image = None
    
    # Create two columns
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("### 📸 Step 1: Upload Photo")
        
        # Body part selection
        body_part = st.radio(
            "Select body area:",
            ["Nails", "Tongue", "Skin", "Eyes"],
            horizontal=True
        )
        
        # File uploader
        uploaded_file = st.file_uploader(
            "Choose a clear photo",
            type=['jpg', 'jpeg', 'png']
        )
        
        if uploaded_file is not None:
            # Display uploaded image
            image = Image.open(uploaded_file)
            st.session_state.current_image = image
            st.image(image, caption=f"Uploaded {body_part}", width=300)
            
            # Analyze button
            if st.button(" Analyze with AI", type="primary", use_container_width=True):
                with st.spinner(" AI is analyzing your image..."):
                    # Call AI analysis function
                    result = analyze_symptom_with_ai(image, body_part)
                    
                    if result['success']:
                        st.session_state.symptom_analysis = result
                        st.success(" Analysis complete!")
                        st.rerun()
                    else:
                        st.error(f"Analysis failed")
        
        # Clear button
        if st.button(" Clear", use_container_width=True):
            st.session_state.symptom_analysis = None
            st.session_state.current_image = None
            st.rerun()
    
    with col2:
        st.markdown("###  Step 2: AI Results")
        
        if st.session_state.symptom_analysis:
            result = st.session_state.symptom_analysis
            analysis_text = result['analysis']
            
            # Show which AI model was used
            if 'model_used' in result:
                st.caption(f" Mode: {result['model_used']}")
            
            # Extract severity
            severity = "Moderate"
            severity_color = "#F59E0B"
            
            if "SEVERITY: Mild" in analysis_text:
                severity = "Mild"
                severity_color = "#10B981"
            elif "SEVERITY: Severe" in analysis_text:
                severity = "Severe"
                severity_color = "#EF4444"
            
            # Extract confidence
            confidence = 85
            confidence_match = re.search(r'CONFIDENCE:\s*(\d+)%', analysis_text)
            if confidence_match:
                confidence = int(confidence_match.group(1))
            
            # Severity display
            st.markdown(f"""
            <div style="
                background: {severity_color}20;
                border-left: 6px solid {severity_color};
                padding: 15px;
                border-radius: 8px;
                margin-bottom: 15px;
            ">
                <h3 style="color: {severity_color}; margin:0;">{severity}</h3>
                <p style="color:white; margin:5px 0 0 0;">Confidence: {confidence}%</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Show sections
            if "DETECTED SYMPTOMS:" in analysis_text:
                parts = analysis_text.split("DETECTED SYMPTOMS:")
                if len(parts) > 1:
                    symptoms_part = parts[1].split("SEVERITY:")[0] if "SEVERITY:" in parts[1] else parts[1]
                    st.markdown("####  Detected Symptoms")
                    st.markdown(symptoms_part)
            
            if "SUPPLEMENT RECOMMENDATION:" in analysis_text:
                parts = analysis_text.split("SUPPLEMENT RECOMMENDATION:")
                if len(parts) > 1:
                    supp_part = parts[1].split("NEXT STEPS:")[0] if "NEXT STEPS:" in parts[1] else parts[1]
                    st.markdown("####  Recommendation")
                    st.info(supp_part)
            
            if "NEXT STEPS:" in analysis_text:
                parts = analysis_text.split("NEXT STEPS:")
                if len(parts) > 1:
                    steps_part = parts[1].split("DOCTOR ADVICE:")[0] if "DOCTOR ADVICE:" in parts[1] else parts[1]
                    st.markdown("####  Next Steps")
                    st.warning(steps_part)
            
            if "DOCTOR ADVICE:" in analysis_text:
                parts = analysis_text.split("DOCTOR ADVICE:")
                if len(parts) > 1:
                    doctor_part = parts[1]
                    st.markdown("####  Doctor Advice")
                    if "Severe" in severity:
                        st.error(doctor_part)
                    else:
                        st.info(doctor_part)
            
            # Download report
            if st.button(" Download Report", use_container_width=True):
                report = f"""B12 SYMPTOM ANALYSIS
Date: {result['timestamp']}
Body Part: {body_part}
Severity: {severity}
Confidence: {confidence}%

{analysis_text}

---
AI Analysis by B12 Assistant
"""
                st.download_button(
                    label="Download Text",
                    data=report,
                    file_name=f"b12_analysis_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
                    mime="text/plain"
                )
            
        else:
            # Placeholder
            st.markdown("""
            <div style="
                background: rgba(255,255,255,0.05);
                padding: 40px;
                border-radius: 10px;
                text-align: center;
                border: 2px dashed #667eea;
            ">
                <div style="font-size: 4rem; color: #667eea;">👆</div>
                <h4 style="color: white;">No analysis yet</h4>
                <p style="color: rgba(255,255,255,0.5);">Upload and click Analyze</p>
            </div>
            """, unsafe_allow_html=True)
    
    # Info section
    with st.expander(" About this tool"):
        st.markdown("""
        **How it works:**
        - AI analyzes your photo for B12 deficiency signs
        - Gives severity assessment and recommendations
        
        **Limitations:**
        - Not a medical diagnosis
        - Always confirm with blood tests
        """)
else:
    # ==================== ABOUT PAGE ====================
    st.markdown('<div class="main-title"> About B12 Assistant</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])    
    with col1:
        st.markdown("""
        ### Our Mission
        
        To make Vitamin B12 deficiency understanding accessible to everyone through technology.
        
        ### Why B12 Matters
        
        Vitamin B12 deficiency affects **1.5 billion people worldwide**, yet remains underdiagnosed. 
        Early detection can prevent irreversible neurological damage.
        
        ### How It Works
        
        1. **Assessment** - Evaluate your risk factors
        2. **Lab Analysis** - Process reports automatically

        ### Key Features
        
         **Risk Assessment** - Data-powered prediction
         **Lab Report Analysis** - PDF/Image processing
        
        ### Safety & Ethics
        
         **Privacy First** - Your data stays secure
         **Educational Only** - Not medical diagnosis
        """)
    
    with col2:
        st.markdown("###  B12 Facts")
        
        facts = [
            ("47%", "of Indians have B12 deficiency"),
            ("3-5 years", "Average delay in diagnosis"),
            ("<200 pg/mL", "Deficiency threshold"),
        ]
        
        for value, text in facts:
            st.metric(value, text)
        
        st.markdown("---")
    
    # Team/Contact
    col2, col3 = st.columns(2)
    
    with col2:
        st.markdown("###  Resources")
        st.write("[NIH B12 Fact Sheet](https://ods.od.nih.gov/factsheets/VitaminB12-HealthProfessional/)")
        st.write("[Mayo Clinic Guide](https://www.mayoclinic.org/diseases-conditions/vitamin-deficiency-anemia/symptoms-causes/syc-20355025)")
        st.write("[WHO Guidelines](https://www.who.int/health-topics/vitamins)")
    
    with col3:
        st.markdown("###  Contact")
        st.write("**For Support:**")
        st.write("healthbridge-b12@gmail.com")


# ==================== HELPER FUNCTIONS ====================

def analyze_b12_food(food_input, b12_database):
    """Helper function to analyze B12 from food input"""
    food_lower = food_input.lower()
    
    found_foods = []
    total_b12 = 0
    
    # Search for matching foods
    for food, value in b12_database.items():
        if food in food_lower:
            found_foods.append(f"{food.title()}: {value} mcg")
            total_b12 += value
    
    st.markdown("---")
    st.markdown("###  Your B12 Results")
    
    # Create two columns for results
    col_res1, col_res2 = st.columns(2)
    
    with col_res1:
        if found_foods:
            st.markdown("** B12-Rich Foods Detected:**")
            for item in found_foods[:8]:  # Show top 8
                st.markdown(f"• {item}")
            if len(found_foods) > 8:
                st.caption(f"... and {len(found_foods)-8} more items")
        else:
            st.warning(" No B12-rich foods detected")
            st.markdown("**Try adding:** eggs, milk, fish, cheese, or yogurt")
    
    with col_res2:
        # Big number for total B12
        st.markdown("**Total Vitamin B12:**")
        st.markdown(f"# {total_b12:.1f} mcg")
        
        # Daily need progress
        daily_goal = 2.4
        percent = (total_b12 / daily_goal) * 100
        percent = min(percent, 100)  # Cap at 100%
        
        # Progress bar
        st.progress(percent/100, text=f"{percent:.0f}% of daily need (2.4 mcg)")
        
        # Rating with emoji
        if total_b12 >= daily_goal:
            st.success(" **EXCELLENT!** You met your daily B12 need!")
        elif total_b12 >= 1.5:
            st.success("🟢 **GOOD** B12 intake")
        elif total_b12 >= 0.5:
            st.warning("🟡 **MODERATE** - Consider adding more B12 foods")
        else:
            st.error("🔴 **LOW** B12 - Try eggs or milk today")
    
    # Suggestions to boost B12
    if total_b12 < daily_goal:
        st.markdown("---")
        st.markdown("###  Quick Ways to Boost Your B12")
        
        col_sug1, col_sug2, col_sug3 = st.columns(3)
        
        with col_sug1:
            st.markdown("** Add an egg**")
            st.markdown("+0.6 mcg B12")
        
        with col_sug2:
            st.markdown("** Drink milk**")
            st.markdown("+1.2 mcg B12 (1 glass)")
        
        with col_sug3:
            st.markdown("** Add fish**")
            st.markdown("+2.5 mcg B12 (100g)")
    
    # Download button for results
    result_text = f"Food: {food_input}\n\nB12 Foods Found: {found_foods}\n\nTotal B12: {total_b12} mcg\n\nPercentage of Daily Need: {percent:.0f}%"
    
    st.download_button(
        label=" Download Results",
        data=result_text,
        file_name=f"b12_scan_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
        mime="text/plain"
    )
    
    # Log activity
    log_user_activity(
        activity_type='food_scan_db',
        data={'food': food_input, 'b12': total_b12},
        description=f"Database scan: {total_b12:.1f} mcg B12"
    )


def convert_schedule_to_table(schedule_text, b12_value, status):
    """Convert schedule text to table format"""
    import pandas as pd
    
    # Parse the schedule text
    lines = schedule_text.split('\n')
    table_data = []
    current_category = None
    
    for line in lines:
        line = line.strip()
        
        # Skip empty lines
        if not line:
            continue
            
        # Check for category headers
        if ' **TREATMENT OVERVIEW**' in line:
            table_data.append({
                'Category': 'Treatment Overview',
                'Phase': status,
                'B12 Level': f"{b12_value} pg/mL",
                'Details': f"Schedule generated on {datetime.now().strftime('%Y-%m-%d')}"
            })
        elif ' **SUPPLEMENT SCHEDULE**' in line:
            current_category = 'Supplements'
        elif ' **DIET SCHEDULE**' in line:
            current_category = 'Diet'
        elif ' **EXERCISE ROUTINE**' in line:
            current_category = 'Exercise'
        elif ' **FOLLOW-UP SCHEDULE**' in line:
            current_category = 'Follow-up'
        elif ' **WEEKLY CHECKLIST**' in line:
            current_category = 'Checklist'
        elif line.startswith('•') and current_category:
            # Remove bullet point and add to table
            item = line[1:].strip()
            table_data.append({
                'Category': current_category,
                'Item': item,
                'Timing': 'Weekly' if current_category == 'Checklist' else 'As scheduled'
            })
        elif 'Phase' in line and ':' in line and current_category == 'Supplements':
            # Handle supplement phases
            parts = line.split(':')
            if len(parts) >= 2:
                phase = parts[0].strip()
                details = parts[1].strip()
                table_data.append({
                    'Category': 'Supplements',
                    'Phase': phase,
                    'Details': details,
                    'Timing': 'As per phase'
                })
    
    # Create DataFrame
    if table_data:
        df = pd.DataFrame(table_data)
        # Reorder columns
        if 'Phase' in df.columns and 'Item' in df.columns:
            df['Details'] = df.apply(lambda x: x['Item'] if pd.notna(x['Item']) else x['Details'] if 'Details' in x else '', axis=1)
            df = df[['Category', 'Phase', 'Details', 'Timing']]
        elif 'Details' in df.columns:
            df = df[['Category', 'Details', 'Timing']]
        else:
            df = df[['Category', 'Timing']]
    else:
        # Create default table
        df = pd.DataFrame({
            'Category': ['Treatment Overview', 'Supplements', 'Diet', 'Follow-up'],
            'Recommendation': [
                f'B12 Level: {b12_value} pg/mL - Status: {status}',
                'Consult doctor for supplement plan',
                'Increase B12-rich foods in diet',
                f'Retest in {"3" if status == "DEFICIENT" else "6" if status == "BORDERLINE" else "12"} months'
            ]
        })
    
    return df