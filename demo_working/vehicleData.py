from demo_working.firebase_auth import initialize_firebase  # Import Firebase authentication

# Get database reference
ref = initialize_firebase()

# Set to store already tracked vehicles
tracked_vehicles = set()


def track_vehicle(track_id,cx,cy):
    # Send test data
    data = {"track_id": track_id,  "x:":cx,"y ":cy}


    vehicle_ref = ref.child(str(track_id))
    vehicle_ref.set(data)
    ref.push(data)
    # print("Data sent successfully!")

# Start tracking vehicles
# track_vehicle()
