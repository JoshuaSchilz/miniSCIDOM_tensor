import glob
import os
import time
from pathlib import Path
import itk
import numpy as np
import torch
from camera_picture_viewer import Camera_picture_viewer
from correction_matrix_producer import Correction_matrix_producer
from image_loader import Image_loader
from reconstructor import Reconstructor
from tomograpic_viewer import Tomograpic_viewer
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

start_time = time.time()

# for online readout (Basler 60gm =0.0634 | pixelfly = 0.073825)
# s = 0.0634  # Basler --- Resolution (mm/pixel) depends on camera
s = 0.073825  # Pixelfly --- Resolution (mm/pixel) depends on camera
directory = "../pictures/online/input/"
list_of_files = glob.glob(
    directory + "*"
)  # * means all if need specific format then *.csv
latest_file = max(list_of_files, key=os.path.getctime)
path_obj = Path(latest_file)
picture_name = path_obj.name
print(f"Latest file: {picture_name}")

# ==================== Input Values ============================================
"""Check if spatial resolution s is put in correctly"""
ROI_diam = 2.5  # Diameter for the evaluated Region in mm (mask)
ROI_diam_sum = 2.5  # Diameter for the evaluated summed up Region (mask)
max_err = 0.05  # Reconstruction stops if relative Error is lower than this value
max_it = 4  # Maximum number of Iterations if Error threshold is not achieved
# it tends to get worse after the 4th or 5th iteration
ring_error = False
num_rings = 15
# Define path for measured pictures
path_pic_front = directory + picture_name
path_pic_top = directory + picture_name
path_pic_120 = directory + picture_name
path_pic_240 = directory + picture_name

# ROI definition
shape_front = (150, 110)
shape_side = (310, 110)
deltaz = 310
rot_angle = 0
x_0 = 5
y_0 = 0
y1_front = 195
y2_front = 345
x1_front = 633
x2_front = 743
y1_top = 447
y2_top = 757
x1_top = 633
x2_top = 743
y1_120 = 442
y2_120 = 752
x1_120 = 902
x2_120 = 1012
y1_240 = 442
y2_240 = 752
x1_240 = 374
x2_240 = 484

shift_image_front = torch.tensor([0, 0], dtype=torch.int)
shift_image_top = torch.tensor([0, 0], dtype=torch.int)
shift_image_120 = torch.tensor([0, 0], dtype=torch.int)
shift_image_240 = torch.tensor([0, 0], dtype=torch.int)

color_channel = "grey"

cam_pic_front = Image_loader(
    path_pic_front,
    color_channel,
    None,
    None,
    rot_angle,
    [y1_front, y2_front, x1_front, x2_front],
    None,
    None,
    shift_image_front,
    False,
    10 / 9,
    device,
).image  # DELTAX,DELTAY SHIFTING
cam_pic_top = Image_loader(
    path_pic_top,
    color_channel,
    None,
    None,
    rot_angle,
    [y1_top, y2_top, x1_top, x2_top],
    None,
    None,
    shift_image_top,
    False,
    1,
    device,
).image
cam_pic_120 = Image_loader(
    path_pic_120,
    color_channel,
    None,
    None,
    rot_angle,
    [y1_120, y2_120, x1_120, x2_120],
    None,
    None,
    shift_image_120,
    False,
    10 / 9,
    device,
).image
cam_pic_240 = Image_loader(
    path_pic_240,
    color_channel,
    None,
    None,
    rot_angle,
    [y1_240, y2_240, x1_240, x2_240],
    None,
    None,
    shift_image_240,
    False,
    10 / 9,
    device,
).image

end_time = time.time()
elapsed_time = end_time - start_time
print(f"Elapsed time Image Loading: {elapsed_time} seconds")

correction_matrix = Correction_matrix_producer(
    shape_front,
    shape_side,
    shift_image_top,
    shift_image_120,
    shift_image_240,
    shift_image_front,
    device,
).correction_matrix

# Uncomment to print correction matrix
# Tomograpic_viewer(correction_matrix, False, 4)

end_time = time.time()
elapsed_time = end_time - start_time
print(f"Elapsed time Correction Matrix: {elapsed_time} seconds")

save_directory = "../pictures/online/output/" + picture_name[:-4] + "/"
if not os.path.exists(save_directory):
    # Create a new directory because it does not exist
    os.makedirs(save_directory)

# Backgroung subtraction
smin = torch.tensor([torch.min(cam_pic_front),
                     torch.min(cam_pic_top),
                     torch.min(cam_pic_120),
                     torch.min(cam_pic_240)])
smin = torch.min(smin)
smin = 0
cam_pic_front[cam_pic_front < smin] = 0
cam_pic_top[cam_pic_top < smin] = 0
cam_pic_120[cam_pic_120 < smin] = 0
cam_pic_240[cam_pic_240 < smin] = 0

#Uncomment to print camers pictures
# Camera_picture_viewer(cam_pic_front, cam_pic_top, cam_pic_120, cam_pic_240,
#                       False, 16)

# end_time = time.time()
# elapsed_time = end_time - start_time
# print(f"Elapsed time Camera Picture Viewer: {elapsed_time} seconds")

# %% ####################################Reconstruction
reconstructor = Reconstructor(
    max_it,
    max_err,
    cam_pic_front,
    cam_pic_top,
    cam_pic_120,
    cam_pic_240,
    correction_matrix,
    False,
    device,
)  # the last one is the median filter

reconstructor.perform_MLEM()
rec_light_dist = reconstructor.rec_light_dist

save_name = "rec_light_dist_" + picture_name[:-4]
np.save(save_directory + save_name, rec_light_dist.cpu().numpy())

# Saving itk file for 3D slicer
image = itk.GetImageFromArray(np.flip(rec_light_dist.cpu().numpy(), axis=1))
image.SetSpacing([s, s, s])
itk.imwrite(image, save_directory+"rec_light_dist" + picture_name[:-4] + ".nrrd")

# Uncomment to show reconstruction
# Tomograpic_viewer(
#     (rec_light_dist / rec_light_dist.max()), False, 1
# )  # here you can enable the logaritmic scale

end_time = time.time()
elapsed_time = end_time - start_time
print(f"Elapsed total time: {elapsed_time} seconds")
