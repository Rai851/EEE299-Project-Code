import cv2
import requests
import time
from classifier import WasteClassifier

ESP32_CTRL_URL = "http://10.112.63.98:8080/open"  # ✅ তোমার IP

CATEGORIES = ['metal', 'paper', 'plastic']

classifier = WasteClassifier()

def send_command(category):
    try:
        requests.get(f"{ESP32_CTRL_URL}/{category}", timeout=3)
        print(f"✅ OPEN {category.upper()} bin")
    except Exception as e:
        print(f"❌ Error: {e}")

def main():
    cap = cv2.VideoCapture("http://10.112.63.190/stream")

    if not cap.isOpened():
        print("❌ Can't open Camera!")
        return

    last_prediction = None
    last_sent_time  = 0
    COOLDOWN = 5

    print("🚀 Smart Dustbin Running... Press Q to close")

    while True:
        ret, frame = cap.read()
        if not ret:
            continue

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        label, confidence = classifier.predict(rgb)

        if label not in CATEGORIES:
            label = CATEGORIES[0]

        color = {
            'plastic': (255, 100, 0),
            'paper':   (0, 200, 0),
            'metal':   (0, 100, 255),
        }

        cv2.putText(frame, f"{label.upper()} ({confidence:.0%})",
                    (10, 40), cv2.FONT_HERSHEY_SIMPLEX,
                    1.2, color.get(label, (255,255,255)), 2)
        cv2.imshow("Smart Dustbin", frame)

        now = time.time()
        if confidence > 0.80 and (label != last_prediction or now - last_sent_time > COOLDOWN):
            send_command(label)
            last_prediction = label
            last_sent_time  = now

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()