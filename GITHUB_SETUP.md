# GitHub Integration Setup

This document explains how to configure and use the GitHub integration feature in Cortex-Dev.

## Features

- Export generated projects directly to GitHub
- Create new repositories automatically
- Push all project files to GitHub
- Token-based authentication

## Configuration Steps

### Step 1: Generate GitHub Personal Access Token

1. Go to GitHub: https://github.com/settings/tokens
2. Click "Generate new token" (classic)
3. Configure the token:
   - **Note**: Enter a descriptive name (e.g., "Cortex-Dev")
   - **Expiration**: Choose an expiration period (recommended: 90 days)
   - **Scopes**: Select the following scopes:
     - `repo` - Full control of private repositories
     - `workflow` - Update GitHub Action workflows
4. Click "Generate token"
5. **Important**: Copy the token immediately (you won't see it again!)

### Step 2: Configure in Cortex-Dev

There are two ways to configure your GitHub token:

#### Option A: Via UI (Recommended)

1. Generate a project in Cortex-Dev
2. Click the "GITHUB" button in the header
3. A modal will appear asking for your GitHub token
4. Paste your token and click "Connect & Export"
5. The token will be saved in your browser's localStorage

#### Option B: Via Backend Environment Variable

1. Open the `.env` file in the backend directory
2. Add the following line:
   ```
   GITHUB_TOKEN=ghp_your_token_here
   ```
3. Restart the backend server

## Usage

### Export to GitHub

1. Generate a project using Cortex-Dev
2. Once files are generated, click the "GITHUB" button in the header
3. If not configured, you'll be prompted to enter your GitHub token
4. The system will:
   - Create a new repository with the project name
   - Push all generated files to the repository
   - Display success/failure status in the logs and chat
5. You'll receive the repository URL in the chat

## API Endpoints

### Backend Endpoints

- `GET /api/github/user` - Get authenticated GitHub user info
- `POST /api/github/create-repo` - Create a new repository
- `POST /api/github/push-files` - Push files to a repository

### Authentication

All GitHub API calls require authentication via:
- Authorization header: `token YOUR_GITHUB_TOKEN`

## Security Notes

- **Never commit your GitHub token to version control**
- Tokens are stored in localStorage (browser-based) or environment variables
- Regularly rotate your GitHub tokens
- Use the minimum required scopes
- Consider using GitHub Apps for production deployments

## Troubleshooting

### Token Issues

**Error**: "Invalid GitHub token"
- Verify the token is correctly copied
- Ensure the token has the required scopes (repo, workflow)
- Check if the token has expired

**Error**: "Failed to create repository"
- Repository name may already exist
- Repository name may contain invalid characters
- Check your GitHub account limits

### File Push Issues

**Error**: "Failed to push files"
- Check if repository exists
- Verify file paths are valid
- Ensure token has write permissions

## Example Workflow

```typescript
// Frontend automatically handles this when you click GITHUB button
const handleExportToGitHub = async () => {
  // 1. Check for token
  if (!githubToken) {
    setShowGithubModal(true)
    return
  }
  
  // 2. Get user info
  const userData = await fetch('/api/github/user')
  
  // 3. Create repository
  const repoData = await fetch('/api/github/create-repo', {
    method: 'POST',
    body: JSON.stringify({ repo_name: 'my-project' })
  })
  
  // 4. Push files
  const pushData = await fetch('/api/github/push-files', {
    method: 'POST',
    body: JSON.stringify({ files: generatedFiles })
  })
}
```

## Additional Resources

- [GitHub Personal Access Tokens Documentation](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token)
- [GitHub REST API Documentation](https://docs.github.com/en/rest)
- [GitHub Scopes Documentation](https://docs.github.com/en/developers/apps/building-oauth-apps/scopes-for-oauth-apps)
