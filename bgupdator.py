# Install: pip install streamlit rembg Pillow
import os
import random
import streamlit as st
from rembg import remove
from PIL import Image, ImageDraw
from io import BytesIO

# Configure the basic page settings
st.set_page_config(
    page_title="BG Updator: Image Compositor",
    page_icon="assets/logo.png",
    layout="wide"
)

# NOTE: This part assumes an 'assets/logo.png' exists locally when the user runs the script.
logo_path = os.path.join(os.path.dirname(__file__), "assets", "logo.png")
if os.path.exists(logo_path):
    try:
        logo_img = Image.open(logo_path)
        st.image(logo_img, width=180)
    except Exception:
        pass

# --- HELPER FUNCTIONS ---

def hex_to_rgb(hex_color):
    """Converts a hex color string (e.g., #FFFFFF) to an RGB tuple."""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

# --- THE IMAGE PROCESSING LOGIC ---
def process_image(fg_file, bg_mode, bg_file=None, solid_color="#FFFFFF", scale_factor=0.5, placement_mode='center', alpha_threshold=0, margin_ratio=0.05, seed=None, jitter_ratio=0.02):
    """Handles image processing: background removal, refinement, resizing, and compositing.
    
    bg_mode: 'cutout', 'color', or 'image'
    alpha_threshold: Integer percentage (0 to 100) to adjust the alpha channel.
    """
    try:
        # 0. Determinism: seed random if provided
        if seed is not None:
            try:
                random.seed(int(seed))
            except Exception:
                pass

        # 1. READ AND REMOVE BACKGROUND
        # Need to reset file pointer if this function is called multiple times on same run
        fg_input = Image.open(BytesIO(fg_file.read())).convert("RGBA")
        fg_file.seek(0) # Reset pointer after reading
        
        # 'remove' uses the U2NET model, producing a mask in the alpha channel
        fg_removed_bg = remove(fg_input).convert("RGBA")
        
        # 1.1 MASK REFINEMENT (Alpha Thresholding)
        if alpha_threshold > 0:
            alpha = fg_removed_bg.getchannel('A')
            # Normalize threshold to 0-255 range
            thresh_value = int(255 * (alpha_threshold / 100)) 
            
            # Apply threshold to the alpha channel: 
            # pixels with alpha below threshold become fully transparent (0), otherwise they keep their original value.
            # This is a simple, non-interactive way to refine the mask edges.
            
            # Create a new alpha channel
            new_alpha = Image.new('L', alpha.size)
            
            # This operation is slow but necessary for pixel-level manipulation in PIL
            alpha_data = alpha.load()
            new_alpha_data = new_alpha.load()
            
            for y in range(alpha.size[1]):
                for x in range(alpha.size[0]):
                    # If current alpha is less than threshold, set to 0 (fully transparent)
                    if alpha_data[x, y] < thresh_value:
                        new_alpha_data[x, y] = 0
                    else:
                        new_alpha_data[x, y] = alpha_data[x, y]
            
            fg_removed_bg.putalpha(new_alpha)

        # 2. CUTOUT ONLY MODE
        if bg_mode == 'cutout':
            processed_image_io = BytesIO()
            fg_removed_bg.save(processed_image_io, format='PNG')
            processed_image_io.seek(0)
            return processed_image_io, None, 'PNG'


        # --- COMPOSITING SETUP (IMAGE OR COLOR BACKGROUND) ---
        original_width, original_height = fg_removed_bg.size
        
        if bg_mode == 'image':
            # 2.1 READ UPLOADED BACKGROUND
            bg_img = Image.open(BytesIO(bg_file.read())).convert("RGB")
            bg_file.seek(0) # Reset pointer after reading
        elif bg_mode == 'color':
            # 2.2 CREATE SOLID COLOR BACKGROUND
            if bg_file and bg_file.size > 0:
                 # If color mode is selected but an old image file is passed, ignore it
                 bg_width, bg_height = Image.open(BytesIO(bg_file.read())).size
            else:
                 # Use foreground size as a default placeholder size if no BG image was loaded
                 bg_width, bg_height = original_width * 2, original_height * 2 
                 
            bg_img = Image.new('RGB', (bg_width, bg_height), color=hex_to_rgb(solid_color))
        else:
            return None, "Error: Invalid background mode selected.", None
            
        bg_width, bg_height = bg_img.size

        # 3. RESIZE FOREGROUND
        # Calculate new dimensions from requested scale
        new_width = int(original_width * scale_factor)
        new_height = int(original_height * scale_factor)

        if new_width == 0 or new_height == 0:
            return None, "Error: Scale factor resulted in zero dimension.", None

        # Fit scaled foreground if it's larger than the background
        if new_width > bg_width or new_height > bg_height:
            fit_scale = min(bg_width / original_width, bg_height / original_height)
            new_width = max(1, int(original_width * fit_scale))
            new_height = max(1, int(original_height * fit_scale))

        fg_resized = fg_removed_bg.resize((new_width, new_height), Image.Resampling.LANCZOS)

        # Calculate available ranges
        max_x = max(0, bg_width - new_width)
        max_y = max(0, bg_height - new_height)

        # 4. Determine placement (Logic remains the same)
        pmode = str(placement_mode).lower().replace(" ", "_")
        
        if pmode == 'random':
            margin_px = int(min(bg_width, bg_height) * float(margin_ratio))
            x_low, x_high = (margin_px, max_x - margin_px) if max_x > 2 * margin_px else (0, max_x)
            y_low, y_high = (margin_px, max_y - margin_px) if max_y > 2 * margin_px else (0, max_y)
            x_pos = random.randint(x_low, x_high) if x_low <= x_high else max(0, max_x // 2)
            y_pos = random.randint(y_low, y_high) if y_low <= y_high else max(0, max_y // 2)

        elif pmode in ('thirds', 'rule_of_thirds'):
            tx, ty = bg_width / 3.0, bg_height / 3.0
            candidates = [
                (int(tx - new_width / 2), int(ty - new_height / 2)),
                (int(2 * tx - new_width / 2), int(ty - new_height / 2)),
                (int(tx - new_width / 2), int(2 * ty - new_height / 2)),
                (int(2 * tx - new_width / 2), int(2 * ty - new_height / 2)),
            ]
            jitter_px = int(min(bg_width, bg_height) * float(jitter_ratio))
            chosen = random.choice(candidates)
            x_pos = chosen[0] + random.randint(-jitter_px, jitter_px) if jitter_px > 0 else chosen[0]
            y_pos = chosen[1] + random.randint(-jitter_px, jitter_px) if jitter_px > 0 else chosen[1]
            x_pos = min(max(0, x_pos), max_x)
            y_pos = min(max(0, y_pos), max_y)

        elif pmode in ('corners', 'corner'):
            margin_px = int(min(bg_width, bg_height) * float(margin_ratio))
            corners = [
                (margin_px, margin_px),
                (max_x - margin_px, margin_px),
                (margin_px, max_y - margin_px),
                (max_x - margin_px, max_y - margin_px),
            ]
            corners = [(min(max(0, int(x)), max_x), min(max(0, int(y)), max_y)) for x, y in corners]
            x_pos, y_pos = random.choice(corners)

        else:
            # center placement by default
            x_pos = max(0, (bg_width - new_width) // 2)
            y_pos = max(0, (bg_height - new_height) // 2)

        box = (x_pos, y_pos, x_pos + new_width, y_pos + new_height)

        # 5. COMPOSITE
        bg_img.paste(fg_resized, box, mask=fg_resized)

        # 6. SAVE RESULT TO MEMORY (BytesIO)
        processed_image_io = BytesIO()
        bg_img.save(processed_image_io, format='JPEG')
        processed_image_io.seek(0)

        return processed_image_io, None, 'JPEG'

    except Exception as e:
        return None, f"An error occurred during processing: {e}", None

# --- STREAMLIT APP LAYOUT AND UI ---

st.title("BG Updator: Image Compositor")
st.markdown("Remove the background from a photo and composite it onto a new image or a solid color. Create professional cutouts with a transparency option. ")

st.divider()

# Create an outer 3-column layout
left_col, center_col, right_col = st.columns([1, 8, 1])

with center_col:
    
    st.header("1. Upload Photo")
    foreground_file = st.file_uploader(
        "**Upload your Foreground Photo (The Cutout)**", 
        type=['png', 'jpg', 'jpeg'],
        help="This image will have its background removed."
    )
    
    # Check if a file is uploaded to enable settings
    if foreground_file:
        st.header("2. Background Mode & Settings")
        
        # --- BACKGROUND MODE SELECTION ---
        bg_mode_selection = st.radio(
            "Select Output Mode:", 
            options=["Upload Image", "Solid Color", "Cutout Only"], 
            index=0, 
            horizontal=True,
            key="bg_mode_select"
        )
        
        # Normalize mode for logic
        bg_mode = "cutout" if bg_mode_selection == "Cutout Only" else ("color" if bg_mode_selection == "Solid Color" else "image")

        # --- CONDITIONAL BACKGROUND INPUTS ---
        background_file = None
        solid_color = "#FFFFFF"

        if bg_mode == 'image':
            background_file = st.file_uploader(
                "**Upload the New Background Image**", 
                type=['png', 'jpg', 'jpeg'],
                help="The cutout will be composited onto this image."
            )
        elif bg_mode == 'color':
            solid_color = st.color_picker(
                "Choose Solid Background Color", 
                value='#0000FF', 
                help="Select any color or enter a hex code (e.g., #FF0000)."
            )
            st.info("The size of the final image will be twice the size of the foreground image unless a background image was previously uploaded to set dimensions.")

        st.subheader("Placement & Size Controls")
        
        scale = st.slider(
            "Resize Factor for Cutout (0.1 = 10% | 1.0 = 100%)", 
            min_value=0.1, 
            max_value=1.0, 
            value=0.5, 
            step=0.05,
            help="Adjust the size of the foreground photo relative to its original size."
        )

        # Placement options are only relevant for compositing modes
        placement_mode = "Center"
        margin_ratio = 0.05
        seed = None
        jitter_ratio = 0.02
        alpha_threshold = 0

        if bg_mode in ('image', 'color'):
            placement_mode = st.selectbox("Placement Mode", options=["Center", "Random", "Rule of Thirds", "Corners"], index=0, help="Choose where to place the cutout on the background.")
            
            # Show advanced placement options
            if placement_mode in ("Random", "Corners"):
                margin_percent = st.slider("Edge margin (%)", min_value=0, max_value=20, value=5, step=1, help="Percent of the smaller background dimension used as a safe margin from edges.")
                margin_ratio = margin_percent / 100.0
            
            seed_input = st.text_input("Random seed (optional)", value="", help="Enter an integer to reproduce random placements.")
            seed = int(seed_input) if seed_input.strip().isdigit() else None

            if placement_mode == "Rule of Thirds":
                jitter_percent = st.slider("Thirds jitter (%)", min_value=0, max_value=10, value=2, step=1, help="Maximum jitter around the thirds intersection.")
                jitter_ratio = jitter_percent / 100.0
        
        # --- MASK REFINEMENT CONTROLS ---
        st.subheader("Mask Refinement Controls (Faux Erase/Restore)")
        st.markdown("Use the slider to refine the edges of the cutout.")
        alpha_threshold = st.slider(
            "Alpha Threshold (%)", 
            min_value=0, 
            max_value=90, 
            value=0, 
            step=5, 
            help="Increases the sensitivity of the background removal, making faint edges more transparent (acting like an erase tool on blurry mask edges). Try increasing this value to remove unwanted faint halos."
        )


        st.markdown("---")
        st.header("3. Result & Download")

        # Check if we have enough info to run the process
        can_process = foreground_file and (bg_mode == 'cutout' or bg_mode == 'color' or (bg_mode == 'image' and background_file))

        if can_process:
            # Show a progress spinner while processing
            with st.spinner('Processing image... This may take a moment to remove the background.'):
                output_image_io, error_message, output_format = process_image(
                    foreground_file,
                    bg_mode,
                    background_file,
                    solid_color,
                    scale,
                    placement_mode=placement_mode,
                    alpha_threshold=alpha_threshold,
                    margin_ratio=margin_ratio,
                    seed=seed,
                    jitter_ratio=jitter_ratio
                )

            if output_image_io:
                st.success(f"✅ Success! Image ready for download as {output_format}.")

                # Display the image centered
                st.image(
                    output_image_io, 
                    caption=f"Final Composited Image (Format: {output_format})", 
                    use_column_width=True
                )
                
                # Prepare download button
                download_label = f"⬇️ Download {output_format} Result"
                file_name = f"bg_updator_result.{output_format.lower()}"
                mime_type = f"image/{output_format.lower()}"
                
                dl_left, dl_center, dl_right = st.columns([1, 2, 1])
                with dl_center:
                    st.download_button(
                        label=download_label,
                        data=output_image_io.getvalue(),
                        file_name=file_name,
                        mime=mime_type,
                        type="primary"
                    )

            elif error_message:
                st.error(f"Processing Failed: {error_message}")
        else:
            if bg_mode == 'image' and not background_file:
                st.info("Please upload a Background Image to proceed with compositing.")
            elif bg_mode == 'cutout':
                st.info("The image will be processed when you interact with the settings.")
            else:
                 st.info("Adjust the settings to generate your updated image.")
    
    else:
        st.info("Please upload a Foreground Photo in Section 1 to begin configuring the image updator.")