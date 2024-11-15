import json
import threading
import time
from datetime import datetime
import websocket
import colorama

colorama.init(autoreset=True)
GREEN = colorama.Fore.GREEN
RED = colorama.Fore.RED
RESET = colorama.Fore.RESET

class WebSocketConnector:
    def __init__(self, local_storage_manager, countdown_manager):
        self.socket = None
        self.ping_interval = None
        self.retry_delay = 1
        self.local_storage_manager = local_storage_manager
        self.countdown_manager = countdown_manager

    def connect(self, user_id, proxy=None):
        if self.socket:
            return
        version = "v0.2"
        url = "wss://secure.ws.teneo.pro"
        ws_url = f"{url}/websocket?userId={user_id}&version={version}"

        options = {}
        if proxy:
            options['http_proxy'] = proxy

        self.socket = websocket.WebSocketApp(ws_url, **options)

        self.socket.on_open = self.on_open
        self.socket.on_message = self.on_message
        self.socket.on_close = self.on_close
        self.socket.on_error = self.on_error
        
        try:
            threading.Thread(target=self.socket.run_forever).start()
        except Exception as e:
            print(f"Error during connect: {e}")

    def disconnect(self):
        if self.socket:
            self.socket.close()
            self.socket = None
            self.stop_pinging()

    def on_open(self, ws):
        connection_time = datetime.now().isoformat()
        self.local_storage_manager.set_local_storage({'lastUpdated': connection_time})
        print("WebSocket connected at", connection_time)
        self.start_pinging()
        self.countdown_manager.start_countdown_and_points()

    def on_message(self, ws, message):
        data = json.loads(message)
        print(GREEN + "Received message from WebSocket:", str(data) + RESET)
        if 'pointsTotal' in data and 'pointsToday' in data:
            last_updated = datetime.now().isoformat()
            self.local_storage_manager.set_local_storage({
                'lastUpdated': last_updated,
                'pointsTotal': data['pointsTotal'],
                'pointsToday': data['pointsToday'],
            })
            self.countdown_manager.points_total = data['pointsTotal']
            self.countdown_manager.points_today = data['pointsToday']

    def on_close(self, ws, close_status_code, close_msg):
        try:
            self.socket = None
            print(f"WebSocket disconnected with code: {close_status_code}, reason: {close_msg}")
            self.stop_pinging()
            time.sleep(self.retry_delay)
            self.retry_delay = min(self.retry_delay * 2, 30)
            self.connect_web_socket()  # Assume user_id and proxy are stored in TeneoNodeCLI
        except Exception as e:
            print(f"Error during on_close: {e}")
            self.retry_delay = 1  # Reset the retry delay in case of error

    def on_error(self, ws, error):
        print("WebSocket error:", error)
        try:
            time.sleep(5)
            self.socket = None
            self.connect_web_socket()
        except:
            print(f"Error...")


    def start_pinging(self):
        self.stop_pinging()
        self.ping_interval = threading.Timer(10, self.ping)
        self.ping_interval.start()

    def stop_pinging(self):
        if self.ping_interval:
            self.ping_interval.cancel()
            self.ping_interval = None

    def ping(self):
        if self.socket and self.socket.sock is not None and self.socket.sock.connected:
            self.socket.send(json.dumps({'type': 'PING'}))
            self.local_storage_manager.set_local_storage({'lastPingDate': datetime.now().isoformat()})
        else:
            print(RED + "Failed to send PING to WebSocket" + RESET)
        self.start_pinging()

