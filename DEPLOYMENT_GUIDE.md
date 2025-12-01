# PythonAnywhere Deployment Guide

## Prerequisites
- PythonAnywhere account (free tier available at https://www.pythonanywhere.com)
- Your Flask app files ready

## Important Notes

### ⚠️ Limitations on Free Tier:
1. **PyTorch & YOLO Model**: The free tier has limited CPU and may struggle with large models (your `best.pt` is 6MB)
2. **Storage**: Free tier has 512MB disk space - your YOLO model + dependencies may exceed this
3. **CPU Time**: Limited daily CPU seconds on free tier
4. **External Network**: Free accounts can only access whitelisted sites for email/API calls

### 💡 Recommendation:
Consider **PythonAnywhere Paid Tier** ($5/month) for better performance with ML models, or use **Render.com/Railway.app** which have better free tiers for ML applications.

---

## Step-by-Step Deployment to PythonAnywhere

### 1. Sign Up & Login
1. Go to https://www.pythonanywhere.com
2. Create a free account
3. Login to your dashboard

### 2. Upload Your Files
**Option A: Using Git (Recommended)**
```bash
# On PythonAnywhere Bash console:
git clone <your-repository-url>
cd <your-project-folder>
```

**Option B: Manual Upload**
1. Click on "Files" tab
2. Upload all files from `CODE/Frontend` folder:
   - `app.py`
   - `best.pt` (6MB YOLO model)
   - `templates/` folder
   - `static/` folder
   - `requirements_pythonanywhere.txt`

### 3. Set Up Virtual Environment
In PythonAnywhere Bash console:
```bash
# Create virtual environment with Python 3.10 (recommended for PyTorch)
mkvirtualenv --python=/usr/bin/python3.10 myenv

# Activate it
workon myenv

# Navigate to your project
cd ~/your-project-folder

# Install dependencies
pip install -r requirements_pythonanywhere.txt
```

**Note**: Installing PyTorch and ultralytics may take 10-15 minutes.

### 4. Configure Web App
1. Go to "Web" tab
2. Click "Add a new web app"
3. Choose "Manual configuration"
4. Select Python 3.10
5. Click through the wizard

### 5. Configure WSGI File
1. On the Web tab, click on the WSGI configuration file link
2. Replace the contents with:

```python
import sys
import os

# Add your project directory to the sys.path
project_home = '/home/YOUR_USERNAME/your-project-folder'
if project_home not in sys.path:
    sys.path = [project_home] + sys.path

# Set environment variable for Flask
os.environ['FLASK_APP'] = 'app.py'

# Import your Flask app
from app import app as application
```

**Replace**:
- `YOUR_USERNAME` with your PythonAnywhere username
- `your-project-folder` with your actual folder name

### 6. Set Virtual Environment Path
1. On the Web tab, find "Virtualenv" section
2. Enter the path: `/home/YOUR_USERNAME/.virtualenvs/myenv`
3. Replace `YOUR_USERNAME` with your actual username

### 7. Configure Static Files (Optional)
On the Web tab, add static files mapping:
- URL: `/static/`
- Directory: `/home/YOUR_USERNAME/your-project-folder/static/`

### 8. Create Uploads Directory
In Bash console:
```bash
cd ~/your-project-folder
mkdir uploads
chmod 755 uploads
```

### 9. Reload Web App
1. On the Web tab, click the green "Reload" button
2. Visit your site: `https://YOUR_USERNAME.pythonanywhere.com`

---

## Troubleshooting

### Error: "No module named 'cv2'"
The free tier may have issues with OpenCV. Try:
```bash
pip install opencv-python-headless==4.12.0.88
```

### Error: "Disk quota exceeded"
- Free tier only has 512MB storage
- PyTorch + YOLO models are large
- Consider upgrading or using lighter models

### Error: "CPU time limit exceeded"
- YOLO inference uses significant CPU
- Free tier has daily limits
- Upgrade to paid tier for production use

### Email Not Sending
- Free accounts can only connect to whitelisted sites
- Gmail (smtp.gmail.com) should work
- Check PythonAnywhere's whitelist: https://www.pythonanywhere.com/whitelist/

### Database Issues
- SQLite database will be created automatically
- Path: `/home/YOUR_USERNAME/your-project-folder/instance/users.db`

---

## Performance Optimization Tips

1. **Use opencv-python-headless** instead of opencv-python (smaller size)
2. **Consider model quantization** to reduce model size
3. **Add caching** for repeated predictions
4. **Use background tasks** for heavy processing (on paid tier)

---

## Alternative Deployment Options

If PythonAnywhere free tier doesn't work well:

### 1. **Render.com** (Better for ML apps)
- 750 hours/month free
- Better resources for ML models
- Easy Docker deployment

### 2. **Railway.app**
- $5 free credit monthly
- Good for ML applications
- Simple deployment

### 3. **Google Cloud Run**
- Pay per use
- Scales to zero (free when idle)
- Great for ML models

---

## Security Improvements Before Deployment

### 1. Change Secret Key
In `app.py`, replace:
```python
app.config['SECRET_KEY'] = 'your_secret_key'
```
With a strong random key:
```python
app.config['SECRET_KEY'] = 'generate-a-long-random-string-here'
```

### 2. Use Environment Variables
Create `.env` file:
```
SECRET_KEY=your-secret-key
EMAIL_ADDRESS=your-email@gmail.com
EMAIL_PASSWORD=your-app-password
```

Install python-dotenv:
```bash
pip install python-dotenv
```

Update app.py to use environment variables.

### 3. Don't Commit Sensitive Data
Create `.gitignore`:
```
*.db
.env
uploads/
__pycache__/
*.pyc
instance/
```

---

## Next Steps After Deployment

1. Test all features (registration, login, upload)
2. Monitor CPU usage and performance
3. Set up proper error logging
4. Consider upgrading if performance is insufficient
5. Add HTTPS (PythonAnywhere provides this automatically)

---

## Estimated Costs

- **Free Tier**: $0/month (limited resources, may not work well with YOLO)
- **Hacker Plan**: $5/month (better for ML apps)
- **Web Developer Plan**: $12/month (production-ready)

---

## Support & Resources

- PythonAnywhere Help: https://help.pythonanywhere.com/
- Flask Deployment Guide: https://help.pythonanywhere.com/pages/Flask/
- Ultralytics Documentation: https://docs.ultralytics.com/

Good luck with your deployment! 🚀
