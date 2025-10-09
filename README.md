# Introduction
The following library performs image reconstruction from the miniSCIDOM detector using PyTorch for faster computations. The original code for the reconstruction was written by *Angela Corvino and Marvin Reimold* (https://github.com/AngelaCorvino/MiniSCIDOM).

Corresponding publication: https://www.cambridge.org/core/journals/high-power-laser-science-and-engineering/article/miniscidom-a-scintillatorbased-tomograph-for-volumetric-dose-reconstruction-of-single-laserdriven-proton-bunches/171051DA9A4C1744E0020F783F1381D1

# Requirements (defined in 'environment.yaml')
- `streamlit`
- `pytorch`
- `scipy`
- `scikit`
- `opencv`
- `kornia`
- `fft-conv-pytorch`
- `tifffile`
- `torchmetrics`
# Running the code
## Running the UI Locally
Run the UI using (make sure to have all necessary packages installed in your Python environment)
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

- `setup.sh` - setup up the necessary containers and Python packages to be used for a standalone functioning. **Can take quite a while**
- `run_app.sh` - verify all the installation files and run the zrok application.

- Before running zrok, please create an account on `myzrok.io`, get the account token from `api-v1.zrok.io`, and save it in the zrok.env file in the main directory.

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
- Input the directory of your raw image or place it in the default directory and select the image you want to reconstruct.
- An example image ("example_img.tif") is provided. 

<img width="256" height="355" alt="image" src="https://github.com/user-attachments/assets/daa0f0b8-ca13-4bae-b1de-9a82cb6c74c5" />

## 2. Parameter Settings:
- Different parameters have to be set correctly for an accurate reconstruction
- Firstly, the resolution in mm/pixel depends on the camera which is used (Default: PCO Pixelfly 4.2)
- Efficiency factor can be used if an optical filter was placed in front of the objective, i.e, an OD1 filter with a transmission of 10%. To make the signal level comparable (to the setting without a filter), one would put in 0.1 for the efficiency factor
- The ROI diameter describes the size of a circular mask that is placed over the reconstruction and in which the depth dose distribution will be calculated. The ROI can be shifted in the x and y plane by adjusting "Shift ROI X/Y (pixels). 

<img width="1510" height="357" alt="image" src="https://github.com/user-attachments/assets/9b50afa4-25bd-4c53-9c82-c327e8657148" />

## 3. Reconstruction
- The selected image will be shown.
- Now the placement of the region of interest (ROI) has to be set for each of the 4 projections.
  - One can toggle a logarithmic color scale for the plot of the image to better visualize the edges of the projections
  - Under Shape Front: The height and the width of the Side and Front ROI's can be changed and thus increase or decrease the reconstruction volume. Typically, it is easier to reconstruct a smaller volume; however, this also depends on the dose distribution.
  - The position of the individual ROIs is shown in the plot of the loaded image. The precise position is crucial for a good and accurate 3D reconstruction (shifting the ROI by a few pixels can make a huge difference).
  - Under the different tabs ("Front", "Top", "120°", and "240°"), one can set the position of the scale
- When done setting the ROI positions, one presses "Run Reconstruction and Save ROI's"
- An indication of how accurate your reconstruction is is the "Quotients from the reconstruction". They basically showcase your error of the reconstruction, so one aims to get this quotient for all 4 projections to 1±0.05 by the 4th iteration for a 5% error.
- So this takes a few tries: Reconstruct --> Check Quotient and Reconstruction --> Adjust ROI positions --> and so on, until you are pleased with the result

<img width="1518" height="936" alt="image" src="https://github.com/user-attachments/assets/b77ca843-5640-4064-a3ec-949b798fec8b" />

- If you have previously reconstructed an image and want to do the reconstruction again, you can drag and drop the .json file, which is automatically created during the reconstruction and saved in the output folder, into the overlay. This will load the ROI positions and parameter settings that were used for the reconstruction of that image

<img width="1521" height="138" alt="image" src="https://github.com/user-attachments/assets/7dbb5713-109f-41c9-8d4a-628f840520af" />

## 4. Analysis Tools
- After reconstruction, one can have a lot at the reconstructed 3D light/dose distribution. This is a tomographic viewer with which one can look at the different slices of the 3D dose distribution.
- As well as the position of the circular ROI under "Masked 3D Distribution"

<img width="779" height="922" alt="image" src="https://github.com/user-attachments/assets/5ad14392-98b9-472b-8073-3b3515c46bce" />

- Under "Analysis Plot" one can see the plotted depth dose distribution, which is calculated by taking the mean signal value inside the circular masked ROI

<img width="510" height="535" alt="image" src="https://github.com/user-attachments/assets/f73208a5-dc90-41c1-82f3-16ff0820e8bd" />

- Furthermore, one can evaluate the lateral and vertical profile of individual slices 

<img width="504" height="745" alt="image" src="https://github.com/user-attachments/assets/374b856f-f9ce-41d4-a66d-07bd8521327d" />

- All these curves will be saved to the output folder

## 5. LET correction
- For correcting the LET, one first has to simulate the track-averaged LET inside the miniSCIDOM with the corresponding particle spectrum that was used during the irradiation
- The code can directly read the output file from Topas (.csv) as well as 1D arrays (.npy)
- Be aware that the bin length of the LET correction is hard-coded in "evaluation_funcs.py" in the "return_let_corrected" function in the variable "bin_length_zletprofile". This bin length has to be adjusted to fit the resolution of your LET simulation data
```  
def return_let_corrected(outputfile_topas, rec_light_dist, mean_array, params, shape_side, outdir, q_err_rel, term_input):
  
    s = params['res']
    ROI_diam = params['roi_diam']
    shift_ROI_x = params['shift_roi_x']
    shift_ROI_y = params['shift_roi_y']
    
    bin_length_zletprofile = 0.0806452
```
- The "Adjusted Start" is important to define where the reconstruction starts. For example, your ROI for (Front, 120° and 240°) is not placed directly at the edge of the scintillator, but 3 pixels further in for a nicer reconstruction. This has to be considered so your simulated LET curve aligns with the reconstructed volume  
<img width="798" height="921" alt="image" src="https://github.com/user-attachments/assets/7706e674-be5e-4587-9655-755ea833501e" />


## 6. Output files
- An Output folder with the same name as the image will be created, containing the following files
- ROI_Data.json
  - Containing all the ROI and other parameters used for the reconstruction
  - can be dragged and dropped into the UI to apply it to an Image
- rec_light_dist.npy / .tif
  - 3D array of the reconstructed light/dose distribution
  - .tif file saved for quick viewing in i.e., ImageJ
- depthdose.png
  - Depth dose distribution calculated by the mean dose inside the circular ROI (purple curve)
- ROI_mean.npz
  - corresponding data to the depth dose curve containing dose and error values
- vertical_profile_data.npz
- lateral_profile_data.npz
- quenching_corr_rec_light_dist.npy / .tif
- quenching_corr_depthdose.png
- quenching_corr_ROI_mean.npz

# Troubleshooting
- *In case of problems, try deleting the image inside the apptainer folder and try again*
- *please make the shell (.sh) files executable by running:*
`chmod +x setup.sh` and `chmod +x run_app.sh`
- *In case you get long errors (that might be related to file watching) when running without a linux container-(apptainer), please delete the apptainer folder (don't worry - it can be generated back with the setup.sh file) and try again*

# Comments
- Evaluation functions are located in `libs/evaluation_funcs.py`
- The Main deconvolution class is located in libs/deconvolute.py
- Run_ui.py takes care of plotting, however, older libraries are kept for backwards compatibility
