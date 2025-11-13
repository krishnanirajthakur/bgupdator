Place the Travel Setu logo image here as `logo.png` so the Streamlit app can display it in the header.

Recommended:
- File name: `logo.png`
- Recommended display width: 300px (the app will resize to width=180 for header display)
- Format: PNG with transparent background preferred

How to add:
1. Create an `assets` folder at the project root if it doesn't exist.
2. Copy your `logo.png` into the `assets` folder.
3. Commit and push to GitHub:

```powershell
git add assets/logo.png
git commit -m "Add Travel Setu logo"
git push origin master
```

Once pushed, redeploy or wait for Streamlit Cloud to pick up changes and the app will show the logo automatically.
