# 🚀 GitHub Setup Guide

Step-by-step instructions to push your Data to Video Encoder project to GitHub.

## 📋 Prerequisites

1. **Git installed** on your computer
   ```bash
   git --version
   ```
   If not installed: https://git-scm.com/downloads

2. **GitHub account** created at https://github.com

## 🎯 Step-by-Step Instructions

### Step 1: Initialize Local Repository

Navigate to your project directory:
```bash
cd /path/to/your/project
```

Run the setup script (or do it manually):
```bash
bash setup_git.sh
```

**OR manually:**
```bash
git init
git add .
git status
```

### Step 2: Make Your First Commit

```bash
git commit -m "Initial commit: Data to Video Encoder with Basic and Advanced modes"
```

### Step 3: Create GitHub Repository

1. Go to https://github.com
2. Click the **"+"** icon (top right) → **"New repository"**
3. Fill in repository details:
   - **Name**: `data-to-video-encoder` (or your preferred name)
   - **Description**: "Convert any file to video using RGB pixels and audio channels"
   - **Public** or **Private** (your choice)
   - ⚠️ **Do NOT** initialize with README, .gitignore, or license (we already have these)
4. Click **"Create repository"**

### Step 4: Connect Local Repository to GitHub

GitHub will show you commands. Use these:

```bash
# Add remote repository
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git

# Rename branch to main (if needed)
git branch -M main

# Push to GitHub
git push -u origin main
```

**Example:**
```bash
git remote add origin https://github.com/johndoe/data-to-video-encoder.git
git branch -M main
git push -u origin main
```

### Step 5: Enter GitHub Credentials

When prompted, enter:
- **Username**: Your GitHub username
- **Password**: Your Personal Access Token (NOT your account password)

#### 🔑 Creating a Personal Access Token (if needed)

1. Go to https://github.com/settings/tokens
2. Click **"Generate new token"** → **"Generate new token (classic)"**
3. Give it a name: "data-to-video-encoder"
4. Select scopes: Check **"repo"** (full control of private repositories)
5. Click **"Generate token"**
6. **Copy the token immediately** (you won't see it again!)
7. Use this token as your password when pushing

### Step 6: Verify Upload

1. Go to your GitHub repository URL
2. You should see all your files uploaded
3. The README.md should be displayed on the main page

## 📁 Repository Structure

After upload, your repository will contain:

```
data-to-video-encoder/
├── .gitignore
├── LICENSE
├── README.md (this will be README_MAIN.md)
├── README_ADVANCED.md
├── requirements.txt
├── data_to_video.py
├── advanced_data_to_video.py
├── example_usage.py
├── example_advanced.py
└── compare_encoders.py
```

## 🔄 Future Updates

After making changes to your code:

```bash
# Check what changed
git status

# Add all changes
git add .

# Commit with a message
git commit -m "Description of what you changed"

# Push to GitHub
git push
```

## 🌿 Useful Git Commands

```bash
# Check repository status
git status

# View commit history
git log --oneline

# View remote repository URL
git remote -v

# Create a new branch
git checkout -b feature-name

# Switch branches
git checkout main

# Pull latest changes from GitHub
git pull

# Clone your repo to another machine
git clone https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
```

## ⚠️ Troubleshooting

### Problem: "Permission denied"
**Solution**: Make sure you're using a Personal Access Token, not your password.

### Problem: "Remote origin already exists"
**Solution**: Remove and re-add the remote:
```bash
git remote remove origin
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
```

### Problem: "Failed to push"
**Solution**: Pull first, then push:
```bash
git pull origin main --allow-unrelated-histories
git push -u origin main
```

### Problem: Large files won't upload
**Solution**: Make sure your .gitignore is working and test files aren't being tracked:
```bash
git rm --cached *.bin *.mp4
git commit -m "Remove large files"
git push
```

## 📝 Best Practices

1. **Commit often** with clear messages
2. **Don't commit** large test files (they're in .gitignore)
3. **Write clear commit messages**: "Add audio encoding feature" not "Update stuff"
4. **Keep README updated** with new features
5. **Tag releases**: 
   ```bash
   git tag -a v1.0 -m "Version 1.0: Initial release"
   git push origin v1.0
   ```

## 🎉 You're Done!

Your project is now on GitHub! Share the link with others:
```
https://github.com/YOUR_USERNAME/data-to-video-encoder
```

## 📈 Optional: Add Badges to README

Add these to your README.md for a professional look:

```markdown
![Python](https://img.shields.io/badge/python-3.7+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Stars](https://img.shields.io/github/stars/YOUR_USERNAME/YOUR_REPO_NAME?style=social)
```

## 🌟 Making Your Repository Popular

1. **Add topics** to your repository (Settings → Topics): `python`, `video-encoding`, `data-storage`, `steganography`
2. **Write a good README** with examples and screenshots
3. **Add a demo video** or GIF showing it in action
4. **Share on social media** and relevant subreddits
5. **Add to awesome-lists** related to Python projects

---

**Need help?** Open an issue on GitHub or check the Git documentation: https://git-scm.com/doc
