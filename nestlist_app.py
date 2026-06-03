# ============================================================
# NESTLIST PRESTIGE — nestlist_app.py  |  Clean Build June 2026
# ============================================================

import streamlit as st
import anthropic
import os
import bcrypt
import requests
from supabase import create_client, Client
from datetime import datetime

# ============================================================
# PAGE CONFIG — must be first Streamlit call
# ============================================================
st.set_page_config(
    page_title="NestList Prestige",
    page_icon="🏡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# ENVIRONMENT VARIABLES
# ============================================================
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
SUPABASE_URL      = os.environ.get("SUPABASE_URL", "")
SUPABASE_KEY      = os.environ.get("SUPABASE_KEY", "")
FB_PAGE_TOKEN     = os.environ.get("FB_PAGE_ACCESS_TOKEN", "")
FB_PAGE_ID        = os.environ.get("FB_PAGE_ID", "")

# ============================================================
# CLIENTS
# ============================================================
@st.cache_resource
def get_supabase():
    return create_client(SUPABASE_URL, SUPABASE_KEY)

@st.cache_resource
def get_anthropic_client():
    return anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

supabase = get_supabase()
claude   = get_anthropic_client()

# ============================================================
# LOGO — Compass Rose, base64 embedded (no external URL)
# ============================================================
LOGO_B64 = "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"
LOGO_URI = f"data:image/jpeg;base64,{LOGO_B64}"

# ============================================================
# CSS — Tropical Modern Elevated / NestList Prestige
# ============================================================
def inject_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@400;600;700&family=Montserrat:wght@300;400;500;600&display=swap');

    /* ---- Hide Streamlit chrome ---- */
    #MainMenu, footer, header { visibility: hidden; }
    .stDeployButton { display: none; }
    [data-testid="stToolbar"] { display: none; }

    /* ---- Base ---- */
    html, body, [data-testid="stAppViewContainer"] {
        background-color: #0a1f14;
        color: #f0ebe3;
        font-family: 'Montserrat', sans-serif;
    }

    /* ---- Sidebar ---- */
    [data-testid="stSidebar"] {
        background-color: #071910 !important;
        border-right: 2px solid #D4AF37 !important;
        padding-top: 0 !important;
    }
    [data-testid="stSidebar"] > div:first-child {
        padding-top: 1rem;
    }

    /* ---- Sidebar text ---- */
    [data-testid="stSidebar"] * {
        color: #e8e0d0 !important;
        font-family: 'Montserrat', sans-serif !important;
    }

    /* ---- Nav radio — hide dots, style labels ---- */
    [data-testid="stSidebar"] .stRadio > label {
        display: none;
    }
    [data-testid="stSidebar"] .stRadio div[role="radiogroup"] {
        gap: 0 !important;
    }
    [data-testid="stSidebar"] .stRadio label {
        display: flex !important;
        padding: 0.6rem 1.2rem !important;
        cursor: pointer;
        border-left: 3px solid transparent;
        transition: all 0.2s;
        font-size: 0.85rem;
        letter-spacing: 0.08em;
        text-transform: uppercase;
    }
    [data-testid="stSidebar"] .stRadio label:hover {
        border-left-color: #D4AF37;
        background: rgba(212,175,55,0.08);
    }
    [data-testid="stSidebar"] .stRadio label[data-baseweb="radio"] input:checked + div {
        border-left-color: #D4AF37 !important;
    }
    /* Hide radio circle */
    [data-testid="stSidebar"] .stRadio label div:first-child {
        display: none !important;
    }

    /* ---- Header bar ---- */
    .nestlist-header {
        background: #071910;
        border-bottom: 2px solid #D4AF37;
        padding: 1rem 2rem 0.8rem 2rem;
        margin: -1rem -1rem 1.5rem -1rem;
    }
    .nestlist-header h1 {
        font-family: 'Cormorant Garamond', serif;
        font-size: 1.6rem;
        font-weight: 600;
        color: #D4AF37;
        letter-spacing: 0.15em;
        margin: 0;
    }
    .nestlist-header p {
        font-size: 0.75rem;
        color: #8a9e8f;
        letter-spacing: 0.1em;
        text-transform: uppercase;
        margin: 0.2rem 0 0 0;
    }

    /* ---- Welcome bar ---- */
    .welcome-bar {
        background: #0f2d1f;
        border: 1px solid rgba(212,175,55,0.3);
        border-radius: 4px;
        padding: 0.8rem 1.2rem;
        margin-bottom: 1.5rem;
        font-size: 0.9rem;
        color: #c8c0b0;
    }
    .welcome-bar span {
        color: #D4AF37;
        font-weight: 600;
    }

    /* ---- Stat cards ---- */
    .stat-row { display: flex; gap: 1rem; margin-bottom: 1.5rem; }
    .stat-card {
        flex: 1;
        background: #0f2d1f;
        border: 1px solid rgba(212,175,55,0.25);
        border-top: 3px solid #D4AF37;
        border-radius: 4px;
        padding: 1.2rem 1.4rem;
        text-align: center;
    }
    .stat-number {
        font-family: 'Cormorant Garamond', serif;
        font-size: 3rem;
        font-weight: 700;
        color: #D4AF37;
        line-height: 1;
        margin-bottom: 0.3rem;
    }
    .stat-label {
        font-size: 0.7rem;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        color: #8a9e8f;
    }

    /* ---- Panel cards ---- */
    .panel-card {
        background: #0f2d1f;
        border: 1px solid rgba(212,175,55,0.2);
        border-radius: 4px;
        padding: 1.4rem;
        margin-bottom: 1.2rem;
    }
    .panel-title {
        font-family: 'Cormorant Garamond', serif;
        font-size: 1rem;
        font-weight: 600;
        color: #D4AF37;
        letter-spacing: 0.1em;
        text-transform: uppercase;
        margin-bottom: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 1px solid rgba(212,175,55,0.2);
    }

    /* ---- Hero image panel ---- */
    .hero-panel {
        width: 100%;
        min-height: 380px;
        background: linear-gradient(135deg, #071910 0%, #0f2d1f 100%);
        border: 1px solid rgba(212,175,55,0.3);
        border-radius: 4px;
        display: flex;
        align-items: flex-end;
        padding: 2rem;
        margin-bottom: 1.2rem;
        position: relative;
        overflow: hidden;
    }
    .hero-overlay {
        background: linear-gradient(to top, rgba(7,25,16,0.95) 0%, transparent 60%);
        position: absolute; inset: 0;
    }
    .hero-text { position: relative; z-index: 2; }
    .hero-text h2 {
        font-family: 'Cormorant Garamond', serif;
        font-size: 1.8rem;
        color: #f0ebe3;
        margin: 0 0 0.3rem 0;
    }
    .hero-text p {
        font-size: 0.8rem;
        color: #D4AF37;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        margin: 0;
    }

    /* ---- Market Pulse ---- */
    .pulse-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 0.8rem; }
    .pulse-item { text-align: center; padding: 0.6rem; }
    .pulse-value {
        font-family: 'Cormorant Garamond', serif;
        font-size: 1.4rem;
        color: #D4AF37;
        font-weight: 600;
    }
    .pulse-desc { font-size: 0.7rem; color: #8a9e8f; text-transform: uppercase; letter-spacing: 0.08em; }
    .pulse-disclaimer {
        font-size: 0.65rem;
        color: #5a6e5f;
        margin-top: 1rem;
        font-style: italic;
        border-top: 1px solid rgba(212,175,55,0.1);
        padding-top: 0.6rem;
    }

    /* ---- Buttons ---- */
    .stButton > button {
        background: transparent;
        border: 1px solid #D4AF37;
        color: #D4AF37;
        font-family: 'Montserrat', sans-serif;
        font-size: 0.75rem;
        letter-spacing: 0.1em;
        text-transform: uppercase;
        padding: 0.6rem 1.4rem;
        border-radius: 2px;
        transition: all 0.2s;
    }
    .stButton > button:hover {
        background: #D4AF37;
        color: #071910;
    }

    /* ---- Gold primary button ---- */
    .stButton > button[kind="primary"] {
        background: #D4AF37;
        color: #071910;
        font-weight: 600;
    }

    /* ---- Form fields ---- */
    .stTextInput input, .stTextArea textarea, .stSelectbox select {
        background: #0a1f14 !important;
        border: 1px solid rgba(212,175,55,0.3) !important;
        color: #f0ebe3 !important;
        border-radius: 2px !important;
    }
    .stTextInput input:focus, .stTextArea textarea:focus {
        border-color: #D4AF37 !important;
        box-shadow: 0 0 0 1px #D4AF37 !important;
    }

    /* ---- Listing card ---- */
    .listing-card {
        background: #0f2d1f;
        border: 1px solid rgba(212,175,55,0.2);
        border-left: 3px solid #D4AF37;
        border-radius: 4px;
        padding: 1.2rem;
        margin-bottom: 0.8rem;
    }
    .listing-card h4 {
        color: #D4AF37;
        font-family: 'Cormorant Garamond', serif;
        margin: 0 0 0.3rem 0;
        font-size: 1rem;
    }
    .listing-card p { font-size: 0.82rem; color: #c8c0b0; margin: 0; }

    /* ---- Compliance badges ---- */
    .badge-pass {
        background: rgba(34,139,34,0.2);
        border: 1px solid #228b22;
        color: #90ee90;
        padding: 0.2rem 0.6rem;
        border-radius: 2px;
        font-size: 0.7rem;
        letter-spacing: 0.08em;
    }
    .badge-fail {
        background: rgba(178,34,34,0.2);
        border: 1px solid #b22222;
        color: #ff6b6b;
        padding: 0.2rem 0.6rem;
        border-radius: 2px;
        font-size: 0.7rem;
    }

    /* ---- Divider ---- */
    hr { border-color: rgba(212,175,55,0.2); }

    /* ---- Logout link ---- */
    .logout-link {
        font-size: 0.72rem;
        color: #5a6e5f;
        text-decoration: none;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        cursor: pointer;
    }
    .logout-link:hover { color: #D4AF37; }
    </style>
    """, unsafe_allow_html=True)

# ============================================================
# PASSWORD UTILITIES
# ============================================================
def verify_password(plain: str, stored: str) -> bool:
    """Handles both bcrypt hashes and legacy plain text."""
    try:
        stored_bytes = stored.encode("utf-8") if isinstance(stored, str) else stored
        return bcrypt.checkpw(plain.encode("utf-8"), stored_bytes)
    except Exception:
        # Legacy plain text fallback
        return plain == stored

def hash_password(plain: str) -> str:
    return bcrypt.hashpw(plain.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

# ============================================================
# SUPABASE HELPERS
# ============================================================
def get_agent_by_email(email: str):
    try:
        res = supabase.table("agents").select("*").eq("email", email).execute()
        return res.data[0] if res.data else None
    except Exception as e:
        st.error(f"Database error: {e}")
        return None

def get_listings_for_agent(agent_id: str):
    try:
        res = (supabase.table("listings")
               .select("*")
               .eq("agent_id", agent_id)
               .order("created_at", desc=True)
               .limit(20)
               .execute())
        return res.data or []
    except Exception:
        return []

def save_listing(agent_id: str, title: str, content: str, property_type: str, location: str, price: str):
    try:
        supabase.table("listings").insert({
            "agent_id": agent_id,
            "title": title,
            "content": content,
            "property_type": property_type,
            "location": location,
            "price": price,
            "created_at": datetime.utcnow().isoformat()
        }).execute()
        return True
    except Exception as e:
        st.error(f"Save error: {e}")
        return False

def update_agent_profile(agent_id: str, fields: dict):
    try:
        supabase.table("agents").update(fields).eq("id", agent_id).execute()
        return True
    except Exception as e:
        st.error(f"Profile update error: {e}")
        return False

# ============================================================
# FACEBOOK POSTING
# ============================================================
def post_to_facebook(message: str) -> dict:
    if not FB_PAGE_TOKEN or not FB_PAGE_ID:
        return {"error": "Facebook credentials not configured"}
    try:
        url = f"https://graph.facebook.com/v25.0/{FB_PAGE_ID}/feed"
        payload = {
            "message": message + "\n\n#NestListPrestige #SingaporeProperty #GCB #LuxuryRealEstate",
            "access_token": FB_PAGE_TOKEN
        }
        r = requests.post(url, data=payload, timeout=15)
        return r.json()
    except Exception as e:
        return {"error": str(e)}

# ============================================================
# URA GCB COMPLIANCE CHECKER
# ============================================================
GCB_ZONES = [
    "nassim", "white house", "cluny", "dalvey", "swiss club", "oei tiong ham",
    "victoria park", "maryland", "queen astrid", "jesselton", "binjai",
    "coronation", "fordham", "king albert", "clementi", "greenwood",
    "raffles park", "first avenue", "sixth avenue", "watten", "garlick",
    "olive road", "yarwood", "leedon", "cornwall", "chestnut",
    "dunearn", "windsor", "worcester", "belmont", "chee hoon",
    "linden", "margoliouth", "seton close", "bishop gate",
    "white house park", "ridout", "gallop"
]

def check_gcb_compliance(location: str, land_size_sqm: float, plot_width_m: float,
                          storeys: int, plot_depth_m: float, site_coverage_pct: float,
                          is_singapore_citizen: bool) -> dict:
    results = {}
    location_lower = location.lower()
    in_gcb_zone = any(zone in location_lower for zone in GCB_ZONES)

    results["gcb_zone"]       = {"pass": in_gcb_zone,
                                  "msg": "Recognised GCB zone" if in_gcb_zone else "Location not in known GCB zone — verify with URA"}
    results["land_size"]      = {"pass": land_size_sqm >= 1400,
                                  "msg": f"{land_size_sqm:.0f} sqm — min 1,400 sqm required"}
    results["plot_width"]     = {"pass": plot_width_m >= 18.5,
                                  "msg": f"{plot_width_m:.1f} m — min 18.5 m required"}
    results["storeys"]        = {"pass": storeys <= 2,
                                  "msg": f"{storeys} storeys — max 2 storeys (+ attic) allowed"}
    results["plot_depth"]     = {"pass": plot_depth_m >= 30,
                                  "msg": f"{plot_depth_m:.1f} m — min 30 m required"}
    results["site_coverage"]  = {"pass": site_coverage_pct <= 40,
                                  "msg": f"{site_coverage_pct:.1f}% — max 40% allowed"}
    results["sg_citizen"]     = {"pass": is_singapore_citizen,
                                  "msg": "Singapore Citizen confirmed" if is_singapore_citizen else "GCB ownership restricted to Singapore Citizens"}

    all_pass = all(v["pass"] for v in results.values())
    results["overall"] = "APPROVED" if all_pass else "PENDING REVIEW"
    return results

# ============================================================
# AI LISTING WRITER
# ============================================================
def write_listing(agent_name: str, agent_style: str, property_type: str, location: str,
                  land_size: str, buildup: str, bedrooms: str, price: str, features: str) -> str:
    style_map = {
        "Formal":  "professional, precise, authoritative — suitable for high-net-worth buyers",
        "Warm":    "warm, personal, family-focused — emphasise lifestyle and community",
        "Bold":    "bold, punchy, aspirational — every sentence commands attention",
        "Jane Lee": "warm and conversational, family-focused, signature phrase: 'Home is where the heart is'"
    }
    style_desc = style_map.get(agent_style, style_map["Formal"])

    prompt = f"""You are writing a luxury Singapore property listing for NestList Prestige.

Agent: {agent_name}
Writing style: {style_desc}

Property details:
- Type: {property_type}
- Location: {location}
- Land size: {land_size}
- Built-up: {buildup}
- Bedrooms: {bedrooms}
- Price: {price}
- Key features: {features}

Write a compelling luxury listing (250-350 words). Structure:
1. Powerful headline (ALL CAPS, max 12 words)
2. Opening paragraph — evoke prestige and lifestyle
3. Property highlights — specific, vivid details
4. Location advantages — Singapore context
5. Closing invitation

Use no emojis. Write with confidence and elegance. This is Singapore's finest real estate market."""

    try:
        msg = claude.messages.create(
            model="claude-sonnet-4-5",
            max_tokens=800,
            messages=[{"role": "user", "content": prompt}]
        )
        return msg.content[0].text
    except Exception as e:
        return f"Error generating listing: {e}"

# ============================================================
# SESSION STATE INIT
# ============================================================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "agent" not in st.session_state:
    st.session_state.agent = None
if "page" not in st.session_state:
    st.session_state.page = "Dashboard"

# ============================================================
# LOGIN PAGE
# ============================================================
def show_login():
    inject_css()
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown(f'<div style="text-align:center"><img src="{LOGO_URI}" width="160"></div>', unsafe_allow_html=True)
        st.markdown("""
        <div style="text-align:center; margin: 1rem 0 2rem 0;">
            <p style="font-family: Cormorant Garamond, serif; font-size: 1.8rem; color: #D4AF37; letter-spacing: 0.2em; margin:0;">NESTLIST PRESTIGE</p>
            <p style="font-size: 0.7rem; color: #5a6e5f; letter-spacing: 0.15em; text-transform: uppercase; margin: 0.3rem 0 0 0;">Singapore Luxury Property Platform</p>
        </div>
        """, unsafe_allow_html=True)

        email    = st.text_input("Email", placeholder="your@email.com")
        password = st.text_input("Password", type="password", placeholder="••••••••")

        if st.button("Sign In", use_container_width=True):
            if not email or not password:
                st.error("Please enter your email and password.")
            else:
                agent = get_agent_by_email(email.strip().lower())
                if agent and verify_password(password, agent.get("password_hash", "")):
                    st.session_state.logged_in = True
                    st.session_state.agent = agent
                    st.rerun()
                else:
                    st.error("Invalid credentials. Please try again.")

        st.markdown("""
        <p style="text-align:center; font-size: 0.7rem; color: #3a4e3f; margin-top: 2rem; letter-spacing: 0.08em;">
        SMARTER LISTINGS. BETTER RESULTS.<br>
        <span style="color: #2a3e2f;">NestList Pte Ltd · Singapore 2026</span>
        </p>
        """, unsafe_allow_html=True)

# ============================================================
# SIDEBAR
# ============================================================
def show_sidebar():
    agent = st.session_state.agent
    name  = agent.get("name", "Agent") if agent else "Agent"

    with st.sidebar:
        st.markdown(f'<div style="text-align:center; padding: 1.2rem 0 0.8rem 0;"><img src="{LOGO_URI}" width="150"></div>', unsafe_allow_html=True)
        st.markdown("""
        <div style="text-align:center; padding-bottom: 1rem; border-bottom: 1px solid rgba(212,175,55,0.2);">
            <p style="font-family: Cormorant Garamond, serif; font-size: 1.1rem; color: #D4AF37; letter-spacing: 0.18em; margin: 0;">NESTLIST PRESTIGE</p>
            <p style="font-size: 0.6rem; color: #3a5a42; letter-spacing: 0.12em; text-transform: uppercase; margin: 0.2rem 0 0 0;">Smarter Listings. Better Results.</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<p style="font-size: 0.6rem; color: #3a5a42; letter-spacing: 0.15em; text-transform: uppercase; padding: 0 1.2rem; margin-bottom: 0.3rem;">Navigation</p>', unsafe_allow_html=True)

        page = st.radio("", ["Dashboard", "New Listing", "My Listings", "My Profile", "Billing"], label_visibility="collapsed")
        st.session_state.page = page

        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown(f"""
        <div style="padding: 0 1.2rem; border-top: 1px solid rgba(212,175,55,0.15); padding-top: 1rem;">
            <p style="font-size: 0.72rem; color: #5a6e5f; margin: 0;">{name}</p>
            <p style="font-size: 0.65rem; color: #3a4e3f; margin: 0.1rem 0 0 0;">NestList Prestige</p>
        </div>
        """, unsafe_allow_html=True)

        if st.button("Sign Out", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.agent = None
            st.rerun()

    return page

# ============================================================
# PAGE: DASHBOARD
# ============================================================
def page_dashboard():
    agent    = st.session_state.agent
    name     = agent.get("name", "Agent") if agent else "Agent"
    agent_id = agent.get("id", "") if agent else ""

    st.markdown('<div class="nestlist-header"><h1>NestList Prestige</h1><p>Agent Command Centre</p></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="welcome-bar">Welcome back, <span>{name}</span>. Your listings are working for you.</div>', unsafe_allow_html=True)

    # Stat cards
    listings = get_listings_for_agent(agent_id)
    n_listings = len(listings)
    st.markdown(f"""
    <div class="stat-row">
        <div class="stat-card"><div class="stat-number">{n_listings}</div><div class="stat-label">Active Listings</div></div>
        <div class="stat-card"><div class="stat-number">0</div><div class="stat-label">Enquiries This Week</div></div>
        <div class="stat-card"><div class="stat-number">0</div><div class="stat-label">Profile Views</div></div>
        <div class="stat-card"><div class="stat-number">0</div><div class="stat-label">Serious Buyers</div></div>
    </div>
    """, unsafe_allow_html=True)

    col_left, col_right = st.columns([1.4, 1])

    with col_left:
        # Hero panel
        st.markdown("""
        <div class="hero-panel">
            <div class="hero-overlay"></div>
            <div class="hero-text">
                <h2>Queen Astrid Park</h2>
                <p>Good Class Bungalow · Prime District 10</p>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Recent listings
        st.markdown('<div class="panel-card"><div class="panel-title">Recent Listings</div>', unsafe_allow_html=True)
        if listings:
            for l in listings[:5]:
                st.markdown(f"""
                <div class="listing-card">
                    <h4>{l.get("title","Untitled")}</h4>
                    <p>{l.get("location","")} · {l.get("price","")} · {l.get("property_type","")}</p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown('<p style="font-size:0.82rem; color:#5a6e5f;">No listings yet. Create your first listing.</p>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col_right:
        # Quick actions
        st.markdown('<div class="panel-card"><div class="panel-title">Quick Actions</div>', unsafe_allow_html=True)
        if st.button("＋  New Listing", use_container_width=True):
            st.session_state.page = "New Listing"
            st.rerun()
        if st.button("View All Listings", use_container_width=True):
            st.session_state.page = "My Listings"
            st.rerun()
        if st.button("Edit Profile", use_container_width=True):
            st.session_state.page = "My Profile"
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

        # Client reminders
        st.markdown("""
        <div class="panel-card">
            <div class="panel-title">Client Reminders</div>
            <p style="font-size:0.78rem; color:#5a6e5f;">No reminders. Follow-up tracking coming soon.</p>
        </div>
        """, unsafe_allow_html=True)

        # Market Pulse
        st.markdown("""
        <div class="panel-card">
            <div class="panel-title">Singapore Market Pulse</div>
            <div class="pulse-grid">
                <div class="pulse-item"><div class="pulse-value">36</div><div class="pulse-desc">GCB Transactions 2025</div></div>
                <div class="pulse-item"><div class="pulse-value">SGD 1.36B</div><div class="pulse-desc">Total Transaction Value</div></div>
                <div class="pulse-item"><div class="pulse-value">SGD 2,134</div><div class="pulse-desc">Avg PSF</div></div>
                <div class="pulse-item"><div class="pulse-value">SGD 148M</div><div class="pulse-desc">Largest Single Deal</div></div>
            </div>
            <p class="pulse-disclaimer">Source: URA / EdgeProp 2025. Data for reference only. Verify with URA before advising clients. NestList bears no liability for reliance on these figures.</p>
        </div>
        """, unsafe_allow_html=True)

# ============================================================
# PAGE: NEW LISTING
# ============================================================
def page_new_listing():
    st.markdown('<div class="nestlist-header"><h1>New Listing</h1><p>Create a luxury property listing</p></div>', unsafe_allow_html=True)

    agent      = st.session_state.agent
    agent_id   = agent.get("id", "") if agent else ""
    agent_name = agent.get("name", "Agent") if agent else "Agent"

    col1, col2 = st.columns(2)
    with col1:
        property_type = st.selectbox("Property Type", ["GCB (Good Class Bungalow)", "Landed — Detached", "Landed — Semi-Detached", "Landed — Terrace", "Penthouse", "Luxury Condo"])
        location      = st.text_input("Location / District", placeholder="e.g. Queen Astrid Park, District 10")
        land_size     = st.text_input("Land Size", placeholder="e.g. 2,000 sqm")
        buildup       = st.text_input("Built-up Area", placeholder="e.g. 850 sqm")
    with col2:
        bedrooms  = st.text_input("Bedrooms / Configuration", placeholder="e.g. 6 bedrooms + study")
        price     = st.text_input("Asking Price", placeholder="e.g. SGD 28,000,000")
        features  = st.text_area("Key Features", placeholder="Pool, lift, wine cellar, panoramic views...", height=100)
        style     = st.selectbox("Writing Style", ["Formal", "Warm", "Bold", "Jane Lee"])

    is_gcb = "GCB" in property_type

    if is_gcb:
        st.markdown("---")
        st.markdown('<div class="panel-title" style="font-family: Cormorant Garamond, serif; color: #D4AF37;">URA GCB Compliance Check</div>', unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        with c1:
            land_sqm    = st.number_input("Land Size (sqm)", min_value=0.0, value=1400.0, step=10.0)
            plot_width  = st.number_input("Plot Width (m)", min_value=0.0, value=18.5, step=0.5)
        with c2:
            storeys     = st.number_input("Number of Storeys", min_value=1, max_value=5, value=2)
            plot_depth  = st.number_input("Plot Depth (m)", min_value=0.0, value=30.0, step=1.0)
        with c3:
            site_cov    = st.number_input("Site Coverage (%)", min_value=0.0, max_value=100.0, value=40.0)
            sg_citizen  = st.checkbox("I confirm the buyer is a Singapore Citizen")

        declaration = st.checkbox("I declare that the information submitted is accurate and I accept responsibility for compliance with URA regulations.")
    else:
        declaration = st.checkbox("I declare that the information submitted is accurate.")

    if st.button("Generate Listing", type="primary"):
        if not declaration:
            st.warning("Please tick the declaration checkbox before proceeding.")
        elif not location or not price:
            st.warning("Please fill in Location and Asking Price.")
        else:
            compliance_ok = True
            if is_gcb:
                results = check_gcb_compliance(location, land_sqm, plot_width, storeys, plot_depth, site_cov, sg_citizen)
                st.markdown("**Compliance Results:**")
                for key, val in results.items():
                    if key == "overall":
                        colour = "#90ee90" if val == "APPROVED" else "#ff6b6b"
                        st.markdown(f'<p style="font-size:0.9rem; color:{colour}; font-weight:600;">Overall: {val}</p>', unsafe_allow_html=True)
                    else:
                        icon = "✅" if val["pass"] else "⚠️"
                        st.markdown(f'{icon} {val["msg"]}')
                if results["overall"] != "APPROVED":
                    compliance_ok = False
                    st.warning("Compliance issues detected. Please review before publishing.")

            if compliance_ok:
                with st.spinner("NestList AI is crafting your listing..."):
                    listing_text = write_listing(agent_name, style, property_type, location, land_size, buildup, bedrooms, price, features)

                st.markdown("---")
                st.markdown('<div class="panel-title" style="font-family: Cormorant Garamond, serif; color: #D4AF37;">Your Generated Listing</div>', unsafe_allow_html=True)
                st.text_area("", value=listing_text, height=350)

                title = f"{property_type} — {location}"
                if save_listing(agent_id, title, listing_text, property_type, location, price):
                    st.success("Listing saved to your portfolio.")

                if st.button("Post to Facebook"):
                    fb_message = f"{title}\n\nAsking: {price}\n\n{listing_text[:800]}"
                    result = post_to_facebook(fb_message)
                    if "id" in result:
                        st.success("Posted to Facebook successfully!")
                    else:
                        st.error(f"Facebook error: {result.get('error', 'Unknown error')}")

                st.markdown("""
                <p style="font-size:0.65rem; color:#3a4e3f; margin-top:1rem; font-style:italic;">
                ⚠ This listing is generated by AI. All details must be verified by the agent before publication.
                NestList Pte Ltd accepts no liability for the accuracy of AI-generated content.
                Compliance with URA and CEA regulations remains the responsibility of the agent.
                </p>
                """, unsafe_allow_html=True)

# ============================================================
# PAGE: MY LISTINGS
# ============================================================
def page_my_listings():
    st.markdown('<div class="nestlist-header"><h1>My Listings</h1><p>Your property portfolio</p></div>', unsafe_allow_html=True)

    agent_id = st.session_state.agent.get("id", "") if st.session_state.agent else ""
    listings = get_listings_for_agent(agent_id)

    if not listings:
        st.markdown('<p style="color:#5a6e5f;">No listings yet. Go to New Listing to create your first.</p>', unsafe_allow_html=True)
        return

    for l in listings:
        with st.expander(f"{l.get('title','Untitled')} · {l.get('price','')}"):
            st.markdown(f"**Location:** {l.get('location','')}")
            st.markdown(f"**Type:** {l.get('property_type','')}")
            st.text_area("Listing text", value=l.get("content",""), height=200, key=f"lt_{l.get('id','')}")
            if st.button("Post to Facebook", key=f"fb_{l.get('id','')}"):
                msg = f"{l.get('title','')} · {l.get('price','')}\n\n{l.get('content','')[:800]}"
                result = post_to_facebook(msg)
                if "id" in result:
                    st.success("Posted!")
                else:
                    st.error(f"Error: {result.get('error','Unknown')}")

# ============================================================
# PAGE: MY PROFILE
# ============================================================
def page_my_profile():
    st.markdown('<div class="nestlist-header"><h1>My Profile</h1><p>Agent settings and preferences</p></div>', unsafe_allow_html=True)

    agent = st.session_state.agent or {}

    with st.form("profile_form"):
        col1, col2 = st.columns(2)
        with col1:
            name      = st.text_input("Full Name",    value=agent.get("name",""))
            email     = st.text_input("Email",         value=agent.get("email",""), disabled=True)
            cea       = st.text_input("CEA Licence No", value=agent.get("cea_number",""), placeholder="e.g. R012345A")
        with col2:
            agency    = st.text_input("Agency",        value=agent.get("agency","NestList"))
            specialty = st.text_input("Specialty",     value=agent.get("specialty","Landed. GCB. Penthouses. Ultra Luxury."))
            style     = st.selectbox("Writing Style",  ["Formal","Warm","Bold","Jane Lee"],
                                     index=["Formal","Warm","Bold","Jane Lee"].index(agent.get("style","Formal")) if agent.get("style","Formal") in ["Formal","Warm","Bold","Jane Lee"] else 0)

        submitted = st.form_submit_button("Save Profile", type="primary")
        if submitted:
            updates = {"name": name, "agency": agency, "specialty": specialty, "style": style, "cea_number": cea}
            if update_agent_profile(agent.get("id",""), updates):
                st.session_state.agent.update(updates)
                st.success("Profile saved!")
                st.balloons()

# ============================================================
# PAGE: BILLING
# ============================================================
def page_billing():
    st.markdown('<div class="nestlist-header"><h1>Billing</h1><p>Subscription details</p></div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="panel-card">
        <div class="panel-title">Current Plan</div>
        <p style="font-family: Cormorant Garamond, serif; font-size: 1.4rem; color: #D4AF37;">NestList Prestige</p>
        <p style="font-size: 0.82rem; color: #c8c0b0;">SGD 299 / month</p>
        <p style="font-size: 0.78rem; color: #5a6e5f; margin-top: 0.8rem;">GCB · Landed · Penthouses · Ultra Luxury<br>Unlimited listings · Facebook auto-posting · AI listing writer · URA compliance checker</p>
    </div>
    <div class="panel-card">
        <div class="panel-title">Payment</div>
        <p style="font-size: 0.82rem; color: #5a6e5f;">Stripe payment integration coming soon.<br>Contact hello.nestlist@gmail.com for billing enquiries.</p>
    </div>
    """, unsafe_allow_html=True)

# ============================================================
# MAIN APP ROUTER
# ============================================================
def main():
    inject_css()

    if not st.session_state.logged_in:
        show_login()
        return

    page = show_sidebar()

    if page == "Dashboard":
        page_dashboard()
    elif page == "New Listing":
        page_new_listing()
    elif page == "My Listings":
        page_my_listings()
    elif page == "My Profile":
        page_my_profile()
    elif page == "Billing":
        page_billing()

if __name__ == "__main__":
    main()
