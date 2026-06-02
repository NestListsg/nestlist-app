import streamlit as st
import anthropic
import os
import bcrypt
import requests
from datetime import datetime
from supabase import create_client, Client

# Page config
st.set_page_config(
    page_title="NestList Prestige — Agent Dashboard",
    page_icon="🏡",
    layout="wide"
)

# Custom CSS — NestList Prestige
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@300;400;500&family=Montserrat:wght@300;400;500&family=Bodoni+Moda:wght@300;400;500&display=swap');

/* ── GLOBAL ── */
html, body, [class*="css"] {
    font-family: 'Montserrat', sans-serif;
}
.stApp { background: #0E2820; }
.main .block-container { padding: 0 !important; max-width: 100% !important; }

/* ── HIDE STREAMLIT CHROME ── */
#MainMenu { visibility: hidden; }
footer { visibility: hidden; }
header { visibility: hidden; }
[data-testid="stToolbar"] { display: none; }

/* ── SIDEBAR ── */
[data-testid="stSidebar"] {
    background: #163D2E !important;
    border-right: 0.5px solid rgba(212,175,55,0.2) !important;
}
[data-testid="stSidebar"] > div { padding: 0 !important; }
[data-testid="stSidebarContent"] { padding: 0 !important; }

/* ── HEADER ── */
.nl-header {
    background: #163D2E;
    padding: 20px 28px;
    border-bottom: 0.5px solid rgba(212,175,55,0.2);
    display: flex;
    justify-content: space-between;
    align-items: center;
}
.nl-brand {
    font-family: 'Cormorant Garamond', serif;
    font-size: 30px;
    font-weight: 300;
    letter-spacing: 0.22em;
    text-transform: uppercase;
    color: #F8F4EC;
    line-height: 1;
}
.nl-brand-gold { color: #D4AF37; }
.nl-prestige-tag {
    font-family: 'Montserrat', sans-serif;
    font-size: 10px;
    color: rgba(212,175,55,0.6);
    margin-left: 14px;
    font-weight: 300;
    letter-spacing: 0.18em;
    vertical-align: middle;
}
.nl-tagline {
    font-size: 9px;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    margin-top: 6px;
    color: rgba(212,175,55,0.45);
}
.nl-avatar {
    width: 36px; height: 36px;
    border-radius: 50%;
    border: 1px solid #D4AF37;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    color: #D4AF37;
    font-size: 11px;
    font-weight: 400;
    letter-spacing: 0.06em;
    margin-right: 10px;
    font-family: 'Montserrat', sans-serif;
}
.nl-agent-name { color: rgba(248,244,236,0.6); font-size: 12px; font-family: 'Montserrat', sans-serif; }

/* ── GOLD ACCENT LINE ── */
.nl-accent {
    height: 1px;
    background: linear-gradient(to right, transparent, #D4AF37, transparent);
    opacity: 0.5;
}

/* ── WELCOME BAR ── */
.nl-welcome {
    background: #163D2E;
    padding: 14px 28px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-bottom: 0.5px solid rgba(0,0,0,0.2);
}
.nl-welcome-text { color: rgba(248,244,236,0.85); font-size: 13px; letter-spacing: 0.03em; font-family: 'Montserrat', sans-serif; }
.nl-welcome-text strong { color: #F8F4EC; font-weight: 500; }
.nl-badge {
    border: 1px solid #D4AF37;
    color: #D4AF37;
    font-size: 9px;
    padding: 5px 14px;
    border-radius: 2px;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    font-family: 'Montserrat', sans-serif;
}

/* ── BODY ── */
.nl-body { background: #F5F1E8; padding: 24px 28px; min-height: 80vh; }
.nl-section-label {
    font-size: 9px;
    font-weight: 400;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    color: rgba(212,175,55,0.7);
    margin-bottom: 16px;
    font-family: 'Montserrat', sans-serif;
}

/* ── STAT CARDS ── */
.nl-card {
    background: white;
    border-radius: 4px;
    padding: 22px 20px 18px;
    border: 0.5px solid rgba(212,175,55,0.3);
    border-top: 2px solid #D4AF37;
    box-shadow: 0 2px 12px rgba(0,0,0,0.06);
    text-align: center;
}
.nl-card-num {
    font-family: 'Cormorant Garamond', serif;
    font-size: 52px;
    font-weight: 300;
    color: #0E2820;
    letter-spacing: -0.02em;
    line-height: 1;
}
.nl-card-label {
    font-size: 9px;
    margin-top: 8px;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: #D4AF37;
    font-family: 'Montserrat', sans-serif;
}

/* ── PANELS ── */
.nl-panel {
    background: white;
    border-radius: 4px;
    padding: 20px;
    border: 0.5px solid rgba(212,175,55,0.2);
    box-shadow: 0 2px 12px rgba(0,0,0,0.06);
}
.nl-panel-title {
    font-size: 10px;
    font-weight: 400;
    letter-spacing: 0.16em;
    text-transform: uppercase;
    color: #0E2820;
    margin-bottom: 14px;
    display: flex;
    align-items: center;
    gap: 8px;
    font-family: 'Montserrat', sans-serif;
}
.nl-panel-title::before {
    content: '';
    display: inline-block;
    width: 16px;
    height: 1.5px;
    background: #D4AF37;
    flex-shrink: 0;
}
.nl-listing-row {
    font-size: 12px;
    color: #2C3E2D;
    padding: 8px 0;
    border-bottom: 0.5px solid rgba(212,175,55,0.15);
    font-family: 'Montserrat', sans-serif;
    letter-spacing: 0.02em;
}
.nl-listing-row:last-child { border-bottom: none; }

/* ── QUICK ACTION BUTTONS ── */
.nl-action-btn {
    display: block;
    width: 100%;
    background: transparent;
    border: 1px solid rgba(14,40,32,0.3);
    color: #0E2820;
    font-family: 'Montserrat', sans-serif;
    font-size: 10px;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    padding: 14px 16px;
    border-radius: 2px;
    text-align: center;
    cursor: pointer;
    margin-bottom: 10px;
}
.nl-action-btn:hover {
    background: #0E2820;
    color: #F8F4EC;
}

/* ── HERO PANEL ── */
.nl-hero {
    border-radius: 4px;
    overflow: hidden;
    position: relative;
    min-height: 380px;
    background: linear-gradient(135deg, #0E2820 0%, #163D2E 100%);
}
.nl-hero-overlay {
    position: absolute;
    bottom: 0; left: 0; right: 0;
    background: linear-gradient(to top, rgba(7,25,16,0.92) 0%, transparent 100%);
    padding: 28px;
}
.nl-hero-title {
    font-family: 'Cormorant Garamond', serif;
    font-size: 28px;
    font-weight: 300;
    color: #F8F4EC;
    line-height: 1.3;
    margin-bottom: 8px;
}
.nl-hero-title span { color: #D4AF37; }
.nl-hero-sub {
    font-size: 9px;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    color: rgba(212,175,55,0.6);
    font-family: 'Montserrat', sans-serif;
}

/* ── MARKET PULSE ── */
.nl-pulse-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 10px 0;
    border-bottom: 0.5px solid rgba(212,175,55,0.12);
    font-family: 'Montserrat', sans-serif;
}
.nl-pulse-row:last-child { border-bottom: none; }
.nl-pulse-label { font-size: 11px; color: rgba(248,244,236,0.6); }
.nl-pulse-value { font-size: 12px; color: #D4AF37; font-weight: 400; letter-spacing: 0.04em; }
.nl-pulse-panel {
    background: #163D2E;
    border-radius: 4px;
    padding: 20px;
    border: 0.5px solid rgba(212,175,55,0.2);
}
.nl-pulse-title {
    font-size: 10px;
    font-weight: 400;
    letter-spacing: 0.16em;
    text-transform: uppercase;
    color: #D4AF37;
    margin-bottom: 14px;
    display: flex;
    align-items: center;
    gap: 8px;
    font-family: 'Montserrat', sans-serif;
}
.nl-pulse-title::before {
    content: '';
    display: inline-block;
    width: 16px;
    height: 1.5px;
    background: #D4AF37;
    flex-shrink: 0;
}
.nl-disclaimer {
    font-size: 9px;
    color: rgba(248,244,236,0.3);
    margin-top: 14px;
    line-height: 1.5;
    font-family: 'Montserrat', sans-serif;
}

/* ── SIDEBAR CONTENT ── */
.nl-sb-logo-area {
    padding: 24px 16px 16px;
    border-bottom: 0.5px solid rgba(212,175,55,0.15);
    margin-bottom: 0;
    text-align: center;
}
.nl-sb-wordmark {
    font-family: 'Cormorant Garamond', serif;
    font-size: 20px;
    font-weight: 300;
    letter-spacing: 0.25em;
    text-transform: uppercase;
    color: #F8F4EC;
    margin-top: 10px;
}
.nl-sb-wordmark span { color: #D4AF37; }
.nl-sb-tagline {
    font-size: 7px;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    color: rgba(212,175,55,0.4);
    margin-top: 4px;
    font-family: 'Montserrat', sans-serif;
}
.nl-sb-agent {
    background: rgba(212,175,55,0.08);
    border-left: 2px solid #D4AF37;
    padding: 10px 12px;
    margin: 16px 12px;
    border-radius: 0 3px 3px 0;
}
.nl-sb-agent-name { color: #F8F4EC; font-size: 13px; font-weight: 400; font-family: 'Montserrat', sans-serif; }
.nl-sb-agent-spec { color: rgba(248,244,236,0.5); font-size: 10px; margin-top: 3px; font-family: 'Montserrat', sans-serif; line-height: 1.4; }
.nl-sb-nav-label {
    font-size: 8px;
    letter-spacing: 0.22em;
    text-transform: uppercase;
    padding: 0 16px;
    margin-bottom: 0px;
    color: rgba(212,175,55,0.3);
    font-family: 'Montserrat', sans-serif;
}
.nl-sb-logout {
    font-size: 12px;
    padding: 10px 24px;
    color: rgba(248,244,236,0.3);
    letter-spacing: 0.04em;
    font-family: 'Montserrat', sans-serif;
    cursor: pointer;
    display: block;
    margin-top: 4px;
}
.nl-sb-logout:hover { color: rgba(248,244,236,0.6); }

/* ── RADIO (nav) ── */
[data-testid="stSidebar"] .stRadio { margin: 0 !important; }
[data-testid="stSidebar"] .stRadio > div { gap: 0 !important; }
[data-testid="stSidebar"] .stRadio > label { display: none !important; }
[data-testid="stSidebar"] .stRadio label {
    font-size: 12px !important;
    color: rgba(248,244,236,0.5) !important;
    letter-spacing: 0.04em !important;
    padding: 10px 16px !important;
    border-radius: 4px !important;
    font-family: 'Montserrat', sans-serif !important;
    font-weight: 300 !important;
    margin: 1px 8px !important;
    cursor: pointer !important;
}
[data-testid="stSidebar"] .stRadio label:has(input:checked) {
    background: rgba(212,175,55,0.1) !important;
    color: #F8F4EC !important;
    border-left: 2px solid #D4AF37 !important;
    padding-left: 14px !important;
}
[data-testid="stSidebar"] .stRadio [data-testid="stMarkdownContainer"] p {
    font-size: 12px !important;
    font-family: 'Montserrat', sans-serif !important;
    letter-spacing: 0.04em !important;
}

/* ── FORMS / INPUTS ── */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea,
.stSelectbox > div > div {
    border: 0.5px solid rgba(212,175,55,0.4) !important;
    border-radius: 3px !important;
    background: #FDFAF5 !important;
    font-family: 'Montserrat', sans-serif !important;
    color: #0E2820 !important;
}

/* ── BUTTONS ── */
.stButton > button {
    background: transparent !important;
    border: 1px solid #0E2820 !important;
    color: #0E2820 !important;
    border-radius: 2px !important;
    font-size: 10px !important;
    letter-spacing: 0.1em !important;
    text-transform: uppercase !important;
    font-weight: 400 !important;
    padding: 10px 16px !important;
    font-family: 'Montserrat', sans-serif !important;
}
.stButton > button:hover {
    background: #0E2820 !important;
    color: #F8F4EC !important;
}

/* ── SUCCESS/ERROR ── */
.stSuccess { border-left: 3px solid #D4AF37 !important; background: rgba(212,175,55,0.08) !important; }
.stError { border-left: 3px solid #8B2020 !important; }

/* ── EXPANDER ── */
.streamlit-expanderHeader {
    background: white !important;
    border: 0.5px solid rgba(212,175,55,0.2) !important;
    border-radius: 4px !important;
    color: #0E2820 !important;
    font-family: 'Montserrat', sans-serif !important;
    font-size: 12px !important;
}
</style>
""", unsafe_allow_html=True)

# ================================
# SUPABASE CONNECTION
# ================================
SUPABASE_URL = os.environ.get("SUPABASE_URL", "https://osxxngwryyairxbjqixr.supabase.co")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "")

@st.cache_resource
def get_supabase():
    return create_client(SUPABASE_URL, SUPABASE_KEY)

supabase = get_supabase()

# ================================
# HELPER FUNCTIONS
# ================================
def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password, hashed):
    try:
        if hashed.startswith('$2b$') or hashed.startswith('$2a$'):
            return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
        else:
            return password == hashed
    except Exception:
        return False

def login_agent(email, password):
    try:
        result = supabase.table("agents").select("*").eq("email", email).execute()
        if result.data:
            agent = result.data[0]
            if verify_password(password, agent["password_hash"]):
                if not (agent["password_hash"].startswith('$2b$') or agent["password_hash"].startswith('$2a$')):
                    new_hash = hash_password(password)
                    supabase.table("agents").update({"password_hash": new_hash}).eq("id", agent["id"]).execute()
                    agent["password_hash"] = new_hash
                return agent
        return None
    except Exception as e:
        st.error(f"DB Error: {str(e)}")
        return None

def register_agent(email, password, name, agency, specialty):
    try:
        result = supabase.table("agents").insert({
            "email": email,
            "password_hash": hash_password(password),
            "name": name,
            "agency": agency,
            "specialty": specialty
        }).execute()
        return result.data[0] if result.data else None
    except Exception as e:
        st.error(f"Registration Error: {str(e)}")
        return None

def get_agent_listings(agent_id):
    try:
        result = supabase.table("listings").select("*").eq("agent_id", agent_id).order("created_at", desc=True).execute()
        return result.data or []
    except:
        return []

def save_listing(agent_id, location, price, property_type, content):
    try:
        supabase.table("listings").insert({
            "agent_id": agent_id,
            "location": location,
            "price": price,
            "property_type": property_type,
            "content": content
        }).execute()
        return True
    except:
        return False

def update_agent_profile(agent_id, profile_data):
    try:
        supabase.table("agents").update(profile_data).eq("id", agent_id).execute()
        return True
    except:
        return False

def post_to_facebook(listing_text, location, price):
    try:
        fb_token = os.environ.get("FB_PAGE_ACCESS_TOKEN", "")
        fb_page_id = os.environ.get("FB_PAGE_ID", "")
        if not fb_token or not fb_page_id:
            return False, "Facebook credentials not configured."
        message = f"🏡 New Listing — {location}\n💰 SGD {price}\n\n{listing_text[:800]}...\n\n#NestListPrestige #SingaporeProperty #LuxuryRealEstate #GCB #LandedProperty"
        url = f"https://graph.facebook.com/v25.0/{fb_page_id}/feed"
        response = requests.post(url, data={"message": message, "access_token": fb_token})
        if response.status_code == 200:
            return True, "Posted to Facebook successfully!"
        else:
            return False, f"Facebook error: {response.text}"
    except Exception as e:
        return False, str(e)

# ================================
# LOGIN / REGISTER PAGE
# ================================
if "agent" not in st.session_state:
    st.session_state.agent = None

if st.session_state.agent is None:
    col_l, col_m, col_r = st.columns([1, 1.2, 1])
    with col_m:
        st.markdown("""
        <div style="text-align:center; padding:32px 0 24px;">
            <div style="font-family:'Cormorant Garamond',serif; font-size:34px; font-weight:300; letter-spacing:0.22em; color:#F8F4EC;">
                NEST<span style="color:#D4AF37;">LIST</span>
            </div>
            <div style="font-size:9px; letter-spacing:0.2em; text-transform:uppercase; color:rgba(212,175,55,0.5); margin-top:6px; font-family:'Montserrat',sans-serif;">
                Prestige · Singapore's AI-Powered Property Platform
            </div>
        </div>
        """, unsafe_allow_html=True)

        tab1, tab2 = st.tabs(["Login", "Register"])

        with tab1:
            email = st.text_input("Email", key="login_email")
            password = st.text_input("Password", type="password", key="login_password")
            if st.button("Login", use_container_width=True, key="login_btn"):
                if email and password:
                    agent = login_agent(email, password)
                    if agent:
                        st.session_state.agent = agent
                        st.rerun()
                    else:
                        st.error("Invalid email or password.")
                else:
                    st.error("Please enter email and password.")

        with tab2:
            reg_name = st.text_input("Full Name", key="reg_name")
            reg_email = st.text_input("Email", key="reg_email")
            reg_agency = st.text_input("Agency", key="reg_agency")
            reg_specialty = st.selectbox("Specialty", [
                "Landed & GCB Properties",
                "Luxury Condominiums",
                "HDB Resale",
                "Commercial Properties",
                "Industrial Properties",
                "Residential (All Types)"
            ], key="reg_specialty")
            reg_password = st.text_input("Password", type="password", key="reg_password")
            reg_password2 = st.text_input("Confirm Password", type="password", key="reg_password2")

            if st.button("Create Account", use_container_width=True, key="reg_btn"):
                if not all([reg_name, reg_email, reg_agency, reg_password]):
                    st.error("Please fill in all fields.")
                elif reg_password != reg_password2:
                    st.error("Passwords do not match.")
                elif len(reg_password) < 6:
                    st.error("Password must be at least 6 characters.")
                else:
                    agent = register_agent(reg_email, reg_password, reg_name, reg_agency, reg_specialty)
                    if agent:
                        st.session_state.agent = agent
                        st.success("Account created! Welcome to NestList Prestige!")
                        st.rerun()
                    else:
                        st.error("Email already registered or error occurred.")

    st.stop()

# ================================
# MAIN APP (LOGGED IN)
# ================================
agent = st.session_state.agent
initials = ''.join([n[0] for n in agent['name'].split()[:2]]).upper()

# ── HEADER ──
st.markdown(f"""
<div class="nl-header">
    <div>
        <div class="nl-brand">NEST<span class="nl-brand-gold">LIST</span><span class="nl-prestige-tag">PRESTIGE</span></div>
        <div class="nl-tagline">Singapore's AI-Powered Property Platform</div>
    </div>
    <div style="display:flex; align-items:center;">
        <div class="nl-avatar">{initials}</div>
        <div class="nl-agent-name">{agent['name']}</div>
    </div>
</div>
<div class="nl-accent"></div>
<div class="nl-welcome">
    <div class="nl-welcome-text">Welcome back, <strong>{agent['name']}</strong> &nbsp;·&nbsp; {agent['specialty']}</div>
    <div class="nl-badge">Prestige</div>
</div>
""", unsafe_allow_html=True)

# ── SIDEBAR ──
st.sidebar.markdown(f"""
<div class="nl-sb-logo-area">
    <div style="font-size:48px; line-height:1;">🧭</div>
    <div class="nl-sb-wordmark">NEST<span>LIST</span></div>
    <div class="nl-sb-tagline">Smarter Listings. Better Results.</div>
</div>
<div class="nl-sb-agent">
    <div class="nl-sb-agent-name">{agent['name']}</div>
    <div class="nl-sb-agent-spec">{agent['specialty']}</div>
</div>
<div class="nl-sb-nav-label">Navigation</div>
""", unsafe_allow_html=True)

page = st.sidebar.radio(
    "Navigation",
    ["Dashboard", "New Listing", "My Listings", "Enquiries", "My Profile", "Billing"],
    label_visibility="collapsed"
)

st.sidebar.markdown("<div style='height:20px;'></div>", unsafe_allow_html=True)
st.sidebar.markdown("""
<style>
div[data-testid="stSidebar"] .stButton#logout_btn > button {
    background: transparent !important;
    border: none !important;
    color: rgba(248,244,236,0.35) !important;
    font-family: 'Montserrat', sans-serif !important;
    font-size: 12px !important;
    font-weight: 300 !important;
    letter-spacing: 0.04em !important;
    text-transform: none !important;
    padding: 8px 16px !important;
    text-align: left !important;
    width: auto !important;
    box-shadow: none !important;
}
div[data-testid="stSidebar"] .stButton#logout_btn > button:hover {
    color: rgba(248,244,236,0.6) !important;
    background: transparent !important;
}
</style>
""", unsafe_allow_html=True)
if st.sidebar.button("Logout", key="logout_btn"):
    st.session_state.agent = None
    st.rerun()

# ================================
# DASHBOARD PAGE
# ================================
if page == "Dashboard":

    listings = get_agent_listings(agent['id'])
    total_listings = len(listings)

    st.markdown(f"""
    <div class="nl-body">
        <div class="nl-section-label">Dashboard Overview</div>
        <div style="display:grid; grid-template-columns:repeat(4,1fr); gap:16px; margin-bottom:24px;">
            <div class="nl-card"><div class="nl-card-num">{total_listings}</div><div class="nl-card-label">Active Listings</div></div>
            <div class="nl-card"><div class="nl-card-num">0</div><div class="nl-card-label">Total Enquiries</div></div>
            <div class="nl-card"><div class="nl-card-num">0</div><div class="nl-card-label">Total Views</div></div>
            <div class="nl-card"><div class="nl-card-num">0</div><div class="nl-card-label">Serious Buyers</div></div>
        </div>
        <div style="display:grid; grid-template-columns:1fr 1fr; gap:16px; margin-bottom:24px;">
            <div class="nl-panel">
                <div class="nl-panel-title">Recent Listings</div>
                {"".join([f'<div class="nl-listing-row">{l["location"]} &mdash; SGD {l["price"]}</div>' for l in listings[:3]]) if listings else '<div style="color:rgba(14,40,32,0.4); font-size:12px; font-family:Montserrat,sans-serif;">No listings yet. Create your first one!</div>'}
            </div>
            <div class="nl-panel">
                <div class="nl-panel-title">Quick Actions</div>
                <div style="margin-top:8px;">
                    <div class="nl-action-btn">Create New Listing</div>
                    <div class="nl-action-btn">Update My Profile</div>
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Hero + Market Pulse
    col_hero, col_pulse = st.columns([1, 1])

    with col_hero:
        st.markdown("""
        <div class="nl-hero" style="background-image:url('https://images.unsplash.com/photo-1613977257363-707ba9348227?w=800&q=80'); background-size:cover; background-position:center;">
            <div class="nl-hero-overlay">
                <div class="nl-hero-title">Where Singapore's Finest<br>Properties Find Their <span>Buyers</span></div>
                <div class="nl-hero-sub">NestList Prestige &nbsp;·&nbsp; Est. 2026</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col_pulse:
        st.markdown("""
        <div class="nl-pulse-panel">
            <div class="nl-pulse-title">Singapore Market Pulse</div>
            <div class="nl-pulse-row">
                <span class="nl-pulse-label">GCB Transactions 2025</span>
                <span class="nl-pulse-value">~36 units</span>
            </div>
            <div class="nl-pulse-row">
                <span class="nl-pulse-label">Total GCB Value 2025</span>
                <span class="nl-pulse-value">SGD 1.36B</span>
            </div>
            <div class="nl-pulse-row">
                <span class="nl-pulse-label">Avg. GCB Price psf 2025</span>
                <span class="nl-pulse-value">SGD 2,134</span>
            </div>
            <div class="nl-pulse-row">
                <span class="nl-pulse-label">Largest 2025 Transaction</span>
                <span class="nl-pulse-value">SGD 148M</span>
            </div>
            <div class="nl-pulse-row">
                <span class="nl-pulse-label">Nassim Road Price Range</span>
                <span class="nl-pulse-value">SGD 2,500–4,000 psf</span>
            </div>
            <div class="nl-disclaimer">
                ⓘ Disclaimer: Data sourced from URA Realis & EdgeProp Singapore. Figures are indicative and updated periodically. NestList does not warrant the accuracy of market data. Always verify with URA or a licensed professional before making property decisions.<br>
                <span style="opacity:0.5;">Source: URA Realis / EdgeProp &nbsp;|&nbsp; Last updated: Jan 2026 &nbsp;|&nbsp; Live URA API integration coming soon</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

# ================================
# NEW LISTING PAGE
# ================================
elif page == "New Listing":
    st.markdown("<div class='nl-body'>", unsafe_allow_html=True)
    st.markdown("<div class='nl-section-label'>New Listing</div>", unsafe_allow_html=True)

    with st.form("new_listing_form"):
        col1, col2 = st.columns(2)
        with col1:
            property_type = st.selectbox("1. Property Type", [
                "Good Class Bungalow (GCB)", "Landed Bungalow",
                "Semi-Detached", "Terrace House", "HDB Flat", "Condominium"
            ])
            location = st.text_input("2. Location", placeholder="e.g. Nassim Road, District 10")
            land_size = st.number_input("3. Land Size (sqft)", min_value=0, value=0)
            plot_width = st.number_input("4. Plot Width (metres)", min_value=0.0, value=0.0)
            plot_depth = st.number_input("5. Plot Depth (metres)", min_value=0.0, value=0.0)
        with col2:
            built_up = st.number_input("6. Built-up Size (sqft)", min_value=0, value=0)
            bedrooms = st.text_input("7. Bedrooms & Bathrooms", placeholder="e.g. 4 bedrooms, 4 bathrooms")
            price = st.text_input("8. Asking Price (SGD)", placeholder="e.g. 25,700,000")
            storeys = st.number_input("9. Number of Storeys", min_value=0, max_value=10, value=0)
            site_coverage = st.number_input("10. Site Coverage (%)", min_value=0.0, max_value=100.0, value=0.0)

        features = st.text_area("Special Features", placeholder="e.g. Private pool, 3-car garage, newly renovated")
        sg_citizen = st.checkbox("I confirm the buyer is a Singapore Citizen (required for GCB purchases)")
        declaration = st.checkbox("I confirm all details are accurate and truthful.")
        submitted = st.form_submit_button("Generate My Listing with Claude AI", use_container_width=True)

    if submitted:
        if not declaration:
            st.error("Please tick the declaration box before submitting.")
        elif not location or not bedrooms or not price:
            st.error("Please fill in all required fields.")
        else:
            st.markdown("---")
            st.subheader("Step 1 — URA Compliance Check")

            gcb_zones = [
                "nassim", "cluny", "white house park", "dalvey", "ladyhill",
                "cornwall", "king albert park", "raffles park", "swiss club",
                "victoria park", "holland", "bin tong park", "leedon",
                "maryland", "bishopsgate", "fourth avenue", "grange", "jervois",
                "rochalie", "linden", "chee hoon", "swettenham", "tanglin",
                "chestnut", "sunset", "upper bukit timah", "rifle range",
                "spring grove", "belmont", "windsor"
            ]

            issues = []
            warnings = []
            passed = []
            is_gcb = "gcb" in property_type.lower() or "bungalow" in property_type.lower()

            if is_gcb:
                location_lower = location.lower()
                in_zone = any(z in location_lower for z in gcb_zones)
                if in_zone:
                    passed.append("Location confirmed within gazetted GCBa zone")
                else:
                    warnings.append("Location could not be verified as GCBa zone — please confirm with URA.")

                if land_size >= 15069:
                    passed.append(f"Land size {land_size:,} sqft meets URA minimum of 15,069 sqft")
                elif land_size >= 14000:
                    warnings.append(f"Land size {land_size:,} sqft is slightly below URA minimum — please verify.")
                elif land_size > 0:
                    issues.append(f"Land size {land_size:,} sqft does not meet GCB minimum of 15,069 sqft")

                if plot_width >= 18.5:
                    passed.append(f"Plot width {plot_width}m meets URA minimum of 18.5m")
                elif plot_width > 0:
                    issues.append(f"Plot width {plot_width}m does not meet URA minimum of 18.5m")

                if plot_depth >= 30:
                    passed.append(f"Plot depth {plot_depth}m meets URA minimum of 30m")
                elif plot_depth > 0:
                    issues.append(f"Plot depth {plot_depth}m does not meet URA minimum of 30m")

                if site_coverage > 0:
                    if site_coverage <= 40:
                        passed.append(f"Site coverage {site_coverage}% is within URA maximum of 40%")
                    else:
                        issues.append(f"Site coverage {site_coverage}% exceeds URA maximum of 40%")

                if storeys > 0:
                    if storeys <= 2:
                        passed.append(f"{storeys} storey(s) meets URA maximum height of 2 storeys")
                    else:
                        issues.append(f"{storeys} storeys exceeds URA maximum of 2 storeys for GCB")

                if not sg_citizen:
                    issues.append("GCB purchases are restricted to Singapore Citizens only")
                else:
                    passed.append("Buyer confirmed as Singapore Citizen — eligible for GCB purchase")

            for p in passed:
                st.success(f"✅ {p}")
            for w in warnings:
                st.warning(f"⚠️ {w}")
            for i in issues:
                st.error(f"❌ {i}")

            if not issues:
                st.markdown("---")
                st.subheader("Step 2 — Claude is writing your listing...")

                prompt = f"""
You are {agent['name']} from {agent['agency']},
a specialist in {agent['specialty']}.
Your tone: {agent['tone']}
You emphasise: {agent['emphasis']}
Your signature phrase: "{agent['signature']}"
Weave this phrase in naturally.

Write a premium property listing for:
- Type: {property_type}
- Location: {location}
- Land size: {land_size:,} sqft
- Built-up: {built_up:,} sqft
- Bedrooms: {bedrooms}
- Price: SGD {price}
- Features: {features}

Write:
1. A compelling headline in your style
2. Three paragraphs in your personal voice
3. A warm call to action
4. End with: {agent['name']} | {agent['agency']} Specialist
"""
                try:
                    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
                    claude_client = anthropic.Anthropic(api_key=api_key)

                    with st.spinner("Claude is writing your personalised listing..."):
                        response = claude_client.messages.create(
                            model="claude-sonnet-4-5",
                            max_tokens=1024,
                            messages=[{"role": "user", "content": prompt}]
                        )

                    listing_text = response.content[0].text
                    save_listing(agent['id'], location, price, property_type, listing_text)

                    st.markdown("---")
                    st.subheader("Step 3 — Your Listing is Ready!")
                    st.markdown(listing_text)
                    st.success("✅ Listing saved to My Listings!")

                    st.markdown("---")
                    if st.button("Post to Facebook", key="fb_post_new"):
                        success, msg = post_to_facebook(listing_text, location, price)
                        if success:
                            st.success(msg)
                        else:
                            st.error(msg)

                except Exception as e:
                    st.error(f"Error generating listing: {str(e)}")

    st.markdown("</div>", unsafe_allow_html=True)

# ================================
# MY LISTINGS PAGE
# ================================
elif page == "My Listings":
    st.markdown("<div class='nl-body'>", unsafe_allow_html=True)
    st.markdown("<div class='nl-section-label'>My Listings</div>", unsafe_allow_html=True)

    listings = get_agent_listings(agent['id'])

    if listings:
        st.write(f"You have {len(listings)} listing(s).")
        st.markdown("---")
        for i, listing in enumerate(listings):
            with st.expander(f"{listing['location']} — SGD {listing['price']} | {listing['created_at'][:10]}"):
                st.markdown(listing["content"])
                if st.button("Post to Facebook", key=f"fb_{i}"):
                    success, msg = post_to_facebook(listing["content"], listing["location"], listing["price"])
                    if success:
                        st.success(msg)
                    else:
                        st.error(msg)
    else:
        st.info("No listings yet! Go to 'New Listing' to create your first one.")

    st.markdown("</div>", unsafe_allow_html=True)

# ================================
# ENQUIRIES PAGE
# ================================
elif page == "Enquiries":
    st.markdown("<div class='nl-body'>", unsafe_allow_html=True)
    st.markdown("<div class='nl-section-label'>Buyer Enquiries</div>", unsafe_allow_html=True)
    st.info("Coming in Week 3 — buyer enquiries and AI auto-replies will appear here!")
    st.markdown("</div>", unsafe_allow_html=True)

# ================================
# MY PROFILE PAGE
# ================================
elif page == "My Profile":
    st.markdown("<div class='nl-body'>", unsafe_allow_html=True)
    st.markdown("<div class='nl-section-label'>My Profile & Style Settings</div>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input("Full Name", value=agent["name"])
        agency = st.text_input("Agency", value=agent["agency"])
    with col2:
        specialty = st.text_input("Specialty", value=agent["specialty"])
        contact = st.text_input("Contact", value=agent.get("contact", ""))

    st.markdown("---")
    st.subheader("My Writing Style")

    tone_options = ["Warm & Conversational", "Formal & Professional", "Bold & Punchy"]
    tone = st.selectbox("Writing Tone", tone_options,
        index=tone_options.index(agent["tone"]) if agent["tone"] in tone_options else 0)

    emphasis_options = [
        "Family Living & Emotional Comfort",
        "Investment Returns & Capital Appreciation",
        "Lifestyle & Prestige",
        "Architecture & Design"
    ]
    emphasis = st.selectbox("What I Emphasise", emphasis_options,
        index=emphasis_options.index(agent["emphasis"]) if agent["emphasis"] in emphasis_options else 0)

    signature = st.text_area("My Signature Phrase", value=agent["signature"], height=100)

    st.markdown("---")
    if st.button("Save My Style Settings", use_container_width=True):
        profile_data = {
            "name": name, "agency": agency, "specialty": specialty,
            "tone": tone, "emphasis": emphasis, "signature": signature, "contact": contact
        }
        if update_agent_profile(agent['id'], profile_data):
            st.session_state.agent.update(profile_data)
            st.success("✅ Profile saved!")
            st.balloons()
        else:
            st.error("Error saving profile.")

    st.markdown("</div>", unsafe_allow_html=True)

# ================================
# BILLING PAGE
# ================================
elif page == "Billing":
    st.markdown("<div class='nl-body'>", unsafe_allow_html=True)
    st.markdown("<div class='nl-section-label'>Billing & Subscription</div>", unsafe_allow_html=True)
    st.markdown("""
    <div style="background:rgba(212,175,55,0.08); border:0.5px solid rgba(212,175,55,0.3); border-radius:4px; padding:20px; margin-bottom:16px;">
        <div style="font-family:'Cormorant Garamond',serif; font-size:22px; color:#0E2820; font-weight:300;">NestList Prestige</div>
        <div style="font-size:12px; color:#D4AF37; margin-top:4px; font-family:'Montserrat',sans-serif;">SGD 149 / month</div>
    </div>
    """, unsafe_allow_html=True)
    st.info("Stripe payment integration coming soon!")
    st.markdown("</div>", unsafe_allow_html=True)
