import cv2
import numpy as np
import serial  # Communication UART
from picamera2 import Picamera2
import time
import os
# Initialisation de la Communication UART avec l'Arduino via les pins TX/RX
try:
    arduino = serial.Serial('/dev/serial0', baudrate=115200, timeout=1)
    time.sleep(2)
    print(" Connexion UART avec l'Arduino établie.")
except serial.SerialException:
    print(" Erreur: Impossible de se connecter à l'Arduino via /dev/serial0")
    exit()

# Détection de lignes blanches

def detect_lines(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = cv2.Canny(blurred, 50, 150)
    return cv2.HoughLinesP(edges, 1, np.pi / 180, threshold=100, minLineLength=100, maxLineGap=50)

def is_horizontal(line, angle_threshold=10):
    x1, y1, x2, y2 = line
    dx = x2 - x1
    dy = y2 - y1
    if dx == 0:
        return False
    angle = np.degrees(np.arctan2(abs(dy), abs(dx)))
    return angle < angle_threshold

# Communication UART avec l'Arduino

def send_data(data):
    try:
        arduino.write((data + '\n').encode())
        print(f" Envoyé: {data}")
    except Exception as e:
        print(f" Erreur lors de l'envoi: {e}")

def receive_data():
    try:
        if arduino.in_waiting:
            raw_data = arduino.readline()
            received = raw_data.decode("utf-8", errors="ignore").strip()
            print(f" Reçu: {received}")
    except Exception as e:
        print(f" Erreur de lecture UART: {e}")

# Capture et traitement vidéo

def process_camera_and_save(output_path="video_out.mp4"):
    if os.path.exists(output_path):
        os.remove(output_path)
        print(f"  Ancien fichier {output_path} supprimé.")

    print(" Initialisation de la caméra...")
    picam2 = Picamera2()
    picam2.preview_configuration.main.size = (640, 480)
    picam2.preview_configuration.main.format = "RGB888"
    picam2.configure("preview")
    picam2.start()
    print(" Caméra prête.")

    send_data("START")

    width, height = 640, 480
    fps = 10
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out_detected = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

    line_count = 0
    line_crossed = False
    y_threshold = int(0.8 * height)
    counted_lines = []
    deplacement_envoye = False

    frame_count = 0
    # vidéo 3min 
    # temps d'exécution du code = temps de la video 
    max_frames = 3 * 60 * fps

    while frame_count < max_frames:
        frame = picam2.capture_array()
        if frame is None:
            print(" Erreur : Frame non capturée !")
            break

        lines = detect_lines(frame)
        cv2.line(frame, (0, y_threshold), (width, y_threshold), (0, 0, 255), 2)
        crossing_current = False

        if lines is not None:
            for line in lines:
                x1, y1, x2, y2 = line[0]
                if is_horizontal((x1, y1, x2, y2), angle_threshold=10):
                    if not any(np.array_equal(line[0], counted) for counted in counted_lines):
                        if y1 >= y_threshold or y2 >= y_threshold:
                            counted_lines.append(line[0])
                            crossing_current = True
                            cv2.line(frame, (x1, y1), (x2, y2), (255, 0, 0), 2)
                        else:
                            cv2.line(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    else:
                        cv2.line(frame, (x1, y1), (x2, y2), (255, 0, 0), 2)
                else:
                    cv2.line(frame, (x1, y1), (x2, y2), (0, 255, 255), 2)

        if crossing_current and not line_crossed:
            line_count += 1
            line_crossed = True
            print(f" Ligne franchie ! Total: {line_count}")
            # line count == 4 si c'est sur un vrai terrain de badminton
            if line_count == 2 and not deplacement_envoye:
                print(" Envoi de la commande 'DEPLACEMENT' à l'Arduino...")
                send_data("DEPLACEMENT")
                deplacement_envoye = True

        if not crossing_current:
            line_crossed = False

        cv2.putText(frame, f"Lignes franchies: {line_count}", (50, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255), 2)

        out_detected.write(frame)
        frame_count += 1
        receive_data()

    print(" Enregistrement terminé.")
    picam2.stop()
    out_detected.release()
    cv2.waitKey(100)
    arduino.close()

if __name__ == "__main__":
    process_camera_and_save("video_out.mp4")
