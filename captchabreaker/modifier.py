# coding=utf-8
import cv2
import numpy as np
import base64


# Old code, should be reviewed
def split_joined_characters(image, boxes):
    projection = np.sum(image, axis=0) / 255
    minimas = np.r_[True, projection[1:] < projection[:-1]] & np.r_[projection[:-1] < projection[1:], True]
    return [[x, projection[x]] for x in range(len(minimas)) if minimas[x] and (projection[x] < 10)]


def intersection(a, b):
    x = max(a[0], b[0])
    y = max(a[1], b[1])
    w = min(a[0] + a[2], b[0] + b[2]) - x
    h = min(a[1] + a[3], b[1] + b[3]) - y
    if w < 0 or h < 0:
        return (0, 0, 0, 0)  # or (0,0,0,0) ?
    return (x, y, w, h)


def get_letters(image, boxes):
    image = image.copy()
    # Z původního obrázku vyřežeme jednotlivé číslice
    letters = []
    for i in boxes:
        x, y, w, h = i
        # cv2.rectangle(im2, (x, y), (x + w, y + h), (0, 255, 0), 1)
        letters.append([x, cv2.resize(src=image[y:y + h, x:x + w], dsize=(20, 20), interpolation=cv2.INTER_NEAREST)])
    # Číslice seřadíme podle osy X
    letters = sorted(letters, key=lambda img: img[0])

    letters = list(map(lambda img: img[1], letters))
    return letters


def get_contours(image):
    # Najdeme obdélníky ohraničující spojité plochy v obrázku
    contours, hierarchy = cv2.findContours(
        image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Odstraníme malé plochy představující šum nebo "kousky" číslic
    contours_filtered = [c for c in contours if cv2.contourArea(c) >= 5]

    # print("Počet ploch: %d" % len(contours_filtered))
    return contours_filtered


def contours_to_boxes(contours):
    return list(map(cv2.boundingRect, contours))


def remove_overlapping_boxes(boxes, count):
    while (len(boxes) > count):
        # print(boxes)
        areas = [intersection(boxes[i], boxes[i + 1]) for i in range(len(boxes) - 1)]
        # print(areas)
        i = areas.index(max(areas, key=lambda x: x[2] * x[3]))
        r1 = boxes[i]
        r2 = boxes[i + 1]

        if r1[2] * r1[3] > r2[2] * r2[3]:
            boxes.pop(i + 1)
        else:
            boxes.pop(i)
    return boxes


def blob_to_img(data):
    nparr = np.fromstring(base64.b64decode(data), np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    return img


def bin_to_img(data):
    nparr = np.fromstring(data, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    return img


def find_boxes(image, lettersCount):
    contours = get_contours(image)
    boxes = contours_to_boxes(contours)

    if len(boxes) > lettersCount:
        boxes = remove_overlapping_boxes(boxes, lettersCount)

    if len(boxes) < lettersCount:
        res = split_joined_characters(image, boxes)
        for i in res:
            cv2.line(image, (i[0], 0), (i[0], image.shape[1]), (0, 0, 0), 1)
        contours = get_contours(image.copy())
        boxes = contours_to_boxes(contours)

    return boxes


def draw_boxes(image, boxes):
    image = cv2.cvtColor(image.copy(), cv2.COLOR_GRAY2RGB)
    for i in boxes:
        x, y, w, h = i
        cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 1)
    return image


def img_to_base64(image):
    img_bytes = cv2.imencode('.png', image)[1].tobytes()
    return base64.b64encode(img_bytes).decode('utf-8')
