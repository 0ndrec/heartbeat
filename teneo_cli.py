import os
import json
import re
import colorama
import multiprocessing
from components.imapwatcher import IMAPWatcher
from components.storage import LocalStorageManager
from components.countdown import CountdownManager
from components.acc import UserManager
from components.wsocket import WebSocketConnector


colorama.init(autoreset=True)
GREEN = colorama.Fore.GREEN
RED = colorama.Fore.RED
RESET = colorama.Fore.RESET


SUPABASE_BEAREBER = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imlra25uZ3JneHV4Z2pocGxicGV5Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3MjU0MzgxNTAsImV4cCI6MjA0MTAxNDE1MH0.DRAvf8nH1ojnJBc3rD_Nw6t1AV8X_g6gmY_HByG2Mag"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imlra25uZ3JneHV4Z2pocGxicGV5Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3MjU0MzgxNTAsImV4cCI6MjA0MTAxNDE1MH0.DRAvf8nH1ojnJBc3rD_Nw6t1AV8X_g6gmY_HByG2Mag"

#Find accounts.list in current directory
current_dir = os.path.dirname(os.path.abspath(__file__))
list_file = os.path.join(current_dir, "accounts.list")

def accounts_list(list_file) -> dict:
    data_dict = {}
    with open(list_file, "r") as file:
        for line in file:
            email, password = line.strip().split(":")
            data_dict[email] = password
    return data_dict


def handle_user_input():
    use_proxy = input("Do you want to use a proxy? (y/n): ").lower() == 'y'
    proxy = input("Please enter your proxy URL (e.g., http://username:password@host:port): ") if use_proxy else None
    return proxy

def handle_user_menu(user_id, proxy, local_storage_manager, countdown_manager, websocket_connector, user_manager):
    if not user_id:
        option = input("User ID not found. Would you like to:\n1. Register an account\n2. Login to your account\n3. Enter User ID manually\n4. Register an from list\n5. Approval emails\n6. Run from list\nChoose an option: ")
        if option == '1':
            user_manager.register_user()
        elif option == '2':
            email = input("Enter your email: ")
            password = input("Enter your password: ")
            user_manager.get_user_id(proxy, email, password)
        elif option == '3':
            user_id = input("Please enter your user ID: ")
            local_storage_manager.set_local_storage({'userId': user_id})
            countdown_manager.start_countdown_and_points()
            websocket_connector.connect(user_id, proxy)
        elif option == '4':
            accounts = accounts_list(list_file)
            for email, password in accounts.items():
                try:
                    response = user_manager.register_user(email, password)
                    json_data = response.json()
                    print(f"Created, User ID: {json_data['id']}")
                except Exception as e:
                    print(f"Error registering user with email {email}: {e}")
        # Process approval email sended code
        elif option == '5':
            accounts = accounts_list(list_file)
            for email, password in accounts.items():
                print(f'Checking email: {email}')
                wathcher = IMAPWatcher(email, password, "imap.gmail.com", 993, "nreply@noreply.teneo.pro") #Only for gmail using
                try:
                    wathcher.connect()
                    mailbody = wathcher.get_latest_email()
                    # Find a link who start from "https://eu-west-1.resend-clicks.com"
                    link = re.findall(r'https://eu-west-1.resend-clicks.com/.*', str(mailbody))
                    # extract the link
                    link = link[0].split()[0]
                    print(f"Please click the link for confirmation: {link}")
                except Exception as e:
                    print(f"Error registering user with email {email}: {e}")
        elif option == '6':
            accounts = accounts_list(list_file)
            # Create a new multiprocessing pool
            pool = multiprocessing.Pool()
            # Process each account in parallel
            for email, password in accounts.items():
                try:
                    user_id = user_manager.get_user_id(proxy, email, password)
                    if user_id is not None:
                        pool.apply_async(countdown_manager.start_countdown_and_points)
                        pool.apply_async(websocket_connector.connect, args=(user_id, proxy))
                        print(f"Started countdown and points for user ID: {user_id}")
                except Exception as e:
                    print(f"Error with email {email}: {e}")
            pool.close()
            if pool._state == 'CLOSE':
                pool.join()

    else:
        option = input("Menu:\n1. Logout\n2. Start Running Node\nChoose an option: ")
        if option == '1':
            if os.path.exists('localStorage.json'):
                os.remove('localStorage.json')
            print('Logged out successfully.')
        elif option == '2':
            countdown_manager.start_countdown_and_points() # Start the countdown
            websocket_connector.connect(user_id, proxy) # Connect to the WebSocket


def main():
    print('\n')
    print("Running Teneo Node BETA CLI Version by" + RED + " @Ebunki Uzlov" + RESET)
    local_storage_manager = LocalStorageManager
    try:
        local_storage_data = local_storage_manager.get_local_storage()
        user_id = local_storage_data.get('userId')
    except FileNotFoundError:
        print("localStorage.json not found. Please login to your account first.")
        return
    except json.JSONDecodeError:
        print("localStorage.json is corrupted. Please delete it and try again.")
        return

    try:
        proxy = handle_user_input()
    except KeyboardInterrupt:
        print("\nExiting...")
        return

    try:
        countdown_manager = CountdownManager()
    except Exception as e:
        print(f"An error occurred while initializing the countdown manager: {e}")
        return
    
    websocket_connector = WebSocketConnector(local_storage_manager, countdown_manager)
    user_manager = UserManager(SUPABASE_BEAREBER, SUPABASE_KEY)
    handle_user_menu(user_id, proxy, local_storage_manager, countdown_manager, websocket_connector, user_manager)

if __name__ == "__main__":
    main()

