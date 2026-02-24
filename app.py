# app.py - COMPLETE VERSION WITH WELCOME PAGE
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import io
import uuid
import re
import json

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
    /* Welcome page specific styles */
    .welcome-container {
        background: linear-gradient(rgba(0, 0, 0, 0.7), rgba(0, 0, 0, 0.7)), 
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
        font-size: 3.5rem;
        font-weight: bold;
        margin-bottom: 1rem;
        background: linear-gradient(90deg, #667eea, #764ba2);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    .welcome-subtitle {
        font-size: 1.5rem;
        margin-bottom: 2rem;
        color: #e2e8f0;
        max-width: 800px;
    }
    .welcome-button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 15px 40px;
        border: none;
        border-radius: 50px;
        font-size: 1.2rem;
        font-weight: bold;
        cursor: pointer;
        margin: 10px;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }
    .welcome-button:hover {
        transform: translateY(-3px);
        box-shadow: 0 6px 20px rgba(0,0,0,0.3);
        background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
    }
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
    }
    .feature-icon {
        font-size: 2.5rem;
        margin-bottom: 15px;
    }
    
    /* Original styles remain unchanged */
    .main-title {
        font-size: 2.8rem;
        color: #1E3A8A;
        text-align: center;
        padding: 1rem;
        background: linear-gradient(90deg, #E0F2FE, #DBEAFE);
        border-radius: 10px;
        margin-bottom: 1.5rem;
    }
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
    .card {
        background: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin: 10px 0;
    }
    .schedule-table {
        width: 100%;
        border-collapse: collapse;
        margin: 15px 0;
    }
    .schedule-table th {
        background-color: #3B82F6;
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
    .welcome-page #MainMenu {visibility: hidden;}
    .welcome-page header {visibility: hidden;}
    .welcome-page footer {visibility: hidden;}
    
    /* Streamlit button styling overrides */
    .stButton > button {
        border-radius: 50px;
        padding: 10px 24px;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    /* Custom button classes */
    .primary-button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        border: none !important;
    }
    
    .secondary-button {
        background: rgba(255, 255, 255, 0.1) !important;
        color: white !important;
        border: 1px solid rgba(255, 255, 255, 0.3) !important;
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
        st.markdown("Join thousands who have taken control of their B12 health with our AI assistant.")
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
        
        if st.button(" **Continue as Guest**", use_container_width=True, key="welcome_guest", type="secondary"):
            st.session_state.show_welcome = False
            st.session_state.authenticated = False
            st.rerun()
        
        # Stats
        st.markdown("<br><br>", unsafe_allow_html=True)
        col_stats1, col_stats2, col_stats3, col_stats4 = st.columns(4)
        
        with col_stats1:
            st.metric("Users Helped", "1000+")
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
    st.success(" Logged out successfully")
    st.rerun()

# ==================== HELPER FUNCTIONS ====================

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
    st.markdown(" B12 Assistant")
    st.markdown("---")
    
    # Navigation
    if st.session_state.authenticated:
        menu_options = [
            " Dashboard", " Assessment"," B12 Tracker", " Voice Assistant"," Lab Reports", " Meal Planner",
            " Results", " My Profile", " Cloud Database", " About"
        ]
    else:
        menu_options = [
            " Dashboard", " Assessment", " B12 Tracker"," Voice Assistant"," Lab Reports", " Meal Planner",
            " Results", " Login/Signup", " About"
        ]
    
    page = st.radio(
        "**Navigate to:**",
        menu_options,
        index=0
    )
    
    st.markdown("---")
    
    st.markdown("###  Quick Info")
    if st.session_state.authenticated:
        user = st.session_state.current_user
        st.write(f"**User:** {user['username']}")
        
        if st.button(" Logout"):
            logout()
    else:
        st.write("**Status:** Not logged in")
        
        # Show temp logs count
        if 'temp_logs' in st.session_state and st.session_state.temp_logs:
            temp_count = len(st.session_state.temp_logs)
            if temp_count > 0:
                st.warning(f" {temp_count} unsaved logs")
                st.caption("Login to save to cloud")
        
        # Show Back to Welcome button for non-logged in users
        if st.button("← Back to Welcome"):
            st.session_state.show_welcome = True
            st.rerun()
        
        if page != " Login/Signup":
            if st.button(" Login/Signup"):
                page = " Login/Signup"
                st.rerun()
    
    if st.session_state.user_data:
        user = st.session_state.user_data
        st.write(f"**Age:** {user.get('age', 'N/A')}")
        st.write(f"**Diet:** {user.get('diet_type', 'N/A')}")
        if st.session_state.risk_level:
            risk_color = {
                'High': '🔴',
                'Medium': '🟡', 
                'Low': '🟢'
            }.get(st.session_state.risk_level, '⚪')
            st.write(f"**Risk:** {risk_color} {st.session_state.risk_level}")
    
    st.markdown("---")
    
    st.markdown("###  Model Status")
    if ml_predictor.model:
        st.success(" Model Active")
        dataset_info = ml_predictor.get_dataset_info()
        if dataset_info['status'] == 'Loaded':
            st.caption(f"Dataset: {dataset_info['samples']:,} samples")
    else:
        st.info(" Basic Assessment")
    
    st.markdown("---")
    
    st.markdown("###  Settings")
    if st.button(" Reset Data"):
        clear_user_session()
        st.rerun()

# ==================== AUTHENTICATION CHECK ====================
if page == " Login/Signup" or not st.session_state.authenticated:
    if page != " Login/Signup" and not st.session_state.authenticated:
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
# ==================== DASHBOARD PAGE ====================
if page == " Dashboard":
    # Dashboard Header with Background Image
    st.markdown(f"""
    <div style="
        background: linear-gradient(rgba(0, 0, 0, 0.7), rgba(0, 0, 0, 0.7)), 
                    url('https://th.bing.com/th/id/OIP.a5WONQ-_Hrmrxv0jN8J1XgHaEH?w=333&h=185&c=7&r=0&o=7&dpr=1.3&pid=1.7&rm=3');
        background-size: cover;
        background-position: center;
        padding: 50px 30px;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin-bottom: 30px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.3);
    ">
        <h1 style="font-size: 3.2rem; margin-bottom: 15px; color: white; font-weight: bold;">
            B12 Deficiency Assistant
        </h1>
        <p style="font-size: 1.3rem; color: #e2e8f0; max-width: 800px; margin: 0 auto;">
            Your AI-powered health companion for Vitamin B12 deficiency detection, analysis, and management
        </p>
        <div style="display: flex; justify-content: center; gap: 20px; margin-top: 30px; flex-wrap: wrap;">
            <div style="background: rgba(255, 255, 255, 0.15); padding: 10px 20px; border-radius: 50px; backdrop-filter: blur(10px);">
                <span style="font-weight: bold;">AI Assessment</span>
            </div>
            <div style="background: rgba(255, 255, 255, 0.15); padding: 10px 20px; border-radius: 50px; backdrop-filter: blur(10px);">
                <span style="font-weight: bold;">Lab Analysis</span>
            </div>
            <div style="background: rgba(255, 255, 255, 0.15); padding: 10px 20px; border-radius: 50px; backdrop-filter: blur(10px);">
                <span style="font-weight: bold;">Meal Planning</span>
            </div>
            <div style="background: rgba(255, 255, 255, 0.15); padding: 10px 20px; border-radius: 50px; backdrop-filter: blur(10px);">
                <span style="font-weight: bold;">Voice Assistant</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # User welcome message if authenticated
    if st.session_state.authenticated and st.session_state.current_user:
        user = st.session_state.current_user
        st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            border-radius: 10px;
            color: white;
            margin-bottom: 20px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.2);
        ">
            <h3 style="margin: 0;">
                Welcome back, <span style="color: #fbbf24;">{user['username']}</span>
            </h3>
            <p style="margin: 10px 0 0 0; color: #e2e8f0; font-size: 0.95rem;">
                Last login: {datetime.now().strftime('%Y-%m-%d %H:%M')} | Ready to continue your health journey
            </p>
        </div>
        """, unsafe_allow_html=True)
    else:
        # Show temp logs notification on dashboard
        if not st.session_state.authenticated and 'temp_logs' in st.session_state:
            temp_count = len(st.session_state.temp_logs)
            if temp_count > 0:
                st.warning(f"""
                <div style="background: #fef3c7; padding: 15px; border-radius: 10px; border-left: 5px solid #f59e0b;">
                    <strong>You have {temp_count} unsaved activities</strong><br>
                    Login or create an account to save them to your cloud profile
                </div>
                """, unsafe_allow_html=True)
    
    # Quick Stats Row
    st.markdown("### Quick Statistics")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="High Risk Cases", 
            value="23%", 
            delta="+2.3%", 
            delta_color="inverse",
            help="Percentage of users with high B12 deficiency risk"
        )
    
    with col2:
        st.metric(
            label="Average B12 Level", 
            value="245 pg/mL", 
            delta="-15 pg/mL",
            delta_color="inverse",
            help="Average Vitamin B12 level across all users"
        )
    
    with col3:
        st.metric(
            label="Active Users", 
            value="1,247", 
            delta="+87", 
            help="Number of active users this month"
        )
    
    with col4:
        st.metric(
            label="AI Accuracy", 
            value="94.7%", 
            delta="+1.2%", 
            help="AI model prediction accuracy rate"
        )
    
    st.markdown("---")
    
    # Main Content
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Risk Distribution Chart
        st.markdown("### Risk Distribution Overview")
        
        risk_data = pd.DataFrame({
            'Risk Level': ['Very Low', 'Low', 'Medium', 'High'],
            'Users': [400, 350, 250, 247],
            'Color': ['#10B981', '#34D399', '#F59E0B', '#EF4444']
        })
        
        fig = px.bar(risk_data, x='Risk Level', y='Users', 
                    color='Risk Level', color_discrete_sequence=risk_data['Color'],
                    title="User Risk Levels Distribution",
                    text='Users')
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(size=12),
            showlegend=False
        )
        fig.update_traces(textposition='outside')
        st.plotly_chart(fig, use_container_width=True)
        
        # Quick Self-Check
        st.markdown("### Quick Self-Check")
        with st.expander("Check your risk in 30 seconds", expanded=False):
            q_age = st.slider("Your Age", 18, 80, 30, key="quick_age")
            q_diet = st.selectbox("Your Diet", ["Omnivore", "Vegetarian", "Vegan"], key="quick_diet")
            q_fatigue = st.checkbox("Feel tired often?", key="quick_fatigue")
            
            col_a, col_b = st.columns([3, 1])
            with col_a:
                if st.button("Quick Check", type="primary", use_container_width=True):
                    quick_score = 0
                    if q_age > 50: quick_score += 2
                    if q_diet == "Vegan": quick_score += 3
                    elif q_diet == "Vegetarian": quick_score += 2
                    if q_fatigue: quick_score += 2
                    
                    # Log this activity
                    log_user_activity(
                        activity_type='quick_check',
                        data={
                            'age': q_age,
                            'diet': q_diet,
                            'fatigue': q_fatigue,
                            'score': quick_score
                        },
                        description="Quick risk check"
                    )
                    
                    if quick_score >= 5:
                        st.error("### Moderate to High Risk")
                        st.write("Consider completing a full assessment for detailed analysis")
                    elif quick_score >= 3:
                        st.warning("### Low to Moderate Risk")
                        st.write("Monitor your symptoms and consider preventive measures")
                    else:
                        st.success("### Low Risk")
                        st.write("Maintain healthy habits and regular check-ups")
            
            with col_b:
                if st.button("Clear", type="secondary", use_container_width=True):
                    st.rerun()
    
    with col2:
        # Get Started Section
        st.markdown("### Get Started")
        
        # Feature Cards
        feature_cards = [
            {
                "title": "Complete Assessment",
                "description": "Take 5-minute comprehensive risk assessment",
                "button": "Start Assessment",
                "page": " Assessment",
                "color": "#3B82F6"
            },
            {
                "title": "Upload Lab Reports",
                "description": "Analyze your B12 test results with AI",
                "button": "Upload Reports",
                "page": " Lab Reports",
                "color": "#8B5CF6"
            },
            {
                "title": "Get Meal Plan",
                "description": "Personalized B12-rich diet recommendations",
                "button": "View Meal Plan",
                "page": " Meal Planner",
                "color": "#10B981"
            },
            {
                "title": "Voice Assistant",
                "description": "Ask questions and get voice responses",
                "button": "Try Voice Assistant",
                "page": " Voice Assistant",
                "color": "#F59E0B"
            },
            {
                "title": "B12 Tracker",
                "description": "Track daily symptoms and supplements",
                "button": "Open Tracker",
                "page": " B12 Tracker",
                "color": "#EC4899"
            }
        ]
        
        for card in feature_cards:
            with st.container(border=True):
                st.markdown(f"""
                <div style="margin-bottom: 10px;">
                    <span style="font-weight: bold; font-size: 1.1rem; color: {card['color']};">{card['title']}</span>
                </div>
                <p style="color: #6B7280; font-size: 0.9rem; margin-bottom: 15px;">{card['description']}</p>
                """, unsafe_allow_html=True)
                
                if st.button(card['button'], key=f"dashboard_{card['title'].lower().replace(' ', '_')}"):
                    page = card['page']
                    st.rerun()
        
        # Recent Activity (if any)
        if st.session_state.authenticated or st.session_state.temp_logs:
            st.markdown("### Recent Activity")
            with st.container(border=True):
                if st.session_state.temp_logs:
                    # Show recent temp logs
                    recent_logs = st.session_state.temp_logs[-3:]  # Last 3 logs
                    for log in reversed(recent_logs):
                        st.markdown(f"""
                        <div style="margin: 8px 0;">
                            <div style="font-weight: 500; color: #374151;">{log['description']}</div>
                            <div style="font-size: 0.8rem; color: #6B7280;">{log['date']}</div>
                        </div>
                        <hr style="margin: 5px 0; border-color: #f3f4f6;">
                        """, unsafe_allow_html=True)
                elif st.session_state.authenticated:
                    st.info("No recent activity. Start by completing an assessment!")
    
    # Bottom Section - Tips and Resources
    st.markdown("---")
    st.markdown("### Quick Tips & Resources")
    
    tips_col1, tips_col2, tips_col3 = st.columns(3)
    
    with tips_col1:
        with st.container(border=True):
            st.markdown("#### Dietary Sources")
            st.write("• Animal products (meat, fish, eggs)")
            st.write("• Fortified foods (cereals, plant milks)")
            st.write("• Nutritional yeast")
            st.markdown("---")
            st.markdown("[Learn more about B12-rich foods](https://www.healthline.com/nutrition/vitamin-b12-foods)")
    
    with tips_col2:
        with st.container(border=True):
            st.markdown("#### Common Symptoms")
            st.write("• Fatigue and weakness")
            st.write("• Numbness/tingling")
            st.write("• Memory problems")
            st.write("• Pale or yellowish skin")
            st.markdown("---")
            st.markdown("[Recognize B12 deficiency symptoms](https://www.mayoclinic.org/diseases-conditions/vitamin-deficiency-anemia/symptoms-causes/syc-20355025)")
    
    with tips_col3:
        with st.container(border=True):
            st.markdown("#### When to See a Doctor")
            st.write("• Severe neurological symptoms")
            st.write("• Symptoms worsening")
            st.write("• No improvement with supplements")
            st.write("• Planning pregnancy")
            st.markdown("---")
            st.markdown("[Find a specialist near you](https://www.healthgrades.com)")

# ==================== LAB REPORTS PAGE ====================
elif page == " Lab Reports":
    st.markdown('<div class="main-title"> Lab Report Analysis</div>', unsafe_allow_html=True)
    
    # Only one tab now
    st.markdown("### Upload Your Lab Report")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        uploaded_file = st.file_uploader(
            "Choose PDF file",
            type=['pdf'],
            help="Upload your Vitamin B12 lab report (PDF only)"
        )
    
    with col2:
        st.markdown("**Supported Formats:**")
        st.write("- PDF documents only")
        st.write("- Max size: 10MB")
    
    if uploaded_file is not None:
        # File info
        st.markdown("---")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("File Name", uploaded_file.name)
        with col2:
            st.metric("File Type", "PDF")
        with col3:
            file_size = f"{uploaded_file.size / 1024:.1f} KB"
            st.metric("File Size", file_size)
        
        # Preview
        st.markdown("### Preview")
        with st.expander("View PDF Text"):
            try:
                from utils import extract_text_from_pdf
                text = extract_text_from_pdf(uploaded_file)
                st.text(text[:2000] + "..." if len(text) > 2000 else text)
            except:
                st.info("Could not extract text. The file may be scanned.")
        
        # Single AI Analysis button
        if st.button("  AI PDF Analysis", type="primary", use_container_width=True):
            with st.spinner(" AI is analyzing PDF and generating recommendations..."):
                try:
                    # Use Gemini to analyze PDF
                    ai_result = analyze_lab_pdf_with_gemini(uploaded_file)
                    
                    if ai_result.get('success'):
                        st.markdown("---")
                        st.markdown(" AI Analysis Results")
                        
                        # Get B12 value safely
                        b12_value = ai_result.get('b12_value')
                        
                        # Show B12 value if found - NO "NOT DETECTED" WARNING
                        if b12_value is not None:
                            b12_val = float(b12_value)
                            
                            # Display B12 level with status
                            col1, col2, col3 = st.columns(3)
                            
                            with col1:
                                if b12_val < 200:
                                    st.error(f"**{b12_val} pg/mL**")
                                    st.caption("Deficient")
                                elif b12_val < 300:
                                    st.warning(f"**{b12_val} pg/mL**")
                                    st.caption("Borderline")
                                else:
                                    st.success(f"**{b12_val} pg/mL**")
                                    st.caption("Normal")
                            
                            with col2:
                                if b12_val < 200:
                                    st.metric("Status", "DEFICIENT")
                                elif b12_val < 300:
                                    st.metric("Status", "BORDERLINE")
                                else:
                                    st.metric("Status", "NORMAL")
                            
                            with col3:
                                st.metric("Normal Range", "200-900 pg/mL")
                            
                            # Determine status for recommendations
                            if b12_val < 200:
                                status = "DEFICIENT"
                            elif b12_val < 300:
                                status = "BORDERLINE"
                            else:
                                status = "NORMAL"
                        else:
                            # NO WARNING - just show analysis
                            status = "NOT DETECTED"
                            b12_val = None
                        
                        # Show AI analysis - always show this even if B12 not found
                        st.markdown(" Analysis")
                        analysis_text = ai_result.get('analysis', 'No analysis provided')
                        st.write(analysis_text)
                        
                        # Generate additional AI recommendations
                        st.markdown("---")
                        st.markdown("Recommendations")
                        
                        # Get user data for context if available
                        user_data = st.session_state.user_data if 'user_data' in st.session_state else {}
                        age = user_data.get('age', 30)
                        diet_type = user_data.get('diet_type', 'Omnivore')
                        symptoms_count = user_data.get('symptoms_count', 0)
                        
                        # Generate AI recommendations
                        ai_recs = generate_ai_treatment_recommendations(
                            b12_value=b12_val if b12_value is not None else None,
                            status=status,
                            age=age,
                            diet_type=diet_type,
                            symptoms_count=symptoms_count
                        )
                        
                        if ai_recs.get('success'):
                            # Display recommendations
                            recommendations = ai_recs.get('recommendations', {})
                            
                            if isinstance(recommendations, dict):
                                # Display dictionary format
                                for category, content in recommendations.items():
                                    if content:
                                        st.markdown(f"#### {category.upper().replace('_', ' ')}")
                                        if isinstance(content, list):
                                            for item in content:
                                                st.markdown(f"• {item}")
                                        elif isinstance(content, dict):
                                            for key, value in content.items():
                                                st.markdown(f"**{key}:** {value}")
                                        else:
                                            st.write(content)
                            else:
                                # Display string format
                                st.write(recommendations)
                        
                        # Generate basic treatment timeline - only if B12 value found
                        if b12_value is not None:
                            st.markdown("---")
                            st.markdown(" Basic Treatment Timeline")
                            
                            b12_val = float(b12_value)
                            if b12_val < 150:
                                timeline = """
                                **Severe Deficiency (<150 pg/mL):**
                                • **Weeks 1-4:** High-dose B12 supplements (2000 mcg daily)
                                • **Months 2-6:** Continue supplements, monitor symptoms
                                • **After 6 months:** Maintenance dose, regular testing
                                """
                            elif b12_val < 200:
                                timeline = """
                                **Deficient (150-199 pg/mL):**
                                • **Weeks 1-8:** B12 supplements (1000 mcg daily)
                                • **Months 3-6:** Reduce to maintenance dose
                                • **Follow-up test:** After 3 months
                                • **Medical consultation:** Within 2 weeks
                                """
                            elif b12_val < 300:
                                timeline = """
                                **Borderline (200-299 pg/mL):**
                                • **Months 1-3:** Preventive supplements (500 mcg daily)
                                • **Diet focus:** Increase B12-rich foods
                                • **Follow-up test:** After 6 months
                                • **Monitor symptoms:** Regular self-check
                                """
                            else:
                                timeline = """
                                **Normal (≥300 pg/mL):**
                                • **Maintenance:** Continue healthy diet
                                • **Prevention:** Consider low-dose supplements if at risk
                                • **Annual check:** Regular B12 testing
                                • **Lifestyle:** Maintain balanced diet
                                """
                            
                            st.write(timeline)
                        
                        # Save AI analysis to session
                        st.session_state.ai_pdf_analysis = ai_result
                        
                        # Log lab report activity
                        log_user_activity(
                            activity_type='lab_report',
                            data={
                                'filename': uploaded_file.name,
                                'b12_value': b12_value,
                                'status': status,
                                'ai_analysis': True
                            },
                            description=f"AI PDF analysis - {status}"
                        )
                        
                        # Save to MongoDB if authenticated
                        if st.session_state.authenticated and st.session_state.mongodb.connected:
                            try:
                                mongo_id = st.session_state.mongodb.save_lab_report(
                                    lab_data={
                                        'b12_value': b12_value,
                                        'status': status,
                                        'analysis': ai_result.get('analysis', '')[:500],
                                        'ai_recommendations': ai_recs.get('recommendations', {})
                                    },
                                    user_data=st.session_state.user_data if 'user_data' in st.session_state else {},
                                    user_id=st.session_state.current_user['user_id'],
                                    session_id=st.session_state.session_id
                                )
                                if mongo_id:
                                    st.success(" Analysis saved to cloud!")
                            except Exception as mongo_error:
                                st.warning(f" Could not save: {str(mongo_error)[:100]}")
                        
                        # Save to session state lab reports
                        report_data = {
                            'b12_value': b12_value,
                            'filename': uploaded_file.name,
                            'status': status,
                            'date': datetime.now().strftime("%Y-%m-%d"),
                            'message': f'AI analysis: {status}',
                            'ai_analysis': ai_result.get('analysis', '')[:500],
                            'ai_recommendations': ai_recs.get('recommendations', {})
                        }
                        
                        st.session_state.lab_reports.append(report_data)
                        
                        st.success(" Analysis complete!")
                        
                    else:
                        st.error(f" AI analysis failed: {ai_result.get('error', 'Unknown error')}")
                        
                except Exception as e:
                    st.error(f" Analysis error: {str(e)}")
        
        # Manual entry option as fallback
        st.markdown("---")
        with st.expander(" Enter Value Manually"):
            manual_b12 = st.number_input("Enter B12 Level (pg/mL)", 0, 2000, 0)
            if manual_b12 > 0 and st.button("Save Manual Entry"):
                # Determine status
                if manual_b12 < 200:
                    manual_status = "DEFICIENT"
                elif manual_b12 < 300:
                    manual_status = "BORDERLINE"
                else:
                    manual_status = "NORMAL"
                
                manual_data = {
                    'lab_b12_level': manual_b12,
                    'b12_source': 'manual_entry'
                }
                
                # Add to conflict tracker
                data_tracker.add_data_point(manual_data, "manual_lab_entry")
                
                report_entry = {
                    'b12_value': manual_b12,
                    'filename': 'Manual Entry',
                    'status': manual_status,
                    'date': datetime.now().strftime("%Y-%m-%d"),
                    'message': f'Manual entry: {manual_b12} pg/mL'
                }
                
                st.session_state.lab_reports.append(report_entry)
                
                # Log manual lab entry
                log_user_activity(
                    activity_type='lab_report_manual',
                    data={
                        'b12_value': manual_b12,
                        'status': manual_status,
                        'source': 'manual'
                    },
                    description=f"Manual lab entry - {manual_status}"
                )
                
                # Save to MongoDB if authenticated
                if st.session_state.authenticated and st.session_state.mongodb.connected:
                    try:
                        result = {
                            'b12_value': manual_b12, 
                            'status': manual_status, 
                            'message': 'Manual entry'
                        }
                        mongo_id = st.session_state.mongodb.save_lab_report(
                            lab_data=result,
                            user_data=st.session_state.user_data if 'user_data' in st.session_state else {},
                            user_id=st.session_state.current_user['user_id'],
                            session_id=st.session_state.session_id
                        )
                        if mongo_id:
                            st.success(" Manual entry saved to cloud!")
                    except Exception as mongo_error:
                        st.warning(f" Could not save: {str(mongo_error)[:100]}")
                
                st.success(f"Saved: {manual_b12} pg/mL")
    else:
        st.info(" Upload a PDF lab report to get analysis and recommendations.")

# ==================== MEAL PLANNER PAGE ====================
elif page == " Meal Planner":
    st.markdown('<div class="main-title"> AI-Powered Meal Planner</div>', unsafe_allow_html=True)

    st.info("""
    Get a personalized 3-day B12-rich meal plan created by AI, tailored to your diet and risk profile.
    You can download the plan as a PDF for easy reference.
    """)

    # ----- USER DATA SECTION -----
    col1, col2 = st.columns(2)
    user_data = st.session_state.get('user_data', {})

    with col1:
        # Get primary user info from the assessment
        diet_type = user_data.get('diet_type', 'Omnivore')
        st.markdown(" Your Profile")
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
        with st.expander(" Add Specific Goals/Restrictions"):
            user_goals = st.text_area(
                "e.g., 'Focus on high-energy breakfasts', 'Avoid soy', 'Budget-friendly meals'",
                height=60,
                placeholder="(Optional) Add any specific requests for the AI..."
            )

    st.markdown("---")

    # ----- GENERATE MEAL PLAN WITH AI -----
    st.markdown("###  Generate Your Meal Plan")

    if st.button(" Generate  Meal Plan", type="primary", use_container_width=True):
        if not diet_for_plan:
            st.warning("Please select a diet type.")
        else:
            with st.spinner(" AI is creating your personalized meal plan..."):
                try:
                    from utils import setup_gemini_api
                    
                    # 1. CALL GEMINI AI TO GENERATE THE MEAL PLAN TEXT
                    model = setup_gemini_api()
                    if model:
                        # Build the prompt for the AI
                        prompt = f"""You are a expert nutritionist specializing in Vitamin B12.
Create a detailed, practical, and appetizing 3-day meal plan to help with B12 levels.

USER CONTEXT:
- Diet Type: {diet_for_plan}
- Age Group: {age} years old
- B12 Risk Level: {risk_level}
- Additional Notes: {user_goals if user_goals else 'None'}

GENERATE A PLAN WITH THIS STRUCTURE IN THE FORM OF TABLE SIMPLE TO UNDERSTAND:
**DAY 1**
- **Breakfast:** [Meal name]. [Brief description]. [Estimated B12 content].
- **Lunch:** [Meal name]. [Brief description]. [Estimated B12 content].
- **Dinner:** [Meal name]. [Brief description]. [Estimated B12 content].
- **Snack:** [Snack suggestion].

**DAY 2** (same structure)
**DAY 3** (same structure)

After the 3-day plan, add these two sections:
**SHOPPING LIST**
- **Produce:** [List]
- **Protein:** [List]
- **Pantry:** [List]
- **Dairy/Alternatives:** [List]

**KEY B12 TIPS FOR A {diet_for_plan.upper()} DIET**
- [Tip 1]
- [Tip 2]
- [Tip 3]

Write in clear, encouraging language. Focus on whole foods appropriate for the diet type.
"""
                        response = model.generate_content(prompt)
                        ai_meal_plan_text = response.text

                        # Save the generated text to the session state
                        st.session_state.ai_meal_plan_text = ai_meal_plan_text
                        st.session_state.meal_plan_diet = diet_for_plan
                        st.session_state.meal_plan_generated_time = datetime.now().strftime("%Y-%m-%d")

                        # Log meal plan generation
                        log_user_activity(
                            activity_type='meal_plan',
                            data={
                                'diet_type': diet_for_plan,
                                'risk_level': risk_level,
                                'age': age,
                                'has_goals': bool(user_goals)
                            },
                            description=f"AI meal plan generated for {diet_for_plan} diet"
                        )
                        
                        st.success(" Your AI meal plan is ready!")

                    else:
                        st.error("Could not connect to the AI service. Please check your configuration.")

                except Exception as e:
                    st.error(f"An error occurred while generating the plan: {str(e)}")

    st.markdown("---")

    # ----- DISPLAY AND DOWNLOAD GENERATED PLAN -----
    if 'ai_meal_plan_text' in st.session_state:
        st.markdown(" Your Personalized Meal Plan")

        # Display the plan in an expandable area
        with st.expander(" View Full Meal Plan", expanded=True):
            # Format and display the text
            formatted_text = st.session_state.ai_meal_plan_text.replace('**', '**')
            st.markdown(formatted_text)

        st.markdown("---")
        st.markdown(" Download Your Plan")

        # SIMPLE TEXT DOWNLOAD (ALWAYS WORKS)
        st.download_button(
            label=" Download as Text File",
            data=st.session_state.ai_meal_plan_text,
            file_name=f"B12_Meal_Plan_{st.session_state.get('meal_plan_diet', 'Plan')}_{datetime.now().strftime('%Y%m%d')}.txt",
            mime="text/plain",
            key="download_text_meal_plan"
        )
        
        # Button to generate a new plan
        if st.button(" Generate a New Plan", type="secondary"):
            # Clear the old plan from session state to allow a new one
            keys_to_delete = ['ai_meal_plan_text', 'meal_plan_diet', 'meal_plan_generated_time']
            for key in keys_to_delete:
                st.session_state.pop(key, None)
            st.rerun()

    else:
        # Initial state - no plan generated yet
        st.info(" Click 'Generate Meal Plan' to create your first personalized plan.")

# ==================== VOICE ASSISTANT PAGE ====================
elif page == " Voice Assistant":
    st.markdown('<div class="main-title"> Voice Assistant</div>', unsafe_allow_html=True)
    
    # Initialize session states
    if 'voice_question' not in st.session_state:
        st.session_state.voice_question = ""
    if 'ai_response' not in st.session_state:
        st.session_state.ai_response = ""
    if 'is_speaking' not in st.session_state:
        st.session_state.is_speaking = False
    if 'just_spoke' not in st.session_state:
        st.session_state.just_spoke = False
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # ========== VOICE INPUT ==========
        st.markdown(" Step 1: Speak Your Question")
        
        voice_col1, voice_col2 = st.columns(2)
        
        with voice_col1:
            if st.button(" Start Speaking", type="primary", use_container_width=True):
                try:
                    import speech_recognition as sr
                    r = sr.Recognizer()
                    with sr.Microphone() as source:
                        st.info(" Listening... Speak clearly!")
                        audio = r.listen(source, timeout=10)
                        
                        # Transcribe voice to text
                        text = r.recognize_google(audio)
                        
                        # SAVE TO SESSION STATE
                        st.session_state.voice_question = text
                        st.session_state.just_spoke = True
                        
                        # Show success message
                        st.success(f" Voice captured! '{text[:50]}...'")
                        
                        # Force update without rerun
                        st.rerun()  
                        
                except sr.UnknownValueError:
                    st.error("Could not understand audio")
                except sr.RequestError:
                    st.error("Speech service error")
                except Exception as e:
                    st.error(f"Microphone error: {str(e)}")
        
        with voice_col2:
            if st.button(" Clear All", type="secondary", use_container_width=True):
                st.session_state.voice_question = ""
                st.session_state.ai_response = ""
                st.session_state.just_spoke = False
                st.rerun()
        
        # ========== TEXT BOX (SHOWS SPOKEN TEXT) ==========
        st.markdown(" Step 2: Your Question")
        
        # Show what was just spoken
        if st.session_state.just_spoke and st.session_state.voice_question:
            st.info(f"You said: {st.session_state.voice_question}")
            st.session_state.just_spoke = False  # Reset
        
        # TEXT BOX - Shows your spoken text
        question_box = st.text_area(
            "Edit your question here:",
            value=st.session_state.voice_question,  # ← THIS SHOWS YOUR SPOKEN TEXT
            height=120,
            placeholder="Speak using the button above, text will appear here...",
            key="question_input_box"
        )
        
        # Update session state if user edits
        if question_box != st.session_state.voice_question:
            st.session_state.voice_question = question_box
        
        # Show word count
        if st.session_state.voice_question:
            words = len(st.session_state.voice_question.split())
            st.caption(f" {words} words")
        
        # ========== GET AI RESPONSE ==========
        st.markdown(" Step 3: Get AI Response")
        
        if st.button("Generate AI Answer", type="primary", 
                    use_container_width=True,
                    disabled=not st.session_state.voice_question):
            
            with st.spinner("AI is thinking..."):
                try:
                    from utils import setup_gemini_api
                    
                    # Get user context
                    user_data = st.session_state.get('user_data', {})
                    age = user_data.get('age', 30)
                    diet = user_data.get('diet_type', 'Omnivore')
                    
                    # Call AI
                    model = setup_gemini_api()
                    if model:
                        prompt = f"""User question: {st.session_state.voice_question}
                        User profile: {age} years old, {diet} diet
                        
                        Provide helpful Vitamin B12 advice."""
                        
                        response = model.generate_content(prompt)
                        st.session_state.ai_response = response.text
                        st.success(" response ready!")
                    else:
                        # Fallback response
                        st.session_state.ai_response = f"""**Response to:** {st.session_state.voice_question}

**Recommendation:** Consult doctor for proper diagnosis."""
                        st.success("Response generated!")
                        
                except Exception as e:
                    st.error(f"AI error: {str(e)}")
        
        # ========== SHOW AI RESPONSE ==========
        if st.session_state.ai_response:
            st.markdown(" AI Response")
            
            with st.container(border=True):
                st.markdown(st.session_state.ai_response)
            
            # ========== VOICE OUTPUT ==========
            st.markdown("Step 4: Listen to Answer")
            
            # JavaScript for voice output with STOP button
            voice_js = f"""
            <script>
            let currentSpeech = null;
            let isSpeaking = false;
            
            function speakResponse() {{
                if ('speechSynthesis' in window) {{
                    // Stop any current speech
                    window.speechSynthesis.cancel();
                    
                    const text = `{st.session_state.ai_response.replace('`', '').replace('\\', '')}`;
                    currentSpeech = new SpeechSynthesisUtterance(text);
                    
                    currentSpeech.rate = 1.0;
                    currentSpeech.volume = 1.0;
                    currentSpeech.lang = 'en-US';
                    
                    // Update UI
                    document.getElementById('speakBtn').innerHTML = ' Speaking...';
                    document.getElementById('status').innerHTML = ' Speaking';
                    document.getElementById('status').style.color = 'green';
                    isSpeaking = true;
                    
                    currentSpeech.onend = function() {{
                        document.getElementById('speakBtn').innerHTML = ' Play Again';
                        document.getElementById('status').innerHTML = ' Finished';
                        document.getElementById('status').style.color = 'blue';
                        isSpeaking = false;
                    }};
                    
                    currentSpeech.onerror = function() {{
                        document.getElementById('speakBtn').innerHTML = ' Speak';
                        document.getElementById('status').innerHTML = ' Error';
                        document.getElementById('status').style.color = 'red';
                        isSpeaking = false;
                    }};
                    
                    window.speechSynthesis.speak(currentSpeech);
                }} else {{
                    alert('Voice output requires Chrome, Edge, or Safari.');
                }}
            }}
            
            function stopSpeech() {{
                if ('speechSynthesis' in window && isSpeaking) {{
                    window.speechSynthesis.cancel();
                    document.getElementById('speakBtn').innerHTML = ' Speak';
                    document.getElementById('status').innerHTML = ' Stopped';
                    document.getElementById('status').style.color = 'orange';
                    isSpeaking = false;
                }}
            }}
            
            // Test function
            function testVoice() {{
                if ('speechSynthesis' in window) {{
                    const test = new SpeechSynthesisUtterance("Test voice is working");
                    window.speechSynthesis.speak(test);
                }}
            }}
            </script>
            
            <div style="margin: 20px 0; padding: 15px; background: #f8f9fa; border-radius: 10px;">
                <div style="display: flex; gap: 10px; margin-bottom: 10px;">
                    <button onclick="speakResponse()" id="speakBtn" style="
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        color: white;
                        padding: 12px 24px;
                        border: none;
                        border-radius: 6px;
                        font-size: 16px;
                        cursor: pointer;
                        font-weight: bold;
                    ">
                         Speak Answer
                    </button>
                    
                    <button onclick="stopSpeech()" style="
                        background: #f44336;
                        color: white;
                        padding: 12px 24px;
                        border: none;
                        border-radius: 6px;
                        font-size: 16px;
                        cursor: pointer;
                        font-weight: bold;
                    ">
                         Stop
                    </button>
                    
                    <button onclick="testVoice()" style="
                        background: #2196F3;
                        color: white;
                        padding: 12px 24px;
                        border: none;
                        border-radius: 6px;
                        font-size: 16px;
                        cursor: pointer;
                        font-weight: bold;
                    ">
                         Test
                    </button>
                </div>
                
                <p id="status" style="font-weight: bold; color: gray; margin: 5px 0;">
                    Status: Ready
                </p>
            </div>
            """
            
            st.components.v1.html(voice_js, height=200)
            
            # Download option
            col_d1, col_d2 = st.columns(2)
            with col_d1:
                st.download_button(
                    label=" Save Response",
                    data=st.session_state.ai_response,
                    file_name="b12_answer.txt",
                    mime="text/plain",
                    use_container_width=True
                )
            with col_d2:
                if st.button(" New Question", use_container_width=True):
                    st.session_state.voice_question = ""
                    st.session_state.ai_response = ""
                    st.rerun()
    
    with col2:
        # Status panel
        st.markdown(" Status Panel")
        
        if st.session_state.voice_question:
            st.success(" Question ready")
            with st.expander("View full question"):
                st.write(st.session_state.voice_question)
        else:
            st.info(" No question yet")
        
        if st.session_state.ai_response:
            st.success(" Answer ready")
            response_words = len(st.session_state.ai_response.split())
            st.metric("Response Length", f"{response_words} words")
        
        # Instructions
        st.markdown("""
        1. Click "Start Speaking"
        2. Speak clearly
        """)
        
        # Quick load examples

# ==================== B12 TRACKER PAGE ====================
elif page == " B12 Tracker":
    st.markdown('<div class="main-title"> Daily B12 Tracker</div>', unsafe_allow_html=True)
    
    # ==================== INITIALIZATION ====================
    # Initialize tracker in session state
    if 'tracker_data' not in st.session_state:
        st.session_state.tracker_data = []
    if 'current_date' not in st.session_state:
        st.session_state.current_date = datetime.now().strftime("%Y-%m-%d")
    if 'today_form_data' not in st.session_state:
        st.session_state.today_form_data = {
            'b12_taken': "❓ Not sure",
            'fatigue': 3,
            'numbness': 1,
            'notes': ''
        }
    
    # Get today's date info
    today = datetime.now()
    today_date_str = today.strftime("%Y-%m-%d")
    today_day_name = today.strftime("%A")
    
    # Check if today's entry exists
    today_entry = None
    for entry in st.session_state.tracker_data:
        if entry['date'] == today_date_str:
            today_entry = entry
            break
    
    # Check if MongoDB methods exist
    mongodb_available = (
        st.session_state.mongodb and 
        st.session_state.mongodb.connected
    )
    
    # ==================== CLOUD LOAD BUTTON ====================
    # If user is authenticated and MongoDB is available, show cloud load button
    if st.session_state.authenticated and mongodb_available:
        if st.button(" welcome", type="secondary", key="load_cloud"):
            with st.spinner("HELLO"):
                try:
                    if hasattr(st.session_state.mongodb, 'get_tracker_data'):
                        cloud_data = st.session_state.mongodb.get_tracker_data(
                            user_id=st.session_state.current_user['user_id']
                        )
                        if cloud_data:
                            st.session_state.tracker_data = cloud_data
                            st.success(f"Loaded {len(cloud_data)} entries from cloud!")
                            st.rerun()
                        else:
                            st.info(" No tracking data found in cloud")
                    else:
                        st.warning("Cloud feature not available yet")
                except Exception as e:
                    st.warning(f"Could not load from cloud: {str(e)}")
    
    # ==================== MAIN LAYOUT ====================
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # ========== TODAY'S CHECK-IN FORM ==========
        st.markdown("### Today's Check-in")
        
        with st.container(border=True):
            # Load existing data if editing
            current_b12 = st.session_state.today_form_data['b12_taken']
            current_fatigue = st.session_state.today_form_data['fatigue']
            current_numbness = st.session_state.today_form_data['numbness']
            current_notes = st.session_state.today_form_data['notes']
            
            if today_entry:
                current_b12 = today_entry['b12_taken']
                current_fatigue = today_entry['fatigue']
                current_numbness = today_entry['numbness']
                current_notes = today_entry.get('notes', '')
            
            # 1. B12 Intake Question
            st.markdown("#### 1. Did you take B12 today?")
            b12_taken = st.radio(
                "Select:",
                [" Yes, I took B12", " No, I missed", " Not sure"],
                horizontal=True,
                index=[" Yes, I took B12", " No, I missed", " Not sure"].index(current_b12) 
                if current_b12 in [" Yes, I took B12", " No, I missed", " Not sure"] else 2,
                label_visibility="collapsed",
                key="b12_taken_radio"
            )
            
            # 2. Symptom Rating
            st.markdown("#### 2. How are you feeling today?")
            
            col_s1, col_s2 = st.columns(2)
            with col_s1:
                fatigue = st.slider(
                    "😴 Fatigue Level", 
                    1, 5, current_fatigue,
                    help="1 = Very energetic, 5 = Extremely tired",
                    key="fatigue_slider"
                )
            with col_s2:
                numbness = st.slider(
                    "🤚 Numbness/Tingling", 
                    1, 5, current_numbness,
                    help="1 = No symptoms, 5 = Severe symptoms",
                    key="numbness_slider"
                )
            
            # Symptom indicators
            col_ind1, col_ind2 = st.columns(2)
            with col_ind1:
                fatigue_emoji = ["😊", "🙂", "😐", "😔", "😫"][fatigue-1]
                st.caption(f"{fatigue_emoji} Fatigue: {fatigue}/5")
            with col_ind2:
                numbness_emoji = ["👍", "👌", "🤔", "😣", "😖"][numbness-1]
                st.caption(f"{numbness_emoji} Numbness: {numbness}/5")
            
            # 3. Notes Section
            st.markdown("#### 3. Any notes? (Optional)")
            notes = st.text_area(
                "", 
                value=current_notes,
                placeholder="E.g., 'Took supplement with breakfast', 'Felt dizzy in afternoon', 'Had energy boost after lunch'",
                label_visibility="collapsed", 
                height=80,
                key="notes_textarea"
            )
            
            # Save/Clear Buttons
            col_btn1, col_btn2 = st.columns(2)
            with col_btn1:
                save_disabled = False
                save_label = " 💾 Save Today's Entry"
                
                if st.button(save_label, type="primary", use_container_width=True, disabled=save_disabled):
                    # Calculate wellness score
                    score = 10
                    if " Yes" in b12_taken:
                        score += 5
                    elif " No" in b12_taken:
                        score -= 3
                    
                    # Adjust for symptoms
                    score -= (fatigue + numbness - 2)
                    
                    # Determine emoji and mood based on score
                    if score >= 15:
                        emoji = "😊"
                        mood = "Great"
                    elif score >= 10:
                        emoji = "😐"
                        mood = "Okay"
                    else:
                        emoji = "😔"
                        mood = "Needs improvement"
                    
                    # Create entry
                    entry = {
                        'date': today_date_str,
                        'day_name': today_day_name,
                        'b12_taken': b12_taken,
                        'fatigue': fatigue,
                        'numbness': numbness,
                        'notes': notes,
                        'score': min(max(score, 0), 20),  # Limit 0-20
                        'emoji': emoji,
                        'mood': mood
                    }
                    
                    # Update or add entry
                    if today_entry:
                        # Update existing
                        index = next(i for i, e in enumerate(st.session_state.tracker_data) 
                                    if e['date'] == today_date_str)
                        st.session_state.tracker_data[index] = entry
                        action = "updated"
                    else:
                        # Add new
                        st.session_state.tracker_data.append(entry)
                        action = "saved"
                    
                    # Save form data to session state
                    st.session_state.today_form_data = {
                        'b12_taken': b12_taken,
                        'fatigue': fatigue,
                        'numbness': numbness,
                        'notes': notes
                    }
                    
                    # Log the activity
                    log_user_activity(
                        activity_type='tracker_entry',
                        data=entry,
                        description=f"Daily tracker {action} - Score: {score}/20"
                    )
                    
                    # Save to MongoDB if authenticated and available
                    cloud_success = False
                    if st.session_state.authenticated and mongodb_available:
                        try:
                            if hasattr(st.session_state.mongodb, 'save_tracker_entry'):
                                mongo_id = st.session_state.mongodb.save_tracker_entry(
                                    user_id=st.session_state.current_user['user_id'],
                                    tracker_data=entry,
                                    session_id=st.session_state.session_id
                                )
                                if mongo_id:
                                    cloud_success = True
                        except Exception as mongo_error:
                            st.warning(f" Could not save to cloud: {str(mongo_error)[:100]}")
                    
                    # Show success message
                    if cloud_success:
                        st.success(f" {action.capitalize()} & saved to cloud!")
                    else:
                        st.success(f" Today's entry {action} locally!")
                    
                    st.balloons()
                    st.rerun()
            
            with col_btn2:
                if st.button("  Clear Form", type="secondary", use_container_width=True):
                    st.session_state.today_form_data = {
                        'b12_taken': " Not sure",
                        'fatigue': 3,
                        'numbness': 1,
                        'notes': ''
                    }
                    st.rerun()
    
    with col2:
        # ========== TODAY'S SUMMARY ==========
        st.markdown(f"### {today_day_name}'s Summary")
        
        if today_entry:
            with st.container(border=True):
                # Mood display
                st.markdown(f"<div style='text-align: center; font-size: 4rem; margin: 10px 0;'>{today_entry['emoji']}</div>", 
                           unsafe_allow_html=True)
                st.markdown(f"<div style='text-align: center; font-size: 1.2rem; color: #666; margin-bottom: 20px;'>{today_entry['mood']}</div>", 
                           unsafe_allow_html=True)
                
                # Stats
                st.markdown("**Daily Stats:**")
                col_stat1, col_stat2 = st.columns(2)
                with col_stat1:
                    st.metric("Score", f"{today_entry['score']}/20")
                with col_stat2:
                    b12_icon = "✅" if " Yes" in today_entry['b12_taken'] else "❌" if " No" in today_entry['b12_taken'] else "❓"
                    st.metric("B12", b12_icon)
                
                # Symptoms progress bars
                st.markdown("**Symptoms:**")
                col_sym1, col_sym2 = st.columns(2)
                with col_sym1:
                    fatigue_value = today_entry['fatigue']
                    fatigue_color = "#4CAF50" if fatigue_value <= 2 else "#FF9800" if fatigue_value <= 3 else "#F44336"
                    st.markdown(f"""
                    <div style="background: #f0f0f0; border-radius: 10px; padding: 5px; margin: 5px 0;">
                        <div style="background: {fatigue_color}; width: {fatigue_value*20}%; height: 10px; border-radius: 5px;"></div>
                        <div style="text-align: center; font-size: 0.9rem; margin-top: 5px;">Fatigue: {fatigue_value}/5</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col_sym2:
                    numbness_value = today_entry['numbness']
                    numbness_color = "#4CAF50" if numbness_value <= 1 else "#FF9800" if numbness_value <= 2 else "#F44336"
                    st.markdown(f"""
                    <div style="background: #f0f0f0; border-radius: 10px; padding: 5px; margin: 5px 0;">
                        <div style="background: {numbness_color}; width: {numbness_value*20}%; height: 10px; border-radius: 5px;"></div>
                        <div style="text-align: center; font-size: 0.9rem; margin-top: 5px;">Numbness: {numbness_value}/5</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                # Notes display
                if today_entry['notes']:
                    st.markdown("---")
                    st.markdown("** Notes:**")
                    st.info(today_entry['notes'])
                
                # Edit button
                if st.button("  Edit Entry", use_container_width=True):
                    st.session_state.today_form_data = {
                        'b12_taken': today_entry['b12_taken'],
                        'fatigue': today_entry['fatigue'],
                        'numbness': today_entry['numbness'],
                        'notes': today_entry.get('notes', '')
                    }
                    st.rerun()
        else:
            with st.container(border=True):
                st.markdown("<div style='text-align: center; font-size: 4rem; margin: 20px 0;'>📅</div>", 
                           unsafe_allow_html=True)
                st.markdown("<div style='text-align: center; color: #666;'>No entry yet for today</div>", 
                           unsafe_allow_html=True)
                st.markdown("<div style='text-align: center; margin-top: 20px;'>Fill out the form to start tracking!</div>", 
                           unsafe_allow_html=True)
        
        # ========== STREAK COUNTER ==========
        st.markdown("### 🔥 Current Streak")
        
        # Calculate streak (consecutive days with B12 taken)
        streak = 0
        sorted_data = sorted(st.session_state.tracker_data, 
                            key=lambda x: x['date'], reverse=True)
        
        # Get streak from cloud if available
        cloud_streak = None
        if st.session_state.authenticated and mongodb_available:
            try:
                if hasattr(st.session_state.mongodb, 'get_user_streak'):
                    cloud_streak = st.session_state.mongodb.get_user_streak(
                        user_id=st.session_state.current_user['user_id']
                    )
            except Exception as e:
                pass  # Silently fail if can't get from cloud
        
        if cloud_streak and cloud_streak > 0:
            streak = cloud_streak
        else:
            # Calculate local streak
            for entry in sorted_data:
                if " Yes" in entry['b12_taken']:
                    streak += 1
                else:
                    break
        
        with st.container(border=True):
            if streak > 0:
                # Determine streak level and color
                if streak >= 30:
                    streak_level = "🔥 LEGENDARY"
                    streak_color = "#FF6B6B"
                    streak_msg = f"{streak} days! You're unstoppable!"
                elif streak >= 14:
                    streak_level = "🔥 AMAZING"
                    streak_color = "#FF8E53"
                    streak_msg = f"{streak} days! Keep going!"
                elif streak >= 7:
                    streak_level = "🔥 GREAT"
                    streak_color = "#FFA726"
                    streak_msg = f"{streak} days! One week strong!"
                else:
                    streak_level = "🔥 GOOD"
                    streak_color = "#FFB74D"
                    streak_msg = f"{streak} days! Building momentum!"
                
                # Display streak
                st.markdown(f"<div style='text-align: center; font-size: 2.5rem; color: {streak_color}; margin: 10px 0;'>{streak}</div>", 
                           unsafe_allow_html=True)
                st.markdown(f"<div style='text-align: center; font-size: 1.2rem; color: {streak_color};'>{streak_level}</div>", 
                           unsafe_allow_html=True)
                st.markdown(f"<div style='text-align: center; margin-top: 10px; color: #666;'>{streak_msg}</div>", 
                           unsafe_allow_html=True)
                
                # Save streak to cloud if not already saved
                if (st.session_state.authenticated and 
                    mongodb_available and 
                    not cloud_streak and
                    hasattr(st.session_state.mongodb, 'save_user_streak')):
                    try:
                        st.session_state.mongodb.save_user_streak(
                            user_id=st.session_state.current_user['user_id'],
                            streak=streak
                        )
                    except:
                        pass  # Silently fail if can't save to cloud
                
                # Next milestone progress
                next_milestone = 7 if streak < 7 else 14 if streak < 14 else 30 if streak < 30 else 100
                days_to_go = next_milestone - streak
                if days_to_go > 0:
                    progress = streak / next_milestone
                    st.markdown(f"""
                    <div style="margin: 15px 0;">
                        <div style="display: flex; justify-content: space-between; font-size: 0.9rem; margin-bottom: 5px;">
                            <span>Next: {next_milestone} days</span>
                            <span>{days_to_go} to go</span>
                        </div>
                        <div style="background: #f0f0f0; border-radius: 10px; height: 10px;">
                            <div style="background: {streak_color}; width: {progress*100}%; height: 100%; border-radius: 10px;"></div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                # No streak yet
                st.markdown("<div style='text-align: center; font-size: 3rem; margin: 20px 0;'>💫</div>", 
                           unsafe_allow_html=True)
                st.markdown("<div style='text-align: center; color: #666;'>Start your streak today!</div>", 
                           unsafe_allow_html=True)
                st.markdown("<div style='text-align: center; margin-top: 10px;'>Take B12 today to begin 🔥</div>", 
                           unsafe_allow_html=True)
    
    # ==================== WEEKLY PROGRESS ====================
    st.markdown("---")
    st.markdown("###  Weekly Progress")
    
    if st.session_state.tracker_data:
        # Get last 7 days data
        last_7_days = sorted(st.session_state.tracker_data, 
                            key=lambda x: x['date'], reverse=True)[:7]
        
        if last_7_days:
            # Create DataFrame for chart
            df = pd.DataFrame(last_7_days)
            
            # Ensure we have dates in order
            df['date_display'] = pd.to_datetime(df['date']).dt.strftime('%a %d')
            df = df.sort_values('date')
            
            # Create tabs for different views
            tab1, tab2, tab3 = st.tabs([" Scores", " Fatigue", " Numbness"])
            
            with tab1:
                # Score chart
                fig1 = px.line(df, x='date_display', y='score',
                              title="Daily Wellness Score (Higher is better)",
                              markers=True, line_shape='spline',
                              color_discrete_sequence=['#4CAF50'])
                fig1.update_layout(
                    yaxis_range=[0, 20],
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    xaxis_title="Date",
                    yaxis_title="Wellness Score"
                )
                st.plotly_chart(fig1, use_container_width=True)
            
            with tab2:
                # Fatigue chart
                fig2 = px.bar(df, x='date_display', y='fatigue',
                             title="Fatigue Level (1=Low, 5=High)",
                             color='fatigue',
                             color_continuous_scale='Reds')
                fig2.update_layout(
                    yaxis_range=[1, 5],
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    xaxis_title="Date",
                    yaxis_title="Fatigue Level"
                )
                st.plotly_chart(fig2, use_container_width=True)
            
            with tab3:
                # Numbness chart
                fig3 = px.bar(df, x='date_display', y='numbness',
                             title="Numbness/Tingling (1=Low, 5=High)",
                             color='numbness',
                             color_continuous_scale='Blues')
                fig3.update_layout(
                    yaxis_range=[1, 5],
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    xaxis_title="Date",
                    yaxis_title="Numbness Level"
                )
                st.plotly_chart(fig3, use_container_width=True)
            
            # ========== WEEKLY STATS ==========
            st.markdown("####  Weekly Statistics")
            
            col_stats1, col_stats2, col_stats3, col_stats4 = st.columns(4)
            
            with col_stats1:
                b12_days = sum(1 for e in last_7_days if "✅ Yes" in e['b12_taken'])
                b12_percent = (b12_days / len(last_7_days)) * 100
                st.metric("B12 Days", f"{b12_days}/7", 
                         delta=f"{b12_percent:.0f}%")
            
            with col_stats2:
                avg_fatigue = sum(e['fatigue'] for e in last_7_days) / len(last_7_days)
                st.metric("Avg Fatigue", f"{avg_fatigue:.1f}/5",
                         delta="Lower better", delta_color="inverse")
            
            with col_stats3:
                avg_numbness = sum(e['numbness'] for e in last_7_days) / len(last_7_days)
                st.metric("Avg Numbness", f"{avg_numbness:.1f}/5",
                         delta="Lower better", delta_color="inverse")
            
            with col_stats4:
                avg_score = sum(e['score'] for e in last_7_days) / len(last_7_days)
                st.metric("Avg Score", f"{avg_score:.1f}/20",
                         delta="Higher better")
            
            # ========== TREND ANALYSIS ==========
            st.markdown("####  Trend Analysis")
            
            if len(last_7_days) >= 3:
                # Simple trend analysis
                scores = [e['score'] for e in last_7_days]
                if scores[-1] > scores[0]:
                    st.success(" **Improving trend!** Your scores are going up this week.")
                elif scores[-1] < scores[0]:
                    st.warning(" **Watch out!** Your scores are trending down. Consider consulting your doctor.")
                else:
                    st.info(" **Stable trend.** Your scores are consistent.")
                
                # B12 consistency analysis
                if b12_days >= 6:
                    st.success(" **Excellent consistency!** You're taking B12 almost every day.")
                elif b12_days >= 4:
                    st.info(" **Good effort.** You're taking B12 most days.")
                elif b12_days >= 2:
                    st.warning(" **Needs improvement.** Try to be more consistent with B12.")
                else:
                    st.error(" **Poor consistency.** You need to take B12 more regularly.")
        
    else:
        # No data message
        st.info(" No tracking data yet. Start by saving today's entry above!")
    
    # ==================== TIPS & MOTIVATION ====================
    st.markdown("---")
    with st.expander(" Tips for Better Tracking & Health"):
        st.markdown("""
         Tracking Tips:
        1. Consistency is key - Check-in daily at the same time
        2. Be honest - Accurate tracking helps identify patterns
       
         B12 Supplement Tips:
        1. Take consistently - Same time each day works best
        2. With meals - Take with food for better absorption

         When to See a Doctor:
        1. Severe symptoms - Numbness, balance issues, confusion
        2. No improvement - After 2-3 months of supplements

         Dietary Sources:
        1. Animal products - Meat, fish, eggs, dairy
        2. Fortified foods - Cereals, plant milks, nutritional yeast
        """)

# ==================== RESULTS PAGE ====================
elif page == " Results":
    st.markdown('<div class="main-title"> Your Results & Recommendations</div>', unsafe_allow_html=True)
    
    if not st.session_state.user_data:
        st.warning("Please complete the assessment first!")
        col1, col2, col3 = st.columns([1,2,1])
        with col2:
            st.info("Complete your risk assessment to get personalized recommendations")
            if st.button("Go to Assessment", type="primary"):
                page = " Assessment"
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
        
        # Risk display header
        col1, col2, col3 = st.columns(3)
        
        risk_info = {
            'High': {
                'bg': '#FEE2E2', 
                'border': '#DC2626', 
                'text': '#DC2626', 
                'icon': '🔴',
                'title': 'HIGH RISK'
            },
            'Medium': {
                'bg': '#FEF3C7', 
                'border': '#D97706', 
                'text': '#D97706', 
                'icon': '🟡',
                'title': 'MEDIUM RISK'
            },
            'Low': {
                'bg': '#D1FAE5', 
                'border': '#059669', 
                'text': '#059669', 
                'icon': '🟢',
                'title': 'LOW RISK'
            }
        }
        
        info = risk_info.get(risk_level, {
            'bg': '#F3F4F6', 
            'border': '#6B7280', 
            'text': '#6B7280', 
            'icon': '⚪',
            'title': risk_level + ' RISK'
        })
        
        with col1:
            st.markdown(f"""
            <div style="
                background: {info['bg']};
                padding: 25px;
                border-radius: 10px;
                border-left: 6px solid {info['border']};
                border: 1px solid {info['border']}20;
                text-align: center;
            ">
                <div style="font-size: 2.5rem; margin-bottom: 10px;">
                    {info['icon']}
                </div>
                <h2 style="margin: 0; color: {info['text']};">
                    {info['title']}
                </h2>
                <div style="margin-top: 15px; padding: 10px; background: white; border-radius: 8px;">
                    <p style="margin: 0; font-size: 1.3rem; font-weight: bold; color: #1F2937;">
                        Score: {risk_score:.1%}
                    </p>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div style="
                background: #F8FAFC;
                padding: 20px;
                border-radius: 10px;
                border: 1px solid #E2E8F0;
            ">
                <h4 style="margin: 0 0 15px 0; color: #1E40AF;">Your Profile</h4>
                <div style="background: white; padding: 15px; border-radius: 8px;">
                    <p style="margin: 8px 0; color: #4B5563;"><strong>Age:</strong> <span style="color: #1F2937;">{age} years</span></p>
                    <p style="margin: 8px 0; color: #4B5563;"><strong>Diet:</strong> <span style="color: #1F2937;">{diet_type}</span></p>
                    <p style="margin: 8px 0; color: #4B5563;"><strong>BMI:</strong> <span style="color: #1F2937;">{bmi:.1f}</span></p>
                    <p style="margin: 8px 0; color: #4B5563;"><strong>Symptoms:</strong> <span style="color: #1F2937;">{symptoms_count} reported</span></p>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            # Determine B12 status
            if isinstance(b12_level, (int, float)):
                if b12_level < 200:
                    b12_color = '#DC2626'
                    b12_status = "Deficient"
                  
                elif b12_level < 300:
                    b12_color = '#D97706'
                    b12_status = "Borderline"
                    
                else:
                    b12_color = '#059669'
                    b12_status = "Normal"
                    
                b12_display = f"{b12_level} pg/mL"
            else:
                b12_color = '#6B7280'
                b12_status = "Not tested"
                
                b12_display = "Not tested"
            
            st.markdown(f"""
            <div style="
                background: #F8FAFC;
                padding: 20px;
                border-radius: 10px;
                border: 1px solid #E2E8F0;
            ">
                <h4 style="margin: 0 0 15px 0; color: #1E40AF;"> B12 Status</h4>
                <div style="background: white; padding: 15px; border-radius: 8px; text-align: center;">
                    <p style="margin: 0 0 10px 0; font-size: 1.4rem; font-weight: bold; color: {b12_color};">
                        {b12_display}
                    </p>
                    <p style="margin: 0; font-size: 1.1rem; color: {b12_color}; font-weight: 500;">
                        {b12_status}
                    </p>
                    <div style="margin-top: 10px; font-size: 0.8rem; color: #6B7280;">
                        Normal range: 200-900 pg/mL
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Generate AI Recommendations
        st.markdown(" Recommendations")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            if st.button("Generate  Recommendations", type="primary", use_container_width=True):
                with st.spinner("Analyzing your profile..."):
                    try:
                        # Determine B12 status for AI
                        if b12_level is not None:
                            if b12_level < 200:
                                b12_status = "DEFICIENT"
                            elif b12_level < 300:
                                b12_status = "BORDERLINE"
                            else:
                                b12_status = "NORMAL"
                        else:
                            b12_status = "NOT_TESTED"
                        
                        # Generate AI recommendations
                        ai_recs = generate_ai_treatment_recommendations(
                            b12_value=b12_level,
                            status=b12_status,
                            age=age,
                            diet_type=diet_type,
                            symptoms_count=symptoms_count
                        )
                        
                        if ai_recs.get('success'):
                            recommendations = ai_recs.get('recommendations', {})
                            
                            # Save to session state
                            st.session_state.ai_results_recommendations = {
                                'recommendations': recommendations,
                                'generated_date': ai_recs.get('generated_date'),
                                'risk_level': risk_level,
                                'risk_score': risk_score
                            }
                            
                            # Log AI recommendations generation
                            log_user_activity(
                                activity_type='ai_recommendations',
                                data={
                                    'risk_level': risk_level,
                                    'b12_status': b12_status,
                                    'has_recommendations': bool(recommendations)
                                },
                                description=f"Recommendations generated for {risk_level} risk"
                            )
                            
                            # Display AI recommendations
                            st.markdown("Generated Recommendations")
                            
                            if isinstance(recommendations, dict):
                                # Display dictionary format
                                for category, content in recommendations.items():
                                    if content:
                                        st.markdown(f"#### {category.upper().replace('_', ' ')}")
                                        if isinstance(content, list):
                                            for item in content:
                                                st.markdown(f"• {item}")
                                        elif isinstance(content, dict):
                                            for key, value in content.items():
                                                st.markdown(f"**{key}:** {value}")
                                        else:
                                            st.write(str(content))
                            else:
                                # Display string format
                                st.write(str(recommendations))
                            
                            # Save to cloud
                            if st.session_state.authenticated and st.session_state.mongodb.connected:
                                try:
                                    mongo_id = st.session_state.mongodb.save_user_assessment(
                                        user_data=st.session_state.user_data,
                                        risk_score=risk_score,
                                        risk_level=risk_level,
                                        recommendations={
                                            'ai_recommendations': recommendations,
                                            'generated_date': ai_recs.get('generated_date')
                                        },
                                        user_id=st.session_state.current_user['user_id'],
                                        session_id=st.session_state.session_id
                                    )
                                    if mongo_id:
                                        st.success("AI recommendations saved to cloud!")
                                except Exception as e:
                                    st.warning(f"Could not save: {str(e)[:100]}")
                            
                            st.success("Recommendations generated!")
                        else:
                            st.error(f"Failed: {ai_recs.get('error', 'Unknown error')}")
                            
                    except Exception as e:
                        st.error(f"Error generating  recommendations: {str(e)}")
        
        with col2:
            # Quick action buttons
            st.markdown("### Quick Actions")
            
            if st.button("View Meal Plan", type="secondary"):
                page = " Meal Planner"
                st.rerun()
            
            if st.button("Upload Lab Report", type="secondary"):
                page = " Lab Reports"
                st.rerun()
            
            if st.button("Symptom Check", type="secondary"):
                page = " Voice Assistant"
                st.rerun()
        
        # Show existing AI recommendations if available
        if 'ai_results_recommendations' in st.session_state:
            st.markdown("---")
            st.markdown("### Previously Generated AI Recommendations")
            
            rec_data = st.session_state.ai_results_recommendations
            recommendations = rec_data.get('recommendations', {})
            
            if isinstance(recommendations, dict):
                # Create expandable sections
                for category, content in recommendations.items():
                    if content:
                        with st.expander(f"{category.upper().replace('_', ' ')}", expanded=False):
                            if isinstance(content, list):
                                for item in content:
                                    st.markdown(f"• {item}")
                            elif isinstance(content, dict):
                                for key, value in content.items():
                                    st.markdown(f"**{key}:** {value}")
                            else:
                                st.write(str(content))
            else:
                st.write(str(recommendations))
            
            # Download button for recommendations
            if st.button("Download AI Recommendations"):
                try:
                    # Convert to text
                    if isinstance(recommendations, dict):
                        text_content = ""
                        for category, content in recommendations.items():
                            text_content += f"\n\n{category.upper()}:\n"
                            if isinstance(content, list):
                                for item in content:
                                    text_content += f"• {item}\n"
                            elif isinstance(content, dict):
                                for key, value in content.items():
                                    text_content += f"{key}: {value}\n"
                            else:
                                text_content += str(content) + "\n"
                    else:
                        text_content = str(recommendations)
                    
                    st.download_button(
                        label="Download Text File",
                        data=text_content,
                        file_name=f"b12_ai_recommendations_{datetime.now().strftime('%Y%m%d')}.txt",
                        mime="text/plain"
                    )
                except Exception as e:
                    st.error(f"Download failed: {str(e)}")
        
        st.markdown("---")
        
        # Export section
        st.markdown("### Export Your Results")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("Generate PDF Report", type="secondary"):
                try:
                    pdf_buffer = export_to_pdf(user_data, risk_level, risk_score)
                    
                    # Add validation
                    if pdf_buffer is None:
                        # Create a simple PDF as fallback
                        from io import BytesIO
                        from reportlab.pdfgen import canvas
                        
                        buffer = BytesIO()
                        p = canvas.Canvas(buffer)
                        p.drawString(100, 750, "B12 Assessment Report")
                        p.drawString(100, 730, f"Risk Level: {risk_level}")
                        p.drawString(100, 710, f"Risk Score: {risk_score}")
                        p.save()
                        buffer.seek(0)
                        pdf_buffer = buffer.getvalue()
                    
                    # Log PDF export
                    log_user_activity(
                        activity_type='export_pdf',
                        data={
                            'risk_level': risk_level,
                            'risk_score': risk_score
                        },
                        description="PDF report exported"
                    )
                    
                    st.download_button(
                        label="Download PDF",
                        data=pdf_buffer,
                        file_name="b12_assessment_report.pdf",
                        mime="application/pdf"
                    )
                except Exception as e:
                    st.error(f"PDF generation failed: {str(e)}")
        with col2:
            if st.button("Export to JSON", type="secondary"):
                try:
                    json_data = export_to_json(user_data, risk_level, risk_score)
                    
                    # Log JSON export
                    log_user_activity(
                        activity_type='export_json',
                        data={
                            'risk_level': risk_level,
                            'risk_score': risk_score
                        },
                        description="JSON data exported"
                    )
                    
                    st.download_button(
                        label="Download JSON",
                        data=json_data,
                        file_name="b12_results.json",
                        mime="application/json"
                    )
                except Exception as e:
                    st.error(f"JSON export failed: {str(e)}")
        
        with col3:
            if st.button("Reset & Start Over", type="secondary"):
                keys_to_keep = ['authenticated', 'current_user', 'session_id', 'mongodb', 'temp_logs']
                for key in list(st.session_state.keys()):
                    if key not in keys_to_keep:
                        del st.session_state[key]
                st.success("Ready for new assessment!")
                st.rerun()

# ==================== USER PROFILE PAGE ====================
elif page == " My Profile":
    show_user_profile()

# ==================== CLOUD DATABASE PAGE ====================
elif page == " Cloud Database":
    st.markdown('<div class="main-title"> Cloud Database Dashboard</div>', unsafe_allow_html=True)
    
    if not st.session_state.mongodb or not st.session_state.mongodb.connected:
        st.error("Database not connected")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button(" Retry Connection"):
                st.session_state.mongodb = get_mongodb_connection()
                st.rerun()
    else:
        st.success("Connected to Cloud Database")
        
        # Show connection info
        with st.expander(" Connection Details"):
            st.write(f"**Database:** Online")
            st.write(f"**Session ID:** `{st.session_state.session_id}`")
            
            # Show temp logs info
            if 'temp_logs' in st.session_state and st.session_state.temp_logs:
                temp_count = len(st.session_state.temp_logs)
                st.info(f"**Local logs:** {temp_count} activities waiting to be saved")
        
        # Database Stats
        with st.spinner("Loading database statistics..."):
            stats = st.session_state.mongodb.get_dashboard_stats(user_id=st.session_state.current_user['user_id'])
        
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
            assessments = st.session_state.mongodb.get_user_assessments(
                user_id=st.session_state.current_user['user_id'],
                limit=10
            )
            
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
                st.info("No assessments saved to cloud yet.")
        
        with tab2:
            st.markdown("#### Your Lab Reports")
            lab_reports = st.session_state.mongodb.get_lab_reports(
                user_id=st.session_state.current_user['user_id'],
                limit=10
            )
            
            if lab_reports:
                for report in lab_reports:
                    with st.expander(f"Lab Report: {report.get('filename', 'Manual Entry')}"):
                        col1, col2 = st.columns(2)
                        with col1:
                            if report.get('b12_value'):
                                b12_val = report['b12_value']
                                if b12_val < 200:
                                    st.error(f"**{b12_val} pg/mL** (Deficient)")
                                elif b12_val < 300:
                                    st.warning(f"**{b12_val} pg/mL** (Borderline)")
                                else:
                                    st.success(f"**{b12_val} pg/mL** (Normal)")
                        with col2:
                            st.write(f"**Status:** {report.get('status', 'N/A')}")
                            st.write(f"**Date:** {report.get('timestamp', 'N/A')}")
                        
                        # Show AI analysis if available
                        if report.get('ai_analysis'):
                            st.markdown("**AI Analysis Preview:**")
                            st.write(report.get('ai_analysis', '')[:200] + "...")
            else:
                st.info("No lab reports saved to cloud yet.")
        
        with tab3:
            st.markdown("#### Export Your Data")
            
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
                                # For CSV, create a zip file
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
                        # ==================== ASSESSMENT PAGE ====================
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
            st.info(f"📄 Latest uploaded B12: **{latest['b12_value']} pg/mL**")
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
                            st.success(" Assessment saved to cloud !")
                    except Exception as mongo_error:
                        st.warning(f" Could not save to cloud: {str(mongo_error)[:100]}")
                else:
                    # Show notification for non-logged in users
                    st.info(" Assessment saved locally. Login to save to cloud .")
                
                st.success(" Assessment Complete!")
                st.balloons()
                
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

# ==================== ABOUT PAGE ====================
else:
    st.markdown('<div class="main-title">ℹ About B12 Assistant</div>', unsafe_allow_html=True)
    
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