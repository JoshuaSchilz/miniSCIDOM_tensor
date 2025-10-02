import numpy as np
import matplotlib.pyplot as plt
import torch
import os
from Birkmodel import lightcorrection, dosecorrection
import pandas as pd
from getprofile import Get_profile

def calculate_center_mean_per_slice(arr, radius, shift_x=0, shift_y=0):
    center = np.array(arr.shape) // 2
    
    # Initialize an array to store the mean values per slice
    mean_values_per_slice = np.zeros(arr.shape[0])
    mean_std_per_slice = np.zeros(arr.shape[0])

    for i in range(arr.shape[0]):
        # Create a meshgrid of indices for the current slice
        y, x = np.ogrid[:arr.shape[1], :arr.shape[2]]
        
        # Adjust the center based on the shift values
        shifted_center_x = center[2] + shift_x
        shifted_center_y = center[1] + shift_y
        
        # Calculate the distance of each point from the shifted center
        distance = np.sqrt((x - shifted_center_x) ** 2 + (y - shifted_center_y) ** 2)
        
        # Create a mask for points within the specified radius
        mask = distance <= radius
        
        # Extract values within the circular region for each slice
        circular_region = arr[i, mask]
        
        # Calculate the mean and standard deviation of the circular region for this slice
        mean_values_per_slice[i] = np.mean(circular_region)
        mean_std_per_slice[i] = np.std(circular_region)
    
    return mean_values_per_slice, mean_std_per_slice, mask


def calculate_rings_mean_std_per_slice(arr, radius, num_rings):
    center = np.array(arr.shape) // 2
    mean_values_per_slice = np.zeros((arr.shape[0], num_rings))
    mean_std_per_slice = np.zeros((arr.shape[0], num_rings))

    for i in range(arr.shape[0]):
        y, x = np.ogrid[:arr.shape[1], :arr.shape[2]]
        distance = np.sqrt((x - center[2]) ** 2 + (y - center[1]) ** 2)
        
        # Create a mask for points within the specified radius
        mask = distance <= radius
        
        # Divide the circular region into rings
        ring_width = radius / num_rings
        ring_masks = [(distance >= j * ring_width) & (distance <= (j + 1) * ring_width) for j in range(num_rings)]
        
        # Calculate mean and standard deviation for each ring
        for j, ring_mask in enumerate(ring_masks):
            ring_values = arr[i, ring_mask]
            mean_values_per_slice[i, j] = np.mean(ring_values)
            mean_std_per_slice[i, j] = np.std(ring_values)

    return mean_values_per_slice, mean_std_per_slice, distance, ring_masks

def calculate_center_sum_per_slice(arr, radius):
    center = np.array(arr.shape) // 2
    # Initialize an array to store the mean values per slice
    mean_values_per_slice = np.zeros(arr.shape[0])

    for i in range(arr.shape[0]):
        # Create a meshgrid of indices for the current slice
        y, x = np.ogrid[:arr.shape[1], :arr.shape[2]]
        
        # Calculate the distance of each point from the center
        distance = np.sqrt((x - center[2]) ** 2 + (y - center[1]) ** 2)
        
        # Create a mask for points within the specified radius
        mask = distance <= radius
        
        # Extract values within the circular region for each slice
        circular_region = arr[i, mask]
        
        # Calculate the mean and standard deviation of the circular region for this slice
        mean_values_per_slice[i] = np.sum(circular_region)

    return mean_values_per_slice


def Vertical_profile(outdir, image_array, thick, pos, s, q_err):
    # Flip the image vertically
    image_array = np.flip(image_array, axis=0)
    q_err_rel = q_err
    # Get the dimensions of the image
    height, width = image_array.shape
    
    # Determine the middle column of the image
    middle_col = width // 2 + pos
    
    # Initialize an empty list to store the mean intensity values
    mean_intensity_values = []
    std_vert_values = []
    std_error_values = []
    
    # Calculate the mean intensity over a `thick`-pixel thickness in the x-direction for every y-value
    for i in range(height):
        mean_intensity = np.sum(image_array[i, middle_col - int(thick/2): middle_col + int(thick/2)])
        mean_intensity_values.append(mean_intensity)
        std_vert = np.std(image_array[i, middle_col - int(thick/2): middle_col + int(thick/2)])
        std_vert_values.append(std_vert)
        std_error = std_vert / np.sqrt(len(image_array[i, middle_col - int(thick/2): middle_col + int(thick/2)]))
        std_error_values.append(std_error)
    
    # Plot the selected region on the image
    fig0, ax0 = plt.subplots(figsize=(10, 5))
    ax0.imshow(image_array, cmap='jet')
    ax0.axvline(x=middle_col - int(thick/2), color='r', linestyle='-', label='Profile Location')
    ax0.axvline(x=middle_col + int(thick/2), color='r', linestyle='-')
    ax0.set_title('Vertical Intensity Profile position')
    ax0.set_xlabel('Pixel Position')
    ax0.set_ylabel('Pixel Position')
    ax0.legend()
    
    # Normalize the mean intensity values for plotting
    normalized_intensity_values = np.array(mean_intensity_values) / np.max(mean_intensity_values)
    std_vert_values = np.array(std_vert_values) / np.max(mean_intensity_values)
    std_vert_mean = np.mean(std_vert_values)
    std_vert_error = np.array(std_error_values) / np.max(std_error_values)
    q_err_vert = np.zeros(len(normalized_intensity_values))
    for i in range(0, len(normalized_intensity_values)):
        q_err_vert[i] = normalized_intensity_values[i] * q_err_rel
    
    # Calculate together with std
    print("Hintergrundfehler Vertical", normalized_intensity_values[1])
    err_abs_vert = np.zeros(len(normalized_intensity_values))
    for i in range(0, len(normalized_intensity_values)):
        err_abs_vert[i] = np.sqrt((q_err_vert[i]**2)+(std_vert_values[i]**2)+normalized_intensity_values[1]**2)
    
    y_values = np.arange(0, len(normalized_intensity_values), 1) * s
    
    # Plot the vertical intensity profile with error bounds
    fig1, ax1 = plt.subplots(figsize=(10, 5))
    ax1.plot(y_values, normalized_intensity_values, label='Intensity Profile', color='b')
    # Fill between the error bounds
    ax1.fill_between(y_values, 
                    normalized_intensity_values - err_abs_vert, 
                    normalized_intensity_values + err_abs_vert, 
                    color='b', alpha=0.3, label='Error Bounds')
    
    # Formatting the plot
    ax1.set_title(f'Vertical Profile (Thickness: {round(thick/(1/s),2)}mm)')
    ax1.set_xlabel('y_position [mm]')
    ax1.set_ylabel('Normalized Intensity')
    ax1.set_xlim(0, len(normalized_intensity_values) * s)
    ax1.legend()

    np.savez(f'{outdir}/vertical_profile_data.npz', y_values=y_values, 
            intensity=normalized_intensity_values, 
            error=err_abs_vert)

    return [fig0, fig1], mean_intensity_values, height

def Lateral_profile(outdir, image_array, thick, pos, s, q_err):
    # Flip the image vertically
    image_array = np.flip(image_array, axis=0)
    q_err_rel = q_err
    # Get the dimensions of the image
    height, width = image_array.shape
    
    # Determine the middle row of the image
    middle_row = height // 2 + pos
    
    # Initialize an empty list to store the mean intensity values
    mean_intensity_values = []
    std_lat_values = []
    std_error_values = []
    # Calculate the mean intensity over a `thick`-pixel thickness in the y-direction for every x-value
    for i in range(width):
        mean_intensity = np.sum(image_array[middle_row - int(thick/2): middle_row + int(thick/2), i])
        mean_intensity_values.append(mean_intensity)
        std_lat = np.std(image_array[middle_row - int(thick/2): middle_row + int(thick/2), i])
        std_lat_values.append(std_lat)
        std_error = std_lat / np.sqrt(len(image_array[middle_row - int(thick/2): middle_row + int(thick/2), i]))
        std_error_values.append(std_error)
    
    # Plot the selected region on the image
    fig0, ax0 = plt.subplots(figsize=(10, 5))
    ax0.imshow(image_array, cmap='jet')
    ax0.axhline(y=middle_row - int(thick/2), color='r', linestyle='-', label='Profile Location')
    ax0.axhline(y=middle_row + int(thick/2), color='r', linestyle='-')
    ax0.set_title('Lateral Intensity Profile position')
    ax0.set_xlabel('Pixel Position')
    ax0.set_ylabel('Pixel Position')
    ax0.legend()
    # plt.show()
    
    # Normalize the mean intensity values for plotting
    normalized_intensity_values = np.array(mean_intensity_values) / np.max(mean_intensity_values)
    std_lat_values = np.array(std_lat_values) / np.max(mean_intensity_values)
    std_lat_mean = np.mean(std_lat_values)
    std_lat_error = np.array(std_error_values) / np.max(std_error_values)
    q_err_lat = np.zeros(len(normalized_intensity_values))
    for i in range (0,len(normalized_intensity_values)):
        q_err_lat[i] = normalized_intensity_values[i] * q_err_rel
    # calculate together with std 
    print("Hintergrundfehler Lateral", normalized_intensity_values[1])
    err_abs_lat = np.zeros(len(normalized_intensity_values))
    for i in range (0,len(normalized_intensity_values)):
        err_abs_lat[i] = np.sqrt((q_err_lat[i]**2)+(std_lat_values[i]**2)+normalized_intensity_values[1]**2)
        #err_abs_lat[i] = np.sqrt((q_err_lat[i]**2)+((normalized_intensity_values[i]*std_lat_mean)**2))
    
    x_values = np.arange(0, len(normalized_intensity_values), 1) * s
    # Plot the lateral intensity profile
    fig1, ax1 = plt.subplots(figsize=(10, 5))
    ax1.plot(x_values, normalized_intensity_values, label='Intensity Profile', color='b')
    # Fill between the error bounds
    ax1.fill_between(x_values, 
                     normalized_intensity_values - err_abs_lat, 
                     normalized_intensity_values + err_abs_lat, 
                     color='b', alpha=0.3, label='Error Bounds')

    # Formatting the plot
    ax1.set_title(f'Lateral Profile (Thickness: {round(thick/(1/s),2)}mm)')
    ax1.set_xlabel('x_position [mm]')
    ax1.set_ylabel('Normalized Intensity')
    ax1.set_xlim(0, len(normalized_intensity_values) * s)
    ax1.legend()
    # plt.show()
    
    np.savez(f'{outdir}/lateral_profile_data.npz', x_values=x_values, 
         intensity=normalized_intensity_values, 
         error=err_abs_lat)
    
    return [fig0, fig1], mean_intensity_values, width

def save_and_plot_doses(outdir, mean_array, err_abs, dist_3D, s, ROI_diam):
    normalization_factor = 133
    conversion_factor = 1  # Conversion factor for WET to Gy, adjust as needed
    save_directory_notnormalized = os.path.join(outdir, "notnormalized_lineout")
    isExist = os.path.exists(save_directory_notnormalized)
    if not isExist:
        os.makedirs(save_directory_notnormalized)

    np.save(save_directory_notnormalized + "notnormalizedmean_array", mean_array / normalization_factor)
    np.save(save_directory_notnormalized + "notnormalizederr", err_abs / normalization_factor)
    np.save(save_directory_notnormalized + "notnormalizedmean_array_notmasked", dist_3D)

    fig, ax = plt.subplots(figsize=(3, 3))

    ax.plot(
        np.arange(0, len(mean_array), 1) * s * conversion_factor,
        mean_array / normalization_factor,
        color="tab:purple",
        label="3D masked image",
        linewidth=1
    )
    ax.fill_between(
        np.arange(0, len(mean_array), 1) * s * conversion_factor,
        mean_array / normalization_factor + (err_abs / normalization_factor),
        mean_array / normalization_factor - (err_abs / normalization_factor),
        color='tab:purple',
        alpha = 0.5,
    ) 
    ax.set_title('Not normalized depth dose distr. |  ⌀ ROI = {} mm'.format(ROI_diam), fontsize=7)
    ax.set_xlabel('Depth [mm]', fontsize=7)
    ax.set_ylabel('Signal (Gy)', fontsize=7)
    ax.legend(fontsize=7)
    ax.grid(True)
    ax.tick_params(axis='both', which='major', labelsize=5)
    plt.minorticks_on()
    
    return fig

def letcorrection_function(mean_array, zletprofile, s):
    """
    Function for correcting 2D slices using LET correction simulations in a scintillator.

    Parameters:
    - mean_array: 3D data matrix (e.g., pixel values)
    - zletprofile: Simulated LET profile in the scintillator
    - s: Scaling factor

    Returns:
    - light_correction: Corrected light output
    """
    # Constants for LET correction simulations
    dscintillator = 1.023  # [g/cm^3] scintillator density
    dactivelayer = 1.2     # [g/cm^3] active layer density
    k = 207 / 10000        # [g/MeV cm^2]
    a = 0.9                # Scintillator efficiency
    dx = 65                # [µm] scintillator spatial resolution
    ddx = 1                # Spatial resolution error
    k = k / dscintillator * 10  # [micrometers/keV]

    # Simulated LET in scintillator starting from TOF data
    zletprofile[0] = zletprofile[1]  # Replace the first value to avoid interpolation issues
    ys_ana_mini = zletprofile

    # Interpolate LET profile to match the dimensions of the mean array
    S_a_mini = np.interp(
        np.arange(0, len(mean_array), 1) * s,
        np.arange(0, len(zletprofile), 1) * s,
        ys_ana_mini
    )

    # Correct mean pixel values using dose correction
    P_a_mini = dosecorrection(mean_array, S_a_mini, a, k, dx)
    # Compute the light correction using the interpolated LET profile
    light_correction = lightcorrection(S_a_mini, a, k, dx)
    return light_correction


def return_let_corrected(outputfile_topas, rec_light_dist, mean_array, params, shape_side, outdir, q_err_rel, term_input):
    
    s = params['res']
    ROI_diam = params['roi_diam']
    shift_ROI_x = params['shift_roi_x']
    shift_ROI_y = params['shift_roi_y']
    
    bin_length_zletprofile = 0.0806452
    term = term_input# + 0.221 # Adjusted Thickness to align LET Correction Properly to the measured curve 
    
    # Compute spatial positions
    mean_array_positions = np.arange(len(mean_array)) * s
    
    if outputfile_topas.endswith(".csv"):
        header = pd.read_csv(outputfile_topas, nrows=7)
        df = pd.read_csv(outputfile_topas, comment="#", header=None)
        topas_datamatrix = np.array(df)  # convert dataframe df to array
        letprofile = Get_profile(topas_datamatrix, shape_side[0], 1)
        zletprofile = letprofile.zmeanprofile[5:]
    else:
        zletprofile = np.load(outputfile_topas, allow_pickle=True)
    
    zletprofile_positions = np.arange(len(zletprofile)) * bin_length_zletprofile - term # adjustment for depth dose start
    # Interpolate zletprofile to match mean_array positions
    zletprofile_resampled = np.interp(mean_array_positions, zletprofile_positions, zletprofile)        
    lightcorrection_value = letcorrection_function(mean_array, zletprofile_resampled, s)    
    
    matrix_3D_corrected = np.zeros(
        np.shape(rec_light_dist)
    )  # ((deltaz, 186, 152) z is the first =deltaz

    for i in range(np.shape(rec_light_dist)[0]):  # from 0 to 158
        matrix_3D_corrected[i, :, :] = np.divide(
            rec_light_dist[i, :, :],
            lightcorrection_value[i],
            out=np.zeros_like(rec_light_dist[i, :, :]),
            where=lightcorrection_value[i] != 0,
        )

    calib_value = 1 
    matrix_3D_corrected_calib=matrix_3D_corrected*calib_value
    np.savez(f"{outdir}/light_dist_quenching_corr.npz", matrix_3D_corrected_calib=matrix_3D_corrected_calib)
    
    # ==== Plot 1D mean =====
    mean_array_qk, std_qk, mask = calculate_center_mean_per_slice(matrix_3D_corrected_calib, int((ROI_diam/s)/2), shift_ROI_x,shift_ROI_y)
    
    deltaz = shape_side[0]
    q_err_qk = np.zeros((deltaz))
    for i in range (0,len(mean_array_qk)):
        q_err_qk[i] = mean_array_qk[i] * q_err_rel
    # calculate together with std 

    err_abs_qk = np.zeros((deltaz))
    for i in range (0,len(mean_array_qk)):
        err_abs_qk[i] = np.sqrt((q_err_qk[i]**2)+(std_qk[i]**2))
    
    adj_d = term * 1.045 + 0.01 #+0.1 for 10um pokalon +0.2 WET for the PVC Black tape infront of miniSCIDOM, 0.221 = not taking the first 3 pixels
    
    fig, ax = plt.subplots(figsize=(3, 3))
    ax.plot(
        np.arange(0, len(mean_array_qk), 1) * s * 1.045 + adj_d, 
        mean_array_qk ,
        color="tab:blue",
        label="miniSCIDOM",
        zorder = 2,
    )
    ax.fill_between(
        np.arange(0, len(mean_array_qk), 1) * s * 1.045 + adj_d,
        mean_array_qk  + (err_abs_qk),
        mean_array_qk  - (err_abs_qk),
        color='tab:blue',
        alpha = 0.5,
        zorder=1,
    )

    ax.set_title('Quenching corrected mean depth dose distr. |  ⌀ ROI = {} mm'.format(ROI_diam), fontsize=6)
    ax.set_xlabel('Water equivalent depth [mm]', fontsize=8)
    ax.set_ylabel('Relative Dose [a.u.]', fontsize=8)
    ax.tick_params(axis='both', which='major', labelsize=8)
    #ax.set_ylim(0, 700)
    ax.set_xlim(0, 25)
    ax.legend(fontsize=8)
    #ax.grid(True)
    plt.minorticks_on()
    plt.savefig(f"{outdir}/depthdose_smart.png", dpi = 300)
    
    thickness = 19
    position_adj = 0
    # profile_values, width = Lateral_profile(matrix_3D_corrected_calib[49,:,:],thickness,position_adj, s, q_err_rel)
    
    x_values = np.arange(0, len(mean_array_qk), 1) * s * 1.045 + adj_d

    # Save as a .npz file (preferred for NumPy arrays)
    np.savez(f"{outdir}/quenching_corr_mean.npz", x=x_values, mean=mean_array_qk, err=err_abs_qk)

    return fig