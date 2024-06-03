import time
import cv2


class Camera:
    def __init__(self, n=0, frame_rate=30, target_res=(1920, 1080)):
        self.cam = cv2.VideoCapture(n)
        if not self.cam.isOpened():
            raise ValueError(f"Failed to open camera with number {n}")
        self.cam.set(cv2.CAP_PROP_FRAME_WIDTH, target_res[0])
        self.cam.set(cv2.CAP_PROP_FRAME_HEIGHT, target_res[1])
        self.res = int(self.cam.get(cv2.CAP_PROP_FRAME_WIDTH)), int(self.cam.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.frame_rate = frame_rate
        self.prev_time = 0
        self.prev_frame = None

    def get_frame(self):
        curr_time = time.time()
        if curr_time - self.prev_time < 1 / self.frame_rate:
            return self.prev_frame
        ret, img = self.cam.read()
        if not ret:
            return self.prev_frame
        self.prev_time = curr_time
        self.prev_frame = img
        return img

    def close(self):
        self.cam.release()


def main():
    cam = Camera(n=0, frame_rate=30, target_res=(50, 50))
    print(cam.res)
    while True:
        img = cam.get_frame()
        cv2.imshow("Camera", img)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    cam.close()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
