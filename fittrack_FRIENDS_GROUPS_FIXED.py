import streamlit as st
import json
import os
import time
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

# API keys 
OPENWEATHER_API_KEY = os.environ.get('OPENWEATHER_API_KEY', '')
USDA_API_KEY = os.environ.get('USDA_API_KEY', '')
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY', '')

# Website Colour Palette
COLOURS = {
    'red': '#d32f2f',
    'blue': '#1976d2',
    'gray': '#5a5a5a',
    'light_gray': '#e0e0e0',
    'white': '#ffffff',
    'dark': '#2c2c2c'
}

# Configure page
st.set_page_config(
    page_title="FitTrack - SST Fitness Companion",
    # page_icon removed
    layout="wide",
    initial_sidebar_state="expanded"
)

# Universal fixed palette 
st.markdown(f"""
    <style>
    /* - Force a consistent light theme regardless of OS/browser setting - */
    html, body, [data-testid="stAppViewContainer"], [data-testid="stApp"], .stApp {{
        background-color: #f0f2f6 !important;
        color: #1e1e2e !important;
        color-scheme: light !important;
    }}

    /* Sidebar */
    [data-testid="stSidebar"] {{
        background-color: #ffffff !important;
        border-right: 1px solid #e0e4ef;
    }}
    [data-testid="stSidebar"] * {{
        color: #1e1e2e !important;
    }}

    /* All text */
    h1, h2, h3, h4, h5, h6 {{
        color: #1e1e2e !important;
        font-weight: 700;
    }}
    p, span, label, li, td, th, div {{
        color: #1e1e2e !important;
    }}

    /* Login / hero header */
    .main-header {{
        background: linear-gradient(135deg, {COLOURS['red']} 0%, #b71c1c 100%);
        padding: 30px;
        border-radius: 12px;
        text-align: center;
        margin-bottom: 30px;
        box-shadow: 0 8px 20px rgba(211, 47, 47, 0.25);
    }}
    .main-header h1,
    .main-header p {{
        color: #ffffff !important;
    }}

    /* Cards */
    .stat-card {{
        background: #ffffff;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid {COLOURS['blue']};
        box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
        margin: 10px 0;
        color: #1e1e2e !important;
        transition: transform 0.2s, box-shadow 0.2s;
    }}
    .stat-card:hover {{
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(0, 0, 0, 0.12);
    }}
    .stat-card h1, .stat-card h2, .stat-card h3,
    .stat-card h4, .stat-card p, .stat-card span,
    .stat-card div, .stat-card li {{
        color: #1e1e2e !important;
    }}

    /* NAPFA grade badges */
    .grade-badge {{
        display: inline-block;
        padding: 5px 15px;
        border-radius: 6px;
        font-weight: bold;
        color: #ffffff !important;
        margin: 5px;
    }}
    .grade-5 {{ background: #2e7d32; }}
    .grade-4 {{ background: #558b2f; }}
    .grade-3 {{ background: #f9a825; color: #1e1e2e !important; }}
    .grade-2 {{ background: #e65100; }}
    .grade-1 {{ background: #c62828; }}

    /* Buttons — primary blue */
    .stButton > button {{
        background: linear-gradient(135deg, {COLOURS['blue']} 0%, #1565c0 100%) !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 10px 28px !important;
        font-weight: 600 !important;
        transition: all 0.2s;
    }}
    .stButton > button:hover {{
        background: linear-gradient(135deg, #1565c0 0%, #0d47a1 100%) !important;
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(25, 118, 210, 0.35) !important;
    }}

    /* Input fields — white on light grey page */
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stTextArea > div > div > textarea {{
        background-color: #ffffff !important;
        color: #1e1e2e !important;
        border: 1px solid #c8cfe0 !important;
        border-radius: 6px !important;
    }}

    /* Selectboxes / dropdowns */
    .stSelectbox > div > div,
    .stMultiSelect > div > div {{
        background-color: #ffffff !important;
        color: #1e1e2e !important;
        border: 1px solid #c8cfe0 !important;
        border-radius: 6px !important;
    }}

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {{
        background-color: #e8ebf5 !important;
        border-radius: 8px 8px 0 0;
        gap: 4px;
    }}
    .stTabs [data-baseweb="tab"] {{
        background-color: transparent !important;
        color: #5a6070 !important;
        border-radius: 6px 6px 0 0;
        font-weight: 500;
    }}
    .stTabs [aria-selected="true"] {{
        background-color: #ffffff !important;
        color: {COLOURS['blue']} !important;
        font-weight: 700;
        border-bottom: 3px solid {COLOURS['blue']} !important;
    }}

    /* Metric boxes */
    [data-testid="stMetric"] {{
        background: #ffffff;
        border-radius: 8px;
        padding: 12px 16px;
        box-shadow: 0 1px 6px rgba(0,0,0,0.07);
    }}
    [data-testid="stMetricValue"] {{
        color: {COLOURS['blue']} !important;
        font-weight: 700;
    }}
    [data-testid="stMetricLabel"] {{
        color: #5a6070 !important;
    }}

    /* Mobile */
    @media (max-width: 768px) {{
        .main-header {{ padding: 20px; }}
        .stat-card {{ padding: 14px; margin: 6px 0; }}
        .stButton > button {{ padding: 8px 18px !important; font-size: 14px !important; }}
    }}
    </style>
""", unsafe_allow_html=True)

# Data storage file
DATA_FILE = 'fittrack_users.json'

# Initialize session state
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'username' not in st.session_state:
    st.session_state.username = None
if 'users_data' not in st.session_state:
    st.session_state.users_data = {}

# Load user data
def load_users():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    return {}

# Save user data
def save_users(users_data):
    with open(DATA_FILE, 'w') as f:
        json.dump(users_data, f, indent=2)

# Load data on startup
st.session_state.users_data = load_users()

# Get current user data
def get_user_data():
    if st.session_state.username in st.session_state.users_data:
        return st.session_state.users_data[st.session_state.username]
    return None

# Update user data
def update_user_data(data):
    st.session_state.users_data[st.session_state.username] = data
    save_users(st.session_state.users_data)


def get_user_age(user_data):
    """Return current age, computed from birthday if stored, else fall back to stored age."""
    if user_data and user_data.get('birthday'):
        try:
            dob = datetime.strptime(user_data['birthday'], '%Y-%m-%d').date()
            today = datetime.now().date()
            return today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
        except Exception:
            pass
    return get_user_age(user_data) if user_data else 14

# verifitcation of workout by AI

def verify_workout_with_openai(image, exercise_type, strictness=2):
    """
    Verify workout using OpenAI Vision API.
    strictness: 1 = Lenient, 2 = Standard, 3 = Strict
    Returns: (is_valid, feedback, confidence)
    """
    if not OPENAI_API_KEY:
        return None, "OpenAI API key not configured. Please add OPENAI_API_KEY to your Streamlit secrets.", 0

    try:
        import requests
        import base64
        import io

        # Convert image to base64
        buffered = io.BytesIO()
        image.save(buffered, format="JPEG")
        img_base64 = base64.b64encode(buffered.getvalue()).decode()

        # System prompt changes based on teacher's strictness setting
        system_prompts = {
            1: """You are an encouraging PE teacher at a Singapore secondary school evaluating student exercise form.
Be generous and supportive — these are young students still learning. Accept any reasonable attempt at the exercise.
Only reject if the student is clearly doing a completely different exercise or there is an obvious injury risk.
When in doubt, approve. Focus your feedback on one positive and one gentle tip to improve.""",

            2: """You are a PE teacher at a Singapore secondary school evaluating student exercise form.
Apply age-appropriate standards — students should show clear effort and roughly correct technique.
Accept minor form imperfections but reject sloppy or unsafe form. Give balanced, constructive feedback.""",

            3: """You are a strict PE teacher at a Singapore secondary school evaluating student exercise form.
Hold students to proper technique standards. Check all key form points carefully.
Reject if any major form criterion is not met — partial credit is not given.
Be direct and specific about what needs to improve."""
        }

        system_prompt = system_prompts.get(strictness, system_prompts[2])

        # Exercise-specific form criteria
        exercise_criteria = {
            'pull-ups':        "1) Arms fully extended at bottom, 2) Chin clears the bar at top, 3) No excessive kipping or swinging",
            'pull-up':         "1) Arms fully extended at bottom, 2) Chin clears the bar at top, 3) No excessive kipping or swinging",
            'sit-ups':         "1) Feet flat or anchored, 2) Hands behind head or crossed on chest, 3) Shoulders clearly lift off ground",
            'sit-up':          "1) Feet flat or anchored, 2) Hands behind head or crossed on chest, 3) Shoulders clearly lift off ground",
            'push-ups':        "1) Body forms a straight line, 2) Chest near the floor at bottom, 3) Arms fully extend at top, 4) No sagging hips",
            'push-up':         "1) Body forms a straight line, 2) Chest near the floor at bottom, 3) Arms fully extend at top, 4) No sagging hips",
            'squats':          "1) Feet shoulder-width apart, 2) Knees track over toes, 3) Hips at or below knee level, 4) Back stays straight",
            'squat':           "1) Feet shoulder-width apart, 2) Knees track over toes, 3) Hips at or below knee level, 4) Back stays straight",
            'lunges':          "1) Front knee doesn't go past toes, 2) Back knee lowers close to ground, 3) Torso stays upright",
            'burpees':         "1) Clear push-up position at bottom, 2) Full jump with arms overhead at top",
            'plank (seconds)': "1) Body forms a straight line, 2) Core engaged, 3) No raised or sagging hips",
            'jumping jacks':   "1) Arms reach overhead, 2) Feet jump out wide and back together",
            'mountain climbers':"1) Plank position maintained, 2) Knees drive toward chest alternately",
            'bicycle crunches':"1) Shoulders lift off ground, 2) Opposite elbow meets opposite knee",
            'walk':            "1) Person is clearly walking at a moderate pace",
            'jog':             "1) Person is clearly jogging — both feet leave ground at points",
            'run':             "1) Person is clearly running at a brisk pace",
            'sprint':          "1) Person is running at maximum effort",
        }

        criteria = exercise_criteria.get(
            exercise_type.lower(),
            f"The student is clearly attempting to perform {exercise_type} with reasonable effort and form."
        )

        user_prompt = (
            f"Evaluate this student performing {exercise_type}.\n"
            f"Key form criteria to check: {criteria}\n\n"
            f"Respond with exactly 'VALID' or 'INVALID' on the first line, "
            f"then 2–3 sentences of specific, constructive feedback."
        )

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {OPENAI_API_KEY}"
        }

        payload = {
            "model": "gpt-4o",
            "messages": [
                {"role": "system", "content": system_prompt},
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": user_prompt},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_base64}"}}
                    ]
                }
            ],
            "max_tokens": 300
        }

        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=30
        )

        if response.status_code == 200:
            result = response.json()
            feedback = result['choices'][0]['message']['content']
            is_valid = feedback.upper().startswith('VALID') or (
                'VALID' in feedback.upper() and 'INVALID' not in feedback.upper()
            )
            confidence = 90 if is_valid else 80
            return is_valid, feedback, confidence
        else:
            return None, f"API Error: {response.status_code} - {response.text}", 0

    except Exception as e:
        return None, f"Error: {str(e)}", 0

NAPFA_STANDARDS = {
    12: {
        'm': {
            'SU': [[41,36,32,27,22], False],
            'SBJ': [[202,189,176,163,150], False],
            'SAR': [[39,36,32,28,23], False],
            'PU': [[24,21,16,11,5], False],
            'SR': [[10.4,10.9,11.3,11.7,12.2], True],
            'RUN': [[12.01,13.10,14.20,15.30,16.50], True]
        },
        'f': {
            'SU': [[29,25,21,17,13], False],
            'SBJ': [[167,159,150,141,132], False],
            'SAR': [[39,37,34,30,25], False],
            'PU': [[15,13,10,7,3], False],
            'SR': [[11.5,11.9,12.3,12.7,13.2], True],
            'RUN': [[14.41,15.40,16.40,17.40,18.40], True]
        }
    },
    13: {
        'm': {
            'SU': [[42,38,34,29,25], False],
            'SBJ': [[214,202,189,176,164], False],
            'SAR': [[41,38,34,30,25], False],
            'PU': [[25,22,17,12,7], False],
            'SR': [[10.3,10.7,11.1,11.5,11.9], True],
            'RUN': [[11.31,12.30,13.40,14.50,16.00], True]
        },
        'f': {
            'SU': [[30,26,22,18,14], False],
            'SBJ': [[170,162,153,144,135], False],
            'SAR': [[41,39,36,32,27], False],
            'PU': [[16,13,10,7,3], False],
            'SR': [[11.3,11.7,12.2,12.7,13.2], True],
            'RUN': [[14.31,15.30,16.30,17.30,18.30], True]
        }
    },
    14: {
        'm': {
            'SU': [[42,40,37,33,29], False],
            'SBJ': [[225,216,206,196,186], False],
            'SAR': [[43,40,36,32,27], False],
            'PU': [[26,23,18,13,8], False],
            'SR': [[10.2,10.4,10.8,11.2,11.6], True],
            'RUN': [[11.01,12.00,13.00,14.10,15.20], True]
        },
        'f': {
            'SU': [[30,28,24,20,16], False],
            'SBJ': [[177,169,160,151,142], False],
            'SAR': [[43,41,38,34,29], False],
            'PU': [[16,14,10,7,3], False],
            'SR': [[11.5,11.8,12.2,12.6,13.0], True],
            'RUN': [[14.21,15.20,16.20,17.20,18.20], True]
        }
    },
    15: {
        'm': {
            'SU': [[42,40,37,34,30], False],
            'SBJ': [[237,228,218,208,198], False],
            'SAR': [[45,42,38,34,29], False],
            'PU': [[7,6,5,3,1], False],
            'SR': [[10.2,10.3,10.5,10.9,11.3], True],
            'RUN': [[10.41,11.40,12.40,13.40,14.40], True]
        },
        'f': {
            'SU': [[30,29,25,21,17], False],
            'SBJ': [[182,174,165,156,147], False],
            'SAR': [[45,43,39,35,30], False],
            'PU': [[16,14,10,7,3], False],
            'SR': [[11.3,11.6,12.0,12.4,12.8], True],
            'RUN': [[14.11,15.10,16.10,17.10,18.10], True]
        }
    },
    16: {
        'm': {
            'SU': [[42,40,37,34,31], False],
            'SBJ': [[245,236,226,216,206], False],
            'SAR': [[47,44,40,36,31], False],
            'PU': [[8,7,5,3,1], False],
            'SR': [[10.2,10.3,10.5,10.7,11.1], True],
            'RUN': [[10.31,11.30,12.20,13.20,14.10], True]
        },
        'f': {
            'SU': [[30,29,26,22,18], False],
            'SBJ': [[186,178,169,160,151], False],
            'SAR': [[46,44,40,36,31], False],
            'PU': [[17,14,11,7,3], False],
            'SR': [[11.3,11.5,11.8,12.2,12.6], True],
            'RUN': [[14.01,15.00,16.00,17.00,17.50], True]
        }
    },
    17: {
        'm': {
            'SU': [[42,40,37,34,31], False],
            'SBJ': [[249,240,230,220,210], False],
            'SAR': [[48,45,41,37,32], False],
            'PU': [[9,8,6,4,2], False],
            'SR': [[10.2,10.3,10.5,10.7,10.9], True],
            'RUN': [[10.21,11.10,12.00,12.50,13.40], True]
        },
        'f': {
            'SU': [[30,29,27,23,19], False],
            'SBJ': [[189,181,172,163,154], False],
            'SAR': [[46,44,40,36,32], False],
            'PU': [[17,14,11,7,3], False],
            'SR': [[11.3,11.5,11.8,12.1,12.5], True],
            'RUN': [[14.01,14.50,15.50,16.40,17.30], True]
        }
    },
    18: {
        'm': {
            'SU': [[42,40,37,34,31], False],
            'SBJ': [[251,242,232,222,212], False],
            'SAR': [[48,45,41,37,32], False],
            'PU': [[10,9,7,5,3], False],
            'SR': [[10.2,10.3,10.5,10.7,10.9], True],
            'RUN': [[10.21,11.10,11.50,12.40,13.30], True]
        },
        'f': {
            'SU': [[30,29,27,24,20], False],
            'SBJ': [[192,183,174,165,156], False],
            'SAR': [[46,44,40,36,32], False],
            'PU': [[17,15,11,8,4], False],
            'SR': [[11.3,11.5,11.8,12.1,12.4], True],
            'RUN': [[14.01,14.50,15.40,16.30,17.20], True]
        }
    },
    19: {
        'm': {
            'SU': [[42,40,37,34,31], False],
            'SBJ': [[251,242,232,222,212], False],
            'SAR': [[48,45,41,37,32], False],
            'PU': [[10,9,7,5,3], False],
            'SR': [[10.2,10.3,10.5,10.7,10.9], True],
            'RUN': [[10.21,11.00,11.40,12.30,13.20], True]
        },
        'f': {
            'SU': [[30,29,27,24,21], False],
            'SBJ': [[195,185,174,165,156], False],
            'SAR': [[45,43,39,36,32], False],
            'PU': [[17,15,11,8,5], False],
            'SR': [[11.3,11.5,11.8,12.1,12.4], True],
            'RUN': [[14.21,14.50,15.30,16.20,17.10], True]
        }
    },
    20: {
        'm': {
            'SU': [[39,37,34,31,28], False],
            'SBJ': [[242,234,225,216,207], False],
            'SAR': [[47,44,40,36,32], False],
            'PU': [[10,9,7,5,3], False],
            'SR': [[10.4,10.5,10.7,10.9,11.1], True],
            'RUN': [[10.21,11.00,11.40,12.20,13.00], True]
        },
        'f': {
            'SU': [[28,27,25,23,21], False],
            'SBJ': [[197,186,174,162,150], False],
            'SAR': [[43,41,38,35,31], False],
            'PU': [[17,15,11,8,5], False],
            'SR': [[11.6,11.8,12.1,12.4,12.7], True],
            'RUN': [[15.01,15.30,16.00,16.30,17.00], True]
        }
    }
}

def calc_grade(score, cutoffs, reverse):
    """Calculate grade from score and cutoffs"""
    for i, cutoff in enumerate(cutoffs):
        if reverse:
            if score <= cutoff:
                return 5 - i
        else:
            if score >= cutoff:
                return 5 - i
    return 0

# Body Type Calculator
def calculate_body_type(weight, height):
    """Calculate body type based on BMI and frame"""
    bmi = weight / (height * height)

    # Simplified body type classification
    if bmi < 18.5:
        return "Ectomorph", "Naturally lean, fast metabolism, difficulty gaining weight"
    elif bmi < 25:
        if bmi < 21.5:
            return "Ectomorph", "Naturally lean, fast metabolism, difficulty gaining weight"
        else:
            return "Mesomorph", "Athletic build, gains muscle easily, responds well to training"
    elif bmi < 30:
        return "Mesomorph", "Athletic build, gains muscle easily, responds well to training"
    else:
        return "Endomorph", "Larger bone structure, gains weight easily, slower metabolism"
# Login Page
def login_page():
    st.markdown('<div class="main-header"><h1>FitTrack</h1><p>School of Science and Technology Singapore</p><p>Your Personal Fitness Companion</p></div>', unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["Sign In", "Create Account", "Reset Password"])

    with tab1:
        st.subheader("Welcome Back!")

        # Google-style login
        email = st.text_input("Email Address", key="login_email", placeholder="your.email@example.com")
        password = st.text_input("Password", type="password", key="login_password")

        if st.button("Sign In", key="login_btn", type="primary"):
            # Find user by email
            user_found = None
            for username, data in st.session_state.users_data.items():
                if data.get('email', '').lower() == email.lower():
                    # Simple password check (in real app, this would be hashed)
                    if data.get('password') == password:
                        user_found = username
                        break

            if user_found:
                st.session_state.logged_in = True
                st.session_state.username = user_found
                st.success("Login successful!")
                time.sleep(1)
                st.rerun()
            else:
                st.error("Invalid email or password")

        st.write("")
        st.info("**Students:** Use any email | **Teachers:** Use any email")
        st.write("")

        # Password reset link
        col1, col2 = st.columns([3, 1])
        with col2:
            if st.button("Forgot Password?", key="forgot_link"):
                st.info("Go to 'Reset Password' tab")

    with tab2:
        st.subheader("Create Your Account")

        # Role selection at the top
        st.write("### Select Your Role")
        role = st.radio("I am a:", ["Student", "Teacher"], key="reg_role", horizontal=True)

        st.write("---")
        st.write("### Account Information")

        col1, col2 = st.columns(2)
        with col1:
            new_email = st.text_input("Email Address", key="reg_email",
                                     placeholder="student@example.com" if role == "Student" else "teacher@sst.edu.sg")
            full_name = st.text_input("Full Name", key="reg_name")

        with col2:
            new_password = st.text_input("Password", type="password", key="reg_password")
            confirm_password = st.text_input("Confirm Password", type="password", key="reg_confirm_password")

            # Password strength indicator
            if new_password:
                strength = 0
                if len(new_password) >= 8:
                    strength += 1
                if any(c.isupper() for c in new_password):
                    strength += 1
                if any(c.isdigit() for c in new_password):
                    strength += 1
                if any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in new_password):
                    strength += 1

                strength_colors = {0: "#f44336", 1: "#ff9800", 2: "#ffc107", 3: "#8bc34a", 4: "#4caf50"}
                strength_labels = {0: "Very Weak", 1: "Weak", 2: "Fair", 3: "Good", 4: "Strong"}

                st.markdown(f'<div style="background: {strength_colors[strength]}; color: white; padding: 5px 10px; border-radius: 5px; text-align: center; margin-top: -10px;">Password Strength: {strength_labels[strength]}</div>', unsafe_allow_html=True)

                if strength < 2:
                    st.caption("Use 8+ chars, uppercase, numbers, and symbols for better security")

        st.write("### Personal Details")

        col1, col2 = st.columns(2)
        with col1:
            today = datetime.now().date()
            if role == "Student":
                min_dob = today.replace(year=today.year - 18)
                max_dob = today.replace(year=today.year - 12)
                default_dob = today.replace(year=today.year - 14)
            else:
                min_dob = today.replace(year=today.year - 70)
                max_dob = today.replace(year=today.year - 18)
                default_dob = today.replace(year=today.year - 30)

            birthday = st.date_input(
                "Date of Birth",
                value=default_dob,
                min_value=min_dob,
                max_value=max_dob,
                key="reg_birthday"
            )
            # Calculate age from birthday
            age = today.year - birthday.year - ((today.month, today.day) < (birthday.month, birthday.day))
            st.caption(f"Age: {age} years old")

            gender = st.selectbox("Gender", ["Male", "Female"], key="reg_gender")

        with col2:
            if role == "Student":
                school = st.text_input("School (Optional)", value="School of Science and Technology", key="reg_school")
            else:
                school = "School of Science and Technology"
                st.text_input("School", value=school, disabled=True, key="reg_school_teacher")
                department = st.text_input("Department (Optional)", placeholder="e.g., PE Department", key="reg_department")
                class_label = st.text_input("Class Name", placeholder="e.g., 3-Integrity, Sec 2A", key="reg_class_label")

        if role == "Student":
            st.write("### House Selection")
            st.write("Choose your house to earn points for your team!")

            house_options = {
                "Yellow House": "yellow",
                "Red House": "red",
                "Blue House": "blue",
                "Green House": "green",
                "Black House": "black"
            }

            selected_house_display = st.selectbox("Select Your House", list(house_options.keys()), key="reg_house")
            selected_house = house_options[selected_house_display]

            st.info("Every hour you exercise earns 1 point for your house!")

        if role == "Student":
            st.write("### Privacy Settings")
            show_on_leaderboards = st.checkbox("Show me on public leaderboards", value=False, key="reg_leaderboard")

            st.write("### Join a Class (Optional)")
            class_code = st.text_input("Class Code", placeholder="Enter code from your teacher", key="reg_class_code")

        st.write("---")

        # Email verification 
        if 'verify_otp' not in st.session_state:
            st.session_state.verify_otp = None
        if 'verify_email' not in st.session_state:
            st.session_state.verify_email = None
        if 'verify_pending' not in st.session_state:
            st.session_state.verify_pending = False

        # Clear any stale BYPASS state from previous code version
        if st.session_state.verify_otp == "BYPASS":
            st.session_state.verify_otp = None
            st.session_state.verify_email = None
            st.session_state.verify_pending = False

        def send_verification_email(to_email, otp_code):
            """Send OTP via SMTP. Reads credentials from Streamlit secrets / env vars."""
            import smtplib
            from email.mime.text import MIMEText
            from email.mime.multipart import MIMEMultipart

            smtp_user = os.environ.get('SMTP_EMAIL', '')
            smtp_pass = os.environ.get('SMTP_PASSWORD', '')

            if not smtp_user or not smtp_pass:
                return False, "SMTP credentials not configured."

            try:
                msg = MIMEMultipart('alternative')
                msg['Subject'] = "FitTrack — Verify Your Account"
                msg['From'] = f"FitTrack SST <{smtp_user}>"
                msg['To'] = to_email

                html = f"""
                <div style="font-family:Arial,sans-serif;max-width:480px;margin:auto;padding:30px;
                            border:1px solid #e0e0e0;border-radius:10px;">
                    <h2 style="color:#d32f2f;">FitTrack</h2>
                    <p>Thanks for signing up! Use the code below to verify your email address.</p>
                    <div style="text-align:center;padding:20px;background:#f5f5f5;border-radius:8px;
                                font-size:2.5em;font-weight:bold;letter-spacing:8px;color:#1976d2;">
                        {otp_code}
                    </div>
                    <p style="color:#888;font-size:0.9em;margin-top:20px;">
                        This code expires in 10 minutes. If you didn't request this, ignore this email.
                    </p>
                </div>
                """
                msg.attach(MIMEText(html, 'html'))

                with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
                    server.login(smtp_user, smtp_pass)
                    server.sendmail(smtp_user, to_email, msg.as_string())
                return True, "sent"
            except Exception as e:
                return False, str(e)

        def create_account():
            """Create the account and reset verification state."""
            un = new_email.split('@')[0].replace('.', '_')
            orig = un; c2 = 1
            while un in st.session_state.users_data:
                un = f"{orig}{c2}"; c2 += 1

            if role == "Student":
                st.session_state.users_data[un] = {
                    'email': new_email.lower(),
                    'password': new_password,
                    'role': 'student',
                    'name': full_name,
                    'birthday': birthday.isoformat(),
                    'age': age,
                    'gender': 'm' if gender == "Male" else 'f',
                    'school': school,
                    'house': selected_house,
                    'house_points_contributed': 0,
                    'total_workout_hours': 0,
                    'show_on_leaderboards': show_on_leaderboards,
                    'created': datetime.now().isoformat(),
                    'bmi_history': [],
                    'napfa_history': [],
                    'sleep_history': [],
                    'exercises': [],
                    'goals': [],
                    'schedule': [],
                    'saved_workout_plan': None,
                    'friends': [],
                    'friend_requests': [],
                    'badges': [],
                    'level': 'Novice',
                    'total_points': 0,
                    'last_login': datetime.now().isoformat(),
                    'login_streak': 0,
                    'active_challenges': [],
                    'completed_challenges': [],
                    'teacher_class': None,
                    'email_verified': True
                }
                if class_code:
                    for t_un, t_data in st.session_state.users_data.items():
                        if t_data.get('role') == 'teacher' and t_data.get('class_code') == class_code:
                            cur = t_data.get('students', [])
                            if len(cur) >= 30:
                                st.warning("Class is full. Contact your teacher.")
                            else:
                                st.session_state.users_data[un]['teacher_class'] = t_un
                                cur.append(un)
                                st.session_state.users_data[t_un]['students'] = cur
                                lbl = t_data.get('class_label') or f"{t_data['name']}'s class"
                                st.success(f"Joined **{lbl}**!")
                            break
                    else:
                        st.warning("Invalid class code. You can join a class later.")

            else:  # Teacher
                import random as _rand2, string as _str
                gen_code = ''.join(_rand2.choices(_str.ascii_uppercase + _str.digits, k=6))
                st.session_state.users_data[un] = {
                    'email': new_email.lower(),
                    'password': new_password,
                    'role': 'teacher',
                    'name': full_name,
                    'birthday': birthday.isoformat(),
                    'age': age,
                    'gender': 'm' if gender == "Male" else 'f',
                    'school': school,
                    'department': department,
                    'created': datetime.now().isoformat(),
                    'class_code': gen_code,
                    'class_label': class_label,
                    'students': [],
                    'classes_created': [],
                    'last_login': datetime.now().isoformat(),
                    'house': None,
                    'house_points_contributed': 0,
                    'total_workout_hours': 0,
                    'show_on_leaderboards': False,
                    'bmi_history': [],
                    'napfa_history': [],
                    'sleep_history': [],
                    'exercises': [],
                    'goals': [],
                    'schedule': [],
                    'saved_workout_plan': None,
                    'friends': [],
                    'friend_requests': [],
                    'badges': [],
                    'level': 'Novice',
                    'total_points': 0,
                    'login_streak': 0,
                    'groups': [],
                    'group_invites': [],
                    'smart_goals': [],
                    'email_verified': True
                }
                st.info(f"Your Class Code: **{gen_code}** — Share this with your students!")

            save_users(st.session_state.users_data)
            st.session_state.verify_otp = None
            st.session_state.verify_email = None
            st.session_state.verify_pending = False

        # Step 1: validate then send OTP 
        if not st.session_state.verify_pending:
            if st.button("Send Verification Code & Create Account", key="register_btn", type="primary"):
                if not new_email or not full_name or not new_password:
                    st.error("Please fill in all required fields.")
                elif new_password != confirm_password:
                    st.error("Passwords do not match.")
                elif len(new_password) < 6:
                    st.error("Password must be at least 6 characters.")
                elif any(data.get('email', '').lower() == new_email.lower()
                         for data in st.session_state.users_data.values()):
                    st.error("Email already registered.")
                else:
                    import random as _rand
                    otp = str(_rand.randint(100000, 999999))
                    ok, msg = send_verification_email(new_email, otp)
                    if ok:
                        st.session_state.verify_otp = otp
                        st.session_state.verify_email = new_email.lower()
                        st.session_state.verify_pending = True
                        st.session_state.verify_sent_at = datetime.now().isoformat()
                        st.success(f"Verification code sent to **{new_email}**. Check your inbox!")
                        st.rerun()
                    else:
                        # SMTP not configured — create account immediately, no interruption
                        create_account()
                        st.success("Account created! Please sign in.")
                        st.balloons()
                        time.sleep(2)
                        st.rerun()

        # Step 2: enter OTP 
        else:
            st.info(f"A 6-digit code was sent to **{st.session_state.verify_email}**. Enter it below to complete registration.")
            entered_otp = st.text_input("Verification Code", max_chars=6,
                                        placeholder="Enter 6-digit code", key="otp_input")

            col_verify, col_resend, col_cancel = st.columns([2, 1, 1])

            with col_verify:
                if st.button("Verify & Create Account", type="primary", use_container_width=True, key="verify_btn"):
                    if entered_otp.strip() != st.session_state.verify_otp:
                        st.error("Incorrect code. Please try again.")
                    else:
                        create_account()
                        st.success("Account created! Please sign in.")
                        st.balloons()
                        time.sleep(2)
                        st.rerun()

            with col_resend:
                if st.button("Resend", use_container_width=True, key="resend_btn"):
                    import random as _rand3
                    otp2 = str(_rand3.randint(100000, 999999))
                    ok2, _ = send_verification_email(st.session_state.verify_email, otp2)
                    if ok2:
                        st.session_state.verify_otp = otp2
                        st.success("New code sent!")
                    else:
                        st.error("Failed to resend. Check SMTP settings.")

            with col_cancel:
                if st.button("Cancel", use_container_width=True, key="cancel_verify_btn"):
                    st.session_state.verify_otp = None
                    st.session_state.verify_email = None
                    st.session_state.verify_pending = False
                    st.rerun()

    with tab3:
        st.subheader("Reset Password")
        st.write("Enter your email to reset your password")

        reset_email = st.text_input("Email Address", key="reset_email", placeholder="your.email@example.com")

        if st.button("Send Reset Instructions", key="reset_btn", type="primary"):
            # Find user by email
            user_found = None
            username_found = None
            for username, data in st.session_state.users_data.items():
                if data.get('email', '').lower() == reset_email.lower():
                    user_found = data
                    username_found = username
                    break

            if user_found:
                st.success("Account found!")
                st.write("")
                st.write("### Set New Password")

                new_pwd = st.text_input("New Password", type="password", key="new_pwd")
                confirm_new_pwd = st.text_input("Confirm New Password", type="password", key="confirm_new_pwd")

                if st.button("Reset Password", key="do_reset"):
                    if not new_pwd or len(new_pwd) < 6:
                        st.error("Password must be at least 6 characters")
                    elif new_pwd != confirm_new_pwd:
                        st.error("Passwords do not match")
                    else:
                        # Update password
                        st.session_state.users_data[username_found]['password'] = new_pwd
                        save_users(st.session_state.users_data)
                        st.success("Password reset successful! Please sign in with your new password.")
                        st.balloons()
                        time.sleep(2)
                        st.rerun()
            else:
                st.error("Email not found. Please check your email or create a new account.")

        st.write("")
        st.info("**Note:** In production, this would send a secure reset link to your email. For now, you can reset directly here.")

# BMI Calculator
def bmi_calculator():
    st.header("BMI Calculator")

    col1, col2 = st.columns(2)
    with col1:
        weight = st.number_input("Weight (kg)", min_value=20.0, max_value=200.0, value=60.0, step=0.1)
    with col2:
        height = st.number_input("Height (m)", min_value=1.0, max_value=2.5, value=1.65, step=0.01)

    if st.button("Calculate BMI"):
        bmi = weight / (height * height)

        if bmi < 18.5:
            category = "Underweight"
            color = "#2196f3"
        elif bmi < 25:
            category = "Normal"
            color = "#4caf50"
        elif bmi < 30:
            category = "Overweight"
            color = "#ff9800"
        else:
            category = "Obesity"
            color = "#f44336"

        # Save to history
        user_data = get_user_data()
        user_data['bmi_history'].append({
            'date': datetime.now().strftime('%Y-%m-%d'),
            'bmi': round(bmi, 2),
            'weight': weight,
            'height': height,
            'category': category
        })
        update_user_data(user_data)

        # Display results
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f'<div class="stat-card"><h2 style="color: {color};">BMI: {bmi:.2f}</h2></div>', unsafe_allow_html=True)
        with col2:
            st.markdown(f'<div class="stat-card"><h2 style="color: {COLOURS["gray"]};">Category: {category}</h2></div>', unsafe_allow_html=True)

        st.info(f"You have {len(user_data['bmi_history'])} BMI record(s) saved.")

        # Show history chart if there's data
        if len(user_data['bmi_history']) > 1:
            df = pd.DataFrame(user_data['bmi_history'])
            df_chart = df.set_index('date')['bmi']
            st.subheader("BMI History")
            st.line_chart(df_chart)

# NAPFA Test Calculator
def napfa_calculator():
    st.header("NAPFA Test Calculator")

    user_data = get_user_data()

    col1, col2 = st.columns(2)
    with col1:
        gender = st.selectbox("Gender", ["Male", "Female"],
                            index=0 if user_data['gender'] == 'm' else 1)
    with col2:
        # Compute age from birthday if stored, else fall back to stored age
        if user_data.get('birthday'):
            dob = datetime.strptime(user_data['birthday'], '%Y-%m-%d').date()
            today = datetime.now().date()
            computed_age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
        else:
            computed_age = get_user_age(user_data)
        age = st.number_input("Age", min_value=12, max_value=16, value=min(max(computed_age, 12), 16))

    if age not in NAPFA_STANDARDS:
        st.error("Age must be between 12-16")
        return

    gender_key = 'm' if gender == "Male" else 'f'

    st.subheader("Enter Your Scores")

    col1, col2, col3 = st.columns(3)
    with col1:
        situps = st.number_input("Sit-ups (1 min)", min_value=0, max_value=100, value=30)
        broadjump = st.number_input("Standing Broad Jump (cm)", min_value=0, max_value=300, value=200)
    with col2:
        sitreach = st.number_input("Sit and Reach (cm)", min_value=0, max_value=100, value=35)
        pullups = st.number_input("Pull-ups (30 sec)", min_value=0, max_value=50, value=8)
    with col3:
        shuttlerun = st.number_input("Shuttle Run (seconds)", min_value=5.0, max_value=20.0, value=10.5, step=0.1)
        run_time = st.text_input("2.4km Run (min:sec)", value="10:30")

    if st.button("Calculate Grades"):
        try:
            # Convert run time
            time_parts = run_time.split(':')
            run_minutes = int(time_parts[0]) + int(time_parts[1]) / 60

            standards = NAPFA_STANDARDS[age][gender_key]

            scores = {
                'SU': situps,
                'SBJ': broadjump,
                'SAR': sitreach,
                'PU': pullups,
                'SR': shuttlerun,
                'RUN': run_minutes
            }

            test_names = {
                'SU': 'Sit-Ups',
                'SBJ': 'Standing Broad Jump',
                'SAR': 'Sit and Reach',
                'PU': 'Pull-Ups',
                'SR': 'Shuttle Run',
                'RUN': '2.4km Run'
            }

            grades = {}
            total = 0
            min_grade = 5

            for test in scores:
                grade = calc_grade(scores[test], standards[test][0], standards[test][1])
                grades[test] = grade
                total += grade
                min_grade = min(min_grade, grade)

            # Determine medal
            if total >= 21 and min_grade >= 3:
                medal = "Gold"
                medal_color = "#FFD700"
            elif total >= 15 and min_grade >= 2:
                medal = "Silver"
                medal_color = "#C0C0C0"
            elif total >= 9 and min_grade >= 1:
                medal = "Bronze"
                medal_color = "#CD7F32"
            else:
                medal = "No Medal"
                medal_color = COLOURS['gray']

            # Save to history
            user_data['napfa_history'].append({
                'date': datetime.now().strftime('%Y-%m-%d'),
                'age': age,
                'gender': gender_key,
                'scores': scores,
                'grades': grades,
                'total': total,
                'medal': medal
            })
            update_user_data(user_data)

            # Display results
            st.markdown("### Results")

            results_data = []
            for test, grade in grades.items():
                results_data.append({
                    'Test': test_names[test],
                    'Score': scores[test],
                    'Grade': grade
                })

            df = pd.DataFrame(results_data)
            st.dataframe(df, use_container_width=True, hide_index=True)

            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f'<div class="stat-card"><h2 style="color: {COLOURS["blue"]};">Total: {total}</h2></div>', unsafe_allow_html=True)
            with col2:
                st.markdown(f'<div class="stat-card"><h2 style="color: {medal_color};">Medal: {medal}</h2></div>', unsafe_allow_html=True)

            st.info(f"You have {len(user_data['napfa_history'])} NAPFA test(s) saved.")

        except Exception as e:
            st.error(f"Error calculating grades: {str(e)}")

# Sleep Tracker
def sleep_tracker():
    st.header("Sleep Tracker")

    col1, col2 = st.columns(2)
    with col1:
        sleep_start = st.time_input("Sleep Start Time", value=None)
    with col2:
        sleep_end = st.time_input("Wake Up Time", value=None)

    if st.button("Calculate Sleep"):
        if sleep_start and sleep_end:
            # Convert to datetime for calculation
            start = datetime.combine(datetime.today(), sleep_start)
            end = datetime.combine(datetime.today(), sleep_end)

            # Handle overnight sleep
            if end < start:
                end += timedelta(days=1)

            diff = end - start
            hours = diff.seconds // 3600
            minutes = (diff.seconds % 3600) // 60

            if hours >= 8:
                quality = "Excellent"
                color = "#4caf50"
                advice = "Great job! You're getting enough sleep."
            elif hours >= 7:
                quality = "Good"
                color = "#8bc34a"
                advice = "Good sleep duration. Try to get a bit more."
            elif hours >= 6:
                quality = "Fair"
                color = "#ff9800"
                advice = "You need more sleep. Aim for 8-10 hours per night."
            else:
                quality = "Poor"
                color = "#f44336"
                advice = "You need more sleep. Aim for 8-10 hours per night."

            # Save to history
            user_data = get_user_data()
            user_data['sleep_history'].append({
                'date': datetime.now().strftime('%Y-%m-%d'),
                'sleep_start': str(sleep_start),
                'sleep_end': str(sleep_end),
                'hours': hours,
                'minutes': minutes,
                'quality': quality
            })
            update_user_data(user_data)

            # Display results
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f'<div class="stat-card"><h2 style="color: {color};">Sleep Duration: {hours}h {minutes}m</h2></div>', unsafe_allow_html=True)
            with col2:
                st.markdown(f'<div class="stat-card"><h2 style="color: {COLOURS["blue"]};">Quality: {quality}</h2></div>', unsafe_allow_html=True)

            st.info(advice)
            st.info(f"You have {len(user_data['sleep_history'])} sleep record(s) saved.")

            # Show history chart if there's data
            if len(user_data['sleep_history']) > 1:
                df = pd.DataFrame(user_data['sleep_history'])
                df['total_hours'] = df['hours'] + df['minutes'] / 60
                df_chart = df.set_index('date')['total_hours']
                st.subheader("Sleep Duration History (hours)")
                st.line_chart(df_chart)
        else:
            st.error("Please enter both sleep start and end times")

# Exercise Logger
def exercise_logger():
    st.header("Workout Logger")

    user_data = get_user_data()
    has_openai = bool(OPENAI_API_KEY)

    # Define exercise categories
    COUNTER_EXERCISES = [
        "Push-Ups", "Sit-Ups", "Pull-Ups", "Squats", "Lunges",
        "Burpees", "Jumping Jacks", "Mountain Climbers",
        "Bicycle Crunches", "Plank (seconds)"
    ]
    TIMER_EXERCISES = ["Walk", "Jog", "Run", "Sprint"]
    ALL_EXERCISES = COUNTER_EXERCISES + TIMER_EXERCISES + ["Other"]

    # Create tabs - just 2!
    tab1, tab2 = st.tabs(["Log Workout", "Workout History"])

    with tab1:
        st.subheader("Log Your Workout")

        user_data = get_user_data()

        # AI verification status
        if has_openai:
            st.success("**AI Verification Active** — upload a photo to earn bonus points!")
        else:
            st.info("**Mock Mode** — workouts logged without photo verification for testing.")

        st.write("---")

        # - Exercise selector 
        col1, col2 = st.columns(2)
        with col1:
            exercise_type = st.selectbox(
                "Exercise",
                ALL_EXERCISES,
                help="Strength/bodyweight → rep counter  |  Walk/Jog/Run/Sprint → timer  |  Other → your choice"
            )
        with col2:
            intensity = st.selectbox("Intensity", ["Low", "Medium", "High"])

        is_cardio = exercise_type in TIMER_EXERCISES

        # For "Other", let the user pick counter or timer
        if exercise_type == "Other":
            tracking_mode = st.radio(
                "How would you like to track this exercise?",
                [" Rep Counter", "Timer"],
                horizontal=True
            )
            is_cardio = tracking_mode == "Timer"

        st.write("---")

        # 
        #  COUNTER  (strength / bodyweight exercises)
        # 
        if not is_cardio:
            st.write("###  Rep Counter")

            # Initialise counter state
            if "rep_count" not in st.session_state:
                st.session_state.rep_count = 0
            if "set_count" not in st.session_state:
                st.session_state.set_count = 1
            if "set_log" not in st.session_state:
                st.session_state.set_log = []   # list of (set_no, reps)
            if "last_exercise" not in st.session_state:
                st.session_state.last_exercise = exercise_type

            # Reset counter if exercise changed
            if st.session_state.last_exercise != exercise_type:
                st.session_state.rep_count = 0
                st.session_state.set_count = 1
                st.session_state.set_log = []
                st.session_state.last_exercise = exercise_type

            # Big rep display
            st.markdown(f"""
            <div style='text-align:center; padding:25px; background:linear-gradient(135deg,#1976d2,#1565c0);
                        border-radius:15px; color:white; margin:15px 0; box-shadow:0 8px 20px rgba(0,0,0,0.3);'>
                <p style='font-size:1.2em; margin:0; opacity:0.85;'>Set {st.session_state.set_count}</p>
                <h1 style='font-size:5em; margin:0; font-weight:bold;'>{st.session_state.rep_count}</h1>
                <p style='font-size:1.3em; margin-top:5px;'>{"seconds" if exercise_type == "Plank (seconds)" else "reps"}</p>
            </div>
            """, unsafe_allow_html=True)

            # Counter controls
            btn1, btn2, btn3, btn4 = st.columns(4)
            with btn1:
                if st.button("+1", use_container_width=True):
                    st.session_state.rep_count += 1
                    st.rerun()
            with btn2:
                if st.button("+5", use_container_width=True):
                    st.session_state.rep_count += 5
                    st.rerun()
            with btn3:
                if st.button(" -1", use_container_width=True, disabled=st.session_state.rep_count == 0):
                    st.session_state.rep_count = max(0, st.session_state.rep_count - 1)
                    st.rerun()
            with btn4:
                if st.button("Reset", use_container_width=True):
                    st.session_state.rep_count = 0
                    st.rerun()

            # Finish set button
            st.write("")
            if st.button("Finish Set & Rest", type="primary", use_container_width=True, disabled=st.session_state.rep_count == 0):
                st.session_state.set_log.append((st.session_state.set_count, st.session_state.rep_count))
                st.session_state.set_count += 1
                st.session_state.rep_count = 0
                st.rerun()

            # Show sets completed
            if st.session_state.set_log:
                st.write("**Sets completed:**")
                for s_no, s_reps in st.session_state.set_log:
                    unit = "sec" if exercise_type == "Plank (seconds)" else "reps"
                    st.write(f"  • Set {s_no}: {s_reps} {unit}")
                total_reps = sum(r for _, r in st.session_state.set_log)
                st.write(f"**Total: {total_reps} {'sec' if exercise_type == 'Plank (seconds)' else 'reps'} across {len(st.session_state.set_log)} sets**")

            st.write("---")

            # Duration + notes + photo
            notes = st.text_area("Workout Notes (optional)", placeholder="How did it feel? Any PBs?", key="counter_notes")
            manual_duration = st.number_input("Session Duration (minutes)", min_value=1, max_value=180, value=10, key="counter_dur")

            uploaded_file = st.file_uploader("Upload Workout Photo (optional)", type=["jpg", "jpeg", "png"], key="counter_photo")

            st.write("---")

            if st.button(" Save Workout", type="primary", use_container_width=True, key="save_counter"):
                if not st.session_state.set_log and st.session_state.rep_count == 0:
                    st.error("Log at least one set or some reps first!")
                else:
                    # If there are reps in the counter but set not finished, count them
                    if st.session_state.rep_count > 0:
                        st.session_state.set_log.append((st.session_state.set_count, st.session_state.rep_count))

                    total_reps = sum(r for _, r in st.session_state.set_log)
                    sets_done = len(st.session_state.set_log)
                    points_earned = 0
                    verification_status = "unverified"

                    # Look up teacher's strictness setting
                    teacher_key = user_data.get('teacher_class')
                    strictness = 2  # default Standard
                    if teacher_key and teacher_key in st.session_state.users_data:
                        strictness = st.session_state.users_data[teacher_key].get('verification_strictness', 2)

                    # AI verification if photo uploaded
                    if uploaded_file and has_openai:
                        from PIL import Image
                        image = Image.open(uploaded_file)
                        is_valid, feedback, confidence = verify_workout_with_openai(image, exercise_type, strictness)
                        if is_valid:
                            points_earned = int(manual_duration * 10)
                            verification_status = "verified"
                            st.success(f"**AI Verified!** Confidence: {confidence}%\n\n{feedback}")
                        else:
                            points_earned = int(manual_duration * 3)
                            verification_status = "failed"
                            st.warning(f"Verification issue: {feedback}")
                    elif uploaded_file and not has_openai:
                        points_earned = int(manual_duration * 10)
                        verification_status = "mock"
                        st.success("Workout logged! (Mock mode)")
                    else:
                        points_earned = int(manual_duration * 5)
                        st.success("Workout saved without photo verification.")

                    unit = "sec" if exercise_type == "Plank (seconds)" else "reps"

                    # Store photo as base64 so teacher can review it
                    photo_b64 = None
                    if uploaded_file:
                        import base64, io as _io
                        from PIL import Image as _Img
                        _img = _Img.open(uploaded_file)
                        _buf = _io.BytesIO()
                        _img.save(_buf, format="JPEG", quality=60)  # compressed to keep storage small
                        photo_b64 = base64.b64encode(_buf.getvalue()).decode()

                    workout_entry = {
                        'name': exercise_type,
                        'date': datetime.now().strftime('%Y-%m-%d'),
                        'time': datetime.now().strftime('%H:%M'),
                        'duration': int(manual_duration),
                        'intensity': intensity,
                        'sets': sets_done,
                        'total_reps': total_reps,
                        'reps_unit': unit,
                        'notes': notes,
                        'points_earned': points_earned,
                        'ai_feedback': feedback if uploaded_file and has_openai else None,
                        'verification_status': verification_status,
                        'has_photo': photo_b64 is not None,
                        'photo_b64': photo_b64,
                        'teacher_override': False,
                        'workout_type': 'counter'
                    }

                    user_data['exercises'].insert(0, workout_entry)
                    user_data['total_points'] = user_data.get('total_points', 0) + points_earned
                    house_pts = manual_duration / 60
                    user_data['house_points_contributed'] = user_data.get('house_points_contributed', 0) + house_pts
                    user_data['total_workout_hours'] = user_data.get('total_workout_hours', 0) + (manual_duration / 60)

                    new_badges, badge_pts = check_and_award_badges(user_data)
                    if new_badges:
                        user_data['badges'].extend(new_badges)
                        user_data['total_points'] += badge_pts
                        for badge in new_badges:
                            st.success(f"Badge: {badge['name']} (+{badge['points']} pts)")

                    user_data['level'] = calculate_level(user_data['total_points'])[0]
                    update_user_data(user_data)

                    # Reset
                    st.session_state.rep_count = 0
                    st.session_state.set_count = 1
                    st.session_state.set_log = []

                    st.success(f"Saved! {sets_done} sets · {total_reps} {unit} · +{points_earned} pts")
                    st.balloons()
                    time.sleep(1)
                    st.rerun()

        # 
        #  TIMER  (Walk / Jog / Run / Sprint)
        # 
        else:
            st.write("### Cardio Timer")

            # Timer type
            timer_col1, timer_col2 = st.columns(2)
            with timer_col1:
                timer_type = st.radio("Timer Mode", ["Simple Timer", "Interval Timer (HIIT)"], horizontal=True)

            # - Simple timer 
            if timer_type == "Simple Timer":
                with timer_col2:
                    preset_time = st.selectbox(
                        "Preset Duration",
                        ["30 seconds", "1 minute", "2 minutes", "5 minutes",
                         "10 minutes", "15 minutes", "20 minutes", "30 minutes", "Custom"],
                        index=4
                    )

                if preset_time == "Custom":
                    c1, c2 = st.columns(2)
                    with c1:
                        custom_minutes = st.number_input("Minutes", min_value=0, max_value=120, value=10)
                    with c2:
                        custom_seconds = st.number_input("Seconds", min_value=0, max_value=59, value=0)
                    total_seconds = custom_minutes * 60 + custom_seconds
                else:
                    time_map = {"30 seconds": 30, "1 minute": 60, "2 minutes": 120,
                                "5 minutes": 300, "10 minutes": 600, "15 minutes": 900,
                                "20 minutes": 1200, "30 minutes": 1800}
                    total_seconds = time_map[preset_time]

                # Timer state
                for key, default in [("timer_running", False), ("timer_seconds_left", total_seconds),
                                     ("timer_total", total_seconds), ("timer_start_time", None)]:
                    if key not in st.session_state:
                        st.session_state[key] = default

                if st.session_state.timer_running and st.session_state.timer_start_time:
                    elapsed = time.time() - st.session_state.timer_start_time
                    st.session_state.timer_seconds_left = max(0, st.session_state.timer_total - int(elapsed))
                    if st.session_state.timer_seconds_left == 0:
                        st.session_state.timer_running = False
                        st.session_state.timer_start_time = None

                mins = st.session_state.timer_seconds_left // 60
                secs = st.session_state.timer_seconds_left % 60

                if st.session_state.timer_seconds_left == 0 and st.session_state.timer_total > 0:
                    t_color, status_text = "#4caf50", "Complete! "
                elif st.session_state.timer_running:
                    t_color, status_text = "#ff9800", f"Running… ({mins}:{secs:02d})"
                else:
                    t_color, status_text = "#1976d2", "Ready to Start"

                st.markdown(f"""
                <div style='text-align:center; padding:30px; background:linear-gradient(135deg,{t_color},{t_color}cc);
                            border-radius:15px; color:white; margin:20px 0; box-shadow:0 8px 20px rgba(0,0,0,0.3);'>
                    <h1 style='font-size:4.5em; margin:0; font-weight:bold;'>{mins}:{secs:02d}</h1>
                    <p style='font-size:1.4em; margin-top:10px;'>{status_text}</p>
                </div>
                """, unsafe_allow_html=True)

                if st.session_state.timer_running and st.session_state.timer_seconds_left > 0:
                    time.sleep(1)
                    st.rerun()

                if st.session_state.timer_seconds_left == 0 and st.session_state.timer_total > 0 and not st.session_state.timer_running:
                    st.success("Timer Complete!")
                    st.balloons()

                tc1, tc2, tc3 = st.columns(3)
                with tc1:
                    if st.button("Start", use_container_width=True, disabled=st.session_state.timer_running):
                        st.session_state.timer_running = True
                        st.session_state.timer_seconds_left = total_seconds
                        st.session_state.timer_total = total_seconds
                        st.session_state.timer_start_time = time.time()
                        st.rerun()
                with tc2:
                    if st.button("Pause", use_container_width=True, disabled=not st.session_state.timer_running):
                        st.session_state.timer_running = False
                        st.session_state.timer_total = st.session_state.timer_seconds_left
                        st.session_state.timer_start_time = None
                        st.rerun()
                with tc3:
                    if st.button("Reset", use_container_width=True):
                        st.session_state.timer_running = False
                        st.session_state.timer_seconds_left = total_seconds
                        st.session_state.timer_total = total_seconds
                        st.session_state.timer_start_time = None
                        st.rerun()

                workout_duration_minutes = (st.session_state.timer_total - st.session_state.timer_seconds_left) / 60 if not st.session_state.timer_running else (time.time() - (st.session_state.timer_start_time or time.time())) / 60

            # - Interval timer 
            else:
                with timer_col2:
                    st.write("")

                ic1, ic2, ic3 = st.columns(3)
                with ic1:
                    work_time = st.number_input("Work (sec)", min_value=5, max_value=300, value=30, key="work_time")
                with ic2:
                    rest_time = st.number_input("Rest (sec)", min_value=5, max_value=300, value=10, key="rest_time")
                with ic3:
                    rounds = st.number_input("Rounds", min_value=1, max_value=50, value=8, key="rounds")

                for key, default in [("interval_running", False), ("interval_current_round", 1),
                                     ("interval_is_work", True), ("interval_seconds_left", work_time),
                                     ("interval_start_time", None), ("interval_completed", False)]:
                    if key not in st.session_state:
                        st.session_state[key] = default

                if st.session_state.interval_running and st.session_state.interval_start_time:
                    elapsed = time.time() - st.session_state.interval_start_time
                    period = work_time if st.session_state.interval_is_work else rest_time
                    st.session_state.interval_seconds_left = max(0, period - int(elapsed))
                    if st.session_state.interval_seconds_left == 0:
                        if st.session_state.interval_is_work:
                            st.session_state.interval_is_work = False
                            st.session_state.interval_seconds_left = rest_time
                            st.session_state.interval_start_time = time.time()
                        else:
                            if st.session_state.interval_current_round >= rounds:
                                st.session_state.interval_running = False
                                st.session_state.interval_completed = True
                            else:
                                st.session_state.interval_current_round += 1
                                st.session_state.interval_is_work = True
                                st.session_state.interval_seconds_left = work_time
                                st.session_state.interval_start_time = time.time()

                r_mins = st.session_state.interval_seconds_left // 60
                r_secs = st.session_state.interval_seconds_left % 60
                phase = "WORK" if st.session_state.interval_is_work else "REST"
                i_color = "#d32f2f" if st.session_state.interval_is_work else "#4caf50"

                st.markdown(f"""
                <div style='text-align:center; padding:25px; background:linear-gradient(135deg,{i_color},{i_color}cc);
                            border-radius:15px; color:white; margin:20px 0; box-shadow:0 8px 20px rgba(0,0,0,0.3);'>
                    <p style='font-size:1.4em; margin:0;'>{phase} — Round {st.session_state.interval_current_round}/{rounds}</p>
                    <h1 style='font-size:4.5em; margin:5px 0; font-weight:bold;'>{r_mins}:{r_secs:02d}</h1>
                </div>
                """, unsafe_allow_html=True)

                if st.session_state.interval_running:
                    time.sleep(1)
                    st.rerun()

                if st.session_state.interval_completed:
                    st.success("Interval session complete!")

                ic_b1, ic_b2, ic_b3 = st.columns(3)
                with ic_b1:
                    if st.button("Start", use_container_width=True, disabled=st.session_state.interval_running, key="int_start"):
                        st.session_state.interval_running = True
                        st.session_state.interval_completed = False
                        st.session_state.interval_current_round = 1
                        st.session_state.interval_is_work = True
                        st.session_state.interval_seconds_left = work_time
                        st.session_state.interval_start_time = time.time()
                        st.rerun()
                with ic_b2:
                    if st.button("Pause", use_container_width=True, disabled=not st.session_state.interval_running, key="int_pause"):
                        st.session_state.interval_running = False
                        st.session_state.interval_start_time = None
                        st.rerun()
                with ic_b3:
                    if st.button("Reset", use_container_width=True, key="int_reset"):
                        st.session_state.interval_running = False
                        st.session_state.interval_completed = False
                        st.session_state.interval_current_round = 1
                        st.session_state.interval_is_work = True
                        st.session_state.interval_seconds_left = work_time
                        st.session_state.interval_start_time = None
                        st.rerun()

                total_interval_sec = rounds * (work_time + rest_time)
                workout_duration_minutes = total_interval_sec / 60

            # - Cardio extra info 
            st.write("---")
            cc1, cc2 = st.columns(2)
            with cc1:
                distance_km = st.number_input("Distance (km) — optional", min_value=0.0, max_value=100.0, value=0.0, step=0.1)
            with cc2:
                if distance_km > 0:
                    speed_ref = {"Walk": 5, "Jog": 9, "Run": 12, "Sprint": 20}
                    est_speed = speed_ref.get(exercise_type, 10)
                    st.metric("Estimated Speed", f"~{est_speed} km/h")

            cardio_notes = st.text_area("Notes (optional)", placeholder="Route, feelings, pace notes…", key="cardio_notes")
            uploaded_file = st.file_uploader("Upload Photo (optional)", type=["jpg", "jpeg", "png"], key="cardio_photo")

            st.write("---")

            if st.button(" Save Cardio Session", type="primary", use_container_width=True, key="save_cardio"):
                duration_used = workout_duration_minutes if workout_duration_minutes > 0.1 else st.number_input("Session Duration (minutes)", min_value=1, max_value=300, value=20)

                points_earned = int(duration_used * 8)
                verification_status = "unverified"

                # Look up teacher's strictness setting
                teacher_key = user_data.get('teacher_class')
                strictness = 2  # default Standard
                if teacher_key and teacher_key in st.session_state.users_data:
                    strictness = st.session_state.users_data[teacher_key].get('verification_strictness', 2)

                if uploaded_file and has_openai:
                    from PIL import Image
                    image = Image.open(uploaded_file)
                    is_valid, feedback, confidence = verify_workout_with_openai(image, exercise_type, strictness)
                    if is_valid:
                        points_earned = int(duration_used * 12)
                        verification_status = "verified"
                        st.success(f"Verified! {feedback}")
                    else:
                        verification_status = "failed"
                elif uploaded_file:
                    verification_status = "mock"
                    points_earned = int(duration_used * 10)

                house_pts = duration_used / 60
                steps_per_min = {"Walk": 100, "Jog": 140, "Run": 170, "Sprint": 200}
                estimated_steps = int(steps_per_min.get(exercise_type, 120) * duration_used)

                # Store photo as base64 so teacher can review it
                photo_b64 = None
                if uploaded_file:
                    import base64, io as _io
                    from PIL import Image as _Img
                    _img = _Img.open(uploaded_file)
                    _buf = _io.BytesIO()
                    _img.save(_buf, format="JPEG", quality=60)
                    photo_b64 = base64.b64encode(_buf.getvalue()).decode()

                workout_entry = {
                    'name': exercise_type,
                    'date': datetime.now().strftime('%Y-%m-%d'),
                    'time': datetime.now().strftime('%H:%M'),
                    'duration': int(duration_used),
                    'intensity': intensity,
                    'distance_km': distance_km,
                    'estimated_steps': estimated_steps,
                    'notes': cardio_notes,
                    'points_earned': points_earned,
                    'ai_feedback': feedback if uploaded_file and has_openai else None,
                    'verification_status': verification_status,
                    'has_photo': photo_b64 is not None,
                    'photo_b64': photo_b64,
                    'teacher_override': False,
                    'workout_type': 'cardio'
                }

                user_data['exercises'].insert(0, workout_entry)
                user_data['total_points'] = user_data.get('total_points', 0) + points_earned
                user_data['house_points_contributed'] = user_data.get('house_points_contributed', 0) + house_pts
                user_data['total_workout_hours'] = user_data.get('total_workout_hours', 0) + house_pts

                # Also log to steps_data
                if 'steps_data' not in user_data:
                    user_data['steps_data'] = []
                steps_entry = {
                    'date': datetime.now().strftime('%Y-%m-%d'),
                    'type': 'run_walk',
                    'activity': exercise_type,
                    'distance_km': distance_km,
                    'duration_min': int(duration_used),
                    'steps': estimated_steps,
                    'points_earned': points_earned // 10,
                }
                user_data['steps_data'].insert(0, steps_entry)

                new_badges, badge_pts = check_and_award_badges(user_data)
                if new_badges:
                    user_data['badges'].extend(new_badges)
                    user_data['total_points'] += badge_pts
                    for badge in new_badges:
                        st.success(f"Badge: {badge['name']} (+{badge['points']} pts)")

                user_data['level'] = calculate_level(user_data['total_points'])[0]
                update_user_data(user_data)

                st.success(f"{exercise_type} saved! {int(duration_used)} min · ~{estimated_steps:,} steps · +{points_earned} pts")
                st.balloons()
                time.sleep(1)
                st.session_state.timer_running = False
                st.session_state.timer_seconds_left = 0
                st.session_state.timer_total = 0
                st.rerun()

    # 
    #  TAB 2 — WORKOUT HISTORY  (strength + cardio combined)
    # 
    with tab2:
        st.subheader("Workout History")

        user_data = get_user_data()

        if not user_data.get('exercises'):
            st.info("No workouts logged yet. Head to 'Log Workout' to get started!")
        else:
            exercises = user_data['exercises']

            # Summary stats
            total_workouts = len(exercises)
            total_mins = sum(ex.get('duration', 0) for ex in exercises)
            total_points_all = sum(ex.get('points_earned', 0) for ex in exercises)
            week_ago_str = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
            this_week = [ex for ex in exercises if ex['date'] >= week_ago_str]

            c1, c2, c3, c4 = st.columns(4)
            with c1: st.metric("Total Workouts", total_workouts)
            with c2: st.metric("Total Time", f"{total_mins} min")
            with c3: st.metric("Total Points", total_points_all)
            with c4: st.metric("This Week", len(this_week))

            st.write("")
            st.write("### Recent Workouts")

            for ex in exercises[:15]:
                wtype = ex.get('workout_type', 'counter')
                v_status = ex.get('verification_status', 'unverified')
                pts = ex.get('points_earned', 0)

                if v_status == 'verified':
                    border_color, status_icon = "#4caf50", "Verified"
                elif v_status == 'mock':
                    border_color, status_icon = "#1976d2", "Logged"
                else:
                    border_color, status_icon = "#ff9800", "Unverified"

                if wtype == 'cardio':
                    dist_str = f" · {ex.get('distance_km', 0):.1f} km" if ex.get('distance_km', 0) > 0 else ""
                    steps_str = f" · ~{ex.get('estimated_steps', 0):,} steps" if ex.get('estimated_steps') else ""
                    detail = f"{ex.get('duration', 0)} min{dist_str}{steps_str}"
                else:
                    reps_unit = ex.get('reps_unit', 'reps')
                    sets_str = f"{ex.get('sets', '?')} sets · {ex.get('total_reps', ex.get('duration', '?'))} {reps_unit}"
                    detail = f"{sets_str} · {ex.get('duration', 0)} min"

                st.markdown(f"""
                <div class="stat-card" style="border-left-color:{border_color};">
                    <strong>{ex['date']} {ex.get('time', '')}</strong> — {ex.get('name', 'Exercise')}
                    &nbsp;&nbsp;<span style="opacity:0.7">{status_icon}</span><br>
                     {detail} &nbsp;|&nbsp; {ex.get('intensity','N/A')} &nbsp;|&nbsp;  +{pts} pts
                    {f"<br><em>{ex.get('notes','')}</em>" if ex.get('notes') else ""}
                </div>
                """, unsafe_allow_html=True)

            # Breakdown chart
            st.write("")
            st.write("### Exercise Breakdown")
            exercise_counts = {}
            for ex in exercises:
                name = ex.get('name', 'Unknown')
                exercise_counts[name] = exercise_counts.get(name, 0) + 1
            df_chart = pd.DataFrame({'Exercise': list(exercise_counts.keys()), 'Count': list(exercise_counts.values())})
            st.bar_chart(df_chart.set_index('Exercise'))


def check_and_award_badges(user_data):
    """Check if user earned any new badges and award points"""
    badges_earned = []
    points_earned = 0

    existing_badges = [b['name'] for b in user_data.get('badges', [])]

    # NAPFA Badges
    if user_data.get('napfa_history'):
        latest_napfa = user_data['napfa_history'][-1]

        # First Gold Medal
        if 'First Gold' not in existing_badges and 'Gold' in latest_napfa['medal']:
            badges_earned.append({
                'name': 'First Gold',
                'description': 'Earned your first NAPFA Gold medal!',
                'date': datetime.now().strftime('%Y-%m-%d'),
                'points': 100
            })
            points_earned += 100

        # Perfect Score
        all_grade_5 = all(grade == 5 for grade in latest_napfa['grades'].values())
        if 'Perfect Score' not in existing_badges and all_grade_5:
            badges_earned.append({
                'name': 'Perfect Score',
                'description': 'All Grade 5s on NAPFA test!',
                'date': datetime.now().strftime('%Y-%m-%d'),
                'points': 200
            })
            points_earned += 200

    # Workout Badges
    if user_data.get('exercises'):
        total_workouts = len(user_data['exercises'])

        # Century Club
        if 'Century Club' not in existing_badges and total_workouts >= 100:
            badges_earned.append({
                'name': 'Century Club',
                'description': 'Completed 100 total workouts!',
                'date': datetime.now().strftime('%Y-%m-%d'),
                'points': 150
            })
            points_earned += 150

        # Fifty Strong
        if 'Fifty Strong' not in existing_badges and total_workouts >= 50:
            badges_earned.append({
                'name': 'Fifty Strong',
                'description': 'Completed 50 workouts!',
                'date': datetime.now().strftime('%Y-%m-%d'),
                'points': 75
            })
            points_earned += 75

        # Getting Started
        if 'Getting Started' not in existing_badges and total_workouts >= 10:
            badges_earned.append({
                'name': 'Getting Started',
                'description': 'Completed 10 workouts!',
                'date': datetime.now().strftime('%Y-%m-%d'),
                'points': 25
            })
            points_earned += 25

        # Check workout streak
        workout_dates = sorted(list(set([e['date'] for e in user_data['exercises']])), reverse=True)
        if len(workout_dates) >= 2:
            streak = 1
            current_date = datetime.strptime(workout_dates[0], '%Y-%m-%d')

            for i in range(1, len(workout_dates)):
                prev_date = datetime.strptime(workout_dates[i], '%Y-%m-%d')
                diff = (current_date - prev_date).days

                if diff <= 2:
                    streak += 1
                    current_date = prev_date
                else:
                    break

            # 7-day streak
            if 'Week Warrior' not in existing_badges and streak >= 7:
                badges_earned.append({
                    'name': 'Week Warrior',
                    'description': '7-day workout streak!',
                    'date': datetime.now().strftime('%Y-%m-%d'),
                    'points': 50
                })
                points_earned += 50

            # 30-day streak
            if 'Month Master' not in existing_badges and streak >= 30:
                badges_earned.append({
                    'name': 'Month Master',
                    'description': '30-day workout streak!',
                    'date': datetime.now().strftime('%Y-%m-%d'),
                    'points': 150
                })
                points_earned += 150

    # Sleep Badges
    if user_data.get('sleep_history'):
        # Check last 7 days
        week_ago = datetime.now() - timedelta(days=7)
        recent_sleep = [s for s in user_data['sleep_history']
                       if datetime.strptime(s['date'], '%Y-%m-%d') >= week_ago]

        if len(recent_sleep) >= 7:
            good_sleep_count = sum(1 for s in recent_sleep if s['hours'] >= 8)

            if 'Sleep Champion' not in existing_badges and good_sleep_count >= 7:
                badges_earned.append({
                    'name': 'Sleep Champion',
                    'description': '7 days of 8+ hours sleep!',
                    'date': datetime.now().strftime('%Y-%m-%d'),
                    'points': 50
                })
                points_earned += 50

    # Goal Badges
    if user_data.get('goals'):
        completed_goals = sum(1 for g in user_data['goals'] if g['progress'] >= 100)

        if 'Goal Crusher' not in existing_badges and completed_goals >= 5:
            badges_earned.append({
                'name': 'Goal Crusher',
                'description': 'Completed 5 fitness goals!',
                'date': datetime.now().strftime('%Y-%m-%d'),
                'points': 100
            })
            points_earned += 100

        if 'First Goal' not in existing_badges and completed_goals >= 1:
            badges_earned.append({
                'name': 'First Goal',
                'description': 'Completed your first goal!',
                'date': datetime.now().strftime('%Y-%m-%d'),
                'points': 30
            })
            points_earned += 30

    # Daily Login
    if 'Daily Visitor' not in existing_badges and user_data.get('login_streak', 0) >= 7:
        badges_earned.append({
            'name': 'Daily Visitor',
            'description': '7-day login streak!',
            'date': datetime.now().strftime('%Y-%m-%d'),
            'points': 40
        })
        points_earned += 40

    # House Badges (Phase 7 - NEW!)
    if user_data.get('role') == 'student' and user_data.get('house'):
        house_points = user_data.get('house_points_contributed', 0)

        # House Point Milestones
        if 'House Hero' not in existing_badges and house_points >= 100:
            badges_earned.append({
                'name': 'House Hero',
                'description': '100 points for your house!',
                'date': datetime.now().strftime('%Y-%m-%d'),
                'points': 150
            })
            points_earned += 150

        if 'House Champion' not in existing_badges and house_points >= 50:
            badges_earned.append({
                'name': 'House Champion',
                'description': '50 points for your house!',
                'date': datetime.now().strftime('%Y-%m-%d'),
                'points': 75
            })
            points_earned += 75

        if 'House Starter' not in existing_badges and house_points >= 10:
            badges_earned.append({
                'name': 'House Starter',
                'description': '10 points for your house!',
                'date': datetime.now().strftime('%Y-%m-%d'),
                'points': 25
            })
            points_earned += 25

    # Social Badges (Phase 7 - NEW!)
    if user_data.get('friends'):
        friend_count = len(user_data['friends'])

        if 'Social Butterfly' not in existing_badges and friend_count >= 10:
            badges_earned.append({
                'name': 'Social Butterfly',
                'description': '10 friends added!',
                'date': datetime.now().strftime('%Y-%m-%d'),
                'points': 50
            })
            points_earned += 50

        if 'Friend Finder' not in existing_badges and friend_count >= 5:
            badges_earned.append({
                'name': 'Friend Finder',
                'description': '5 friends added!',
                'date': datetime.now().strftime('%Y-%m-%d'),
                'points': 25
            })
            points_earned += 25

    # Group Badges (Phase 7 - NEW!)
    if user_data.get('groups'):
        group_count = len(user_data['groups'])

        if 'Group Leader' not in existing_badges and group_count >= 3:
            badges_earned.append({
                'name': 'Group Leader',
                'description': 'Member of 3 groups!',
                'date': datetime.now().strftime('%Y-%m-%d'),
                'points': 40
            })
            points_earned += 40

    # Consistency Badges (Phase 7 - NEW!)
    if user_data.get('exercises'):
        # Check workout variety
        exercise_types = set([e['name'] for e in user_data['exercises']])

        if ' Variety Master' not in existing_badges and len(exercise_types) >= 10:
            badges_earned.append({
                'name': ' Variety Master',
                'description': '10 different exercise types!',
                'date': datetime.now().strftime('%Y-%m-%d'),
                'points': 60
            })
            points_earned += 60

    # Total Hours Badge (Phase 7 - NEW!)
    total_hours = user_data.get('total_workout_hours', 0)

    if '⏰ Time Champion' not in existing_badges and total_hours >= 100:
        badges_earned.append({
            'name': '⏰ Time Champion',
            'description': '100 hours of exercise!',
            'date': datetime.now().strftime('%Y-%m-%d'),
            'points': 200
        })
        points_earned += 200

    if '⏰ Time Warrior' not in existing_badges and total_hours >= 50:
        badges_earned.append({
            'name': '⏰ Time Warrior',
            'description': '50 hours of exercise!',
            'date': datetime.now().strftime('%Y-%m-%d'),
            'points': 100
        })
        points_earned += 100

    if '⏰ Time Starter' not in existing_badges and total_hours >= 10:
        badges_earned.append({
            'name': '⏰ Time Starter',
            'description': '10 hours of exercise!',
            'date': datetime.now().strftime('%Y-%m-%d'),
            'points': 30
        })
        points_earned += 30

    return badges_earned, points_earned

def calculate_level(total_points):
    """Calculate user level based on total points"""
    if total_points < 50:
        return "Novice", 0, 50
    elif total_points < 150:
        return "Beginner", 50, 150
    elif total_points < 300:
        return "Intermediate", 150, 300
    elif total_points < 500:
        return "Advanced", 300, 500
    elif total_points < 800:
        return "Expert", 500, 800
    elif total_points < 1200:
        return "Master", 800, 1200
    else:
        return "Legend", 1200, 1200

def update_login_streak(user_data):
    """Update login streak for daily login tracking"""
    last_login = user_data.get('last_login')
    if last_login:
        last_login_date = datetime.fromisoformat(last_login).date()
        today = datetime.now().date()
        days_diff = (today - last_login_date).days

        if days_diff == 1:
            # Consecutive day
            user_data['login_streak'] = user_data.get('login_streak', 0) + 1
        elif days_diff == 0:
            # Same day, no change
            pass
        else:
            # Streak broken
            user_data['login_streak'] = 1
    else:
        user_data['login_streak'] = 1

    user_data['last_login'] = datetime.now().isoformat()
    return user_data

# Community and Social Features
def community_features():
    st.header("Community & Achievements")

    user_data = get_user_data()
    all_users = st.session_state.users_data

    # Create tabs
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "Houses",
        "Leaderboards",
        "My Achievements",
        "Friends",
        "Challenges",
        "Privacy Settings"
    ])

    with tab1:
        st.subheader("House System")
        st.write("Compete for house glory! Every hour you exercise earns 1 point for your house.")

        # Calculate house standings
        house_stats = {
            'yellow': {'points': 0, 'members': 0, 'workouts': 0, 'display': 'Yellow House', 'color': '#FFD700'},
            'red': {'points': 0, 'members': 0, 'workouts': 0, 'display': 'Red House', 'color': '#DC143C'},
            'blue': {'points': 0, 'members': 0, 'workouts': 0, 'display': 'Blue House', 'color': '#1E90FF'},
            'green': {'points': 0, 'members': 0, 'workouts': 0, 'display': 'Green House', 'color': '#32CD32'},
            'black': {'points': 0, 'members': 0, 'workouts': 0, 'display': 'Black House', 'color': '#2F4F4F'}
        }

        # Calculate total points for each house
        for username, data in all_users.items():
            if data.get('role') == 'student' and data.get('house'):
                house = data['house']
                if house in house_stats:
                    house_stats[house]['points'] += data.get('house_points_contributed', 0)
                    house_stats[house]['members'] += 1
                    house_stats[house]['workouts'] += len(data.get('exercises', []))

        # Sort houses by points
        sorted_houses = sorted(house_stats.items(), key=lambda x: x[1]['points'], reverse=True)

        # Display house leaderboard
        st.write("### House Standings")

        for rank, (house_name, stats) in enumerate(sorted_houses, 1):
            medal = "" if rank == 1 else "" if rank == 2 else "" if rank == 3 else f"{rank}."

            with st.container():
                st.markdown(f"""
                <div class="stat-card" style="background: linear-gradient(135deg, {stats['color']} 0%, {stats['color']}dd 100%); color: white; margin: 10px 0;">
                    <h2>{medal} {stats['display']}</h2>
                    <h1>{stats['points']:.1f} Points</h1>
                    <p style="font-size: 1.1em;">
                        {stats['members']} members |
                        {stats['workouts']} total workouts |
                        {(stats['points']/stats['members'] if stats['members'] > 0 else 0):.1f} pts/member
                    </p>
                </div>
                """, unsafe_allow_html=True)

        # User's house info
        if user_data.get('role') == 'student' and user_data.get('house'):
            st.write("")
            st.write("---")
            st.write("### Your House")

            user_house = user_data['house']
            user_house_stats = house_stats.get(user_house, {})

            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Your House", user_house_stats.get('display', user_house.title()))
            with col2:
                st.metric("Your Contribution", f"{user_data.get('house_points_contributed', 0):.1f} pts")
            with col3:
                st.metric("Total Workout Hours", f"{user_data.get('total_workout_hours', 0):.1f}h")

            # House rank
            house_rank = next((i+1 for i, (h, s) in enumerate(sorted_houses) if h == user_house), 0)
            if house_rank == 1:
                st.success(f"Your house is in 1ST PLACE! Keep it up!")
            elif house_rank == 2:
                st.info(f"Your house is in 2nd place. Keep training to reach 1st!")
            elif house_rank == 3:
                st.info(f"Your house is in 3rd place. Every workout counts!")
            else:
                st.warning(f"Your house is in {house_rank}th place. Time to train harder!")

            # Top contributors in user's house
            st.write("")
            st.write(f"###  Top Contributors - {user_house_stats.get('display', 'Your House')}")

            house_members = [(username, data) for username, data in all_users.items()
                           if data.get('house') == user_house and data.get('role') == 'student']
            house_members.sort(key=lambda x: x[1].get('house_points_contributed', 0), reverse=True)

            for idx, (username, member) in enumerate(house_members[:5], 1):
                medal = "" if idx == 1 else "" if idx == 2 else "" if idx == 3 else f"{idx}."
                points = member.get('house_points_contributed', 0)

                highlight = " (You)" if username == st.session_state.username else ""
                st.write(f"{medal} **{member['name']}**{highlight} - {points:.1f} points")
        else:
            st.info("Students: Your house information will appear here after you log workouts!")

    with tab2:
        st.subheader("Leaderboards & High Scores")

        if not user_data.get('show_on_leaderboards', False):
            st.warning("You're not visible on leaderboards. Update your privacy settings to join!")
            st.info("Go to 'Privacy Settings' tab to enable leaderboard participation.")

        # Create sub-tabs for different leaderboard types
        lb_tab1, lb_tab2, lb_tab3, lb_tab4, lb_tab5, lb_tab6 = st.tabs([
            " Global",
            "House Rankings",
            " High Scores",
            "Friends",
            "Groups",
            "Class"
        ])

        # Filter users who opted in to leaderboards
        leaderboard_users = {username: data for username, data in all_users.items()
                            if data.get('show_on_leaderboards', False) and data.get('role') == 'student'}

        with lb_tab1:
            st.write("###  Global Leaderboards")
            st.write("Compete with everyone who opted in!")

            if len(leaderboard_users) == 0:
                st.info("No users on leaderboards yet. Be the first to opt in!")
            else:
                global_board_type = st.selectbox("Select Ranking", [
                    "Total House Points",
                    "Weekly Warriors",
                    "Workout Streak",
                    "Total Workouts"
                ], key="global_board")

                if global_board_type == "Total House Points":
                    st.write("### Top House Point Earners")

                    rankings = []
                    for username, data in leaderboard_users.items():
                        points = data.get('house_points_contributed', 0)
                        if points > 0:
                            rankings.append({
                                'username': username,
                                'name': data['name'],
                                'points': points,
                                'house': data.get('house', 'N/A'),
                                'school': data.get('school', 'N/A')
                            })

                    rankings.sort(key=lambda x: x['points'], reverse=True)

                    for idx, user in enumerate(rankings[:20], 1):
                        medal = "" if idx == 1 else "" if idx == 2 else "" if idx == 3 else f"{idx}."
                        highlight = "" if user['username'] == st.session_state.username else ""

                        house_emoji = {'yellow': '🟡', 'red': '', 'blue': '', 'green': '🟢', 'black': ''}.get(user['house'], '')

                        st.write(f"{medal} {highlight}**{user['name']}** {house_emoji} - {user['points']:.1f} points")

                elif global_board_type == "Weekly Warriors":
                    st.write("### Most Workouts This Week")

                    week_ago = datetime.now() - timedelta(days=7)
                    weekly_counts = []

                    for username, data in leaderboard_users.items():
                        if data.get('exercises'):
                            weekly_workouts = [e for e in data['exercises']
                                             if datetime.strptime(e['date'], '%Y-%m-%d') >= week_ago]

                            if weekly_workouts:
                                weekly_counts.append({
                                    'username': username,
                                    'name': data['name'],
                                    'count': len(weekly_workouts),
                                    'total_time': sum(e['duration'] for e in weekly_workouts),
                                    'house': data.get('house', 'N/A')
                                })

                    weekly_counts.sort(key=lambda x: x['count'], reverse=True)

                    for idx, user in enumerate(weekly_counts[:20], 1):
                        medal = "" if idx == 1 else "" if idx == 2 else "" if idx == 3 else f"{idx}."
                        highlight = "" if user['username'] == st.session_state.username else ""
                        house_emoji = {'yellow': '🟡', 'red': '', 'blue': '', 'green': '🟢', 'black': ''}.get(user['house'], '')

                        st.write(f"{medal} {highlight}**{user['name']}** {house_emoji} - {user['count']} workouts ({user['total_time']} min)")

                elif global_board_type == "Workout Streak":
                    st.write("### Longest Workout Streaks")

                    streaks = []
                    for username, data in leaderboard_users.items():
                        if data.get('exercises'):
                            workout_dates = sorted(list(set([e['date'] for e in data['exercises']])), reverse=True)
                            if len(workout_dates) >= 1:
                                streak = 1
                                current_date = datetime.strptime(workout_dates[0], '%Y-%m-%d')

                                for i in range(1, len(workout_dates)):
                                    prev_date = datetime.strptime(workout_dates[i], '%Y-%m-%d')
                                    diff = (current_date - prev_date).days

                                    if diff <= 2:
                                        streak += 1
                                        current_date = prev_date
                                    else:
                                        break

                                streaks.append({
                                    'username': username,
                                    'name': data['name'],
                                    'streak': streak,
                                    'house': data.get('house', 'N/A')
                                })

                    streaks.sort(key=lambda x: x['streak'], reverse=True)

                    for idx, user in enumerate(streaks[:20], 1):
                        medal = "" if idx == 1 else "" if idx == 2 else "" if idx == 3 else f"{idx}."
                        highlight = "" if user['username'] == st.session_state.username else ""
                        house_emoji = {'yellow': '🟡', 'red': '', 'blue': '', 'green': '🟢', 'black': ''}.get(user['house'], '')

                        st.write(f"{medal} {highlight}**{user['name']}** {house_emoji} - {user['streak']} days ")

                else:  # Total Workouts
                    st.write("### Most Total Workouts")

                    rankings = []
                    for username, data in leaderboard_users.items():
                        total_workouts = len(data.get('exercises', []))
                        if total_workouts > 0:
                            rankings.append({
                                'username': username,
                                'name': data['name'],
                                'workouts': total_workouts,
                                'house': data.get('house', 'N/A')
                            })

                    rankings.sort(key=lambda x: x['workouts'], reverse=True)

                    for idx, user in enumerate(rankings[:20], 1):
                        medal = "" if idx == 1 else "" if idx == 2 else "" if idx == 3 else f"{idx}."
                        highlight = "" if user['username'] == st.session_state.username else ""
                        house_emoji = {'yellow': '🟡', 'red': '', 'blue': '', 'green': '🟢', 'black': ''}.get(user['house'], '')

                        st.write(f"{medal} {highlight}**{user['name']}** {house_emoji} - {user['workouts']} workouts")

        with lb_tab2:
            st.write("### House Rankings")
            st.write("See how each house member ranks!")

            user_house = user_data.get('house')

            if not user_house:
                st.warning("You need to be in a house to view house rankings!")
            else:
                house_display = {'yellow': 'Yellow', 'red': 'Red', 'blue': 'Blue',
                               'green': 'Green', 'black': 'Black'}.get(user_house, user_house.title())

                st.write(f"### {house_display} House Leaderboard")

                # Get all members of user's house who opted in
                house_members = {username: data for username, data in leaderboard_users.items()
                               if data.get('house') == user_house}

                if not house_members:
                    st.info("No house members on leaderboards yet. Encourage your housemates to opt in!")
                else:
                    house_rank_type = st.selectbox("Rank By", [
                        "House Points",
                        "NAPFA Score",
                        "Weekly Workouts"
                    ], key="house_rank")

                    rankings = []

                    if house_rank_type == "House Points":
                        for username, data in house_members.items():
                            points = data.get('house_points_contributed', 0)
                            rankings.append({
                                'username': username,
                                'name': data['name'],
                                'value': points,
                                'display': f"{points:.1f} points"
                            })

                    elif house_rank_type == "NAPFA Score":
                        for username, data in house_members.items():
                            if data.get('napfa_history'):
                                score = data['napfa_history'][-1]['total']
                                rankings.append({
                                    'username': username,
                                    'name': data['name'],
                                    'value': score,
                                    'display': f"{score}/30"
                                })

                    else:  # Weekly Workouts
                        week_ago = datetime.now() - timedelta(days=7)
                        for username, data in house_members.items():
                            if data.get('exercises'):
                                weekly = [e for e in data['exercises']
                                        if datetime.strptime(e['date'], '%Y-%m-%d') >= week_ago]
                                rankings.append({
                                    'username': username,
                                    'name': data['name'],
                                    'value': len(weekly),
                                    'display': f"{len(weekly)} workouts"
                                })

                    rankings.sort(key=lambda x: x['value'], reverse=True)

                    for idx, user in enumerate(rankings, 1):
                        medal = "" if idx == 1 else "" if idx == 2 else "" if idx == 3 else f"{idx}."
                        highlight = "" if user['username'] == st.session_state.username else ""

                        st.write(f"{medal} {highlight}**{user['name']}** - {user['display']}")

        with lb_tab3:
            st.write("###  NAPFA High Scores")
            st.write("Record-breaking performances!")

            if len(leaderboard_users) == 0:
                st.info("No users on leaderboards yet.")
            else:
                # Age and gender filters
                col1, col2 = st.columns(2)
                with col1:
                    score_age = st.selectbox("Age Group", ["All Ages"] + list(range(12, 19)), key="score_age")
                with col2:
                    score_gender = st.selectbox("Gender", ["All", "Male", "Female"], key="score_gender")

                # Filter users
                filtered = leaderboard_users
                if score_age != "All Ages":
                    filtered = {u: d for u, d in filtered.items() if d['age'] == score_age}
                if score_gender != "All":
                    gender_key = 'm' if score_gender == "Male" else 'f'
                    filtered = {u: d for u, d in filtered.items() if d['gender'] == gender_key}

                if not filtered:
                    st.info("No users in this category yet")
                else:
                    score_type = st.selectbox("Component", [
                        "Total NAPFA Score",
                        "Sit-Ups",
                        "Standing Broad Jump",
                        "Sit and Reach",
                        "Pull-Ups",
                        "Shuttle Run",
                        "2.4km Run"
                    ], key="score_component")

                    high_scores = []

                    component_map = {
                        'Sit-Ups': 'SU',
                        'Standing Broad Jump': 'SBJ',
                        'Sit and Reach': 'SAR',
                        'Pull-Ups': 'PU',
                        'Shuttle Run': 'SR',
                        '2.4km Run': 'RUN'
                    }

                    for username, data in filtered.items():
                        if data.get('napfa_history'):
                            latest = data['napfa_history'][-1]

                            if score_type == "Total NAPFA Score":
                                high_scores.append({
                                    'username': username,
                                    'name': data['name'],
                                    'score': latest['total'],
                                    'display': f"{latest['total']}/30",
                                    'house': data.get('house', 'N/A'),
                                    'age': data['age']
                                })
                            else:
                                component_key = component_map[score_type]
                                if component_key in latest['scores']:
                                    score_value = latest['scores'][component_key]

                                    if component_key in ['SR', 'RUN']:
                                        display = f"{score_value:.2f}s" if component_key == 'SR' else f"{int(score_value)}:{int((score_value % 1) * 60):02d}"
                                        reverse_sort = True
                                    else:
                                        display = f"{score_value}"
                                        reverse_sort = False

                                    high_scores.append({
                                        'username': username,
                                        'name': data['name'],
                                        'score': score_value,
                                        'display': display,
                                        'house': data.get('house', 'N/A'),
                                        'age': data['age']
                                    })

                    # Sort (lower is better for SR and RUN)
                    if score_type in ['Shuttle Run', '2.4km Run']:
                        high_scores.sort(key=lambda x: x['score'])
                    else:
                        high_scores.sort(key=lambda x: x['score'], reverse=True)

                    if high_scores:
                        st.write(f"### Top {score_type} Scores")

                        for idx, user in enumerate(high_scores[:15], 1):
                            medal = "" if idx == 1 else "" if idx == 2 else "" if idx == 3 else f"{idx}."
                            highlight = "" if user['username'] == st.session_state.username else ""
                            house_emoji = {'yellow': '🟡', 'red': '', 'blue': '', 'green': '🟢', 'black': ''}.get(user['house'], '')

                            st.write(f"{medal} {highlight}**{user['name']}** {house_emoji} (Age {user['age']}) - {user['display']}")

                        # Show record
                        if high_scores:
                            record_holder = high_scores[0]
                            st.success(f"**Record:** {record_holder['name']} - {record_holder['display']}")
                    else:
                        st.info("No scores available for this component")

        with lb_tab4:
            st.write("### Friends Leaderboard")
            st.write("Compete with your friends!")

            friends = user_data.get('friends', [])

            if not friends:
                st.info("Add friends to see friend leaderboards!")
            else:
                # Include self in friend leaderboard
                friend_users = {st.session_state.username: user_data}
                for friend in friends:
                    if friend in all_users:
                        friend_users[friend] = all_users[friend]

                friend_rank_type = st.selectbox("Rank By", [
                    "House Points",
                    "NAPFA Score",
                    "Total Workouts",
                    "Weekly Workouts"
                ], key="friend_rank")

                rankings = []

                if friend_rank_type == "House Points":
                    for username, data in friend_users.items():
                        points = data.get('house_points_contributed', 0)
                        rankings.append({
                            'username': username,
                            'name': data['name'],
                            'value': points,
                            'display': f"{points:.1f} points",
                            'house': data.get('house', 'N/A')
                        })

                elif friend_rank_type == "NAPFA Score":
                    for username, data in friend_users.items():
                        if data.get('napfa_history'):
                            score = data['napfa_history'][-1]['total']
                            rankings.append({
                                'username': username,
                                'name': data['name'],
                                'value': score,
                                'display': f"{score}/30",
                                'house': data.get('house', 'N/A')
                            })

                elif friend_rank_type == "Total Workouts":
                    for username, data in friend_users.items():
                        total = len(data.get('exercises', []))
                        rankings.append({
                            'username': username,
                            'name': data['name'],
                            'value': total,
                            'display': f"{total} workouts",
                            'house': data.get('house', 'N/A')
                        })

                else:  # Weekly Workouts
                    week_ago = datetime.now() - timedelta(days=7)
                    for username, data in friend_users.items():
                        if data.get('exercises'):
                            weekly = [e for e in data['exercises']
                                    if datetime.strptime(e['date'], '%Y-%m-%d') >= week_ago]
                            rankings.append({
                                'username': username,
                                'name': data['name'],
                                'value': len(weekly),
                                'display': f"{len(weekly)} workouts",
                                'house': data.get('house', 'N/A')
                            })

                rankings.sort(key=lambda x: x['value'], reverse=True)

                for idx, user in enumerate(rankings, 1):
                    medal = "" if idx == 1 else "" if idx == 2 else "" if idx == 3 else f"{idx}."
                    highlight = "" if user['username'] == st.session_state.username else ""
                    house_emoji = {'yellow': '🟡', 'red': '', 'blue': '', 'green': '🟢', 'black': ''}.get(user['house'], '')

                    st.write(f"{medal} {highlight}**{user['name']}** {house_emoji} - {user['display']}")

        with lb_tab5:
            st.write("### Group Leaderboards")
            st.write("See how your groups rank!")

            user_groups = user_data.get('groups', [])

            if not user_groups:
                st.info("Join a group to see group leaderboards!")
            else:
                all_groups = st.session_state.get('all_groups', {})

                selected_group_id = st.selectbox(
                    "Select Group",
                    user_groups,
                    format_func=lambda x: all_groups.get(x, {}).get('name', 'Unknown Group'),
                    key="select_group_lb"
                )

                group = all_groups.get(selected_group_id, {})

                if group:
                    st.write(f"### {group['name']} Leaderboard")

                    group_rank_type = st.selectbox("Rank By", [
                        "House Points",
                        "NAPFA Score",
                        "Total Workouts"
                    ], key="group_rank")

                    rankings = []

                    for member in group['members']:
                        member_data = all_users.get(member, {})

                        if group_rank_type == "House Points":
                            value = member_data.get('house_points_contributed', 0)
                            display = f"{value:.1f} points"
                        elif group_rank_type == "NAPFA Score":
                            if member_data.get('napfa_history'):
                                value = member_data['napfa_history'][-1]['total']
                                display = f"{value}/30"
                            else:
                                continue
                        else:  # Total Workouts
                            value = len(member_data.get('exercises', []))
                            display = f"{value} workouts"

                        rankings.append({
                            'username': member,
                            'name': member_data.get('name', 'Unknown'),
                            'value': value,
                            'display': display,
                            'house': member_data.get('house', 'N/A')
                        })

                    rankings.sort(key=lambda x: x['value'], reverse=True)

                    for idx, user in enumerate(rankings, 1):
                        medal = "" if idx == 1 else "" if idx == 2 else "" if idx == 3 else f"{idx}."
                        highlight = "" if user['username'] == st.session_state.username else ""
                        house_emoji = {'yellow': '🟡', 'red': '', 'blue': '', 'green': '🟢', 'black': ''}.get(user['house'], '')

                        st.write(f"{medal} {highlight}**{user['name']}** {house_emoji} - {user['display']}")

        with lb_tab6:
            st.write("### Class Leaderboard")
            st.write("See how your classmates are doing!")

            teacher_class_key = user_data.get('teacher_class')

            if not teacher_class_key or teacher_class_key not in st.session_state.users_data:
                st.info("Join a class via the **Privacy Settings** tab to see your class leaderboard!")
            else:
                teacher_info = st.session_state.users_data[teacher_class_key]
                class_label = teacher_info.get('class_label') or f"{teacher_info['name']}'s class"
                st.write(f"### {class_label}")

                # Get classmates (same teacher_class) who opted into leaderboards
                classmates = {username: data for username, data in leaderboard_users.items()
                              if data.get('teacher_class') == teacher_class_key}

                if not classmates:
                    st.info("No classmates are on the leaderboard yet!")
                else:
                    class_rank_type = st.selectbox("Rank By", [
                        "NAPFA Score",
                        "House Points",
                        "Total Workouts"
                    ], key="class_rank")

                    rankings = []

                    if class_rank_type == "NAPFA Score":
                        for username, data in classmates.items():
                            if data.get('napfa_history'):
                                score = data['napfa_history'][-1]['total']
                                rankings.append({'username': username, 'name': data['name'],
                                                 'value': score, 'display': f"{score}/30",
                                                 'house': data.get('house', 'N/A')})
                    elif class_rank_type == "House Points":
                        for username, data in classmates.items():
                            points = data.get('house_points_contributed', 0)
                            rankings.append({'username': username, 'name': data['name'],
                                             'value': points, 'display': f"{points:.1f} pts",
                                             'house': data.get('house', 'N/A')})
                    else:
                        for username, data in classmates.items():
                            total = len(data.get('exercises', []))
                            rankings.append({'username': username, 'name': data['name'],
                                             'value': total, 'display': f"{total} workouts",
                                             'house': data.get('house', 'N/A')})

                    rankings.sort(key=lambda x: x['value'], reverse=True)

                    for idx, user in enumerate(rankings, 1):
                        medal = "" if idx == 1 else "" if idx == 2 else "" if idx == 3 else f"{idx}."
                        highlight = "" if user['username'] == st.session_state.username else ""
                        house_emoji = {'yellow': '🟡', 'red': '', 'blue': '', 'green': '🟢', 'black': ''}.get(user['house'], '')
                        st.write(f"{medal} {highlight}**{user['name']}** {house_emoji} — {user['display']}")

    with tab3:
                st.write("### Longest Workout Streaks")

                streaks = []
                for username, data in leaderboard_users.items():
                    if data.get('exercises'):
                        workout_dates = sorted(list(set([e['date'] for e in data['exercises']])), reverse=True)
                        if len(workout_dates) >= 1:
                            streak = 1
                            current_date = datetime.strptime(workout_dates[0], '%Y-%m-%d')

                            for i in range(1, len(workout_dates)):
                                prev_date = datetime.strptime(workout_dates[i], '%Y-%m-%d')
                                diff = (current_date - prev_date).days

                                if diff <= 2:
                                    streak += 1
                                    current_date = prev_date
                                else:
                                    break

                            streaks.append({
                                'username': username,
                                'name': data['name'],
                                'streak': streak,
                                'age': data['age'],
                                'school': data.get('school', 'N/A')
                            })

                streaks.sort(key=lambda x: x['streak'], reverse=True)

                for idx, user in enumerate(streaks[:10], 1):
                    medal = "" if idx == 1 else "" if idx == 2 else "" if idx == 3 else f"{idx}."

                    highlight = "" if user['username'] == st.session_state.username else ""
                    st.write(f"{medal} {highlight}**{user['name']}** (@{user['username']}) - {user['streak']} days ")

    with tab3:
        st.subheader("My Achievements")

        # Check for new badges
        new_badges, new_points = check_and_award_badges(user_data)

        if new_badges:
            st.balloons()
            st.success(f"You earned {len(new_badges)} new badge(s) and {new_points} points!")

            for badge in new_badges:
                user_data['badges'].append(badge)
                user_data['total_points'] = user_data.get('total_points', 0) + badge['points']

            update_user_data(user_data)

        # Display level and progress
        current_level, level_min, level_max = calculate_level(user_data.get('total_points', 0))
        user_data['level'] = current_level
        update_user_data(user_data)

        st.write("### Your Progress")

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Level", current_level)
        with col2:
            st.metric("Total Points", user_data.get('total_points', 0))
        with col3:
            st.metric("Login Streak", f"{user_data.get('login_streak', 0)} days")

        # Progress bar to next level
        if current_level != "Legend":
            progress = (user_data.get('total_points', 0) - level_min) / (level_max - level_min)
            st.progress(progress)
            st.write(f"**Next Level:** {level_max - user_data.get('total_points', 0)} points to go!")
        else:
            st.success("You've reached the maximum level!")

        # Display badges
        st.write("")
        st.write("### Earned Badges")

        if user_data.get('badges'):
            # Sort by date
            badges = sorted(user_data['badges'], key=lambda x: x['date'], reverse=True)

            cols = st.columns(3)
            for idx, badge in enumerate(badges):
                with cols[idx % 3]:
                    st.markdown(f"""
                    <div style="background: linear-gradient(135deg, #1976d2 0%, #1565c0 100%);
                                padding: 15px; border-radius: 10px; color: white; margin: 5px;">
                        <h3>{badge['name']}</h3>
                        <p>{badge['description']}</p>
                        <small>Earned: {badge['date']} | +{badge['points']} pts</small>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.info("No badges earned yet. Keep working out to unlock achievements!")

        # Available badges to earn
        st.write("")
        st.write("### Available Badges")

        all_possible_badges = [
            "First Gold - Earn your first NAPFA Gold medal",
            "Perfect Score - All Grade 5s on NAPFA",
            "Century Club - Complete 100 workouts",
            "Fifty Strong - Complete 50 workouts",
            "Getting Started - Complete 10 workouts",
            "Week Warrior - 7-day workout streak",
            "Month Master - 30-day workout streak",
            "Sleep Champion - 7 days of 8+ hours sleep",
            "Goal Crusher - Complete 5 goals",
            "First Goal - Complete your first goal",
            "Daily Visitor - 7-day login streak"
        ]

        earned_names = [b['name'] for b in user_data.get('badges', [])]
        remaining = [b for b in all_possible_badges if not any(name in b for name in earned_names)]

        for badge in remaining:
            st.write(f" {badge}")

    with tab4:
        st.subheader("Friends")

        # Friend requests
        friend_requests = user_data.get('friend_requests', [])
        if friend_requests:
            st.write("### Friend Requests")
            for requester in friend_requests:
                col1, col2, col3 = st.columns([3, 1, 1])
                with col1:
                    requester_data = all_users.get(requester, {})
                    st.write(f"**{requester_data.get('name', 'Unknown')}** (@{requester})")
                with col2:
                    if st.button("Accept", key=f"accept_{requester}"):
                        # Initialize friends arrays if needed
                        if 'friends' not in user_data:
                            user_data['friends'] = []
                        if 'friends' not in all_users[requester]:
                            all_users[requester]['friends'] = []
                        
                        user_data['friends'].append(requester)
                        user_data['friend_requests'].remove(requester)

                        # Add to requester's friends too
                        all_users[requester]['friends'].append(st.session_state.username)

                        update_user_data(user_data)
                        save_users(all_users)
                        st.success(f"Added {requester} as friend!")
                        st.rerun()
                with col3:
                    if st.button("Decline", key=f"decline_{requester}"):
                        user_data['friend_requests'].remove(requester)
                        update_user_data(user_data)
                        st.rerun()

        # Add friend
        st.write("### Add Friend")
        st.caption("Enter the exact username (shown in Privacy Settings)")
        new_friend = st.text_input("Enter username", key="add_friend_input", placeholder="e.g., john_doe")
        if st.button("Send Friend Request"):
            if not new_friend.strip():
                st.error("Please enter a username!")
            elif new_friend.strip() in all_users:
                new_friend = new_friend.strip()
                if new_friend == st.session_state.username:
                    st.error("You can't add yourself!")
                elif new_friend in user_data.get('friends', []):
                    st.error("Already friends!")
                elif st.session_state.username in all_users[new_friend].get('friend_requests', []):
                    st.error("Request already sent!")
                else:
                    # Initialize friend_requests if it doesn't exist
                    if 'friend_requests' not in all_users[new_friend]:
                        all_users[new_friend]['friend_requests'] = []
                    
                    # Add request to target user
                    all_users[new_friend]['friend_requests'].append(st.session_state.username)
                    save_users(all_users)
                    st.success(f"Friend request sent to {new_friend}!")
                    st.info(f"They will see your request ({st.session_state.username}) in their Friends tab.")
            else:
                st.error(f"User '{new_friend.strip()}' not found. Check the spelling!")
                st.info("Tip: Ask your friend for their exact username from Privacy Settings.")

        # Friends list
        st.write("### My Friends")
        friends = user_data.get('friends', [])

        if friends:
            for friend in friends:
                friend_data = all_users.get(friend, {})

                with st.expander(f"{friend_data.get('name', 'Unknown')} (@{friend})"):
                    col1, col2 = st.columns(2)

                    with col1:
                        st.write(f"**Age:** {friend_data.get('age', 'N/A')}")
                        st.write(f"**School:** {friend_data.get('school', 'N/A')}")
                        st.write(f"**Level:** {friend_data.get('level', 'Novice')}")

                    with col2:
                        if friend_data.get('napfa_history'):
                            latest = friend_data['napfa_history'][-1]
                            st.write(f"**NAPFA:** {latest['total']}/30")
                            st.write(f"**Medal:** {latest['medal']}")

                        if friend_data.get('exercises'):
                            st.write(f"**Workouts:** {len(friend_data['exercises'])}")

                    # Recent activity
                    if friend_data.get('badges'):
                        recent_badge = friend_data['badges'][-1]
                        st.info(f"Recently earned: {recent_badge['name']}")

                    if st.button(f"Remove Friend", key=f"remove_{friend}"):
                        user_data['friends'].remove(friend)
                        all_users[friend]['friends'].remove(st.session_state.username)
                        update_user_data(user_data)
                        save_users(all_users)
                        st.rerun()
        else:
            st.info("No friends yet. Add friends to see their progress!")

        # GROUPS SECTION
        st.write("")
        st.write("---")
        st.write("## Groups")
        st.write("Create or join groups to workout together!")

        # Load groups from database (using a special key)
        if 'app_groups' not in st.session_state.users_data:
            st.session_state.users_data['app_groups'] = {}
            save_users(st.session_state.users_data)
        
        all_groups = st.session_state.users_data.get('app_groups', {})

        # Initialize user groups
        if 'groups' not in user_data:
            user_data['groups'] = []
            user_data['group_invites'] = []
            update_user_data(user_data)

        group_tab1, group_tab2 = st.tabs(["My Groups", "Create/Join Group"])

        with group_tab1:
            st.write("### My Groups")

            user_groups = user_data.get('groups', [])

            if user_groups:
                for group_id in user_groups:
                    group = all_groups.get(group_id, {})
                    if group:
                        with st.expander(f"{group['name']} ({len(group['members'])}/{group['max_members']} members)"):
                            st.write(f"**Type:** {group['type']}")
                            st.write(f"**Description:** {group['description']}")
                            st.write(f"**Admin:** {all_users.get(group['admin'], {}).get('name', 'Unknown')}")
                            st.write(f"**Created:** {group['created']}")

                            # Members list
                            st.write("")
                            st.write("**Members:**")
                            for member in group['members']:
                                member_data = all_users.get(member, {})
                                admin_badge = " " if member == group['admin'] else ""
                                st.write(f"• {member_data.get('name', 'Unknown')} (@{member}){admin_badge}")

                            # Group stats
                            st.write("")
                            group_workouts = sum([len(all_users.get(m, {}).get('exercises', [])) for m in group['members']])
                            group_house_points = sum([all_users.get(m, {}).get('house_points_contributed', 0) for m in group['members']])

                            col1, col2 = st.columns(2)
                            with col1:
                                st.metric("Total Workouts", group_workouts)
                            with col2:
                                st.metric("Total House Points", f"{group_house_points:.1f}")

                            # Group leaderboard
                            st.write("")
                            st.write("**Group Leaderboard:**")
                            member_scores = [(m, all_users.get(m, {}).get('house_points_contributed', 0))
                                           for m in group['members']]
                            member_scores.sort(key=lambda x: x[1], reverse=True)

                            for idx, (member, score) in enumerate(member_scores[:5], 1):
                                medal = "" if idx == 1 else "" if idx == 2 else "" if idx == 3 else f"{idx}."
                                member_name = all_users.get(member, {}).get('name', 'Unknown')
                                highlight = " " if member == st.session_state.username else ""
                                st.write(f"{medal} {member_name}{highlight} - {score:.1f} points")

                            # Invite friends (admin only)
                            if group['admin'] == st.session_state.username:
                                st.write("")
                                st.write("**Invite Friends:**")

                                available_friends = [f for f in user_data.get('friends', []) if f not in group['members']]

                                if available_friends and len(group['members']) < group['max_members']:
                                    invite_friend = st.selectbox(
                                        "Select friend",
                                        available_friends,
                                        format_func=lambda x: all_users.get(x, {}).get('name', 'Unknown'),
                                        key=f"invite_{group_id}"
                                    )

                                    if st.button(f"Send Invite", key=f"send_{group_id}"):
                                        if 'group_invites' not in all_users[invite_friend]:
                                            all_users[invite_friend]['group_invites'] = []
                                        all_users[invite_friend]['group_invites'].append(group_id)
                                        save_users(all_users)
                                        st.success(f"Invite sent!")
                                        st.rerun()
                                elif len(group['members']) >= group['max_members']:
                                    st.info("Group is full!")

                            # Leave group
                            if st.button(f"Leave Group", key=f"leave_{group_id}"):
                                group['members'].remove(st.session_state.username)
                                user_data['groups'].remove(group_id)
                                
                                # Save group changes to database
                                st.session_state.users_data['app_groups'][group_id] = group
                                save_users(st.session_state.users_data)
                                
                                update_user_data(user_data)
                                st.rerun()
            else:
                st.info("You're not in any groups yet. Create or join one in the other tab!")

        with group_tab2:
            st.write("### Create New Group")

            col1, col2 = st.columns(2)
            with col1:
                group_name = st.text_input("Group Name", placeholder="e.g., Running Club")
                group_description = st.text_area("Description", placeholder="Group goals...")

            with col2:
                group_type = st.selectbox("Type",
                                         ["Study Group", "CCA Team", "Running Club", "Gym Buddies", "General Fitness"])
                max_members = st.number_input("Max Members", min_value=2, max_value=50, value=10)

            if st.button("Create Group", type="primary"):
                if group_name:
                    group_id = f"group_{st.session_state.username}_{datetime.now().strftime('%Y%m%d%H%M%S')}"

                    new_group = {
                        'id': group_id,
                        'name': group_name,
                        'description': group_description,
                        'type': group_type,
                        'admin': st.session_state.username,
                        'members': [st.session_state.username],
                        'max_members': max_members,
                        'created': datetime.now().strftime('%Y-%m-%d'),
                        'total_points': 0
                    }

                    # Save to database
                    st.session_state.users_data['app_groups'][group_id] = new_group
                    save_users(st.session_state.users_data)
                    
                    user_data['groups'].append(group_id)
                    update_user_data(user_data)

                    st.success(f"Group '{group_name}' created!")
                    st.balloons()
                    st.rerun()
                else:
                    st.error("Please enter a group name")

            # Group Invites
            group_invites = user_data.get('group_invites', [])
            
            if group_invites:
                st.write("")
                st.write("### Group Invitations")

                for group_id in group_invites:
                    group = all_groups.get(group_id, {})
                    if group:
                        col1, col2, col3 = st.columns([3, 1, 1])
                        with col1:
                            st.write(f"**{group['name']}** - {group['type']}")
                        with col2:
                            if st.button("Join", key=f"join_{group_id}"):
                                if len(group['members']) < group['max_members']:
                                    group['members'].append(st.session_state.username)
                                    user_data['groups'].append(group_id)
                                    user_data['group_invites'].remove(group_id)
                                    
                                    # Save group changes to database
                                    st.session_state.users_data['app_groups'][group_id] = group
                                    save_users(st.session_state.users_data)
                                    
                                    update_user_data(user_data)
                                    st.success(f"Joined {group['name']}!")
                                    st.rerun()
                                else:
                                    st.error("Group is full!")
                        with col3:
                            if st.button("Decline", key=f"decline_{group_id}"):
                                user_data['group_invites'].remove(group_id)
                                update_user_data(user_data)
                                st.rerun()
                    else:
                        st.warning(f"Group invitation found but group no longer exists (ID: {group_id[:10]}...)")
            else:
                st.info("No group invitations yet. Friends will see you in their invite list once they create a group!")

    with tab5:
        st.subheader("Challenges")

        # Weekly Challenges
        st.write("### Weekly Challenges")

        # Define weekly challenges
        weekly_challenges = [
            {
                'name': 'Workout Warrior',
                'description': 'Complete 5 workouts this week',
                'target': 5,
                'type': 'workouts',
                'points': 50
            },
            {
                'name': 'Cardio King',
                'description': 'Total 150 minutes of exercise this week',
                'target': 150,
                'type': 'minutes',
                'points': 60
            },
            {
                'name': 'Early Bird',
                'description': 'Log 7 days of sleep tracking',
                'target': 7,
                'type': 'sleep',
                'points': 40
            }
        ]

        # Check progress
        week_ago = datetime.now() - timedelta(days=7)

        for challenge in weekly_challenges:
            with st.expander(f"{'' if challenge['name'] in [c['name'] for c in user_data.get('completed_challenges', [])] else ''} {challenge['name']} (+{challenge['points']} pts)", expanded=True):
                st.write(f"**Goal:** {challenge['description']}")

                # Calculate progress
                if challenge['type'] == 'workouts':
                    weekly_workouts = [e for e in user_data.get('exercises', [])
                                     if datetime.strptime(e['date'], '%Y-%m-%d') >= week_ago]
                    progress = len(weekly_workouts)
                elif challenge['type'] == 'minutes':
                    weekly_workouts = [e for e in user_data.get('exercises', [])
                                     if datetime.strptime(e['date'], '%Y-%m-%d') >= week_ago]
                    progress = sum(e['duration'] for e in weekly_workouts)
                else:  # sleep
                    weekly_sleep = [s for s in user_data.get('sleep_history', [])
                                  if datetime.strptime(s['date'], '%Y-%m-%d') >= week_ago]
                    progress = len(weekly_sleep)

                st.progress(min(progress / challenge['target'], 1.0))
                st.write(f"**Progress:** {progress}/{challenge['target']}")

                if progress >= challenge['target']:
                    completed_names = [c['name'] for c in user_data.get('completed_challenges', [])]
                    if challenge['name'] not in completed_names:
                        st.success("Challenge completed! Points awarded!")
                        user_data.setdefault('completed_challenges', []).append({
                            'name': challenge['name'],
                            'completed_date': datetime.now().strftime('%Y-%m-%d'),
                            'points': challenge['points']
                        })
                        user_data['total_points'] = user_data.get('total_points', 0) + challenge['points']
                        update_user_data(user_data)

        # Friend Challenges
        st.write("")
        st.write("###  Friend Challenges")

        friends = user_data.get('friends', [])
        if not friends:
            st.info("Add friends to create challenges with them!")
        else:
            selected_friend = st.selectbox("Challenge a friend", friends)

            challenge_types = [
                "Most workouts this week",
                "Highest NAPFA score",
                "Longest workout streak"
            ]

            challenge_type = st.selectbox("Challenge type", challenge_types)

            if st.button("Send Challenge"):
                st.success(f"Challenge sent to {selected_friend}! (Feature coming soon)")

        # Class Challenges
        st.write("")
        st.write("### Class Challenges")

        teacher_class_key = user_data.get('teacher_class')

        if teacher_class_key and teacher_class_key in st.session_state.users_data:
            teacher_info = st.session_state.users_data[teacher_class_key]
            class_label = teacher_info.get('class_label') or f"{teacher_info['name']}'s class"
            st.write(f"**Your Class:** {class_label}")

            # Get class members
            class_members = {u: d for u, d in all_users.items()
                             if d.get('teacher_class') == teacher_class_key and d.get('show_on_leaderboards', False)}

            if len(class_members) > 1:
                st.write(f"**Class Members on leaderboard:** {len(class_members)}")
                st.info("**Class Goal:** Average NAPFA score of 20+ by end of month!")

                napfa_scores = []
                for data in class_members.values():
                    if data.get('napfa_history'):
                        napfa_scores.append(data['napfa_history'][-1]['total'])

                if napfa_scores:
                    class_avg = sum(napfa_scores) / len(napfa_scores)
                    st.metric("Current Class Average", f"{class_avg:.1f}/30")
                    if class_avg >= 20:
                        st.success("Class goal achieved!")
            else:
                st.info("Not enough class members on leaderboards yet.")
        else:
            st.info("Join a class via **Privacy Settings** to participate in class challenges!")

    with tab6:
        st.subheader("Privacy Settings")
        
        # Show username
        st.write("### Your Account Info")
        st.info(f"""
        **Your Username:** `{st.session_state.username}`  
        **Your Name:** {user_data.get('name')}  
        **Email:** {user_data.get('email')}
        
        Use your **username** when adding friends or joining groups!
        """)
        
        st.write("")

        st.write("### Leaderboard Visibility")

        current_setting = user_data.get('show_on_leaderboards', False)
        new_setting = st.checkbox("Show me on public leaderboards", value=current_setting)

        if new_setting != current_setting:
            user_data['show_on_leaderboards'] = new_setting
            update_user_data(user_data)
            st.success("Settings updated!")
            st.rerun()

        st.info("When enabled, your stats will be visible on leaderboards. Your friends can always see your profile.")

        # Join / Leave Class
        st.write("")
        st.write("### Your Class")

        teacher_class_key = user_data.get('teacher_class')

        if teacher_class_key and teacher_class_key in st.session_state.users_data:
            teacher_info = st.session_state.users_data[teacher_class_key]
            class_label = teacher_info.get('class_label') or f"{teacher_info['name']}'s class"
            st.success(f"You are enrolled in **{class_label}** (Teacher: {teacher_info['name']})")

            if st.button("Leave Class", type="secondary"):
                # Remove student from teacher's list
                if teacher_class_key in st.session_state.users_data:
                    teacher_students = st.session_state.users_data[teacher_class_key].get('students', [])
                    if st.session_state.username in teacher_students:
                        teacher_students.remove(st.session_state.username)
                        st.session_state.users_data[teacher_class_key]['students'] = teacher_students
                user_data['teacher_class'] = None
                update_user_data(user_data)
                save_users(st.session_state.users_data)
                st.success("You have left the class.")
                st.rerun()
        else:
            st.info("You are not enrolled in any class yet.")
            join_code = st.text_input("Enter Class Code from your teacher", placeholder="e.g., ABC123", key="privacy_class_code")
            if st.button("Join Class", type="primary"):
                if not join_code.strip():
                    st.error("Please enter a class code.")
                else:
                    matched = False
                    for teacher_username, teacher_data_item in st.session_state.users_data.items():
                        if teacher_data_item.get('role') == 'teacher' and teacher_data_item.get('class_code', '').upper() == join_code.strip().upper():
                            current_students = teacher_data_item.get('students', [])
                            if len(current_students) >= 30:
                                st.error("This class is full (30/30 students). Contact your teacher.")
                            else:
                                user_data['teacher_class'] = teacher_username
                                update_user_data(user_data)
                                if st.session_state.username not in current_students:
                                    current_students.append(st.session_state.username)
                                    st.session_state.users_data[teacher_username]['students'] = current_students
                                    save_users(st.session_state.users_data)
                                label = teacher_data_item.get('class_label') or f"{teacher_data_item['name']}'s class"
                                st.success(f"Joined **{label}**!")
                                st.rerun()
                            matched = True
                            break
                    if not matched:
                        st.error("Invalid class code. Please check with your teacher.")

        # Personal Data Export (Phase 7 BONUS!)
        st.write("")
        st.write("### Export Your Data")
        st.write("Download all your personal fitness data")

        if st.button("Download My Data (JSON)", type="secondary"):
            import json

            # Create exportable data
            export_data = {
                'account_info': {
                    'name': user_data.get('name'),
                    'email': user_data.get('email'),
                    'age': user_data.get('age'),
                    'gender': 'Male' if user_data.get('gender') == 'm' else 'Female',
                    'school': user_data.get('school'),
                    'teacher_class': user_data.get('teacher_class'),
                    'house': user_data.get('house'),
                    'created': user_data.get('created'),
                    'role': user_data.get('role')
                },
                'fitness_data': {
                    'bmi_history': user_data.get('bmi_history', []),
                    'napfa_history': user_data.get('napfa_history', []),
                    'sleep_history': user_data.get('sleep_history', []),
                    'exercises': user_data.get('exercises', []),
                    'total_workout_hours': user_data.get('total_workout_hours', 0),
                    'house_points_contributed': user_data.get('house_points_contributed', 0)
                },
                'achievements': {
                    'badges': user_data.get('badges', []),
                    'level': user_data.get('level'),
                    'total_points': user_data.get('total_points', 0),
                    'login_streak': user_data.get('login_streak', 0)
                },
                'social': {
                    'friends': user_data.get('friends', []),
                    'groups': user_data.get('groups', [])
                },
                'goals': user_data.get('smart_goals', []),
                'exported_date': datetime.now().isoformat()
            }

            # Convert to JSON
            json_data = json.dumps(export_data, indent=2)

            st.download_button(
                label="Download JSON File",
                data=json_data,
                file_name=f"fittrack_data_{user_data.get('name', 'user')}_{datetime.now().strftime('%Y%m%d')}.json",
                mime="application/json"
            )

            st.success("Your data is ready for download!")
            st.info("This JSON file contains all your FitTrack data. Keep it safe as a backup!")

# AI Insights and Recommendations
def ai_insights():
    st.header("AI Fitness Coach")

    user_data = get_user_data()

    # Create tabs for AI features - cleaned up, removed empty/duplicate tabs
    tab1, tab2, tab3 = st.tabs([
        "ML Predictions",
        "SMART Goals",
        "AI Schedule Generator"
    ])

    with tab1:
        st.subheader("Machine Learning Predictions & Statistical Analysis")
        st.write("AI-powered predictions based on your performance data")

        # Check if enough data
        has_napfa = len(user_data.get('napfa_history', [])) > 0
        has_multiple_napfa = len(user_data.get('napfa_history', [])) >= 2
        has_sleep = len(user_data.get('sleep_history', [])) >= 7
        has_exercises = len(user_data.get('exercises', [])) >= 5

        # Prediction 1: When will you reach NAPFA Gold?
        st.write("### NAPFA Gold Prediction")

        if not has_napfa:
            st.info("Complete your first NAPFA test to get predictions!")
        elif not has_multiple_napfa:
            latest_napfa = user_data['napfa_history'][-1]
            current_score = latest_napfa['total']

            if current_score >= 21:
                st.success(f"You already have NAPFA Gold! (Score: {current_score}/30)")
            else:
                points_needed = 21 - current_score
                st.info(f"**Current Score:** {current_score}/30")
                st.info(f"**Points Needed for Gold:** {points_needed}")
                st.write("Complete another NAPFA test to get improvement rate predictions!")
        else:
            # ML Prediction: Linear regression on NAPFA scores
            napfa_history = user_data['napfa_history']
            scores = [test['total'] for test in napfa_history]
            dates = [datetime.strptime(test['date'], '%Y-%m-%d') for test in napfa_history]

            # Calculate improvement rate
            days_between = [(dates[i] - dates[i-1]).days for i in range(1, len(dates))]
            score_changes = [scores[i] - scores[i-1] for i in range(1, len(scores))]

            if sum(days_between) > 0:
                avg_improvement_per_day = sum(score_changes) / sum(days_between)
                avg_improvement_per_month = avg_improvement_per_day * 30

                current_score = scores[-1]

                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Current NAPFA", f"{current_score}/30")
                    st.metric("Improvement Rate", f"+{avg_improvement_per_month:.2f} pts/month")

                with col2:
                    if current_score >= 21:
                        st.success("Gold Medal Achieved!")
                    else:
                        points_needed = 21 - current_score
                        if avg_improvement_per_day > 0:
                            days_to_gold = points_needed / avg_improvement_per_day
                            months_to_gold = days_to_gold / 30
                            predicted_date = datetime.now() + timedelta(days=days_to_gold)

                            st.metric("Points to Gold", points_needed)
                            st.metric("Predicted Gold Date", predicted_date.strftime('%B %Y'))

                            st.info(f"At your current rate, you'll reach Gold in ~{months_to_gold:.1f} months!")
                        else:
                            st.warning("Your score is decreasing. Focus on training to improve!")

                # Show prediction chart
                st.write("### Score Projection")

                # Project next 6 months
                future_dates = [datetime.now() + timedelta(days=30*i) for i in range(7)]
                future_scores = [current_score + (avg_improvement_per_day * 30 * i) for i in range(7)]
                future_scores = [min(max(s, 0), 30) for s in future_scores]  # Cap at 0-30

                df = pd.DataFrame({
                    'Date': [d.strftime('%b %Y') for d in future_dates],
                    'Predicted Score': future_scores
                })

                st.line_chart(df.set_index('Date'))

                st.write(f"**Model:** Linear regression based on {len(napfa_history)} test(s)")
                st.write(f"**Confidence:** {'High' if len(napfa_history) >= 4 else 'Medium' if len(napfa_history) >= 3 else 'Low'}")

        st.write("---")

        # Prediction 2: Sleep Impact on Performance
        st.write("### Sleep Impact Analysis")

        if not has_sleep or not has_napfa:
            st.info("Track sleep for 7+ days and complete NAPFA to see correlation!")
        else:
            sleep_data = user_data['sleep_history']

            # Calculate average sleep
            avg_sleep_hours = sum([s['hours'] + s['minutes']/60 for s in sleep_data]) / len(sleep_data)

            # Analyze NAPFA performance vs sleep
            napfa_score = user_data['napfa_history'][-1]['total']

            # Statistical correlation (simplified)
            if avg_sleep_hours >= 8:
                performance_rating = "Optimal"
                color = "#4caf50"
                insight = "Your sleep supports peak performance! Keep it up."
                predicted_improvement = 0
            elif avg_sleep_hours >= 7:
                performance_rating = "Good"
                color = "#8bc34a"
                insight = "Good sleep, but getting 8+ hours could improve your NAPFA score by ~2-3 points."
                predicted_improvement = 2.5
            else:
                performance_rating = "Below Optimal"
                color = "#ff9800"
                insight = "Poor sleep is limiting your performance. Getting 8+ hours could improve your score by ~5 points!"
                predicted_improvement = 5

            col1, col2 = st.columns(2)
            with col1:
                st.metric("Average Sleep", f"{avg_sleep_hours:.1f} hours")
                st.metric("Current NAPFA", f"{napfa_score}/30")

            with col2:
                st.markdown(f'<div class="stat-card" style="background: {color}; color: white;"><h3>{performance_rating}</h3></div>', unsafe_allow_html=True)
                if predicted_improvement > 0:
                    st.metric("Potential Gain", f"+{predicted_improvement:.1f} points")

            st.info(f"**Insight:** {insight}")

            # Show correlation
            st.write("**Research shows:** Students who sleep 8+ hours score on average 15% higher on NAPFA tests.")

        st.write("---")

        # Prediction 3: Injury Risk Prediction
        st.write("### Injury Risk Assessment")

        if not has_exercises:
            st.info("Log 5+ workouts to get injury risk analysis!")
        else:
            exercises = user_data['exercises']

            # Calculate workout intensity distribution
            intensity_counts = {'Low': 0, 'Medium': 0, 'High': 0}
            for ex in exercises:
                intensity_counts[ex['intensity']] += 1

            total = sum(intensity_counts.values())
            high_intensity_ratio = intensity_counts['High'] / total if total > 0 else 0

            # Check workout frequency (last 2 weeks)
            two_weeks_ago = datetime.now() - timedelta(days=14)
            recent_workouts = [e for e in exercises
                             if datetime.strptime(e['date'], '%Y-%m-%d') >= two_weeks_ago]

            workouts_per_week = len(recent_workouts) / 2

            # Risk calculation
            risk_score = 0
            risk_factors = []

            if high_intensity_ratio > 0.7:
                risk_score += 30
                risk_factors.append("Too many high-intensity workouts (>70%)")

            if workouts_per_week > 6:
                risk_score += 25
                risk_factors.append("Insufficient rest days (<1 per week)")

            if workouts_per_week < 2:
                risk_score += 15
                risk_factors.append("Inconsistent training increases injury risk")

            # Sleep factor
            if has_sleep:
                if avg_sleep_hours < 7:
                    risk_score += 20
                    risk_factors.append("Poor sleep reduces recovery")

            # Determine risk level
            if risk_score >= 50:
                risk_level = "High Risk"
                risk_color = "#f44336"
                recommendation = " REDUCE intensity and take more rest days!"
            elif risk_score >= 25:
                risk_level = "Moderate Risk"
                risk_color = "#ff9800"
                recommendation = "Balance your training intensity and rest."
            else:
                risk_level = "Low Risk"
                risk_color = "#4caf50"
                recommendation = "Your training is well-balanced!"

            st.markdown(f'<div class="stat-card" style="background: {risk_color}; color: white;"><h2>Risk Level: {risk_level}</h2><p>{recommendation}</p></div>', unsafe_allow_html=True)

            if risk_factors:
                st.write("**Risk Factors:**")
                for factor in risk_factors:
                    st.write(factor)

            st.write("")
            st.write("**Injury Prevention Tips:**")
            st.write("1. Include 1-2 rest days per week")
            st.write("2. Mix high, medium, and low intensity workouts")
            st.write("3. Sleep 8+ hours for recovery")
            st.write("4. Warm up before and cool down after exercise")
            st.write("5. Listen to your body - rest if you feel pain")

    with tab2:
        st.subheader("SMART Goals System")
        st.write("Set Specific, Measurable, Achievable, Relevant, and Time-bound goals")

        # Initialize smart_goals if it doesn't exist
        if 'smart_goals' not in user_data:
            user_data['smart_goals'] = []
            update_user_data(user_data)

        # Create or view SMART goals
        goal_tab1, goal_tab2 = st.tabs(["Create New Goal", "My SMART Goals"])

        with goal_tab1:
            st.write("### Create a SMART Goal")

            # Goal type selection
            goal_category = st.selectbox(
                "Goal Category",
                ["NAPFA Improvement", "Weight Management", "Strength Building",
                 "Endurance Training", "Flexibility", "Consistency/Habits"]
            )

            # Specific
            st.write("#### Specific - What exactly do you want to achieve?")

            if goal_category == "NAPFA Improvement":
                specific_options = [
                    "Achieve NAPFA Gold Medal",
                    "Improve specific component to Grade 5",
                    "Increase total NAPFA score by X points",
                    "Get all components to Grade 3+"
                ]
                specific_goal = st.selectbox("Choose specific goal", specific_options)

                if "specific component" in specific_goal:
                    component = st.selectbox("Which component?",
                                            ["Sit-Ups", "Standing Broad Jump", "Sit and Reach",
                                             "Pull-Ups", "Shuttle Run", "2.4km Run"])
                    target_grade = 5
                elif "increase total" in specific_goal:
                    target_increase = st.number_input("Points to increase", min_value=1, max_value=10, value=3)

            elif goal_category == "Weight Management":
                current_weight = st.number_input("Current Weight (kg)", min_value=30.0, max_value=150.0, value=60.0)
                target_weight = st.number_input("Target Weight (kg)", min_value=30.0, max_value=150.0, value=58.0)
                specific_goal = f"Change weight from {current_weight}kg to {target_weight}kg"

            elif goal_category == "Strength Building":
                exercise = st.selectbox("Exercise", ["Push-ups", "Pull-ups", "Sit-ups", "Squats"])
                current_reps = st.number_input(f"Current max {exercise}", min_value=0, max_value=200, value=10)
                target_reps = st.number_input(f"Target {exercise}", min_value=0, max_value=200, value=20)
                specific_goal = f"Increase {exercise} from {current_reps} to {target_reps} reps"

            elif goal_category == "Endurance Training":
                distance = st.selectbox("Distance", ["1km", "2.4km", "5km", "10km"])
                current_time = st.text_input("Current time (min:sec)", value="10:00")
                target_time = st.text_input("Target time (min:sec)", value="9:00")
                specific_goal = f"Run {distance} from {current_time} to {target_time}"

            elif goal_category == "Flexibility":
                current_reach = st.number_input("Current Sit & Reach (cm)", min_value=0, max_value=100, value=30)
                target_reach = st.number_input("Target Sit & Reach (cm)", min_value=0, max_value=100, value=40)
                specific_goal = f"Improve flexibility from {current_reach}cm to {target_reach}cm"

            else:  # Consistency
                workout_days = st.number_input("Workouts per week", min_value=1, max_value=7, value=4)
                duration = st.number_input("For how many weeks?", min_value=1, max_value=52, value=8)
                specific_goal = f"Workout {workout_days} days/week for {duration} weeks"

            # Measurable
            st.write("#### Measurable - How will you track progress?")
            tracking_method = st.multiselect(
                "Tracking methods",
                ["Weekly NAPFA practice tests", "Daily workout logs", "Weekly measurements",
                 "Progress photos", "Performance records"],
                default=["Daily workout logs"]
            )

            # Achievable - AI calculates
            st.write("#### Achievable - Is this realistic?")

            # Calculate if goal is achievable based on current data
            timeline_weeks = st.slider("Timeline (weeks)", min_value=1, max_value=52, value=12)

            achievability = "Achievable"
            ai_feedback = ""

            if goal_category == "NAPFA Improvement":
                if user_data.get('napfa_history'):
                    current_napfa = user_data['napfa_history'][-1]['total']
                    if "Gold" in specific_goal and current_napfa < 15 and timeline_weeks < 12:
                        achievability = "Very Challenging"
                        ai_feedback = "This is ambitious! Consider extending timeline to 16+ weeks."
                    elif current_napfa >= 18:
                        achievability = "Highly Achievable"
                        ai_feedback = "Great goal! You're close to Gold already."
                    else:
                        ai_feedback = "Realistic with consistent training!"

            elif goal_category == "Weight Management":
                weight_change = abs(target_weight - current_weight)
                safe_rate = 0.5  # kg per week
                safe_weeks = weight_change / safe_rate

                if timeline_weeks < safe_weeks * 0.7:
                    achievability = "Too Aggressive"
                    ai_feedback = f"Recommended timeline: {int(safe_weeks)} weeks for safe {weight_change}kg change"
                else:
                    ai_feedback = "Safe and achievable rate!"

            st.info(f"**AI Assessment:** {achievability} - {ai_feedback}")

            # Relevant
            st.write("#### Relevant - Why is this important to you?")
            motivation = st.text_area("Your motivation",
                                     placeholder="e.g., I want to improve my fitness for school sports...")

            # Time-bound
            st.write("#### ⏰ Time-bound - When will you achieve this?")
            target_date = st.date_input("Target completion date",
                                        value=datetime.now() + timedelta(weeks=timeline_weeks))

            # AI generates milestones
            st.write("### AI-Generated Weekly Milestones")

            weeks = (target_date - datetime.now().date()).days // 7
            if weeks > 0:
                st.write(f"**Timeline:** {weeks} weeks")

                # Generate milestones
                milestones = []

                if goal_category == "NAPFA Improvement" and "total" in specific_goal.lower():
                    if user_data.get('napfa_history'):
                        points_per_week = target_increase / weeks
                        current_score = user_data['napfa_history'][-1]['total']

                        for week in range(1, min(weeks + 1, 9)):
                            milestone_score = current_score + (points_per_week * week)
                            milestones.append(f"**Week {week}:** Target score {milestone_score:.1f}/30")

                elif goal_category == "Weight Management":
                    weight_per_week = (target_weight - current_weight) / weeks

                    for week in range(1, min(weeks + 1, 9)):
                        milestone_weight = current_weight + (weight_per_week * week)
                        milestones.append(f"**Week {week}:** Target weight {milestone_weight:.1f}kg")

                elif goal_category == "Strength Building":
                    reps_per_week = (target_reps - current_reps) / weeks

                    for week in range(1, min(weeks + 1, 9)):
                        milestone_reps = int(current_reps + (reps_per_week * week))
                        milestones.append(f"**Week {week}:** Target {milestone_reps} {exercise}")

                for milestone in milestones:
                    st.write(milestone)

            # Save goal
            if st.button(" Save SMART Goal", type="primary"):
                smart_goal = {
                    'category': goal_category,
                    'specific': specific_goal,
                    'measurable': tracking_method,
                    'achievable': achievability,
                    'relevant': motivation,
                    'time_bound': target_date.strftime('%Y-%m-%d'),
                    'milestones': milestones,
                    'created_date': datetime.now().strftime('%Y-%m-%d'),
                    'progress': 0,
                    'weekly_checkpoints': []
                }

                user_data['smart_goals'].append(smart_goal)
                update_user_data(user_data)

                st.success("SMART Goal created!")
                st.balloons()
                time.sleep(1)
                st.rerun()

        with goal_tab2:
            st.write("### My Active SMART Goals")

            if not user_data['smart_goals']:
                st.info("No SMART goals yet. Create your first goal in the other tab!")
            else:
                for idx, goal in enumerate(user_data['smart_goals']):
                    with st.expander(f"{goal['specific']}", expanded=True):
                        col1, col2 = st.columns(2)

                        with col1:
                            st.write(f"**Category:** {goal['category']}")
                            st.write(f"**Target Date:** {goal['time_bound']}")
                            st.write(f"**Created:** {goal['created_date']}")
                            st.write(f"**Achievability:** {goal['achievable']}")

                        with col2:
                            st.write("**Tracking Methods:**")
                            for method in goal['measurable']:
                                st.write(f"• {method}")

                        st.write("")
                        st.write(f"**Motivation:** {goal['relevant']}")

                        # Progress tracking
                        st.write("")
                        st.write("### Progress Tracking")

                        new_progress = st.slider(
                            "Update Progress",
                            min_value=0,
                            max_value=100,
                            value=goal['progress'],
                            key=f"progress_{idx}"
                        )

                        if st.button("Update Progress", key=f"update_{idx}"):
                            user_data['smart_goals'][idx]['progress'] = new_progress
                            user_data['smart_goals'][idx]['weekly_checkpoints'].append({
                                'date': datetime.now().strftime('%Y-%m-%d'),
                                'progress': new_progress
                            })
                            update_user_data(user_data)
                            st.success("Progress updated!")
                            st.rerun()

                        # Show milestones
                        if goal.get('milestones'):
                            st.write("")
                            st.write("**Weekly Milestones:**")
                            for milestone in goal['milestones']:
                                st.write(milestone)

                        # Delete goal
                        if st.button(" Delete Goal", key=f"delete_{idx}"):
                            user_data['smart_goals'].pop(idx)
                            update_user_data(user_data)
                            st.rerun()


    with tab3:
        st.subheader("Comprehensive AI Schedule Generator")
        st.write("Generate a complete personalized schedule based on your fitness data!")

        # Check if user has necessary data
        has_napfa = len(user_data.get('napfa_history', [])) > 0
        has_bmi = len(user_data.get('bmi_history', [])) > 0
        has_sleep = len(user_data.get('sleep_history', [])) > 0

        if not has_napfa or not has_bmi or not has_sleep:
            st.warning("To generate a complete schedule, please complete:")
            if not has_napfa:
                st.write("- NAPFA Test")
            if not has_bmi:
                st.write("- BMI Calculation")
            if not has_sleep:
                st.write("- Sleep Tracking (at least 3 days)")
            st.info("Once you have this data, come back to generate your personalized schedule!")
        else:
            st.success("All data available! Ready to generate your schedule.")

            # Get latest data
            latest_napfa = user_data['napfa_history'][-1]
            latest_bmi_record = user_data['bmi_history'][-1]
            latest_bmi = latest_bmi_record['bmi']

            # Calculate body type
            body_type, body_description = calculate_body_type(
                latest_bmi_record['weight'],
                latest_bmi_record['height']
            )

            # Display current data
            st.write("### Your Current Data")

            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Latest BMI", f"{latest_bmi:.1f}")
                st.write(f"**Body Type:** {body_type}")
            with col2:
                st.metric("NAPFA Score", f"{latest_napfa['total']}/30")
                st.write(f"**Medal:** {latest_napfa['medal']}")
            with col3:
                sleep_week = [s for s in user_data['sleep_history'][-7:]]
                if sleep_week:
                    avg_sleep = sum([s['hours'] + s['minutes']/60 for s in sleep_week]) / len(sleep_week)
                    st.metric("Avg Sleep", f"{avg_sleep:.1f}h")
                    st.write(f"**Records:** {len(sleep_week)} days")

            st.write("---")

            # School schedule input
            st.write("### Your School Schedule")

            col1, col2 = st.columns(2)
            with col1:
                st.write("**Weekdays**")
                weekday_start = st.time_input("School Start Time (Weekdays)", value=datetime.strptime("06:30", "%H:%M").time(), key="weekday_start")
                weekday_end = st.time_input("School End Time (Weekdays)", value=datetime.strptime("19:00", "%H:%M").time(), key="weekday_end")

            with col2:
                st.write("**Weekends**")
                weekend_schedule = st.radio("Weekend Schedule",
                                           ["Full day available", "Half day (morning)", "Half day (afternoon)"],
                                           key="weekend_sched")

            # Generate button
            if st.button(" Generate My Complete Schedule", type="primary"):
                st.write("---")
                st.success("Your Personalized Schedule Generated!")

                # Analyze NAPFA weaknesses
                weak_stations = []
                for station, grade in latest_napfa['grades'].items():
                    if grade <= 2:  # D or E grade
                        weak_stations.append(station)

                # Determine focus areas
                focus_cardio = 'RUN' in weak_stations
                focus_strength = any(s in weak_stations for s in ['PU', 'SU'])
                focus_flexibility = 'SAR' in weak_stations

                # Weekly schedule
                st.write("### Your Weekly Training Schedule")

                schedule_data = {
                    "Monday": [],
                    "Tuesday": [],
                    "Wednesday": [],
                    "Thursday": [],
                    "Friday": [],
                    "Saturday": [],
                    "Sunday": []
                }

                # Build schedule based on analysis
                if focus_cardio:
                    schedule_data["Monday"].append({"time": "06:00-06:45", "activity": "Morning Run (2-3km)", "type": "Cardio"})
                    schedule_data["Wednesday"].append({"time": "17:30-18:15", "activity": "Interval Training", "type": "Cardio"})
                    schedule_data["Friday"].append({"time": "17:30-18:30", "activity": "Long Distance Run (3-4km)", "type": "Cardio"})

                if focus_strength:
                    schedule_data["Tuesday"].append({"time": "17:30-18:30", "activity": "Upper Body: Pull-ups, Push-ups, Sit-ups", "type": "Strength"})
                    schedule_data["Thursday"].append({"time": "17:30-18:30", "activity": "Core & Lower Body: Planks, Squats, Lunges", "type": "Strength"})
                    schedule_data["Saturday"].append({"time": "09:00-10:00", "activity": "Full Body Circuit Training", "type": "Strength"})

                if focus_flexibility:
                    schedule_data["Monday"].append({"time": "19:30-20:00", "activity": " Stretching & Flexibility", "type": "Flexibility"})
                    schedule_data["Wednesday"].append({"time": "19:30-20:00", "activity": " Yoga/Stretching", "type": "Flexibility"})
                    schedule_data["Friday"].append({"time": "19:30-20:00", "activity": " Deep Stretching", "type": "Flexibility"})

                # Add general workouts if no specific weaknesses
                if not weak_stations:
                    schedule_data["Monday"].append({"time": "06:00-06:45", "activity": "Morning Run (3km)", "type": "Cardio"})
                    schedule_data["Tuesday"].append({"time": "17:30-18:30", "activity": "Strength Training", "type": "Strength"})
                    schedule_data["Wednesday"].append({"time": "06:00-06:45", "activity": "Speed Work", "type": "Cardio"})
                    schedule_data["Thursday"].append({"time": "17:30-18:30", "activity": "Core & Upper Body", "type": "Strength"})
                    schedule_data["Friday"].append({"time": "17:30-18:30", "activity": "Endurance Run", "type": "Cardio"})
                    schedule_data["Saturday"].append({"time": "09:00-10:00", "activity": " Flexibility & Recovery", "type": "Flexibility"})

                # Add rest day
                schedule_data["Sunday"].append({"time": "All Day", "activity": " Rest & Recovery", "type": "Rest"})

                # Display schedule
                for day, activities in schedule_data.items():
                    if activities:
                        st.markdown(f"#### {day}")
                        for activity in activities:
                            activity_type = activity['type']
                            color = {
                                'Cardio': '#ff5722',
                                'Strength': '#2196f3',
                                'Flexibility': '#4caf50',
                                'Rest': '#9e9e9e'
                            }.get(activity_type, '#607d8b')

                            st.markdown(f"""
                            <div style="background: {color}; color: white; padding: 10px; border-radius: 8px; margin: 5px 0;">
                                <strong>{activity['time']}</strong><br>
                                {activity['activity']}
                            </div>
                            """, unsafe_allow_html=True)

                # Diet recommendations
                st.write("---")
                st.write("###  Nutrition Plan")

                if latest_bmi < 18.5:
                    st.info("**Goal:** Healthy weight gain with muscle building")
                    st.write("""
                    - **Daily Calories:** 2,800-3,200 kcal
                    - **Protein:** 1.8-2.2g per kg body weight
                    - **Meals:** 5-6 small meals throughout the day
                    - **Focus:** Lean proteins, complex carbs, healthy fats
                    """)
                elif latest_bmi > 25:
                    st.info("**Goal:** Healthy weight loss with muscle preservation")
                    st.write("""
                    - **Daily Calories:** 1,800-2,200 kcal
                    - **Protein:** 1.6-2.0g per kg body weight
                    - **Meals:** 4-5 balanced meals
                    - **Focus:** High protein, moderate carbs, healthy fats
                    """)
                else:
                    st.info("**Goal:** Maintain weight and build fitness")
                    st.write("""
                    - **Daily Calories:** 2,200-2,600 kcal
                    - **Protein:** 1.6-1.8g per kg body weight
                    - **Meals:** 4-5 balanced meals
                    - **Focus:** Balanced macros, nutrient-dense foods
                    """)

                # Sleep recommendations
                st.write("---")
                st.write("### Sleep Schedule")

                if avg_sleep < 8:
                    st.warning(f"You're averaging {avg_sleep:.1f}h - aim for 8-10h for teens!")
                    st.write("""
                    **Target:** 8-10 hours per night
                    - **Bedtime:** 22:00-22:30
                    - **Wake time:** 06:00-06:30
                    - **Pre-bed routine:** No screens 1hr before, light stretching
                    - **Weekend:** Keep similar schedule (±1 hour)
                    """)
                else:
                    st.success(f"Great sleep average: {avg_sleep:.1f}h - keep it up!")
                    st.write("""
                    **Target:** Maintain 8-10 hours per night
                    - **Bedtime:** 22:00-22:30
                    - **Wake time:** 06:00-06:30
                    - **Keep consistent schedule** on weekends too
                    """)

                # Specific recommendations based on weaknesses
                if weak_stations:
                    st.write("---")
                    st.write("### Focus Areas (Based on NAPFA Weaknesses)")

                    station_names = {
                        'SU': 'Sit-ups',
                        'SBJ': 'Standing Broad Jump',
                        'SAR': 'Sit & Reach',
                        'PU': 'Pull-ups',
                        'SR': 'Shuttle Run',
                        'RUN': '2.4km Run'
                    }

                    for station in weak_stations:
                        st.write(f"**{station_names.get(station, station)}** - Grade {['F', 'E', 'D', 'C', 'B', 'A'][latest_napfa['grades'].get(station, 0)]}")

                    st.info("Your training schedule above is customized to improve these areas. Stay consistent!")

                st.write("---")
                st.success("Schedule generated! Track your progress in the Exercise Log and NAPFA Test sections.")


def reminders_and_progress():
    st.header("Weekly Progress Report")

    user_data = get_user_data()

    # Quick Stats Widget (Phase 7 BONUS!)
    st.markdown("### Quick Stats")

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        total_workouts = len(user_data.get('exercises', []))
        st.metric("Total Workouts", total_workouts)

    with col2:
        house_points = user_data.get('house_points_contributed', 0)
        st.metric("House Points", f"{house_points:.1f}")

    with col3:
        total_badges = len(user_data.get('badges', []))
        st.metric("Badges", total_badges)

    with col4:
        level = user_data.get('level', 'Novice')
        st.metric(" Level", level)

    with col5:
        streak = user_data.get('login_streak', 0)
        st.metric("Streak", f"{streak} days")

    # Show progress bar for current level
    total_points = user_data.get('total_points', 0)
    level_name, min_points, max_points = calculate_level(total_points)

    if max_points > min_points:
        progress = min(100, ((total_points - min_points) / (max_points - min_points)) * 100)
        st.progress(progress / 100)
        st.caption(f"{total_points} / {max_points} points to next level")

    st.write("---")

    # Reminder Bar at the top
    st.markdown("###  Today's Reminders")

    today = datetime.now().strftime('%A')
    today_date = datetime.now().strftime('%Y-%m-%d')

    # Check scheduled activities for today
    today_activities = [s for s in user_data.get('schedule', []) if s['day'] == today]

    if today_activities:
        for activity in today_activities:
            st.info(f"⏰ **Today:** {activity['activity']} - {activity['time']} ({activity['duration']} min)")
    else:
        st.success(f"No workouts scheduled for {today}. Good rest day or add a session!")

    # Smart reminders based on data
    reminders = []

    # Check last NAPFA test
    if user_data.get('napfa_history'):
        last_napfa_date = datetime.strptime(user_data['napfa_history'][-1]['date'], '%Y-%m-%d')
        days_since_napfa = (datetime.now() - last_napfa_date).days
        if days_since_napfa > 30:
            reminders.append(f"It's been {days_since_napfa} days since your last NAPFA test. Consider retesting to track progress!")

    # Check last BMI
    if user_data.get('bmi_history'):
        last_bmi_date = datetime.strptime(user_data['bmi_history'][-1]['date'], '%Y-%m-%d')
        days_since_bmi = (datetime.now() - last_bmi_date).days
        if days_since_bmi > 14:
            reminders.append(f" Update your BMI - last recorded {days_since_bmi} days ago")

    # Check sleep tracking
    if user_data.get('sleep_history'):
        last_sleep_date = datetime.strptime(user_data['sleep_history'][-1]['date'], '%Y-%m-%d')
        if last_sleep_date.strftime('%Y-%m-%d') != today_date:
            reminders.append("Don't forget to log your sleep from last night!")
    else:
        reminders.append("Start tracking your sleep for better recovery insights!")

    # Check exercise logging
    if user_data.get('exercises'):
        last_exercise_date = datetime.strptime(user_data['exercises'][0]['date'], '%Y-%m-%d')
        days_since_exercise = (datetime.now() - last_exercise_date).days
        if days_since_exercise > 2:
            reminders.append(f"It's been {days_since_exercise} days since your last logged workout. Time to get moving!")
    else:
        reminders.append("Start logging your exercises to track your fitness journey!")

    # Check goals progress
    if user_data.get('goals'):
        for goal in user_data['goals']:
            target_date = datetime.strptime(goal['date'], '%Y-%m-%d')
            days_until = (target_date - datetime.now()).days
            if 0 <= days_until <= 7:
                reminders.append(f"Goal deadline approaching: '{goal['target']}' in {days_until} days!")

    if reminders:
        st.markdown("### Smart Reminders")
        for reminder in reminders:
            st.warning(reminder)

    st.write("---")

    # Weekly Progress Report
    st.markdown("### Your Weekly Summary")

    # Calculate date range
    today = datetime.now()
    week_ago = today - timedelta(days=7)

    # Create tabs for different metrics
    tab1, tab2, tab3, tab4 = st.tabs(["Overview", "Exercise Stats", "Sleep Analysis", "NAPFA Progress"])

    with tab1:
        st.subheader("This Week at a Glance")

        # Count activities this week
        exercises_this_week = [e for e in user_data.get('exercises', [])
                              if datetime.strptime(e['date'], '%Y-%m-%d') >= week_ago]

        sleep_this_week = [s for s in user_data.get('sleep_history', [])
                          if datetime.strptime(s['date'], '%Y-%m-%d') >= week_ago]

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Workouts Logged", len(exercises_this_week))
        with col2:
            if exercises_this_week:
                total_mins = sum([e['duration'] for e in exercises_this_week])
                st.metric("Total Exercise", f"{total_mins} min")
            else:
                st.metric("Total Exercise", "0 min")
        with col3:
            st.metric("Sleep Tracked", len(sleep_this_week))
        with col4:
            if sleep_this_week:
                avg_sleep = sum([s['hours'] + s['minutes']/60 for s in sleep_this_week]) / len(sleep_this_week)
                st.metric("Avg Sleep", f"{avg_sleep:.1f}h")
            else:
                st.metric("Avg Sleep", "No data")

        # All-time stats
        st.write("")
        st.markdown("#### All-Time Statistics")

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Total Workouts", len(user_data.get('exercises', [])))
        with col2:
            st.metric("NAPFA Tests", len(user_data.get('napfa_history', [])))
        with col3:
            st.metric("BMI Records", len(user_data.get('bmi_history', [])))
        with col4:
            st.metric("Active Goals", len(user_data.get('goals', [])))

        # Workout consistency
        if user_data.get('exercises'):
            st.write("")
            st.markdown("#### Workout Consistency")

            # Get unique workout dates
            workout_dates = list(set([e['date'] for e in user_data.get('exercises', [])]))
            workout_dates.sort(reverse=True)

            if len(workout_dates) >= 2:
                # Calculate streak
                streak = 1
                current_date = datetime.strptime(workout_dates[0], '%Y-%m-%d')

                for i in range(1, len(workout_dates)):
                    prev_date = datetime.strptime(workout_dates[i], '%Y-%m-%d')
                    diff = (current_date - prev_date).days

                    if diff <= 2:  # Allow 1 rest day
                        streak += 1
                        current_date = prev_date
                    else:
                        break

                if streak >= 3:
                    st.success(f"{streak} day streak! Keep it up!")
                else:
                    st.info(f"Current streak: {streak} days. Aim for 3+ for consistency!")

    with tab4:
        st.subheader("NAPFA Performance")

        if not user_data.get('napfa_history'):
            st.info("No NAPFA tests recorded yet. Complete your first test to track progress!")
        else:
            napfa_data = user_data['napfa_history']

            # Show latest scores
            latest = napfa_data[-1]
            st.write(f"**Latest Test:** {latest['date']}")
            st.write(f"**Total Score:** {latest['total']} points")
            st.write(f"**Medal:** {latest['medal']}")

            # Show grades breakdown
            test_names = {
                'SU': 'Sit-Ups',
                'SBJ': 'Standing Broad Jump',
                'SAR': 'Sit and Reach',
                'PU': 'Pull-Ups',
                'SR': 'Shuttle Run',
                'RUN': '2.4km Run'
            }

            st.write("")
            st.write("**Grade Breakdown:**")

            grades_df = pd.DataFrame([
                {
                    'Test': test_names[test],
                    'Score': latest['scores'][test],
                    'Grade': grade
                }
                for test, grade in latest['grades'].items()
            ])

            st.dataframe(grades_df, use_container_width=True, hide_index=True)

            # Progress over time
            if len(napfa_data) > 1:
                st.write("")
                st.write("**Progress Over Time:**")

                df = pd.DataFrame([
                    {'Date': test['date'], 'Total Score': test['total']}
                    for test in napfa_data
                ])
                df = df.set_index('Date')
                st.line_chart(df)

                # Calculate improvement
                first_score = napfa_data[0]['total']
                latest_score = napfa_data[-1]['total']
                improvement = latest_score - first_score

                if improvement > 0:
                    st.success(f"You've improved by {improvement} points since your first test!")
                elif improvement < 0:
                    st.warning(f" Score decreased by {abs(improvement)} points. Review your training plan.")
                else:
                    st.info("Score unchanged. Time to push harder!")

    with tab2:
        st.subheader("Exercise Statistics")

        if not user_data.get('exercises'):
            st.info("No exercises logged yet. Start logging your workouts!")
        else:
            exercises = user_data['exercises']

            # Total stats
            total_workouts = len(exercises)
            total_minutes = sum([e['duration'] for e in exercises])

            col1, col2 = st.columns(2)
            with col1:
                st.metric("Total Workouts", total_workouts)
            with col2:
                st.metric("Total Time", f"{total_minutes} min ({total_minutes/60:.1f} hrs)")

            # Exercise frequency
            st.write("")
            st.write("**Exercise Frequency:**")
            exercise_counts = {}
            for ex in exercises:
                exercise_counts[ex['name']] = exercise_counts.get(ex['name'], 0) + 1

            df_chart = pd.DataFrame({
                'Exercise': list(exercise_counts.keys()),
                'Count': list(exercise_counts.values())
            }).sort_values('Count', ascending=False)

            df_chart = df_chart.set_index('Exercise')
            st.bar_chart(df_chart)

            # Intensity breakdown
            st.write("")
            st.write("**Intensity Distribution:**")
            intensity_counts = {'Low': 0, 'Medium': 0, 'High': 0}
            for ex in exercises:
                intensity_counts[ex['intensity']] += 1

            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Low Intensity", intensity_counts['Low'])
            with col2:
                st.metric("Medium Intensity", intensity_counts['Medium'])
            with col3:
                st.metric("High Intensity", intensity_counts['High'])

            # Recent workouts
            st.write("")
            st.write("**Recent Workouts:**")
            recent = exercises[:5]  # Last 5
            for ex in recent:
                st.write(f"• {ex['date']}: {ex['name']} - {ex['duration']}min ({ex['intensity']} intensity)")

    with tab3:
        st.subheader("Sleep Analysis")

        if not user_data.get('sleep_history'):
            st.info("No sleep data yet. Start tracking your sleep!")
        else:
            sleep_data = user_data['sleep_history']

            # Calculate stats
            total_records = len(sleep_data)
            avg_hours = sum([s['hours'] + s['minutes']/60 for s in sleep_data]) / total_records

            quality_counts = {'Excellent': 0, 'Good': 0, 'Fair': 0, 'Poor': 0}
            for s in sleep_data:
                quality_counts[s['quality']] += 1

            # Display metrics
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Average Sleep", f"{avg_hours:.1f} hours")
            with col2:
                st.metric("Records Tracked", total_records)

            # Quality breakdown
            st.write("")
            st.write("**Sleep Quality Distribution:**")
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric(" Excellent", quality_counts['Excellent'])
            with col2:
                st.metric("Good", quality_counts['Good'])
            with col3:
                st.metric(" Fair", quality_counts['Fair'])
            with col4:
                st.metric("Poor", quality_counts['Poor'])

            # Sleep trend
            if len(sleep_data) > 1:
                st.write("")
                st.write("**Sleep Duration Trend:**")
                df = pd.DataFrame(sleep_data)
                df['total_hours'] = df['hours'] + df['minutes'] / 60
                df_chart = df.set_index('date')['total_hours']
                st.line_chart(df_chart)

            # Sleep insights
            st.write("")
            st.write("**Insights:**")
            if avg_hours >= 8:
                st.success("Excellent sleep habits! Keep it up for optimal recovery and performance.")
            elif avg_hours >= 7:
                st.info("Good sleep duration. Try to get closer to 8-10 hours for peak performance.")
            else:
                st.warning("You're not getting enough sleep. Aim for 8-10 hours for teenagers!")

            # Best and worst
            if len(sleep_data) >= 3:
                sleep_sorted = sorted(sleep_data, key=lambda x: x['hours'] + x['minutes']/60, reverse=True)
                best = sleep_sorted[0]
                worst = sleep_sorted[-1]

                st.write(f"**Best night:** {best['date']} - {best['hours']}h {best['minutes']}m")
                st.write(f"**Shortest night:** {worst['date']} - {worst['hours']}h {worst['minutes']}m")

# Advanced Health Metrics
def advanced_metrics():
    st.header("Advanced Health Metrics")
    st.write("Track detailed health and fitness metrics")

    user_data = get_user_data()

    # Create tabs
    tab1, tab2, tab3 = st.tabs([
        "BMR & Calories",
        "Heart Rate Zones",
        "Body Composition"
    ])

    with tab1:
        st.subheader("Basal Metabolic Rate (BMR) Calculator")
        st.write("Calculate your daily calorie needs")

        # Get user data
        if user_data.get('bmi_history'):
            latest_bmi = user_data['bmi_history'][-1]
            default_weight = latest_bmi['weight']
            default_height = latest_bmi['height'] * 100  # Convert to cm
        else:
            default_weight = 60.0
            default_height = 165.0

        col1, col2 = st.columns(2)
        with col1:
            weight = st.number_input("Weight (kg)", min_value=30.0, max_value=150.0,
                                    value=float(default_weight), step=0.1, key="bmr_weight")
            height = st.number_input("Height (cm)", min_value=100.0, max_value=250.0,
                                    value=float(default_height), step=0.5, key="bmr_height")

        with col2:
            age = get_user_age(user_data)
            gender = user_data.get('gender', 'm')

            st.metric("Age", age)
            st.metric("Gender", "Male" if gender == 'm' else "Female")

        activity_level = st.selectbox(
            "Activity Level",
            [
                "Sedentary (little/no exercise)",
                "Lightly Active (1-3 days/week)",
                "Moderately Active (3-5 days/week)",
                "Very Active (6-7 days/week)",
                "Extremely Active (athlete, 2x/day)"
            ],
            index=2
        )

        if st.button("Calculate BMR & Calories", type="primary"):
            # Mifflin-St Jeor Equation (most accurate for teens)
            if gender == 'm':
                bmr = (10 * weight) + (6.25 * height) - (5 * age) + 5
            else:
                bmr = (10 * weight) + (6.25 * height) - (5 * age) - 161

            # Activity multipliers
            activity_multipliers = {
                "Sedentary (little/no exercise)": 1.2,
                "Lightly Active (1-3 days/week)": 1.375,
                "Moderately Active (3-5 days/week)": 1.55,
                "Very Active (6-7 days/week)": 1.725,
                "Extremely Active (athlete, 2x/day)": 1.9
            }

            multiplier = activity_multipliers[activity_level]
            tdee = bmr * multiplier  # Total Daily Energy Expenditure

            # Calculate macros
            protein_grams = weight * 1.6  # 1.6g per kg for active teens
            protein_cals = protein_grams * 4

            fat_cals = tdee * 0.25  # 25% from fat
            fat_grams = fat_cals / 9

            carb_cals = tdee - protein_cals - fat_cals
            carb_grams = carb_cals / 4

            # Display results
            st.write("---")
            st.write("### Your Metabolic Profile")

            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("BMR", f"{bmr:.0f} cal/day")
                st.write("*Calories burned at rest*")

            with col2:
                st.metric("TDEE", f"{tdee:.0f} cal/day")
                st.write("*Total daily calories needed*")

            with col3:
                calories_per_workout = 300  # Average
                workout_days = 4  # Estimate
                weekly_exercise_cals = calories_per_workout * workout_days
                st.metric("Exercise Burns", f"{weekly_exercise_cals:.0f} cal/week")

            # Goals-based recommendations
            st.write("")
            st.write("### Calorie Targets by Goal")

            col1, col2, col3 = st.columns(3)

            with col1:
                st.markdown("""
                <div class="stat-card" style="background: #f44336; color: white;">
                    <h3>Weight Loss</h3>
                    <h2>{:.0f} cal/day</h2>
                    <p>Deficit: -500 cal/day</p>
                    <p>Rate: -0.5kg/week</p>
                </div>
                """.format(tdee - 500), unsafe_allow_html=True)

            with col2:
                st.markdown("""
                <div class="stat-card" style="background: #4caf50; color: white;">
                    <h3> Maintenance</h3>
                    <h2>{:.0f} cal/day</h2>
                    <p>No deficit/surplus</p>
                    <p>Maintain weight</p>
                </div>
                """.format(tdee), unsafe_allow_html=True)

            with col3:
                st.markdown("""
                <div class="stat-card" style="background: #2196f3; color: white;">
                    <h3>Muscle Gain</h3>
                    <h2>{:.0f} cal/day</h2>
                    <p>Surplus: +300 cal/day</p>
                    <p>Rate: +0.25kg/week</p>
                </div>
                """.format(tdee + 300), unsafe_allow_html=True)

            # Macronutrients
            st.write("")
            st.write("### Recommended Macronutrients")

            st.write(f"**For your activity level ({activity_level}):**")

            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Protein", f"{protein_grams:.0f}g/day")
                st.write(f"({protein_cals:.0f} cal)")
                st.progress(protein_cals / tdee)

            with col2:
                st.metric("Carbs", f"{carb_grams:.0f}g/day")
                st.write(f"({carb_cals:.0f} cal)")
                st.progress(carb_cals / tdee)

            with col3:
                st.metric("Fats", f"{fat_grams:.0f}g/day")
                st.write(f"({fat_cals:.0f} cal)")
                st.progress(fat_cals / tdee)

            # Save to user data
            if 'bmr_history' not in user_data:
                user_data['bmr_history'] = []

            user_data['bmr_history'].append({
                'date': datetime.now().strftime('%Y-%m-%d'),
                'bmr': round(bmr),
                'tdee': round(tdee),
                'weight': weight,
                'height': height,
                'activity_level': activity_level
            })
            update_user_data(user_data)

    with tab2:
        st.subheader("Heart Rate Training Zones")
        st.write("Optimize your training with heart rate zones")

        # Calculate max heart rate
        age = get_user_age(user_data)
        max_hr = 220 - age

        # Resting heart rate input
        st.write("### Calculate Your Training Zones")

        resting_hr = st.number_input(
            "Resting Heart Rate (bpm)",
            min_value=40,
            max_value=100,
            value=70,
            help="Measure first thing in the morning before getting out of bed"
        )

        # Heart Rate Reserve method (Karvonen Formula)
        hr_reserve = max_hr - resting_hr

        # Define zones
        zones = {
            "Zone 1 - Very Light": {
                "range": (0.50, 0.60),
                "description": "Recovery, warm-up",
                "benefits": "Promotes recovery, builds base endurance",
                "duration": "Long (45-60+ min)",
                "color": "#90caf9"
            },
            "Zone 2 - Light": {
                "range": (0.60, 0.70),
                "description": "Fat burning, base training",
                "benefits": "Builds aerobic base, burns fat",
                "duration": "Moderate-Long (30-60 min)",
                "color": "#81c784"
            },
            "Zone 3 - Moderate": {
                "range": (0.70, 0.80),
                "description": "Aerobic endurance",
                "benefits": "Improves cardiovascular fitness",
                "duration": "Moderate (20-40 min)",
                "color": "#fff176"
            },
            "Zone 4 - Hard": {
                "range": (0.80, 0.90),
                "description": "Lactate threshold",
                "benefits": "Increases NAPFA performance, speed",
                "duration": "Short-Moderate (10-30 min)",
                "color": "#ffb74d"
            },
            "Zone 5 - Maximum": {
                "range": (0.90, 1.00),
                "description": "VO2 Max, sprints",
                "benefits": "Max power, NAPFA 2.4km final sprint",
                "duration": "Very Short (1-5 min intervals)",
                "color": "#e57373"
            }
        }

        st.write("")
        st.write(f"### Your Heart Rate Zones (Max HR: {max_hr} bpm)")

        for zone_name, zone_info in zones.items():
            min_percent, max_percent = zone_info['range']
            min_hr = int(resting_hr + (hr_reserve * min_percent))
            max_hr_zone = int(resting_hr + (hr_reserve * max_percent))

            with st.expander(f"{zone_name}: {min_hr}-{max_hr_zone} bpm", expanded=True):
                st.markdown(f"""
                <div class="stat-card" style="background: {zone_info['color']};">
                    <h3>{zone_info['description']}</h3>
                    <h2>{min_hr} - {max_hr_zone} bpm</h2>
                    <p><strong>Benefits:</strong> {zone_info['benefits']}</p>
                    <p><strong>Duration:</strong> {zone_info['duration']}</p>
                </div>
                """, unsafe_allow_html=True)

        # NAPFA-specific recommendations
        st.write("")
        st.write("### NAPFA Training Recommendations")

        st.info("""
        **For 2.4km Run:**
        - Zone 2-3: 70% of training (build endurance)
        - Zone 4: 20% of training (improve speed)
        - Zone 5: 10% of training (final sprint power)

        **For Shuttle Run:**
        - Zone 4-5: High-intensity intervals
        - 30 sec sprints, 90 sec rest

        **For Recovery:**
        - Zone 1: Active recovery days
        - Light jogging or walking
        """)

        # Save resting HR
        if 'heart_rate_data' not in user_data:
            user_data['heart_rate_data'] = []

        if st.button("Save Resting HR"):
            user_data['heart_rate_data'].append({
                'date': datetime.now().strftime('%Y-%m-%d'),
                'resting_hr': resting_hr,
                'max_hr': max_hr
            })
            update_user_data(user_data)
            st.success("Resting heart rate saved!")

    with tab3:
        st.subheader("Body Composition Analyzer")
        st.write("Estimate body fat percentage using the Navy Method")

        # Get user data
        user_data = get_user_data()
        age = get_user_age(user_data)
        gender = user_data.get('gender', 'm')

        if user_data.get('bmi_history'):
            latest_bmi = user_data['bmi_history'][-1]
            default_weight = latest_bmi['weight']
            default_height = latest_bmi['height'] * 100  # Convert to cm
        else:
            default_weight = 60.0
            default_height = 165.0

        st.write("### Body Measurements")
        st.info("**Tip:** Use a measuring tape and measure at the widest/thickest point. Take measurements in the morning for consistency.")

        col1, col2 = st.columns(2)

        with col1:
            st.write("**Basic Info**")
            weight = st.number_input("Weight (kg)", min_value=30.0, max_value=150.0,
                                    value=float(default_weight), step=0.1, key="comp_weight")
            height_cm = st.number_input("Height (cm)", min_value=100.0, max_value=250.0,
                                       value=float(default_height), step=0.5, key="comp_height")

            st.metric("Age", age)
            st.metric("Gender", "Male" if gender == 'm' else "Female")

        with col2:
            st.write("**Circumference Measurements (cm)**")
            neck = st.number_input("Neck circumference", min_value=20.0, max_value=60.0,
                                  value=35.0, step=0.5,
                                  help="Measure just below the larynx (Adam's apple)")
            waist = st.number_input("Waist circumference", min_value=40.0, max_value=150.0,
                                   value=75.0, step=0.5,
                                   help="Measure at the narrowest point, usually at belly button level")

            if gender == 'f':
                hip = st.number_input("Hip circumference", min_value=50.0, max_value=180.0,
                                     value=95.0, step=0.5,
                                     help="Measure at the widest point of the hips")

        if st.button("Calculate Body Composition", type="primary"):
            # Navy Method formulas
            if gender == 'm':
                # Male formula
                body_fat_pct = (495 / (1.0324 - 0.19077 * np.log10(waist - neck) + 0.15456 * np.log10(height_cm))) - 450
            else:
                # Female formula
                body_fat_pct = (495 / (1.29579 - 0.35004 * np.log10(waist + hip - neck) + 0.22100 * np.log10(height_cm))) - 450

            # Calculate fat mass and lean mass
            fat_mass = (body_fat_pct / 100) * weight
            lean_mass = weight - fat_mass

            # Determine category based on age and gender
            if gender == 'm':
                if body_fat_pct < 6:
                    category = "Essential Fat Only"
                    color = "#2196f3"
                    desc = "Too low - health risks"
                elif body_fat_pct < 14:
                    category = "Athletes"
                    color = "#4caf50"
                    desc = "Athletic/Fit"
                elif body_fat_pct < 18:
                    category = "Fitness"
                    color = "#8bc34a"
                    desc = "Good fitness level"
                elif body_fat_pct < 25:
                    category = "Average"
                    color = "#ffc107"
                    desc = "Average range"
                else:
                    category = "Above Average"
                    color = "#ff9800"
                    desc = "Consider reducing"
            else:
                if body_fat_pct < 14:
                    category = "Essential Fat Only"
                    color = "#2196f3"
                    desc = "Too low - health risks"
                elif body_fat_pct < 21:
                    category = "Athletes"
                    color = "#4caf50"
                    desc = "Athletic/Fit"
                elif body_fat_pct < 25:
                    category = "Fitness"
                    color = "#8bc34a"
                    desc = "Good fitness level"
                elif body_fat_pct < 32:
                    category = "Average"
                    color = "#ffc107"
                    desc = "Average range"
                else:
                    category = "Above Average"
                    color = "#ff9800"
                    desc = "Consider reducing"

            # Display results
            st.write("---")
            st.write("### Your Body Composition")

            col1, col2, col3 = st.columns(3)

            with col1:
                st.markdown(f"""
                <div class="stat-card" style="background: {color}; color: white;">
                    <h3>Body Fat %</h3>
                    <h1>{body_fat_pct:.1f}%</h1>
                    <p><strong>{category}</strong></p>
                    <p>{desc}</p>
                </div>
                """, unsafe_allow_html=True)

            with col2:
                st.metric("Fat Mass", f"{fat_mass:.1f} kg")
                st.write(f"{(fat_mass/weight*100):.1f}% of body weight")

            with col3:
                st.metric("Lean Mass", f"{lean_mass:.1f} kg")
                st.write(f"{(lean_mass/weight*100):.1f}% of body weight")

            # Body composition breakdown chart
            st.write("")
            st.write("### Composition Breakdown")

            comp_data = pd.DataFrame({
                'Component': ['Fat Mass', 'Lean Mass'],
                'Weight (kg)': [fat_mass, lean_mass],
                'Percentage': [body_fat_pct, 100-body_fat_pct]
            })

            col1, col2 = st.columns(2)
            with col1:
                st.bar_chart(comp_data.set_index('Component')['Weight (kg)'])
            with col2:
                st.dataframe(comp_data, use_container_width=True)

            # Reference ranges
            st.write("")
            st.write("### Reference Ranges by Category")

            if gender == 'm':
                ref_data = {
                    'Category': ['Essential Fat', 'Athletes', 'Fitness', 'Average', 'Above Average'],
                    'Male (%)': ['2-5%', '6-13%', '14-17%', '18-24%', '25%+']
                }
            else:
                ref_data = {
                    'Category': ['Essential Fat', 'Athletes', 'Fitness', 'Average', 'Above Average'],
                    'Female (%)': ['10-13%', '14-20%', '21-24%', '25-31%', '32%+']
                }

            st.table(pd.DataFrame(ref_data))

            # Recommendations
            st.write("")
            st.write("### Personalized Recommendations")

            if body_fat_pct < (6 if gender == 'm' else 14):
                st.warning("""
                **Body Fat Too Low**
                - Increase calorie intake
                - Focus on healthy fats (nuts, avocado, olive oil)
                - Reduce intense cardio, increase strength training
                - Consult with a healthcare provider
                """)
            elif body_fat_pct > (25 if gender == 'm' else 32):
                st.info("""
                **Body Fat Reduction Tips**
                - Create moderate calorie deficit (300-500 cal/day)
                - Increase protein intake (1.6-2.0g per kg)
                - Combine cardio (3-4x/week) with strength training (3x/week)
                - Focus on NAPFA training for functional fitness
                - Track food intake for 2 weeks to identify patterns
                """)
            else:
                st.success("""
                **Healthy Range - Maintenance Tips**
                - Continue current training routine
                - Maintain balanced diet
                - Focus on NAPFA performance improvements
                - Build muscle through strength training
                - Monitor every 4-6 weeks for changes
                """)

            # NAPFA correlation
            st.write("")
            st.write("### Impact on NAPFA Performance")

            st.info("""
            **Body composition affects NAPFA scores:**

            - **Lower body fat** generally improves:
              - 2.4km run time (less weight to carry)
              - Pull-ups (better strength-to-weight ratio)
              - Shuttle run speed

            - **Higher lean mass** generally improves:
              - Standing broad jump (more power)
              - Pull-ups (more muscle)
              - Sit-ups (stronger core)

            - **Balanced composition** is key:
              - Too low body fat can reduce energy/performance
              - Optimal is athletic/fitness range for your gender
            """)

            # Save to history
            if 'body_comp_history' not in user_data:
                user_data['body_comp_history'] = []

            user_data['body_comp_history'].append({
                'date': datetime.now().strftime('%Y-%m-%d'),
                'body_fat_pct': round(body_fat_pct, 1),
                'fat_mass': round(fat_mass, 1),
                'lean_mass': round(lean_mass, 1),
                'weight': weight,
                'neck': neck,
                'waist': waist,
                'hip': hip if gender == 'f' else None
            })
            update_user_data(user_data)

            st.success("Body composition data saved to your history!")

        # Show history if available
        if user_data.get('body_comp_history') and len(user_data['body_comp_history']) > 1:
            st.write("")
            st.write("### Progress Tracking")

            df_comp = pd.DataFrame(user_data['body_comp_history'])
            df_comp['date'] = pd.to_datetime(df_comp['date'])

            col1, col2 = st.columns(2)

            with col1:
                st.write("**Body Fat % Trend**")
                st.line_chart(df_comp.set_index('date')['body_fat_pct'])

            with col2:
                st.write("**Lean Mass Trend**")
                st.line_chart(df_comp.set_index('date')['lean_mass'])

        # Method explanation
        st.write("")
        with st.expander("About the Navy Method"):
            st.write("""
            **The U.S. Navy Body Composition Method:**

            This is a validated method used by the U.S. military that estimates body fat percentage
            using circumference measurements. It's considered one of the most accurate non-clinical methods.

            **Advantages:**
            - No special equipment needed (just a measuring tape)
            - Good accuracy (within 3-4% of DEXA scans)
            - Easy to do at home
            - Tracks changes over time

            **Tips for Accurate Measurements:**
            1. Measure in the morning before eating
            2. Stand relaxed, don't suck in or flex
            3. Keep tape horizontal and snug (not tight)
            4. Take 2-3 measurements and use the average
            5. Same person should measure each time if possible

            **Note:** This is an estimate. For most accurate results, consider professional body composition
            testing (DEXA scan, hydrostatic weighing, or BodPod) if available.
            """)

# API Integrations
def api_integrations():
    st.header("API Integrations")
    st.write("Connect with external services for enhanced features")

    user_data = get_user_data()

    # Create tabs
    tab1, tab2, tab3 = st.tabs([
        "Weather API",
        "Nutrition API",
        "YouTube API"
    ])

    with tab1:
        st.subheader("Weather-Based Workout Recommendations")
        st.write("Get outdoor workout suggestions based on current weather")

        # Show API status
        if OPENWEATHER_API_KEY:
            st.success("Real Weather API Active")
        else:
            st.info("Using simulated weather data. Add API key to enable real-time weather.")

        location = st.text_input("Your Location", value="Singapore", placeholder="Enter city name")

        if st.button("Get Weather & Recommendations", type="primary"):

            if OPENWEATHER_API_KEY:
                # REAL API CALL
                try:
                    import requests

                    # OpenWeatherMap API endpoint
                    url = f"http://api.openweathermap.org/data/2.5/weather"
                    params = {
                        'q': location,
                        'appid': OPENWEATHER_API_KEY,
                        'units': 'metric'  # Get temperature in Celsius
                    }

                    response = requests.get(url, params=params)

                    if response.status_code == 200:
                        data = response.json()

                        # Extract weather data
                        temp = round(data['main']['temp'])
                        humidity = data['main']['humidity']
                        conditions = data['weather'][0]['main']
                        description = data['weather'][0]['description']

                        st.success(f"Real-time weather data from OpenWeatherMap")
                    else:
                        st.error(f"Error fetching weather: {response.status_code}")
                        # Fallback to mock data
                        temp, humidity, conditions = 30, 75, "Clear"

                except Exception as e:
                    st.error(f"API Error: {str(e)}")
                    st.info("Falling back to simulated data")
                    # Fallback to mock data
                    import random
                    temp = random.randint(25, 35)
                    humidity = random.randint(60, 90)
                    conditions = random.choice(["Clear", "Partly Cloudy", "Cloudy", "Light Rain", "Rainy"])

            else:
                # MOCK DATA (when no API key)
                import random
                temp = random.randint(25, 35)
                humidity = random.randint(60, 90)
                conditions = random.choice(["Clear", "Partly Cloudy", "Cloudy", "Light Rain", "Rainy"])

                if not OPENWEATHER_API_KEY:
                    st.warning("Simulated weather data (no API key configured)")

            # Display weather (same for both real and mock)
            st.write("### Current Weather")

            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric(" Temperature", f"{temp}°C")
            with col2:
                st.metric("Humidity", f"{humidity}%")
            with col3:
                st.metric(" Conditions", conditions)

            # Generate recommendations (same logic for both)
            st.write("")
            st.write("### Workout Recommendations")

            if temp < 28 and "Rain" not in conditions:
                recommendation = "Perfect for outdoor running!"
                workout = "2.4km NAPFA practice run"
                color = "#4caf50"
            elif temp < 32 and "Rain" not in conditions:
                recommendation = "Good for outdoor, stay hydrated"
                workout = "Morning or evening run (avoid midday)"
                color = "#ff9800"
            elif "Rain" in conditions:
                recommendation = "Indoor workout recommended"
                workout = "Indoor circuit: push-ups, sit-ups, burpees"
                color = "#2196f3"
            else:
                recommendation = " Too hot! Indoor training"
                workout = "Air-con gym or home workout"
                color = "#f44336"

            st.markdown(f"""
            <div class="stat-card" style="background: {color}; color: white;">
                <h3>{recommendation}</h3>
                <h4>Suggested: {workout}</h4>
            </div>
            """, unsafe_allow_html=True)

            # Hydration advice
            hydration_need = "High" if temp > 30 or humidity > 80 else "Moderate"
            st.info(f"**Hydration Need:** {hydration_need} - Drink {500 if hydration_need == 'High' else 300}ml before workout")

        # Setup instructions
        if not OPENWEATHER_API_KEY:
            st.write("")
            st.write("---")
            st.write("###  Enable Real-Time Weather")

            with st.expander("Setup Instructions", expanded=False):
                st.markdown("""
                **Step 1: Get Free API Key**
                1. Go to: https://openweathermap.org/api
                2. Click "Sign Up" (it's FREE!)
                3. Verify your email
                4. Go to "API Keys" tab
                5. Copy your API key

                **Step 2: Add to Streamlit Cloud**
                1. Deploy your app to Streamlit Cloud
                2. Go to your app settings ()
                3. Click "Secrets"
                4. Add this:
                ```
                OPENWEATHER_API_KEY = "your_api_key_here"
                ```
                5. Save and restart app

                **Step 3: Run Locally (Optional)**
                Create a file called `.streamlit/secrets.toml`:
                ```
                OPENWEATHER_API_KEY = "your_api_key_here"
                ```

                **That's it!** The app will automatically use real weather data.

                **Free Tier Limits:**
                - 1,000 API calls per day
                - 60 calls per minute
                - More than enough for personal use!
                """)


    with tab2:
        st.subheader("Food & Nutrition Database")
        st.write("Search nutritional information for any food")

        # Show API status
        if USDA_API_KEY:
            st.success("Real USDA Food Database Active (350,000+ foods)")
        else:
            st.info("Using sample food database. Add USDA API key for 350,000+ foods.")

        # Food search
        food_query = st.text_input("Search for a food", placeholder="e.g., chicken rice, banana, salmon")

        # Advanced search options
        with st.expander("Advanced Search Options"):
            col1, col2 = st.columns(2)
            with col1:
                food_category = st.selectbox(
                    "Food Category (optional)",
                    ["All Categories", "Dairy", "Fruits", "Vegetables", "Proteins",
                     "Grains", "Snacks", "Beverages", "Fast Foods"]
                )
            with col2:
                sort_by = st.selectbox(
                    "Sort by",
                    ["Relevance", "Protein (High to Low)", "Calories (Low to High)", "Calories (High to Low)"]
                )

        if st.button("Search Nutrition", type="primary"):

            if USDA_API_KEY:
                # REAL USDA API CALL
                try:
                    import requests

                    # FoodData Central API endpoint
                    url = "https://api.nal.usda.gov/fdc/v1/foods/search"

                    params = {
                        'api_key': USDA_API_KEY,
                        'query': food_query,
                        'pageSize': 10,  # Get top 10 results
                    }

                    # Note: Removed dataType filter as it can cause 400 errors
                    # The API will return the best matches automatically

                    response = requests.get(url, params=params)

                    if response.status_code == 200:
                        data = response.json()
                        foods = data.get('foods', [])

                        if foods:
                            st.success(f"Found {len(foods)} results from USDA database")

                            # Sort results if needed
                            if sort_by == "Protein (High to Low)":
                                foods = sorted(foods, key=lambda x: get_nutrient_from_food(x, 'Protein'), reverse=True)
                            elif sort_by == "Calories (Low to High)":
                                foods = sorted(foods, key=lambda x: get_nutrient_from_food(x, 'Energy'))
                            elif sort_by == "Calories (High to Low)":
                                foods = sorted(foods, key=lambda x: get_nutrient_from_food(x, 'Energy'), reverse=True)

                            # Display results
                            for food in foods[:5]:  # Show top 5
                                food_name = food.get('description', 'Unknown Food')
                                brand = food.get('brandOwner', '')

                                # Extract nutrients
                                nutrients = food.get('foodNutrients', [])

                                calories = get_nutrient_value(nutrients, 'Energy')
                                protein = get_nutrient_value(nutrients, 'Protein')
                                carbs = get_nutrient_value(nutrients, 'Carbohydrate, by difference')
                                fat = get_nutrient_value(nutrients, 'Total lipid (fat)')
                                fiber = get_nutrient_value(nutrients, 'Fiber, total dietary')
                                sugar = get_nutrient_value(nutrients, 'Sugars, total including NLEA')

                                # Handle alternative nutrient names
                                if calories is None:
                                    calories = get_nutrient_value(nutrients, 'Energy (Atwater General Factors)')
                                if carbs is None:
                                    carbs = get_nutrient_value(nutrients, 'Carbohydrate')
                                if fat is None:
                                    fat = get_nutrient_value(nutrients, 'Fat')

                                # Serving size
                                serving = food.get('servingSize', 100)
                                serving_unit = food.get('servingUnit', 'g')

                                with st.expander(f" {food_name}" + (f" ({brand})" if brand else ""), expanded=True):
                                    col1, col2 = st.columns([2, 1])

                                    with col1:
                                        st.write(f"**Serving Size:** {serving} {serving_unit}")

                                        col_a, col_b, col_c, col_d = st.columns(4)
                                        col_a.metric("Calories", f"{calories:.0f}" if calories else "N/A")
                                        col_b.metric("Protein", f"{protein:.1f}g" if protein else "N/A")
                                        col_c.metric("Carbs", f"{carbs:.1f}g" if carbs else "N/A")
                                        col_d.metric("Fat", f"{fat:.1f}g" if fat else "N/A")

                                        if fiber or sugar:
                                            st.write("")
                                            col_e, col_f = st.columns(2)
                                            if fiber:
                                                col_e.write(f"**Fiber:** {fiber:.1f}g")
                                            if sugar:
                                                col_f.write(f"**Sugars:** {sugar:.1f}g")

                                    with col2:
                                        # Macro ratio
                                        if calories and calories > 0:
                                            st.write("**Macro Ratio:**")
                                            p_cals = (protein or 0) * 4
                                            c_cals = (carbs or 0) * 4
                                            f_cals = (fat or 0) * 9
                                            total = p_cals + c_cals + f_cals

                                            if total > 0:
                                                st.write(f"Protein: {(p_cals/total*100):.0f}%")
                                                st.write(f"Carbs: {(c_cals/total*100):.0f}%")
                                                st.write(f"Fat: {(f_cals/total*100):.0f}%")

                                        # Health score (simple)
                                        health_score = calculate_health_score(protein, carbs, fat, fiber, sugar)
                                        if health_score:
                                            st.write("")
                                            st.metric("Health Score", f"{health_score}/10")
                        else:
                            st.warning(f"No results found for '{food_query}'. Try a different search term.")

                    elif response.status_code == 400:
                        st.error("API Error 400: Invalid request format")
                        st.write("**Debug Info:**")
                        st.write(f"Query: {food_query}")
                        try:
                            error_detail = response.json()
                            st.write(f"Error details: {error_detail}")
                        except:
                            st.write(f"Response: {response.text}")
                        st.info("Falling back to sample database")
                        show_mock_nutrition_data(food_query)

                    elif response.status_code == 403:
                        st.error("API Error 403: Invalid API key")
                        st.write("Please check your USDA_API_KEY in Streamlit Secrets")
                        st.info("Falling back to sample database")
                        show_mock_nutrition_data(food_query)

                    else:
                        st.error(f"API Error: {response.status_code}")
                        st.info("Falling back to sample database")
                        show_mock_nutrition_data(food_query)

                except Exception as e:
                    st.error(f"Error: {str(e)}")
                    st.info("Falling back to sample database")
                    show_mock_nutrition_data(food_query)

            else:
                # MOCK DATA (when no API key)
                show_mock_nutrition_data(food_query)

        # Setup instructions
        if not USDA_API_KEY:
            st.write("")
            st.write("---")
            st.write("###  Enable Full Food Database")

            with st.expander("Setup Instructions (2 minutes)", expanded=False):
                st.markdown("""
                **Step 1: Get FREE API Key**
                1. Go to: https://fdc.nal.usda.gov/api-key-signup.html
                2. Fill in:
                   - First Name
                   - Last Name
                   - Email Address
                   - Organization: "School of Science and Technology" (or "Personal")
                3. Click "Sign Up"
                4. Check your email for API key
                5. Copy the key (long string of letters/numbers)

                **Step 2: Add to Streamlit Cloud**
                1. Go to your deployed app
                2. Click Settings → Secrets
                3. Add this line:
                ```
                USDA_API_KEY = "your_api_key_here"
                ```
                4. Save and restart

                **Step 3: Test**
                1. Come back to this page
                2. Should see "Real USDA Food Database Active"
                3. Search any food - get instant results!

                **What You Get:**
                - 350,000+ foods (vs. 5 sample foods)
                - Brand name foods
                - Restaurant foods
                - Complete nutrient data (vitamins, minerals, etc.)
                - Serving size info
                - Unlimited searches (FREE forever!)

                **Free Tier:**
                - 1,000 requests per hour
                - No daily limit
                - No credit card needed
                - FREE forever!
                """)

    with tab3:
        st.subheader("Exercise Tutorial Videos")
        st.write("Curated YouTube videos for NAPFA components and exercises")

        st.info("We use curated video links for best quality tutorials!")

        # NAPFA Component Videos
        st.write("### NAPFA Component Tutorials")

        napfa_videos = {
            "Sit-Ups": "https://www.youtube.com/results?search_query=proper+sit+ups+form",
            "Standing Broad Jump": "https://www.youtube.com/results?search_query=standing+broad+jump+technique",
            "Sit and Reach": "https://www.youtube.com/results?search_query=sit+and+reach+flexibility",
            "Pull-Ups": "https://www.youtube.com/results?search_query=pull+ups+tutorial",
            "Shuttle Run": "https://www.youtube.com/results?search_query=shuttle+run+technique",
            "2.4km Run": "https://www.youtube.com/results?search_query=running+form+tips"
        }

        for component, url in napfa_videos.items():
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write(f"**{component}**")
            with col2:
                st.link_button("Watch Videos", url, type="secondary")

        st.write("")
        st.write("### General Workout Videos")

        workout_videos = {
            "Strength Training": "https://www.youtube.com/results?search_query=strength+training+beginners",
            "Cardio Workouts": "https://www.youtube.com/results?search_query=cardio+workout+home",
            "Flexibility & Stretching": "https://www.youtube.com/results?search_query=flexibility+stretching+routine",
            "HIIT Training": "https://www.youtube.com/results?search_query=HIIT+workout",
            "Warm Up Exercises": "https://www.youtube.com/results?search_query=dynamic+warm+up",
            "Cool Down Stretches": "https://www.youtube.com/results?search_query=cool+down+stretches"
        }

        for workout, url in workout_videos.items():
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write(f"**{workout}**")
            with col2:
                st.link_button("Watch Videos", url, type="secondary")

        st.write("")
        st.success("All video links lead to curated YouTube search results for best tutorials!")

# Helper functions for USDA API
def get_nutrient_from_food(food, nutrient_name):
    """Extract nutrient value from food object for sorting"""
    nutrients = food.get('foodNutrients', [])
    value = get_nutrient_value(nutrients, nutrient_name)
    return value if value is not None else 0

def get_nutrient_value(nutrients, nutrient_name):
    """Extract nutrient value from USDA food data"""
    for nutrient in nutrients:
        # Check nutrient name
        name = nutrient.get('nutrientName', '')
        if nutrient_name.lower() in name.lower():
            return nutrient.get('value', 0)
    return None

def calculate_health_score(protein, carbs, fat, fiber, sugar):
    """Simple health score calculation (1-10)"""
    if not all([protein is not None, carbs is not None, fat is not None]):
        return None

    score = 5.0  # Start at neutral

    # High protein is good
    if protein and protein > 10:
        score += 1.5
    elif protein and protein > 5:
        score += 0.5

    # High fiber is good
    if fiber and fiber > 5:
        score += 1.5
    elif fiber and fiber > 2:
        score += 0.5

    # High sugar is bad
    if sugar and sugar > 20:
        score -= 2.0
    elif sugar and sugar > 10:
        score -= 1.0

    # Balance of macros
    total = protein + carbs + fat
    if total > 0:
        protein_ratio = protein / total
        if 0.2 <= protein_ratio <= 0.4:  # Good protein ratio
            score += 1.0

    return max(1, min(10, round(score, 1)))

def show_mock_nutrition_data(food_query):
    """Display mock nutrition data when API not available"""
    # Simulated nutrition database
    nutrition_db = {
        "chicken rice": {
            "calories": 607,
            "protein": 25,
            "carbs": 86,
            "fat": 15,
            "fiber": 2,
            "sugar": 3,
            "serving": "1 plate (350g)"
        },
        "banana": {
            "calories": 105,
            "protein": 1.3,
            "carbs": 27,
            "fat": 0.4,
            "fiber": 3.1,
            "sugar": 14,
            "serving": "1 medium (118g)"
        },
        "apple": {
            "calories": 95,
            "protein": 0.5,
            "carbs": 25,
            "fat": 0.3,
            "fiber": 4.4,
            "sugar": 19,
            "serving": "1 medium (182g)"
        },
        "white rice": {
            "calories": 204,
            "protein": 4.2,
            "carbs": 45,
            "fat": 0.4,
            "fiber": 0.6,
            "sugar": 0.1,
            "serving": "1 cup cooked (158g)"
        },
        "grilled chicken breast": {
            "calories": 165,
            "protein": 31,
            "carbs": 0,
            "fat": 3.6,
            "fiber": 0,
            "sugar": 0,
            "serving": "100g"
        },
        "salmon": {
            "calories": 206,
            "protein": 22,
            "carbs": 0,
            "fat": 13,
            "fiber": 0,
            "sugar": 0,
            "serving": "100g"
        },
        "broccoli": {
            "calories": 55,
            "protein": 3.7,
            "carbs": 11,
            "fat": 0.6,
            "fiber": 5.1,
            "sugar": 2.2,
            "serving": "1 cup chopped (156g)"
        },
        "egg": {
            "calories": 72,
            "protein": 6,
            "carbs": 0.4,
            "fat": 5,
            "fiber": 0,
            "sugar": 0.2,
            "serving": "1 large (50g)"
        }
    }

    # Search (case-insensitive, partial match)
    results = {k: v for k, v in nutrition_db.items() if food_query.lower() in k.lower()}

    if results:
        st.success(f"Found {len(results)} result(s) in sample database")

        for food_name, nutrition in results.items():
            with st.expander(f" {food_name.title()}", expanded=True):
                col1, col2 = st.columns([2, 1])

                with col1:
                    st.write(f"**Serving Size:** {nutrition['serving']}")

                    col_a, col_b, col_c, col_d = st.columns(4)
                    col_a.metric("Calories", f"{nutrition['calories']} kcal")
                    col_b.metric("Protein", f"{nutrition['protein']}g")
                    col_c.metric("Carbs", f"{nutrition['carbs']}g")
                    col_d.metric("Fat", f"{nutrition['fat']}g")

                    st.write("")
                    col_e, col_f = st.columns(2)
                    col_e.write(f"**Fiber:** {nutrition['fiber']}g")
                    col_f.write(f"**Sugars:** {nutrition['sugar']}g")

                with col2:
                    # Macro ratio
                    total_cals = (nutrition['protein'] * 4 + nutrition['carbs'] * 4 + nutrition['fat'] * 9)
                    if total_cals > 0:
                        st.write("**Macro Ratio:**")
                        st.write(f"Protein: {(nutrition['protein']*4/total_cals*100):.0f}%")
                        st.write(f"Carbs: {(nutrition['carbs']*4/total_cals*100):.0f}%")
                        st.write(f"Fat: {(nutrition['fat']*9/total_cals*100):.0f}%")

                    # Health score
                    health_score = calculate_health_score(
                        nutrition['protein'],
                        nutrition['carbs'],
                        nutrition['fat'],
                        nutrition['fiber'],
                        nutrition['sugar']
                    )
                    if health_score:
                        st.write("")
                        st.metric("Health Score", f"{health_score}/10")

        st.info("**Limited to 8 sample foods.** Add USDA API key for 350,000+ foods!")
    else:
        st.warning(f"No results for '{food_query}' in sample database.")
        st.write("**Try searching:** chicken rice, banana, apple, white rice, grilled chicken breast, salmon, broccoli, egg")
        st.info("Add USDA API key to search any food!")

# Workout Timer with Audio
        st.subheader("Exercise Tutorial Videos")
        st.write("Get exercise demonstrations from YouTube")

        # NAPFA component selector
        exercise = st.selectbox(
            "Select Exercise",
            ["Sit-Ups", "Standing Broad Jump", "Sit and Reach",
             "Pull-Ups", "Shuttle Run", "2.4km Running Tips"]
        )

        if st.button("Find Tutorials", type="primary"):
            # Simulated YouTube recommendations (in production, use YouTube Data API)
            videos = {
                "Sit-Ups": [
                    {"title": "Perfect Sit-Up Form for NAPFA", "channel": "FitnessBlender", "duration": "5:23"},
                    {"title": "How to Do More Sit-Ups", "channel": "PE Coach", "duration": "8:15"},
                    {"title": "NAPFA Sit-Up Training", "channel": "SG Fitness", "duration": "6:40"}
                ],
                "Pull-Ups": [
                    {"title": "Pull-Up Progression Guide", "channel": "Calisthenicmovement", "duration": "12:30"},
                    {"title": "Get Your First Pull-Up", "channel": "Athlean-X", "duration": "10:15"},
                    {"title": "NAPFA Pull-Up Technique", "channel": "PE Singapore", "duration": "7:20"}
                ],
                "Standing Broad Jump": [
                    {"title": "Standing Broad Jump Technique", "channel": "Track Coach", "duration": "6:45"},
                    {"title": "How to Jump Further", "channel": "Sprint Master", "duration": "9:10"}
                ],
                "2.4km Running Tips": [
                    {"title": "2.4km NAPFA Strategy", "channel": "Running Coach SG", "duration": "11:20"},
                    {"title": "How to Run Faster 2.4km", "channel": "TrackStar", "duration": "8:50"}
                ]
            }

            if exercise in videos:
                st.write(f"###  Top Tutorials for {exercise}")

                for video in videos[exercise]:
                    with st.expander(f"{video['title']} - {video['duration']}", expanded=True):
                        st.write(f"**Channel:** {video['channel']}")
                        st.write(f"**Duration:** {video['duration']}")

                        # In production, embed actual video
                        st.info("Video would be embedded here with real YouTube API")

                        st.write("** Search on YouTube:** ")
                        search_url = f"https://www.youtube.com/results?search_query={exercise.replace(' ', '+')}+NAPFA+tutorial"
                        st.markdown(f"[Open YouTube Search]({search_url})")

            st.write("")
            st.info("""
            ** To enable video embedding:**

            Use YouTube Data API v3 (free quota):
            1. Get API key: https://console.cloud.google.com/
            2. Enable YouTube Data API
            3. Embed videos directly in app
            """)

def teacher_dashboard():
    st.header("Teacher Dashboard")

    user_data = get_user_data()
    all_users = st.session_state.users_data

    # Display class code
    class_display_label = user_data.get('class_label') or 'My Class'
    st.markdown(f"""
    <div class="stat-card" style="background: linear-gradient(135deg, {COLOURS['blue']} 0%, #1565c0 100%); color: white;">
        <h2>{class_display_label}</h2>
        <h3>Class Code: <strong>{user_data['class_code']}</strong></h3>
        <p>Share this code with your students so they can join your class</p>
    </div>
    """, unsafe_allow_html=True)

    st.write("")

    # Get student list
    student_usernames = user_data.get('students', [])
    students_data = {username: all_users[username] for username in student_usernames if username in all_users}

    # Create tabs
    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
        "My Fitness",
        "Houses",
        "Class Overview",
        "Student List",
        "Workout Reviews",
        "Performance Analysis",
        "Export Reports"
    ])

    with tab1:
        st.subheader("My Personal Fitness")
        st.write("Track your own fitness alongside your students!")

        # Allow teachers to access all student features
        teacher_feature = st.selectbox(
            "Select Feature",
            ["Dashboard", "BMI Calculator", "NAPFA Test", "Sleep Tracker",
             "Exercise Log", "Training Schedule", "AI Insights", "Community"]
        )

        if teacher_feature == "Dashboard":
            st.write("### Your Fitness Overview")

            # Teacher's personal stats
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                if user_data.get('bmi_history'):
                    latest_bmi = user_data['bmi_history'][-1]['bmi']
                    st.metric("Latest BMI", f"{latest_bmi:.1f}")
                else:
                    st.metric("Latest BMI", "No data")

            with col2:
                if user_data.get('napfa_history'):
                    latest_napfa = user_data['napfa_history'][-1]['total']
                    st.metric("NAPFA Score", f"{latest_napfa}/30")
                else:
                    st.metric("NAPFA Score", "No data")

            with col3:
                total_workouts = len(user_data.get('exercises', []))
                st.metric("Total Workouts", total_workouts)

            with col4:
                if user_data.get('house'):
                    house_display = {'yellow': 'Yellow', 'red': 'Red', 'blue': 'Blue',
                                   'green': 'Green', 'black': 'Black'}.get(user_data['house'], 'None')
                    st.metric("Your House", house_display)
                else:
                    st.metric("Your House", "Not assigned")

            # Quick actions
            st.write("")
            st.write("###  Quick Actions")

            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button("Log Workout", key="teacher_log"):
                    st.session_state.teacher_feature_nav = "Exercise Log"
                    st.rerun()
            with col2:
                if st.button("Take NAPFA", key="teacher_napfa"):
                    st.session_state.teacher_feature_nav = "NAPFA Test"
                    st.rerun()
            with col3:
                if st.button("AI Insights", key="teacher_ai"):
                    st.session_state.teacher_feature_nav = "AI Insights"
                    st.rerun()

            # Recent activity
            if user_data.get('exercises'):
                st.write("")
                st.write("###  Recent Workouts")
                recent = user_data['exercises'][:5]
                for ex in recent:
                    st.write(f"• **{ex['name']}** - {ex['duration']} min ({ex['date']})")

        elif teacher_feature == "BMI Calculator":
            bmi_calculator()

        elif teacher_feature == "NAPFA Test":
            napfa_calculator()

        elif teacher_feature == "Sleep Tracker":
            sleep_tracker()

        elif teacher_feature == "Exercise Log":
            exercise_logger()

        elif teacher_feature == "Training Schedule":
            schedule_manager()

        elif teacher_feature == "AI Insights":
            ai_insights()

        elif teacher_feature == "Community":
            st.write("### Community Features")
            st.info("As a teacher, you can join houses, compete on leaderboards, and connect with colleagues!")

            community_sub = st.selectbox("Select", ["Leaderboards", "My Achievements", "Friends"])

            if community_sub == "Leaderboards":
                st.write("Access leaderboards from the main Community section")
                st.write("You can compete with students and other teachers!")

            elif community_sub == "My Achievements":
                st.write("### Your Badges & Achievements")
                badges = user_data.get('badges', [])
                if badges:
                    for badge in badges:
                        st.success(f"{badge['name']} - {badge['description']} (+{badge['points']} pts)")
                else:
                    st.info("Complete workouts and NAPFA tests to earn badges!")

            elif community_sub == "Friends":
                st.write("### Connect with Colleagues")
                st.write("Add other teachers as friends to compare fitness progress!")

    with tab2:
        st.subheader("House System - Your Class")

        # Calculate house stats for THIS teacher's students only
        house_stats = {
            'yellow': {'points': 0, 'members': [], 'workouts': 0, 'display': 'Yellow House', 'color': '#FFD700'},
            'red': {'points': 0, 'members': [], 'workouts': 0, 'display': 'Red House', 'color': '#DC143C'},
            'blue': {'points': 0, 'members': [], 'workouts': 0, 'display': 'Blue House', 'color': '#1E90FF'},
            'green': {'points': 0, 'members': [], 'workouts': 0, 'display': 'Green House', 'color': '#32CD32'},
            'black': {'points': 0, 'members': [], 'workouts': 0, 'display': 'Black House', 'color': '#2F4F4F'}
        }

        # Calculate points for teacher's students only
        for username, student in students_data.items():
            if student.get('house'):
                house = student['house']
                if house in house_stats:
                    house_stats[house]['points'] += student.get('house_points_contributed', 0)
                    house_stats[house]['members'].append(username)
                    house_stats[house]['workouts'] += len(student.get('exercises', []))

        # Sort houses
        sorted_houses = sorted(house_stats.items(), key=lambda x: x[1]['points'], reverse=True)

        # Display house standings
        st.write("### House Standings (Your Class)")

        for rank, (house_name, stats) in enumerate(sorted_houses, 1):
            if stats['members']:  # Only show houses with members
                medal = "" if rank == 1 else "" if rank == 2 else "" if rank == 3 else f"{rank}."

                st.markdown(f"""
                <div class="stat-card" style="background: linear-gradient(135deg, {stats['color']} 0%, {stats['color']}dd 100%); color: white;">
                    <h3>{medal} {stats['display']}</h3>
                    <h2>{stats['points']:.1f} Points</h2>
                    <p>{len(stats['members'])} members | {stats['workouts']} workouts</p>
                </div>
                """, unsafe_allow_html=True)

        # House distribution
        st.write("")
        st.write("### House Distribution")

        col1, col2, col3, col4, col5 = st.columns(5)
        cols = [col1, col2, col3, col4, col5]

        for idx, (house_name, stats) in enumerate(sorted_houses):
            with cols[idx]:
                st.metric(stats['display'], len(stats['members']))

        # Students not assigned to house
        unassigned = [username for username, student in students_data.items() if not student.get('house')]
        if unassigned:
            st.write("")
            st.warning(f"{len(unassigned)} student(s) not assigned to a house")
            st.write("Go to 'Student List' tab to assign houses.")

    with tab3:
        st.subheader("Class Overview")

        # Stats
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Total Students", f"{len(students_data)}/30")

        with col2:
            # Calculate average NAPFA
            napfa_scores = []
            for student in students_data.values():
                if student.get('napfa_history'):
                    napfa_scores.append(student['napfa_history'][-1]['total'])

            if napfa_scores:
                avg_napfa = sum(napfa_scores) / len(napfa_scores)
                st.metric("Avg NAPFA Score", f"{avg_napfa:.1f}/30")
            else:
                st.metric("Avg NAPFA Score", "No data")

        with col3:
            # Active this week
            week_ago = datetime.now() - timedelta(days=7)
            active_count = 0
            for student in students_data.values():
                if student.get('exercises'):
                    for exercise in student['exercises']:
                        if datetime.strptime(exercise['date'], '%Y-%m-%d') >= week_ago:
                            active_count += 1
                            break

            st.metric("Active This Week", f"{active_count}/{len(students_data)}")

        with col4:
            # Total workouts this week
            total_workouts = 0
            for student in students_data.values():
                if student.get('exercises'):
                    weekly = [e for e in student['exercises']
                            if datetime.strptime(e['date'], '%Y-%m-%d') >= week_ago]
                    total_workouts += len(weekly)

            st.metric("Class Workouts", total_workouts)

        # Performance distribution
        if napfa_scores:
            st.write("")
            st.write("### NAPFA Score Distribution")

            # Create distribution chart
            df = pd.DataFrame({'Score': napfa_scores})
            st.bar_chart(df['Score'].value_counts().sort_index())

            # Medal counts
            st.write("")
            st.write("###  Medal Distribution")

            medal_counts = {'Gold': 0, 'Silver': 0, 'Bronze': 0, 'No Medal': 0}
            for student in students_data.values():
                if student.get('napfa_history'):
                    medal = student['napfa_history'][-1]['medal']
                    if '' in medal:
                        medal_counts['Gold'] += 1
                    elif '' in medal:
                        medal_counts['Silver'] += 1
                    elif '' in medal:
                        medal_counts['Bronze'] += 1
                    else:
                        medal_counts['No Medal'] += 1

            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Gold", medal_counts['Gold'])
            col2.metric("Silver", medal_counts['Silver'])
            col3.metric("Bronze", medal_counts['Bronze'])
            col4.metric("No Medal", medal_counts['No Medal'])

        # Top performers
        if napfa_scores:
            st.write("")
            st.write("###  Top Performers")

            student_scores = []
            for username, student in students_data.items():
                if student.get('napfa_history'):
                    student_scores.append({
                        'name': student['name'],
                        'username': username,
                        'score': student['napfa_history'][-1]['total'],
                        'medal': student['napfa_history'][-1]['medal']
                    })

            student_scores.sort(key=lambda x: x['score'], reverse=True)

            for idx, student in enumerate(student_scores[:5], 1):
                medal = "" if idx == 1 else "" if idx == 2 else "" if idx == 3 else f"{idx}."
                st.write(f"{medal} **{student['name']}** - {student['score']}/30 ({student['medal']})")

        # Students needing attention
        st.write("")
        st.write("### Students Needing Attention")

        needs_attention = []
        for username, student in students_data.items():
            # Check if inactive
            if not student.get('exercises') or len(student.get('exercises', [])) == 0:
                needs_attention.append(f"**{student['name']}** - No workouts logged")
            elif student.get('napfa_history'):
                latest_napfa = student['napfa_history'][-1]
                if latest_napfa['total'] < 9:
                    needs_attention.append(f" **{student['name']}** - Low NAPFA score ({latest_napfa['total']}/30)")

        if needs_attention:
            for msg in needs_attention[:5]:
                st.warning(msg)
        else:
            st.success("All students doing well!")

    with tab4:
        st.subheader("Student List")

        if not students_data:
            st.info("No students in your class yet. Share your class code: " + user_data['class_code'])
        else:
            # Search and filter
            search = st.text_input("Search students", placeholder="Enter name or username")

            # Display students
            for username, student in students_data.items():
                if search.lower() in student['name'].lower() or search.lower() in username.lower() or not search:
                    with st.expander(f"{student['name']} (@{username})"):
                        col1, col2, col3 = st.columns(3)

                        with col1:
                            st.write(f"**Email:** {student.get('email', 'N/A')}")
                            st.write(f"**Age:** {student.get('age', 'N/A')}")
                            st.write(f"**Gender:** {'Male' if student.get('gender') == 'm' else 'Female'}")

                        with col2:
                            if student.get('napfa_history'):
                                latest = student['napfa_history'][-1]
                                st.write(f"**NAPFA:** {latest['total']}/30")
                                st.write(f"**Medal:** {latest['medal']}")
                            else:
                                st.write("**NAPFA:** Not tested")

                            st.write(f"**Workouts:** {len(student.get('exercises', []))}")

                        with col3:
                            st.write(f"**Level:** {student.get('level', 'Novice')}")
                            st.write(f"**Points:** {student.get('total_points', 0)}")
                            st.write(f"**Login Streak:** {student.get('login_streak', 0)} days")

                        # House info and assignment
                        st.write("")
                        current_house = student.get('house', 'Not assigned')
                        if current_house != 'Not assigned':
                            house_display = {
                                'yellow': 'Yellow',
                                'red': 'Red',
                                'blue': 'Blue',
                                'green': 'Green',
                                'black': 'Black'
                            }
                            st.write(f"**House:** {house_display.get(current_house, current_house.title())}")
                            st.write(f"**House Points:** {student.get('house_points_contributed', 0):.1f}")
                        else:
                            st.write("**House:** Not assigned")

                        # House assignment
                        st.write("")
                        house_options = ['yellow', 'red', 'blue', 'green', 'black']
                        new_house = st.selectbox(
                            "Assign to House",
                            house_options,
                            index=house_options.index(current_house) if current_house in house_options else 0,
                            key=f"house_{username}",
                            format_func=lambda x: {'yellow': 'Yellow', 'red': 'Red', 'blue': 'Blue',
                                                  'green': 'Green', 'black': 'Black'}[x]
                        )

                        col_a, col_b = st.columns(2)
                        with col_a:
                            if st.button(f"Update House", key=f"update_house_{username}"):
                                student['house'] = new_house
                                save_users(all_users)
                                st.success(f"Updated {student['name']}'s house to {new_house.title()}!")
                                st.rerun()

                        with col_b:
                            if st.button(f"Remove from class", key=f"remove_{username}"):
                                user_data['students'].remove(username)
                                student['teacher_class'] = None
                                update_user_data(user_data)
                                save_users(all_users)
                                st.success(f"Removed {student['name']} from class")
                                st.rerun()


    with tab5:
        st.subheader("Workout Reviews")
        st.write("Review your students' workout photos and adjust points if the AI graded unfairly.")

        if not students_data:
            st.info("No students in your class yet.")
        else:
            # Gather all workouts with photos across all students
            all_reviews = []
            for s_username, s_data in students_data.items():
                for idx, ex in enumerate(s_data.get('exercises', [])):
                    if ex.get('has_photo') and ex.get('photo_b64'):
                        all_reviews.append({
                            'student_username': s_username,
                            'student_name': s_data['name'],
                            'exercise_idx': idx,
                            'exercise': ex,
                        })

            if not all_reviews:
                st.info("No photo submissions yet. Photos will appear here once students upload them with their workouts.")
            else:
                # Filters
                fc1, fc2, fc3 = st.columns(3)
                with fc1:
                    filter_student = st.selectbox(
                        "Filter by student",
                        ["All students"] + sorted(set(r["student_name"] for r in all_reviews)),
                        key="review_filter_student"
                    )
                with fc2:
                    filter_status = st.selectbox(
                        "Filter by AI status",
                        ["All", "Verified", "Failed", "Unverified", " Teacher overridden"],
                        key="review_filter_status"
                    )
                with fc3:
                    sort_order = st.selectbox(
                        "Sort by",
                        ["Newest first", "Oldest first", "Failed first"],
                        key="review_sort"
                    )

                # Apply filters
                filtered = all_reviews
                if filter_student != "All students":
                    filtered = [r for r in filtered if r["student_name"] == filter_student]
                if filter_status == "Verified":
                    filtered = [r for r in filtered if r["exercise"].get("verification_status") == "verified" and not r["exercise"].get("teacher_override")]
                elif filter_status == "Failed":
                    filtered = [r for r in filtered if r["exercise"].get("verification_status") == "failed"]
                elif filter_status == "Unverified":
                    filtered = [r for r in filtered if r["exercise"].get("verification_status") in ("unverified", "mock")]
                elif filter_status == " Teacher overridden":
                    filtered = [r for r in filtered if r["exercise"].get("teacher_override")]

                # Sort
                def _sort_key(r):
                    return f"{r['exercise'].get('date','')} {r['exercise'].get('time','')}"

                if sort_order == "Newest first":
                    filtered = sorted(filtered, key=_sort_key, reverse=True)
                elif sort_order == "Oldest first":
                    filtered = sorted(filtered, key=_sort_key)
                else:  # Failed first
                    filtered = sorted(filtered, key=lambda r: (
                        0 if r["exercise"].get("verification_status") == "failed" else 1, _sort_key(r)
                    ))

                st.write(f"**{len(filtered)} submission{'s' if len(filtered) != 1 else ''} shown**")
                st.write("---")

                for review in filtered:
                    ex = review["exercise"]
                    s_name = review["student_name"]
                    s_username = review["student_username"]
                    ex_idx = review["exercise_idx"]
                    v_status = ex.get("verification_status", "unverified")
                    overridden = ex.get("teacher_override", False)

                    status_display = {
                        "verified": "AI Verified",
                        "failed": "AI Failed",
                        "unverified": "Unverified",
                        "mock": "Mock Mode",
                    }.get(v_status, v_status)
                    if overridden:
                        status_display = " Teacher Override"

                    border_color = {
                        "verified": "#2e7d32",
                        "failed": "#c62828",
                        "unverified": "#f9a825",
                        "mock": "#1976d2",
                    }.get(v_status, "#888")
                    if overridden:
                        border_color = "#6a1b9a"

                    st.markdown(f"""
                    <div class="stat-card" style="border-left-color:{border_color}; margin-bottom:4px;">
                        <strong>{s_name}</strong> &nbsp;·&nbsp; {ex.get("name","Exercise")}
                        &nbsp;·&nbsp; {ex.get("date","")} {ex.get("time","")}
                        &nbsp;&nbsp;<span style="color:{border_color};">{status_display}</span>
                    </div>
                    """, unsafe_allow_html=True)

                    col_img, col_detail = st.columns([1, 2])

                    with col_img:
                        import base64 as _b64
                        img_data = ex.get("photo_b64", "")
                        if img_data:
                            st.markdown(
                                f'<img src="data:image/jpeg;base64,{img_data}" '                                f'style="width:100%;border-radius:8px;border:1px solid #e0e4ef;">',
                                unsafe_allow_html=True
                            )

                    with col_detail:
                        if ex.get("workout_type") == "counter":
                            st.write(f"**Sets:** {ex.get('sets','?')} &nbsp;·&nbsp; **{ex.get('reps_unit','reps').title()}:** {ex.get('total_reps','?')}")
                        else:
                            dist = f" · {ex.get('distance_km',0):.1f} km" if ex.get("distance_km", 0) > 0 else ""
                            st.write(f"**Duration:** {ex.get('duration',0)} min{dist}")

                        st.write(f"**Intensity:** {ex.get('intensity','N/A')}")

                        if ex.get("notes"):
                            st.caption(f"{ex['notes']}")

                        if ex.get("ai_feedback"):
                            with st.expander("View AI Feedback"):
                                st.write(ex["ai_feedback"])

                        current_pts = int(ex.get("points_earned", 0))
                        st.write(f"**Current points:** {current_pts} pts{'   *(teacher adjusted)*' if overridden else ''}")

                        new_pts = st.number_input(
                            "Override points",
                            min_value=0,
                            max_value=500,
                            value=current_pts,
                            step=5,
                            key=f"pts_{s_username}_{ex_idx}",
                            help="Adjust if you think the AI graded unfairly"
                        )

                        b1, b2 = st.columns(2)
                        with b1:
                            if st.button(" Save", key=f"save_{s_username}_{ex_idx}", use_container_width=True, type="primary"):
                                diff = new_pts - current_pts
                                st.session_state.users_data[s_username]["exercises"][ex_idx]["points_earned"] = new_pts
                                st.session_state.users_data[s_username]["exercises"][ex_idx]["teacher_override"] = True
                                st.session_state.users_data[s_username]["exercises"][ex_idx]["verification_status"] = "verified"
                                st.session_state.users_data[s_username]["total_points"] = (
                                    st.session_state.users_data[s_username].get("total_points", 0) + diff
                                )
                                save_users(st.session_state.users_data)
                                st.success(f"Saved! {'+' if diff >= 0 else ''}{diff} pts applied to {s_name}.")
                                st.rerun()

                        with b2:
                            if overridden:
                                if st.button("↩ Reset AI", key=f"reset_{s_username}_{ex_idx}", use_container_width=True):
                                    st.session_state.users_data[s_username]["exercises"][ex_idx]["teacher_override"] = False
                                    save_users(st.session_state.users_data)
                                    st.info("Reset to AI decision.")
                                    st.rerun()

                    st.write("---")

    with tab6:
        st.subheader("Performance Analysis")

        if not students_data:
            st.info("No students to analyze yet")
        else:
            # NAPFA component analysis
            st.write("### NAPFA Component Breakdown")

            component_scores = {
                'Sit-Ups': [],
                'Broad Jump': [],
                'Sit & Reach': [],
                'Pull-Ups': [],
                'Shuttle Run': [],
                '2.4km Run': []
            }

            component_map = {
                'SU': 'Sit-Ups',
                'SBJ': 'Broad Jump',
                'SAR': 'Sit & Reach',
                'PU': 'Pull-Ups',
                'SR': 'Shuttle Run',
                'RUN': '2.4km Run'
            }

            for student in students_data.values():
                if student.get('napfa_history'):
                    grades = student['napfa_history'][-1]['grades']
                    for code, name in component_map.items():
                        if code in grades:
                            component_scores[name].append(grades[code])

            if any(component_scores.values()):
                # Calculate averages
                avg_scores = {name: sum(scores)/len(scores) if scores else 0
                            for name, scores in component_scores.items()}

                df = pd.DataFrame({
                    'Component': list(avg_scores.keys()),
                    'Average Grade': list(avg_scores.values())
                })

                st.bar_chart(df.set_index('Component'))

                # Identify weak areas
                weak_components = [name for name, avg in avg_scores.items() if avg < 3]
                if weak_components:
                    st.warning(f"**Class weak areas:** {', '.join(weak_components)}")
                    st.info("Consider focusing class training on these components")

            # Participation trends
            st.write("")
            st.write("### Weekly Participation Trend")

            # Last 4 weeks
            weeks_data = []
            for week in range(4):
                week_start = datetime.now() - timedelta(days=7 * (week + 1))
                week_end = datetime.now() - timedelta(days=7 * week)

                active_count = 0
                for student in students_data.values():
                    if student.get('exercises'):
                        for exercise in student['exercises']:
                            ex_date = datetime.strptime(exercise['date'], '%Y-%m-%d')
                            if week_start <= ex_date < week_end:
                                active_count += 1
                                break

                weeks_data.append({
                    'Week': f"Week {4-week}",
                    'Active Students': active_count
                })

            df_weeks = pd.DataFrame(weeks_data)
            st.line_chart(df_weeks.set_index('Week'))

    with tab7:
        st.subheader("Export Class Reports")

        # Class name management
        st.write("###  Rename Your Class")
        current_label = user_data.get('class_label', '')
        new_label = st.text_input("Class Name", value=current_label, placeholder="e.g., 3-Integrity, Sec 2A", key="teacher_class_label")
        if st.button(" Save Class Name"):
            user_data['class_label'] = new_label.strip()
            update_user_data(user_data)
            st.success(f"Class renamed to **{new_label.strip()}**!")
            st.rerun()

        st.write("---")

        # AI Verification Strictness
        st.write("### AI Form Verification Strictness")
        st.write("Controls how strictly the AI evaluates your students' exercise photos.")

        strictness_options = {
            " Lenient — Accept any reasonable attempt": 1,
            " Standard — Roughly correct technique required": 2,
            "Strict — Proper form on all key criteria": 3,
        }

        current_strictness = user_data.get('verification_strictness', 2)
        current_label_str = next(
            (k for k, v in strictness_options.items() if v == current_strictness),
            " Standard — Roughly correct technique required"
        )

        selected = st.radio(
            "Verification Level",
            list(strictness_options.keys()),
            index=list(strictness_options.keys()).index(current_label_str),
            key="teacher_strictness"
        )

        strictness_descriptions = {
            1: (
                "**Lenient** — Great for beginners or to build exercise habits. "
                "The AI approves any honest attempt at the exercise and only rejects "
                "if there's a clear injury risk or the wrong exercise entirely."
            ),
            2: (
                "**Standard** — Balanced for most classes. "
                "Students need to show clear effort and roughly correct form, "
                "but minor imperfections are accepted with encouraging feedback."
            ),
            3: (
                "**Strict** — For advanced or competitive groups. "
                "All key form criteria must be met. The AI rejects partial or sloppy form "
                "and gives direct feedback on exactly what needs to improve."
            ),
        }

        new_strictness = strictness_options[selected]
        st.info(strictness_descriptions[new_strictness])

        if st.button(" Save Strictness Setting", key="save_strictness"):
            user_data['verification_strictness'] = new_strictness
            update_user_data(user_data)
            st.success("Strictness setting saved! It will apply to all your students' next verifications.")

        st.write("---")
        st.write("### Google Sheets Export")
        st.info("Generate a comprehensive class report and export to Google Sheets")

        # Report options
        include_napfa = st.checkbox("Include NAPFA scores", value=True)
        include_workouts = st.checkbox("Include workout logs", value=True)
        include_attendance = st.checkbox("Include attendance/participation", value=True)

        if st.button("Generate Report (Download CSV)", type="primary"):
            if not students_data:
                st.error("No students to export")
            else:
                # Generate report data
                report_data = []

                for username, student in students_data.items():
                    row = {
                        'Name': student['name'],
                        'Email': student.get('email', ''),
                        'Age': student.get('age', ''),
                        'Gender': 'Male' if student.get('gender') == 'm' else 'Female'
                    }

                    if include_napfa and student.get('napfa_history'):
                        latest = student['napfa_history'][-1]
                        row['NAPFA Total'] = latest['total']
                        row['Medal'] = latest['medal']
                        row['Sit-Ups'] = latest['grades'].get('SU', 0)
                        row['Broad Jump'] = latest['grades'].get('SBJ', 0)
                        row['Sit & Reach'] = latest['grades'].get('SAR', 0)
                        row['Pull-Ups'] = latest['grades'].get('PU', 0)
                        row['Shuttle Run'] = latest['grades'].get('SR', 0)
                        row['2.4km Run'] = latest['grades'].get('RUN', 0)

                    if include_workouts:
                        row['Total Workouts'] = len(student.get('exercises', []))

                        # This week
                        week_ago = datetime.now() - timedelta(days=7)
                        weekly = [e for e in student.get('exercises', [])
                                if datetime.strptime(e['date'], '%Y-%m-%d') >= week_ago]
                        row['Workouts This Week'] = len(weekly)

                    if include_attendance:
                        row['Login Streak'] = student.get('login_streak', 0)
                        row['Level'] = student.get('level', 'Novice')
                        row['Total Points'] = student.get('total_points', 0)

                    report_data.append(row)

                # Create DataFrame
                df_report = pd.DataFrame(report_data)

                # Convert to CSV
                csv = df_report.to_csv(index=False)

                st.download_button(
                    label="Download CSV Report",
                    data=csv,
                    file_name=f"class_report_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )

                st.success("Report generated! Click to download.")

                # Preview
                st.write("### Preview")
                st.dataframe(df_report, use_container_width=True)

        st.write("")
        st.write("###  Share Instructions")
        st.info("""
        **To share this report with others:**
        1. Download the CSV file
        2. Upload to Google Sheets
        3. Click Share → Add people (enter emails)
        4. Set permissions (Viewer = read-only, Editor = can edit)
        5. Send the link!

        **For automatic Google Sheets export, this feature will be available after deployment.**
        """)

def schedule_manager():
    st.header("Training Schedule")

    with st.form("schedule_form"):
        day = st.selectbox("Day of Week",
                          ["Monday", "Tuesday", "Wednesday", "Thursday",
                           "Friday", "Saturday", "Sunday"])
        activity = st.text_input("Activity", placeholder="e.g., Morning run")

        col1, col2 = st.columns(2)
        with col1:
            time = st.time_input("Time")
        with col2:
            duration = st.number_input("Duration (minutes)", min_value=1, max_value=300, value=30)

        submitted = st.form_submit_button("Add to Schedule")

        if submitted:
            if activity:
                user_data = get_user_data()
                user_data['schedule'].append({
                    'day': day,
                    'activity': activity,
                    'time': str(time),
                    'duration': duration
                })
                update_user_data(user_data)
                st.success("Activity added to schedule!")
                st.rerun()
            else:
                st.error("Please enter activity name")

    # Display schedule
    user_data = get_user_data()
    if user_data['schedule']:
        st.subheader("Weekly Schedule")
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

        for day in days:
            day_activities = [s for s in user_data['schedule'] if s['day'] == day]
            if day_activities:
                st.markdown(f"### {day}")
                for activity in day_activities:
                    st.markdown(f'<div class="stat-card"><strong>{activity["activity"]}</strong><br>{activity["time"]} - {activity["duration"]} minutes</div>',
                              unsafe_allow_html=True)
    else:
        st.info("No activities scheduled yet.")

# Main App
def main_app():
    user_data = get_user_data()

    # Check if teacher or student
    is_teacher = user_data.get('role') == 'teacher'

    # Header with logout
    col1, col2 = st.columns([4, 1])
    with col1:
        current_dt = datetime.now().strftime("%A, %d %B %Y  |  %I:%M %p")
        if is_teacher:
            st.markdown(f'<div class="main-header"><h1>FitTrack - Teacher Portal</h1><p>Welcome, {user_data["name"]}!</p><p style="font-size:0.9em; opacity:0.85;">{current_dt}</p></div>',
                       unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="main-header"><h1>FitTrack</h1><p>Welcome back, {user_data["name"]}!</p><p style="font-size:0.9em; opacity:0.85;">{current_dt}</p></div>',
                       unsafe_allow_html=True)
    with col2:
        st.write("")
        st.write("")
        if st.button("Logout"):
            st.session_state.logged_in = False
            st.session_state.username = None
            st.rerun()

    # Different interface for teachers vs students
    if is_teacher:
        teacher_dashboard()
    else:
        # Update login streak for students
        user_data = update_login_streak(user_data)
        update_user_data(user_data)

        # Sidebar navigation
        st.sidebar.title("Navigation")
        page = st.sidebar.radio("Choose a feature:",
                               ["Weekly Progress", "Community", "AI Insights",
                                "Advanced Metrics", "Integrations",
                                "Log Workout",
                                "BMI Calculator", "NAPFA Test", "Sleep Tracker",
                                "Training Schedule"])

        # Display selected page
        if page == "Weekly Progress":
            reminders_and_progress()
        elif page == "Community":
            community_features()
        elif page == "AI Insights":
            ai_insights()
        elif page == "Advanced Metrics":
            advanced_metrics()
        elif page == "Integrations":
            api_integrations()
        elif page == "Log Workout":
            exercise_logger()
        elif page == "BMI Calculator":
            bmi_calculator()
        elif page == "NAPFA Test":
            napfa_calculator()
        elif page == "Sleep Tracker":
            sleep_tracker()
        elif page == "Training Schedule":
            schedule_manager()

# Main execution
if not st.session_state.logged_in:
    login_page()
else:
    main_app()
