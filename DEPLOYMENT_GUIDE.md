# GitHub Deployment Guide for Stock Count Streamlit App

This guide walks you through the process of deploying your Stock Count Streamlit application using GitHub and Streamlit Community Cloud.

## Prerequisites

Before deploying, ensure you have:

- A GitHub account
- Your Stock Count app code ready and working locally
- Basic familiarity with Git commands

## Step 1: Prepare Your Repository

1. **Create a GitHub Repository**:
   - Go to [GitHub](https://github.com) and log in
   - Click the "+" icon in the top-right corner and select "New repository"
   - Name your repository (e.g., "stockcountapp")
   - Optionally add a description
   - Choose public or private visibility
   - Click "Create repository"

2. **Initialize Your Local Repository**:
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   ```

3. **Connect Your Local Repository to GitHub**:
   ```bash
   git remote add origin https://github.com/username/stockcountapp.git
   git branch -M main
   git push -u origin main
   ```

## Step 2: Ensure Required Files Exist

Ensure your repository includes:

1. **app.py**: The main Streamlit application file
2. **requirements.txt**: Lists all Python dependencies
   ```
   streamlit==1.29.0
   pandas==2.1.0
   numpy==1.24.0
   pillow==10.0.0
   ```

3. **.streamlit/config.toml**: Streamlit configuration
   ```toml
   [server]
   headless = true
   enableCORS = false
   
   [browser]
   serverAddress = "0.0.0.0"
   gatherUsageStats = false
   
   [theme]
   primaryColor = "#6a28e8"
   ```

4. **README.md**: Project documentation
5. **assets folder**: Contains static assets like images

## Step 3: Deploy on Streamlit Community Cloud

1. **Go to Streamlit Community Cloud**:
   - Visit [https://share.streamlit.io/](https://share.streamlit.io/)
   - Sign in with your GitHub account
   - Allow Streamlit to access your repositories if prompted

2. **Select Your Repository**:
   - Click "New app"
   - Choose your GitHub account
   - Select the repository containing your Streamlit app
   - Select the branch (usually "main")
   - Enter the path to your main file ("app.py")

3. **Configure Advanced Settings**:
   - Add any required secrets (if applicable)
   - Configure Python version (3.10+ recommended)
   - Click "Deploy!"

4. **Wait for Deployment**:
   - Streamlit Cloud will build and deploy your app
   - You'll see a progress indicator during deployment
   - Once complete, you'll get a unique URL for your app

## Step 4: Update Your App

Whenever you want to update your deployed app:

1. Make changes to your code locally
2. Commit and push changes to GitHub:
   ```bash
   git add .
   git commit -m "Update app with new features"
   git push
   ```
3. Streamlit Community Cloud will automatically detect changes and rebuild your app

## Step 5: Custom Domain (Optional)

For professional deployments, you can configure a custom domain:

1. Go to your app's settings in Streamlit Community Cloud
2. Click "Custom domain"
3. Follow the instructions to set up DNS records
4. Verify ownership and configure SSL

## Common Issues and Solutions

### App Fails to Deploy

- Check your requirements.txt for incompatible packages
- Ensure all imports in your code match packages in requirements.txt
- Look at build logs for specific errors

### CSS Styling Issues

- Use relative paths for all assets
- Ensure your CSS selectors match Streamlit's current DOM structure
- Test CSS changes locally before deploying

### File Upload/Download Issues

- Always use Streamlit's built-in functions for file operations
- Don't rely on local file system for persistent storage

## Resources

- [Streamlit Documentation](https://docs.streamlit.io/)
- [Streamlit Community Cloud Documentation](https://docs.streamlit.io/streamlit-community-cloud)
- [GitHub Documentation](https://docs.github.com/)

---

Happy deploying! If you encounter any issues, check the Streamlit Community forums or open an issue in your GitHub repository.