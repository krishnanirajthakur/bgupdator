# Deployment Guide: Connect to GitHub & Deploy Travel Setu Virtual Darshan to Streamlit Cloud

## 📋 Prerequisites
- GitHub account
- Streamlit Cloud account (free at share.streamlit.io)
- Git installed on your machine

## 🚀 Step 1: Push to GitHub

### 1.1 Initialize Git (if not already done)
```powershell
cd c:\Users\krish\OneDrive\Desktop\TravelSetuVirtual
git init
git add .
git commit -m "Initial commit: Travel Setu Virtual Darshan Streamlit app"
git branch -M master
```

### 1.2 Connect to GitHub Repository
Replace the URL with your actual GitHub repo:
```powershell
git remote add origin https://github.com/krishnanirajthakur/travelsetuvirtualdarshan.git
git push -u origin master
```

**If you get an authentication error**, use GitHub Personal Access Token:
```powershell
git remote set-url origin https://<YOUR_GITHUB_USERNAME>:<YOUR_PERSONAL_ACCESS_TOKEN>@github.com/krishnanirajthakur/travelsetuvirtualdarshan.git
```

## 📤 Step 2: Deploy to Streamlit Cloud

### 2.1 Create Streamlit Cloud Account
- Go to [share.streamlit.io](https://share.streamlit.io)
- Sign up with GitHub (recommended)

### 2.2 Deploy Your App
1. Click **"New app"**
2. Select:
   - **Repository**: krishnanirajthakur/travelsetuvirtualdarshan
   - **Branch**: master
   - **Main file path**: photocompositor.py
3. Click **"Deploy"**

The app will be live at: `https://travelsetuvirtualdarshan.streamlit.app`

Tip: To display the Travel Setu logo in the app header, add a file `assets/logo.png` to the repository (recommended size ~300x100). The app will load this automatically if present.

## 🔄 Step 3: Continuous Updates

After deployment, any push to GitHub automatically updates your app:

```powershell
# Make changes to your code
# Then commit and push
git add .
git commit -m "Update: Added new features"
git push origin master
```

Your Streamlit Cloud app will automatically redeploy within minutes!

## 🐛 Troubleshooting

### Issue: "rembg" takes too long to download
**Solution**: The first run downloads the AI model (~350MB). This is normal.
- Streamlit Cloud will cache it for future deployments

### Issue: "Import Error: No module named 'streamlit'"
**Solution**: Make sure `requirements.txt` has all dependencies

### Issue: App crashes on Streamlit Cloud
**Steps**:
1. Check the **Manage app** → **Logs** for errors
2. Verify all imports work locally: `python photocompositor.py`
3. Check if packages need different versions for Linux (Streamlit Cloud uses Linux)

## 📁 Project Structure (Complete)

```
TravelSetuVirtual/
├── photocompositor.py          # Main Streamlit app
├── app.py                       # Alternative entry point
├── requirements.txt             # Dependencies
├── README.md                    # Project documentation
├── .gitignore                   # Git ignore rules
└── .streamlit/
    └── config.toml             # Streamlit configuration
```

## 🔐 Important Security Notes

✅ Keep sensitive data in Streamlit secrets:
- Go to **Manage app** → **Secrets**
- Add environment variables there instead of in code

✅ Never commit:
- API keys
- Passwords
- `.env` files (already in .gitignore)

## 📚 Useful Links

- **Streamlit Docs**: https://docs.streamlit.io
- **Streamlit Cloud Docs**: https://docs.streamlit.io/streamlit-cloud
- **rembg Documentation**: https://github.com/danielgatis/rembg
- **GitHub Desktop** (alternative to Git CLI): https://desktop.github.com

## ✅ Deployment Checklist

- [ ] Code pushed to GitHub
- [ ] `requirements.txt` has all dependencies
- [ ] Streamlit Cloud account created
- [ ] App deployed successfully
- [ ] Tested the live link
- [ ] (Optional) Custom domain configured
- [ ] (Optional) GitHub Actions configured for CI/CD
