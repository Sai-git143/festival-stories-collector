import requests
import streamlit as st
from typing import Optional, Dict, List
from config.settings import settings
import uuid # Import uuid for generating unique IDs

class SwechaAPIClient:
    def __init__(self):
        self.base_url = settings.API_BASE_URL
        self.session = requests.Session()
        self.session.timeout = 30  # 30 seconds timeout
        
    def set_auth_token(self, token: str):
        """Set authentication token for API requests"""
        self.session.headers.update({
            "Authorization": f"Bearer {token}",
        })
    
    def _handle_response(self, response: requests.Response) -> Optional[Dict]:
        """Handle API response and errors"""
        try:
            if response.status_code in [200, 201]:
                return response.json()
            elif response.status_code == 401:
                st.error("Authentication failed. Please login again.")
                st.session_state.authenticated = False
                return None
            elif response.status_code == 422:
                try:
                    error_detail = response.json().get('detail', 'Validation error')
                    st.error(f"Validation error: {error_detail}. Full response: {response.text}") # Log full response text
                except ValueError:
                    st.error(f"Validation error: Could not parse error detail. Full response: {response.text}")
                return None
            else:
                st.error(f"API Error ({response.status_code}): {response.text}")
                return None
        except Exception as e:
            st.error(f"Error processing response: {str(e)}")
            return None
    
    def login_for_access_token(self, phone_number: str, password: str) -> Optional[Dict]:
        """Login user and get access token (POST /api/v1/auth/login)"""
        try:
            data = {
                "phone": phone_number,
                "password": password
            }
            response = self.session.post(
                f"{self.base_url}/api/v1/auth/login",
                json=data,
                headers={"Content-Type": "application/json"}
            )
            return self._handle_response(response)
        except requests.RequestException as e:
            st.error(f"Network error during login: {str(e)}")
            return None

    def read_users_me(self) -> Optional[Dict]:
        """Read Users Me (GET /api/v1/auth/me)"""
        try:
            response = self.session.get(f"{self.base_url}/api/v1/auth/me")
            return self._handle_response(response)
        except requests.RequestException as e:
            st.error(f"Error fetching user profile: {str(e)}")
            return None

    def change_password(self, current_password: str, new_password: str) -> Optional[Dict]:
        """Change Password (POST /api/v1/auth/change-password)"""
        try:
            data = {
                "current_password": current_password,
                "new_password": new_password
            }
            response = self.session.post(
                f"{self.base_url}/api/v1/auth/change-password",
                json=data,
                headers={"Content-Type": "application/json"}
            )
            return self._handle_response(response)
        except requests.RequestException as e:
            st.error(f"Network error during password change: {str(e)}")
            return None

    def send_signup_otp(self, phone_number: str) -> Optional[Dict]:
        """Send Signup OTP (POST /api/v1/auth/signup/send-otp)"""
        try:
            data = {"phone_number": phone_number}
            response = self.session.post(
                f"{self.base_url}/api/v1/auth/signup/send-otp",
                json=data,
                headers={"Content-Type": "application/json"}
            )
            return self._handle_response(response)
        except requests.RequestException as e:
            st.error(f"Network error during OTP send: {str(e)}")
            return None

    def verify_signup_otp(self, phone_number: str, otp_code: str, name: str, email: str, password: str, has_given_consent: bool) -> Optional[Dict]:
        """Verify Signup OTP (POST /api/v1/auth/signup/verify-otp)"""
        try:
            data = {
                "phone_number": phone_number,
                "otp_code": otp_code,
                "name": name,
                "email": email,
                "password": password,
                "has_given_consent": has_given_consent
            }
            response = self.session.post(
                f"{self.base_url}/api/v1/auth/signup/verify-otp",
                json=data,
                headers={"Content-Type": "application/json"}
            )
            return self._handle_response(response)
        except requests.RequestException as e:
            st.error(f"Network error during OTP verification: {str(e)}")
            return None

    def resend_signup_otp(self, phone_number: str) -> Optional[Dict]:
        """Resend Signup OTP (POST /api/v1/auth/signup/resend-otp)"""
        try:
            data = {"phone_number": phone_number}
            response = self.session.post(
                f"{self.base_url}/api/v1/auth/signup/resend-otp",
                json=data,
                headers={"Content-Type": "application/json"}
            )
            return self._handle_response(response)
        except requests.RequestException as e:
            st.error(f"Network error during OTP resend: {str(e)}")
            return None

    def create_user(self, user_data: Dict) -> Optional[Dict]:
        """Create new user account (POST /api/v1/users/)"""
        # This method is kept for now, but will be replaced by OTP flow in app.py
        # It might still be used by other parts of the system or for admin purposes.
        try:
            response = self.session.post(
                f"{self.base_url}/api/v1/users/",
                json=user_data,
                headers={"Content-Type": "application/json"}
            )
            return self._handle_response(response)
        except requests.RequestException as e:
            st.error(f"Network error during user creation: {str(e)}")
            return None

    def upload_file_chunk(self, chunk_data: bytes, filename: str, chunk_index: int, total_chunks: int, upload_uuid: str) -> Optional[Dict]:
        """Upload a single chunk of a file (POST /api/v1/records/upload/chunk)"""
        try:
            files = {"chunk": (filename, chunk_data, "application/octet-stream")}
            data = {
                "filename": filename,
                "chunk_index": chunk_index,
                "total_chunks": total_chunks,
                "upload_uuid": upload_uuid
            }
            headers = {k: v for k, v in self.session.headers.items()
                      if k.lower() != "content-type"}

            response = self.session.post(
                f"{self.base_url}/api/v1/records/upload/chunk",
                files=files,
                data=data,
                headers=headers
            )
            response_data = self._handle_response(response)
            if response_data:
                st.info(f"Chunk upload response: {response_data}") # Log the response
            return response_data
        except requests.RequestException as e:
            st.error(f"File chunk upload error: {str(e)}")
            return None

    def finalize_record_upload(self, title: str, description: str, media_type: str, filename: str, total_chunks: int, release_rights: str, language: str, upload_uuid: str, user_id: str, category_id: str, latitude: Optional[float] = None, longitude: Optional[float] = None, use_uid_filename: Optional[bool] = None) -> Optional[Dict]:
        """Finalize chunked upload and create a record (POST /api/v1/records/upload)"""
        try:
            data = {
                "title": title,
                "description": description,
                "media_type": media_type,
                "filename": filename,
                "total_chunks": total_chunks,
                "release_rights": release_rights,
                "language": language,
                "upload_uuid": upload_uuid,
                "user_id": user_id,
                "category_id": category_id,
            }
            if latitude is not None:
                data["latitude"] = latitude
            if longitude is not None:
                data["longitude"] = longitude
            if use_uid_filename is not None:
                data["use_uid_filename"] = use_uid_filename

            st.info(f"Finalizing record with data: {data}") # Added logging for data being sent

            # Remove explicit Content-Type header, let requests handle it for form-encoded data
            headers = {}
            if "Authorization" in self.session.headers:
                headers["Authorization"] = self.session.headers["Authorization"]

            response = self.session.post(
                f"{self.base_url}/api/v1/records/upload",
                data=data, # Send data as form-encoded
                headers=headers
            )
            return self._handle_response(response)
        except requests.RequestException as e:
            st.error(f"Record finalization error: {str(e)}")
            return None

    def get_user_contributions_by_media(self, user_id: str, media_type: str) -> Optional[List[Dict]]:
        """Get User Contributions By Media (GET /api/v1/users/{user_id}/contributions/{media_type})"""
        try:
            response = self.session.get(f"{self.base_url}/api/v1/users/{user_id}/contributions/{media_type}")
            return self._handle_response(response)
        except requests.RequestException as e:
            st.error(f"Network error fetching user contributions by media type: {str(e)}")
            return None

    def get_categories(self) -> Optional[List[Dict]]:
        """Get Categories (GET /api/v1/categories/)"""
        try:
            response = self.session.get(f"{self.base_url}/api/v1/categories/")
            return self._handle_response(response)
        except requests.RequestException as e:
            st.error(f"Network error fetching categories: {str(e)}")
            return None

    def get_users(self, skip: int = 0, limit: int = 20) -> Optional[List[Dict]]:
        """Get Users (GET /api/v1/users/)"""
        try:
            params = {"skip": skip, "limit": limit}
            response = self.session.get(f"{self.base_url}/api/v1/users/", params=params)
            return self._handle_response(response)
        except requests.RequestException as e:
            st.error(f"Network error fetching users: {str(e)}")
            return None

    def get_user(self, user_id: str) -> Optional[Dict]:
        """Get User (GET /api/v1/users/{user_id})"""
        try:
            response = self.session.get(f"{self.base_url}/api/v1/users/{user_id}")
            return self._handle_response(response)
        except requests.RequestException as e:
            st.error(f"Network error fetching user: {str(e)}")
            return None

    def update_user(self, user_id: str, user_data: Dict) -> Optional[Dict]:
        """Update User (PUT /api/v1/users/{user_id})"""
        try:
            response = self.session.put(
                f"{self.base_url}/api/v1/users/{user_id}",
                json=user_data,
                headers={"Content-Type": "application/json"}
            )
            return self._handle_response(response)
        except requests.RequestException as e:
            st.error(f"Network error updating user: {str(e)}")
            return None
