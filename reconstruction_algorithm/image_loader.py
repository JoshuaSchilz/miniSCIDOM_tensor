import cv2
import numpy as np
import matplotlib.pyplot as plt
import torch
import torchvision.transforms.functional as TF
from skimage.morphology import disk, opening

# from scipy import signal


class Image_loader(object):
    """Class for loading and manipulate camera pictures.

    Parameters
    ----------
    path : type
        Description of parameter `path`.
    color : type
        Description of parameter `color`.
    rescale : type
        Description of parameter `rescale`.
    flip : type
        Description of parameter `flip`.
    rot : type
        Description of parameter `rot`.
    crop : type
        Description of parameter `crop`.
    radius_cut_edge : type
        Description of parameter `radius_cut_edge`.
    radius_circle : type
        Description of parameter `radius_circle`.
    shift : type
        Description of parameter `shift`.
    mask_borders : type
        Description of parameter `mask_borders`.
    numpy : type
        Description of parameter `numpy`.
    factor : type
        Description of parameter `factor`.

    Attributes
    ----------
    width : type
        Description of attribute `width`.
    height : type
        Description of attribute `height`.
    image : type
        Description of attribute `image`.
    path
    color
    rescale
    flip
    rot
    crop
    radius_cut_edge
    radius_circle
    shift
    mask_borders
    numpy
    factor

    """

    # Initialization of class
    def __init__(self, path, color, rescale, flip, rot, crop, radius_cut_edge,
                 radius_circle, shift, numpy, factor, device):

        # 3D data matrix
        self.path = path
        self.color = color
        self.rescale = rescale
        self.flip = flip
        self.rot = rot
        self.crop = crop
        self.radius_cut_edge = radius_cut_edge
        self.radius_circle = radius_circle
        self.shift = shift
        self.numpy = numpy
        self.factor = factor
        self.width = None
        self.height = None
        self.device = device
        self.image = self.load_and_process_image()

    # Function load and manipulated image
    def load_and_process_image(self):
        if self.numpy:
            im = np.load(self.path, allow_pickle=True)
            im = im.astype('float32')
            im = torch.from_numpy(im).to(self.device)

        else:
            im = cv2.imread(self.path, -1)
            im = im.astype('float32')
            im = torch.from_numpy(im).to(self.device)
            im = torch.rot90(im, 1, [0, 1])

        self.height, self.width = im.shape[:2]

        # choose color channel
        if self.color == 'red':
            im = im[:, :, 2].T
        elif self.color == 'green':
            im = im[:, :, 1].T
        elif self.color == 'blue':
            im = im[:, :, 0].T
        elif self.color == 'grey':
            im = im.T

        # rescale pixel number
        if self.rescale is not None:
            self.height = int(self.height*self.rescale)
            self.width = int(self.width*self.rescale)
            im = TF.resize(TF.to_pil_image(im.cpu()), (self.height, self.width),
                           interpolation=TF.InterpolationMode.BICUBIC)
            im = TF.to_tensor(im).to(self.device)

        # rotate image
        if self.rot is not None:
            M = cv2.getRotationMatrix2D((self.height/2, self.width/2), self.rot, 1)
            im = cv2.warpAffine(im.cpu().numpy(), M, (self.height, self.width))
            im = cv2.flip(im, 1)
            im = torch.from_numpy(im.astype('float32')).to(self.device)

        # Uncomment to plot the images before cropping
        # plt.imshow(im.cpu().numpy(), cmap="jet", vmin=0,
        #            vmax=65000, interpolation=None)  # oncoray
        # plt.plot([self.crop[2], self.crop[3], self.crop[3],
        #           self.crop[2], self.crop[2]],
        #          [self.crop[0], self.crop[0], self.crop[1],
        #           self.crop[1], self.crop[0]], linewidth=0.5)

        # Crop image
        if self.crop is not None:
            im = im[self.crop[0]:self.crop[1], self.crop[2]:self.crop[3]]

        # Flip image
        if self.flip is not None:
            if self.flip == 0:  # Vertical flip
                im = TF.vflip(im)
            elif self.flip == 1:  # Horizontal Flip
                im = TF.hflip(im)
            elif self.flip == -1:  # Vertical and horizontal flip
                im = TF.hflip(im)
                im = TF.vflip(im)

        # Cut edge
        if self.radius_cut_edge is not None:
            selem = disk(self.radius_cut_edge)
            im = opening(im.cpu(), selem).to(self.device)

        # Cut circle
        if self.radius_circle is not None:
            y, x = np.ogrid[-self.height // 2:self.height // 2,
                            -self.width // 2:self.width // 2]
            mask = x**2 + y**2 > self.radius_circle**2
            im[mask] = 0

        # Shift image
        if self.shift is not None:
            shift_x, shift_y = self.shift
            if shift_x < 0:
                im = torch.nn.functional.pad(im, (0, abs(shift_x)),
                                             "constant", 0)[:, :-abs(shift_x)]
            elif shift_x > 0:
                im = torch.nn.functional.pad(im, (abs(shift_x), 0), 
                                             "constant", 0)[:, abs(shift_x):]

            if shift_y < 0:
                im = torch.nn.functional.pad(im, (0, 0, abs(shift_y), 0),
                                             "constant", 0)[:-abs(shift_y), :]
            elif shift_y > 0:
                im = torch.nn.functional.pad(im, (0, 0, 0, abs(shift_y)),
                                             "constant", 0)[abs(shift_y):, :]

        # if self.numpy==False:
        #     for i in range(1):
                # op=1#changes to decide how big the hotspots are to remove,
                # but if you increase it too much the image will blur.
                # selem=disk(op)
                # im=opening(im, selem)
                # im=cv2.medianBlur(im,1)  #If the input type is not np.uint8,
                # the only allowed ksize values for cv2.medianBlur are 3 and 5
                # print(type(im))
                # im=scipy.signal.medfilt2d(im,1) #allows for float64 with larger kernel sizes
                # im=cv2.GaussianBlur(im,(5,5),5,5) #Gaussian Kernel Size 5x5

        im *= self.factor

        return im
