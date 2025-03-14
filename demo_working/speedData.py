from demo_working.firebase_auth import initialize_firebase  # Import Firebase authentication
import time
# Get database reference
ref = initialize_firebase()

# Set to store already tracked vehicles
tracked_vehicles = set()


def log_speed(track_id, speed):
    """
    Logs speed as a separate entry under /speedData/{track_id} with a unique key
    """
    speed_ref = ref.child("speedData").child(str(track_id)).push()
    speed_ref.set({
        "speed": speed,
        "timestamp": int(time.time())  # Unix timestamp for tracking time
    })
    # print(f"Speed logged for track ID {track_id}: {speed} km/h")