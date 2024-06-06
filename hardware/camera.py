import time
import cv2


class Camera:
    def __init__(self, camera_number=0, frame_rate=30, target_res=(1920, 1080)):
        self.cam = cv2.VideoCapture(camera_number)
        if not self.cam.isOpened():
            raise ValueError(f"Failed to open camera with number {camera_number}")
        self.cam.set(cv2.CAP_PROP_FRAME_WIDTH, target_res[0])
        self.cam.set(cv2.CAP_PROP_FRAME_HEIGHT, target_res[1])
        self.res = int(self.cam.get(cv2.CAP_PROP_FRAME_WIDTH)), int(self.cam.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.frame_rate = frame_rate
        self.prev_time = 0
        self.prev_frame = None

    def capture_frame(self):
        curr_time = time.time()
        if curr_time - self.prev_time < 1 / self.frame_rate:
            return self.prev_frame
        ret, frame = self.cam.read()
        if not ret:
            return self.prev_frame
        self.prev_time = curr_time
        self.prev_frame = frame
        return frame

    def close(self):
        self.cam.release()


def convert(frame, file_format=".jpg"):
    return cv2.imencode(file_format, frame)[1].tobytes()


def initialize_cameras() -> dict[str, Camera]:
    cams = {'overhead': Camera(camera_number=0, frame_rate=30, target_res=(1920, 1080)),
            'onboard': Camera(camera_number=0, frame_rate=30, target_res=(1920, 1080))}
    return cams


cameras = initialize_cameras()


def main():
    cam = cameras['overhead']
    while True:
        img = cam.capture_frame()
        cv2.imshow("Overhead Camera", img)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    cam.close()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
