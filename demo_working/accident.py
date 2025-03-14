
from demo_working.firebase_auth import initialize_firebase  # Import Firebase authentication


ref = initialize_firebase()

def pushAccident(track_id,cx,cy):
    accident_ref=ref.child("vehicle_Breakdown").child(str(track_id))
    accident_ref.set({
        "x":cx,
        "y":cy
    })



