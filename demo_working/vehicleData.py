from demo_working.firebase_auth import initialize_firebase  # Import Firebase authentication

# Get database reference
ref = initialize_firebase()

# Set to store already tracked vehicles
tracked_vehicles = set()


def track_vehicle(track_id,cx,cy):
    # Send test data
    data = {"track_id": track_id,  "x:":cx,"y ":cy}

    vechle_data=ref.child("vehicle_Data")
    vehicle_ref = vechle_data.child(str(track_id))
    vehicle_ref.set(data)
