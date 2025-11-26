# ai_personal_expense_advisor_final.py
"""
AI PERSONAL EXPENSE ADVISOR - Final polished version
Features:
- Animated gradient header (Paytm-like)
- Sidebar with gradient + icons
- Add / Edit / Delete expenses & incomes
- Auto-category via keywords and "teach" memory (saved JSON)
- CSV upload & download
- Plotly charts (pie + line) with visible axis & labels
- Forecast using smoothing + linear regression + small variation
- Persistence to CSV/JSON
- Styled UI with CSS
- AUTHOR : Samarth Moraiya (Stylized)
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import date, datetime, timedelta
import json
import os
from sklearn.linear_model import LinearRegression
import plotly.express as px
import time
from auth import login, signup, logout
from auth import _load_users, reset_password

# --- FORCE LOGOUT IF SESSION HALF-LOADED ---
if "logged_in_user" in st.session_state and \
   ("expenses" not in st.session_state or "incomes" not in st.session_state):
    st.session_state.clear()

# ------------------------- Page config -------------------------
st.set_page_config(page_title="AI PERSONAL EXPENSE ADVISOR", layout="wide")

 # ------------------------- File paths helper (per-user) -------------------------
def get_user_files():
    if "logged_in_user" not in st.session_state:
        return ("expenses_default.csv", "incomes_default.csv", "category_memory_default.json")

    u = st.session_state.logged_in_user["username"]
    u = u.strip().replace(" ", "_")   # safe filename
    return (
        f"expenses_{u}.csv",
        f"incomes_{u}.csv",
        f"category_memory_{u}.json"
    )


# 🔁 Helper function for instant refresh after actions
def rerun_after_action(seconds: float = 0.8):
    time.sleep(seconds)
    st.rerun()

# ------------------------- CSV & MEMORY HELPERS -------------------------
def load_csv_safe(path, expected_cols):
    if os.path.exists(path):
        try:
            df = pd.read_csv(path)
            for c in expected_cols:
                if c not in df.columns:
                    df[c] = ""
            if "date" in df.columns:
                df["date"] = pd.to_datetime(df["date"], errors="coerce")
            return df
        except:
            return pd.DataFrame(columns=expected_cols)
    return pd.DataFrame(columns=expected_cols)


def save_csv_safe(df, path):
    df2 = df.copy()
    if "date" in df2.columns:
        df2["date"] = pd.to_datetime(df2["date"], errors="coerce").dt.strftime("%Y-%m-%d")
    df2.to_csv(path, index=False)


def load_memory(path):
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return {}
    return {}


def save_memory(mem, path):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(mem, f, indent=2)
# ------------------ FORGOT PASSWORD SECTION ------------------
if st.session_state.get("forgot_mode", False):

    st.markdown("## 🔐 Reset Password")

    uname = st.text_input("Enter your username")

    if st.button("Get Security Question"):
        users = _load_users()
        if uname not in users:
            st.error("User does not exist ❌")
        else:
            st.session_state["fp_username"] = uname
            st.session_state["fp_question"] = users[uname]["security_question"]
            st.rerun()

    if "fp_question" in st.session_state:
        st.info("Security Question: " + st.session_state["fp_question"])

        ans = st.text_input("Your Answer")
        newp = st.text_input("New Password", type="password")

        if st.button("Reset Now"):
            msg = reset_password(
                st.session_state["fp_username"],
                ans,
                newp
            )
            if "successfully" in msg:
                st.success(msg)
                st.session_state["forgot_mode"] = False
                st.session_state.pop("fp_question", None)
                st.session_state.pop("fp_username", None)
                st.rerun()
            else:
                st.error(msg)

    # ---------- GRADIENT BUTTON CSS (Login + Signup) ----------
        st.markdown("""
            <style>
            .stButton>button {
                width: 100%;
                padding: 14px;
                border-radius: 10px;
                border: none;
                background: linear-gradient(90deg,#1E3A8A,#3B82F6) !important;
                color: white !important;
                font-size: 16px;
                font-weight: 700;
                cursor: pointer;
                transition: 0.25s ease-in-out;
                letter-spacing: 0.6px;
            }

            .stButton>button:hover {
                transform: scale(1.03);
                background: linear-gradient(90deg,#3B82F6,#1E3A8A) !important;
                color: #e2e8f0 !important;
            }
            </style>
            """, unsafe_allow_html=True)
    st.stop()
# ---------------------- LOGIN / SIGNUP PAGE ----------------------
if "logged_in_user" not in st.session_state:

    st.markdown("""
    <style>
        /* REMOVE EXTRA GAP BELOW ALL TEXT INPUTS */
        div[data-testid="stTextInput"] > div:nth-child(1) {
            margin-bottom: -18px !important;
            padding-bottom: 0px !important;
        }

        /* REMOVE GAP BELOW NUMBER INPUTS ALSO (if any) */
        div[data-testid="stNumberInput"] > div:nth-child(1) {
            margin-bottom: -18px !important;
            padding-bottom: 0px !important;
        }

        /* MAKE LABELS TIGHT TO THE INPUT FIELD */
        .tight-label {
            margin-bottom: -4px !important;
            padding-bottom: 0px !important;
        }
    </style>
    """, unsafe_allow_html=True)

    
    # PAGE BACKGROUND (light gradient)
    st.markdown("""
    <style>
    body {
        background: linear-gradient(135deg, #eef2ff 0%, #dbeafe 100%);
    }
    </style>
    """, unsafe_allow_html=True)

    # CENTERED CONTAINER
    st.markdown("""
        <div style="
            width: 100%;
            background: linear-gradient(90deg, #1E3A8A, #3B82F6);
            padding: 60px 0px 50px 0px;
            text-align: center;
            border-radius: 0 0 22px 22px;
            box-shadow: 0 8px 25px rgba(0,0,0,0.20);
            font-family: 'Poppins', sans-serif;
        ">
            <h1 style="
                font-size: 50px;
                font-weight: 900;
                color: white;
                margin-bottom: 8px;
                letter-spacing: 1.4px;
                text-transform: uppercase;
            ">
                AI PERSONAL EXPENSE ADVISOR
            </h1>
            <p style="
                font-size: 18px;
                color: rgba(255,255,255,0.90);
                margin-top: 0px;
            ">  
                Login or Create your account
            </p>

        </div>
    """, unsafe_allow_html=True)


    tab1, tab2 = st.tabs(["🔑 Login", "📝 Signup"])

    # ------------------ LOGIN TAB ------------------

    with tab1:
        st.markdown("<p class='tight-label' style='text-align:left;color:#334155'>Username</p>", unsafe_allow_html=True)
        username = st.text_input("", placeholder="Enter your username", key="user_login")

        st.markdown("<p class='tight-label' style='text-align:left;color:#334155;margin-top:10px'>Password</p>", unsafe_allow_html=True)
        password = st.text_input("", placeholder="Enter password", type="password", key="pass_login")

        # ---------- FORGOT PASSWORD TOGGLE ----------
        if st.button("Forgot Password?"):
            st.session_state["forgot_mode"] = True
            st.rerun()

        login_btn = st.button("Login", key="login_btn")

        if login_btn:
            user = login(username, password)
            if user:
                st.session_state.logged_in_user = user
                
                exp_file, inc_file, mem_file = get_user_files()

                if not os.path.exists(exp_file):
                    pd.DataFrame(columns=['date','amount','description','category']).to_csv(exp_file, index=False)

                if not os.path.exists(inc_file):
                    pd.DataFrame(columns=['date','amount','source','id']).to_csv(inc_file, index=False)

                if not os.path.exists(mem_file):
                    with open(mem_file, "w") as f:
                        json.dump({}, f)

                st.session_state.expenses = load_csv_safe(exp_file, ['date','amount','description','category'])
                st.session_state.incomes  = load_csv_safe(inc_file, ['date','amount','source','id'])
                st.session_state.memory   = load_memory(mem_file)
                st.success("Login successful! Redirecting....")
                st.rerun()
            else:
                st.error("Invalid username or password ❌")

    # ------------------ SIGNUP TAB ------------------
    with tab2:
        st.markdown("<p class='tight-label' style='text-align:left;color:#334155'>Full Name</p>", unsafe_allow_html=True)
        name = st.text_input("", placeholder="Enter your full name", key="signup_name")

        st.markdown("<p class='tight-label' style='text-align:left;color:#334155'>Create Username</p>", unsafe_allow_html=True)
        new_username = st.text_input("", placeholder="Choose a username", key="signup_user")

        st.markdown("<p class='tight-label' style='text-align:left;color:#334155'>Create Password</p>", unsafe_allow_html=True)
        new_password = st.text_input("", placeholder="Choose a password", type="password", key="signup_pass")

        # 🔥 STEP–2 → Security Questions (ADD HERE)
        st.markdown("<p style='text-align:left;color:#334155'>Choose a Security Question</p>", unsafe_allow_html=True)

        security_questions = [
            "What is your childhood pet’s name?",
            "What is the funniest nickname your friends call you?",
            "What is the name of your first crush?",
            "What is the weirdest thing you have ever eaten?",
            "What is your favourite teacher’s nickname?",
            "What was the name of your favourite childhood toy?",
            "What is the funniest username you ever used?"
        ]

        sq = st.selectbox("", security_questions)

        st.markdown("<p style='text-align:left;color:#334155'>Your Answer</p>", unsafe_allow_html=True)
        sa = st.text_input("", placeholder="Enter answer", key="signup_answer")

        signup_btn = st.button("Create Account", key="signup_btn")

        if signup_btn:
            msg = signup(name, new_username, new_password, sq, sa)
            if "successfully" in msg:
                st.success(msg)
            else:
                st.error(msg)

        # ---------- GRADIENT BUTTON CSS (Login + Signup) ----------
        st.markdown("""
            <style>
            .stButton>button {
                width: 100%;
                padding: 14px;
                border-radius: 10px;
                border: none;
                background: linear-gradient(90deg,#1E3A8A,#3B82F6);
                color: white;
                font-size: 16px;
                font-weight: 700;
                cursor: pointer;
                transition: 0.25s ease-in-out;
                letter-spacing: 0.6px;
            }

            .stButton>button:hover {
                transform: scale(1.03);
                background: linear-gradient(90deg,#3B82F6,#1E3A8A);
                color: #e2e8f0;
            }
            </style>
        """, unsafe_allow_html=True)
        st.stop()

#--------------------------GLOBAL-css---------------------------
st.markdown(
"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;700;900&family=Montserrat:wght@700;900&family=Poppins:wght@400;600&display=swap');

/* Sidebar gradient */
[data-testid="stSidebar"]{
    background: linear-gradient(180deg,#6d28d9 0%,#06b6d4 100%) !important;
    color: white;
    padding-top: 24px;
}
[data-testid="stSidebar"] .css-1d391kg { color: white !important; }

/* Animated header */
.hero {
  margin: 14px auto;
  max-width: 1180px;
  border-radius: 12px;
  padding: 22px 28px;
  color: white;
  box-shadow: 0 12px 40px rgba(13,23,42,0.06);
  background: linear-gradient(90deg,#6d28d9,#0ea5e9,#06b6d4);
  background-size: 300% 300%;
  animation: gradientShift 8s ease infinite;
}
@keyframes gradientShift {
  0%{background-position:0% 50%} 50%{background-position:100% 50%} 100%{background-position:0% 50%}
}
.hero-title { font-family: 'Montserrat', sans-serif; font-weight:900; font-size:34px; text-transform:uppercase; margin:0; color:#fff; }
.hero-sub { font-weight:700; margin-top:6px; color:rgba(255,255,255,0.95); }

/* Gradient text used for icons */
.gtext {
  background: linear-gradient(90deg,#6d28d9,#06b6d4);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  font-weight:900;
}
.gicon { font-size:18px; vertical-align:middle; margin-right:8px; }

/* Cards and tables */
.card { background: #ffffff; border-radius:10px; padding:14px; box-shadow:0 8px 24px rgba(15,23,42,0.06); }
.stat-value { font-size:20px; font-weight:800; color:#0f1724; margin-top:6px; }

/* Buttons */
.stButton>button { border-radius:10px; font-weight:800; color:white; padding:8px 14px; }
.stButton>button[style] { background: linear-gradient(90deg,#6d28d9,#06b6d4) !important; }

/* Input & table rounding */
.stTextInput>div>div>input, .stNumberInput>div>div>input, .css-1siy2j7 { border-radius:10px !important; padding:12px !important; }

/* Ensure plotly graphs have white area and dark labels */
.plotly-graph-div .main-svg { background: white !important; }
.plotly-graph-div .main-svg text { fill: #0f1724 !important; }

/* Small responsive tweak for mobile */
@media (max-width: 600px) {
  .hero-title { font-size: 22px; }
  .hero { padding: 16px; }
}
</style>
""",
unsafe_allow_html=True
)

st.markdown("""
<style>

.stButton>button {
    background: linear-gradient(90deg,#1E3A8A,#3B82F6) !important;
    color: white !important;
    padding: 10px 18px !important;
    border-radius: 8px !important;
    border: none !important;
    font-weight: 600 !important;
    cursor: pointer !important;
    transition: 0.25s;
}

.stButton>button:hover {
    background: linear-gradient(90deg,#3B82F6,#1E3A8A) !important;
    transform: scale(1.03);
}

</style>
""", unsafe_allow_html=True)

# ---------- GLOBAL GRADIENT BUTTON CSS FOR FORGOT PASSWORD ----------
st.markdown("""
<style>
.fgbtn button {
    width: 100%;
    padding: 14px;
    border-radius: 10px;
    border: none;
    background: linear-gradient(90deg,#1E3A8A,#3B82F6) !important;
    color: white !important;
    font-size: 16px;
    font-weight: 700;
    cursor: pointer;
    transition: 0.25s ease-in-out;
    letter-spacing: 0.6px;
}
.fgbtn button:hover {
    transform: scale(1.03);
    background: linear-gradient(90deg,#3B82F6,#1E3A8A) !important;
    color: #e2e8f0 !important;
}
</style>
""", unsafe_allow_html=True)

# ------------------------- Persistence helpers -------------------------
def load_csv_safe(path, expected_cols):
    if os.path.exists(path):
        try:
            df = pd.read_csv(path)
            for c in expected_cols:
                if c not in df.columns:
                    df[c] = ""
            if "date" in df.columns:
                df["date"] = pd.to_datetime(df["date"], errors="coerce")
            return df
        except:
            return pd.DataFrame(columns=expected_cols)
    return pd.DataFrame(columns=expected_cols)

def save_csv_safe(df, path):
    df2 = df.copy()
    if "date" in df2.columns:
        df2["date"] = pd.to_datetime(df2["date"], errors="coerce").dt.strftime("%Y-%m-%d")
    df2.to_csv(path, index=False)

def load_memory(path):
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_memory(mem, path):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(mem, f, indent=2)


# ------------------------- Keyword mapping for auto-category -------------------------
KEYWORD_MAP = {
    'Food': [
        'zomato','swiggy','blinkit','bigbasket','grocery','groceries','restaurant','dominos','ubereats','pizza','mcdonalds','kfc','starbucks','subway','foodpanda','instacart','talabat','grubhub','burger king','food'
    ],
    'Shopping': [
        'amazon','fashion','flipkart','myntra','ajio','ebay','walmart','mall','order','purchase','shopping','asos','zalando','target','costco','shopee','lazada','alibaba','mercado libre','tata cliq'
    ],
    'Bills': [
        'recharge','bill','electricity','internet','mobile','rent','water','bills','jio','idea','airtel','vodafone','telefonica','verizon','comcast','spectrum','utility','utilities','tv','wifi','gas','lpg','cng'
    ],
    'Travel': [
        'uber','ola','taxi','bus','flight','train','petrol','fuel','diesel','make my trip','rapido','booking.com','kayak','skyscanner','airbnb','expedia','tripadvisor','holiday','vacation','ethiia','qatarairways','delta','metro','travel'
    ],
    'Entertainment': [
        'netflix','hotstar','prime','movie','spotify','hulu','disney+','sony','music','concert','event','streaming','playstation','xbox','steam','minecraft','tiktok','jio hotstar','entertainment'
    ],
    'Health': [
        'doctor','clinic','hospital','medicine','pharmacy','ayushman card','wellness','fitness','gym','medicare','healthcare','dentist','optical','surgery','allergy','health','accident','operation'
    ],
    'Education': [
        'course','udemy','coursera','school','college','book','tuition','khanacademy','skillshare','linkedin learning','academic','edu','scholarship','canvas','physics wallah','apna college','unacademy','exam fees','certificates','byjus','allen','education'
    ],
    'Groceries': [
        'groceries','grocery','bigbasket','dmart','aldi','tesco','walmart','wholefoods','aldi','carrefour','supermarket','costco','lidl'
    ],
    'Transport': [
        'metro','bus','auto','cab','railway','uber','ola','taxi','lyft','tram','subway','ticket','commute','transportation','vehicle','transit'
    ],
    'Shop': [
	'shop'],
    'Others': [
        'miscellaneous','other','unknown','charity','gift','donation','subscription','club','membership','fee','tax','fine'
    ]
}


# ------------------------- Auto category function -------------------------
def auto_category(description: str) -> str:
    if not isinstance(description, str) or description.strip() == "":
        return "Others"
    text = description.lower()
    # direct memory exact match first
    mem = st.session_state.memory
    if text in mem:
        return mem[text]
    # keyword scanning
    for cat, kws in KEYWORD_MAP.items():
        for kw in kws:
            if kw in text:
                return cat
    return "Others"

# ------------------------- persist helper -------------------------
# ------------------------- persist helper -------------------------
def persist_all():
    # GET USER-SPECIFIC FILES
    exp_file, inc_file, mem_file = get_user_files()

    # SAVE DATA SEPARATELY FOR EACH USER
    save_csv_safe(st.session_state.expenses, exp_file)
    save_csv_safe(st.session_state.incomes, inc_file)

    # SAVE MEMORY (category learning)
    save_memory(st.session_state.memory, mem_file)

    # KEEP YOUR UPLOADER CSS SAME
    st.markdown("""
    <style>
    div[data-testid="stFileUploader"] > section {
        background-color: white !important;
        border: 2px solid #3B82F6 !important;
        padding: 10px !important;
        border-radius: 10px !important;
    }

    div[data-testid="stFileUploader"] label {
        color: black !important;
        font-weight: 600 !important;
    }

    div[data-testid="stFileUploader"] button {
        background-color: #3B82F6 !important;
        color: white !important;
        border-radius: 8px !important;
        padding: 8px 14px !important;
        border: none !important;
    }
    </style>
    """, unsafe_allow_html=True)



# ------------------------- Sidebar with icons -------------------------
with st.sidebar:
    st.markdown(
        "<div style='padding-left:16px;'>"
        "<span class='gtext gicon'>🤖</span>"
        "<strong style='color:white;font-size:20px'>AI PERSONAL EXPENSE ADVISOR</strong>"
        "</div>",
        unsafe_allow_html=True
    )

    st.markdown("<hr style='border-color:rgba(255,255,255,0.08)'>", unsafe_allow_html=True)

    menu = st.radio(
    "",
    ["Dashboard", "Expenses", "Income", "Forecast", "Reports", "AI Advice"],  # Added "AI Advice"
    index=0,
    format_func=lambda x: (
        "🏠 Dashboard" if x == "Dashboard"
        else "💸 Expenses" if x == "Expenses"
        else "💰 Income" if x == "Income"
        else "🔮 Forecast" if x == "Forecast"
        else "📊 Reports" if x == "Reports"
        else "🧠 AI Advice"  # Added AI Advice icon and label
    )
)


    st.markdown("---")
    # CSV uploader (expenses)
    uploaded = st.file_uploader("Upload expenses CSV/XLSX (optional)", type=['csv','xlsx'])
    if uploaded is not None:
        try:
            if uploaded.name.lower().endswith('.xlsx'):
                new = pd.read_excel(uploaded)
            else:
                new = pd.read_csv(uploaded)
            # normalize columns
            new_cols = [c.strip().lower() for c in new.columns]
            new.columns = new_cols
            required = {'date','amount','description'}
            if not required.issubset(set(new_cols)):
                st.error("Uploaded file must contain columns: date, amount, description (case-insensitive).")
            else:
                new['date'] = pd.to_datetime(new['date'], errors='coerce')
                if 'category' not in new.columns:
                    new['category'] = new['description'].apply(lambda x: auto_category(str(x)))
                else:
                    # fill blanks
                    new['category'] = new['category'].fillna('')
                    new.loc[new['category'].str.strip()=='','category'] = new.loc[new['category'].str.strip()=='','description'].apply(lambda x: auto_category(str(x)))
                new = new[['date','amount','description','category']]
                old_count = len(st.session_state.expenses)
                st.session_state.expenses = pd.concat([st.session_state.expenses, new], ignore_index=True)
                persist_all()
                st.success(f"Uploaded {len(new)} rows. Total now: {len(st.session_state.expenses)}")
        except Exception as e:
            st.error(f"Upload error: {e}")

    st.markdown("---")
    st.markdown("<div style='font-size:12px;color:rgba(255,255,255,0.9);padding-left:8px'>Tips: Use 'Teach the app' to correct categories. CSV uploads accept 'date','amount','description' columns.</div>", unsafe_allow_html=True)
        
# ------------------------- LOGOUT BUTTON -------------------------
    st.markdown("<hr>", unsafe_allow_html=True)

    if st.button("🚪 Logout"):
        logout()
        st.session_state.pop("logged_in_user", None)
        st.success("Logged out successfully!")
        st.rerun()
    
# ------------------------- Animated Header -------------------------
st.markdown(
    f"""
    <div class="hero">
      <div style="display:flex;align-items:center;justify-content:space-between;max-width:1180px;margin:auto">
        <div>
          <div class="hero-title">AI PERSONAL EXPENSE ADVISOR</div>
        </div>
      </div>
    </div>
    """,
    unsafe_allow_html=True
)

# ------------------------- Helper: render stats cards -------------------------
def render_stat_cards(exp_df):
    if exp_df.empty:
        total = 0
        this_month = 0
        avg_month = 0
        records = 0
    else:
        df = exp_df.copy()
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
        total = df['amount'].astype(float).sum()
        now = datetime.now()
        this_month = df.loc[df['date'].dt.month == now.month, 'amount'].sum() if 'date' in df else 0
        if df['date'].notnull().any():
            avg_month = df.groupby(df['date'].dt.to_period('M'))['amount'].sum().mean()
            avg_month = 0 if np.isnan(avg_month) else avg_month
        else:
            avg_month = 0
        records = len(df)
    c1, c2, c3, c4 = st.columns([1,1,1,1])
    c1.markdown(f"<div class='card'><span class='gtext gicon'>💰</span><div style='display:inline-block;vertical-align:middle'><div style='color:#6b7280'>Total spent</div><div class='stat-value'>₹{total:,.0f}</div></div></div>", unsafe_allow_html=True)
    c2.markdown(f"<div class='card'><span class='gtext gicon'>📅</span><div style='display:inline-block;vertical-align:middle'><div style='color:#6b7280'>This month</div><div class='stat-value'>₹{this_month:,.0f}</div></div></div>", unsafe_allow_html=True)
    c3.markdown(f"<div class='card'><span class='gtext gicon'>📈</span><div style='display:inline-block;vertical-align:middle'><div style='color:#6b7280'>Avg monthly</div><div class='stat-value'>₹{avg_month:,.0f}</div></div></div>", unsafe_allow_html=True)
    c4.markdown(f"<div class='card'><span class='gtext gicon'>🧾</span><div style='display:inline-block;vertical-align:middle'><div style='color:#6b7280'>Records</div><div class='stat-value'>{records}</div></div></div>", unsafe_allow_html=True)


# ------------------------- DASHBOARD (FULL & FINAL) -------------------------
if menu == "Dashboard":
    import plotly.graph_objects as go
    import plotly.express as px
    from datetime import datetime, date

    # --- Header / Overview ---
    st.markdown("""
    <div style="
        padding: 26px;
        border-radius: 16px;
        background: linear-gradient(135deg,#4F46E5,#3B82F6);
        color: #fff;
        font-family: 'Poppins', sans-serif;
        box-shadow: 0 8px 30px rgba(0,0,0,0.35);
        margin-bottom:18px;
    ">
        <h2 style="margin:0 0 6px 0;">🏠 Dashboard</h2>
        <div style="opacity:0.95; font-size:17px;">
            Complete financial snapshot: expenses, income analytics, trends, income vs expense comparison, 
            Financial Health meter, and convenient downloads.
        </div>
    </div>
    """, unsafe_allow_html=True)

    # --- Load Data ---
    df_exp = st.session_state.expenses.copy()
    df_inc = st.session_state.incomes.copy()

    # Ensure datetime conversion
    if not df_exp.empty:
        df_exp["date"] = pd.to_datetime(df_exp["date"], errors="coerce")
    if not df_inc.empty:
        df_inc["date"] = pd.to_datetime(df_inc["date"], errors="coerce")

    # ------------------------- EXPENSE STATS -------------------------
    total_spent = df_exp["amount"].sum() if not df_exp.empty else 0
    this_month_spent = df_exp[df_exp["date"].dt.month == date.today().month]["amount"].sum() if not df_exp.empty else 0
    avg_monthly_spend = df_exp.groupby(df_exp["date"].dt.to_period("M"))["amount"].sum().mean() if not df_exp.empty else 0
    total_records = len(df_exp)

    # ------------------------- INCOME STATS (FIXED) -------------------------
    if not df_inc.empty:
        df_inc["date"] = pd.to_datetime(df_inc["date"], errors="coerce")

    total_income = df_inc["amount"].sum() if not df_inc.empty else 0

    monthly_income = (
        df_inc[df_inc["date"].dt.month == date.today().month]["amount"].sum()
        if not df_inc.empty else 0
    )

    yearly_income = (
        df_inc[df_inc["date"].dt.year == date.today().year]["amount"].sum()
        if not df_inc.empty else 0
    )

    weekly_income = (
        df_inc[df_inc["date"].dt.isocalendar().week == datetime.now().isocalendar().week]["amount"].sum()
        if not df_inc.empty else 0
    )


    # ------------------------- CARD CSS -------------------------
    st.markdown("""
    <style>
    .dash-card {border-radius:12px; padding:18px; color:#fff; font-family:'Poppins';
    box-shadow:0 6px 18px rgba(0,0,0,0.25);}
    .dash-card .label {font-size:14px; opacity:0.95;}
    .dash-card .val {font-weight:900; font-size:24px; margin-top:6px;}
    .card-gradient-1 {background: linear-gradient(90deg,#06b6d4,#3b82f6);}
    .card-gradient-2 {background: linear-gradient(90deg,#7c3aed,#06b6d4);}
    .card-gradient-3 {background: linear-gradient(90deg,#06b6d4,#10b981);}
    .card-gradient-4 {background: linear-gradient(90deg,#ef4444,#f97316);}
    </style>
    """, unsafe_allow_html=True)

    # ------------------------- EXPENSE CARDS -------------------------
    col1, col2, col3, col4 = st.columns(4)
    col1.markdown(f"<div class='dash-card card-gradient-1'><div class='label'>Total Spent</div><div class='val'>₹{total_spent:,.0f}</div></div>", unsafe_allow_html=True)
    col2.markdown(f"<div class='dash-card card-gradient-2'><div class='label'>This Month Spend</div><div class='val'>₹{this_month_spent:,.0f}</div></div>", unsafe_allow_html=True)
    col3.markdown(f"<div class='dash-card card-gradient-3'><div class='label'>Avg Monthly Spend</div><div class='val'>₹{avg_monthly_spend:,.0f}</div></div>", unsafe_allow_html=True)
    col4.markdown(f"<div class='dash-card card-gradient-4'><div class='label'>Expense Records</div><div class='val'>{total_records}</div></div>", unsafe_allow_html=True)

    st.markdown(" ")

    # ------------------------- INCOME CARDS -------------------------
    i1, i2, i3, i4 = st.columns([1,1,1,1], gap="small")

    i1.markdown(f"<div class='dash-card card-gradient-1'><div class='label'>Total Income</div><div class='val'>₹{total_income:,.0f}</div></div>", unsafe_allow_html=True)
    i2.markdown(f"<div class='dash-card card-gradient-2'><div class='label'>Monthly Income</div><div class='val'>₹{monthly_income:,.0f}</div></div>", unsafe_allow_html=True)
    i3.markdown(f"<div class='dash-card card-gradient-3'><div class='label'>Weekly Income</div><div class='val'>₹{weekly_income:,.0f}</div></div>", unsafe_allow_html=True)
    i4.markdown(f"<div class='dash-card card-gradient-4'><div class='label'>Yearly Income</div><div class='val'>₹{yearly_income:,.0f}</div></div>", unsafe_allow_html=True)


    st.markdown("---")

    # ------------------------- VISUAL SUMMARY -------------------------
    st.markdown("""
    <h2 style='font-family:Poppins; font-size:32px; font-weight:700; color:#000; margin-bottom:12px;'>
    📊 Visual Summary
    </h2>
    """, unsafe_allow_html=True)

    left, right = st.columns([1.3, 1])


# ------------------------- LEFT: PIE + DAILY TREND -------------------------
    with left:

    # CATEGORY PIE CHART
        if not df_exp.empty:
            st.markdown("""
            <h3 style='font-family:Poppins; font-size:26px; font-weight:600; color:#000; margin-bottom:0px;'>
                📌 Spending by Category
            </h3>
            """, unsafe_allow_html=True)

            cat = df_exp.groupby("category")["amount"].sum().reset_index()

            fig_pie = px.pie(
                cat,
                names="category",
                values="amount",
                hole=0.45,
                title=""   # 🔥 THIS REMOVES "undefined"
            )
            fig_pie.update_traces(
                textinfo="label+percent",
                textfont=dict(size=14, color="#000")    # ← dark font added
            )
            fig_pie.update_layout(
                paper_bgcolor="white",
                plot_bgcolor="white",
                legend=dict(font=dict(color="#000")),
            )

            st.plotly_chart(fig_pie, use_container_width=True)


    # DAILY EXPENSE TREND
        if not df_exp.empty:
            st.markdown("""
            <h3 style='font-family:Poppins; font-size:24px; font-weight:600; color:#000; margin-top:10px;'>
            📈 Daily Expense Trend
            </h3>
            """, unsafe_allow_html=True)

            daily = df_exp.groupby(df_exp["date"].dt.date)["amount"].sum().reset_index()
            daily["date"] = pd.to_datetime(daily["date"])

            fig_daily = px.line(daily, x="date", y="amount", markers=True)
            fig_daily.update_traces(
                line_color="#3B82F6",
                line_width=3,
                marker=dict(size=7, color="#3B82F6", line=dict(width=1.5, color="white"))
            )

            fig_daily.update_layout(
                paper_bgcolor='white',
                plot_bgcolor='white',
                font=dict(color="#000"),
                xaxis=dict(title='📅 Date →', title_font=dict(color="#000"),                 tickfont=dict(color="#000"), linecolor="#000"),
                yaxis=dict(title='💵 ₹ Amount →', title_font=dict(color="#000"), tickfont=dict(color="#000"), linecolor="#000")
            )

            st.plotly_chart(fig_daily, use_container_width=True)




# =========================================================
# RIGHT COLUMN — YEARLY INCOME PIE + INCOME VS EXPENSE
# =========================================================
    with right:

    # ---------- YEARLY INCOME BY SOURCE ----------
        st.markdown("""
        <h3 style='font-family:Poppins; font-size:26px; font-weight:600; color:#000; margin-bottom:0px;'>
            Yearly Income by Source
        </h3>
        """, unsafe_allow_html=True)

        if not df_inc.empty:
            df_year = df_inc[df_inc["date"].dt.year == date.today().year]

            if not df_year.empty:
                src_sum = df_year.groupby("source")["amount"].sum().reset_index()

                fig_src = px.pie(
                    src_sum,
                    names="source",
                    values="amount",
                    hole=0.45,
                    title=""   # 🔥 NO UNDEFINED NOW
                )

                fig_src.update_traces(
                    textinfo="label+percent",
                    textfont=dict(size=14, color="#000")
                )

                fig_src.update_layout(
                    paper_bgcolor="white",
                    plot_bgcolor="white",
                    legend=dict(font=dict(color="#000")),
                )

                st.plotly_chart(fig_src, use_container_width=True)
            else:
                st.info("No income found for this year.")


    # ---------- INCOME VS EXPENSE ----------
        st.markdown("""
        <h3 style='font-family:Poppins; font-size:26px; font-weight:600; color:#000; margin-bottom:0px;'>
            📊 Income vs Expense (Monthly)    
        </h3>
        """, unsafe_allow_html=True)

        if (not df_exp.empty) or (not df_inc.empty):

            me = df_exp.groupby(df_exp['date'].dt.to_period("M"))['amount'].sum().reset_index().rename(columns={'amount':'expense'})
            mi = df_inc.groupby(df_inc['date'].dt.to_period("M"))['amount'].sum().reset_index().rename(columns={'amount':'income'})

            combined = pd.merge(mi, me, on='date', how='outer').fillna(0)
            combined['month'] = combined['date'].astype(str)

            fig_small = go.Figure()
            fig_small.add_trace(go.Scatter(
                x=combined['month'], y=combined['income'],
                mode='lines+markers', name='Income',
                line=dict(color='#10B981', width=3)
            ))
            fig_small.add_trace(go.Scatter(
                x=combined['month'], y=combined['expense'],
                mode='lines+markers', name='Expense',
                line=dict(color='#EF4444', width=3)
            ))

            fig_small.update_layout(
                title="Monthly Comparison",
                paper_bgcolor="white",
                plot_bgcolor="white",
                font=dict(color="#000000"),

                xaxis=dict(
                    title="Month →",
                    title_font=dict(color="#000000"),
                    tickfont=dict(color="#000000"),
                    linecolor="#000000",
                    gridcolor="rgba(0,0,0,0.15)"
                ),
                yaxis=dict(
                    title="💵 ₹ Amount →",
                    title_font=dict(color="#000000"),
                    tickfont=dict(color="#000000"),
                    linecolor="#000000",
                    gridcolor="rgba(0,0,0,0.15)"
                ),
                legend=dict(font=dict(color="#000000"))

            )

            st.plotly_chart(fig_small, use_container_width=True)

    # ------------------------- FINANCIAL HEALTH -------------------------
    st.markdown("""
    <h3 style='font-family:Poppins; font-size:26px; font-weight:600; color:#000; margin-bottom:0px;'>
        💹 Financial Health Meter    
    </h3>
    """, unsafe_allow_html=True)

    surplus = max(0, total_income - total_spent)
    health = (surplus / total_income * 100) if total_income > 0 else 0
    health = max(0, min(100, health))

    fig_health = go.Figure(go.Indicator(
        mode="gauge+number",
        value=health,
        number={'suffix':"%", 'font': {'size': 28, 'color':'#000'}},
        gauge={
            'axis': {'range': [0, 100]},
            'bar': {'color': "#3B82F6"},
            'steps': [
                {'range': [0, 40], 'color': "#ef4444"},
                {'range': [40, 70], 'color': "#f59e0b"},
                {'range': [70, 100], 'color': "#10b981"},
            ],
        }
    ))
    st.plotly_chart(fig_health, use_container_width=True)

    st.markdown("---")

    # ------------------------- DOWNLOADS -------------------------
    st.subheader("📂 Downloads & Quick Actions")
    c1, c2, c3 = st.columns(3)

    if not df_exp.empty:
        c1.download_button("⬇️ Download Expenses (CSV)", df_exp.to_csv(index=False), "expenses.csv")
    else:
        c1.write("No expense CSV")

    if not df_inc.empty:
        c2.download_button("⬇️ Download Income (CSV)", df_inc.to_csv(index=False), "income.csv")
    else:
        c2.write("No income CSV")


# ------------------------- Expenses page -------------------------
elif menu == "Expenses":
    st.header("💸 Expense Manager — Add / Edit / Analyze")

    # 🌈 Overview Card
    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, #1E3A8A, #3B82F6);
        padding: 20px;
        border-radius: 18px;
        color: white;
        font-family: 'Poppins', sans-serif;
        box-shadow: 0 8px 25px rgba(0,0,0,0.25);
        margin-bottom: 30px;
        border: 1px solid rgba(255,255,255,0.2);
    ">
        <h3>📘 Expense Overview</h3>
        <p style="font-size:16px; line-height:1.6;">
            Track, analyze, and visualize your daily expenses using AI insights  
            and advanced visualizations. From forecasts to category analysis,  
            this section gives you complete control of your financial data.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # 🧾 Add Expense
    st.subheader("🧾 Add New Expense")
    with st.form("add_expense_form", clear_on_submit=False):
        col1, col2, col3 = st.columns([2, 1, 3])
        d_in = col1.date_input("Date", value=date.today())
        amt = col2.number_input("Amount (₹)", min_value=0.0, value=100.0, step=10.0, format="%.2f")
        desc = col3.text_input("Description", "")
        cat_manual = st.text_input("Category (optional)")
        submitted = st.form_submit_button("💾 Add Expense")

        if submitted:
            try:
                cat_final = cat_manual.strip() if cat_manual.strip() else auto_category(desc)
                new = {'date': pd.to_datetime(d_in), 'amount': float(amt), 'description': desc, 'category': cat_final}
                st.session_state.expenses = pd.concat(
                    [st.session_state.expenses, pd.DataFrame([new])], ignore_index=True
                )
                persist_all()
                st.success(f"✅ Expense of ₹{amt:,.2f} added successfully!")
                rerun_after_action()
            except Exception as e:
                st.error(f"Add failed: {e}")

    st.markdown("---")

    # 📋 Expense Table
    st.subheader("📋 Your Recorded Expenses")
    exp = st.session_state.expenses.copy().reset_index().rename(columns={'index': 'row'})

    if exp.empty:
        st.info("No expense records found. Add some above to get started.")
    else:
        display_df = exp[['row', 'date', 'amount', 'description', 'category']].copy()
        display_df['date'] = pd.to_datetime(display_df['date'], errors='coerce').dt.strftime('%Y-%m-%d')
        st.dataframe(display_df, height=300)

        # ✏️ Edit / Delete
        st.subheader("✏️ Edit or Delete Expense")
        idx = st.number_input("Row index to edit/delete (start=0)", min_value=0, max_value=max(0, len(exp) - 1), value=0)
        choose_action = st.radio("Action", ["No action", "Change category", "Delete row"])

        if choose_action == "Change category":
            new_cat = st.selectbox("New category", options=[
                'Food', 'Shopping', 'Bills', 'Travel', 'Entertainment', 'Health',
                'Education', 'Groceries', 'Transport', 'Others'
            ])
            if st.button("Apply new category"):
                try:
                    real_idx = int(exp.loc[idx, 'row'])
                    desc_key = str(st.session_state.expenses.at[real_idx, 'description']).lower().strip()
                    st.session_state.expenses.at[real_idx, 'category'] = new_cat
                    st.session_state.memory[desc_key] = new_cat
                    persist_all()
                    st.success("✅ Category updated successfully.")
                    rerun_after_action()
                except Exception as e:
                    st.error(f"Update failed: {e}")

        elif choose_action == "Delete row":
            if st.button("🗑️ Delete selected row"):
                try:
                    real_idx = int(exp.loc[idx, 'row'])
                    st.session_state.expenses = st.session_state.expenses.drop(real_idx).reset_index(drop=True)
                    persist_all()
                    st.success("✅ Row deleted successfully.")
                    rerun_after_action()
                except Exception as e:
                    st.error(f"Delete failed: {e}")

        st.markdown("---")

        # 🎯 Monthly Expense Goal (Permanent + Editable Anytime)
        import json, os

        # 🔹 Load goal from JSON file if it exists
        GOAL_FILE = "goal_data.json"

        if "monthly_goal" not in st.session_state:
            if os.path.exists(GOAL_FILE):
                try:
                    data = json.load(open(GOAL_FILE))
                    st.session_state.monthly_goal = data.get("monthly_goal", 10000.0)
                except:
                    st.session_state.monthly_goal = 10000.0
            else:
                st.session_state.monthly_goal = 10000.0

        st.subheader("🎯 Monthly Expense Goal Progress")

        # 🔹 Display current goal
        st.markdown(f"### 💰 Current Goal: ₹{st.session_state.monthly_goal:,.2f}")

        # 🔘 Button to enable goal change
        if "edit_goal" not in st.session_state:
            st.session_state.edit_goal = False

        if not st.session_state.edit_goal:
            if st.button("✏️ Change Goal"):
                st.session_state.edit_goal = True
        else:
            new_goal = st.number_input(
                "Enter new monthly goal (₹)",
                min_value=0.0,
                value=st.session_state.monthly_goal,
                step=500.0,
                key="goal_input"
            )

            save_col, cancel_col = st.columns(2)
            if save_col.button("💾 Save Goal"):
                st.session_state.monthly_goal = new_goal
                json.dump({"monthly_goal": st.session_state.monthly_goal}, open(GOAL_FILE, "w"))
                st.session_state.edit_goal = False
                st.success(f"✅ Monthly goal updated to ₹{new_goal:,.2f}")
                rerun_after_action()

            if cancel_col.button("❌ Cancel"):
                st.session_state.edit_goal = False
                st.info("Goal change cancelled.")

        # 🔹 Use goal in expense calculation
        monthly_goal = st.session_state.monthly_goal
        exp['date'] = pd.to_datetime(exp['date'], errors='coerce')
        current_month = exp[exp['date'].dt.month == datetime.now().month]
        monthly_spent = current_month['amount'].sum()
        progress = (monthly_spent / monthly_goal) * 100 if monthly_goal > 0 else 0

        st.progress(min(progress / 100, 1.0))
        st.markdown(f"**You’ve spent ₹{monthly_spent:,.2f} out of ₹{monthly_goal:,.2f} ({progress:.1f}%) this month.**")

        if progress > 100:
            st.warning("⚠️ You’ve exceeded your monthly budget goal!")
        elif progress > 75:
            st.info("🟠 You’re nearing your limit. Be cautious this week.")
        else:
            st.success("🟢 Great! You’re managing within your target.")

        # 📈 Daily Expense Trend
        st.subheader("📈 Expense Trend Over Time")
        trend = exp.groupby(exp['date'].dt.date)['amount'].sum().reset_index()
        fig = px.line(
            trend, x='date', y='amount', markers=True,
            title="📊 Daily Expense Trend",
            labels={'date': '📅 Date →', 'amount': '🧾₹ Expense →'}
        )
        fig.update_traces(line_color='#0072FF', line_width=3,
                          marker=dict(size=7, color='#0072FF', line=dict(width=1.5, color='white')))
        st.plotly_chart(fig, use_container_width=True)

        # 🤖 Weekly AI Forecast
        st.subheader("🤖 Weekly AI Forecast")
        exp['week'] = exp['date'].dt.isocalendar().week
        exp['year'] = exp['date'].dt.year
        exp['week_start'] = exp['date'] - pd.to_timedelta(exp['date'].dt.weekday, unit='d')
        weekly_expense = exp.groupby(['year', 'week', 'week_start'])['amount'].sum().reset_index()

        if len(weekly_expense) >= 2:
            current_week = weekly_expense.iloc[-1]['amount']
            prev_week = weekly_expense.iloc[-2]['amount']
            change_percent = ((current_week - prev_week) / prev_week) * 100 if prev_week != 0 else 0
            if change_percent > 10:
                st.error(f"🚨 Overspending Alert! You spent {change_percent:.1f}% more than last week.")
            elif change_percent < -5:
                st.success(f"✅ Great Job! You reduced expenses by {abs(change_percent):.1f}% this week.")
            else:
                st.info(f"ℹ️ Spending is stable (±{abs(change_percent):.1f}%).")

        # 🔮 Next Week Prediction
        st.subheader("🔮 AI Predicted Next Week Expense")
        if len(weekly_expense) >= 3:
            X = np.arange(len(weekly_expense)).reshape(-1, 1)
            y = weekly_expense['amount'].values
            model = LinearRegression().fit(X, y)
            prediction = model.predict([[len(weekly_expense)]])[0]
            st.markdown(f"📊 **Estimated next week’s expense:** ₹{prediction:,.2f}")
        else:
            st.info("🧩 Add at least 3 weeks of data for prediction.")

        
        # 📆 5-Week Comparison
        st.subheader("📆 Last 5 Weeks Expense Comparison")

        # Add week start date for readability
        exp['week_start'] = exp['date'] - pd.to_timedelta(exp['date'].dt.weekday, unit='d')

        # Group by year, week, and week_start for clear labeling
        weekly_expense = exp.groupby(['year', 'week', 'week_start'])['amount'].sum().reset_index()

        # Take last 5 weeks
        last5 = weekly_expense.tail(5)

        # Bar chart with readable x-axis
        fig_bar = px.bar(
            last5,
            x='week_start',
            y='amount',
            text_auto=True,
            color='amount',
            color_continuous_scale='Blues',
            title="📆 Last 5 Weeks Expense Comparison"
        )

        fig_bar.update_layout(
            xaxis_title="📅 Week Starting",
            yaxis_title="₹ Total Expense",
            font=dict(family="Poppins", size=14),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            title_font=dict(size=18)
        )

        # Add hover info
        fig_bar.update_traces(
            hovertemplate="<b>Week of %{x|%b %d, %Y}</b><br>Expense: ₹%{y:,.2f}<extra></extra>"
        )

        st.plotly_chart(fig_bar, use_container_width=True)


        # 🧠 Category Breakdown
        st.subheader("🧠 AI Category-Wise Breakdown")
        category_exp = exp.groupby("category")["amount"].sum().reset_index().sort_values(by="amount", ascending=False)
        fig_cat = px.bar(category_exp, x="category", y="amount", color="amount",
                         text_auto=True, title="Spending by Category", color_continuous_scale="Viridis")
        st.plotly_chart(fig_cat, use_container_width=True)

        # 🔥 AI Suggestion
        if not category_exp.empty:
            top_cat = category_exp.iloc[0]["category"]
            st.markdown(f"""
            <div style="background:rgba(0,114,255,0.1);padding:20px;border-radius:15px;">
                <h4>💡 AI Suggestion for {top_cat}</h4>
                <ul>
                    <li>Try cutting down spending on <b>{top_cat}</b> by 15-20% next week.</li>
                    <li>Set a weekly limit alert for this category.</li>
                    <li>Review unnecessary items to save ₹500–₹1000 easily.</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)

        # 🗓️ Heatmap Visualization
        st.subheader("🌡️ Expense Heatmap Calendar")
        heatmap_data = exp.groupby(exp['date'].dt.date)['amount'].sum().reset_index()
        fig_heat = px.density_heatmap(
            heatmap_data,
            x='date', y='date', z='amount',
            color_continuous_scale='RdYlBu_r',
            title="Expense Intensity Calendar"
        )
        fig_heat.update_layout(
            xaxis_title="📅 Date",
            yaxis_title="🧾 Expense Intensity",
            coloraxis_colorbar=dict(title="₹ Spent"),
            font=dict(family="Poppins", color="black")
        )

        st.plotly_chart(fig_heat, use_container_width=True)

        # 📂 Download CSV
        csv = exp.to_csv(index=False).encode("utf-8")
        st.download_button("⬇️ Download Expense Records (CSV)", data=csv, file_name="expense_records.csv", mime="text/csv")

        # 💡 Smart Insights
        st.markdown("""
        <div style="
            background: rgba(0,114,255,0.1);
            padding: 20px;
            border-radius: 15px;
            margin-top: 25px;
            font-family: 'Poppins';
        ">
            <h4>💡 Smart Expense Insights</h4>
            <ul>
                <li>Use the Heatmap to spot high-spending dates instantly.</li>
                <li>Monitor your monthly goal — aim to stay below 80% mid-month.</li>
                <li>Track category-wise peaks and use AI suggestions for optimization.</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)


# ------------------------- Income page -------------------------
elif menu == "Income":
    st.header("💰 Income Manager")

    # Initialize income DataFrame
    if "incomes" not in st.session_state:
        st.session_state.incomes = pd.DataFrame(columns=["id", "date", "amount", "source"])

    df_income = st.session_state.incomes.copy()

    # ---------------- INCOME OVERVIEW ---------------- #
    if not df_income.empty:
        total_income = df_income["amount"].sum()
        avg_income = total_income / max(1, len(df_income["date"].astype(str).str[:7].unique()))
        top_source = df_income["source"].mode()[0] if not df_income["source"].empty else "N/A"
        last_date = df_income["date"].max()

        st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, #1E3A8A, #3B82F6);
            padding: 20px;
            border-radius: 18px;
            color: white;
            font-family: 'Poppins', sans-serif;
            box-shadow: 0 8px 25px rgba(0,0,0,0.25);
            margin-bottom: 28px;
            border: 1px solid rgba(255,255,255,0.25);
        ">
            <h3 style="margin-bottom:12px;">📘 Income Overview</h3>
            <ul style="font-size:16px; line-height:1.8; margin-left:18px;">
                <li>Total Recorded Income: <b>₹{total_income:,.2f}</b></li>
                <li>Average Monthly Income: <b>₹{avg_income:,.2f}</b></li>
                <li>Primary Source: <b>{top_source}</b></li>
                <li>Last Income Added On: <b>{last_date}</b></li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.info("📘 No income records yet. Add your first one below.")

    # 🧾 Add Income Form
    with st.form("add_income_form", clear_on_submit=False):
        c1, c2, c3 = st.columns([2, 1, 2])
        idate = c1.date_input("Date", value=date.today())
        iamt = c2.number_input("Amount (₹)", min_value=0.0, value=1000.0, step=100.0)
        src = c3.text_input("Source", value="Salary")

        submitted = st.form_submit_button("💾 Add Income")
        if submitted:
            try:
                new_id = np.random.randint(10**7, 10**9)
                new = {'date': pd.to_datetime(idate), 'amount': float(iamt), 'source': src, 'id': new_id}
                st.session_state.incomes = pd.concat(
                    [st.session_state.incomes, pd.DataFrame([new])], ignore_index=True
                )
                persist_all()
                with st.spinner("🔄 Saving income..."):
                    time.sleep(0.7)
                st.success("✅ Income added successfully!")
                rerun_after_action()
            except Exception as e:
                st.error(f"Add income failed: {e}")

    st.markdown("---")

    # ---------------- INCOME RECORDS ---------------- #
    st.subheader("📜 Income Records")
    df_income = st.session_state.incomes.copy().reset_index(drop=True)

    if not df_income.empty:
        df_income["date"] = pd.to_datetime(df_income["date"], errors="coerce").dt.strftime("%Y-%m-%d")
        st.dataframe(df_income[["id", "date", "amount", "source"]], height=280)

    # Modify / Delete income
        st.markdown("### ✏️ Modify or Delete Income")
        col1, col2 = st.columns(2)

    # ✏️ Modify Income Section (fixed version)
    # ✏️ Modify Income Section (Fixed + Clean Indentation)
        with col1:
            mod_id = st.number_input("Enter Income ID to Modify", min_value=0, step=1)

        # Step 1: enable edit mode once valid ID entered
            if st.button("✏️ Modify"):
                if mod_id in df_income["id"].values:
                    st.session_state.editing_income = True
                    st.session_state.edit_id = mod_id
                    st.success(f"Editing mode ON for ID {mod_id}")
                else:
                    st.warning("⚠️ ID not found in records.")

        # Step 2: show editable fields if in edit mode
            if st.session_state.get("editing_income", False):
                edit_id = st.session_state.get("edit_id")

                if edit_id in df_income["id"].values:
                    row = df_income[df_income["id"] == edit_id].iloc[0]
                    st.info(f"🛠️ Modifying record ID {edit_id}")

                    new_amt = st.number_input("New Amount (₹)", value=float(row["amount"]), step=100.0, key="edit_amt")
                    new_src = st.text_input("New Source", value=row["source"], key="edit_src")

                    save_col, cancel_col = st.columns(2)

                    with save_col:
                        if st.button("✅ Save Changes"):
                            try:
                                idx = df_income.index[df_income["id"] == edit_id][0]
                                st.session_state.incomes.at[idx, "amount"] = new_amt
                                st.session_state.incomes.at[idx, "source"] = new_src
                                
                                exp_file, inc_file, mem_file = get_user_files()

                                persist_all()

                            # Reload immediately from file
                                st.session_state.incomes = pd.read_csv(inc_file)
                                st.session_state.incomes['date'] = pd.to_datetime(st.session_state.incomes['date'], errors='coerce')
                                st.success(f"✅ Income ID {edit_id} updated successfully!")
                                st.session_state.editing_income = False
                                rerun_after_action()
                            except Exception as e:
                                st.error(f"⚠️ Update failed: {e}")

                    with cancel_col:
                        if st.button("❌ Cancel Edit"):
                            st.session_state.editing_income = False
                            st.info("Edit cancelled.")
                else:
                    st.warning("⚠️ ID not found in records.")  # ✅ Correct indentation here


    # 🗑️ Delete Income Section
        with col2:
            del_id = st.number_input("Enter Income ID to Delete", min_value=0, step=1, key="delete_id")
            if st.button("🗑️ Delete"):
                if del_id in df_income["id"].values:
                    try:
                        st.session_state.incomes = st.session_state.incomes[
                            st.session_state.incomes["id"] != del_id
                        ].reset_index(drop=True)
                        persist_all()
                        with st.spinner("🧹 Deleting record..."):
                            time.sleep(0.8)
                        st.success(f"✅ Deleted record ID {del_id} successfully!")
                        rerun_after_action()
                    except Exception as e:
                        st.error(f"⚠️ Delete failed: {e}")
                else:
                    st.warning("⚠️ ID not found in records.")

    else:
        st.info("📭 No income records found yet. Add new entries above to get started.")


               # ---------------- MONTHLY CHART (Enhanced Visibility) ---------------- #
    # ---------------- MONTHLY CHART + LINE CHART + DOWNLOAD + SMART TIPS ---------------- 
    st.subheader("📈 Monthly Income Trend")

# Ensure date is parsed correctly
    df_income["date"] = pd.to_datetime(df_income["date"], errors="coerce")

# Group by month
    monthly = (
        df_income.groupby(df_income["date"].dt.to_period("M"))["amount"]
        .sum()
        .reset_index()
    )
    monthly["month"] = monthly["date"].dt.strftime("%b %Y")  # 👈 show Jan, Feb, Mar format

    # ----------- BAR CHART -----------
    fig_bar = px.bar(
        monthly,
        x="month",
        y="amount",
        text="amount",
        title="📊 Monthly Income Overview",
        labels={"month": "📅 Month →", "amount": "₹ Income →"},
    )    
    fig_bar.update_traces(
        marker_color="#0072FF",
        texttemplate="₹%{text:,.0f}",
        textposition="outside"
    )

    fig_bar.update_layout(
        paper_bgcolor="white",
        plot_bgcolor="white",
        font=dict(color="#111111", family="Poppins", size=16),
        title_font=dict(size=20, color="#000000", family="Poppins"),

        xaxis=dict(
            showgrid=True,
            gridcolor='rgba(0,0,0,0.15)',
            showline=True,
            linecolor='rgba(0,0,0,1)',
            ticks='outside',
            tickfont=dict(size=15, color='black', family='Poppins'),
            title_font=dict(color='black', size=19, family='Poppins'),
            tickformat="%b %Y",        # ✔ OK (Month only)
            showspikes=True,
            title="📅 Month →",
            mirror=True,
            zeroline=False
        ),

        yaxis=dict(
            showgrid=True,
            gridcolor="rgba(0,0,0,0.15)",
            linecolor='rgba(0,0,0,1)',
            ticks='outside',
            tickfont=dict(size=15, color='black', family='Poppins'),
            title_font=dict(color='black', size=19, family='Poppins'),
           # ❌ REMOVE WRONG tickformat (THIS CAUSED FADE BUG)
            showspikes=True,
            title="💰 ₹ Income →",
            mirror=True,
            zeroline=False
        ),

        margin=dict(t=60, b=60, l=80, r=40),
    )
    st.plotly_chart(fig_bar, use_container_width=True)


# ----------- LINE CHART -----------
    st.subheader("📈 Income Growth Line Chart")
    fig_line = px.line(
        monthly,
        x="month",
        y="amount",
        markers=True,
        title="📈 Monthly Income Growth Trend",
        labels={"month": "📅 Month →", "amount": "₹ Income →"}
    )

    fig_line.update_traces(
        line_color="#0072FF",
        line_width=3,
        marker=dict(size=9, color="#0072FF", line=dict(width=1.8, color="white"))
    )

    fig_line.update_layout(
        paper_bgcolor="white",
        plot_bgcolor="white",
        font=dict(color="#000000", family="Poppins", size=15),
        title_font=dict(size=20, color="#000000", family="Poppins"),

        xaxis=dict(
            showgrid=True,
            gridcolor="rgba(0,0,0,0.2)",
            linecolor='black',
            ticks='outside',
            tickfont=dict(size=15, color='black', family='Poppins'),
            title_font=dict(color='black', size=19, family='Poppins'),
            tickformat="%b %Y",        # ✔ Only for month
            showspikes=True,
            title="📅 Month →"
        ),

        yaxis=dict(
            showgrid=True,
            gridcolor="rgba(0,0,0,0.2)",
            linecolor='black',
            ticks='outside',
            tickfont=dict(size=15, color='black', family='Poppins'),
            title_font=dict(color='black', size=19, family='Poppins'),
        # ❌ REMOVE WRONG tickformat
            showspikes=True,
            title="💰 ₹ Income →"
        ),

        margin=dict(t=60, b=60, l=80, r=40),
    )

    st.plotly_chart(fig_line, use_container_width=True)


    # ----------- DOWNLOAD CSV -----------
    st.subheader("⬇️ Export Income Data")
    csv = df_income.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="💾 Download Income Records (CSV)",
        data=csv,
        file_name="income_records.csv",
        mime="text/csv",
        use_container_width=True
    )

# ----------- SMART INCOME TIPS -----------
    st.markdown("""
    <div style="
        background: rgba(0, 114, 255, 0.1);
        padding: 20px;
        border-radius: 15px;
        font-family: 'Poppins';
        margin-top: 25px;
        border: 1px solid rgba(0,0,0,0.05);
    ">
        <h4>💡 Smart Income Management Tips</h4>
        <ul style="line-height:1.8; font-size:16px;">
            <li>🏦 <b>Automate savings</b> by moving 20% of income to a separate account every month.</li>
            <li>📊 Maintain income categories (Salary, Freelance, Bonus) to see which source is growing fastest.</li>
            <li>🧾 Update wrong entries immediately — accurate data = accurate analysis.</li>
            <li>💰 Keep at least 3 months of income saved as an <b>emergency fund</b>.</li>
            <li>📈 Track your monthly trend — aim for at least a 10% income growth every quarter.</li>
            <li>🎯 Use surplus income for short-term investments or debt reduction.</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    


# ------------------------- Forecast page -------------------------
elif menu == "Forecast":
    st.header("🔮 Forecast & Predictions")

    df = st.session_state.expenses.copy()

    if df.empty or len(df) < 3:
        st.info("📊 Add at least 3 expense records for a meaningful forecast.")
    else:
        try:
            # Overview Theory
            st.markdown("""
            <div style="
                background: linear-gradient(135deg, #1E3A8A, #3B82F6);
                padding: 20px;
                border-radius: 15px;
                color: white;
                font-family: 'Poppins', sans-serif;
                margin-bottom: 20px;
            ">
            <h3>📈 Forecast Overview</h3>
            <p style="font-size:16px; line-height:1.6;">
            The <b>AI Forecast module</b> analyzes your past daily expenses and predicts            <b>future spending trends</b> using a regression-based model.<br>
            It helps you visualize upcoming financial patterns so you can <b>plan budgets,             track spikes, and optimize savings</b> effectively.<br>
            This forecast considers your <b>historical averages</b> and <b>trend slopes</b>   to provide accurate insights for smarter decision-making.
            </p>
            </div>
            """, unsafe_allow_html=True)


            # Data preparation
            df['date'] = pd.to_datetime(df['date'], errors='coerce')
            daily = df.groupby(df['date'].dt.date)['amount'].sum().reset_index().rename(columns={'date': 'day'})
            daily['day'] = pd.to_datetime(daily['day'])

            if daily.empty:
                st.warning("⚠️ Not enough daily data available for trend prediction.")
            else:
                # Apply smoothing for realistic trend
                daily['smoothed'] = daily['amount'].rolling(window=3, min_periods=1).mean()

                # Regression Model
                X = np.arange(len(daily)).reshape(-1, 1)
                y = daily['smoothed'].values
                model = LinearRegression().fit(X, y)

                # Prediction for next N days
                n = st.slider("🔢 Select number of days to predict", 3, 30, 10)
                future_index = np.arange(len(daily), len(daily) + n)
                preds = model.predict(future_index.reshape(-1, 1))

                # Add a little realistic variation
                variation = np.sin(np.linspace(0, 2 * np.pi, n)) * 100
                preds = preds + variation

                # Future Dates
                future_dates = [daily['day'].max() + timedelta(days=i + 1) for i in range(n)]
                pred_df = pd.DataFrame({'date': future_dates, 'predicted_amount': np.round(preds, 2)})

                st.markdown("### 🗓️ Forecasted Expense for Upcoming Days")
                st.dataframe(pred_df.style.format({'predicted_amount': '₹{:,.2f}'.format}))

                # Combine past + future data for chart
                past = daily[['day', 'amount']].rename(columns={'day': 'date', 'amount': 'value'})
                future = pred_df.rename(columns={'predicted_amount': 'value'})
                combined = pd.concat([past, future], ignore_index=True)

                # Create interactive Line Chart (Improved Visibility)
                fig = px.line(
                    combined,
                    x='date',
                    y='value',
                    markers=True,
                    title="📊 Expense Forecast Trend",
                    labels={'date': '📅 Date →', 'value': '₹ Amount (Y-axis ↑)'}
                )

                # Highlight past vs future data visually
                past_count = len(past)
                fig.update_traces(
                    line_color='#5B21B6',  # Deep royal purple
                    line_width=3,
                    marker=dict(
                        size=8,
                        color='#5B21B6',
                        line=dict(width=1.5, color='white')
                    ),
                    selector=dict(mode='lines+markers')
                )

                # Add dotted line style for predicted future part
                fig.add_scatter(
                    x=future['date'],
                    y=future['value'],
                    mode='lines+markers',
                    name='Predicted',
                    line=dict(color='#9333EA', width=3, dash='dot'),
                    marker=dict(size=7, color='#9333EA', line=dict(width=1.5, color='white'))
                )

                # Better layout and contrast
                fig.update_layout(
                    paper_bgcolor='rgba(255,255,255,1)',  # pure white opaque background
                    plot_bgcolor='rgba(255,255,255,1)',   # no fade layer
                    font=dict(color='rgba(0,0,0,1)', family='Poppins', size=15),  # solid black font
                    xaxis=dict(
                        showgrid=True,
                        gridcolor='rgba(0,0,0,0.15)',
                        showline=True,
                        linecolor='rgba(0,0,0,1)',  # pure black axis line
                        ticks='outside',
                        tickfont=dict(size=15, color='rgba(0,0,0,0.95)', family='Poppins'),  # solid black ticks
                        mirror=True,
                        title='📅 Date →',
                        title_font=dict(color='rgba(0,0,0,1)', size=19, family='Poppins'),
                        tickformat="%d %b %Y",
                        showspikes=True,
                        zeroline=False
                    ),
                    yaxis=dict(
                        showgrid=True,
                        gridcolor='rgba(0,0,0,0.15)',
                        showline=True,
                        linecolor='rgba(0,0,0,1)',
                        ticks='outside',
                        tickfont=dict(size=15, color='rgba(0,0,0,0.95)', family='Poppins'),
                        mirror=True,
                        title='💵 Amount (₹) →',
                        title_font=dict(color='rgba(0,0,0,1)', size=19, family='Poppins'),


                        zeroline=False
                    ),
                    margin=dict(t=70, b=60, l=80, r=40),
                    legend=dict(
                        title='Legend',
                        orientation='h',
                        yanchor='bottom',
                        y=1.08,
                        xanchor='center',
                        x=0.5,
                        bgcolor='rgba(255,255,255,1)',
                        bordercolor='rgba(0,0,0,0.3)',
                        borderwidth=1,
                        font=dict(color='rgba(0,0,0,1)', size=13)
                    ),
                    title_font=dict(size=21, color='rgba(0,0,0,1)', family='Poppins')

                )

                st.plotly_chart(fig, use_container_width=True)

        except Exception as e:
            st.error(f"⚠️ Forecast processing error: {e}") 

# ------------------------- Reports -------------------------
elif menu == "Reports":
    
    
    st.header("📊 Reports & Insights")

    df = st.session_state.expenses.copy()
    if df.empty:
        st.info("No expenses recorded yet.")
    else:
        # Calculations
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
        total_spent = df['amount'].sum()
        start_date, end_date = df['date'].min().date(), df['date'].max().date()
        avg_monthly = total_spent / max(1, len(df['date'].dt.to_period('M').unique()))
        top_cat = df.groupby('category')['amount'].sum().idxmax()

        # 🌊 Vibrant Blue Gradient Overview Card (Same as Forecast Section)
        st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, #1E3A8A, #2563EB);
            padding: 25px;
            border-radius: 18px;
            color: white;
            font-family: 'Poppins', sans-serif;
            box-shadow: 0 8px 25px rgba(0,0,0,0.25);
            margin-bottom: 28px;
            border: 1px solid rgba(255,255,255,0.25);
        ">
            <h3 style="margin-bottom:12px; font-size:22px;">📘 Expense Overview</h3>
            <p style="font-size:16px; line-height:1.7;">
                Here's a summary of your financial activity between 
                <b>{start_date}</b> and <b>{end_date}</b>.
            </p>
            <ul style="font-size:16px; line-height:1.8; margin-left:18px;">
                <li>Total spent during this period: <b>₹{total_spent:,.2f}</b></li>
                <li>Average monthly spending: <b>₹{avg_monthly:,.2f}</b></li>
                <li>Most spent category: <b>{top_cat}</b></li>
            </ul>
            <p style="font-size:15px; line-height:1.6; margin-top:12px;">
                This report gives you a breakdown of your expenses by 
                <b>category</b>, <b>month</b>, and <b>year</b> — helping you 
                visualize and control your spending more effectively.
            </p> 
        </div>
        """, unsafe_allow_html=True)

        # Dummy spacing for layout adjustment
        st.write("")


        

        # ===== TOTAL PER CATEGORY =====
        st.subheader("💰 Total per Category")
        per_cat = df.groupby('category')['amount'].sum().reset_index().sort_values('amount', ascending=False)
        st.dataframe(per_cat, use_container_width=True)

        # ===== MONTHLY TOTAL =====
        st.subheader("📅 Monthly Total")
        monthly = df.groupby(df['date'].dt.to_period('M'))['amount'].sum().reset_index()
        monthly['Month'] = monthly['date'].astype(str)
        monthly = monthly.rename(columns={'amount': 'Total Amount (₹)'})
        st.dataframe(monthly[['Month', 'Total Amount (₹)']], use_container_width=True)

        # ===== YEARLY TOTAL =====
        st.subheader("🗓️ Yearly Total")
        yearly = df.groupby(df['date'].dt.year)['amount'].sum().reset_index()
        yearly = yearly.rename(columns={'date': 'Year', 'amount': 'Total Amount (₹)'})
        st.dataframe(yearly, use_container_width=True)

        # ===== GRAND TOTAL =====
        st.success(f"🏦 **Overall Total Spent:** ₹{total_spent:,.2f}")

        # ===== DOWNLOAD OPTION =====
        st.download_button(
            "⬇️ Download expenses CSV",
            data=df.to_csv(index=False).encode('utf-8'),
            file_name="expenses_export.csv"
        )

        # ===== VISUAL CHARTS =====
        st.markdown("## 📈 Spending Trends Visualization")
        # -------------------------------------------
# THEME DETECTION (Light / Dark Auto-Support)
# -------------------------------------------
        theme = st.get_option("theme.base")
        is_dark = theme == "dark"

        text_color = "#FFFFFF" if is_dark else "#000000"
        axis_color = "#FFFFFF" if is_dark else "#000000"
        grid_color = "rgba(255,255,255,0.25)" if is_dark else "rgba(0,0,0,0.2)"

# -------------------------------------------
# ----------- MONTHLY TREND ---------------
# -------------------------------------------
        st.markdown("<h4 style='color:#60A5FA'>📆 Monthly Spending Trend</h4>", unsafe_allow_html=True)

        fig_monthly = px.line(
            monthly,
            x='Month',
            y='Total Amount (₹)',
            markers=True
        )

        fig_monthly.update_traces(
            line_color="#2563EB",
            line_width=3,
            marker=dict(size=8, color="#3B82F6")
        ) 

        fig_monthly.update_layout(
            paper_bgcolor='white',
            plot_bgcolor='white',
            font=dict(color=text_color, size=13),

            xaxis=dict(
                title='🗓️ Month →',
                title_font=dict(size=15, color=axis_color),
                tickfont=dict(size=12, color=axis_color),
                showgrid=True,
                gridcolor=grid_color,
                showline=True,
                linecolor=axis_color,
                linewidth=1.5,
            ),

            yaxis=dict(
                title='💵 Amount (₹) →',
                title_font=dict(size=15, color=axis_color),
                tickfont=dict(size=12, color=axis_color),
                showgrid=True,
                gridcolor=grid_color,
                showline=True,
                linecolor=axis_color,
                linewidth=1.5,
            )
        )

        st.plotly_chart(fig_monthly, use_container_width=True)

# -------------------------------------------
# ----------- YEARLY TREND -----------------
# -------------------------------------------
        st.markdown("<h4 style='color:#34D399'>📅 Yearly Spending Comparison</h4>",  unsafe_allow_html=True)

        fig_yearly = px.bar(
            yearly,
            x='Year',
            y='Total Amount (₹)',
            text='Total Amount (₹)'
        )

        fig_yearly.update_traces(
            texttemplate='₹%{text:,.0f}',
            textposition='outside',
            marker_color='#10B981'
        ) 

        fig_yearly.update_layout(
            paper_bgcolor='white',
            plot_bgcolor='white',
            font=dict(color=text_color, size=13),

            xaxis=dict(
                title='📅 Year →',
                title_font=dict(size=15, color=axis_color),
                tickfont=dict(size=12, color=axis_color),
                showgrid=True,
                gridcolor=grid_color,
                showline=True,
                linecolor=axis_color,
                linewidth=1.5,
            ),

            yaxis=dict(
                title='💵 Amount (₹) →',
                title_font=dict(size=15, color=axis_color),
                tickfont=dict(size=12, color=axis_color),
                showgrid=True,
                gridcolor=grid_color,
                showline=True,
                linecolor=axis_color,
                linewidth=1.5,
            )
        )

        st.plotly_chart(fig_yearly, use_container_width=True)


# --------------------------- Ai Advice ------------------------------
elif menu == "AI Advice":
    st.header("🧠 AI Advice")

    df = st.session_state.expenses.copy()

    if df.empty:
        st.warning("⚠️ No expenses recorded yet. Add your expenses to get AI-powered insights!")
    else:
        st.markdown("""
        <div style="
            background: linear-gradient(135deg, #1E3A8A, #2563EB);
            padding: 20px;
            border-radius: 15px;
            color: white;
            font-family: 'Poppins', sans-serif;
            margin-bottom: 20px;
        ">
        <h3>🤖 AI Expense Analysis Overview</h3>
        <p style="font-size:16px; line-height:1.6;">
        Your <b>AI Personal Expense Advisor</b> examines your recorded expenses and spending categories to detect <b>spending patterns</b>.<br>
        It compares your expenses with your income (if available), identifies <b>   overspending areas</b>, and gives <b>personalized suggestions</b> for smarter money management.<br>
        These insights help you <b>save strategically</b> and balance your lifestyle with financial discipline.
        </p>
        </div>
        """, unsafe_allow_html=True)


        # Total spent and category-wise breakdown
        category_spending = df.groupby("category")["amount"].sum().reset_index()
        category_spending = category_spending.sort_values(by="amount", ascending=False)
        total_spent = category_spending["amount"].sum()

        total_income = st.session_state.incomes["amount"].sum() if not st.session_state.incomes.empty else 0
        top_cat = category_spending.iloc[0]["category"]
        top_amt = category_spending.iloc[0]["amount"]

        st.markdown("### 💸 Spending Summary")
        st.dataframe(category_spending, height=220)
        st.success(f"📊 You’ve spent a total of **₹{total_spent:,.2f}** this month — most on **{top_cat} (₹{top_amt:,.2f})**")

        # Personalized insights list
        st.markdown("### 💬 AI-Generated Personal Recommendations")

        tips = []

        # 1️⃣ Category-based smart advice
        for _, row in category_spending.iterrows():
            cat = row["category"]
            amt = row["amount"]

            if amt > 0.25 * total_spent:
                tips.append(f"⚠️ Your spending on **{cat}** is unusually high (₹{amt:,.0f}). Try limiting this to 20% of total expenses next month.")
            elif amt < 0.05 * total_spent:
                tips.append(f"✅ Spending on **{cat}** is under control — great job maintaining discipline!")

        # 2️⃣ Income to expense ratio analysis
        if total_income > 0:
            ratio = (total_spent / total_income) * 100
            if ratio > 80:
                tips.append("🚨 You're spending over **80% of your income**! Consider reviewing essential vs non-essential expenses.")
            elif 60 < ratio <= 80:
                tips.append("💡 Spending between 60–80% of income — you can aim to save a little more each month.")
            else:
                tips.append("🟢 Excellent! You're spending wisely and maintaining a good savings margin.")

            # AI Suggested savings
            tips.append(f"💰 Based on your income, you should save **₹{round(total_income * 0.2):,} (20%)** monthly as your base goal.")

        # 3️⃣ Detecting overspending patterns based on user data
        recent_expenses = df.sort_values(by="date", ascending=False).head(5)
        avg_expense = df["amount"].mean()

        for _, exp in recent_expenses.iterrows():
            if exp["amount"] > avg_expense * 1.5:
                tips.append(f"🧐 Your recent expense in **{exp['category']} (₹{exp['amount']})** was significantly higher than average. Recheck if it was necessary.")

        # 4️⃣ General lifestyle & budget tips
        tips.extend([
            "📅 Try maintaining a fixed monthly budget for each category (Food, Travel, Entertainment).",
            "🍽️ Prepare meals at home more often — saves ₹2,000–₹4,000 monthly.",
            "🧾 Use a spending tracker app to monitor expenses daily.",
            "💳 Avoid EMI purchases unless necessary — interest eats into savings.",
            "🛍️ Delay luxury buys using the **24-hour rule** before confirming a purchase.",
            "💡 Automate savings transfers every salary day — treat savings as an expense.",
            "📈 Follow the **50-30-20 rule**: 50% needs, 30% wants, 20% savings.",
            "📊 Review this dashboard weekly to track spending drift.",
            "🏦 Keep 3 months’ expense as emergency savings — ensures stability.",
            "🧠 Use cashback or reward offers smartly — not as excuses to overspend."
        ])
          
        # 🔍 Deep analysis on the highest expense category
        st.markdown("### 🔎 Focus: Highest Expense Category Analysis")

        # Get the top expense category and its amount
        top_cat = category_spending.iloc[0]["category"]
        top_amt = category_spending.iloc[0]["amount"]
        percent = (top_amt / total_spent) * 100

        st.info(f"📈 Your highest expense is **{top_cat}**, which takes up **{percent:.1f}%** of your total spending (₹{top_amt:,.2f}).")

        # AI gives 3 specific action points
        st.markdown("#### 💡 How to Reduce It (3 Practical Steps):")
        st.markdown(f"""
        1️⃣ **Limit it by around 20–30% next month.**  
        &nbsp;&nbsp;&nbsp;&nbsp;→ Example: Set a goal to spend only **₹{top_amt * 0.8:,.0f}** instead of ₹{top_amt:,.0f}.  

        2️⃣ **Track it weekly using your expense log.**  
            &nbsp;&nbsp;&nbsp;&nbsp;→ Divide your budget for {top_cat} into 4 weeks and review progress every Sunday.  
        &nbsp;&nbsp;&nbsp;&nbsp;→ This helps avoid mid-month overshooting.

        3️⃣ **Reduce unnecessary patterns behind it.**  
            &nbsp;&nbsp;&nbsp;&nbsp;→ Find what’s driving this category — habits, lifestyle, or emotional spending.  
        &nbsp;&nbsp;&nbsp;&nbsp;→ Example: If it’s “Food,” cut frequent outside meals; if “Shopping,” set monthly wishlist priorities.
        """)

        # Small motivation banner
        st.success(f"🎯 If you successfully reduce your {top_cat} spending by 25%, you can save **₹{top_amt * 0.25:,.0f}** next month!")

        # Show all AI-generated tips
        for i, tip in enumerate(tips[:15], 1):  # limit to 15 visible tips
            st.markdown(f"{i}. {tip}")

        # 5️⃣ Pie Chart with full legend + clear labels
        st.markdown("### 📊 Spending by Category")

        fig = px.pie(
            category_spending,
            names="category",
            values="amount",
            title="Spending Breakdown by Category",
            hole=0.3,
            color_discrete_sequence=px.colors.qualitative.Safe
        )

        fig.update_traces(
            textinfo="label+percent",
            textfont=dict(color="#000000", size=13),
            pull=[0.03] * len(category_spending)
        )

        fig.update_layout(
            paper_bgcolor="white",
            font=dict(color="#000000", size=14, family="Nunito"),
            legend=dict(
                font=dict(size=13, color="#000000"),
                title_font=dict(size=14, color="#000000"),
                orientation="v",
                yanchor="middle",
                y=0.5,
                xanchor="right",
                x=1.1
            ),
            title_font=dict(size=16, color="#000000", family="Montserrat"),
            margin=dict(t=60, b=60, l=60, r=60)
        )

        st.plotly_chart(fig, use_container_width=True)

        # ------------------------- Teach the App (GlobalTrainer) -------------------------
        # --- Teach the App (Improve AI Accuracy) Header ---
        st.markdown("""
        <div style="
            background: linear-gradient(135deg, #1E3A8A, #3B82F6);
            padding: 18px;
            border-radius: 15px;
            color: white;
            font-family: 'Poppins', sans-serif;
            margin-top: 25px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.25);
        ">
            <h3 style="margin:0; padding:0;">🧠 Teach the App (Improve AI Accuracy)</h3>
            <p style="margin-top:6px;">
                Correct any wrongly detected categories below.<br>
                Your corrections instantly update → Expenses, Reports, Dashboard & AI Memory. ⚡
            </p>
        </div>
        """, unsafe_allow_html=True)


# --- SAFE FILE UPLOADER FIX CSS ---
        st.markdown("""
        <style>
        /* Make file uploader visible in light theme */
        div[data-testid="stFileUploader"] > section {
            background-color: #ffffff !important;
            border: 2px solid #3B82F6 !important;
            border-radius: 10px !important;
            padding: 12px !important;
        }
        div[data-testid="stFileUploader"] button {
            background-color: #3B82F6 !important;
            color: white !important;
            border-radius: 8px !important;
            padding: 8px 14px !important;
            border: none !important;
        }
        </style>
        """, unsafe_allow_html=True)


# --- Load DataFrame ---
        df = st.session_state.expenses.copy().reset_index().rename(columns={'index': 'row'})

        if df.empty:
            st.info("No expense data yet. Add some expenses to train the AI.")
        else:
            df["date"] = pd.to_datetime(df["date"], errors="coerce").dt.strftime("%Y-%m-%d")

            st.dataframe(
                df[['row', 'date', 'amount', 'description', 'category']],
                height=280
            )

    # --- Corrections UI ---
            idx = st.number_input("Select row index to correct",
                                  min_value=0,
                                  max_value=max(0, len(df)-1),
                                  value=0,
                                  step=1)

            new_cat = st.selectbox(
                "Select correct category",
                ['Food', 'Shopping', 'Bills', 'Travel', 'Entertainment',
         'Health', 'Education', 'Groceries', 'Transport', 'Others']
            )
    
            st.markdown("""
            <style>
            /* EXACT SAME AS STREAMLIT "Browse files" BUTTON */
            div.stButton > button {
                background-color: #1A73E8 !important;    /* Same blue */
                color: white !important;
                border: 1px solid #1A73E8 !important;
                padding: 8px 22px !important;
                font-size: 15px !important;
                font-weight: 500 !important;
                border-radius: 6px !important;
                cursor: pointer !important;
                box-shadow: 0px 2px 4px rgba(0,0,0,0.15) !important;
            }

            /* Hover effect (same as browse button) */
            div.stButton > button:hover {
                background-color: #1664D4 !important;
                border-color: #1664D4 !important;
            }

            /* Focus effect */
            div.stButton > button:focus {
                outline: none !important;
                box-shadow: 0 0 0 2px #A7C7F9 !important;
            }
            </style>
            """, unsafe_allow_html=True)

    # --- FIXED BUTTON (visible in light & dark both) ---
            update_btn = st.button("✅ Update Category Globally")

            if update_btn:
                try:
            # Real index in original df
                    real_idx = int(df.loc[idx, 'row'])

            # Key for AI memory
                    desc_key = str(st.session_state.expenses.at[real_idx, 'description']).lower().strip()

            # Update category in main dataset
                    st.session_state.expenses.at[real_idx, 'category'] = new_cat

            # Update AI memory for auto ML categorization
                    st.session_state.memory[desc_key] = new_cat
                   
                    exp_file, inc_file, mem_file = get_user_files()

            # Save changes permanently
                    persist_all()

            # Reload after saving
                    st.session_state.expenses = pd.read_csv(exp_file)
                    st.session_state.expenses["date"] = pd.to_datetime(
                        st.session_state.expenses["date"], errors="coerce"
                    )

                    st.success("✅ Category updated successfully across all sections!")
                except Exception as e:
                    st.error(f"Update failed: {e}")

     

# ------------------------- Final persist to be safe -------------------------
persist_all()

# ------------------------- footer helpful note -------------------------
st.markdown("<hr>", unsafe_allow_html=True)
st.markdown("<div style='text-align:center;color:#6b7280'>Author: <b>SAMARTH MORAIYA</b></div>", unsafe_allow_html=True)
