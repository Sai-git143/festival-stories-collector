import re
import streamlit as st
from typing import List, Dict, Any
import math
from datetime import datetime

def validate_email(email: str) -> bool:
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def validate_password(password: str) -> tuple[bool, str]:
    """Validate password strength"""
    if len(password) < 6:
        return False, "Password must be at least 6 characters long"
    if not re.search(r'[A-Za-z]', password):
        return False, "Password must contain at least one letter"
    if not re.search(r'[0-9]', password):
        return False, "Password must contain at least one number"
    return True, "Password is valid"

def format_file_size(size_bytes: int) -> str:
    """Format file size in human readable format"""
    if size_bytes == 0:
        return "0B"
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return f"{s} {size_names[i]}"

def sanitize_input(text: str) -> str:
    """Basic input sanitization"""
    if not text:
        return ""
    # Remove potential harmful characters
    sanitized = re.sub(r'[<>"\']', '', text.strip())
    return sanitized

def format_datetime(datetime_str: str) -> str:
    """Format datetime string for display"""
    try:
        dt = datetime.fromisoformat(datetime_str.replace('Z', '+00:00'))
        return dt.strftime("%B %d, %Y at %I:%M %p")
    except:  # noqa: E722
        return datetime_str

def filter_contributions(contributions: List[Dict], filters: Dict[str, Any]) -> List[Dict]:
    """Filter contributions based on criteria"""
    if not contributions:
        return []
    
    filtered = contributions.copy()
    
    # Filter by region
    if filters.get('region') and filters['region'] != "All Regions":
        filtered = [c for c in filtered 
                   if c.get('metadata', {}).get('region') == filters['region']]
    
    # Filter by category
    if filters.get('category') and filters['category'] != "All Categories":
        filtered = [c for c in filtered 
                   if c.get('metadata', {}).get('category') == filters['category']]
    
    # Filter by search term
    if filters.get('search_term'):
        search_lower = filters['search_term'].lower()
        filtered = [c for c in filtered if (
            search_lower in c.get('metadata', {}).get('game_name', '').lower() or
            search_lower in c.get('metadata', {}).get('description', '').lower() or
            search_lower in c.get('metadata', {}).get('rules', '').lower()
        )]
    
    return filtered

def create_download_link(data: str, filename: str, text: str) -> str:
    """Create download link for data"""
    import base64
    b64 = base64.b64encode(data.encode()).decode()
    return f'<a href="data:file/txt;base64,{b64}" download="{filename}">{text}</a>'

def show_success_message(message: str, icon: str = "🎉"):
    """Show styled success message"""
    st.markdown(f"""
    <div class="success-box">
        {icon} {message}
    </div>
    """, unsafe_allow_html=True)

def show_error_message(message: str, icon: str = "❌"):
    """Show styled error message"""
    st.markdown(f"""
    <div class="error-box">
        {icon} {message}
    </div>
    """, unsafe_allow_html=True)

def generate_game_stats(contributions: List[Dict]) -> Dict[str, Any]:
    """Generate statistics from contributions"""
    if not contributions:
        return {}
    
    stats = {
        'total_games': len(contributions),
        'regions': len(set(c.get('metadata', {}).get('region', 'Unknown') 
                          for c in contributions)),
        'categories': len(set(c.get('metadata', {}).get('category', 'Unknown') 
                             for c in contributions)),
        'with_files': sum(1 for c in contributions if c.get('file_ids')),
        'top_regions': {},
        'top_categories': {}
    }
    
    # Calculate top regions and categories
    regions = [c.get('metadata', {}).get('region', 'Unknown') for c in contributions]
    categories = [c.get('metadata', {}).get('category', 'Unknown') for c in contributions]
    
    from collections import Counter
    stats['top_regions'] = dict(Counter(regions).most_common(5))
    stats['top_categories'] = dict(Counter(categories).most_common(5))
    
    return stats

def validate_file_upload(uploaded_file, max_size_mb: int = 10) -> tuple[bool, str]:
    """Validate uploaded file"""
    if not uploaded_file:
        return True, "No file uploaded"
    
    # Check file size
    if uploaded_file.size > max_size_mb * 1024 * 1024:
        return False, f"File size exceeds {max_size_mb}MB limit"
    
    # Check file extension
    allowed_extensions = ['png', 'jpg', 'jpeg', 'gif', 'mp4', 'mov', 'avi', 'mp3', 'wav', 'pdf']
    file_extension = uploaded_file.name.split('.')[-1].lower()
    
    if file_extension not in allowed_extensions:
        return False, f"File type '{file_extension}' not supported"
    
    return True, "File is valid"