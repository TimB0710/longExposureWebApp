import numpy as np
import cv2
from .helper_functions import *
import math

def lighten(image1, image2):
    # Ensure the images are the same size and have the same number of channels
    if image1.shape != image2.shape:
        raise ValueError("Both images must have the same dimensions and number of channels")
    
    # Apply the lighten blend mode by taking the maximum of each pixel in both images
    result = np.maximum(image1, image2)
    
    return result

def darken(image1, image2):
    if image1.shape != image2.shape:
        raise ValueError("Both images must have the same dimensions and number of channels")
    result = np.minimum(image1, image2)
    return result

def average(image1, image2):
    if image1.shape != image2.shape:
        raise ValueError("Both images must have the same dimensions and number of channels")
    result = ((image1.astype(np.float32) + image2.astype(np.float32)) / 2).astype(np.uint8)
    return result

def screen(image1, image2):
    if image1.shape != image2.shape:
        raise ValueError("Both images must have the same dimensions and number of channels")
    image1 = image1.astype(np.float32) / 255.0
    image2 = image2.astype(np.float32) / 255.0
    result = 1 - (1 - image1) * (1 - image2)
    result = (result * 255).astype(np.uint8)
    return result

def screen2(image1, image2, alpha=0.95):
    alpha = calc_alpha(np.mean(image2))
    # print(alpha)
    if image1.shape != image2.shape:
        raise ValueError("Both images must have the same dimensions and number of channels")
    image1 = image1.astype(np.float32) / 255.0
    image2 = image2.astype(np.float32) / 255.0
    blended = 1 - (1 - image1) * (1 - image2)

    # Rauschreduzierung durch gleitenden Mittelwert
    result = (alpha * image1 + (1 - alpha) * blended)

    return (result * 255).astype(np.uint8)

def overlay(image1, image2):
    if image1.shape != image2.shape:
        raise ValueError("Both images must have the same dimensions and number of channels")
    image1 = image1.astype(np.float32) / 255.0
    image2 = image2.astype(np.float32) / 255.0
    result = np.where(image1 <= 0.5, 2 * image1 * image2, 1 - 2 * (1 - image1) * (1 - image2))
    result = (result * 255).astype(np.uint8)
    return result

def difference(image1, image2):
    if image1.shape != image2.shape:
        raise ValueError("Both images must have the same dimensions and number of channels")
    result = np.abs(image1.astype(np.int16) - image2.astype(np.int16)).astype(np.uint8)
    return result

def add(image1, image2):
    if image1.shape != image2.shape:
        raise ValueError("Both images must have the same dimensions and number of channels")
    # result = cv2.add(image1, image2)  # Handles overflow by capping at 255
    result = scale_to_valid_range(image1.astype(np.float64)+image2.astype(np.float64))
    return result

def hsvblend(image1,image2):
    if image1.shape != image2.shape:
        raise ValueError("Both images must have the same dimensions and number of channels")
    hsv_image1 = cv2.cvtColor(image1.astype(np.uint8), cv2.COLOR_RGB2HSV)
    hsv_image2 = cv2.cvtColor(image2.astype(np.uint8), cv2.COLOR_RGB2HSV)
    h1, s1, v1 = cv2.split(hsv_image1)
    h2, s2, v2 = cv2.split(hsv_image2)

    h_image = np.astype((h1+h2)/2,np.uint8)
    s_image = np.astype((s1+s2)/2,np.uint8)
    v_image = scale_to_valid_range(v1+v2).astype(np.uint8)
    hsv_image = cv2.merge([h_image, s_image, v_image])
    rgb_image = cv2.cvtColor(hsv_image, cv2.COLOR_HSV2RGB)
    return rgb_image

def multiply(image1,image2):
    if image1.shape != image2.shape:
        raise ValueError("Both images must have the same dimensions and number of channels")
    image1 = np.astype(image1,np.float64)
    image2 = np.astype(image2,np.float64)
    return scale_to_valid_range(image1*image2).astype(np.uint8)

