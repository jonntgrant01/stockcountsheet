# Stock Count Application

A Streamlit-based stock counting application for efficient inventory management.

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://share.streamlit.io/)
[![GitHub license](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

<p align="center">
  <img src="assets/company_logo.png" alt="ARC Inspirations Logo" width="200"/>
</p>

## Features

- Advanced search functionality with multi-word matching
- User-friendly data entry interface with iOS-style design
- Responsive and intuitive UI with custom styling
- Recent search history tracking (up to 10 searches)
- CSV import/export capabilities with special column handling
- Real-time count tracking with location tagging
- Count history and session management

## Deployment Guides

We've created comprehensive deployment guides to help you get your app online:

1. **[Basic Deployment Guide](DEPLOYMENT_GUIDE.md)** - Step-by-step instructions for deploying on Streamlit Community Cloud
2. **[GitHub Pages Deployment](GITHUB_PAGES_DEPLOYMENT.md)** - Alternative deployment using GitHub Pages
3. **[Continuous Deployment Guide](CONTINUOUS_DEPLOYMENT_GUIDE.md)** - Set up automated testing and deployment

You can also run the included deployment checker:

```bash
python deployment_check.py
```

This script will analyze your project and provide guidance on deployment readiness.

## Quick Deployment Steps

1. Fork this repository
2. Go to [https://share.streamlit.io/](https://share.streamlit.io/)
3. Sign in with your GitHub account
4. Connect your forked repository
5. Set the main file path to `app.py`
6. Deploy the application

## Local Development

```bash
# Install dependencies
pip install streamlit pandas numpy pillow trafilatura

# Run the application
streamlit run app.py
```

### Required Dependencies

For deployment or local development, make sure to install:

- streamlit>=1.22.0
- pandas>=1.5.0
- numpy>=1.22.0
- pillow>=9.0.0
- trafilatura>=1.6.0

When deploying on Streamlit Cloud, these dependencies will be automatically installed.

## CSV File Format

This application expects CSV files with:
- Metadata in row 1
- Column headers in row 2
- Data starting from row 3
- Specific columns like [E]Close SC for count values

## Configuration

Adjust the configuration in `.streamlit/config.toml` for custom styling and server settings.

## Deployment Utilities

- **GitHub Actions Workflow** - Automatic testing before deployment (see `.github/workflows/`)
- **Deployment Check Script** - Validates your app's deployment readiness
- **Streamlit Configuration** - Pre-configured for cloud deployment