import os
from moviepy.editor import VideoFileClip, concatenate_videoclips, vfx
import streamlit as st
import numpy as np
from scenedetect import VideoManager, SceneManager
from scenedetect.detectors import ContentDetector

st.set_page_config(page_title='AI B-Roll Video Splitter Tool', layout='centered')

st.title('AI B-Roll Video Splitter Tool')
st.write('Upload a video, customize your split pattern, choose your resolution, and let AI do the work!')

uploaded_files = st.file_uploader('Upload your video files', type=['mp4', 'mov', 'avi'], accept_multiple_files=True)

interval_option = st.selectbox(
    'Select Interval Type (Split Frequency)',
    ('High-Energy Content (0.5 seconds)', 'Narrative-Driven Content (2 seconds)', 'Cinematic Content (3 seconds)', 'AI Scene Detection')
)

interval_dict = {
    'High-Energy Content (0.5 seconds)': 0.5,
    'Narrative-Driven Content (2 seconds)': 2,
    'Cinematic Content (3 seconds)': 3,
}

pattern = st.selectbox('Select Clip Deletion Pattern:', 
                       ('Delete every other clip', 'Keep every third clip', 'Keep every fourth clip', 'No deletion (keep all)'))

resolution_option = st.selectbox(
    "Select Resolution for Social Media",
    ("Original", "1080x1080 (Instagram Feed, Facebook)", "1080x1920 (Instagram Reels, TikTok)", "1920x1080 (YouTube)", "1280x720 (Twitter)")
)

resolution_dict = {
    "Original": None,
    "1080x1080 (Instagram Feed, Facebook)": (1080, 1080),
    "1080x1920 (Instagram Reels, TikTok)": (1080, 1920),
    "1920x1080 (YouTube)": (1920, 1080),
    "1280x720 (Twitter)": (1280, 720)
}

desired_length = st.number_input('Enter desired final video length (in seconds)', min_value=1, value=30)
use_motion_filter = st.checkbox('Enable Motion Filter (Keep only high-movement clips)')

if st.button('Start Processing'):
    if uploaded_files:
        st.write("Processing your files... This may take a few moments.")

        for uploaded_file in
