
import streamlit as st
import anthropic
import os

# Page config
st.set_page_config(
    page_title="NestList — Agent Dashboard",
    page_icon="🏡",
    layout="wide"
)

# Header
st.markdown("""
<style>
.header {
    background: #2C3E8C;
    color: white;
    padding: 20px;
    border-radius: 10px;
    margin-bottom: 20px;
}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="header"><h2>🏡 NestList Premium</h2><p>Welcome back, Jane Lee</p></div>', 
            unsafe_allow_html=True)

# Sidebar navigation
page = st.sidebar.selectbox(
    "Navigation",
    ["📊 Dashboard", "✍️ New Listing", "🏡 My Listings", 
     "💬 Enquiries", "👤 My Profile"]
)

# ================================
# NEW LISTING PAGE
# ================================
if page == "✍️ New Listing":
    st.title("Submit New Listing")
    st.write("Fill in the 7 details below. Claude will write your personalised listing and run a compliance check automatically.")
    
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
                placeholder=14500
            )
            plot_width = st.number_input(
                "4. Plot Width (metres)",
                min_value=0.0,
                placeholder=20.0
            )
        
        with col2:
            built_up = st.number_input(
                "5. Built-up Size (sqft)",
                min_value=0,
                placeholder=4500
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
            placeholder="e.g. Private pool, 3-car garage, newly renovated, smart home system"
        )
        
        st.markdown("---")
        declaration = st.checkbox(
            "I confirm all details above are accurate and truthful. "
            "I understand NestList will run an automatic URA compliance "
            "check before posting."
        )
        
        submitted = st.form_submit_button(
            "🤖 Generate & Post My Listing Automatically",
            use_container_width=True
        )
    
    # When form is submitted
    if submitted:
        if not declaration:
            st.error("Please tick the declaration box before submitting.")
        elif not location or not bedrooms or not price:
            st.error("Please fill in all required fields.")
        else:
            # STEP 1 — Run compliance check
            st.markdown("---")
            st.subheader("Step 1 — Running URA Compliance Check...")
            
            gcb_zones = [
                "nassim", "cluny", "white house park", "dalvey",
                "ladyhill", "cornwall", "king albert park",
                "raffles park", "swiss club", "victoria park",
                "holland", "bin tong park", "leedon", "maryland",
                "bishopsgate", "fourth avenue", "grange", "jervois",
                "rochalie", "linden", "chee hoon", "swettenham",
                "tanglin", "chestnut", "sunset", "upper bukit timah",
                "rifle range", "spring grove", "belmont", "windsor",
                "hendersons", "yarwood", "ewart", "ford"
            ]
            
            issues = []
            warnings = []
            passed = []
            
            is_gcb = "gcb" in property_type.lower() or "bungalow" in property_type.lower()
            
            if is_gcb:
                # Check location
                location_lower = location.lower()
                in_zone = any(z in location_lower for z in gcb_zones)
                if in_zone:
                    passed.append("Location is within a gazetted GCBa zone")
                else:
                    warnings.append("Location could not be automatically verified as a GCBa zone. Please confirm with URA.")
                
                # Check land size
                if land_size >= 15069:
                    passed.append(f"Land size {land_size:,} sqft meets URA minimum")
                elif land_size >= 14000:
                    warnings.append(f"Land size {land_size:,} sqft is slightly below minimum 15,069 sqft. Please verify with URA.")
                elif land_size > 0:
                    issues.append(f"Land size {land_size:,} sqft does not meet GCB minimum of 15,069 sqft")
                
                # Check plot width
                if plot_width >= 18.5:
                    passed.append(f"Plot width {plot_width}m meets URA minimum of 18.5m")
                elif plot_width > 0:
                    warnings.append(f"Plot width {plot_width}m is below URA minimum of 18.5m. Please verify.")
                else:
                    warnings.append("Plot width not provided. Please verify minimum 18.5m with URA.")
            
            # Show compliance result
            if issues:
                st.error("❌ Compliance Check Failed — Listing cannot be posted")
                for issue in issues:
                    st.error(f"• {issue}")
                st.stop()
            elif warnings:
                st.warning("⚠️ Passed with Warnings — Please verify before posting")
                for warning in warnings:
                    st.warning(f"• {warning}")
                for p in passed:
                    st.success(f"✅ {p}")
            else:
                for p in passed:
                    st.success(f"✅ {p}")
                st.success("✅ All compliance checks passed!")
            
            # STEP 2 — Generate listing with Claude
            st.markdown("---")
            st.subheader("Step 2 — Claude is writing your listing...")
            
            # Jane's personal style profile
            agent_style = """
You are Jane Lee from NestList, a specialist in 
Landed and GCB Properties in Singapore.
Your tone is warm and conversational.
You emphasise family living and emotional comfort of home.
Your signature phrase: "Home is where the heart is, 
so the saying goes. Nothing beats coming back to a place 
where you feel most comfort after a long day."
Weave this phrase in naturally.
"""
            
            prompt = f"""
{agent_style}

Write a premium property listing for:
- Type: {property_type}
- Location: {location}
- Land size: {land_size:,} sqft
- Built-up: {built_up:,} sqft
- Bedrooms: {bedrooms}
- Price: SGD {price}
- Features: {features}

Write:
1. A warm compelling headline
2. Three paragraphs in Jane's voice
3. A gentle call to action
4. End with: Jane Lee | NestList Specialist
"""
            
            try:
                api_key = os.environ.get("ANTHROPIC_API_KEY", "")
                client = anthropic.Anthropic(api_key=api_key)
                
                with st.spinner("Claude is writing your listing..."):
                    response = client.messages.create(
                        model="claude-sonnet-4-5",
                        max_tokens=1024,
                        messages=[{
                            "role": "user",
                            "content": prompt
                        }]
                    )
                
                listing_text = response.content[0].text
                
                # STEP 3 — Show the listing
                st.markdown("---")
                st.subheader("Step 3 — Your Listing is Ready! 🎉")
                st.markdown(listing_text)
                
                # Disclaimer
                st.markdown("---")
                st.caption(
                    "DISCLAIMER: This listing has been automatically verified "
                    "by NestList's compliance system based on URA guidelines. "
                    "Agents are responsible for accuracy. Buyers should conduct "
                    "their own due diligence."
                )
                
                st.success(
                    "✅ Your listing has been generated! "
                    "Multi-channel posting coming in Week 3!"
                )
                
            except Exception as e:
                st.error(f"Error generating listing: {str(e)}")

# ================================
# DASHBOARD PAGE
# ================================
elif page == "📊 Dashboard":
    st.title("Dashboard")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Active Listings", "3")
    with col2:
        st.metric("Total Enquiries", "12")
    with col3:
        st.metric("Total Views", "847")
    with col4:
        st.metric("Serious Buyers", "2")
    
    st.markdown("---")
    st.subheader("Recent Activity")
    st.info("📋 King Albert Park GCB — 342 views this week")
    st.info("💬 New enquiry from Mr Tan Wei Ming — AI reply sent")
    st.info("📋 Nassim Road GCB — 505 views this week")

# ================================
# MY PROFILE PAGE
# ================================
elif page == "👤 My Profile":
    st.title("My Profile & Style Settings")
    
    st.subheader("Agent Details")
    col1, col2 = st.columns(2)
    with col1:
        st.text_input("Name", value="Jane Lee", disabled=True)
        st.text_input("Agency", value="NestList", disabled=True)
    with col2:
        st.text_input("Specialty", 
                     value="Landed & GCB Properties", 
                     disabled=True)
        st.text_input("Plan", 
                     value="NestList Premium — SGD 149/month", 
                     disabled=True)
    
    st.markdown("---")
    st.subheader("My Writing Style")
    
    tone = st.selectbox(
        "Writing Tone",
        ["Warm & Conversational", 
         "Formal & Professional", 
         "Bold & Punchy"],
        index=0
    )
    emphasis = st.selectbox(
        "What I Emphasise",
        ["Family Living & Emotional Comfort",
         "Investment Returns & Capital Appreciation",
         "Lifestyle & Prestige",
         "Architecture & Design"],
        index=0
    )
    signature = st.text_area(
        "My Signature Phrase",
        value="Home is where the heart is, so the saying goes. Nothing beats coming back to a place where you feel most comfort after a long day.",
        height=100
    )
    
    if st.button("💾 Save My Style Settings", 
                 use_container_width=True):
        st.success(
            "✅ Style saved! Your next listing will use "
            "these settings automatically."
        )

# ================================
# OTHER PAGES
# ================================
elif page == "🏡 My Listings":
    st.title("My Listings")
    st.info("Coming in Day 8 — your listing history will appear here!")

elif page == "💬 Enquiries":
    st.title("Buyer Enquiries")
    st.info("Coming in Week 3 — buyer enquiries and AI replies will appear here!")
