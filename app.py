import os
from moviepy.editor import VideoFileClip, concatenate_videoclips
import streamlit as st
import numpy as np

st.set_page_config(page_title='AI B-Roll Video Splitter Tool', layout='centered')

st.title('AI B-Roll Video Splitter Tool')
st.write('Upload a video, customize your split pattern, choose your resolution, and let AI do the work!')

uploaded_files = st.file_uploader('Upload your video files', type=['mp4
