__author__ = " Angela Corvino and Marvin Reimold"
__copyright__ = "Copyright (C) 2023 Angela Corvino and Marvin Reimold"
__license__ = "Public Domain"
__version__ = "1.0"

import torch
import torchvision.transforms.functional as TF


class Correction_matrix_producer(object):
    """
    Class for calculating the response matrix in reconstruction volume.

    Parameters
    ----------
    shape_front : tuple-like
        Tuple that defines front projection dimension.
    shape_side : tuple-like
        Tuple that defines lateral projections dimension.
    shift_image_top : list-like
        List of 2 integr numbers that defines how much the top 2D array is
        going to be shifted.
    shift_image_120 : list-like
        Description of parameter `shift_image_120`.
    shift_image_240 :list-like
        Description of parameter `shift_image_240`.
    shift_image_front : list-like
        List of 2 elements.
    mask_border_front : list-like
        List of 4 elements.
    mask_border_top : list-like
        List of 4 elements.
    mask_border_120 : list-like
        List of 4 elements.
    mask_border_240 : list-like
        List of 4 elements. The first teo numbers are used to set the side values to zero,
        while the other two are used to set the front number to 0.

    Attributes
    ----------
    shape_front
    """

    def __init__(self, shape_front, shape_side, shift_image_top,
                 shift_image_120, shift_image_240, shift_image_front, device):

        self.shape_front = shape_front
        self.shape_side = shape_side
        self.shift_image_top = shift_image_top
        self.shift_image_120 = shift_image_120
        self.shift_image_240 = shift_image_240
        self.shift_image_front = shift_image_front
        self.device = device
        self.correction_matrix = self.calc_corr_matrix()

    def apply_shift(self, picture_array, shift_image):
        if shift_image[1] > 0:
            picture_array[:shift_image[1], :] = 0
        elif shift_image[1] < 0:
            picture_array[shift_image[1]:, :] = 0
        if shift_image[0] > 0:
            picture_array[:, -shift_image[0]:] = 0
        elif shift_image[0] < 0:
            picture_array[:, :-shift_image[0]] = 0

    def calc_corr_matrix(self):
        side_picture_array = torch.ones(self.shape_side, dtype=torch.float32,
                                        device=self.device)
        picture_array_top = side_picture_array.clone()
        picture_array_120 = side_picture_array.clone()
        picture_array_240 = side_picture_array.clone()

        picture_array_front = torch.ones(self.shape_front, dtype=torch.float32,
                                         device=self.device)

        self.apply_shift(picture_array_top, self.shift_image_top)
        self.apply_shift(picture_array_120, self.shift_image_120)
        self.apply_shift(picture_array_240, self.shift_image_240)
        self.apply_shift(picture_array_front, self.shift_image_front)

        correction_matrix_front = (picture_array_front.unsqueeze(0)
                                   .repeat(self.shape_side[0], 1, 1)
                                   .to(self.device))
        correction_matrix_top = (picture_array_top.unsqueeze(1)
                                 .repeat(1, self.shape_front[0], 1)
                                 .to(self.device))
        correction_matrix_120 = (picture_array_120.unsqueeze(1)
                                 .repeat(1, self.shape_front[0], 1)
                                 .to(self.device))
        correction_matrix_240 = (picture_array_240.unsqueeze(1)
                                 .repeat(1, self.shape_front[0], 1)
                                 .to(self.device))

        correction_matrix_120 = TF.rotate(correction_matrix_120, angle=120,
                                          interpolation=TF.InterpolationMode.NEAREST,
                                          expand=False)
        correction_matrix_240 = TF.rotate(correction_matrix_120, angle=240,
                                          interpolation=TF.InterpolationMode.NEAREST,
                                          expand=False)
        correction_matrix = (correction_matrix_top + correction_matrix_120 +
                             correction_matrix_240 + correction_matrix_front)

        return correction_matrix