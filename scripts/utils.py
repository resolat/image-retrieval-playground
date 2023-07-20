import cv2
import imutils


def mask_borders(img, borders):
    h = img.shape[0]
    w = img.shape[1]

    x_min = int(borders[0] * w / 100)
    x_max = w - int(borders[2] * w / 100)
    y_min = int(borders[1] * h / 100)
    y_max = h - int(borders[3] * h / 100)

    return img[y_min:y_max, x_min:x_max]


def preprocess_image_change_detection(img,
                                      gaussian_blur_radius_list=None,
                                      black_mask=(5, 10, 20, 0)):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = mask_borders(gray, black_mask)
    if gaussian_blur_radius_list is not None:
        for radius in gaussian_blur_radius_list:
            gray = cv2.GaussianBlur(gray, (radius, radius), 0)

    return gray


def compare_frames_change_detection(prev_frame, next_frame, min_contour_area):
    frame_delta = cv2.absdiff(prev_frame, next_frame)
    thresh = cv2.threshold(frame_delta, 45, 255, cv2.THRESH_BINARY)[1]

    thresh = cv2.dilate(thresh, None, iterations=2)

    cnts = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)

    score = 0
    res_cnts = []
    for c in cnts:
        if cv2.contourArea(c) < min_contour_area:
            continue

        res_cnts.append(c)
        score += cv2.contourArea(c)

    return score, res_cnts, thresh


def read_preproc_img(img_path,
                     resize_to=None,
                     gaussian_blur_radius_list=None,
                     black_mask=(5, 10, 5, 0),
                     min_h=480,
                     min_w=640):
    """Read and preprocess image for comparison.

    Parameters
    ----------
    img_path : str or pathlib.Path
        Path to the image.
    resize_to : tuple, optional
        Resize image to this (h, w), by default None
    gaussian_blur_radius_list : array-like, optional
        An array of Gaussian blur radiuses, by default None
    black_mask : tuple, optional
        Mask image from borders (left, top, right, bottom), in percentage,
        by default (5, 10, 5, 0)
    min_h : int, optional
        Minimal height of the image, by default 480
    min_w : int, optional
        Minimal width of the image, by default 640

    Returns
    -------
    numpy.ndarray or None
        Preprocessed image or None if image doesn't meet minimal requirements.

    """
    img = cv2.imread(str(img_path), cv2.IMREAD_COLOR)
    if img is None:
        return None

    if (img.shape[0] < min_h) or (img.shape[1] < min_w):
        return None

    if resize_to is not None:
        if (img.shape[0] != resize_to[0]) or (img.shape[1] != resize_to[1]):
            img = cv2.resize(img, resize_to[::-1])

    return preprocess_image_change_detection(
        img, gaussian_blur_radius_list, black_mask)
