import streamlit as st
import pandas as pd
from PIL import Image
import os
import re
import io

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

    # File uploader - accepts multiple images
    uploaded_files = st.file_uploader(
        "📤 Drop Your Meme Folder Here",
        type=['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp'],
        accept_multiple_files=True,
        help="Select all images from your meme folder or drag & drop the entire folder"
    )

    if st.button("📁 Load Memes", use_container_width=True, disabled=not uploaded_files):
        if uploaded_files:
            # Sort files by number in filename
            sorted_files = sorted(uploaded_files, key=lambda x: extract_number_for_sorting(x.name))

            # Store images
            st.session_state.images = []
            st.session_state.meme_numbers = []

            for file in sorted_files:
                # Read image
                image = Image.open(file)
                meme_id = get_meme_identifier(file.name)

                st.session_state.images.append({
                    'image': image,
                    'filename': file.name,
                    'meme_id': meme_id
                })
                st.session_state.meme_numbers.append(meme_id)

            st.session_state.current_index = 0

            # Initialize annotations
            for meme_id in st.session_state.meme_numbers:
                if meme_id not in st.session_state.annotations:
                    st.session_state.annotations[meme_id] = {
                        'sentiment': '',
                        'topic': '',
                        'intent': ''
                    }

            st.success(f"✅ Loaded {len(st.session_state.images)} memes!")
            st.info(f"📊 First: {st.session_state.meme_numbers[0]} | Last: {st.session_state.meme_numbers[-1]}")

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

            # Save to Excel in memory
            if st.session_state.meme_numbers:
                first = st.session_state.meme_numbers[0]
                last = st.session_state.meme_numbers[-1]
                output_file = f"meme_annotation_{first}_to_{last}.xlsx"
            else:
                output_file = "meme_annotation.xlsx"

            # Create Excel file in memory
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, index=False)
            output.seek(0)

            st.success(f"✅ Ready to download!")

            # Provide download button
            st.download_button(
                label="⬇️ Download Excel",
                data=output,
                file_name=output_file,
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )

# Main content
if not st.session_state.images:
    st.info("👈 Upload your meme images and click 'Load Memes' to start!")

    # Instructions with visual guide
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        ### 📋 Instructions:
        1. Click **"Browse files"** in the sidebar
        2. **Select all images** from your meme folder:
           - Windows: `Ctrl + A` to select all
           - Mac: `Cmd + A` to select all
        3. Or **drag & drop** all images at once
        4. Click **"Load Memes"**
        5. Annotate using dropdowns
        6. Click **"Save to Excel"** when done
        """)

    with col2:
        st.markdown("""
        ### 💡 Tips:
        - Accepts: JPG, PNG, GIF, BMP, WEBP
        - Upload up to **200MB** total
        - Use **arrow keys** (← →) for navigation
        - Leave fields **empty** if meme doesn't fit
        - Progress auto-saves in the app
        - Excel uses **exact filenames** as meme numbers
        """)

    st.markdown("---")
    st.warning(
        "⚠️ **Note:** If uploading 350+ images is slow, consider running this tool locally instead. Ask your instructor for the local version!")

else:
    # Get current meme info
    current_meme = st.session_state.images[st.session_state.current_index]
    current_meme_id = current_meme['meme_id']
    current_filename = current_meme['filename']
    current_image = current_meme['image']

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
            st.image(current_image, use_container_width=True)
            st.caption(f"📁 {current_filename}")
        except Exception as e:
            st.error(f"Error displaying image: {e}")

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
        col_skip, col_jump = st.columns(2)

        with col_skip:
            if st.button("⏭️ Skip", use_container_width=True):
                st.session_state.annotations[current_meme_id] = {
                    'sentiment': '',
                    'topic': '',
                    'intent': ''
                }
                if st.session_state.current_index < len(st.session_state.images) - 1:
                    st.session_state.current_index += 1
                st.rerun()

        with col_jump:
            jump_to = st.number_input("Jump to #", min_value=1, max_value=len(st.session_state.images),
                                      value=st.session_state.current_index + 1, label_visibility="collapsed")
            if st.button("🎯 Go", use_container_width=True):
                st.session_state.current_index = jump_to - 1
                st.rerun()

        # Keyboard shortcuts info
        st.info("⌨️ Use **arrow keys** to navigate")

# Footer
st.markdown("---")
st.markdown(
    "<p style='text-align: center; color: gray;'>Meme Annotation Tool for Data Mining Assignment | Built with Streamlit</p>",
    unsafe_allow_html=True
)