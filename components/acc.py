import requests
from getpass import getpass
from components.storage import LocalStorageManager
from components.countdown import CountdownManager
from components.wsocket import WebSocketConnector

SUPABASE_URL = "https://ikknngrgxuxgjhplbpey.supabase.co"
SUPABASE_BEAREBER = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imlra25uZ3JneHV4Z2pocGxicGV5Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3MjU0MzgxNTAsImV4cCI6MjA0MTAxNDE1MH0.DRAvf8nH1ojnJBc3rD_Nw6t1AV8X_g6gmY_HByG2Mag"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imlra25uZ3JneHV4Z2pocGxicGV5Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3MjU0MzgxNTAsImV4cCI6MjA0MTAxNDE1MH0.DRAvf8nH1ojnJBc3rD_Nw6t1AV8X_g6gmY_HByG2Mag"

class UserManager:
    def __init__(self, authorization, apikey):
        self.authorization = authorization
        self.apikey = apikey

    def get_user_id(self, proxy=None, email=None, password=None):
        login_url = f"{SUPABASE_URL}/auth/v1/token?grant_type=password"
        try:
            response = requests.post(login_url, json={
                'email': email,
                'password': password
            }, headers={
                'Authorization': self.authorization,
                'apikey': self.apikey
            })

            response.raise_for_status()
            user_id = response.json()['user']['id']
            print('User ID:', user_id)

            profile_url = f"{SUPABASE_URL}/rest/v1/profiles?select=personal_code&id=eq.{user_id}"
            profile_response = requests.get(profile_url, headers={
                'Authorization': self.authorization,
                'apikey': self.apikey
            })

            profile_response.raise_for_status()
            print('Profile Data:', profile_response.json())
            LocalStorageManager.set_local_storage({'userId': user_id})
            CountdownManager().start_countdown_and_points()
            WebSocketConnector(LocalStorageManager, CountdownManager()).connect(user_id, proxy)
        except requests.exceptions.RequestException as e:
            print('Error:', e)

    def register_user(self, email=None, password=None):
        signup_url = f"{SUPABASE_URL}/auth/v1/signup"

        if email is None or password is None:
            email = input("Enter your email: ")
            password = getpass("Enter your password: ")


        try:
            response = requests.post(signup_url, json={
                'email': email,
                'password': password,
                'data': {'invited_by': "teL7Y"},
                'gotrue_meta_security': {},
                'code_challenge': None,
                'code_challenge_method': None
            }, headers={
                'Authorization': self.authorization,
                'apikey': self.apikey
            })

            response.raise_for_status()
            print('Registration... Please confirm your email at:', email)
            return response
        except requests.exceptions.RequestException as e:
            print('Error during registration:', e)
