import streamlit as st
import anthropic
import os
import bcrypt
import requests
from datetime import datetime
from supabase import create_client, Client

# Page config
st.set_page_config(
    page_title="NestList — Agent Dashboard",
    page_icon="🏡",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
.header {
    background: linear-gradient(135deg, #2C3E8C, #1A6B4A);
    color: white;
    padding: 20px 24px;
    border-radius: 12px;
    margin-bottom: 24px;
}
.header h2 { margin: 0; font-size: 22px; }
.header p { margin: 4px 0 0; opacity: 0.85; font-size: 14px; }
.stat-box {
    background: white;
    border: 1px solid #E8ECF0;
    border-radius: 10px;
    padding: 16px;
    text-align: center;
}
.stat-num { font-size: 28px; font-weight: 700; color: #2C3E8C; }
.stat-label { font-size: 12px; color: #888; margin-top: 4px; }
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
# FACEBOOK AUTO-POSTING
# ================================
def post_to_facebook(listing_text, location, price, property_type):
    """Post a listing to the NestList Facebook Page."""
    fb_token = os.environ.get("FB_PAGE_ACCESS_TOKEN", "")
    fb_page_id = os.environ.get("FB_PAGE_ID", "")

    if not fb_token or not fb_page_id:
        return False, "Facebook credentials not configured."

    # Create a short, punchy Facebook post from the listing
    post_message = f"""🏡 NEW LISTING | {property_type}
📍 {location}
💰 SGD {price}

{listing_text[:800]}...

📞 Contact us at nestlist.sg to find out more!

#NestList #Singapore #SingaporeProperty #GCB #LandedProperty #PropertySG #RealEstate"""

    url = f"https://graph.facebook.com/v25.0/{fb_page_id}/feed"
    payload = {
        "message": post_message,
        "access_token": fb_token
    }

    try:
        response = requests.post(url, data=payload)
        result = response.json()
        if "id" in result:
            return True, result["id"]
        else:
            return False, result.get("error", {}).get("message", "Unknown error")
    except Exception as e:
        return False, str(e)

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

# ================================
# LOGIN / REGISTER PAGE
# ================================
if "agent" not in st.session_state:
    st.session_state.agent = None

if st.session_state.agent is None:
    st.markdown("""
    <div style="text-align:center; padding: 40px 0 20px;">
        <h1 style="color:#2C3E8C;">🏡 NestList</h1>
        <p style="color:#666;">Singapore's AI-Powered Property Platform</p>
    </div>
    """, unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["Login", "Register"])

    with tab1:
        st.subheader("Agent Login")
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
        st.subheader("New Agent Registration")
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
                    st.success("Account created! Welcome to NestList!")
                    st.rerun()
                else:
                    st.error("Email already registered or error occurred.")

    st.stop()

# ================================
# MAIN APP (LOGGED IN)
# ================================
agent = st.session_state.agent

# Header
st.markdown(f"""
<div class="header">
    <h2>🏡 NestList Premium</h2>
    <p>Welcome back, {agent['name']} | {agent['specialty']}</p>
</div>
""", unsafe_allow_html=True)

# Sidebar
st.sidebar.markdown(f"### 👤 {agent['name']}")
st.sidebar.markdown(f"*{agent['agency']}*")
st.sidebar.markdown("---")
page = st.sidebar.radio(
    "Navigation",
    ["📊 Dashboard",
     "✍️ New Listing",
     "🏡 My Listings",
     "💬 Enquiries",
     "👤 My Profile",
     "💳 Billing"],
    label_visibility="hidden"
)
st.sidebar.markdown("---")
if st.sidebar.button("🚪 Logout", use_container_width=True):
    st.session_state.agent = None
    st.rerun()

# ================================
# DASHBOARD PAGE
# ================================
if page == "📊 Dashboard":
    st.title("Dashboard")

    listings = get_agent_listings(agent['id'])
    total_listings = len(listings)

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"""
        <div class="stat-box">
            <div class="stat-num">{total_listings}</div>
            <div class="stat-label">Active Listings</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div class="stat-box">
            <div class="stat-num">0</div>
            <div class="stat-label">Total Enquiries</div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown("""
        <div class="stat-box">
            <div class="stat-num">0</div>
            <div class="stat-label">Total Views</div>
        </div>
        """, unsafe_allow_html=True)
    with col4:
        st.markdown("""
        <div class="stat-box">
            <div class="stat-num">0</div>
            <div class="stat-label">Serious Buyers</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    st.subheader("Recent Listings")
    if listings:
        for listing in listings[:3]:
            with st.expander(f"🏡 {listing['location']} — SGD {listing['price']}"):
                st.write(listing['content'])
    else:
        st.info("No listings yet. Click '✍️ New Listing' to create your first one!")

    st.markdown("---")
    st.subheader("Quick Actions")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("✍️ Create New Listing", use_container_width=True):
            st.info("Go to '✍️ New Listing' in the sidebar!")
    with col2:
        if st.button("👤 Update My Profile", use_container_width=True):
            st.info("Go to '👤 My Profile' in the sidebar!")

# ================================
# NEW LISTING PAGE
# ================================
elif page == "✍️ New Listing":
    st.title("Submit New Listing")
    st.write("Fill in the details below. Claude will write your personalised listing automatically.")

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
        submitted = st.form_submit_button("🤖 Generate My Listing Automatically", use_container_width=True)

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
                    issues.append("GCB purchases are restricted to Singapore Citizens only — PRs and foreigners are not eligible")
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
                    claude = anthropic.Anthropic(api_key=api_key)

                    with st.spinner("Claude is writing your personalised listing..."):
                        response = claude.messages.create(
                            model="claude-sonnet-4-5",
                            max_tokens=1024,
                            messages=[{"role": "user", "content": prompt}]
                        )

                    listing_text = response.content[0].text
                    save_listing(agent['id'], location, price, property_type, listing_text)

                    st.markdown("---")
                    st.subheader("Step 3 — Your Listing is Ready! 🎉")
                    st.markdown(listing_text)
                    st.success("✅ Listing saved to My Listings!")

                    # ================================
                    # FACEBOOK AUTO-POSTING
                    # ================================
                    st.markdown("---")
                    st.subheader("Step 4 — Post to Facebook 📘")
                    st.info("Your listing is ready to post to the NestList Facebook Page!")

                    if st.button("📘 Post to NestList Facebook Page Now", use_container_width=True):
                        with st.spinner("Posting to Facebook..."):
                            success, result = post_to_facebook(listing_text, location, price, property_type)
                        if success:
                            st.success(f"✅ Successfully posted to Facebook! Post ID: {result}")
                            st.balloons()
                        else:
                            st.error(f"❌ Facebook post failed: {result}")

                except Exception as e:
                    st.error(f"Error generating listing: {str(e)}")

# ================================
# MY LISTINGS PAGE
# ================================
elif page == "🏡 My Listings":
    st.title("My Listings")
    listings = get_agent_listings(agent['id'])

    if listings:
        st.write(f"You have {len(listings)} listing(s).")
        st.markdown("---")
        for i, listing in enumerate(listings):
            with st.expander(f"🏡 {listing['location']} — SGD {listing['price']} | {listing['created_at'][:10]}"):
                st.markdown(listing["content"])
                if st.button(f"📘 Post to Facebook", key=f"fb_post_{i}"):
                    with st.spinner("Posting to Facebook..."):
                        success, result = post_to_facebook(
                            listing["content"],
                            listing["location"],
                            listing["price"],
                            listing["property_type"]
                        )
                    if success:
                        st.success(f"✅ Posted to Facebook! Post ID: {result}")
                    else:
                        st.error(f"❌ Failed: {result}")
    else:
        st.info("No listings yet! Go to '✍️ New Listing' to create your first one.")

# ================================
# ENQUIRIES PAGE
# ================================
elif page == "💬 Enquiries":
    st.title("Buyer Enquiries")
    st.info("🔜 Coming in Week 3 — buyer enquiries and AI auto-replies will appear here!")

# ================================
# MY PROFILE PAGE
# ================================
elif page == "👤 My Profile":
    st.title("My Profile & Style Settings")

    st.subheader("Agent Details")
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
    if st.button("💾 Save My Style Settings", use_container_width=True):
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

# ================================
# BILLING PAGE
# ================================
elif page == "💳 Billing":
    st.title("Billing & Subscription")
    st.markdown("""
    <div style="background:#EEEDFE;border-radius:10px;padding:16px;margin-bottom:16px;">
        <h3 style="color:#3C3489;margin:0;">NestList Premium</h3>
        <p style="color:#534AB7;margin:4px 0 0;">SGD 149 / month</p>
    </div>
    """, unsafe_allow_html=True)
    st.info("🔜 Stripe payment integration coming soon!")
