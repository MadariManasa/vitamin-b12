# utils.py - UPDATED VERSION
import pandas as pd
import numpy as np
from datetime import datetime
import re
import pdfplumber
import easyocr
from PIL import Image
import pickle
import json
import os
import random
import google.generativeai as genai
import io
import streamlit as st

# ==================== GEMINI API CONFIGURATION ====================

GEMINI_API_KEY = "AIzaSyCL8Ytb9AmsThmsPTgGgdVzdorN_-UABkg"

def setup_gemini_api():
    """Setup Gemini API configuration with correct model name"""
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        
        # First, let's see what models are actually available
        print("🔍 Checking available models...")
        models = genai.list_models()
        
        available_models = []
        for model in models:
            if 'generateContent' in model.supported_generation_methods:
                model_name = model.name
                available_models.append(model_name)
                print(f"  ✅ Found: {model_name}")
        
        print(f"📊 Total available models: {len(available_models)}")
        
        # Try each available model
        for model_name in available_models:
            try:
                print(f"  Testing model: {model_name}")
                # Create model with the full name
                model = genai.GenerativeModel(model_name)
                # Quick test
                test_response = model.generate_content("Hello")
                print(f"  ✅ Model {model_name} works!")
                return model
            except Exception as e:
                print(f"  ❌ Model {model_name} failed: {str(e)[:100]}")
                continue
        
        print("❌ No working models found")
        return None
                
    except Exception as e:
        print(f"❌ Gemini API Error: {e}")
        return None
# ==================== GEMINI API FUNCTIONS ====================

def generate_meal_plan_with_gemini(diet_type, risk_level, age, preferences=""):
    """Generate personalized meal plan using Gemini API"""
    
    model = setup_gemini_api()
    if not model:
        return {
            "success": False,
            "error": "API not configured",
            "meal_plan": "Please add your Gemini API key to enable this feature."
        }
    
    prompt = f"""
    Create a detailed 7-day B12-focused meal plan for:
    
    DIET: {diet_type}
    RISK LEVEL: {risk_level}
    AGE: {age} years
    
    Include for each day:
    1. Breakfast (with B12 estimate)
    2. Lunch (with B12 estimate)  
    3. Dinner (with B12 estimate)
    4. 2 Snacks (with B12 estimate)
    5. Total daily B12
    
    Add:
    - Weekly shopping list
    - Cooking tips
    - B12-rich food suggestions
    
    Format clearly with headings.
    """
    
    try:
        response = model.generate_content(prompt)
        return {
            "success": True,
            "meal_plan": response.text,
            "generated_date": datetime.now().strftime("%Y-%m-%d %H:%M")
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

def analyze_lab_pdf_with_gemini(pdf_file):
    """Extract text from PDF and analyze with Gemini"""
    
    # First extract text
    text = extract_text_from_pdf(pdf_file)
    if not text:
        return {"error": "No text extracted from PDF"}
    
    model = setup_gemini_api()
    if not model:
        return {
            "success": False,
            "error": "API not configured",
            "analysis": "Add Gemini API key to analyze lab reports."
        }
    
    prompt = f"""
    Analyze this lab report for B12 deficiency:
    
    {text[:1500]}...
    
    Extract:
    1. Vitamin B12 level (pg/mL or pmol/L)
    2. Deficiency status (Severe/Moderate/Borderline/Normal)
    3. Recommendations
    4. Other relevant markers
    
    Format response clearly.
    """
    
    try:
        response = model.generate_content(prompt)
        
        # Also extract B12 value with regex
        b12_value = extract_b12_value(text)
        
        return {
            "success": True,
            "analysis": response.text,
            "b12_value": b12_value,
            "text_preview": text[:500],
            "generated_date": datetime.now().strftime("%Y-%m-%d %H:%M")
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

def generate_ai_treatment_recommendations(b12_value, status, age, diet_type, symptoms_count=0):
    """Generate AI treatment recommendations using Gemini"""
    
    model = setup_gemini_api()
    if not model:
        return {
            "success": False,
            "error": "API not configured",
            "recommendations": "Add Gemini API key for AI recommendations."
        }
    
    prompt = f"""
    As a medical AI specializing in Vitamin B12 deficiency, provide personalized treatment recommendations.
    
    PATIENT PROFILE:
    - B12 Level: {b12_value} pg/mL
    - Status: {status}
    - Age: {age} years
    - Diet: {diet_type}
    - Symptoms: {symptoms_count} reported
    
    Provide comprehensive recommendations.
    
    Focus on:
    1. Immediate actions
    2. Supplement plan
    3. Diet recommendations
    4. Follow-up schedule
    5. Warning signs
    
    Make it personalized, practical, and evidence-based.
    """
    
    try:
        response = model.generate_content(prompt)
        
        return {
            "success": True,
            "recommendations": response.text,
            "generated_date": datetime.now().strftime("%Y-%m-%d %H:%M")
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "recommendations": f"Based on B12 level of {b12_value} pg/mL: Consult a healthcare provider for personalized treatment."
        }

# ==================== DOCUMENT PROCESSING ====================

def extract_text_from_pdf(pdf_file):
    """Extract text from uploaded PDF file"""
    text = ""
    try:
        with pdfplumber.open(pdf_file) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
    except Exception as e:
        print(f"PDF extraction error: {e}")
    return text

def extract_text_from_image(image_file):
    """Extract text from uploaded image using OCR"""
    text = ""
    try:
        reader = easyocr.Reader(['en'])
        image = Image.open(image_file)
        image_np = np.array(image)
        results = reader.readtext(image_np, detail=0)
        text = "\n".join(results)
    except Exception as e:
        print(f"Image OCR error: {e}")
    return text

def extract_b12_value(text):
    """Extract B12 value from text using regex patterns"""
    patterns = [
        r'Vitamin B12[\s:]*([\d,.]+)\s*(?:pg/mL|pg/ml|pg)',
        r'B12[\s:]*([\d,.]+)\s*(?:pg/mL|pg/ml|pg)',
        r'Cobalamin[\s:]*([\d,.]+)\s*(?:pg/mL|pg/ml|pg)',
        r'([\d,.]+)\s*(?:pg/mL|pg/ml|pg).*?B12',
        r'Serum B12[\s:]*([\d,.]+)'
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        if matches:
            try:
                value = float(matches[0].replace(',', ''))
                return value
            except:
                continue
    return None

def analyze_lab_report(file, file_type):
    """Analyze uploaded lab report"""
    result = {'b12_value': None, 'status': '', 'message': '', 'text': ''}
    
    try:
        # Extract text
        if file_type == 'pdf':
            text = extract_text_from_pdf(file)
        else:
            text = extract_text_from_image(file)
        
        result['text'] = text
        
        # Find B12 value
        b12_value = extract_b12_value(text)
        result['b12_value'] = b12_value
        
        # Determine status
        if b12_value:
            if b12_value < 200:
                result['status'] = 'DEFICIENT'
                result['message'] = f'B12 Level: {b12_value} pg/mL (Deficient <200)'
            elif b12_value < 300:
                result['status'] = 'BORDERLINE'
                result['message'] = f'B12 Level: {b12_value} pg/mL (Borderline 200-300)'
            else:
                result['status'] = 'NORMAL'
                result['message'] = f'B12 Level: {b12_value} pg/mL (Normal >300)'
        else:
            result['status'] = 'NOT_FOUND'
            result['message'] = 'B12 value not found in report'
            
    except Exception as e:
        result['message'] = f'Error: {str(e)}'
    
    return result

# ==================== CONFLICT RESOLUTION SYSTEM ====================

class DataConflictTracker:
    """Track and resolve data conflicts for the same user"""
    
    def __init__(self):
        self.user_history = []
        self.data_quality = {'grade': 'A', 'score': 100, 'issues': []}
        self.user_id = None
    
    def set_user_id(self, user_id):
        """Set user identifier for tracking"""
        self.user_id = user_id
    
    def add_data_point(self, user_data, source_type):
        """Add new data point with conflict checking"""
        cleaned_data = self._clean_data(user_data)
        
        self.user_history.append({
            'timestamp': datetime.now(),
            'data': cleaned_data,
            'source': source_type,
            'has_lab_data': 'lab_b12_level' in cleaned_data and cleaned_data['lab_b12_level'] is not None and cleaned_data['lab_b12_level'] > 0
        })
        
        self._check_conflicts()
        return self.data_quality
    
    def _clean_data(self, user_data):
        """Clean and validate input data"""
        cleaned = user_data.copy()
        
        # Convert BMI to float if possible
        if 'bmi' in cleaned:
            try:
                cleaned['bmi'] = float(cleaned['bmi'])
                if cleaned['bmi'] < 10 or cleaned['bmi'] > 60:
                    cleaned['bmi'] = 22.5
            except:
                cleaned['bmi'] = 22.5
        
        # Handle B12 values
        if 'b12_level' in cleaned:
            b12_val = cleaned['b12_level']
            if b12_val in [None, 'None', 'none', '', 0, '0']:
                cleaned['b12_level'] = None
            elif isinstance(b12_val, str):
                try:
                    cleaned['b12_level'] = float(b12_val.replace(',', ''))
                except:
                    cleaned['b12_level'] = None
        
        # Same for lab_b12_level
        if 'lab_b12_level' in cleaned:
            b12_val = cleaned['lab_b12_level']
            if b12_val in [None, 'None', 'none', '', 0, '0']:
                cleaned['lab_b12_level'] = None
            elif isinstance(b12_val, str):
                try:
                    cleaned['lab_b12_level'] = float(b12_val.replace(',', ''))
                except:
                    cleaned['lab_b12_level'] = None
        
        return cleaned
    
    def _check_conflicts(self):
        """Check for data conflicts in history"""
        if len(self.user_history) < 2:
            return
        
        self.data_quality['issues'] = []
        issues_count = 0
        
        latest = self.user_history[-1]
        
        for i, previous in enumerate(self.user_history[:-1]):
            # Check BMI conflicts
            latest_bmi = latest['data'].get('bmi')
            prev_bmi = previous['data'].get('bmi')
            
            if latest_bmi and prev_bmi and abs(latest_bmi - prev_bmi) > 5:
                issues_count += 1
                self.data_quality['issues'].append({
                    'type': 'BMI_CONTRADICTION',
                    'message': f'BMI changed significantly: {prev_bmi} → {latest_bmi}',
                    'severity': 'medium'
                })
        
        # Update data quality grade
        if issues_count == 0:
            self.data_quality['grade'] = 'A'
            self.data_quality['score'] = 100
        elif issues_count == 1:
            self.data_quality['grade'] = 'B'
            self.data_quality['score'] = 85
        elif issues_count == 2:
            self.data_quality['grade'] = 'C'
            self.data_quality['score'] = 70
        elif issues_count == 3:
            self.data_quality['grade'] = 'D'
            self.data_quality['score'] = 60
        else:
            self.data_quality['grade'] = 'F'
            self.data_quality['score'] = 50
        
        return self.data_quality
    
    def get_resolved_data(self):
        """Resolve conflicts and return most reliable data"""
        if not self.user_history:
            return {}
        
        resolved = self.user_history[-1]['data'].copy()
        
        lab_data_found = False
        for entry in reversed(self.user_history):
            if 'lab_b12_level' in entry['data'] and entry['data']['lab_b12_level']:
                resolved['lab_b12_level'] = entry['data']['lab_b12_level']
                resolved['b12_source'] = 'lab_report'
                lab_data_found = True
                if 'bmi' in entry['data']:
                    resolved['bmi'] = entry['data']['bmi']
                break
        
        if not lab_data_found:
            for entry in reversed(self.user_history):
                if 'b12_level' in entry['data'] and entry['data']['b12_level']:
                    resolved['b12_level'] = entry['data']['b12_level']
                    resolved['b12_source'] = 'manual_entry'
                    break
        
        if self.data_quality['issues']:
            resolved['has_conflicts'] = True
            resolved['data_quality'] = self.data_quality.copy()
            resolved['conflict_count'] = len(self.data_quality['issues'])
        else:
            resolved['has_conflicts'] = False
        
        resolved['report_count'] = len(self.user_history)
        resolved['data_sources'] = list(set([h['source'] for h in self.user_history]))
        
        return resolved
    
    def clear_history(self):
        """Clear user history"""
        self.user_history = []
        self.data_quality = {'grade': 'A', 'score': 100, 'issues': []}

# Initialize global tracker
data_tracker = DataConflictTracker()

# ==================== ML MODEL LOADING ====================

class B12MLPredictor:
    """Wrapper for ML model predictions"""
    
    def __init__(self, model_path='b12_deficiency_model.pkl'):
        self.model = None
        self.scaler = None
        self.feature_names = None
        self.model_metrics = None
        self.dataset_stats = None
        
        self.dataset_features = [
            'age', 'gender', 'bmi', 'systolic_bp', 'diastolic_bp',
            'cholesterol', 'hdl', 'ldl', 'glucose', 'smoker',
            'diabetic', 'diet_score', 'risk_factor'
        ]
        
        if os.path.exists(model_path):
            self.load_model(model_path)
            self._load_dataset_stats()
    
    def load_model(self, model_path):
        """Load trained ML model"""
        try:
            with open(model_path, 'rb') as f:
                model_data = pickle.load(f)
            
            self.model = model_data['model']
            self.scaler = model_data['scaler']
            self.feature_names = model_data['feature_names']
            self.model_metrics = model_data.get('metrics', {})
            
        except Exception as e:
            print(f"❌ Error loading model: {e}")
            self.model = None
    
    def _load_dataset_stats(self):
        """Load dataset statistics for reference"""
        try:
            if os.path.exists('nhanes_real_processed.csv'):
                self.dataset_df = pd.read_csv('nhanes_real_processed.csv')
                self.dataset_stats = {
                    'total_samples': len(self.dataset_df),
                    'deficiency_rate': self.dataset_df['b12_deficient'].mean(),
                    'b12_min': self.dataset_df['b12_level'].min(),
                    'b12_max': self.dataset_df['b12_level'].max(),
                    'b12_mean': self.dataset_df['b12_level'].mean()
                }
        except:
            self.dataset_df = None
            self.dataset_stats = None
    
    def predict_from_dataset_features(self, dataset_features_dict):
        """Predict B12 deficiency using ONLY dataset features"""
        if self.model is None:
            raise ValueError("ML model not loaded.")
        
        try:
            missing_features = [f for f in self.feature_names if f not in dataset_features_dict]
            if missing_features:
                raise ValueError(f"Missing dataset features: {missing_features}")
            
            feature_vector = [dataset_features_dict[feature] for feature in self.feature_names]
            feature_vector_scaled = self.scaler.transform([feature_vector])
            
            probability = self.model.predict_proba(feature_vector_scaled)[0]
            prediction = self.model.predict(feature_vector_scaled)[0]
            
            return {
                'deficient_probability': float(probability[1]),
                'prediction': int(prediction),
                'prediction_label': 'Deficient' if prediction == 1 else 'Normal',
                'confidence': float(max(probability)),
                'risk_level': self._probability_to_risk_level(probability[1])
            }
            
        except Exception as e:
            print(f"❌ Dataset prediction error: {e}")
            raise
    
    def map_user_to_dataset_features(self, user_data):
        """Map user form data to dataset features"""
        mapped_features = {}
        
        mapping_rules = {
            'age': lambda d: self._validate_age(d.get('age', 35)),
            'gender': lambda d: 1 if str(d.get('gender', 'Male')).lower() in ['female', 'f'] else 0,
            'bmi': lambda d: self._validate_bmi(d.get('bmi', 22.5)),
            'diet_score': lambda d: {
                'Vegan': 2,
                'Vegetarian': 4,
                'Pescetarian': 6,
                'Omnivore': 8
            }.get(d.get('diet_type', 'Omnivore'), 5),
            'diabetic': lambda d: 1 if 'Diabetes' in str(d.get('conditions_list', '')) else 0,
            'risk_factor': lambda d: min(d.get('symptoms_count', 0) + 
                                       len(str(d.get('medical_conditions', '')).split(',')) * 2, 10),
            'systolic_bp': lambda d: 120,
            'diastolic_bp': lambda d: 80,
            'cholesterol': lambda d: 200,
            'hdl': lambda d: 50,
            'ldl': lambda d: 120,
            'glucose': lambda d: 90,
            'smoker': lambda d: 0
        }
        
        for feature in self.dataset_features:
            if feature in mapping_rules:
                mapped_features[feature] = mapping_rules[feature](user_data)
            else:
                if self.dataset_df is not None and feature in self.dataset_df.columns:
                    mapped_features[feature] = float(self.dataset_df[feature].median())
                else:
                    mapped_features[feature] = 0
        
        return mapped_features
    
    def _validate_age(self, age):
        """Validate age value"""
        try:
            age_val = int(age)
            if 0 < age_val < 120:
                return age_val
        except:
            pass
        return 35
    
    def _validate_bmi(self, bmi):
        """Validate BMI value"""
        try:
            bmi_val = float(bmi)
            if 10 <= bmi_val <= 60:
                return bmi_val
        except:
            pass
        return 22.5
    
    def _probability_to_risk_level(self, probability):
        """Convert probability to risk level"""
        if probability >= 0.7:
            return "High"
        elif probability >= 0.4:
            return "Medium"
        elif probability >= 0.2:
            return "Low"
        else:
            return "Very Low"
    
    def get_dataset_info(self):
        """Get information about the training dataset"""
        if self.dataset_stats:
            return {
                'status': 'Loaded',
                'samples': self.dataset_stats['total_samples'],
                'deficiency_rate': f"{self.dataset_stats['deficiency_rate']:.1%}",
                'b12_range': f"{self.dataset_stats['b12_min']:.0f}-{self.dataset_stats['b12_max']:.0f} pg/mL",
                'features': self.feature_names
            }
        elif self.model_metrics:
            return {
                'status': 'Trained',
                'samples': self.model_metrics.get('n_samples', 0),
                'accuracy': f"{self.model_metrics.get('test_accuracy', 0):.1%}",
                'features': self.feature_names
            }
        else:
            return {'status': 'No dataset information available'}

# Initialize global predictor
try:
    ml_predictor = B12MLPredictor('b12_deficiency_model.pkl')
except:
    ml_predictor = B12MLPredictor()

# ==================== PREDICTION FUNCTIONS ====================

def predict_with_conflict_resolution(user_data, lab_b12_level=None, source_type='user_form'):
    """MAIN PREDICTION FUNCTION with conflict resolution"""
    track_data = user_data.copy()
    if lab_b12_level:
        track_data['lab_b12_level'] = lab_b12_level
    
    data_quality = data_tracker.add_data_point(track_data, source_type)
    resolved_data = data_tracker.get_resolved_data()
    
    final_b12_level = None
    if resolved_data.get('lab_b12_level'):
        final_b12_level = resolved_data['lab_b12_level']
    elif resolved_data.get('b12_level'):
        final_b12_level = resolved_data['b12_level']
    elif lab_b12_level:
        final_b12_level = lab_b12_level
    
    try:
        dataset_features = ml_predictor.map_user_to_dataset_features(resolved_data)
        prediction = ml_predictor.predict_from_dataset_features(dataset_features)
        
        if final_b12_level and final_b12_level > 0:
            prediction = _adjust_with_lab_data(prediction, final_b12_level)
        
        if data_quality['issues']:
            prediction['has_conflicts'] = True
            prediction['data_quality'] = data_quality
            prediction['resolved_data'] = resolved_data
            
            if data_quality['score'] < 80:
                prediction['confidence'] = prediction['confidence'] * 0.8
        
        return prediction
        
    except Exception as e:
        fallback = _simple_risk_calculation_with_conflict(resolved_data, final_b12_level, data_quality)
        fallback['has_conflicts'] = bool(data_quality['issues'])
        fallback['data_quality'] = data_quality
        return fallback

def _adjust_with_lab_data(prediction, lab_b12_level):
    """Adjust prediction with lab B12 data"""
    dataset_prob = prediction.get('deficient_probability', 0.5)
    
    if lab_b12_level < 150:
        lab_prob = 0.75
        urgency = "Immediate"
    elif lab_b12_level < 200:
        lab_prob = 0.65
        urgency = "Soon"
    elif lab_b12_level < 300:
        lab_prob = 0.55
        urgency = "Monitor"
    else:
        lab_prob = 0.25
        urgency = "None"
    
    if lab_b12_level < 300:
        lab_weight = 0.6
    else:
        lab_weight = 0.4
    
    dataset_weight = 1 - lab_weight
    combined_prob = (lab_prob * lab_weight) + (dataset_prob * dataset_weight)
    combined_prob = min(combined_prob, 0.85)
    
    prediction['deficient_probability'] = combined_prob
    prediction['prediction'] = 1 if combined_prob > 0.5 else 0
    prediction['prediction_label'] = 'Deficient' if combined_prob > 0.5 else 'Normal'
    prediction['confidence'] = combined_prob if combined_prob > 0.5 else 1 - combined_prob
    prediction['lab_adjusted'] = True
    prediction['lab_b12_level'] = lab_b12_level
    prediction['lab_urgency'] = urgency
    
    if lab_b12_level < 200 and combined_prob > 0.6:
        prediction['risk_level'] = 'High'
    elif lab_b12_level < 200:
        if prediction['risk_level'] == 'Low':
            prediction['risk_level'] = 'Medium'
    
    return prediction

def _simple_risk_calculation_with_conflict(user_data, lab_b12_level=None, data_quality=None):
    """Simple fallback calculation with conflict awareness"""
    has_conflicts = False
    if data_quality and data_quality.get('issues'):
        has_conflicts = True
    
    probability = 0
    
    if lab_b12_level and lab_b12_level < 150:
        probability = 0.70
    elif lab_b12_level and lab_b12_level < 200:
        probability = 0.60
    elif lab_b12_level and lab_b12_level < 300:
        probability = 0.40
    else:
        probability = 0.20
    
    if user_data.get('age', 0) > 50:
        probability += 0.10
    if user_data.get('diet_type', '') == 'Vegan':
        probability += 0.15
    elif user_data.get('diet_type', '') == 'Vegetarian':
        probability += 0.08
    if user_data.get('symptoms_count', 0) > 0:
        probability += min(user_data['symptoms_count'] * 0.04, 0.15)
    
    if user_data.get('medical_conditions', 0) > 0:
        probability += user_data['medical_conditions'] * 0.05
    
    if has_conflicts:
        probability += 0.05
    
    probability = min(probability, 0.80)
    probability = max(probability, 0.05)
    
    if probability > 0.65:
        risk_level = 'High'
    elif probability > 0.35:
        risk_level = 'Medium'
    else:
        risk_level = 'Low'
    
    result = {
        'deficient_probability': probability,
        'prediction': 1 if probability > 0.5 else 0,
        'prediction_label': 'Deficient' if probability > 0.5 else 'Normal',
        'confidence': probability if probability > 0.5 else 1 - probability,
        'risk_level': risk_level
    }
    
    if has_conflicts:
        result['has_conflicts'] = True
        result['data_quality'] = data_quality
        result['confidence'] = result['confidence'] * 0.7
    
    return result

# ==================== SCHEDULE GENERATION ====================

def generate_ai_treatment_recommendations(b12_value, status, age, diet_type, symptoms_count=0):
    """Generate comprehensive AI treatment recommendations using Gemini"""
    
    # Handle None b12_value
    if b12_value is None:
        b12_value = 0
        status = "UNKNOWN"
    
    model = setup_gemini_api()
    if not model:
        return {
            "success": False,
            "error": "API not configured",
            "recommendations": "Add Gemini API key for AI recommendations."
        }
    
    prompt = f"""
    As a medical AI specializing in Vitamin B12 deficiency, provide comprehensive treatment recommendations.
    
    PATIENT PROFILE:
    - B12 Level: {b12_value} pg/mL ({'Not detected' if b12_value == 0 else 'Detected'})
    - Status: {status}
    - Age: {age} years
    - Diet: {diet_type}
    - Symptoms: {symptoms_count} reported
    
    Provide ALL of these in one comprehensive response:
    
    1. IMMEDIATE ACTIONS (what to do right now)
    2. SUPPLEMENT PLAN (specific type, dose, frequency, duration)
    3. DIET RECOMMENDATIONS (specific foods for {diet_type} diet)
    4. LIFESTYLE CHANGES (exercise, sleep, habits)
    5. FOLLOW-UP SCHEDULE (when to test again, what tests)
    6. WARNING SIGNS (when to see a doctor immediately)
    7. EXPECTED TIMELINE (when to expect improvement)
    
    Format it clearly with headings and bullet points.
    Make it practical, personalized, and evidence-based.
    """
    
    try:
        response = model.generate_content(prompt)
        
        return {
            "success": True,
            "recommendations": response.text,
            "generated_date": datetime.now().strftime("%Y-%m-%d %H:%M")
        }
        
    except Exception as e:
        # Provide fallback recommendations that don't depend on b12_value comparisons
        if b12_value == 0:
            fallback = """**B12 Level Not Detected in Report:**

**Immediate Actions:**
1. Consult a healthcare provider for proper B12 testing
2. Consider getting a comprehensive blood test
3. Monitor your symptoms

**General Recommendations:**
• Include B12-rich foods in your diet
• Consider a basic B12 supplement (250-500 mcg daily)
• Get proper medical evaluation

**When to See a Doctor:**
• If you experience fatigue, tingling, or memory issues
• If symptoms worsen
• For proper diagnosis and treatment"""
        else:
            # Use safe comparisons
            b12_val = float(b12_value)
            if b12_val < 200:
                dose = "1000-2000 mcg daily"
                duration = "3-6 months minimum"
                followup = "3 months"
            elif b12_val < 300:
                dose = "500-1000 mcg daily"
                duration = "2-3 months"
                followup = "6 months"
            else:
                dose = "250-500 mcg daily"
                duration = "Ongoing if at risk"
                followup = "12 months"
            
            fallback = f"""Based on B12 level of {b12_value} pg/mL ({status}):

**Immediate Actions:**
1. Consult a healthcare provider for personalized advice
2. Consider starting B12 supplements: {dose}
3. Adjust diet to include more B12-rich foods

**Supplement Plan:**
• Type: {"Methylcobalamin (for better absorption)" if b12_val < 200 else "Cyanocobalamin (standard)"}
• Dose: {dose}
• Frequency: Daily
• Duration: {duration}

**Diet Recommendations for {diet_type}:**
• Include fortified foods daily
• Consume B12-rich sources regularly
• Consider nutritional yeast supplementation

**Follow-up:**
• Retest B12 in {followup}
• Monitor symptoms regularly

**Warning Signs:**
• Worsening neurological symptoms
• Severe fatigue preventing daily activities
• New or unusual symptoms"""
        
        return {
            "success": True,
            "recommendations": fallback,
            "generated_date": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "note": "Using fallback recommendations"
        }
# ==================== RECOMMENDATIONS ====================

def generate_recommendations(risk_level, diet_type, age, ml_prediction=None):
    """Generate personalized recommendations"""
    recs = {
        "diet": [],
        "supplements": [],
        "lifestyle": [],
        "medical": [],
        "warnings": []
    }
    
    # SUPPLEMENTS SECTION
    if risk_level == "High":
        recs["supplements"] = [
            {"type": "Methylcobalamin", "dose": "1000-2000 mcg", "frequency": "Daily", "duration": "3-6 months minimum"},
            {"type": "B-Complex", "dose": "1 tablet", "frequency": "Daily", "duration": "3 months"},
            {"type": "Folate", "dose": "400-800 mcg", "frequency": "Daily", "duration": "3 months"}
        ]
    elif risk_level == "Medium":
        recs["supplements"] = [
            {"type": "Cyanocobalamin", "dose": "500-1000 mcg", "frequency": "Daily", "duration": "2-3 months"},
            {"type": "Multivitamin", "dose": "1 tablet", "frequency": "Daily", "duration": "Ongoing"}
        ]
    else:
        recs["supplements"] = [
            {"type": "Maintenance B12", "dose": "250-500 mcg", "frequency": "Daily", "duration": "Ongoing"}
        ]
    
    # DIET RECOMMENDATIONS
    if diet_type == "Vegan":
        recs["diet"] = [
            "Include fortified foods: Nutritional yeast, plant milks, breakfast cereals (2-3 servings/day)",
            "Consider Marmite/Vegemite: 1 tsp daily provides ~1.4 mcg B12",
            "All vegans require B12 supplements - no exceptions"
        ]
    elif diet_type == "Vegetarian":
        recs["diet"] = [
            "Include dairy: Milk, yogurt, cheese (3 servings/day)",
            "Include eggs: 2-3 eggs daily",
            "Consider fortified foods as backup source"
        ]
    elif diet_type == "Pescetarian":
        recs["diet"] = [
            "Include fish: Salmon, trout, tuna (3-4 servings/week)",
            "Include shellfish: Clams, mussels, oysters (2 servings/week)",
            "Include eggs and dairy"
        ]
    else:
        recs["diet"] = [
            "Include red meat: Lean beef, lamb (3-4 servings/week)",
            "Include poultry: Chicken, turkey (2-3 servings/week)",
            "Include fish: Fatty fish (2 servings/week)",
            "Include dairy: Milk, cheese, yogurt (2-3 servings/day)"
        ]
    
    # LIFESTYLE RECOMMENDATIONS
    recs["lifestyle"] = [
        "Avoid smoking: Smoking reduces B12 absorption",
        "Limit alcohol: <2 drinks/day",
        "Regular exercise: Improves circulation and nutrient absorption",
        "Stress management: Practice meditation or yoga"
    ]
    
    # MEDICAL RECOMMENDATIONS
    if age > 50:
        recs["medical"].append("Age 50+: Consider regular B12 monitoring")
    
    if risk_level in ["High", "Medium"]:
        recs["medical"].extend([
            "Get blood tests: Complete blood count (CBC), folate, iron studies",
            "Follow-up: Retest B12 in 3-6 months after starting treatment"
        ])
    
    # WARNINGS
    if risk_level == "High":
        recs["warnings"].extend([
            "Consult healthcare provider within 1-2 weeks",
            "Monitor for neurological symptoms",
            "Consider B12 injections if absorption issues"
        ])
    
    return recs

# ==================== UTILITY FUNCTIONS ====================

def calculate_bmi(weight_kg, height_cm):
    """Calculate BMI from weight and height"""
    try:
        height_m = height_cm / 100
        bmi = weight_kg / (height_m ** 2)
        return round(bmi, 1)
    except:
        return None

def get_bmi_category(bmi):
    """Get BMI category"""
    if bmi is None:
        return "Unknown", "No BMI data"

    try:
        bmi_float = float(bmi)
    
        if bmi_float < 16.5:
            return "Severely Underweight", "Needs medical attention"
        elif bmi_float < 18.5:
            return "Underweight", "Consider gaining weight"
        elif bmi_float < 25:
            return "Normal", "Healthy weight"
        elif bmi_float < 30:
            return "Overweight", "Consider losing weight"
        elif bmi_float < 35:
            return "Obese Class I", "Medical advice recommended"
        elif bmi_float < 40:
            return "Obese Class II", "Medical attention needed"
        else:
            return "Obese Class III", "Urgent medical attention needed"
    except:
        return "Invalid", "Invalid BMI value"

def export_to_pdf(user_data, risk_level, risk_score):
    """Export results to PDF format"""
    try:
        from fpdf import FPDF
        
        pdf = FPDF()
        pdf.add_page()
        
        pdf.set_font('Arial', 'B', 16)
        pdf.cell(0, 10, 'Vitamin B12 Deficiency Assessment Report', 0, 1, 'C')
        pdf.ln(5)
        
        pdf.set_font('Arial', '', 12)
        pdf.cell(0, 10, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}", 0, 1, 'C')
        pdf.ln(10)
        
        pdf.set_font('Arial', 'B', 14)
        risk_text = f"Risk Level: {risk_level}"
        pdf.cell(0, 10, risk_text, 0, 1, 'C')
        pdf.ln(10)
        
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(0, 10, 'User Information:', 0, 1)
        pdf.set_font('Arial', '', 11)
        
        info_lines = [
            f"Age: {user_data.get('age', 'N/A')}",
            f"Gender: {user_data.get('gender', 'N/A')}",
            f"Diet: {user_data.get('diet_type', 'N/A')}",
            f"Symptoms Reported: {user_data.get('symptoms_count', 0)}",
            f"Risk Score: {risk_score:.1%}"
        ]
        
        for line in info_lines:
            pdf.cell(0, 7, line, 0, 1)
        
        pdf.ln(10)
        
        pdf.set_font('Arial', 'I', 8)
        pdf.cell(0, 10, 'Note: This report is for informational purposes only. Consult a healthcare provider for medical advice.', 0, 0, 'C')
        
        # Save to buffer
        buffer = io.BytesIO()
        pdf.output(buffer)
        buffer.seek(0)
        
        return buffer.getvalue()
        
    except ImportError:
        return None
    except Exception as e:
        return None

def export_to_json(user_data, risk_level, risk_score):
    """Export results to JSON format"""
    try:
        export_data = {
            "metadata": {
                "export_date": datetime.now().isoformat(),
                "report_type": "B12 Deficiency Assessment"
            },
            "user_data": user_data,
            "risk_level": risk_level,
            "risk_score": risk_score
        }
        
        return json.dumps(export_data, indent=2, default=str)
        
    except Exception as e:
        return None

def save_user_data(user_data, risk_level):
    """Simple function to save user data to a JSON file"""
    import json
    
    try:
        data_to_save = {
            'user_data': user_data,
            'risk_level': risk_level,
            'timestamp': datetime.now().isoformat()
        }
        
        filename = f"user_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w') as f:
            json.dump(data_to_save, f, indent=2)
        
        print(f"✅ User data saved to: {filename}")
        return True
    except Exception as e:
        print(f"❌ Error saving user data: {e}")
        return False

def clear_user_session():
    """Clear all session data"""
    data_tracker.clear_history()
    print("🧹 Session data cleared")
    return True

# ==================== INITIALIZATION ====================

print("=" * 60)
print("B12 Deficiency Assistant - Utility Module Loaded")
print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 60)

if ml_predictor.model is not None:
    print(f"✅ ML Model: Active")
else:
    print("⚠️ Using basic assessment system")

print(f"📊 Data Tracker: Ready")
print("=" * 60)

# ==================== DAILY TRACKER FUNCTIONS ====================

def save_daily_log_to_mongodb(user_id, daily_data):
    """Save daily tracker data to MongoDB"""
    try:
        # Get MongoDB connection
        mongodb = st.session_state.mongodb
        if not mongodb or not mongodb.connected:
            return {"success": False, "message": "Database not connected"}
        
        # Get daily_logs collection
        collection = mongodb.get_collection('daily_logs')
        
        # Prepare document
        log_doc = {
            "user_id": user_id,
            "date": daily_data.get('date'),
            "log_type": "daily_tracker",
            "data": {
                # Food intake
                "foods": daily_data.get('foods', []),
                "foods_other": daily_data.get('foods_other', ""),
                
                # Supplements
                "supplements": daily_data.get('supplements', []),
                "supplement_dose": daily_data.get('supplement_dose', ""),
                "supplement_time": daily_data.get('supplement_time', ""),
                
                # Symptoms
                "symptoms": daily_data.get('symptoms', []),
                "symptom_severity": daily_data.get('symptom_severity', 0),
                "symptoms_notes": daily_data.get('symptoms_notes', ""),
                
                # Daily metrics
                "energy_level": daily_data.get('energy_level', 5),
                "sleep_hours": daily_data.get('sleep_hours', 7),
                "mood": daily_data.get('mood', "neutral"),
                "water_glasses": daily_data.get('water_glasses', 0),
                
                # Calculated values
                "estimated_b12": daily_data.get('estimated_b12', 0),
                "daily_score": daily_data.get('daily_score', 0)
            },
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }
        
        # Check if log already exists for this date
        existing_log = collection.find_one({
            "user_id": user_id,
            "date": daily_data.get('date')
        })
        
        if existing_log:
            # Update existing log
            result = collection.update_one(
                {"_id": existing_log['_id']},
                {"$set": {
                    "data": log_doc['data'],
                    "updated_at": datetime.now()
                }}
            )
            return {
                "success": True,
                "message": "Updated today's log!",
                "action": "updated",
                "log_id": str(existing_log['_id'])
            }
        else:
            # Insert new log
            result = collection.insert_one(log_doc)
            return {
                "success": True,
                "message": "Saved today's log!",
                "action": "created",
                "log_id": str(result.inserted_id)
            }
            
    except Exception as e:
        print(f"❌ Error saving daily log: {e}")
        return {
            "success": False,
            "message": f"Error saving: {str(e)}"
        }


def get_user_daily_logs(user_id, limit=30):
    """Get user's daily logs from MongoDB"""
    try:
        mongodb = st.session_state.mongodb
        if not mongodb or not mongodb.connected:
            return []
        
        collection = mongodb.get_collection('daily_logs')
        
        # Get logs sorted by date (newest first)
        logs = list(collection.find(
            {"user_id": user_id}
        ).sort("date", -1).limit(limit))
        
        # Convert ObjectId to string for JSON serialization
        for log in logs:
            log['_id'] = str(log['_id'])
            if 'created_at' in log:
                log['created_at'] = log['created_at'].isoformat() if isinstance(log['created_at'], datetime) else str(log['created_at'])
            if 'updated_at' in log:
                log['updated_at'] = log['updated_at'].isoformat() if isinstance(log['updated_at'], datetime) else str(log['updated_at'])
        
        return logs
        
    except Exception as e:
        print(f"❌ Error getting daily logs: {e}")
        return []


def get_todays_log(user_id):
    """Get today's log if it exists"""
    try:
        today = datetime.now().strftime("%Y-%m-%d")
        
        mongodb = st.session_state.mongodb
        if not mongodb or not mongodb.connected:
            return None
        
        collection = mongodb.get_collection('daily_logs')
        
        today_log = collection.find_one({
            "user_id": user_id,
            "date": today
        })
        
        if today_log:
            today_log['_id'] = str(today_log['_id'])
            if 'created_at' in today_log:
                today_log['created_at'] = today_log['created_at'].isoformat() if isinstance(today_log['created_at'], datetime) else str(today_log['created_at'])
        
        return today_log
        
    except Exception as e:
        print(f"❌ Error getting today's log: {e}")
        return None


def calculate_daily_score(daily_data):
    """Calculate a daily health score (0-100)"""
    score = 50  # Base score
    
    # Add points for foods
    foods = daily_data.get('foods', [])
    score += len(foods) * 5  # +5 points per food type
    
    # Add points for supplements
    if daily_data.get('supplements'):
        score += 10
    
    # Adjust for symptoms
    symptoms = daily_data.get('symptoms', [])
    symptom_severity = daily_data.get('symptom_severity', 0)
    score -= len(symptoms) * 5  # -5 points per symptom
    score -= symptom_severity * 2  # -2 points per severity level
    
    # Add points for water
    water = daily_data.get('water_glasses', 0)
    if water >= 8:
        score += 10
    elif water >= 4:
        score += 5
    
    # Add points for sleep
    sleep = daily_data.get('sleep_hours', 0)
    if 7 <= sleep <= 9:
        score += 10
    elif sleep >= 6:
        score += 5
    
    # Add points for energy
    energy = daily_data.get('energy_level', 5)
    if energy >= 7:
        score += 10
    elif energy >= 5:
        score += 5
    
    # Mood points
    mood = daily_data.get('mood', 'neutral')
    mood_points = {
        'sad': 0,
        'neutral': 5,
        'happy': 10,
        'very_happy': 15
    }
    score += mood_points.get(mood, 5)
    
    # Ensure score is between 0-100
    score = max(0, min(100, score))
    
    return score


def estimate_b12_intake(daily_data):
    """Estimate B12 intake in micrograms"""
    b12_total = 0
    
    # B12 content of foods (approximate mcg)
    food_b12 = {
        'dairy': 1.2,      # per serving
        'eggs': 0.6,       # per egg
        'meat_fish': 2.4,  # per serving
        'fortified': 1.5,  # per serving
        'yeast': 2.0,      # per tablespoon
    }
    
    foods = daily_data.get('foods', [])
    for food in foods:
        b12_total += food_b12.get(food, 0)
    
    # Add supplements
    supplements = daily_data.get('supplements', [])
    if 'methylcobalamin' in supplements:
        b12_total += int(daily_data.get('supplement_dose', 0) or 500)
    elif 'cyanocobalamin' in supplements:
        b12_total += int(daily_data.get('supplement_dose', 0) or 1000)
    elif 'b_complex' in supplements:
        b12_total += 50  # Typical B12 in B-complex
    
    return round(b12_total, 1)


def migrate_temp_logs_to_mongodb(user_id):
    """Migrate temporary session logs to MongoDB"""
    try:
        if 'temp_logs' not in st.session_state:
            return {"success": True, "message": "No temp logs to migrate", "count": 0}
        
        temp_logs = st.session_state.temp_logs
        if not temp_logs:
            return {"success": True, "message": "No temp logs to migrate", "count": 0}
        
        migrated_count = 0
        for log in temp_logs:
            result = save_daily_log_to_mongodb(user_id, log)
            if result['success']:
                migrated_count += 1
        
        # Clear temp logs after migration
        st.session_state.temp_logs = []
        
        return {
            "success": True,
            "message": f"Migrated {migrated_count} logs to database",
            "count": migrated_count
        }
        
    except Exception as e:
        return {
            "success": False,
            "message": f"Migration error: {str(e)}",
            "count": 0
        }