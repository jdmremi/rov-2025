import cv2

def list_available_cameras(max_index=5):
    for index in range(max_index):
        cap = cv2.VideoCapture(index)
        if cap.isOpened():
            print(f"Camera index {index} is available.")
            cap.release()
        else:
            print(f"Camera index {index} not available.")

if __name__ == "__main__":
    list_available_cameras(5)

