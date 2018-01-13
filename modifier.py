import cv2
import numpy as np

def blob_to_cv_img(data):
    nparr = np.fromstring(data, np.uint8)
    img_np = cv2.imdecode(nparr, 0)
    print(img_np)
