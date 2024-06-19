import cv2
import numpy as np


def convert_img_format(img, file_format=".jpg"):
    return cv2.imencode(file_format, img)[1].tobytes()


def erode(img, kernel_size=5):
    kernel = np.ones((kernel_size, kernel_size), np.uint8)
    return cv2.erode(img, kernel, iterations=1)


def dilate(img, kernel_size=5):
    kernel = np.ones((kernel_size, kernel_size), np.uint8)
    return cv2.dilate(img, kernel, iterations=1)


class Masker:
    max_h = 360.0
    max_s = 100.0
    max_v = 100.0

    cv2_max_h = 180
    cv2_max_s = 255
    cv2_max_v = 255

    post_processing_funcs = {
        'dilate': dilate,
        'erode': erode,
    }

    default_post_processing = [(dilate, 5), (erode, 10), (dilate, 5)]

    def __init__(self, h_range=(0, max_h), s_range=(0, max_s), v_range=(0, max_v),
                 post_processing=None):
        self.h_range = h_range
        self.s_range = s_range
        self.v_range = v_range
        self.post_processing = Masker.resolve_post_processing(post_processing)

    def create_mask(self, img):
        hsv_img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        lower_bound = np.array(Masker.to_cv2_hsv((self.h_range[0], self.s_range[0], self.v_range[0])), dtype=np.uint8)
        upper_bound = np.array(Masker.to_cv2_hsv((self.h_range[1], self.s_range[1], self.v_range[1])), dtype=np.uint8)
        mask = cv2.inRange(hsv_img, lower_bound, upper_bound)
        for process, *args in self.post_processing:
            mask = process(mask, *args)
        return mask

    def overlay(self, img, blending=0.5):
        mask = self.create_mask(img)
        return cv2.addWeighted(img, blending, cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR), 1 - blending, 0)

    def crop(self, img):
        mask = self.create_mask(img)
        return cv2.bitwise_and(img, img, mask=mask)

    def rgb(self):
        middle = ((self.h_range[1] + self.h_range[0]) // 2,
                  (self.s_range[1] + self.s_range[0]) // 2,
                  (self.v_range[1] + self.v_range[0]) // 2)
        middle = Masker.to_cv2_hsv(middle)
        img = np.array([[middle]], dtype=np.uint8)
        return cv2.cvtColor(img, cv2.COLOR_HSV2RGB)[0][0]

    @staticmethod
    def to_cv2_hsv(hsv):
        return (int(hsv[0] / Masker.max_h * Masker.cv2_max_h),
                int(hsv[1] / Masker.max_s * Masker.cv2_max_s),
                int(hsv[2] / Masker.max_v * Masker.cv2_max_v))

    @staticmethod
    def resolve_post_processing(post_processing):
        if post_processing is None:
            return []
        elif post_processing == 'default':
            return Masker.default_post_processing
        elif isinstance(post_processing, tuple):
            if callable(post_processing[0]):
                return [post_processing]
            raise ValueError(f"Invalid post processing function: {post_processing}")
        result = []
        for func, *args in post_processing:
            if isinstance(func, str):
                result.append((Masker.post_processing_funcs[func], *args))
            elif callable(func):
                result.append((func, *args))
            else:
                raise ValueError(f"Invalid post processing function: {func}")
        return post_processing


default_maskers = {
    'blue': Masker(h_range=(200, 240), s_range=(72, 100), v_range=(23, 55), post_processing='default'),
}


def create_color_masks(img, maskers=None):
    if maskers is None:
        maskers = default_maskers
    masks = {}
    for color, color_mask in maskers.items():
        masks[color] = color_mask.create_mask(img)
    return masks


def find_pucks(img, lower_puck_radius, upper_puck_radius, puck_maskers=None) \
        -> dict[str, list[tuple[tuple[int, int], int]]]:
    if puck_maskers is None:
        puck_maskers = default_maskers
    masks = create_color_masks(img, puck_maskers)
    puck_positions = {}
    for color, mask in masks.items():
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        puck_positions[color] = []
        for contour in contours:
            moment = cv2.moments(contour)
            center = (int(moment["m10"] / moment["m00"]), int(moment["m01"] / moment["m00"]))
            area = cv2.contourArea(contour)
            radius = int(np.sqrt(area / np.pi))
            if lower_puck_radius < radius < upper_puck_radius:
                puck_positions[color].append((center, int(radius)))
    return puck_positions


def main():
    img = cv2.imread('../images/test.jpg')
    pucks = find_pucks(img, 200, 400)
    print(pucks)
    for color in pucks:
        for center, radius in pucks[color]:
            cv2.drawMarker(img, center, (0, 255, 0), cv2.MARKER_CROSS, 20, 2)
            cv2.circle(img, center, radius, (0, 255, 0), 2)
    cv2.imshow("Pucks", img)
    while True:
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break


if __name__ == '__main__':
    main()
