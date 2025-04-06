import os
from moviepy.editor import VideoFileClip, concatenate_videoclips
import streamlit as st
import cv2
import numpy as np
import shutil

st.set_page_config(page_title='AI B-Roll Video Splitter Tool', layout='centered')

st.title('AI B-Roll Video Splitter Tool')
st.write('Upload a video, customize your split pattern, and let AI do the work!')

uploaded_files = st.file_uploader('Upload your video files', type=['mp4', 'mov', 'avi'], accept_multiple_files=True)

# User input for customization
interval = st.number_input('Enter interval length in seconds (default is 0.5):', value=0.5, min_value=0.1)
pattern = st.selectbox('Select clip deletion pattern:', ('Delete every other clip', 'Keep every third clip', 'Keep every fourth clip'))

advanced_features = st.checkbox('Enable Advanced Features')

if advanced_features:
    ai_scene_detection = st.checkbox('AI Scene Detection (Detects natural cuts/transitions)')
    preview_enabled = st.checkbox('Enable Visual Previews')
    merge_videos = st.checkbox('Allow Merging Multiple Videos')

# Add a process button
if st.button('Start Processing'):
    if uploaded_files:
        st.write("Processing your files... This may take a few moments.")

        for uploaded_file in uploaded_files:
            input_path = uploaded_file.name
            output_path = "processed_" + uploaded_file.name

            with open(input_path, 'wb') as f:
