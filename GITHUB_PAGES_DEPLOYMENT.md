# Deploying to GitHub Pages (Alternative Method)

While Streamlit Community Cloud is the recommended deployment method, you can also create a static landing page on GitHub Pages that links to your Streamlit deployment or provides information about your app.

## Method 1: Creating a Landing Page for Your App

This method creates a simple HTML page on GitHub Pages that links to your Streamlit Cloud deployment.

### Step 1: Create a GitHub Pages Branch

```bash
# Create and switch to a new orphan branch (no history)
git checkout --orphan gh-pages

# Remove all files from staging
git rm -rf .

# Create an index.html file
cat > index.html << EOL
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Stock Count App</title>
    <style>
        body {
            font-family: 'Helvetica Neue', Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
        }
        .header {
            text-align: center;
            margin-bottom: 40px;
        }
        .logo {
            max-width: 200px;
            margin-bottom: 20px;
        }
        .button {
            display: inline-block;
            background: linear-gradient(135deg, #8a2be2, #6a28e8);
            color: white;
            padding: 12px 24px;
            border-radius: 50px;
            text-decoration: none;
            font-weight: bold;
            margin: 20px 0;
            box-shadow: 0 4px 12px rgba(106, 40, 232, 0.2);
            transition: all 0.3s ease;
        }
        .button:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 15px rgba(106, 40, 232, 0.3);
        }
        .features {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin: 40px 0;
        }
        .feature {
            background-color: #f9f7ff;
            border-radius: 8px;
            padding: 20px;
            text-align: center;
        }
        .screenshots {
            margin: 40px 0;
        }
        .screenshots img {
            max-width: 100%;
            border-radius: 8px;
            margin-bottom: 20px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        }
        footer {
            margin-top: 60px;
            text-align: center;
            color: #666;
            font-size: 0.9em;
        }
    </style>
</head>
<body>
    <div class="header">
        <img src="https://raw.githubusercontent.com/username/stockcountapp/main/assets/company_logo.png" alt="Company Logo" class="logo">
        <h1>Stock Count App</h1>
        <p>A powerful Streamlit-based stock counting application for efficient inventory management</p>
        <a href="https://share.streamlit.io/username/stockcountapp/main/app.py" class="button">Launch App</a>
    </div>
    
    <div class="features">
        <div class="feature">
            <h3>Smart Search</h3>
            <p>Advanced search with multi-word matching and intelligent scoring</p>
        </div>
        <div class="feature">
            <h3>User-Friendly</h3>
            <p>Intuitive iOS-style interface with responsive design</p>
        </div>
        <div class="feature">
            <h3>CSV Support</h3>
            <p>Import and export inventory data with CSV compatibility</p>
        </div>
        <div class="feature">
            <h3>Location Tracking</h3>
            <p>Tag count locations for better inventory organization</p>
        </div>
    </div>
    
    <div class="screenshots">
        <h2>App Screenshots</h2>
        <img src="https://user-images.githubusercontent.com/your-id/screenshot1.png" alt="App Screenshot 1">
    </div>
    
    <footer>
        <p>© 2025 ARC Inspirations. All rights reserved.</p>
        <p><a href="https://github.com/username/stockcountapp">View on GitHub</a></p>
    </footer>
</body>
</html>
EOL

# Add the index.html file
git add index.html

# Commit the changes
git commit -m "Add GitHub Pages landing page"

# Push to the gh-pages branch
git push origin gh-pages

# Switch back to the main branch
git checkout main
```

### Step 2: Enable GitHub Pages

1. Go to your GitHub repository
2. Click on "Settings"
3. Scroll down to the "GitHub Pages" section
4. Select the "gh-pages" branch as the source
5. Click "Save"

Your landing page will be available at: `https://username.github.io/stockcountapp`

## Method 2: Creating an iframe Embed of Your Streamlit App

For a more advanced approach, you can embed your Streamlit app directly in your GitHub Pages site using an iframe.

### Create an index.html with iframe Embed

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Stock Count App | Embedded</title>
    <style>
        body, html {
            margin: 0;
            padding: 0;
            height: 100%;
            overflow: hidden;
        }
        .container {
            display: flex;
            flex-direction: column;
            height: 100vh;
        }
        .header {
            background: linear-gradient(135deg, #8a2be2, #6a28e8);
            color: white;
            padding: 10px 20px;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }
        .header img {
            height: 40px;
        }
        .header h1 {
            margin: 0;
            font-size: 1.2rem;
        }
        .iframe-container {
            flex: 1;
            overflow: hidden;
        }
        iframe {
            width: 100%;
            height: 100%;
            border: none;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <img src="https://raw.githubusercontent.com/username/stockcountapp/main/assets/company_logo.png" alt="Logo">
            <h1>Stock Count Application</h1>
            <a href="https://github.com/username/stockcountapp" target="_blank" style="color: white;">View on GitHub</a>
        </div>
        <div class="iframe-container">
            <iframe src="https://share.streamlit.io/username/stockcountapp/main/app.py" allowfullscreen></iframe>
        </div>
    </div>
</body>
</html>
```

## Important Notes

1. Replace `username` with your actual GitHub username in all URLs
2. Update the Streamlit Cloud URL once you have deployed your app
3. GitHub Pages only supports static content, so your Streamlit app must still be hosted elsewhere (like Streamlit Cloud)

## Benefits of This Approach

1. Professional landing page for your app
2. SEO benefits from GitHub Pages
3. Control over the presentation of your app 
4. Ability to add documentation, screenshots, and feature descriptions