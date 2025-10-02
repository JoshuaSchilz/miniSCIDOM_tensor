# Introduction
The following library performs reconstruction of images from the miniSCIDOM detector using pytorch for faster computations. The original code for the reconstruction was written by *Angela Corvino and Marvin Reimold* (https://github.com/AngelaCorvino/MiniSCIDOM).

Corresponding publication: https://www.cambridge.org/core/journals/high-power-laser-science-and-engineering/article/miniscidom-a-scintillatorbased-tomograph-for-volumetric-dose-reconstruction-of-single-laserdriven-proton-bunches/171051DA9A4C1744E0020F783F1381D1

# Requirements (defined in 'environment.yaml')
- `streamlit`
- `pytorch`
- `scipy`
# Running the code
## Running the UI Locally
Run the UI using (make sure to have all necessary packages installed in your python enviroment)
```
python -m streamlit run run_ui.py
```
This will provide a link to the web-based user interface 
Example:
```
  You can now view your Streamlit app in your browser.

  Local URL: http://localhost:8501
```
## Running the UI Online
- The program uses the zrok api to expose the streamlit application to a public URL.

- `setup.sh` - setup up the neccesary containers and packages to be used for a standalone functioning. **Can take quite a while**
- `run_app.sh` - verify all the installation files and run the zrok application.

- Before running zrok, please create an account on `myzrok.io`, get the account token from `api-v1.zrok.io` and save it in zrok.env file in the main directory.

- Execute the shell scripts using:
```
./setup.sh
./run_app.sh 
```

- If everything works properly, you get a public URL in the terminal that can be accessed remotely from any device.

## Running the base code directly
The base class for reconstruction is located in `libs/deconvolute.py`. The simple reconstructed light distribution can be obtained using the following minimal code:

```
from libs.deconvolute import Deconvolute
image_path = "pictures/online/input/example_img.tif"
factor = 1
outdir = "pictures/online/"

deconvoluter = Deconvolute(image_path, factor, outdir=outdir)
shape_roi = [[150, 110],[310, 110]]
rois = [
    [237, 387, 609, 719],
    [487, 797, 609, 719],
    [480, 790, 872, 982],
    [479, 789, 344, 454]
]

deconvoluter.define_roi(shape_roi=shape_roi, rois=rois)
correction_matrix = deconvoluter.create_correction_matrix()
rec_light_dist = deconvoluter.perform_reconstruction(max_it=4, max_err=0.05, resolution=0.073825)
```
# How to use the UI of the miniSCIDOM analysis tool 
## 1. Image loading:
- Input the directory of your raw image or place it in the defaul directory and select the image you want to reconstruct.
- An example image ("example_img.tif") is provided. 

<img width="256" height="355" alt="image" src="https://github.com/user-attachments/assets/daa0f0b8-ca13-4bae-b1de-9a82cb6c74c5" />

## 2. Parameter Settings:
- There are different parameters which have to best set correctly for an accurate reconstructuion
- Firstly the resolution in mm/pixel this depends on the camera which is used (Default: PCO Pixelfly 4.2)
- Efficiency factor can be used if a optical filter was placed infront of the objective, i.e. an OD1 filter with a transmission of 10%. In order to make the signal level comparable (to the without filter setting) one would put in 0.1 for the efficiancy factor
- The ROI diameter describes the size of a circular mask which is placed over the reconstruction in the and in which the depth dose distribution will be calculated. The ROI can be shiftet in the x and y plane by adjusting "Shift ROI X/Y (pixels). 

<img width="1510" height="357" alt="image" src="https://github.com/user-attachments/assets/9b50afa4-25bd-4c53-9c82-c327e8657148" />

## 3. Reconstruction
- The selected image will be shown.
- Now the placement of the region of interests (ROI's) have to be set for each of the 4 projection.
  - One can toggle a logarithmic color scale for the plot of the image to better visualize the edges of the projections
  - Under Shape Front: The height and the width of the Side and Front ROI's can be changed and thus increase or decrease the reconstruction volume. Typically it is easier to reconstruct a smaller volume but this also changes depending on the dose distribution.
  - The position of the individual ROIs is shown in the plot of the loaded image. The precise position is cruicial for a good and accurate 3D reconstruction (shifting the ROI by a few pixels can make a huge difference).
  - Under the different tabs ("Front", "Top", "120°" and "240°") one can set the position of the scale
- When done setting the ROI positions one presses "Run Reconstruction and Save ROI's"
- An indication on how accurate your reconstruction is are the "Quotients from the reconstruction". They basically showcase your error of the reconstruction, so one aims to get this quotient for all 4 projetion to 1±0.05 by the 4th iteration for a 5% Error.
- So this takes a few tries: Reconstruct --> Check Quotient and Reconstruction --> Adjust ROI positions --> and so on, until you are pleased with the result

<img width="1518" height="936" alt="image" src="https://github.com/user-attachments/assets/b77ca843-5640-4064-a3ec-949b798fec8b" />

- If you have previously reconstructed an image and want to do the reconstruction again, you can drag and drop the .json file which is automatically created during the reconstruction and saved in the output folder into the overlay. This will load the ROI positions and parameter settings which were used for the reconstruction of that image

<img width="1521" height="138" alt="image" src="https://github.com/user-attachments/assets/7dbb5713-109f-41c9-8d4a-628f840520af" />

## 4. Analysis Tools

## 5. LET correction

# Troubleshooting
- *In case of problems, try deleting the image inside the apptainer folder and try again*
- *please make the shell (.sh) files executable by running:*
`chmod +x setup.sh` and `chmod +x run_app.sh`
- *In case you get long errors (that might be related to file watching) when running without a linux container-(apptainer), please delete the apptainer folder (dont worry - it can be generated back with the setup.sh file) and try again*

# Comments
- Evaluation function are located in `libs/evaluation_funcs.py`
- The Main deconvolution class is located in libs/deconvolute.py
- Run_ui.py takes care of plotting, however older libraries are kept for backwards compatibility
