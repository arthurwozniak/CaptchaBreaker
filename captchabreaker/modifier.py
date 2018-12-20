# coding=utf-8
import cv2
import numpy as np
import base64


# Old code, should be reviewed
def split_joined_characters(image, boxes):
    # print("Splitting joined characters")
    img = image.copy()
    # print(img)
    # print(type(img))
    projection = np.sum(image, axis=0) / 255
    # print(projection)
    minimas = np.r_[True, projection[1:] < projection[:-1]
              ] & np.r_[projection[:-1] < projection[1:], True]
    # print(minimas)
    # print(len([x for x in minimas if x]))
    # print([[x, projection[x]] for x in range(len(minimas)) if minimas[x]])
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
    letters = sorted(letters, key=lambda x: x[0])

    letters = list(map(lambda x: x[1], letters))
    return letters


def get_contours(image):
    # Najdeme obdélníky ohraničující spojité plochy v obrázku
    im2, contours, hierarchy = cv2.findContours(
        image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Odstraníme malé plochy představující šum nebo "kousky" číslic
    contours_filtered = [c for c in contours if cv2.contourArea(c) >= 20]

    # print("Počet ploch: %d" % len(contours_filtered))
    return contours_filtered


def contours_to_boxes(contours):
    boxes = []
    for i in contours:
        x, y, w, h = cv2.boundingRect(i)
        boxes.append([x, y, w, h])
    return boxes


def remove_overlapping_boxes(boxes, count):
    print("removing")
    #         boxes.append([x, y, w, h])
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


def img_grayscale(image):
    image = image.copy()
    grayscaled = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    return grayscaled


def img_treshhold(image):
    image = image.copy()
    tresholded = cv2.threshold(
        image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
    tresholded = cv2.bitwise_not(tresholded)
    return tresholded


def img_filter(image, lower=0, upper=0):
    image = image.copy()
    filtered = cv2.inRange(image, np.array([lower]), np.array([upper]))
    return filtered


def img_unmask(image, count, onlyLetters=False):
    image = image.copy()
    contours = get_contours(image.copy())
    boxes = contours_to_boxes(contours)
    print("captcha letters: ", count)
    print("boxes found: ", len(boxes))

    if len(boxes) > count:
        boxes = remove_overlapping_boxes(boxes, count)

    if len(boxes) < count:
        res = split_joined_characters(image, boxes)
        for i in res:
            cv2.line(image, (i[0], 0), (i[0], image.shape[1]), (0, 0, 0), 1)
        contours = get_contours(image.copy())
        boxes = contours_to_boxes(contours)

    # Zakreslíme ohraničující čtverce
    image_bordered = cv2.cvtColor(image.copy(), cv2.COLOR_GRAY2RGB)
    letters = get_letters(image, boxes)

    rects = []

    for i in boxes:
        x, y, w, h = i
        rects.append([x, y, w, h])
        cv2.rectangle(image_bordered, (x, y), (x + w, y + h), (0, 255, 0), 1)

    if onlyLetters:
        return letters
    return image_bordered


def img_to_base64(image):
    img_bytes = cv2.imencode('.png', image)[1].tobytes()
    return base64.b64encode(img_bytes).decode('utf-8')
