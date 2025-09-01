# app.py - Main Streamlit Application for Festival Story Collector (పండుగల కథల సేకరణ)

import streamlit as st
import os
from typing import Optional, Dict, List
import pandas as pd
from dotenv import load_dotenv
from utils.api_client import SwechaAPIClient
import uuid # Import uuid for generating unique IDs
from datetime import datetime # Import datetime for handling timestamp sorting

# Load environment variables
load_dotenv()

# Initialize API client (cached to persist across reruns)
@st.cache_resource
def get_api_client():
    return SwechaAPIClient()

api_client = get_api_client()

# Page configuration
st.set_page_config(
    page_title="పండుగల కథల సేకరణ - Festival Story Collector",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Telugu text and festival-themed UI
st.markdown("""
<style>
    .main-header {
        text-align: center;
        color: #ff6b35;
        font-size: 2.5rem;
        margin-bottom: 2rem;
        font-weight: bold;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }
    .festival-card {
        border: 2px solid #ffeb3b;
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
        background: linear-gradient(135deg, #fff3e0 0%, #ffe0b2 100%);
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    .telugu-text {
        font-family: "Noto Sans Telugu", sans-serif;
        font-size: 1.2rem;
    }
    .success-box {
        background-color: #e8f5e8;
        border: 1px solid #4caf50;
        border-radius: 8px;
        padding: 12px;
        color: #2e7d32;
    }
    .error-box {
        background-color: #ffebee;
        border: 1px solid #f44336;
        border-radius: 8px;
        padding: 12px;
        color: #c62828;
    }
    .festival-theme {
        background: linear-gradient(45deg, #ff9800, #ffc107);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# Session state management
def init_session_state():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    if "user_data" not in st.session_state:
        st.session_state.user_data = None
    if "access_token" not in st.session_state:
        st.session_state.access_token = None

def main():
    init_session_state()
    
    # Ensure API client always has the current token if available in session state
    if st.session_state.access_token:
        api_client.set_auth_token(st.session_state.access_token)
        
        # Attempt to re-authenticate if token exists but session is not authenticated
        if not st.session_state.authenticated:
            user_profile = api_client.read_users_me()
            if user_profile:
                st.session_state.user_data = user_profile
                st.session_state.authenticated = True
                st.success("Re-authenticated successfully!")
                st.rerun() # Rerun to update UI with authenticated state
            else:
                st.session_state.access_token = None # Clear invalid token
                st.session_state.authenticated = False
                st.warning("Session expired or invalid token. Please log in again.")
    
    # Main header
    st.markdown('<h1 class="main-header">పండుగల కథల సేకరణ (Festival Story Collector)</h1>', unsafe_allow_html=True)
    st.markdown('<p class="telugu-text" style="text-align: center;">Preserving Festival Traditions and Stories - సాంప్రదాయ పండుగల కథలు మరియు జ్ఞాపకాలను పరిరక్షిస్తూ</p>', unsafe_allow_html=True)
    st.markdown("---")
    
    # Authentication check
    if not st.session_state.authenticated:
        show_auth_pages(api_client)
    else:
        # Default to Home page if authenticated
        if "current_page" not in st.session_state:
            st.session_state.current_page = "Home"
        show_main_app(api_client)

def show_auth_pages(api_client):
    """Show authentication pages (login/signup)"""
    auth_tab = st.sidebar.selectbox("Choose Action", ["Login", "Sign Up"])
    
    if auth_tab == "Login":
        show_login_page(api_client)
    else:
        show_signup_page(api_client)

def show_login_page(api_client):
    """Show login page"""
    st.header("🪔 Login to Your Account")
    
    with st.form("login_form"):
        col1, col2 = st.columns([1, 1])
        
        with col1:
            phone_number = st.text_input("Phone Number", placeholder="Enter your phone number")
            password = st.text_input("Password", type="password", placeholder="Enter your password")
        
        with col2:
            st.markdown("### Welcome Back to Festival Stories!")
            st.markdown("Login to continue sharing and preserving our beautiful festival traditions.")
            st.markdown("**New here?** Switch to Sign Up to join our community of storytellers.")
        
        submitted = st.form_submit_button("Login", use_container_width=True)
        
    if submitted and phone_number and password:
        with st.spinner("Logging in..."):
            result = api_client.login_for_access_token(phone_number, password)
            if result and "access_token" in result:
                st.session_state.access_token = result["access_token"]
                api_client.set_auth_token(st.session_state.access_token)

                # Fetch user profile
                user_profile = api_client.read_users_me()
                if user_profile:
                    st.session_state.user_data = user_profile
                    st.session_state.authenticated = True
                    st.success("Login successful! Redirecting...")
                    st.rerun()

def show_signup_page(api_client):
    """Show signup page with OTP verification"""
    st.header("✨ Join Our Festival Story Community")
    
    # Initialize session state for signup steps
    if "signup_step" not in st.session_state:
        st.session_state.signup_step = 1
    if "signup_phone_number" not in st.session_state:
        st.session_state.signup_phone_number = ""
    if "signup_name" not in st.session_state:
        st.session_state.signup_name = ""
    if "signup_email" not in st.session_state:
        st.session_state.signup_email = ""
    if "signup_password" not in st.session_state:
        st.session_state.signup_password = ""
    if "signup_consent" not in st.session_state:
        st.session_state.signup_consent = False

    if st.session_state.signup_step == 1:
        st.subheader("Step 1: Enter Phone Number")
        with st.form("send_otp_form"):
            phone_number = st.text_input("Phone Number", placeholder="Enter your phone number (e.g., +919876543210)")
            submitted_otp_send = st.form_submit_button("Send OTP", use_container_width=True)

            if submitted_otp_send and phone_number:
                with st.spinner("Sending OTP..."):
                    result = api_client.send_signup_otp(phone_number)
                    if result:
                        st.session_state.signup_phone_number = phone_number
                        st.session_state.signup_step = 2
                        st.success("OTP sent successfully! Please check your phone.")
                        st.rerun()
                    else:
                        st.error("Failed to send OTP. Please try again.")
    
    elif st.session_state.signup_step == 2:
        st.subheader("Step 2: Verify OTP and Complete Registration")
        with st.form("verify_otp_form"):
            col1, col2 = st.columns([1, 1])
            
            with col1:
                st.text_input("Phone Number", value=st.session_state.signup_phone_number, disabled=True)
                otp_code = st.text_input("OTP Code", placeholder="Enter the 6-digit OTP")
                name = st.text_input("Full Name", value=st.session_state.signup_name, placeholder="Enter your full name")
                email = st.text_input("Email", value=st.session_state.signup_email, placeholder="Enter your email address")
                password = st.text_input("Password", type="password", value=st.session_state.signup_password, placeholder="Create a strong password")
                confirm_password = st.text_input("Confirm Password", type="password", placeholder="Confirm your password")
                has_given_consent = st.checkbox("I agree to the terms and conditions", value=st.session_state.signup_consent)
            
            with col2:
                st.markdown("### 🎊 Join Our Festival Community!")
                st.markdown("Help preserve the rich traditions and stories of Indian festivals for future generations.")
                st.markdown("**Key Features:**")
                st.markdown("- 📸 Share festival photos and videos")
                st.markdown("- 📖 Document festival stories and legends")
                st.markdown("- 🎵 Record traditional festival songs")
                st.markdown("- 🏮 Build your festival memory collection")
            
            submitted_otp_verify = st.form_submit_button("Verify OTP & Create Account", use_container_width=True)
            resend_otp_button = st.form_submit_button("Resend OTP", use_container_width=True)

            if submitted_otp_verify:
                if not all([otp_code, name, email, password, confirm_password]):
                    st.error("Please fill in all fields.")
                elif password != confirm_password:
                    st.error("Passwords don't match.")
                elif len(password) < 6:
                    st.error("Password must be at least 6 characters long.")
                elif not has_given_consent:
                    st.error("Please agree to the terms and conditions.")
                else:
                    st.session_state.signup_name = name
                    st.session_state.signup_email = email
                    st.session_state.signup_password = password
                    st.session_state.signup_consent = has_given_consent

                    with st.spinner("Verifying OTP and creating account..."):
                        result = api_client.verify_signup_otp(
                            phone_number=st.session_state.signup_phone_number,
                            otp_code=otp_code,
                            name=name,
                            email=email,
                            password=password,
                            has_given_consent=has_given_consent
                        )
                        if result:
                            st.success("Account created successfully! Please login with your credentials.")
                            st.balloons()
                            st.session_state.signup_step = 1 # Reset for next signup
                            st.session_state.signup_phone_number = ""
                            st.session_state.signup_name = ""
                            st.session_state.signup_email = ""
                            st.session_state.signup_password = ""
                            st.session_state.signup_consent = False
                            st.rerun()
                        else:
                            st.error("OTP verification failed or account creation error. Please check OTP and try again.")
            
            if resend_otp_button:
                with st.spinner("Resending OTP..."):
                    result = api_client.resend_signup_otp(st.session_state.signup_phone_number)
                    if result:
                        st.success("OTP re-sent successfully!")
                    else:
                        st.error("Failed to resend OTP. Please try again.")

def show_main_app(api_client):
    """Show main application after authentication"""
    # Sidebar navigation
    st.sidebar.title("Navigation")
    st.sidebar.markdown(f"**Welcome, {st.session_state.user_data.get('full_name', 'User')}!**")
    
    page = st.sidebar.selectbox(
        "Choose a page",
        ["Home", "Dashboard", "Share Festival Story", "Profile"]
    )
    
    # Logout button
    if st.sidebar.button("Logout", use_container_width=True):
        st.session_state.authenticated = False
        st.session_state.user_data = None
        st.session_state.access_token = None
        st.rerun()
    
    # Route to appropriate page
    if page == "Home":
        show_home_page(api_client)
    elif page == "Dashboard":
        show_dashboard(api_client)
    elif page == "Share Festival Story":
        show_add_content_page(api_client)
    elif page == "Profile":
        show_profile_page(api_client)

def show_home_page(api_client):
    """Show the home page with festival story collector overview content."""
    st.header("🪔 Welcome to Festival Story Collector! (పండుగల కథల సేకరణకు స్వాగతం!)")
    st.markdown("""
    Festival Story Collector (పండుగల కథల సేకరణ) is a community-driven platform dedicated to preserving and celebrating the rich traditions, stories, and memories associated with Indian festivals. In our rapidly changing world, many beautiful festival traditions, family stories, and cultural practices are at risk of being forgotten. This project aims to document these precious memories, making them accessible to current and future generations.

    **Our Mission:**
    *   **Preserve:** Document festival stories, traditions, family customs, and cultural practices.
    *   **Celebrate:** Share the joy and significance of festivals across different regions and communities.
    *   **Connect:** Create a platform where families can share their unique festival experiences and traditions.

    **What you can share here:**
    *   **Festival Stories:** Document the legends, myths, and historical significance of festivals.
    *   **Family Traditions:** Share your family's unique ways of celebrating festivals.
    *   **Memories:** Upload photos, videos, and audio recordings of festival celebrations.
    *   **Recipes:** Traditional festival foods and their preparation methods.
    *   **Songs & Prayers:** Festival songs, bhajans, and traditional prayers.

    Join us in creating a beautiful digital archive of India's festival heritage!
    """)
    
    # Festival categories section
    st.markdown("### 🎊 Festival Categories We Collect")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        **🌾 Harvest Festivals**
        - Makar Sankranti
        - Pongal
        - Baisakhi
        - Onam
        """)
    
    with col2:
        st.markdown("""
        **🪔 Religious Festivals**
        - Diwali
        - Holi
        - Dussehra
        - Janmashtami
        """)
    
    with col3:
        st.markdown("""
        **🌍 Regional Festivals**
        - Durga Puja
        - Ganesh Chaturthi
        - Karva Chauth
        - Local celebrations
        """)
    
    st.markdown("""
    ---
    <div class="telugu-text">
    <p>
    పండుగల కథల సేకరణ అనేది భారతీయ పండుగలతో అనుబంధించబడిన గొప్ప సంప్రదాయాలు, కథలు మరియు జ్ఞాపకాలను పరిరక్షించడానికి మరియు జరుపుకోవడానికి అంకితం చేయబడిన ఒక కమ్యూనిటీ-ఆధారిత వేదిక. మన వేగంగా మారుతున్న ప్రపంచంలో, అనేక అందమైన పండుగ సంప్రదాయాలు, కుటుంబ కథలు మరియు సాంస్కృతిక అభ్యాసాలు మరచిపోయే ప్రమాదం ఉంది. ఈ ప్రాజెక్ట్ ఈ అమూల్యమైన జ్ఞాపకాలను నమోదు చేయడం లక్ష్యంగా పెట్టుకుని, వాటిని ప్రస్తుత మరియు భవిష్యత్తు తరాలకు అందుబాటులోకి తీసుకురావాలని అనుకుంటుంది.

    **మా లక్ష్యం:**
    *   **పరిరక్షించడం:** పండుగ కథలు, సంప్రదాయాలు, కుటుంబ ఆచారాలు మరియు సాంస్కృతిక అభ్యాసాలను నమోదు చేయడం.
    *   **జరుపుకోవడం:** వివిధ ప్రాంతాలు మరియు సంఘాలలో పండుగల ఆనందం మరియు ప్రాముఖ్యతను పంచుకోవడం.
    *   **కనెక్ట్ చేయడం:** కుటుంబాలు వారి ప్రత్యేక పండుగ అనుభవాలు మరియు సంప్రదాయాలను పంచుకోగల వేదికను సృష్టించడం.

    మన అందమైన పండుగల వారసత్వాన్ని కాపాడటంలో మాతో చేరండి!
    </p>
    </div>
    """, unsafe_allow_html=True)

def show_dashboard(api_client):
    """Show dashboard with festival story statistics"""
    st.header("🎊 Festival Stories Dashboard")
    
    # Stats cards
    col1, col2 = st.columns(2)
    
    with col1:
        user_id = st.session_state.user_data.get('id')
        if user_id:
            # Fetch user contributions by media type to get total contributions
            all_user_contributions = []
            media_types = ['text', 'audio', 'image', 'video']
            for media_type in media_types:
                response = api_client.get_user_contributions_by_media(user_id=user_id, media_type=media_type)
                if response and response.get('contributions'):
                    all_user_contributions.extend(response['contributions'])
            
            if all_user_contributions:
                st.metric(
                    "Your Festival Stories",
                    len(all_user_contributions),
                    help="Festival stories you've shared"
                )
            else:
                st.metric("Your Festival Stories", "📖 0", help="You haven't shared any festival stories yet.")
        else:
            st.metric("Your Festival Stories", "📖 N/A", help="Login to see your contributions")
    
    with col2:
        # Community Contributors - still requires roles, so keep as N/A
        st.metric("Community Storytellers", "🔒 N/A", help="Requires 'admin' or 'reviewer' role to view all contributors.")
    
    # Recent activity
    st.subheader("🌟 Your Recent Festival Stories")
    
    with st.spinner("Loading your recent festival stories..."):
        user_id = st.session_state.user_data.get('id')
        if user_id:
            all_recent_contributions = []
            media_types = ['text', 'audio', 'image', 'video']
            for media_type in media_types:
                response = api_client.get_user_contributions_by_media(user_id=user_id, media_type=media_type)
                if response and response.get('contributions'):
                    all_recent_contributions.extend(response['contributions'])
            
            if all_recent_contributions:
                # Sort contributions by timestamp, most recent first. Handle None timestamps.
                all_recent_contributions.sort(key=lambda x: datetime.fromisoformat(x['timestamp'].replace('Z', '+00:00')) if x.get('timestamp') else datetime.min, reverse=True)
                
                st.success(f"Found {len(all_recent_contributions)} of your recent festival stories!")
                for contrib in all_recent_contributions:
                    with st.container():
                        col1, col2 = st.columns([3, 1])
                        with col1:
                            story_title = contrib.get('title', 'Unknown Festival Story')
                            
                            location_data = contrib.get('location', {})
                            location_display = "Not specified"
                            if location_data and location_data.get('latitude') is not None and location_data.get('longitude') is not None:
                                location_display = f"Lat: {location_data['latitude']}, Lon: {location_data['longitude']}"
                            
                            st.markdown(f"**🎊 {story_title}**")
                            st.caption(f"Location: {location_display} | Shared by: {st.session_state.user_data.get('full_name', 'You')}")
                        with col2:
                            st.markdown(f"*{contrib.get('timestamp', 'Recently')}*")
                    st.markdown("---")
            else:
                st.info("No recent festival stories found. Be the first to share a beautiful festival story!")
        else:
            st.info("Login to see your recent festival stories.")

def show_add_content_page(api_client):
    """Show page to add new festival story contribution"""
    st.header("🌟 Share Your Festival Story")
    st.markdown("Help preserve our cultural heritage by sharing beautiful festival traditions and memories!")
    
    with st.form("add_festival_story_form", clear_on_submit=True):
        # Festival Story Information
        st.subheader("🎊 Festival Story Information")
        title = st.text_input("Story Title *", placeholder="Enter a title for your festival story")
        description = st.text_area("Brief Description *", 
                                   placeholder="Provide a brief description of your festival story (minimum 32 characters)", 
                                   height=100)
        content_text = st.text_area("Full Festival Story *",
                                   placeholder="Share your complete festival story, traditions, memories, or experiences...", 
                                   height=200)
        
        # Category
        categories_data = api_client.get_categories()
        category_names = [cat.get('name') for cat in categories_data if cat.get('name')] if categories_data else []
        selected_category_name = st.selectbox("Festival Category *", category_names)
        
        selected_category_id = None
        if categories_data and selected_category_name:
            for cat in categories_data:
                if cat.get('name') == selected_category_name:
                    selected_category_id = cat.get('id')
                    break
        
        if not selected_category_id:
            st.error("Selected category ID not found. Please try again or select a different category.")
            st.stop()

        # Festival-specific details
        st.subheader("🏮 Festival Details")
        col_festival, col_region = st.columns(2)
        with col_festival:
            festival_name = st.text_input("Festival Name", placeholder="e.g., Diwali, Holi, Durga Puja (Optional)")
        with col_region:
            region = st.text_input("Region/State", placeholder="e.g., Andhra Pradesh, West Bengal (Optional)")

        # Location
        st.subheader("📍 Location (Optional)")
        col_lat, col_lon = st.columns(2)
        with col_lat:
            latitude_str = st.text_input("Latitude", placeholder="e.g., 17.3850 (Optional)")
            if latitude_str:
                try:
                    latitude = float(latitude_str)
                except ValueError:
                    st.error("Invalid Latitude. Please enter a number.")
            else:
                latitude = None
        with col_lon:
            longitude_str = st.text_input("Longitude", placeholder="e.g., 78.4867 (Optional)")
            if longitude_str:
                try:
                    longitude = float(longitude_str)
                except ValueError:
                    st.error("Invalid Longitude. Please enter a number.")
            else:
                longitude = None
        
        # Language and Release Rights
        st.subheader("🌐 Language & Rights")
        language_options = ["-- Select a language --", "Telugu", "English", "Hindi", "Other"]
        language = st.selectbox("Select Language *", language_options)
        
        release_rights_options = {
            "This work is created by me and anyone is free to use it.": "creator",
            "This work is created by my family/friends and I took permission to upload their work.": "family_or_friend",
            "I downloaded this from the internet and/or I don't know if it is free to share.": "downloaded"
        }
        selected_release_rights_display = st.radio("Release Rights *", list(release_rights_options.keys()))
        
        # File uploads
        st.subheader("📸 Festival Media (Optional)")
        st.markdown("Upload photos, videos, or audio recordings from your festival celebrations.")
        
        uploaded_files = st.file_uploader(
            "Choose festival media files",
            accept_multiple_files=True,
            type=['png', 'jpg', 'jpeg', 'mp4', 'mov', 'mp3', 'wav', 'pdf']
        )
        
        # Submit button
        submitted = st.form_submit_button("🚀 Share Festival Story", use_container_width=True)
        
        if submitted:
            # Map UI selections to backend enum values
            mapped_release_rights = release_rights_options.get(selected_release_rights_display, "NA")
            
            # Backend expects specific language codes. Map common ones, default to 'NA' or a specific code.
            language_mapping = {
                "Telugu": "telugu",
                "English": "NA",
                "Hindi": "hindi",
                "Other": "NA"
            }
            mapped_language = language_mapping.get(language, "NA")

            # Validation
            if not all([title, description, content_text, selected_category_id, selected_release_rights_display]):
                st.error("Please fill in all required fields marked with *")
            elif language == "-- Select a language --":
                st.error("Please select a valid language.")
            elif len(description) < 32:
                st.error("Brief Description must be at least 32 characters long.")
            elif len(content_text) < 32:
                st.error("Full Festival Story must be at least 32 characters long.")
            else:
                user_id = st.session_state.user_data.get('id')
                if not user_id:
                    st.error("User ID not found. Please ensure you are logged in.")
                    st.stop()

                # Combine all story information into a comprehensive description
                combined_description = f"Festival Story: {title}\n\nBrief Description: {description}\n\nFull Story: {content_text}"
                
                # Add optional details if provided
                if festival_name:
                    combined_description += f"\n\nFestival Name: {festival_name}"
                if region:
                    combined_description += f"\nRegion: {region}"
                
                if len(combined_description) < 32:
                    st.error("The combined festival story content must be at least 32 characters long.")
                else:
                    with st.spinner("Sharing your festival story..."):
                        uploaded_files_info = []
                        uploaded_files_count = 0
                        
                        if uploaded_files:
                            for uploaded_file in uploaded_files:
                                file_bytes = uploaded_file.read()
                                file_size = len(file_bytes)
                                chunk_size = 1024 * 1024 # 1MB chunks
                                total_chunks = (file_size + chunk_size - 1) // chunk_size
                                
                                file_upload_uuid = str(uuid.uuid4())
                                
                                current_file_upload_successful = True
                                last_chunk_result = None
                                
                                for i in range(total_chunks):
                                    chunk = file_bytes[i * chunk_size:(i + 1) * chunk_size]
                                    chunk_result = api_client.upload_file_chunk(
                                        chunk_data=chunk,
                                        filename=uploaded_file.name,
                                        chunk_index=i,
                                        total_chunks=total_chunks,
                                        upload_uuid=file_upload_uuid
                                    )
                                    if not chunk_result:
                                        st.warning(f"Failed to upload chunk {i+1} for {uploaded_file.name}. Aborting upload.")
                                        current_file_upload_successful = False
                                        break
                                    last_chunk_result = chunk_result
                                
                                if current_file_upload_successful:
                                    uploaded_files_info.append({
                                        "name": uploaded_file.name,
                                        "type": uploaded_file.type,
                                        "size": file_size,
                                        "uuid": file_upload_uuid,
                                        "total_chunks": total_chunks
                                    })
                                    uploaded_files_count += 1
                                else:
                                    st.error(f"File upload failed for {uploaded_file.name}.")

                        # Now, finalize records for successfully uploaded files
                        if uploaded_files_info:
                            for file_info in uploaded_files_info:
                                # Determine media_type
                                media_type_full = file_info['type'] if file_info['type'] else "application/octet-stream"
                                if "audio" in media_type_full:
                                    media_type = "audio"
                                elif "video" in media_type_full:
                                    media_type = "video"
                                elif "image" in media_type_full or "pdf" in media_type_full:
                                    media_type = "image"
                                else:
                                    media_type = "text"

                                finalize_result = api_client.finalize_record_upload(
                                    title=title,
                                    description=combined_description,
                                    media_type=media_type,
                                    filename=file_info['name'],
                                    total_chunks=file_info['total_chunks'],
                                    release_rights=mapped_release_rights,
                                    language=mapped_language,
                                    upload_uuid=file_info['uuid'],
                                    user_id=user_id,
                                    category_id=selected_category_id,
                                    latitude=latitude,
                                    longitude=longitude,
                                    use_uid_filename=False
                                )
                                if not finalize_result:
                                    st.warning(f"Failed to finalize record for {file_info['name']}.")
                                    uploaded_files_count -= 1
                            
                            if uploaded_files_count > 0:
                                st.success(f"🎉 {uploaded_files_count} files uploaded and festival story shared successfully! Thank you for preserving our festival heritage!")
                                st.balloons()
                                
                                # Show success summary
                                st.markdown("### 📋 Festival Story Summary")
                                st.markdown(f"**Story Title:** {title}")
                                st.markdown(f"**Festival Category:** {selected_category_name}")
                                if festival_name:
                                    st.markdown(f"**Festival Name:** {festival_name}")
                                if region:
                                    st.markdown(f"**Region:** {region}")
                                st.markdown(f"**Language:** {language}")
                                st.markdown(f"**Media Files:** {uploaded_files_count} files")
                                st.info("Your festival story is now part of our community collection and helps preserve our beautiful cultural heritage!")
                            else:
                                st.error("Failed to upload festival story. Please try again.")
                        else:
                            st.error("No media files were selected for upload or all uploads failed. Please try again.")

def show_profile_page(api_client):
    """Show user profile page"""
    st.header("👤 User Profile")
    
    if st.session_state.user_data:
        user_id = st.session_state.user_data.get('id')
        
        if user_id:
            with st.spinner("Loading user profile..."):
                user = api_client.get_user(user_id=user_id)
                
                if user:
                    col1, col2 = st.columns([1, 2])
                    
                    with col1:
                        st.markdown("### 🌟 Profile Information")
                        st.markdown(f"**Phone:** {user.get('phone', 'N/A')}")
                        st.markdown(f"**Name:** {user.get('name', 'N/A')}")
                        st.markdown(f"**Email:** {user.get('email', 'N/A')}")
                        st.markdown(f"**Gender:** {user.get('gender', 'N/A')}")
                        st.markdown(f"**Date of Birth:** {user.get('date_of_birth', 'N/A')}")
                        st.markdown(f"**Place:** {user.get('place', 'N/A')}")
                        st.markdown(f"**Member Since:** {user.get('created_at', 'Recently')}")
                        st.markdown(f"**Last Login:** {user.get('last_login_at', 'Recently')}")
                    
                    with col2:
                        st.markdown("### 🎊 Your Festival Story Journey")
                        st.info("Festival story statistics and contribution analytics are available through the dashboard. Keep sharing beautiful festival memories to build your storyteller profile!")
                        
                        st.markdown("### 🏮 Storyteller Badge")
                        st.markdown("*Keep sharing festival stories to unlock special badges and recognition in our community!*")
                else:
                    st.error("User profile not found.")
        else:
            st.info("Please log in to view your profile.")
        
        st.markdown("---")
        
        # Profile settings
        st.markdown("### ⚙️ Account Settings")
        
        with st.expander("🔒 Change Password"):
            with st.form("change_password_form"):
                st.text_input("Current Password", type="password")
                new_password = st.text_input("New Password", type="password")
                confirm_new_password = st.text_input("Confirm New Password", type="password")
                
                if st.form_submit_button("Update Password"):
                    if new_password != confirm_new_password:
                        st.error("New passwords don't match!")
                    elif len(new_password) < 6:
                        st.error("Password must be at least 6 characters long!")
                    else:
                        with st.spinner("Changing password..."):
                            change_result = api_client.change_password(st.session_state.access_token, new_password)
                            if change_result:
                                st.success("Password changed successfully!")
                            else:
                                st.error("Failed to change password.")
        
        with st.expander("📧 Update Profile"):
            with st.form("update_profile_form"):
                updated_name = st.text_input("Name", value=user.get('name', ''))
                updated_email = st.text_input("Email", value=user.get('email', ''))
                
                if st.form_submit_button("Update Profile"):
                    if not validate_email(updated_email):
                        st.error("Please enter a valid email address.")
                    else:
                        user_update_data = {
                            "name": updated_name,
                            "email": updated_email
                        }
                        with st.spinner("Updating profile..."):
                            update_result = api_client.update_user(user.get('id'), user_update_data)
                            if update_result:
                                st.session_state.user_data.update(update_result)
                                st.success("Profile updated successfully!")
                                st.rerun()
                            else:
                                st.error("Failed to update profile.")

# Helper functions
def validate_email(email):
    """Simple email validation"""
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def format_file_size(size_bytes):
    """Format file size in human readable format"""
    import math
    if size_bytes == 0:
        return "0B"
    size_names = ["B", "KB", "MB", "GB"]
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return f"{s} {size_names[i]}"

# Run the application
if __name__ == "__main__":
    main()
