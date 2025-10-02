import streamlit as st
import os
import glob
from io import BytesIO
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
import uuid
import json

# It's good practice to group custom library imports
# Make sure 'libs' is in the Python path
from .evaluation_funcs import (
    calculate_center_mean_per_slice, 
    save_and_plot_doses, 
    Lateral_profile, 
    Vertical_profile,
    return_let_corrected
)

# --- Utility and Plotting Functions ---

def import_from_json(json_file):
    """Imports ROIs from a JSON file."""
    data = json.load(json_file)
    params = data.get('params', {})
    rois = data.get('rois', {})
    shape_roi = data.get('shape_roi', [])
    return params, rois, shape_roi

def roi_image_plotter(image_data, rois):
    """Uses Matplotlib to plot an image with ROIs and returns a buffer."""
    if not isinstance(image_data, np.ndarray):
        image_data = image_data.cpu().numpy()

    fig, ax = plt.subplots(figsize=(5, 5))
    log = st.checkbox("Logarithmic Color Scale", value=False)
    
    if log:
        ax.imshow(image_data, cmap="jet", interpolation=None, norm="log")
    else:
        ax.imshow(image_data, cmap="jet", vmin=0, vmax=65000, interpolation=None)
    
    for crop in rois:
        ax.plot([crop[2], crop[3], crop[3], crop[2], crop[2]],
                [crop[0], crop[0], crop[1], crop[1], crop[0]], 
                linewidth=0.5)
    
    buf = BytesIO()
    fig.savefig(buf, format="png", bbox_inches='tight', pad_inches=0)
    buf.seek(0)
    plt.close(fig)
    return buf

def interactive_tomographic_viewer(data_3d, key_prefix, c_log=False):
    """Displays a 3D numpy array with interactive slice viewers."""
    if not isinstance(data_3d, np.ndarray):
        data_3d = data_3d.cpu().numpy()

    norm = LogNorm() if c_log else None
    
    # Use unique keys for session state
    z_key, y_key, x_key = f'{key_prefix}_z', f'{key_prefix}_y', f'{key_prefix}_x'

    # Initialize slice indices in session state if they don't exist
    st.session_state.setdefault(z_key, 0)
    st.session_state.setdefault(y_key, data_3d.shape[1] // 2)
    st.session_state.setdefault(x_key, data_3d.shape[2] // 2)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.session_state[x_key] = st.slider('X-Slice', 0, data_3d.shape[2] - 1, st.session_state[x_key], key=f"{key_prefix}_slider_x")
    with col2:
        st.session_state[y_key] = st.slider('Y-Slice', 0, data_3d.shape[1] - 1, st.session_state[y_key], key=f"{key_prefix}_slider_y")
    with col3:
        # Z-slice can also be interactive if needed
        st.session_state[z_key] = st.slider('Z-Slice', 0, data_3d.shape[0] - 1, st.session_state[z_key], key=f"{key_prefix}_slider_z")

    fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(15, 5))

    # X-Slice
    ax1.set_title(f'X-Slice: {st.session_state[x_key]}')
    ax1.imshow(data_3d[:, :, st.session_state[x_key]], cmap='jet', origin='lower', aspect='auto', norm=norm)
    ax1.axhline(y=st.session_state[z_key], color='r', linestyle='--'); ax1.axvline(x=st.session_state[y_key], color='r', linestyle='--')
    ax1.set_xlabel('Y-axis'); ax1.set_ylabel('Z-axis')

    # Y-Slice
    ax2.set_title(f'Y-Slice: {st.session_state[y_key]}')
    ax2.imshow(data_3d[:, st.session_state[y_key], :], cmap='jet', origin='lower', aspect='auto', norm=norm)
    ax2.axhline(y=st.session_state[z_key], color='r', linestyle='--'); ax2.axvline(x=st.session_state[x_key], color='r', linestyle='--')
    ax2.set_xlabel('X-axis'); ax2.set_ylabel('Z-axis')

    # Z-Slice
    ax3.set_title(f'Z-Slice: {st.session_state[z_key]}')
    ax3.imshow(data_3d[st.session_state[z_key], :, :], cmap='jet', origin='lower', aspect='auto', norm=norm)
    ax3.axhline(y=st.session_state[y_key], color='r', linestyle='--'); ax3.axvline(x=st.session_state[x_key], color='r', linestyle='--')
    ax3.set_xlabel('X-axis'); ax3.set_ylabel('Y-axis')

    # fig.tight_layout()
    st.pyplot(fig, use_container_width=False)
    plt.close(fig)

def interactive_camera_viewer(cam_pics, key_prefix=None):
    """
    A Streamlit-native version of the Camera_picture_viewer.
    Displays four camera images with interactive controls for color mapping.
    """
    if key_prefix is None:
        key_prefix = uuid.uuid4().hex

    cam_pic_front, cam_pic_top, cam_pic_120, cam_pic_240 = [p.cpu().numpy() for p in cam_pics]

    # --- Widget Controls ---
    st.write("Use the controls below to adjust the image display.")
    c_log = st.checkbox("Logarithmic Color Scale", key=f"{key_prefix}_log_scale")
    
    # Use a range slider for vmin and vmax
    min_val, max_val = st.slider(
        "Color Range (vmin, vmax)",
        min_value=0,
        max_value=65535,
        value=(0, 65535),
        key=f"{key_prefix}_color_range"
    )

    # --- Plotting ---
    fig, ((ax1, ax2, ax3, ax4)) = plt.subplots(1, 4, figsize=(12, 5))

    imshow_args = {
        'origin': 'upper',
        'aspect': 'equal',
        'cmap': 'jet'
    }
    
    if c_log:
        imshow_args['norm'] = LogNorm(vmin=max(1, min_val), vmax=max_val)
    else:
        # For linear scale, pass vmin/vmax directly.
        imshow_args['vmin'] = min_val
        imshow_args['vmax'] = max_val
        
    # Top camera
    ax1.set_title('Top camera')
    ax1.imshow(cam_pic_top, **imshow_args)

    # 120 camera
    ax2.set_title('120° camera')
    ax2.imshow(cam_pic_120, **imshow_args)

    # 240 camera
    ax3.set_title('240° camera')
    ax3.imshow(cam_pic_240, **imshow_args)

    # Front camera
    ax4.set_title('Front camera')
    im = ax4.imshow(cam_pic_front, **imshow_args)

    fig.colorbar(im, ax=ax4, label='Intensity', orientation='vertical', fraction=0.046, pad=0.04)
    
    fig.tight_layout()
    st.pyplot(fig, use_container_width=False)
    plt.close(fig)

# --- UI Rendering Functions ---

def render_sidebar(data_dir):
    """Renders the sidebar and returns user selections."""
    with st.sidebar:
        mode = st.selectbox("Select Mode", ["online", "offline"], index=0)
        file_loc = st.text_input(
            "Path to input files:",
            value=os.path.join(data_dir, mode, 'input')
        )
        
        st.markdown("#### Select Image for Processing")
        selected_image_path = None
        st.markdown(f"File LOcation: {file_loc}")
        if os.path.isdir(file_loc):
            try:
                file_paths = glob.glob(os.path.join(file_loc, "*.tif")) + glob.glob(os.path.join(file_loc, "*original.png"))
                file_paths.sort(key=os.path.getmtime, reverse=True)
                file_names = [os.path.basename(path) for path in file_paths]
                
                if not file_names:
                    st.warning("No .tif files found in the specified directory.")
                    return None, None, None

                selected_file = st.radio("Select one image:", file_names, key="image_radio")
                selected_image_path = os.path.join(file_loc, selected_file)

                # Clear previous results if the image changes
                if st.session_state.get('previous_image') != selected_image_path:
                    if 'reconstruction_result' in st.session_state:
                        del st.session_state['reconstruction_result']
                    st.session_state['previous_image'] = selected_image_path

            except Exception as e:
                st.error(f"Error reading directory: {e}")
                return None, None, None
        else:
            st.warning(f"Directory not found: {file_loc}")

        # output_dir = os.path.join(data_dir, mode, 'output')
        output_dir = ""
        return selected_image_path, mode, output_dir

def render_results(reconstruction_result, deconvoluter, params, shape_side):
    """
    Function to render the results of the reconstruction.
    Displays the reconstructed light distribution, analysis plots, and allows for LET correction.
    Args:
        reconstruction_result: The result of the reconstruction.
        deconvoluter: The Deconvolute object containing the reconstruction parameters.
        params: Dictionary containing parameters like resolution, ROI diameter, etc.
        shape_side: Tuple containing the shape of the side view.
    Returns:
        None
    This function uses Streamlit to display the results interactively.
    It includes:
        - An interactive viewer for the reconstructed light distribution.
        - Analysis plots for depth dose and lateral/vertical profiles.
        - Option to apply LET correction using a selected file.
    """

    with st.expander("**Reconstructed Light Distribution**", expanded=True):
        interactive_tomographic_viewer(reconstruction_result, key_prefix="rec_light")

    rec_light_dist_numpy = reconstruction_result.cpu().numpy()
    
    # Vectorized error calculation is much faster and cleaner
    mean_array, std, mask = calculate_center_mean_per_slice(
        rec_light_dist_numpy, 
        int((params['roi_diam'] / params['res']) / 2), 
        params['shift_roi_x'], 
        params['shift_roi_y']
    )
    
    q_err = mean_array * deconvoluter.q_err_rel
    err_abs = np.sqrt(q_err**2 + std**2)
    
    dist_3D = np.sum(rec_light_dist_numpy, axis=(1, 2))
    # ROI masked images
    dist_3D_mask = np.zeros(np.shape(rec_light_dist_numpy))
    for index, _ in enumerate(mean_array):
        img = rec_light_dist_numpy[index, :, :]
        dist_3D_mask[index, mask] = img[mask]

    with st.expander("**Masked 3D Distribution**", expanded=False):
        interactive_tomographic_viewer(dist_3D_mask / dist_3D_mask.max(), key_prefix="roi_masked", c_log=False)
    
    dose_plot_fig = save_and_plot_doses(deconvoluter.outdir, mean_array, std, dist_3D, params['res'], params['roi_diam'])
    st.header("Analysis Plots")
    col1, col2, col3 = st.columns(3)
    with col1, st.expander("**Depth Dose Plot**", expanded=True):
        st.pyplot(dose_plot_fig, use_container_width=True)
        plt.close(dose_plot_fig)

    # Add a slider for profile analysis to avoid magic numbers
    max_slice = rec_light_dist_numpy.shape[0] - 1

    with col2, st.expander("**Lateral Profile**", expanded=True):
        lat_profile_slice = st.slider("Slice for Lateral Profile", 0, max_slice, 10)
        thickness_l = st.number_input("Thickness (mm)", value=20, step=1, key="thickness_l")
        position_adj_l = st.number_input("Position Adjustment (pixels)", value=-8, step=1, key="position_adj_l")
        lat_figs, _, _ = Lateral_profile(deconvoluter.outdir, rec_light_dist_numpy[lat_profile_slice,:,:], thickness_l, position_adj_l, params['res'], deconvoluter.q_err_rel)
        for fig in lat_figs:
            st.pyplot(fig, use_container_width=True)
            plt.close(fig)

    with col3, st.expander("**Vertical Profile**", expanded=True):
        vert_profile_slice = st.slider("Slice for Vertical Profile", 0, max_slice, 10)
        thickness_v = st.number_input("Thickness (mm)", value=20, step=1, key="thickness_v")
        position_adj_v = st.number_input("Position Adjustment (pixels)", value=-8, step=1, key="position_adj_v")
        vert_figs, _, _ = Vertical_profile(deconvoluter.outdir, rec_light_dist_numpy[vert_profile_slice,:,:], thickness_v, position_adj_v, params['res'], deconvoluter.q_err_rel)
        for fig in vert_figs:
            st.pyplot(fig, use_container_width=True)
            plt.close(fig)

    # Do LET correction
    st.header("LET CORRECTION")
    do_let = st.toggle("Rerun with LET correction", value=False)
    if do_let:
        let_folder_loc = st.text_input(
            "Path to input topaz file for let correction:",
            value="/home/rawdata/2025/2025_08_21/miniSCIDOM/LET"
            # value=os.path.join(os.path.dirname(__file__), '..', 'extra_data', 'let_correction')
        )
    
        # Input field for "Adjusted Start" which sets the 'Term' variable
        term = st.number_input("Adjusted Start (in miniSCIDOM Thickness) Note: 0.221475 is for First 3 Pixels", value=0.221475, help="This value will be used as 'Term' in evaluation_funcs", format="%.6f")
    
        st.markdown("#### Select Folder for Processing")
        if os.path.isdir(let_folder_loc):
            try:
                if os.path.isdir(let_folder_loc):
                    file_paths = glob.glob(os.path.join(let_folder_loc, "*LET*.csv")) + glob.glob(os.path.join(let_folder_loc, "*LET*.npy"))
                    file_paths.sort(key=os.path.getmtime, reverse=True)
                    file_names = [os.path.basename(path) for path in file_paths]

                    if not file_names:
                        st.warning("No LET correction files (.csv or .npy) found in the selected folder.")
                    else:
                        selected_file = st.radio("Select one let correction file:", file_names, key="let_radio")
                        selected_let_file = os.path.join(let_folder_loc, selected_file)


                        fig = return_let_corrected(selected_let_file, reconstruction_result.cpu().numpy(), mean_array,
                                                params, shape_side,
                                                deconvoluter.outdir, deconvoluter.q_err_rel, term_input = term)

                        st.pyplot(fig, use_container_width=False)
                        st.success("LET correction applied successfully!")
    
            except Exception as e:
                st.error(f"Error reading directory: {e}")
        else:
            st.warning(f"Directory not found: {let_folder_loc}")            
    # do_let = st.checkbox("Rerun with LET correction", value=False)
    # if do_let:
    #     let_folder_loc = st.text_input(
    #         "Path to input topaz file for let correction:",
    #         value=os.path.join(os.path.dirname(__file__), '..', 'extra_data', 'let_correction')
    #         )
    
    #     st.markdown("#### Select Folder for Processing")
    #     folders = os.listdir(let_folder_loc)
    #     selected_folder = st.radio("Select a folder:", folders, key="folder_select")
    #     let_file_loc = os.path.join(let_folder_loc, selected_folder)
    #     if os.path.isdir(let_file_loc):
    #         try:
    #             file_paths = glob.glob(os.path.join(let_file_loc, "*LET*.csv")) + glob.glob(os.path.join(let_file_loc, "*LET*.npy"))
    #             file_paths.sort(key=os.path.getmtime, reverse=True)
    #             file_names = [os.path.basename(path) for path in file_paths]
                
    #             if not file_names:
    #                 st.warning("No .csv files found in the specified directory.")
    #                 return None, None, None

    #             selected_file = st.radio("Select one let correction file:", file_names, key="let_radio")
    #             selected_let_file = os.path.join(let_file_loc, selected_file)
    #         except Exception as e:
    #             st.error(f"Error reading directory: {e}")
    #             return None, None, None
    #     else:
    #         st.warning(f"Directory not found: {let_folder_loc}")

    #     print(f"Using LET file: {selected_let_file}")

    #     fig = return_let_corrected(selected_let_file, reconstruction_result.cpu().numpy(), mean_array,
    #                             params, shape_side, 
    #                             deconvoluter.outdir, deconvoluter.q_err_rel)
        
    #     st.pyplot(fig, use_container_width=False)
    #     st.success("LET correction applied successfully!")
