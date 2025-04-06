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

        for uploaded_file in uploaded_files:
            input_path = uploaded_file.name
            output_path = "processed_" + uploaded_file.name

            with open(input_path, 'wb') as f:
                f.write(uploaded_file.getbuffer())
            
            def split_and_filter_video(input_path, output_path, interval, pattern_type, resolution, desired_length, use_motion_filter, use_ai_detection=False):
                video = VideoFileClip(input_path)
                duration = video.duration

                if resolution:
                    video = video.resize(newsize=resolution)

                clips = []
                clip_index = 0
                clip_points = np.arange(0, duration, interval).tolist()

                if use_ai_detection:
                    video_manager = VideoManager([input_path])
                    scene_manager = SceneManager()
                    scene_manager.add_detector(ContentDetector())
                    
                    video_manager.set_downscale_factor()
                    video_manager.start()
                    
                    scene_manager.detect_scenes(video_manager)
                    scene_list = scene_manager.get_scene_list()
                    
                    clip_points = [scene[0].get_seconds() for scene in scene_list]

                if use_motion_filter:
                    motion_scores = []
                    for clip_start in clip_points:
                        clip_end = min(clip_start + interval, duration)
                        clip = video.subclip(clip_start, clip_end)
                        motion_score = clip.get_frame(0).std()
                        motion_scores.append((clip, motion_score))

                    motion_scores.sort(key=lambda x: x[1], reverse=True)
                    clips = [x[0] for x in motion_scores[:int(desired_length / interval)]]
                else:
                    for clip_start in clip_points:
                        clip_end = min(clip_start + interval, duration)
                        clip = video.subclip(clip_start, clip_end)
                        clips.append(clip)
                
                if clips:
                    combined_duration = sum([clip.duration for clip in clips])
                    
                    if combined_duration > desired_length:
                        playback_speed = combined_duration / desired_length
                        clips = [clip.fx(vfx.speedx, playback_speed) for clip in clips]

                    final_clip = concatenate_videoclips(clips)
                    final_clip.write_videofile(output_path, codec='libx264', fps=24, preset='ultrafast', threads=4)
                    video.close()
                    return output_path
                else:
                    video.close()
                    return None

            use_ai_detection = interval_option == 'AI Scene Detection'
            result = split_and_filter_video(input_path, output_path, interval_dict.get(interval_option, 0.5), pattern, resolution_dict[resolution_option], desired_length, use_motion_filter, use_ai_detection)

            if result:
                st.success(f"Video processed successfully!")

                with open(result, "rb") as file:
                    st.download_button(
                        label="Download Processed Video",
                        data=file,
                        file_name=output_path,
                        mime="video/mp4"
                    )
                
                os.remove(input_path)
                os.remove(output_path)
            else:
                st.error("Processing failed. Try adjusting your settings.")
    else:
        st.warning("Please upload a video file before processing.")
