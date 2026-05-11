
import streamlit as st
import anthropic
import os
import json
from datetime import datetime

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

# Header
st.markdown("""
<div class="header">
    <h2>🏡 NestList Premium</h2>
    <p>Welcome back, Jane Lee | Landed & GCB Specialist</p>
</div>
""", unsafe_allow_html=True)

# Sidebar
st.sidebar.image("https://via.placeholder.com/150x50/2C3E8C/ffffff?text=NestList", 
                  use_container_width=True)
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

# Initialize session state for listings
if "listings" not in st.session_state:
    st.session_state.listings = []

if "agent_profile" not in st.session_state:
    st.session_state.agent_profile = {
        "name": "Jane Lee",
        "agency": "NestList",
        "specialty": "Landed & GCB Properties",
        "tone": "Warm & Conversational",
        "emphasis": "Family Living & Emotional Comfort",
        "signature": "Home is where the heart is, so the saying goes. Nothing beats coming back to a place where you feel most comfort after a long day.",
        "contact": "Contact Jane for a private viewing"
    }

# ================================
# DASHBOARD PAGE
# ================================
if page == "📊 Dashboard":
    st.title("Dashboard")
    
    # Real stats from session
    total_listings = len(st.session_state.listings)
    
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
    
    # Recent listings
    st.subheader("Recent Listings")
    if st.session_state.listings:
        for listing in reversed(st.session_state.listings[-3:]):
            with st.expander(f"🏡 {listing['location']} — SGD {listing['price']}"):
                st.write(listing['content'])
    else:
        st.info("No listings yet. Click '✍️ New Listing' to create your first one!")

    st.markdown("---")
    st.subheader("Quick Actions")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("✍️ Create New Listing", use_container_width=True):
            st.switch_page
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
            property_type = st.selectbox(
                "1. Property Type",
                ["Good Class Bungalow (GCB)",
                 "Landed Bungalow",
                 "Semi-Detached",
                 "Terrace House",
                 "HDB Flat",
                 "Condominium"]
            )
            location = st.text_input(
                "2. Location",
                placeholder="e.g. Nassim Road, District 10"
            )
            land_size = st.number_input(
                "3. Land Size (sqft)",
                min_value=0,
                value=0
            )
            plot_width = st.number_input(
                "4. Plot Width (metres)",
                min_value=0.0,
                value=0.0
            )

        with col2:
            built_up = st.number_input(
                "5. Built-up Size (sqft)",
                min_value=0,
                value=0
            )
            bedrooms = st.text_input(
                "6. Bedrooms & Bathrooms",
                placeholder="e.g. 4 bedrooms, 4 bathrooms"
            )
            price = st.text_input(
                "7. Asking Price (SGD)",
                placeholder="e.g. 25,700,000"
            )

        features = st.text_area(
            "Special Features",
            placeholder="e.g. Private pool, 3-car garage, newly renovated"
        )

        st.markdown("---")
        declaration = st.checkbox(
            "I confirm all details are accurate and truthful. "
            "I understand NestList will run an automatic URA "
            "compliance check before posting."
        )

        submitted = st.form_submit_button(
            "🤖 Generate My Listing Automatically",
            use_container_width=True
        )

    if submitted:
        if not declaration:
            st.error("Please tick the declaration box before submitting.")
        elif not location or not bedrooms or not price:
            st.error("Please fill in all required fields.")
        else:
            # COMPLIANCE CHECK
            st.markdown("---")
            st.subheader("Step 1 — URA Compliance Check")

            gcb_zones = [
                "nassim", "cluny", "white house park", "dalvey",
                "ladyhill", "cornwall", "king albert park",
                "raffles park", "swiss club", "victoria park",
                "holland", "bin tong park", "leedon", "maryland",
                "bishopsgate", "fourth avenue", "grange", "jervois",
                "rochalie", "linden", "chee hoon", "swettenham",
                "tanglin", "chestnut", "sunset", "upper bukit timah",
                "rifle range", "spring grove", "belmont", "windsor"
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
                    warnings.append("Location could not be verified as GCBa zone. Please confirm with URA.")

                if land_size >= 15069:
                    passed.append(f"Land size {land_size:,} sqft meets URA minimum")
                elif land_size >= 14000:
                    warnings.append(f"Land size {land_size:,} sqft slightly below minimum. Please verify with URA.")
                elif land_size > 0:
                    issues.append(f"Land size {land_size:,} sqft does not meet GCB minimum of 15,069 sqft")

                if plot_width >= 18.5:
                    passed.append(f"Plot width {plot_width}m meets URA minimum")
                elif plot_width > 0:
                    warnings.append(f"Plot width {plot_width}m below URA minimum of 18.5m. Please verify.")
                else:
                    warnings.append("Plot width not provided. Please verify minimum 18.5m.")

            for p in passed:
                st.success(f"✅ {p}")
            for w in warnings:
                st.warning(f"⚠️ {w}")
            for i in issues:
                st.error(f"❌ {i}")

            if issues:
                st.error("❌ Listing blocked — please fix the issues above.")
            else:
                # GENERATE LISTING
                st.markdown("---")
                st.subheader("Step 2 — Claude is writing your listing...")

                profile = st.session_state.agent_profile
                prompt = f"""
You are {profile['name']} from {profile['agency']}, 
a specialist in {profile['specialty']}.
Your tone: {profile['tone']}
You emphasise: {profile['emphasis']}
Your signature phrase: "{profile['signature']}"
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
4. End with: {profile['name']} | {profile['agency']} Specialist
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

                    # Save to session state
                    st.session_state.listings.append({
                        "location": location,
                        "price": price,
                        "type": property_type,
                        "date": datetime.now().strftime("%d %b %Y %I:%M %p"),
                        "content": listing_text
                    })

                    # Show listing
                    st.markdown("---")
                    st.subheader("Step 3 — Your Listing is Ready! 🎉")
                    st.markdown(listing_text)

                    st.caption(
                        "DISCLAIMER: Auto-verified by NestList compliance system. "
                        "Agents responsible for accuracy. Buyers conduct own due diligence."
                    )
                    st.success("✅ Listing generated and saved to My Listings!")

                except Exception as e:
                    st.error(f"Error generating listing: {str(e)}")

# ================================
# MY LISTINGS PAGE
# ================================
elif page == "🏡 My Listings":
    st.title("My Listings")

    if st.session_state.listings:
        st.write(f"You have {len(st.session_state.listings)} listing(s) generated this session.")
        st.markdown("---")

        for i, listing in enumerate(reversed(st.session_state.listings)):
            with st.expander(
                f"🏡 {listing['location']} — SGD {listing['price']} | {listing['date']}"
            ):
                st.markdown(listing["content"])
                col1, col2 = st.columns(2)
                with col1:
                    st.button(f"📋 Copy Listing #{i+1}", 
                             key=f"copy_{i}")
                with col2:
                    st.button(f"🔄 Regenerate #{i+1}", 
                             key=f"regen_{i}")
    else:
        st.info("No listings yet! Go to '✍️ New Listing' to create your first one.")
        st.markdown("Once you generate listings they will appear here automatically.")

# ================================
# ENQUIRIES PAGE
# ================================
elif page == "💬 Enquiries":
    st.title("Buyer Enquiries")
    st.info("🔜 Coming in Week 3 — buyer enquiries and AI auto-replies will appear here!")
    st.markdown("""
    **What's coming:**
    - Buyers enquire through your listing
    - AI reads their message automatically  
    - AI sends a smart personalised reply instantly
    - You get notified on WhatsApp
    - All enquiries tracked here in one place
    """)

# ================================
# MY PROFILE PAGE
# ================================
elif page == "👤 My Profile":
    st.title("My Profile & Style Settings")
    st.write("Update your details below. Your style is applied to every listing you generate.")

    profile = st.session_state.agent_profile

    st.subheader("Agent Details")
    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input("Full Name", value=profile["name"])
        agency = st.text_input("Agency", value=profile["agency"])
    with col2:
        specialty = st.text_input("Specialty", value=profile["specialty"])
        contact = st.text_input("Contact", value=profile["contact"])

    st.markdown("---")
    st.subheader("My Writing Style")

    tone = st.selectbox(
        "Writing Tone",
        ["Warm & Conversational",
         "Formal & Professional",
         "Bold & Punchy"],
        index=["Warm & Conversational",
               "Formal & Professional",
               "Bold & Punchy"].index(profile["tone"])
        if profile["tone"] in ["Warm & Conversational",
                               "Formal & Professional",
                               "Bold & Punchy"] else 0
    )

    emphasis = st.selectbox(
        "What I Emphasise",
        ["Family Living & Emotional Comfort",
         "Investment Returns & Capital Appreciation",
         "Lifestyle & Prestige",
         "Architecture & Design"],
        index=["Family Living & Emotional Comfort",
               "Investment Returns & Capital Appreciation",
               "Lifestyle & Prestige",
               "Architecture & Design"].index(profile["emphasis"])
        if profile["emphasis"] in ["Family Living & Emotional Comfort",
                                   "Investment Returns & Capital Appreciation",
                                   "Lifestyle & Prestige",
                                   "Architecture & Design"] else 0
    )

    signature = st.text_area(
        "My Signature Phrase",
        value=profile["signature"],
        height=100,
        help="This phrase will be woven naturally into every listing you generate."
    )

    st.markdown("---")
    if st.button("💾 Save My Style Settings", use_container_width=True):
        st.session_state.agent_profile = {
            "name": name,
            "agency": agency,
            "specialty": specialty,
            "tone": tone,
            "emphasis": emphasis,
            "signature": signature,
            "contact": contact
        }
        st.success("✅ Profile saved! Your next listing will use these settings.")
        st.balloons()

# ================================
# BILLING PAGE
# ================================
elif page == "💳 Billing":
    st.title("Billing & Subscription")

    st.markdown("""
    <div style="background:#EEEDFE;border-radius:10px;padding:16px;margin-bottom:16px;">
        <h3 style="color:#3C3489;margin:0;">NestList Premium</h3>
        <p style="color:#534AB7;margin:4px 0 0;">SGD 149 / month | Next billing: 1 June 2026</p>
    </div>
    """, unsafe_allow_html=True)

    st.subheader("Billing History")
    billing = [
        ("May 2026", "1 May 2026", "SGD 149"),
        ("April 2026", "1 April 2026", "SGD 149"),
    ]
    for month, date, amount in billing:
        col1, col2, col3 = st.columns([3, 3, 1])
        with col1:
            st.write(f"**{month}** — NestList Premium")
        with col2:
            st.write(f"Paid on {date}")
        with col3:
            st.write(f"✅ {amount}")
        st.divider()
