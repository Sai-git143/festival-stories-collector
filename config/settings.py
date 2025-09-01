# settings.py - Configuration for Festival Story Collector (పండుగల కథల సేకరణ)

import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    # API Configuration
    API_BASE_URL = os.getenv("API_BASE_URL", "https://api.corpus.swecha.org")
    API_KEY = os.getenv("SWECHA_API_KEY")
    
    # App Configuration
    APP_NAME = os.getenv("APP_NAME", "పండుగల కథల సేకరణ - Festival Story Collector")
    APP_VERSION = os.getenv("APP_VERSION", "1.0.0")
    DEBUG = os.getenv("DEBUG", "False").lower() == "true"
    
    # File Upload Configuration
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    ALLOWED_EXTENSIONS = ['png', 'jpg', 'jpeg', 'gif', 'mp4', 'mov', 'avi', 'mp3', 'wav', 'pdf']
    
    # Pagination
    DEFAULT_PAGE_SIZE = 20
    MAX_PAGE_SIZE = 100
    
    # Regional Configuration for Festival Stories
    INDIAN_STATES = [
        "Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar", "Chhattisgarh",
        "Goa", "Gujarat", "Haryana", "Himachal Pradesh", "Jharkhand", "Karnataka",
        "Kerala", "Madhya Pradesh", "Maharashtra", "Manipur", "Meghalaya", "Mizoram",
        "Nagaland", "Odisha", "Punjab", "Rajasthan", "Sikkim", "Tamil Nadu",
        "Telangana", "Tripura", "Uttar Pradesh", "Uttarakhand", "West Bengal"
    ]
    
    # Festival Categories for Story Collection
    FESTIVAL_CATEGORIES = [
        "Religious Festivals",
        "Harvest Festivals", 
        "Seasonal Celebrations",
        "Regional Festivals",
        "Family Traditions",
        "Community Festivals",
        "Cultural Events",
        "Ritual Ceremonies",
        "Folk Celebrations",
        "Modern Adaptations",
        "Festival Foods & Recipes",
        "Festival Songs & Music"
    ]
    
    # Types of Festival Content
    CONTENT_TYPES = [
        "Festival Stories & Legends",
        "Family Traditions & Customs", 
        "Personal Memories",
        "Historical Accounts",
        "Regional Variations",
        "Festival Preparations",
        "Traditional Recipes",
        "Songs & Prayers",
        "Ritual Procedures",
        "Cultural Significance"
    ]
    
    # Festival Story Media Types
    MEDIA_CATEGORIES = {
        "image": ["Festival Photos", "Traditional Art", "Decorations", "Food Images"],
        "video": ["Celebration Videos", "Ritual Recordings", "Dance Performances"],
        "audio": ["Festival Songs", "Prayers & Chants", "Story Narrations"],
        "text": ["Written Stories", "Recipe Instructions", "Historical Accounts"]
    }
    
    # Popular Indian Festivals
    MAJOR_FESTIVALS = [
        # Religious Festivals
        "Diwali (Deepavali)",
        "Holi",
        "Dussehra (Vijayadashami)",
        "Navratri",
        "Janmashtami",
        "Ram Navami",
        "Maha Shivratri",
        "Karva Chauth",
        "Raksha Bandhan",
        
        # Regional Festivals
        "Durga Puja (Bengal)",
        "Ganesh Chaturthi (Maharashtra)",
        "Onam (Kerala)",
        "Pongal (Tamil Nadu)",
        "Ugadi (Andhra Pradesh/Telangana)",
        "Baisakhi (Punjab)",
        "Poila Boishakh (Bengal)",
        "Gudi Padwa (Maharashtra)",
        
        # Harvest Festivals
        "Makar Sankranti",
        "Lohri",
        "Bhogali Bihu (Assam)",
        "Wangala (Meghalaya)",
        
        # Seasonal & Cultural
        "Teej",
        "Kumbh Mela",
        "Eid Celebrations",
        "Christmas Traditions",
        "Local Folk Festivals"
    ]
    
    # Languages for Festival Stories
    STORY_LANGUAGES = [
        "Telugu", "Hindi", "English", "Tamil", "Bengali", "Marathi", 
        "Gujarati", "Kannada", "Malayalam", "Punjabi", "Oriya",
        "Assamese", "Urdu", "Sanskrit", "Other Regional Languages"
    ]
    
    # Story Collection Themes
    STORY_THEMES = [
        "Childhood Festival Memories",
        "Family Traditions Passed Down",
        "Regional Festival Variations", 
        "Festival Food & Recipes",
        "Traditional Songs & Music",
        "Decorations & Preparations",
        "Religious Significance",
        "Community Celebrations",
        "Modern Adaptations",
        "Lost Traditions"
    ]

settings = Settings()
