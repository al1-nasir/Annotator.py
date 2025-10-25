import streamlit as st
import pandas as pd
from PIL import Image
import os
import re
from pathlib import Path

# Page config
st.set_page_config(page_title="Meme Annotator", layout="wide", initial_sidebar_state="expanded")

# Initialize session state
if 'current_index' not in st.session_state:
    st.session_state.current_index = 0
if 'annotations' not in st.session_state:
    st.session_state.annotations = {}
if 'images' not in st.session_state:
    st.session_state.images = []
if 'meme_numbers' not in st.session_state:
    st.session_state.meme_numbers = []

# Categories
SENTIMENT = ['', 'Positive', 'Negative', 'Neutral']
TOPIC = ['', 'Politics', 'Social issues', 'Culture', 'Entertainment', 'Education', 'Technology']
INTENT = ['', 'Informative', 'Relatable', 'Satirical']


def get_meme_identifier(filename):
    """Get meme identifier from filename (filename without extension)"""
    return os.path.splitext(filename)[0]


def extract_number_for_sorting(filename):
    """Extract number from filename for sorting"""
    match = re.search(r'(\d+)', filename)
    return int(match.group(1)) if match else 0


# Title
st.title("🎭 Meme Annotation Tool")
st.markdown("---")

# Sidebar for setup
with st.sidebar:
    st.header("⚙️ Setup")

    # Folder path input
    folder_path = st.text_input(
        "Meme Folder Path",
        placeholder="C:/path/to/your/meme/folder",
        help="Paste the full path to your meme images folder"
    )

    if st.button("📁 Load Memes", use_container_width=True):
        if folder_path and os.path.exists(folder_path):
            # Get all image files
            image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']
            image_files = []

            for file in os.listdir(folder_path):
                if any(file.lower().endswith(ext) for ext in image_extensions):
                    image_files.append(file)

            # Sort by number in filename
            image_files.sort(key=extract_number_for_sorting)

            # Store images with their filenames as identifiers
            st.session_state.images = [(os.path.join(folder_path, f), f) for f in image_files]
            st.session_state.meme_numbers = [get_meme_identifier(f) for f in image_files]
            st.session_state.current_index = 0

            # Initialize annotations using filenames as identifiers
            for meme_id in st.session_state.meme_numbers:
                if meme_id not in st.session_state.annotations:
                    st.session_state.annotations[meme_id] = {
                        'sentiment': '',
                        'topic': '',
                        'intent': ''
                    }

            st.success(f"✅ Loaded {len(st.session_state.images)} memes!")
            st.info(f"📊 First: {st.session_state.meme_numbers[0]} | Last: {st.session_state.meme_numbers[-1]}")
        else:
            st.error("❌ Invalid folder path!")

    st.markdown("---")

    # Progress
    if st.session_state.images:
        total = len(st.session_state.images)
        completed = sum(1 for ann in st.session_state.annotations.values()
                        if ann['sentiment'] and ann['topic'] and ann['intent'])

        st.metric("Progress", f"{completed}/{total}")
        st.progress(completed / total if total > 0 else 0)

        st.markdown("---")

        # Save button
        if st.button("💾 Save to Excel", use_container_width=True, type="primary"):
            # Create DataFrame
            data = []
            for meme_id in sorted(st.session_state.annotations.keys(),
                                  key=lambda x: extract_number_for_sorting(str(x))):
                ann = st.session_state.annotations[meme_id]
                # Only add rows that have at least one annotation
                if ann['sentiment'] or ann['topic'] or ann['intent']:
                    data.append({
                        'Meme Number': meme_id,
                        'Sentiment Analysis': ann['sentiment'],
                        'Topic of the Meme': ann['topic'],
                        'Intent': ann['intent']
                    })

            df = pd.DataFrame(data)

            # Save to Excel
            if st.session_state.meme_numbers:
                first = st.session_state.meme_numbers[0]
                last = st.session_state.meme_numbers[-1]
                output_file = f"meme_annotation_{first}_to_{last}.xlsx"
            else:
                output_file = "meme_annotation.xlsx"

            df.to_excel(output_file, index=False)

            st.success(f"✅ Saved to {output_file}")

            # Provide download button
            with open(output_file, 'rb') as f:
                st.download_button(
                    label="⬇️ Download Excel",
                    data=f,
                    file_name=output_file,
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )

# Main content
if not st.session_state.images:
    st.info("👈 Paste your folder path and click 'Load Memes' to start!")
    st.markdown("""
    ### 📋 Instructions:
    1. Paste the **full path** to your meme folder (e.g., `C:/Downloads/Meme_Images/YourName`)
    2. Click **Load Memes**
    3. Annotate each meme using the dropdowns
    4. Use **Next/Previous** buttons or arrow keys to navigate
    5. Click **Save to Excel** when done

    ### 💡 Tips:
    - Use **arrow keys** (← →) for quick navigation
    - Leave all fields **empty** if meme doesn't fit any category
    - Your progress is automatically saved in the app
    - The Excel will use actual filenames as meme numbers (e.g., meme_4201, meme_4202, etc.)
    """)
else:
    # Get current meme info
    current_path, current_filename = st.session_state.images[st.session_state.current_index]
    current_meme_id = st.session_state.meme_numbers[st.session_state.current_index]

    # Navigation and info
    col1, col2, col3 = st.columns([1, 2, 1])

    with col1:
        if st.button("⬅️ Previous", use_container_width=True, disabled=st.session_state.current_index == 0):
            st.session_state.current_index -= 1
            st.rerun()

    with col2:
        st.markdown(
            f"<h3 style='text-align: center;'>{current_meme_id} ({st.session_state.current_index + 1}/{len(st.session_state.images)})</h3>",
            unsafe_allow_html=True)

    with col3:
        if st.button("Next ➡️", use_container_width=True,
                     disabled=st.session_state.current_index >= len(st.session_state.images) - 1):
            st.session_state.current_index += 1
            st.rerun()

    st.markdown("---")

    # Layout: Image on left, annotations on right
    col_img, col_ann = st.columns([2, 1])

    with col_img:
        try:
            img = Image.open(current_path)
            st.image(img, use_container_width=True)
            st.caption(f"📁 {current_filename}")
        except Exception as e:
            st.error(f"Error loading image: {e}")

    with col_ann:
        st.subheader("📝 Annotations")

        current_ann = st.session_state.annotations[current_meme_id]

        # Sentiment
        sentiment = st.selectbox(
            "Sentiment Analysis",
            SENTIMENT,
            index=SENTIMENT.index(current_ann['sentiment']) if current_ann['sentiment'] in SENTIMENT else 0,
            key=f"sentiment_{current_meme_id}"
        )

        # Topic
        topic = st.selectbox(
            "Topic of the Meme",
            TOPIC,
            index=TOPIC.index(current_ann['topic']) if current_ann['topic'] in TOPIC else 0,
            key=f"topic_{current_meme_id}"
        )

        # Intent
        intent = st.selectbox(
            "Intent",
            INTENT,
            index=INTENT.index(current_ann['intent']) if current_ann['intent'] in INTENT else 0,
            key=f"intent_{current_meme_id}"
        )

        # Update annotations
        st.session_state.annotations[current_meme_id] = {
            'sentiment': sentiment,
            'topic': topic,
            'intent': intent
        }

        # Status
        if sentiment and topic and intent:
            st.success("✅ Complete")
        else:
            st.warning("⚠️ Incomplete")

        st.markdown("---")

        # Quick actions
        if st.button("⏭️ Skip (Leave Empty)", use_container_width=True):
            st.session_state.annotations[current_meme_id] = {
                'sentiment': '',
                'topic': '',
                'intent': ''
            }
            if st.session_state.current_index < len(st.session_state.images) - 1:
                st.session_state.current_index += 1
            st.rerun()

        # Keyboard shortcuts info
        st.info("⌨️ Use **arrow keys** to navigate")

# Footer
st.markdown("---")
st.markdown(
    "<p style='text-align: center; color: gray;'>Meme Annotation Tool for Data Mining Assignment</p>",
    unsafe_allow_html=True
)