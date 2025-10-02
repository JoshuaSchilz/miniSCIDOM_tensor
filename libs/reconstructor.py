import torch
import torch.nn.functional as F
import torchvision.transforms.functional as TF


class Reconstructor(object):
    """
    Class for MLEM reconstruction

    Parameters
    ----------
    max_it : type
        Description of parameter `max_it`.
    cam_pic_front : type
        Description of parameter `cam_pic_front`.
    cam_pic_top : type
        Description of parameter `cam_pic_top`.
    cam_pic_120 : type
        Description of parameter `cam_pic_120`.
    cam_pic_240 : type
        Description of parameter `cam_pic_240`.
    correction_matrix : type
        Description of parameter `correction_matrix`.
    median_filter : type
        Description of parameter `median_filter`.

    Attributes
    ----------
    rec_light_dist : type
        Description of attribute `rec_light_dist`.
    max_it
    cam_pic_front
    cam_pic_top
    cam_pic_120
    cam_pic_240
    correction_matrix
    median_filter

    """

    # Initialization of class
    def __init__(self, max_it, max_err, cam_pic_front, cam_pic_top, cam_pic_120,
                 cam_pic_240, correction_matrix, median_filter, device):

        # Number of iterations
        self.max_it = max_it
        self.max_err = max_err
        # Camera pictures
        self.cam_pic_front = cam_pic_front.float()
        self.cam_pic_top = cam_pic_top.float()
        self.cam_pic_120 = cam_pic_120.float()
        self.cam_pic_240 = cam_pic_240.float()

        # Correction matrix
        self.correction_matrix = correction_matrix.float()
        self.rec_light_dist = torch.ones_like(self.correction_matrix)

        # Median Filter
        self.median_filter = median_filter
        self.device = device

    # Iterative MLEM algorithm for 3D reconstruction of the light distribution
    # measured with SCIDOM detector
    def MLEM(self):

        # Multiply previous/starting light distribution with correction array
        rec_light_dist_120 = TF.rotate(self.rec_light_dist, angle=120,
                                       interpolation=TF.InterpolationMode.NEAREST,
                                       expand=False)
        rec_light_dist_240 = TF.rotate(self.rec_light_dist, angle=240,
                                       interpolation=TF.InterpolationMode.NEAREST,
                                       expand=False)

        # Calculate forward projections
        forw_proj_front = self.rec_light_dist.sum(axis=0)
        forw_proj_top = self.rec_light_dist.sum(axis=1)
        forw_proj_120 = rec_light_dist_120.sum(axis=1)
        forw_proj_240 = rec_light_dist_240.sum(axis=1)

        # Divide cam pictures (projection_values) by forward projections
        self.quotient_front = torch.where(
            torch.logical_and(self.cam_pic_front != 0, forw_proj_front != 0),
            self.cam_pic_front / forw_proj_front,
            torch.zeros_like(self.cam_pic_front)
        )
        self.quotient_top = torch.where(
            torch.logical_and(self.cam_pic_top != 0, forw_proj_top != 0),
            self.cam_pic_top / forw_proj_top,
            torch.zeros_like(self.cam_pic_top)
        )
        self.quotient_120 = torch.where(
            torch.logical_and(self.cam_pic_120 != 0, forw_proj_120 != 0),
            self.cam_pic_120 / forw_proj_120,
            torch.zeros_like(self.cam_pic_120)
        )
        self.quotient_240 = torch.where(
            torch.logical_and(self.cam_pic_240 != 0, forw_proj_240 != 0),
            self.cam_pic_240 / forw_proj_240,
            torch.zeros_like(self.cam_pic_240)
        )

        # Back project qoutient into 3D volume
        rec_part_front = torch.stack(
                        [self.quotient_front] * self.rec_light_dist.shape[0],
                        dim=0)
        rec_part_top = torch.stack(
                        [self.quotient_top] * self.rec_light_dist.shape[1],
                        dim=1)
        rec_part_120 = torch.stack(
                        [self.quotient_120] * self.rec_light_dist.shape[1],
                        dim=1)
        rec_part_240 = torch.stack(
                        [self.quotient_240] * self.rec_light_dist.shape[1],
                        dim=1)

        # Rotate backprojected 120° and 240° light distributions
        rec_part_120 = TF.rotate(rec_part_120, angle=120,
                                 interpolation=TF.InterpolationMode.NEAREST,
                                 expand=False)
        rec_part_240 = TF.rotate(rec_part_240, angle=240,
                                 interpolation=TF.InterpolationMode.NEAREST, 
                                 expand=False)

        # Add back projected light distributions
        back_proj_light_dist = (
            rec_part_front + rec_part_120 + rec_part_240 + rec_part_top
        )

        # Multiply back projected 3D light distributions with previous light distribution
        # (already multiplied with correction matrix)
        self.rec_light_dist = torch.where(
            torch.logical_and(self.rec_light_dist != 0, back_proj_light_dist != 0),
            self.rec_light_dist * back_proj_light_dist,
            torch.zeros_like(self.rec_light_dist)
        )
        self.rec_light_dist = torch.where(
            torch.logical_and(self.rec_light_dist != 0, self.correction_matrix != 0),
            self.rec_light_dist / self.correction_matrix,
            torch.zeros_like(self.rec_light_dist)
        )

        if self.median_filter:
            self.rec_light_dist = F.median_pool2d(self.rec_light_dist.unsqueeze(0),
                                                  kernel_size=5, padding=2).squeeze(0)

    # Perform iterative reconstruction
    def perform_MLEM(self):
        self.quotient_front_ar = [99]
        self.quotient_top_ar = [99]
        self.quotient_120_ar = [99]
        self.quotient_240_ar = [99]

        center_height = 67
        center_width = 67

        print("Considering center area of size: ", center_height, "x", center_width," for reconstruction")
        i = 0

        def calculate_center_mean(input_tensor, center_height, center_width):
            # Calculate the starting indices for the center area
            start_row = (input_tensor.shape[0] - center_height) // 2
            start_col = (input_tensor.shape[1] - center_width) // 2
            # Extract the center area
            center_area = input_tensor[start_row:start_row + center_height,
                                       start_col:start_col + center_width]
            # Calculate the mean of the center area
            mean_center_area = center_area.mean().item()
            return mean_center_area

        # Loop for iterative process
        # for i in tqdm(range(self.max_it)): # loop for iteration based 
        while (
            abs(1 - self.quotient_front_ar[-1]) > self.max_err
            or abs(1 - self.quotient_top_ar[-1]) > self.max_err
            or abs(1 - self.quotient_120_ar[-1]) > self.max_err
            or abs(1 - self.quotient_240_ar[-1]) > self.max_err
        ):

            self.MLEM()
            # Append the quotients to the respective lists in each iteration
            self.quotient_front_ar.append(calculate_center_mean(self.quotient_front,
                                                                center_height, center_width))
            self.quotient_top_ar.append(calculate_center_mean(self.quotient_top,
                                                              center_height, center_width))
            self.quotient_120_ar.append(calculate_center_mean(self.quotient_120,
                                                              center_height, center_width))
            self.quotient_240_ar.append(calculate_center_mean(self.quotient_240,
                                                              center_height, center_width))
            i += 1
            print("Iteration ", i, " done!")
            if i == self.max_it:
                break
                print("Could'nt achive desired uncertainty in given maximum iterations")

        self.quotient_front_ar = self.quotient_front_ar[1:]
        self.quotient_top_ar = self.quotient_top_ar[1:]
        self.quotient_120_ar = self.quotient_120_ar[1:]
        self.quotient_240_ar = self.quotient_240_ar[1:]

        # print("Quotient front: ", self.quotient_front_ar)
        # print("Quotient top: ", self.quotient_top_ar)
        # print("Quotient 120: ", self.quotient_120_ar)
        # print("Quotient 240: ", self.quotient_240_ar)

        self.rec_light_dist = torch.flip(self.rec_light_dist, dims=(0, 1))