import cv2
import time

cap = cv2.VideoCapture(0)
desired_fps = 5
delay = 1 / desired_fps
time_prev = 0

while True:
    time_now = time.time()
    ret, frame = cap.read()
    if not ret:
        break
    
    if (time_now - time_prev) > delay:
        # Process the frame
        cv2.imshow('frame', frame)
        time_prev = time_now

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()