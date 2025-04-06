import os
from moviepy.editor import VideoFileClip, concatenate_videoclips
import streamlit as st
import cv2
import numpy as np

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
    if uploaded_files is not None:
        st.write("Processing your files... This may take a few moments.")

        for uploaded_file in uploaded_files:
            # Save the file to the server
            with open(uploaded_file.name, 'wb') as f:
                f.write(uploaded_file.getbuffer())
            
            input_path = uploaded_file.name
            output_path = "processed_" + uploaded_file.name

            def split_and_filter_video(input_path, output_path, interval, pattern_type):
                video = VideoFileClip(input_path)
                duration = video.duration

                clips = []
                clip_index = 0
                clip_points = np.arange(0, duration, interval).tolist()

                for clip_start in clip_points:
                    clip_end = min(clip_start + interval, duration)
                    clip = video.subclip(clip_start, clip_end)

                    if pattern_type == 'Delete every other clip' and clip_index % 2 == 0:
                        clips.append(clip)
                    elif pattern_type == 'Keep every third clip' and clip_index % 3 == 0:
                        clips.append(clip)
                    elif pattern_type == 'Keep every fourth clip' and clip_index % 4 == 0:
                        clips.append(clip)

                    clip_index += 1

                if clips:
                    final_clip = concatenate_videoclips(clips)
                    final_clip.write_videofile(output_path, codec='libx264', fps=24)
                    video.close()
                    return True
                else:
                    video.close()
                    return False

            if split_and_filter_video(input_path, output_path, interval, pattern):
                st.success(f"Video processed successfully! Download your file: {output_path}")
            else:
                st.error("Processing failed. Try adjusting your settings.")
    else:
        st.warning("Please upload a video file before processing.")
