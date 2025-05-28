from .blending_algorithms import *


def create_stacked_image(video_path, result_path, star_threshold=None,
    alpha=None, save_debug_image=True):
  print("Creating stacked image", video_path, result_path)
  vidcap = cv2.VideoCapture(video_path)
  video_length = int(vidcap.get(cv2.CAP_PROP_FRAME_COUNT))

  print("Finding stars in images")
  possible_points_by_image = []
  success, frame = vidcap.read()
  debug_img = frame.copy()
  i = 0
  while success:
    possible_points_by_image.append(find_stars(frame, i))
    success, frame = vidcap.read()
    i += 1

  next_group = 0
  for i in range(0, len(possible_points_by_image[0])):
    possible_points_by_image[0][i].set_group(next_group)
    next_group += 1

  # use all found points as reference points
  reference_points = []
  for points in possible_points_by_image:
    for p in points:
      reference_points.append(p)

  max_dist = 50
  print("Finding nearest neighbours")
  for i in range(1, len(possible_points_by_image)):
    for point in possible_points_by_image[i]:
      # Get the nearest point and the distance to it considering the frame number as an extra dimension
      nearest_point, dist = get_nearest_point(point, reference_points, 10)

      if dist <= max_dist:
        point.set_group(nearest_point.group)
      else:
        point.set_group(next_group)
        next_group += 1

  if save_debug_image:
    for points in possible_points_by_image:
      for p in points:
        if p.group is not None:
          col = hsv2bgr(((p.group * 10) % 255, 255, 255))
        else:
          col = (255, 255, 255)
        cv2.drawMarker(debug_img, p.pos, col, markerType=cv2.MARKER_CROSS,
                       markerSize=10, thickness=1)

    debug_img_path = result_path.replace('.jpg', '_debug.jpg')
    cv2.imwrite(debug_img_path, debug_img)

  number_of_points_by_image = []
  for points in possible_points_by_image:
    number_of_points_by_image.append(len(points))

  sorted_indices = sorted(range(len(number_of_points_by_image)),
                          key=lambda i: number_of_points_by_image[i],
                          reverse=True)
  most_stars_index = sorted_indices[0]
  print('most_stars_index', most_stars_index)
  print('len(possible_points_by_image)', len(possible_points_by_image))
  print('video_length', video_length)

  aligned_images = []
  pts1 = possible_points_by_image[most_stars_index]
  vidcap.set(cv2.CAP_PROP_POS_FRAMES, 0)
  print(f"Aligning images based on Stars")
  for i in range(0, video_length):
    success, image = vidcap.read()
    if not success:
      continue
    # if i == most_stars_index:
    #     aligned_images.append(frame)
    #     continue
    pts2 = possible_points_by_image[i]
    T = compute_transformation_matrix(pts1, pts2)
    # T = compute_rotation_translation_matrix(pts1,pts2)
    if T is None:
      continue
    height, width = image.shape[:2]
    transformed_image = cv2.warpAffine(image, T, (width, height))
    aligned_images.append(transformed_image)
  print('len(aligned_images)', len(aligned_images))
  cv2.imwrite(result_path, stack_images(aligned_images, screen2))
