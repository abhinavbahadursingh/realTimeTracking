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



def calculate_and_store_avg_speed():
    """Calculate the average speed for each track_id and store it in avg_speed.csv."""

    speed_data = defaultdict(list)

    # Read the existing speed logs
    try:
        with open("speed_log.csv", mode="r") as file:
            reader = csv.reader(file)
            for row in reader:
                if len(row) < 2:
                    continue  # Skip empty or malformed rows
                track_id, speed, timestamp = row
                speed_data[track_id].append(float(speed))

        # Calculate average speeds
        avg_speeds = []
        for track_id, speeds in speed_data.items():
            avg_speed = sum(speeds) / len(speeds)  # Compute average
            avg_speeds.append([track_id, round(avg_speed, 2), int(time.time())])  # Corrected this line

        # Store in avg_speed.csv
        with open("avg_speed.csv", mode="w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["track_id", "avg_speed", "timestamp"])  # Write header
            writer.writerows(avg_speeds)

        # print("Average speed calculations stored in avg_speed.csv")

    except FileNotFoundError:
        print("No speed log file found. Make sure speed_log.csv exists.")



def run_periodic_update(interval=5):
    """Runs push_avg_speed_to_firebase every `interval` seconds."""
    while True:
        push_avg_speed_to_firebase()  # Push avg speed to Firebase
        time.sleep(interval)  # Wait for the specified interval (e.g., 5 seconds)

# Call this function to start periodic updates
def push_avg_speed_to_firebase():

    calculate_and_store_avg_speed()
    try:
        with open("avg_speed.csv", mode="r") as file:
            reader = csv.reader(file)
            next(reader)  # Skip header
            for row in reader:
                if len(row) < 3:
                    continue  # Skip malformed rows
                track_id, avg_speed, timestamp = row
                track_ref = ref.child("speed_Data").child("average_speed").child(str(track_id))
                track_ref.set({
                    "speed": float(avg_speed),

                })
                # print(f"Updated avg speed for track_id {track_id}: {avg_speed} km/h at {timestamp}")

    except FileNotFoundError:
        print("Error: avg_speed.csv not found.")


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
