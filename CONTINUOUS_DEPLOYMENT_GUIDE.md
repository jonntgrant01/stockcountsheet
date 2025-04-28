# Continuous Deployment for Streamlit Apps

This guide shows you how to set up continuous deployment for your Streamlit app using GitHub Actions and Streamlit Cloud.

## What is Continuous Deployment?

Continuous Deployment (CD) is a software development practice where code changes are automatically built, tested, and deployed to production. For your Streamlit app, this means:

1. You push changes to GitHub
2. GitHub Actions runs tests on your code
3. If tests pass, your app is automatically deployed to Streamlit Cloud

## Setup Instructions

### Step 1: Set Up GitHub Actions

A GitHub Actions workflow file (`.github/workflows/streamlit_deploy.yml`) is already included in this repository. This workflow:

- Runs when you push to the `main` branch
- Installs dependencies
- Runs linting and basic tests
- Prepares for deployment

### Step 2: Connect Streamlit Cloud to GitHub

1. Go to [Streamlit Community Cloud](https://share.streamlit.io/)
2. Sign in with your GitHub account
3. Click "New app"
4. Select your repository and branch (`main`)
5. Set the main file path to `app.py`
6. Click "Deploy"

### Step 3: Set Up Secrets (Optional)

If your app requires API keys or credentials:

1. Go to your Streamlit Cloud app
2. Click "Settings" > "Secrets"
3. Add your secrets in the format:
   ```
   OPENAI_API_KEY = "your-key-here"
   ```

4. For local development, create a `.streamlit/secrets.toml` file locally with the same secrets (don't commit this file)

### Step 4: Enable Auto-Deployment

In Streamlit Cloud:

1. Go to your app's settings
2. Ensure "Reboot app when..." is checked under "Advanced settings"
3. Select "Automatically update this app when the source code changes"

## How to Use

Once configured, your deployment workflow is simple:

1. Make changes to your code locally
2. Test locally with `streamlit run app.py`
3. Commit and push to GitHub:
   ```bash
   git add .
   git commit -m "Update feature X"
   git push
   ```

4. GitHub Actions will run tests
5. If tests pass, Streamlit Cloud will detect the changes and redeploy automatically
6. Check your app's URL to see the updated version

## Monitoring Deployments

### GitHub Actions Dashboard

To monitor the test and build process:

1. Go to your GitHub repository
2. Click the "Actions" tab
3. You'll see all workflow runs listed by commit
4. Click any run to see detailed logs and status

### Streamlit Cloud Dashboard

To check deployment status:

1. Go to [Streamlit Cloud](https://share.streamlit.io/)
2. Sign in and view your apps
3. Each app shows its current status
4. Click an app to see its logs and settings

## Best Practices

1. **Use Version Control Properly**:
   - Work in feature branches
   - Use pull requests for major changes
   - Only merge to main when features are ready for deployment

2. **Write Tests**:
   - Add pytest tests to verify your app's functionality
   - Test both the UI components and data processing logic

3. **Monitor Your App**:
   - Check Streamlit Cloud logs regularly
   - Set up error alerting if possible

4. **Manage Dependencies**:
   - Keep your `requirements.txt` up to date
   - Pin specific versions to avoid compatibility issues

## Troubleshooting Common Issues

### GitHub Actions Workflow Failing

If your GitHub Actions workflow fails:

1. Check the error logs in the Actions tab
2. Common issues include:
   - Missing dependencies in `requirements.txt`
   - Syntax errors in Python code
   - Failed tests

### Streamlit Cloud Deployment Issues

If your app doesn't deploy correctly:

1. Check the app logs in Streamlit Cloud
2. Verify that your `requirements.txt` includes all dependencies
3. Check that any required secrets are properly configured
4. Ensure your app works locally before pushing

## Advanced Configuration

### Custom Domains

To use a custom domain with your Streamlit app:

1. Go to your app's settings in Streamlit Cloud
2. Click "Custom domain"
3. Follow the instructions to set up DNS records
4. Wait for DNS propagation and SSL certificate issuance

### Multi-Environment Setup

For a professional workflow with staging and production environments:

1. Create two branches: `staging` and `main`
2. Deploy the `staging` branch to a separate Streamlit Cloud app
3. Test changes in staging before merging to `main`
4. Configure GitHub Actions to run different workflows for each branch

---

By following this guide, you'll have a professional continuous deployment pipeline for your Streamlit application.