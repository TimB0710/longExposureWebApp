from typing import List
from .Point import Point
import numpy as np
import cv2
import math
import multiprocessing


def compute_transformation_matrix(pts_t1, pts_t2):
  pts1 = []
  pts1_groups = []
  pts2 = []
  pts2_groups = []
  for p in pts_t1:
    pts1_groups.append(p.group)
  for p in pts_t2:
    pts2_groups.append(p.group)
  common_groups = set(pts1_groups) & set(pts2_groups)
  for p in pts_t1:
    if p.group in common_groups:
      pts1.append(p.pos)
  for p in pts_t2:
    if p.group in common_groups:
      pts2.append(p.pos)

  pts1 = np.array(pts1)
  pts2 = np.array(pts2)
  A = np.hstack([pts2, np.ones((pts2.shape[0], 1))])
  try:
    X, _, _, _ = np.linalg.lstsq(A, pts1, rcond=None)
    return X.T  # 2x3-Transformationsmatrix
  except:
    return None


def get_nearest_point(ref: Point, points: List[Point],
    max_lookback: int = None):
  min_dist = float('inf')
  min_dist_point = None
  for point in points:
    if point.frame >= ref.frame:
      continue
    if max_lookback is not None:
      if point.frame - ref.frame > 10:
        continue
    # dist = get_dist(ref,point)
    dist = ref.get_dist_with_time(point)
    if dist < min_dist:
      min_dist = dist
      min_dist_point = point
  return min_dist_point, min_dist


def find_one_block_centers(arr):
  indices = np.where(arr == 1)[0]
  # Blöcke identifizieren
  diffs = np.diff(indices)
  split_points = np.where(diffs > 1)[0] + 1
  blocks = np.split(indices, split_points)
  centers = [int(np.mean(block)) for block in blocks if len(block) > 0]
  return centers


def get_thresholded_image(img):
  img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
  img_gray = cv2.blur(img_gray, (3, 3), 0)
  background = cv2.GaussianBlur(img_gray, (51, 51), 0)
  normalized = cv2.subtract(img_gray, background)
  hist = cv2.calcHist([normalized], [0], None, [256], [0, 256])
  cv2.normalize(hist, hist, alpha=0, beta=1, norm_type=cv2.NORM_MINMAX)
  normalized = cv2.normalize(normalized, None, alpha=0, beta=255,
                             norm_type=cv2.NORM_MINMAX)
  threshold = np.mean(img_gray) * 10
  out = normalized > threshold
  return out


def find_stars(img, frame, group=None):
  th_image = get_thresholded_image(img)
  x_hist = np.sum(th_image, axis=0)
  y_hist = np.sum(th_image, axis=1)

  x_hist = x_hist > 0
  y_hist = y_hist > 0

  x_centers = find_one_block_centers(x_hist)
  y_centers = find_one_block_centers(y_hist)

  points = []
  for x_pos in x_centers:
    for y_pos in y_centers:
      if th_image[y_pos][x_pos] > 0:
        points.append(Point((x_pos, y_pos), group, frame))
        # points.append((x_pos,y_pos))

  return points


def hsv2bgr(col):
  hsl_np = np.uint8([[col]])  # OpenCV erwartet ein 3D-Array
  bgr = cv2.cvtColor(hsl_np, cv2.COLOR_HSV2BGR)[0, 0]  # Umwandlung
  return tuple(map(int, bgr))


def stack_images(image_list, blending_function):
  """
  Stacked die Bilder und erzeugt einen Langzeitbelichtungseffekt.
  """

  if len(image_list) < 2:
    print('image_list has to contain at least 2 images')
    return None

  print(blending_function)
  out = blending_function(image_list[0], image_list[1])
  for i in range(2, len(image_list)):
    out = blending_function(out, image_list[i])

  return out


# ChatGPT
def stack_images_parallel(image_list, blending_function, num_chunks=10):
  if len(image_list) < 2:
    print('image_list has to contain at least 2 images')
    return None
  # Noch bafangen, dass image list anch teilung in chunks nich zu klein is
  if num_chunks > len(image_list) / 2:
    num_chunks = np.floor(len(image_list) / 2)
    print(
      f'NOTICE [stack_images_parallel]: reduced number of chunks to {num_chunks}')
  chunk_size = max(1, len(image_list) // num_chunks)
  chunks = [image_list[i:i + chunk_size] for i in
            range(0, len(image_list), chunk_size)]
  print('stack_images_parallel:', blending_function)
  with multiprocessing.Pool(processes=num_chunks) as pool:
    results = pool.starmap(blend_chunk,
                           [(chunk, blending_function) for chunk in chunks])

  # Reduziere die Teilresultate sequentiell
  out = results[0]
  for res in results[1:]:
    out = blending_function(out, res)

  return out


def blend_chunk(chunk, blending_function):
  out = chunk[0]
  for img in chunk[1:]:
    out = blending_function(out, img)
  return out


def scale_to_valid_range(image):
  # Scale logarithmicly !
  # Use Histogram
  print('[scale_to_valid_range] before scaling np.max(image)=', np.max(image))
  print('[scale_to_valid_range] before scaling np.min(image)=', np.min(image))
  r = -np.log(1 - 0.995) / np.max(image)
  K = 255
  res = K * (1 - np.exp(-r * image)) / (1 + np.exp(-r * image))
  np.round(res)
  print('[scale_to_valid_range] after scaling np.max(image)=', np.max(res))
  print('[scale_to_valid_range] after scaling np.min(image)=', np.min(res))
  return res.astype(np.uint8)


#                                       ##########################                                       #
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~##♥️♥️♥️♥️## CHAT-GPT ##♥️♥️♥️♥️##~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
#                                       ##########################                                       #

def log_f(x, K, P0, r, v):
  return K / (1 + ((K - P0) / P0) * math.e ** (-r * (x - v)))


def log1_f(x, K0, K, P0, r, v, n):
  return (K0 / (1 + ((K - P0) / P0) * math.e ** (-r * (x - v)))) + n


def calc_alpha(x):
  # K0=0.95
  # P0=0.7
  # r=0.4
  # v=1.2
  # n=0.04
  # K=K0-n
  K0 = 0.95
  P0 = 0.4
  r = 0.3
  v = -3.9
  n = 0.04
  K = K0 - n

  res = log1_f(x, K0, K, P0, r, v, n)
  res = min(res, 0.95)
  res = max(res, 0.70)

  return res
