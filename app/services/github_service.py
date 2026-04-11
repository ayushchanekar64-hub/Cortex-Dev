import requests
import base64
import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)


class GitHubService:
    def __init__(self, token: Optional[str] = None):
        self.github_token = token
        self.github_api_url = "https://api.github.com"
        
    def _get_headers(self, token: Optional[str] = None) -> Dict[str, str]:
        """Get headers with GitHub token for authentication."""
        auth_token = token or self.github_token
        if not auth_token:
            raise ValueError("GitHub token not provided.")
        return {
            "Authorization": f"token {auth_token}",
            "Accept": "application/vnd.github.v3+json"
        }
    
    async def create_repository(self, repo_name: str, description: str = "", private: bool = False, token: Optional[str] = None) -> Dict[str, Any]:
        """Create a new GitHub repository."""
        try:
            url = f"{self.github_api_url}/user/repos"
            data = {
                "name": repo_name,
                "description": description,
                "private": private,
                "auto_init": False
            }
            
            response = requests.post(url, json=data, headers=self._get_headers(token))
            
            if response.status_code == 201:
                logger.info(f"Repository {repo_name} created successfully")
                return {
                    "success": True,
                    "repo_url": response.json()["html_url"],
                    "clone_url": response.json()["clone_url"],
                    "repo_name": repo_name
                }
            elif response.status_code == 422:
                error_msg = response.json().get("errors", [{}])[0].get("message", "Repository already exists or invalid name")
                logger.error(f"Failed to create repository: {error_msg}")
                return {
                    "success": False,
                    "error": error_msg
                }
            else:
                logger.error(f"Failed to create repository: {response.status_code} - {response.text}")
                return {
                    "success": False,
                    "error": f"GitHub API error: {response.status_code}"
                }
        except Exception as e:
            logger.error(f"Error creating repository: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def create_file(self, owner: str, repo: str, file_path: str, content: str, commit_message: str = "Initial commit", token: Optional[str] = None) -> Dict[str, Any]:
        """Create or update a file in a GitHub repository."""
        try:
            url = f"{self.github_api_url}/repos/{owner}/{repo}/contents/{file_path}"
            
            # Encode content to base64
            encoded_content = base64.b64encode(content.encode()).decode()
            
            data = {
                "message": commit_message,
                "content": encoded_content
            }
            
            response = requests.put(url, json=data, headers=self._get_headers(token))
            
            if response.status_code in [200, 201]:
                logger.info(f"File {file_path} created/updated successfully")
                return {"success": True, "file_path": file_path}
            else:
                logger.error(f"Failed to create file {file_path}: {response.status_code} - {response.text}")
                return {
                    "success": False,
                    "error": f"Failed to create file: {response.status_code}",
                    "file_path": file_path
                }
        except Exception as e:
            logger.error(f"Error creating file {file_path}: {e}")
            return {
                "success": False,
                "error": str(e),
                "file_path": file_path
            }
    
    async def push_project_files(self, owner: str, repo: str, files: List[Dict[str, Any]], project_name: str, token: Optional[str] = None) -> Dict[str, Any]:
        """Push multiple project files to a GitHub repository."""
        try:
            results = []
            success_count = 0
            failed_count = 0
            
            for file_data in files:
                file_path = file_data.get("path", file_data.get("name", ""))
                content = file_data.get("content", "")
                
                if not file_path or not content:
                    logger.warning(f"Skipping file with missing path or content: {file_path}")
                    continue
                
                # Normalize file path
                if not file_path.startswith(repo.lower()):
                    file_path = f"{repo.lower()}/{file_path}"
                
                result = await self.create_file(
                    owner=owner,
                    repo=repo,
                    file_path=file_path,
                    content=content,
                    commit_message=f"Add {file_path}",
                    token=token
                )
                
                results.append(result)
                
                if result.get("success"):
                    success_count += 1
                else:
                    failed_count += 1
            
            logger.info(f"Pushed {success_count} files successfully, {failed_count} failed")
            
            return {
                "success": True,
                "total_files": len(files),
                "success_count": success_count,
                "failed_count": failed_count,
                "results": results
            }
        except Exception as e:
            logger.error(f"Error pushing project files: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_user_info(self, token: Optional[str] = None) -> Dict[str, Any]:
        """Get authenticated user information."""
        try:
            url = f"{self.github_api_url}/user"
            response = requests.get(url, headers=self._get_headers(token))
            
            if response.status_code == 200:
                user_data = response.json()
                return {
                    "success": True,
                    "username": user_data.get("login"),
                    "avatar_url": user_data.get("avatar_url"),
                    "name": user_data.get("name")
                }
            else:
                logger.error(f"Failed to get user info: {response.status_code}")
                return {
                    "success": False,
                    "error": "Failed to authenticate with GitHub"
                }
        except Exception as e:
            logger.error(f"Error getting user info: {e}")
            return {
                "success": False,
                "error": str(e)
            }


def get_github_service(token: Optional[str] = None) -> GitHubService:
    """Get a GitHub service instance with optional token."""
    return GitHubService(token=token)
