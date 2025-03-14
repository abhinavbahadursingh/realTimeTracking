import csv
from collections import defaultdict
from demo_working.firebase_auth import initialize_firebase  # Import Firebase authentication
import time
# Get database reference
ref = initialize_firebase()

# Set to store already tracked vehicles
tracked_vehicles = set()

def log_speed_to_csv(track_id, speed):
    """Append speed data to a CSV file for calculating the average later."""
    with open("speed_log.csv", mode="a", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([track_id, speed, int(time.time())])  # Store with timestamp

 g

def calculate_and_update_avg_speed():
    """Calculates the average speed of each track_id and updates Firebase."""
    speeds = defaultdict(list)

    try:
        with open("speed_log.csv", mode="r") as file:
            reader = csv.reader(file)
            for row in reader:
                track_id, speed, timestamp = row
                speeds[track_id].append(float(speed))

        # Store all speeds separately and update the average
        for track_id, speed_list in speeds.items():
            track_ref = ref.child("speed_Data").child("avg_Speed")  # Reference to track_id under speedData

            # Push each recorded speed with a unique key (avoiding overwriting)
            for idx, speed in enumerate(speed_list):
                track_ref.child(f"speed_{idx+1}").set(speed)

            # Update the average speed separately
            avg_speed = sum(speed_list) / len(speed_list)
            track_ref.child("average_speed").set(avg_speed)



    except FileNotFoundError:
        print("No speed data available yet.")


def log_speed(track_id, speed):

    speed_ref = ref.child("speed_Data").child("real_Time_Speed").child(str(track_id))

    # Get the current count from Firebase
    count_ref = speed_ref.child("count")
    count_snapshot = count_ref.get()

    if count_snapshot is None:
        count = 1  # Initialize count if it doesn't exist
    else:
        count = count_snapshot + 1  # Increment count

    # Store speed with unique key
    speed_ref.child(f"time{count}").set({"speed": speed})

    # Update the count for the next entry
    count_ref.set(count)
