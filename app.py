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

def detect_scenes(video_path):
    video = cv2.VideoCapture(video_path)
    prev_frame = None
    scenes = []
    frame_rate = video.get(cv2.CAP_PROP_FPS)
    success, frame = video.read()
    frame_index = 0

    while success:
        if prev_frame is not None:
            diff = cv2.absdiff(frame, prev_frame)
            gray = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
            blur = cv2.GaussianBlur(gray, (21, 21), 0)
            thresh = cv2.threshold(blur, 25, 255, cv2.THRESH_BINARY)[1]
            non_zero_count = np.count_nonzero(thresh)

            if non_zero_count > 50000:
                scenes.append(frame_index / frame_rate)
        
        prev_frame = frame
        success, frame = video.read()
        frame_index += 1

    video.release()
    return scenes

def split_and_filter_video(input_path, output_path, interval, pattern_type, preview=False, use_scene_detection=False):
    video = VideoFileClip(input_path)
    duration = video.duration

    clips = []
    clip_index = 0

    if use_scene_detection:
        scenes = detect_scenes(input_path)
        scenes.append(duration)
        clip_points = scenes
    else:
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
        if preview:
            st.write('Showing preview of retained clips:')
            for i, clip in enumerate(clips[:3]):
                clip.preview()
        
        final_clip = concatenate_videoclips(clips)
        final_clip.write_videofile(output_path, codec='libx264', fps=24)
        video.close()
        return True
    else:
        video.close()
        return False
