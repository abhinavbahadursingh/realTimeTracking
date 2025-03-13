import cv2
import time
import numpy as np
from ultralytics import YOLO
from collections import defaultdict

# Load YOLO model
model = YOLO('yolo11n.pt')
class_list = model.names

# Load video
cap = cv2.VideoCapture(r'C:\Users\tar30\dmeo\Data\Video\testoing.mp4')

# Get video properties
fps = cap.get(cv2.CAP_PROP_FPS)
fps=60
# if fps <= 0:
#     fps = 30  # Default if can't get FPS

# Tracking variables
vehicle_data = {}
frame_count = 0

# Distance calibration (adjust these values based on your scene)
pixels_per_meter = 20  # Calibrate this based on known objects in the scene

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    frame_count += 1
    current_time = time.time()

    # Process frame with YOLO
    results = model.track(frame, persist=True)

    # # Draw tracking lines for reference
    # cv2.line(frame, (190, 220), (850, 220), (0, 0, 255), 3)  # Red line
    # cv2.line(frame, (27, 450), (960, 450), (255, 0, 0), 3)  # Blue line

    if results[0].boxes.data is not None:
        boxes = results[0].boxes.xyxy.cpu().numpy()

        # Check if tracking IDs are available
        if results[0].boxes.id is not None:
            track_ids = results[0].boxes.id.int().cpu().tolist()
            classes = results[0].boxes.cls.int().cpu().tolist()

            # Process each detected vehicle
            for box, track_id, class_id in zip(boxes, track_ids, classes):
                x1, y1, x2, y2 = map(int, box)
                cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
                class_name = class_list[class_id]

                # Initialize vehicle data if this is a new vehicle
                if track_id not in vehicle_data:
                    vehicle_data[track_id] = {
                        'class': class_name,
                        'first_seen_frame': frame_count,
                        'last_seen': current_time,
                        'positions': [(frame_count, cx, cy)],
                        'speed': 0.0
                    }
                else:
                    # Update existing vehicle data
                    vehicle_data[track_id]['last_seen'] = current_time
                    vehicle_data[track_id]['positions'].append((frame_count, cx, cy))

                    # Keep only the most recent 10 positions for memory efficiency
                    if len(vehicle_data[track_id]['positions']) > 10:
                        vehicle_data[track_id]['positions'] = vehicle_data[track_id]['positions'][-10:]

                    # Calculate speed based on recent position changes
                    if len(vehicle_data[track_id]['positions']) >= 2:
                        # Get oldest and newest positions
                        old_frame, old_x, old_y = vehicle_data[track_id]['positions'][0]
                        new_frame, new_x, new_y = vehicle_data[track_id]['positions'][-1]

                        # Calculate distance in pixels
                        pixel_distance = np.sqrt((new_x - old_x) ** 2 + (new_y - old_y) ** 2)

                        # Convert to meters
                        distance_meters = pixel_distance / pixels_per_meter

                        # Calculate time difference in seconds
                        frame_diff = new_frame - old_frame
                        time_diff = frame_diff / fps  # Convert frame count to seconds

                        # Calculate speed if time difference is valid
                        if time_diff > 0:
                            # Calculate speed in km/h (distance in m / time in s * 3.6)
                            speed_km_h = (distance_meters / time_diff) * 3.6

                            # Apply smoothing (exponential moving average)
                            alpha = 0.3  # Smoothing factor
                            old_speed = vehicle_data[track_id]['speed']
                            new_speed = alpha * speed_km_h + (1 - alpha) * old_speed

                            # Update vehicle speed
                            vehicle_data[track_id]['speed'] = round(new_speed, 2)

                # Draw bounding box
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

                # Display ID and class
                cv2.putText(frame, f"ID: {track_id} {class_name}", (x1, y1 - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)

                # Display speed
                speed = vehicle_data[track_id]['speed']
                cv2.putText(frame, f"Speed: {speed:.2f} KM/H", (x1, y2 + 20),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)

    # Remove vehicles not seen for more than 5 seconds
    current_time = time.time()
    vehicles_to_remove = [v_id for v_id, data in vehicle_data.items()
                          if current_time - data['last_seen'] > 5]

    for v_id in vehicles_to_remove:
        print(f"❌ Removing Vehicle {v_id} from tracking")
        vehicle_data.pop(v_id)

    # Display the frame
    cv2.imshow("YOLO Object Tracking & Counting", frame)

    # Exit on ESC key
    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()