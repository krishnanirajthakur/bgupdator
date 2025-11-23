# Install: pip install streamlit rembg Pillow
import os
import random
import streamlit as st
from rembg import remove
from PIL import Image
from io import BytesIO

# Configure the basic page settings
st.set_page_config(
    page_title="Travel Setu Virtual Darshan",
    page_icon="assets/logo.png",
    layout="wide"
)

# Try to show a local logo if provided at assets/logo.png. If not present, the app will show the text title.
logo_path = os.path.join(os.path.dirname(__file__), "assets", "logo.png")
if os.path.exists(logo_path):
    try:
        logo_img = Image.open(logo_path)
        # Show a small logo at the top of the app
        st.image(logo_img, width=180)
    except Exception:
        # If logo fails to load, ignore and continue with textual title
        pass

# --- THE IMAGE PROCESSING LOGIC ---
def composite_images_web(fg_file, bg_file, scale_factor, placement_mode='center', margin_ratio=0.05, seed=None, jitter_ratio=0.02):
    """Handles image processing: background removal, resizing, and compositing.

    placement_mode: 'center', 'random', 'thirds', or 'corners'
    margin_ratio: fraction of min(bg_width, bg_height) used as safe-edge margin when randomizing
    seed: optional integer to seed randomness for reproducible placements
    jitter_ratio: fraction of min(bg_width, bg_height) used as maximum jitter for 'thirds' placement
    """
    try:
        # determinism: seed random if provided
        if seed is not None:
            try:
                random.seed(int(seed))
            except Exception:
                pass

        # 1. READ AND REMOVE BACKGROUND
        fg_input = Image.open(BytesIO(fg_file.read())).convert("RGBA")
        fg_removed_bg = remove(fg_input).convert("RGBA")

        # 2. READ BACKGROUND
        bg_img = Image.open(BytesIO(bg_file.read())).convert("RGB")

        # 3. RESIZE FOREGROUND
        original_width, original_height = fg_removed_bg.size
        bg_width, bg_height = bg_img.size

        # Calculate new dimensions from requested scale
        new_width = int(original_width * scale_factor)
        new_height = int(original_height * scale_factor)

        # Check for minimum size constraints before resizing
        if new_width == 0 or new_height == 0:
            return None, "Error: Scale factor resulted in zero dimension."

        # If the scaled foreground is larger than the background, fit it to background while preserving aspect
        if new_width > bg_width or new_height > bg_height:
            fit_scale = min(bg_width / original_width, bg_height / original_height)
            new_width = max(1, int(original_width * fit_scale))
            new_height = max(1, int(original_height * fit_scale))

        # Resize the foreground to computed size
        fg_resized = fg_removed_bg.resize((new_width, new_height), Image.Resampling.LANCZOS)

        # Calculate available ranges
        max_x = max(0, bg_width - new_width)
        max_y = max(0, bg_height - new_height)

        # Determine placement
        pmode = str(placement_mode).lower()
        if pmode == 'random':
            # margin in pixels to avoid placing too close to edges
            margin_px = int(min(bg_width, bg_height) * float(margin_ratio))

            x_low = margin_px if margin_px < max_x else 0
            x_high = max_x - margin_px if (max_x - margin_px) > 0 else max_x
            y_low = margin_px if margin_px < max_y else 0
            y_high = max_y - margin_px if (max_y - margin_px) > 0 else max_y

            if x_low <= x_high:
                x_pos = random.randint(x_low, x_high)
            else:
                x_pos = max(0, (bg_width - new_width) // 2)

            if y_low <= y_high:
                y_pos = random.randint(y_low, y_high)
            else:
                y_pos = max(0, (bg_height - new_height) // 2)

        elif pmode in ('thirds', 'rule_of_thirds', 'rule-of-thirds'):
            # Rule of thirds intersection points: (1/3,1/3), (2/3,1/3), (1/3,2/3), (2/3,2/3)
            tx = bg_width / 3.0
            ty = bg_height / 3.0
            candidates = [
                (int(tx - new_width / 2), int(ty - new_height / 2)),
                (int(2 * tx - new_width / 2), int(ty - new_height / 2)),
                (int(tx - new_width / 2), int(2 * ty - new_height / 2)),
                (int(2 * tx - new_width / 2), int(2 * ty - new_height / 2)),
            ]
            # apply jitter in pixels
            jitter_px = int(min(bg_width, bg_height) * float(jitter_ratio))
            chosen = random.choice(candidates)
            x_pos = chosen[0] + random.randint(-jitter_px, jitter_px) if jitter_px > 0 else chosen[0]
            y_pos = chosen[1] + random.randint(-jitter_px, jitter_px) if jitter_px > 0 else chosen[1]

            # clamp
            x_pos = min(max(0, x_pos), max_x)
            y_pos = min(max(0, y_pos), max_y)

        elif pmode in ('corners', 'corner'):
            # corners with margin
            margin_px = int(min(bg_width, bg_height) * float(margin_ratio))
            corners = [
                (margin_px, margin_px),  # top-left
                (max_x - margin_px, margin_px),  # top-right
                (margin_px, max_y - margin_px),  # bottom-left
                (max_x - margin_px, max_y - margin_px),  # bottom-right
            ]
            # clean corners (ensure within bounds)
            corners = [(min(max(0, int(x)), max_x), min(max(0, int(y)), max_y)) for x, y in corners]
            chosen = random.choice(corners)
            x_pos, y_pos = chosen

        else:
            # center placement by default
            x_pos = max(0, (bg_width - new_width) // 2)
            y_pos = max(0, (bg_height - new_height) // 2)

        box = (x_pos, y_pos, x_pos + new_width, y_pos + new_height)

        # 4. COMPOSITE
        bg_img.paste(fg_resized, box, mask=fg_resized)

        # 5. SAVE RESULT TO MEMORY (BytesIO)
        processed_image_io = BytesIO()
        bg_img.save(processed_image_io, format='JPEG')
        processed_image_io.seek(0)

        return processed_image_io, None

    except Exception as e:
        return None, f"An error occurred during processing: {e}"

# --- STREAMLIT APP LAYOUT AND UI ---

st.title("Travel Setu Virtual Darshan")
st.markdown("Easily remove the background from one image and composite it onto another. The final image is saved as a JPEG. Presented by Travel Setu.")

st.divider()

# Create an outer 3-column layout and use the center column for the app content to visually center everything
left_col, center_col, right_col = st.columns([1, 8, 1])

with center_col:
    # Centered header and subtitle
    st.header("1. Upload & Settings")

    # Upload Widgets (centered because they're inside center_col)
    foreground_file = st.file_uploader(
        "**Upload your Foreground Photo (The Cutout)**", 
        type=['png', 'jpg', 'jpeg'],
        help="This image will have its background removed."
    )
    
    background_file = st.file_uploader(
        "**Upload the New Background Image**", 
        type=['png', 'jpg', 'jpeg'],
        help="The final image will be pasted onto this."
    )

    st.subheader("Image Scale")
    # Scale Slider
    scale = st.slider(
        "Resize Factor for Cutout (0.1 = 10% | 1.0 = 100%)", 
        min_value=0.1, 
        max_value=1.0, 
        value=0.5, 
        step=0.05,
        help="Adjust the size of the foreground photo relative to its original size."
    )

    # Placement options (presets + deterministic seed)
    placement_mode = st.selectbox("Placement Mode", options=["Center", "Random", "Rule of Thirds", "Corners"], index=0, help="Choose where to place the cutout on the background.")
    # Default margin for edge-based placements
    if placement_mode in ("Random", "Corners"):
        margin_percent = st.slider("Edge margin (%)", min_value=0, max_value=20, value=5, step=1, help="Percent of the smaller background dimension used as a safe margin from edges when placing the cutout.")
        margin_ratio = margin_percent / 100.0
    else:
        margin_ratio = 0.05

    # Options for reproducibility and subtle variation
    seed_input = st.text_input("Random seed (optional)", value="", help="Enter an integer to reproduce placements. Leave blank for different random placement each run.")
    seed = int(seed_input) if seed_input.strip().isdigit() else None

    jitter_ratio = 0.02
    if placement_mode == "Rule of Thirds":
        jitter_percent = st.slider("Thirds jitter (%)", min_value=0, max_value=10, value=2, step=1, help="Maximum jitter around the thirds intersection as percent of smaller background dimension.")
        jitter_ratio = jitter_percent / 100.0

    st.markdown("---")

    st.header("2. Result & Download")

    if foreground_file and background_file:
        # Show a progress spinner while processing
        with st.spinner('Processing image... This may take a moment to remove the background.'):
            output_image_io, error_message = composite_images_web(
                foreground_file,
                background_file,
                scale,
                placement_mode=placement_mode.lower(),
                margin_ratio=margin_ratio
            )

        if output_image_io:
            st.success("✅ Success! Image ready for download.")

            # Display the image centered by using the center column width
            st.image(
                output_image_io, 
                caption=f"Final Composited Image (Scale Factor: {scale:.2f})", 
                use_column_width=True
            )

            # Provide a centered download button by using an inner 3-column layout and placing the button in the middle
            dl_left, dl_center, dl_right = st.columns([1, 2, 1])
            with dl_center:
                st.download_button(
                    label="⬇️ Download Composited Image (JPEG)",
                    data=output_image_io,
                    file_name="composited_result.jpg",
                    mime="image/jpeg",
                    type="primary"
                )

        elif error_message:
            st.error(f"Processing Failed: {error_message}")
    else:
        st.info("Please upload both a Foreground Photo and a New Background Image to begin.")