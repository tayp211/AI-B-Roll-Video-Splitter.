import os
from moviepy.editor import VideoFileClip, concatenate_videoclips
import streamlit as st
import numpy as np

st.set_page_config(page_title='AI B-Roll Video Splitter Tool', layout='centered')

st.title('AI B-Roll Video Splitter Tool')
st.write('Upload a video, customize your split pattern, choose your resolution, and let AI do the work!')

uploaded_files = st.file_uploader('Upload your video files', type=['mp4', 'mov', 'avi'], accept_multiple_files=True)

# User input for customization
interval_option = st.selectbox(
    'Select Interval Type (Split Frequency)',
    ('High-Energy Content (0.5 seconds)', 'Narrative-Driven Content (2 seconds)', 'Cinematic Content (3 seconds)')
)

interval_dict = {
    'High-Energy Content (0.5 seconds)': 0.5,
    'Narrative-Driven Content (2 seconds)': 2,
    'Cinematic Content (3 seconds)': 3
}

interval = interval_dict[interval_option]

pattern = st.selectbox('Select Clip Deletion Pattern:', 
                       ('Delete every other clip', 'Keep every third clip', 'Keep every fourth clip', 'No deletion (keep all)'))

# Resolution selection for different platforms
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

# Add a process button
if st.button('Start Processing'):
    if uploaded_files:
        st.write("Processing your files... This may take a few moments.")

        for uploaded_file in uploaded_files:
            input_path = uploaded_file.name
            output_path = "processed_" + uploaded_file.name

            with open(input_path, 'wb') as f:
                f.write(uploaded_file.getbuffer())
            
            def split_and_filter_video(input_path, output_path, interval, pattern_type, resolution):
                video = VideoFileClip(input_path)
                duration = video.duration

                # Resize the video if a resolution is selected
                if resolution:
                    video = video.resize(newsize=resolution)

                clips = []
                clip_index = 0
                clip_points = np.arange(0, duration, interval).tolist()
                
                # Progress bar for processing clips
                clip_progress = st.progress(0)
                total_clips = len(clip_points)

                for idx, clip_start in enumerate(clip_points):
                    clip_end = min(clip_start + interval, duration)
                    clip = video.subclip(clip_start, clip_end)

                    if pattern_type == 'Delete every other clip' and clip_index % 2 == 0:
                        clips.append(clip)
                    elif pattern_type == 'Keep every third clip' and clip_index % 3 == 0:
                        clips.append(clip)
                    elif pattern_type == 'Keep every fourth clip' and clip_index % 4 == 0:
                        clips.append(clip)
                    elif pattern_type == 'No deletion (keep all)':
                        clips.append(clip)

                    clip_index += 1
                    clip_progress.progress((idx + 1) / total_clips)

                if clips:
                    final_clip = concatenate_videoclips(clips)
                    
                    # Exporting progress bar
                    export_progress = st.progress(0)
                    final_clip.write_videofile(
                        output_path, 
                        codec='libx264', 
                        fps=24, 
                        preset='ultrafast',
                        threads=4  # Faster encoding using multiple threads
                    )
                    
                    export_progress.progress(1.0)
                    
                    video.close()
                    return output_path
                else:
                    video.close()
                    return None

            result = split_and_filter_video(input_path, output_path, interval, pattern, resolution_dict[resolution_option])

            if result:
                st.success(f"Video processed successfully!")

                # Provide a download link
                with open(result, "rb") as file:
                    st.download_button(
                        label="Download Processed Video",
                        data=file,
                        file_name=output_path,
                        mime="video/mp4"
                    )
                
                # Clean up files after processing
                os.remove(input_path)
                os.remove(output_path)
            else:
                st.error("Processing failed. Try adjusting your settings.")
    else:
        st.warning("Please upload a video file before processing.")
