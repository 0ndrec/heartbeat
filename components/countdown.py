import json
import os
import random
import threading
from datetime import datetime, timedelta
from components.storage import LocalStorageManager

class CountdownManager:
    def __init__(self):
        self.countdown_interval = None
        self.potential_points = 0
        self.countdown = "Calculating..."
        self.points_total = 0
        self.points_today = 0

    def start_countdown_and_points(self):
        self.stop_countdown_and_points()
        self.update_countdown_and_points()
        self.countdown_interval = threading.Timer(1, self.start_countdown_and_points)
        self.countdown_interval.start()

    def stop_countdown_and_points(self):
        if self.countdown_interval:
            self.countdown_interval.cancel()
            self.countdown_interval = None

    def update_countdown_and_points(self):
        local_storage = LocalStorageManager.get_local_storage()
        last_updated = local_storage.get('lastUpdated')
        if last_updated:
            next_heartbeat = datetime.fromisoformat(last_updated) + timedelta(minutes=15)
            now = datetime.now()
            diff = next_heartbeat - now


            if diff.total_seconds() > 0:
                minutes = diff.total_seconds() // 60
                seconds = diff.total_seconds() % 60
                self.countdown = f"{int(minutes)}m {int(seconds)}s"

                max_points = 25
                time_elapsed = now - datetime.fromisoformat(last_updated)
                time_elapsed_minutes = time_elapsed.total_seconds() / 60
                new_points = min(max_points, (time_elapsed_minutes / 15) * max_points)
                new_points = round(new_points, 2)

                if random.random() < 0.1:
                    bonus = random.random() * 2
                    new_points = min(max_points, new_points + bonus)
                    new_points = round(new_points, 2)

                self.potential_points = new_points
            else:
                self.countdown = "Calculating..."
                self.potential_points = 25
        else:
            self.countdown = "Calculating..."
            self.potential_points = 0

        LocalStorageManager.set_local_storage({'potentialPoints': self.potential_points, 'countdown': self.countdown})
