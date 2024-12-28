import streamlit as st
import os
import yaml
from mutagen import File
import pandas as pd
from pathlib import Path
import shutil
import html
import re

def load_config():
    config_path = Path(__file__).parent.parent / "conf" / "secrets.yaml"
    with open(config_path, 'r') as file:
        return yaml.safe_load(file)

def get_music_path():
    # For development, using hardcoded path
    return r"D:\ai-assistant\FAM\music"

def sanitize_string(value):
    """Sanitize string values for safe HTML display"""
    if not isinstance(value, (str, int, float)):
        try:
            value = str(value[0]) if isinstance(value, (list, tuple)) else str(value)
        except:
            return "Unable to display value"
    
    # Remove non-printable characters and sanitize for HTML
    value = re.sub(r'[^\x20-\x7E]', '', str(value))
    return html.escape(value)

def get_file_metadata(file_path):
    try:
        audio = File(file_path)
        if audio is None:
            return {"Error": "Not a valid audio file"}
        
        metadata = {}
        # Basic file info
        metadata["File Size"] = f"{os.path.getsize(file_path) / (1024*1024):.2f} MB"
        metadata["Format"] = audio.mime[0].split('/')[-1].upper()
        
        # Audio-specific metadata
        if hasattr(audio.info, 'length'):
            metadata["Duration"] = f"{int(audio.info.length // 60)}:{int(audio.info.length % 60):02d}"
        if hasattr(audio.info, 'bitrate'):
            metadata["Bitrate"] = f"{int(audio.info.bitrate / 1000)} kbps"
        
        # Tags
        if hasattr(audio, 'tags'):
            tags = audio.tags
            if tags:
                for key in tags.keys():
                    metadata[key] = tags[key]
        
        # Sanitize metadata values
        sanitized_metadata = {}
        for key, value in metadata.items():
            sanitized_metadata[sanitize_string(key)] = sanitize_string(value)
        
        return sanitized_metadata
    except Exception as e:
        return {"Error": str(e)}

def main():
    st.set_page_config(page_title="Music File Management", layout="wide")
    # Add custom CSS
    st.markdown("""
        <style>
        .music-card {
            background-color: #282828;
            padding: 20px;
            border-radius: 8px;
            margin: 10px 0;
        }
        .file-title {
            color: #1DB954;
            font-size: 24px;
            font-weight: bold;
        }
        .metadata-item {
            background-color: #181818;
            padding: 10px;
            border-radius: 4px;
            margin: 5px 0;
        }
        .property-name {
            color: #b3b3b3;
            font-size: 14px;
        }
        .property-value {
            color: white;
            font-size: 16px;
        }
        </style>
    """, unsafe_allow_html=True)

    st.title("🎵 Music File Management")
    
    music_path = get_music_path()
    
    if not os.path.exists(music_path):
        os.makedirs(music_path)
    
    # File Upload with better styling
    st.markdown("### Upload New Track 🎵")
    uploaded_file = st.file_uploader(
        label="Choose a music file",
        type=['mp3', 'wav', 'm4a', 'ogg'],
        label_visibility="collapsed"
    )
    if uploaded_file:
        with open(os.path.join(music_path, uploaded_file.name), 'wb') as f:
            f.write(uploaded_file.getvalue())
        st.success(f"🎉 Successfully uploaded: {uploaded_file.name}")
    
    music_files = [f for f in os.listdir(music_path) if f.lower().endswith(('.mp3', '.wav', '.m4a', '.ogg'))]
    
    if not music_files:
        st.info("🎵 No music files found in the directory.")
        return
    
    # Use session_state to track selected file
    if "selected_file" not in st.session_state:
        st.session_state.selected_file = music_files[0]
    
    st.selectbox(
        label="Select a music file",
        options=music_files,
        key="selected_file",
        label_visibility="collapsed"
    )
    
    file_path = os.path.join(music_path, st.session_state.selected_file)
    metadata = get_file_metadata(file_path)
    
    # Create a music card
    st.markdown(f"""
        <div class="music-card">
            <div class="file-title">🎵 {st.session_state.selected_file}</div>
        </div>
    """, unsafe_allow_html=True)
    
    # Action buttons in a more compact layout
    col_buttons = st.columns([1, 1, 2])
    
    with col_buttons[0]:
        with open(file_path, 'rb') as f:
            st.download_button(
                label="⬇️ Download",
                data=f,
                file_name=st.session_state.selected_file,
                mime="audio/mpeg"
            )
    
    with col_buttons[1]:
        if st.button("🗑️ Delete"):
            try:
                os.remove(file_path)
                st.success(f"Deleted: {st.session_state.selected_file}")
                music_files.remove(st.session_state.selected_file)
                if music_files:
                    st.session_state.selected_file = music_files[0]
                else:
                    st.session_state.selected_file = None
            except Exception as e:
                st.error(f"Error deleting file: {e}")
    
    # Display metadata in a more attractive way
    st.markdown("### 📊 Track Info")
    
    # Filter and organize important metadata first
    important_fields = ['Format', 'Duration', 'Bitrate', 'File Size']
    for field in important_fields:
        if field in metadata:
            try:
                st.markdown(f"""
                    <div class="metadata-item">
                        <span class="property-name">{sanitize_string(field)}</span><br>
                        <span class="property-value">{sanitize_string(metadata[field])}</span>
                    </div>
                """, unsafe_allow_html=True)
            except Exception as e:
                st.error(f"Error displaying metadata for {field}")
    
    # Display other metadata
    st.markdown("### 🏷️ Additional Tags")
    other_metadata = {k: v for k, v in metadata.items() if k not in important_fields and k != 'Error'}
    for key, value in other_metadata.items():
        try:
            st.markdown(f"""
                <div class="metadata-item">
                    <span class="property-name">{sanitize_string(key)}</span><br>
                    <span class="property-value">{sanitize_string(value)}</span>
                </div>
            """, unsafe_allow_html=True)
        except Exception as e:
            st.error(f"Error displaying metadata for {key}")
    
    # Audio player with some spacing
    st.markdown("### 🎧 Player")
    st.audio(file_path)

if __name__ == "__main__":
    main()
