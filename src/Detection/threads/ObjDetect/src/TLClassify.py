import cv2
import numpy as np

def TLClassification(original_image, threshold=150):

    h, w, _ = original_image.shape
    k = 15
    original_image = original_image[h//k:h-h//k,4*w//k:w-4*w//k]
    gray_image = cv2.cvtColor(original_image, cv2.COLOR_BGR2GRAY)

    min_val, max_val, _, _ = cv2.minMaxLoc(gray_image)
    scaled_image = ((gray_image - min_val) / (max_val - min_val)) * 255
    scaled_image = np.uint8(scaled_image)

    _, binary_image = cv2.threshold(scaled_image, threshold, 255, cv2.THRESH_BINARY)

    contours, _ = cv2.findContours(binary_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    max_contour = max(contours, key=cv2.contourArea)

    M = cv2.moments(max_contour)
    # center_x = int(M["m10"] / M["m00"])
    if (M["m00"] == 0) or (M["m01"] == 0 ): 
        TL_state = "nocolor"
    else:
        center_y = int(M["m01"] / M["m00"])
        h, w, _ = original_image.shape
        if center_y < h // 3:
           TL_state = "red"
        elif center_y > 2 * h // 3:
           TL_state = "green"
        elif h // 3 < center_y < 2 * h // 3:
           TL_state = "yellow"

    return TL_state
