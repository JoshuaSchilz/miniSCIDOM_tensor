import streamlit as st
import os
import glob
from io import BytesIO
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
import uuid
import pandas as pd
import json

# It's good practice to group custom library imports
# Make sure 'libs' is in the Python path
from libs.deconvolute import Deconvolute
from libs.image_loader import Image_loader
import json
from libs.ui_utils import (
    import_from_json,
    roi_image_plotter,
    interactive_tomographic_viewer,
    interactive_camera_viewer,
    render_sidebar,
    render_results
)

# --- Constants ---
BASE_PATH = os.path.dirname(__file__)
DATA_DIR = os.path.join(BASE_PATH, 'pictures')
output_dir = os.path.join(BASE_PATH, "pictures/online/output/")

# --- Caching Functions ---
@st.cache_data
def load_deconvoluter(image_path, factor, outdir):
    """Caches the Deconvolute object creation."""
    return Deconvolute(image_path, factor, outdir=outdir)

# --- Main Application ---

def main():
    """Main function to run the Streamlit app."""
    st.set_page_config(page_title="miniSCIDOM Analysis", layout="wide")
    col1, col2 = st.columns([1,3])
    with col1:
        logo_path = os.path.join(BASE_PATH, "HZDR_logo.png")
        if os.path.exists(logo_path):
            st.image(logo_path, use_container_width=False, )
    with col2:
        st.title("miniSCIDOM Analysis Tool")

    os.makedirs(DATA_DIR, exist_ok=True)
    # output_dir defined here in the third return vars     
    selected_image, mode, _ = render_sidebar(DATA_DIR)
    if not selected_image:
        st.info("Please select a .tif image from the sidebar to begin.")
        st.stop()
    
    uploaded_file = st.file_uploader("Upload a JSON file for the parameters and ROI", type="json")
    if uploaded_file is not None:
        uploaded_data = json.load(uploaded_file)
        st.session_state["uploaded_data"] = uploaded_data
    else:
        uploaded_data = st.session_state.get("uploaded_data", {})
    
    # Main Section Parameters
    uploaded_params = uploaded_data.get("params", {})
    with st.expander("**Parameters**", expanded=False):
        st.write("Resolution (mm/pixel): Basler 60gm ≈ 0.0634 | pixelfly ≈ 0.073825")
        col1, col2 = st.columns(2)
        params = {
            'res': col1.number_input("Resolution", 
                                    value=uploaded_params.get('res', 0.073825), format="%.6f"),
            'roi_diam': col1.number_input("ROI Diameter (mm)", 
                                    value=uploaded_params.get('roi_diam' , 2.5), step=0.1),
            'img_rot_angle': col1.number_input("Image Rotation Angle (deg)", 
                                    value=uploaded_params.get('img_rot_angle' , 0.0), step=0.1),
            'factor': col2.number_input("Efficiency Factor", 
                                    value=uploaded_params.get('factor' , 1.0), format="%.6f"),
            'shift_roi_x': col2.number_input("Shift ROI X (pixels)", 
                                    value=uploaded_params.get('shift_roi_x' , 4), step=1),
            'shift_roi_y': col2.number_input("Shift ROI Y (pixels)", 
                                    value=uploaded_params.get('shift_roi_y' , -4), step=1) 
        }    
    
    outdir = os.path.join(output_dir, os.path.basename(selected_image)[:-4])
    deconvoluter = load_deconvoluter(selected_image, params['factor'], outdir)

    # --- ROI Settings - load from json if available---
    st.header("Region of Interest (ROI) Settings")
    uploaded_roi = uploaded_data.get("rois", {})
    uploaded_shape_roi = uploaded_data.get("shape_roi", [[150,110],[310,110]])
    front = uploaded_roi.get("front", [240, 0, 630, 0])
    top = uploaded_roi.get("top", [487, 0, 630, 0])
    _120 = uploaded_roi.get("120", [487, 0, 885, 0])
    _240 = uploaded_roi.get("240", [487, 0, 360, 0])
    with st.expander("**SETTINGS: Click to expand**", expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            st.write("**Shape Front**")
            sf_c1, sf_c2 = st.columns(2)
            shape_front_h = sf_c1.number_input("Height", value=uploaded_shape_roi[0][0], key="shape_front_h")
            shape_front_w = sf_c2.number_input("Width", value=uploaded_shape_roi[0][1], key="shape_front_w")

        with col2:
            st.write("**Shape Side**")
            ss_c1, ss_c2 = st.columns(2)
            shape_side_h = ss_c1.number_input("Height", value=uploaded_shape_roi[1][0], key="shape_side_h")
            shape_side_w = ss_c2.number_input("Width", value=uploaded_shape_roi[1][1], key="shape_side_w")
            
        tab_front, tab_top, tab_120, tab_240 = st.tabs(["Front", "Top", "120°", "240°"])
        with tab_front:
            uploaded_front = uploaded_roi.get("front",{})
            st.write("Define ROI for the **Front** image.")
            col1, col2 = st.columns(2)
            y1_front = col1.number_input("y1 (bottom)", key="y1_front", step=1, value=front[0])
            y2_front = col2.number_input("y2 (top) = y1 + shape front height + value", value=0, key="y2_front") + shape_front_h + y1_front
            x1_front = col1.number_input("x1 (left)", key="x1_front", step=1, value=front[2])
            x2_front = col2.number_input("x2 (right) = x2 + shape front width", value=0, key="x2_front") + shape_front_w + x1_front
        
        with tab_top:
            st.write("Define ROI for the **Top** image.")
            col1, col2 = st.columns(2)
            y1_top = col1.number_input("y1 (bottom)", key="y1_top", step=1, value=top[0])
            y2_top = col2.number_input("y2 (top) = y1 + shape side height + value", value=0, key="y2_top") + shape_side_h + y1_top
            x1_top = col1.number_input("x1 (left)", key="x1_top", step=1, value=top[2])
            x2_top = col2.number_input("x2 (right) = x2 + shape side width", value=0, key="x2_top") + shape_side_w + x1_top
        
        with tab_120:
            st.write("Define ROI for the **120°** image.")
            col1, col2 = st.columns(2)
            y1_120 = col1.number_input("y1 (bottom)", key="y1_120", step=1, value=_120[0])
            y2_120 = col2.number_input("y2 (top) = y1 + shape side height + value", value=0, key="y2_120") + shape_side_h + y1_120
            x1_120 = col1.number_input("x1 (left)", key="x1_120", step=1, value=_120[2])
            x2_120 = col2.number_input("x2 (right) = x2 + shape side width", value=0, key="x2_120") + shape_side_w + x1_120
        
        with tab_240:
            st.write("Define ROI for the **240°** image.")
            col1, col2 = st.columns(2)
            y1_240 = col1.number_input("y1 (bottom)", key="y1_240", step=1, value = _240[0])
            y2_240 = col2.number_input("y2 (top) = y1 + shape side height + value", value=0, key="y2_240") + shape_side_h + y1_240
            x1_240 = col1.number_input("x1 (left)", key="x1_240", step=1, value=_240[2])
            x2_240 = col2.number_input("x2 (right) = x2 + shape side width", value=0, key="x2_240") + shape_side_w + x1_240    
    
    rois = [[y1_front, y2_front, x1_front, x2_front],
            [y1_top, y2_top, x1_top, x2_top],
            [y1_120, y2_120, x1_120, x2_120],
            [y1_240, y2_240, x1_240, x2_240]]
    
    shape_front = (shape_front_h, shape_front_w)
    shape_side = (shape_side_h, shape_side_w)
    shape_roi = [shape_front, shape_side]
    
    col1, col2 = st.columns(2)
    with col1:
        st.image(roi_image_plotter(deconvoluter.get_default_image(params.get('img_rot_angle', 0.0)), rois), 
                 clamp=False, use_container_width=False, width=550)

    with col2:
        if st.button("Run Reconstruction and Save ROIs", type="primary"):
            filename = os.path.join(outdir, "ROI_Data.json")
            os.makedirs(outdir, exist_ok=True)
            
            data_to_save = {
                "params": params,
                "rois": {
                    "front": rois[0],
                    "top": rois[1],
                    "120": rois[2],
                    "240": rois[3]
                },
                "shape_roi": shape_roi
            }
            
            with open(filename, 'w') as file:
                json.dump(data_to_save, file, indent=4)
            st.toast(f"ROI data saved to {filename}")
                
            deconvoluter.define_roi(rot_angle=params.get('img_rot_angle', 0.0), shape_roi=shape_roi, rois=rois)
            correction_matrix = deconvoluter.create_correction_matrix()
            
            with st.spinner("Processing reconstruction..."):
                rec_light_dist = deconvoluter.perform_reconstruction(max_it=4, max_err=0.05, resolution=params['res'])
            
            st.success("Reconstruction completed successfully!")
            camera_names = ["Front", "Top", "120°", "240°"]
            iterations = [f"Iteration {i+1}" for i in range(len(deconvoluter.quotients[0]))]
            df = pd.DataFrame(deconvoluter.quotients, index=camera_names, columns=iterations)
            st.write("Quotients from the reconstruction:")
            st.dataframe(df)

            st.session_state.reconstruction_result = rec_light_dist
            st.session_state.correction_matrix = correction_matrix
            st.session_state.cam_pics = [
                deconvoluter.cam_pic_front,
                deconvoluter.cam_pic_top,
                deconvoluter.cam_pic_120,
                deconvoluter.cam_pic_240
            ]

    if 'reconstruction_result' in st.session_state:
        # Display these immediately after calculation
        with st.expander("**Display Correction Matrix**"):
            interactive_tomographic_viewer(st.session_state.correction_matrix, key_prefix="corr_mat")
        with st.expander("**Display Camera Images**", expanded=False):
            interactive_camera_viewer(st.session_state.cam_pics, key_prefix="cam_viewer")

        render_results(st.session_state.reconstruction_result, deconvoluter, params, shape_side)


if __name__ == "__main__":
    main()