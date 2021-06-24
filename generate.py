import math
import sys

import cv2
import pytesseract
from PIL import Image, ImageOps


def speed_ms(frame, swapped=False):
    crop = (72, 640, 72+75, 640+30)  # not swapped
    ready_image = ImageOps.invert(frame.crop(crop))
    ready_image.save('working/text_speed.jpg')
    data = pytesseract.image_to_string(
        ready_image,
        lang='eng',
        config='--psm 10 --oem 3 -c tessedit_char_whitelist=0123456789'
    )
    try:
        val = int(data)
        return val / 3.6
    except ValueError:
        pass


def height_m(frame, swapped=False):
    crop = (178, 640, 178+75, 640+30) # not swapped
    ready_image = ImageOps.invert(frame.crop(crop))
    ready_image.save('working/text_height.jpg')
    data = pytesseract.image_to_string(
        ready_image,
        lang='eng',
        config='--psm 10 --oem 3 -c tessedit_char_whitelist=0123456789.'
    )
    try:
        return float(data) * 1000.0
    except ValueError:
        pass


def extract(video_path, start, swap, every=30):
    cap = cv2.VideoCapture(video_path)

    # Seek to start
    fps = cap.get(cv2.CAP_PROP_FPS)
    cap.set(cv2.CAP_PROP_POS_FRAMES, (fps * start) - 1)

    last_elapsed = 0
    last_altitude = 0
    last_speed = 0

    cumulative_downrange = 0

    print("Time (s),Downrange (m),Altitude (m)")

    while True:
        for i in range(every):
            success, image = cap.read()

        elapsed = (cap.get(cv2.CAP_PROP_POS_MSEC) * 0.001) - start

        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        image = cv2.threshold(image, 100, 255, cv2.THRESH_BINARY)[1]

        pil_im = Image.fromarray(image)
        pil_im.thumbnail((1280, 720))
        pil_im.save('working/last_frame.jpg')

        altitude = height_m(pil_im)
        if altitude is None:
            continue

        # Update data on change of lowest granularity value, the altitude.
        if altitude == last_altitude:
            continue

        # Decimal point lost - this can happen with noisy visuals.
        if last_altitude > 0 and altitude >= last_altitude * 5:
            continue

        # No point wasting cycles extracting speed until we have a useful
        # altitude delta.
        speed = speed_ms(pil_im)
        if speed is None:
            continue

        # Sign is irrelevant, we're measuring downrange regardless. This
        # wouldn't work with a boost-back burn.
        delta_altitude = abs(altitude - last_altitude)

        delta_elapsed = elapsed - last_elapsed

        # This assumes constant speed, I need to account for acceleration.
        average_speed = (speed + last_speed) / 2.0

        # D = VT.
        distance_travelled = delta_elapsed * average_speed

        # Noisy values can create invalid (non-right-angle) triangles
        if distance_travelled < delta_altitude:
            distance_travelled = delta_altitude

        # Pythagoras - we know one side (delta_altitude) and the hypotenuse (distance_travelled).
        # We're just 
        delta_downrange = math.sqrt(pow(distance_travelled, 2) - pow(delta_altitude, 2))

        cumulative_downrange += delta_downrange

        print(f'{elapsed},{int(cumulative_downrange)},{int(altitude)}')

        # Landed, safely of course.
        if altitude == 0:
            break

        last_speed = speed
        last_elapsed = elapsed
        last_altitude = altitude


if __name__ == '__main__':
    start = int(sys.argv[1])
    swap = int(sys.argv[2])
    video_path = sys.argv[3]
    extract(video_path, start, swap)
