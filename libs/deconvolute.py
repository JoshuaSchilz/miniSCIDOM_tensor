import os,sys
import itk
import numpy as np
import torch
import tifffile
import json
base_path = os.path.dirname(__file__)
sys.path.append(base_path)

from correction_matrix_producer import Correction_matrix_producer
from image_loader import Image_loader
from reconstructor import Reconstructor

class Deconvolute(object):
    """Class for deconvoluting image.

    Parameters
    ----------
    path : str
        Path to the image file.
    color_channel : str
        Color channel to be used.
    factor : float
        Efficiency factor for the image.
    device : torch.device
        Device to run the computations on.

    Attributes
    ----------
    image : torch.Tensor
        Deconvoluted image tensor.
    """

    def __init__(self, path_pic, factor, outdir):
        self.path_pic = path_pic
        self.factor = factor
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.outdir = outdir
        self.quotients = []
        self.q_err_rel = 0
    
    def get_default_image(self, rot_angle):
        """Loads the full image once to be used for ROI selection display."""
        _, default_image = Image_loader(
            self.path_pic, "grey", None, 1, rot_angle, [0,0,0,0], None, None, 
            torch.tensor([0, 0], dtype=torch.int), False, 1, self.device
        ).image
        return default_image
    
    def define_roi(self, rot_angle=0,
                   shape_roi=[[0,0], [0,0]], 
                   rois=[[0,0,0,0], [0,0,0,0], [0,0,0,0], [0,0,0,0]]):
        self.shape_front, self.shape_side = shape_roi
        self.rois = rois
        color_channel = "grey"
        # Define the coordinates for cropping
        shape_front = self.shape_front
        shape_side = self.shape_side
        rot_angle = 0
        y1_front, y2_front, x1_front, x2_front = self.rois[0]
        y1_top, y2_top, x1_top, x2_top = self.rois[1]
        y1_120, y2_120, x1_120, x2_120 = self.rois[2]
        y1_240, y2_240, x1_240, x2_240 = self.rois[3]

        # Define the shift values for each camera
        self.shift_image_front = torch.tensor([0, 0], dtype=torch.int)
        self.shift_image_top = torch.tensor([0, 0], dtype=torch.int)
        self.shift_image_120 = torch.tensor([0, 0], dtype=torch.int)
        self.shift_image_240 = torch.tensor([0, 0], dtype=torch.int)

        # Load the images using Image_loader
        self.cam_pic_front, _ = Image_loader(
            self.path_pic,
            color_channel,
            None,
            1,
            rot_angle,
            [y1_front, y2_front, x1_front, x2_front],
            None,
            None,
            self.shift_image_front,
            False,
            10 / 9 / self.factor,
            self.device,
        ).image
        
        self.cam_pic_top, _ = Image_loader(
            self.path_pic,
            color_channel,
            None,
            1,
            rot_angle,
            [y1_top, y2_top, x1_top, x2_top],
            None,
            None,
            self.shift_image_top,
            False,
            1 / self.factor,
            self.device,
        ).image
        self.cam_pic_120, _ = Image_loader(
            self.path_pic,
            color_channel,
            None,
            1,
            rot_angle,
            [y1_120, y2_120, x1_120, x2_120],
            None,
            None,
            self.shift_image_120,
            False,
            10 / 9 / self.factor,
            self.device,
        ).image
        self.cam_pic_240, _ = Image_loader(
            self.path_pic,
            color_channel,
            None,
            1,
            rot_angle,
            [y1_240, y2_240, x1_240, x2_240],
            None,
            None,
            self.shift_image_240,
            False,
            10 / 9 / self.factor,
            self.device,
        ).image

    def create_correction_matrix(self):
        """Create correction matrix for the given camera picture."""
        self.correction_matrix = Correction_matrix_producer(
            self.shape_front,
            self.shape_side,
            self.shift_image_top,
            self.shift_image_120,
            self.shift_image_240,
            self.shift_image_front,
            self.device,
        ).correction_matrix

        return self.correction_matrix

    def perform_reconstruction(self, max_it, max_err, resolution):
        """Runs the MLEM reconstruction."""
        if not hasattr(self, 'correction_matrix'):
            self.create_correction_matrix()

        # Background subtraction
        smin = torch.tensor([torch.min(self.cam_pic_front),
                            torch.min(self.cam_pic_top),
                            torch.min(self.cam_pic_120),
                            torch.min(self.cam_pic_240)])
        smin = torch.min(smin)
        smin = 0
        self.cam_pic_front[self.cam_pic_front < smin] = 0
        self.cam_pic_top[self.cam_pic_top < smin] = 0
        self.cam_pic_120[self.cam_pic_120 < smin] = 0
        self.cam_pic_240[self.cam_pic_240 < smin] = 0

        reconstructor = Reconstructor(
            max_it,
            max_err,
            self.cam_pic_front,
            self.cam_pic_top,
            self.cam_pic_120,
            self.cam_pic_240,
            self.correction_matrix,
            False, # Median filter
            self.device,
        )

        reconstructor.perform_MLEM()
        rec_light_dist = reconstructor.rec_light_dist
        if not os.path.exists(self.outdir):
            os.makedirs(self.outdir) 
        np.save(self.outdir + "/rec_light_dist.npy", rec_light_dist.cpu().numpy())
        #image = itk.GetImageFromArray(np.flip(rec_light_dist.cpu().numpy(), axis = 1))
        #image.SetSpacing([resolution, resolution, resolution])
        #itk.imwrite(image, self.outdir + "/rec_light_dist" + ".nrrd")
        tifffile.imwrite(self.outdir + "/rec_light_dist.tif", rec_light_dist.cpu().numpy())
        
        q_front = np.array(reconstructor.quotient_front_ar)
        q_top = np.array(reconstructor.quotient_top_ar)
        q_120 = np.array(reconstructor.quotient_120_ar)
        q_240 = np.array(reconstructor.quotient_240_ar)
        self.quotients = [q_front, q_top, q_120, q_240]
        self.q_err_rel = abs(((q_front[-1:]+q_top[-1:]+q_120[-1:]+q_240[-1:])/4)-1)
        
        return rec_light_dist