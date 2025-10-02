__author__ = " Angela Corvino and Marvin Reimold"
__copyright__ = "Copyright (C) 2023 Angela Corvino and Marvin Reimold"
__license__ = "Public Domain"
__version__ = "1.0"

import matplotlib.pyplot as plt
from matplotlib.widgets import Slider
from matplotlib.colors import LogNorm


class Camera_picture_viewer(object):
    """Class for showing reconstruted 3D data slices.

    Parameters
    ----------
    cam_pic_front : array-like
        2D array front projection.
    cam_pic_top :   array-like
        2D array top projection.
    cam_pic_120 : array-like
        2D array 120 projection.
    cam_pic_240 : type
        2D array 240 projection.
    c_log : boolean
        if True the color scale is logaritmic.
    bits : integer-like
        Number of bits that define the color range.

    Attributes
    ----------
    im_1 : type
        AxesImage for cam_pic_top.
    im_2 : type
        Description of attribute `im_2`.
    im_3 : type
        Description of attribute `im_3`.
    im_4 : type
        Description of attribute `im_4`.
    axmin : type
        Description of attribute `axmin`.
    axmax : type
        Description of attribute `axmax`.
    smin : type
        Description of attribute `smin`.
    smax : integer-like
        Description of attribute `smax`.
    onclick : object
        Function for handling click events.
    sminval : integer-like
        Description of attribute `sminval`.
    c_log
    bits

    """

    def __init__(self, cam_pic_front, cam_pic_top,
                 cam_pic_120, cam_pic_240, c_log, bits):

        # Convert PyTorch tensors to NumPy arrays
        cam_pic_front = cam_pic_front.cpu().numpy()
        cam_pic_top = cam_pic_top.cpu().numpy()
        cam_pic_120 = cam_pic_120.cpu().numpy()
        cam_pic_240 = cam_pic_240.cpu().numpy()
        fig, (ax1, ax2, ax3, ax4) = plt.subplots(1, 4, figsize=(10, 4))

        self.c_log = c_log
        self.bits = bits

        # Subplot which shows top camera picture
        if self.c_log:
            norm = LogNorm()
        else:
            norm = None

        ax1.set_title('Top camera')
        ax1.set_xlabel('x in pixel')
        ax1.set_ylabel('z in pixel')

        self.im_1 = ax1.imshow(cam_pic_top,
                               origin='upper', aspect='equal',
                               cmap='jet', norm=norm)

        # Subplot which shows 120 camera picture
        ax2.set_title('120° camera ')
        ax2.set_xlabel('x_120_deg in pixel')
        ax2.set_ylabel('z in pixel')

        self.im_2 = ax2.imshow(cam_pic_120,
                               origin='upper', aspect='equal',
                               cmap='jet', norm=norm)

        # Subplot which shows 240 camera picture
        ax3.set_title('240° camera')
        ax3.set_xlabel('x_240_deg in pixel')
        ax3.set_ylabel('z in pixel')

        self.im_3 = ax3.imshow(cam_pic_240,
                               origin='upper', aspect='equal',
                               cmap='jet', norm=norm)

        # Subplot which shows front camera picture
        ax4.set_title('Front camera')
        ax4.set_xlabel('x in pixel')
        ax4.set_ylabel('y in pixel')

        self.im_4 = ax4.imshow(cam_pic_front,
                               origin='lower', aspect='equal',
                               cmap='jet', norm=norm)

        plt.colorbar(self.im_4, label='Intensity')

        # Axes and sliders for changing window for linear colormap
        axcolor = 'lightgoldenrodyellow'
        self.axmin = fig.add_axes([0.3, 0.01, 0.10, 0.03], facecolor=axcolor)
        self.axmax = fig.add_axes([0.7, 0.01, 0.10, 0.03], facecolor=axcolor)
        if self.c_log:
            self.smin = Slider(self.axmin,
                               'Min', 1, 2**self.bits, valinit=0)
            self.smax = Slider(self.axmax,
                               'Max', 1, 2**self.bits, valinit=2**self.bits)
        else:
            self.smin = Slider(self.axmin,
                               'Min', 1, 2**self.bits, valinit=0)
            self.smax = Slider(self.axmax,
                               'Max', 1, 2**self.bits, valinit=2**self.bits)

        # Set window for linear colormap
        self.im_1.set_clim([self.smin.val, self.smax.val])
        self.im_2.set_clim([self.smin.val, self.smax.val])
        self.im_3.set_clim([self.smin.val, self.smax.val])
        self.im_4.set_clim([self.smin.val, self.smax.val])

        # Connect different events to functions
        fig.canvas.mpl_connect('button_press_event', self.onclick)

        plt.tight_layout()
        plt.show()

        # the minimun value is the one you choose before closing the plot
        self.sminval = self.smin.val

    def onclick(self, event):
        """Function for handling click events.

        Parameters
        ----------
        event : type
            Description of parameter `event`.

        Returns
        -------
        type
            Description of returned object.
        """

        # Check if zoom etc is selected
        mode = plt.get_current_fig_manager().toolbar.mode
        if mode == '':

            # Selecting min and max values for linear colormap
            if event.inaxes is self.axmin:
                self.update()
            elif event.inaxes is self.axmax:
                self.update()

    def update(self):
        """
        Short summary.
        Returns
        -------
        object
            Return the updated 2D arrays.

        """
        # Update front camera picture
        self.im_1.set_clim([self.smin.val, self.smax.val])

        # Update top camera picture
        self.im_2.set_clim([self.smin.val, self.smax.val])

        # Update 120 camera picture
        self.im_3.set_clim([self.smin.val, self.smax.val])

        # Update 240 camera picture
        self.im_4.set_clim([self.smin.val, self.smax.val])

        # Redraw front camera picture
        self.im_1.axes.figure.canvas.draw()

        # Redraw top camera picture
        self.im_2.axes.figure.canvas.draw()

        # Redraw 120 camera picture
        self.im_3.axes.figure.canvas.draw()

        # Redraw 240 camera picture
        self.im_4.axes.figure.canvas.draw()