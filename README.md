# Travel Setu Virtual Darshan - Streamlit App

A web application that removes backgrounds from images and composites them onto new backgrounds. Presented by Travel Setu.

## Features

✂️ **Background Removal** - Uses AI-powered rembg to automatically remove backgrounds
🎨 **Image Compositing** - Overlay processed images onto custom backgrounds
📐 **Scaling Control** - Adjust the size of your cutout image
⬇️ **Easy Download** - Download your final composited image as JPEG

## Installation

### Local Setup

1. Clone the repository:
```bash
git clone https://github.com/krishnanirajthakur/travelsetuvirtualdarshan.git
cd TravelSetuVirtual
```

2. Create a virtual environment:
```bash
python -m venv venv
venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run the app:
```bash
streamlit run photocompositor.py
```

The app will open at `http://localhost:8501`

## Deployment

### Deploy to Streamlit Cloud

1. Push your code to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Click "New app"
4. Select your repository, branch, and main file (`photocompositor.py`)
5. Click "Deploy"

## Dependencies

- **streamlit** - Web framework for data apps
- **rembg** - AI-powered background removal
- **Pillow** - Image processing

See `requirements.txt` for versions.

## Usage

1. Upload a foreground image (the image you want to cut out)
2. Upload a background image (the new background)
3. Adjust the scale factor to resize your cutout
4. Download the final composited image

## License

MIT License - feel free to use and modify as needed.
