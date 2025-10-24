#!/usr/bin/env python3
"""
Script to fetch merged pull requests from celigo/qa-automation repository
Requires GitHub Personal Access Token for private repository access
"""

import requests
import pandas as pd
import os
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import json

class CeligoPRFetcher:
    def __init__(self, token: str):
        """
        Initialize fetcher with GitHub token
        
        Args:
            token: GitHub Personal Access Token with repo access
        """
        self.token = token
        self.headers = {
            'Authorization': f'token {token}',
            'Accept': 'application/vnd.github.v3+json',
            'User-Agent': 'CeligoPRFetcher/1.0'
        }
        self.base_url = 'https://api.github.com'
        self.repo_owner = 'celigo'
        self.repo_name = 'celigo-qa-automation'
        
    def test_authentication(self) -> bool:
        """Test if the token is valid and has access to the repository"""
        try:
            # Test API access
            response = requests.get(f'{self.base_url}/user', headers=self.headers)
            if response.status_code != 200:
                print(f"❌ Authentication failed: {response.status_code}")
                return False
            
            user_info = response.json()
            print(f"✅ Authenticated as: {user_info.get('login', 'Unknown')}")
            
            # Test repository access
            repo_url = f'{self.base_url}/repos/{self.repo_owner}/{self.repo_name}'
            response = requests.get(repo_url, headers=self.headers)
            
            if response.status_code == 200:
                repo_info = response.json()
                print(f"✅ Repository access confirmed: {repo_info['full_name']}")
                print(f"   Private: {repo_info['private']}")
                print(f"   Description: {repo_info.get('description', 'No description')}")
                return True
            elif response.status_code == 404:
                print(f"❌ Repository {self.repo_owner}/{self.repo_name} not found or no access")
                return False
            else:
                print(f"❌ Repository access error: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Authentication test failed: {e}")
            return False
    
    def fetch_merged_prs(self, days_back: int = 90) -> List[Dict]:
        """
        Fetch merged pull requests from the last N days
        
        Args:
            days_back: Number of days to look back
            
        Returns:
            List of PR dictionaries
        """
        cutoff_date = datetime.now() - timedelta(days=days_back)
        cutoff_iso = cutoff_date.isoformat() + 'Z'
        
        print(f"Fetching merged PRs since: {cutoff_iso}")
        
        all_prs = []
        page = 1
        
        while True:
            print(f"Fetching page {page}...")
            
            # GitHub API for merged pull requests
            url = f'{self.base_url}/repos/{self.repo_owner}/{self.repo_name}/pulls'
            params = {
                'state': 'closed',
                'sort': 'updated',
                'direction': 'desc',
                'per_page': 100,
                'page': page
            }
            
            try:
                response = requests.get(url, headers=self.headers, params=params)
                response.raise_for_status()
                
                prs = response.json()
                
                if not prs:
                    print("No more PRs found.")
                    break
                
                # Filter for merged PRs within the date range
                page_prs = []
                for pr in prs:
                    # Skip if not merged
                    if not pr.get('merged_at'):
                        continue
                    
                    merged_at = datetime.fromisoformat(pr['merged_at'].replace('Z', '+00:00'))
                    
                    # Check if within our date range
                    if merged_at < cutoff_date.replace(tzinfo=merged_at.tzinfo):
                        print("Reached PRs older than cutoff date. Stopping.")
                        return all_prs
                    
                    # Extract PR data
                    pr_data = {
                        'pr_number': pr['number'],
                        'title': pr['title'],
                        'author': pr['user']['login'],
                        'created_at': pr['created_at'],
                        'merged_at': pr['merged_at'],
                        'labels': ','.join([label['name'] for label in pr.get('labels', [])]),
                        'url': pr['html_url'],
                        'state': pr['state'],
                        'draft': pr.get('draft', False),
                        'additions': pr.get('additions', 0),
                        'deletions': pr.get('deletions', 0),
                        'changed_files': pr.get('changed_files', 0)
                    }
                    
                    page_prs.append(pr_data)
                
                all_prs.extend(page_prs)
                print(f"Found {len(page_prs)} merged PRs on page {page}")
                
                # Check if we have more pages
                if len(prs) < 100:
                    break
                    
                page += 1
                
            except requests.exceptions.RequestException as e:
                print(f"❌ Error fetching PRs: {e}")
                break
        
        print(f"Total merged PRs found: {len(all_prs)}")
        return all_prs
    
    def save_to_csv(self, prs: List[Dict], filename: str = 'github_prs.csv') -> None:
        """Save PR data to CSV file"""
        if not prs:
            # Create empty CSV with correct headers
            df = pd.DataFrame(columns=[
                'pr_number', 'title', 'author', 'labels', 'created_at', 
                'merged_at', 'url', 'state', 'draft', 'additions', 
                'deletions', 'changed_files'
            ])
            df.to_csv(filename, index=False)
            print(f"✅ Created empty {filename} (no merged PRs found)")
            return
        
        df = pd.DataFrame(prs)
        df.to_csv(filename, index=False)
        print(f"✅ Saved {len(prs)} PRs to {filename}")
        
        # Show summary
        print(f"📊 Summary:")
        print(f"   - Total PRs: {len(prs)}")
        print(f"   - Date range: {df['merged_at'].min()} to {df['merged_at'].max()}")
        print(f"   - Authors: {df['author'].nunique()}")

def main():
    """Main execution function"""
    print("🔍 Celigo QA Automation PR Fetcher")
    print("=" * 50)
    
    # Get GitHub token from environment
    token = os.getenv('GITHUB_TOKEN')
    
    if not token:
        print("❌ GitHub token not found!")
        print("Please set your GitHub Personal Access Token:")
        print("   export GITHUB_TOKEN='your_token_here'")
        print()
        print("To create a token:")
        print("   1. Go to https://github.com/settings/tokens")
        print("   2. Click 'Generate new token (classic)'")
        print("   3. Select 'repo' scope for private repository access")
        print("   4. Copy the token and set it as environment variable")
        return
    
    # Initialize fetcher
    fetcher = CeligoPRFetcher(token)
    
    # Test authentication and repository access
    print("Testing authentication and repository access...")
    if not fetcher.test_authentication():
        print("❌ Cannot proceed without proper access")
        return
    
    print("\n" + "=" * 50)
    print("Fetching merged pull requests...")
    
    # Fetch PRs from last 90 days
    prs = fetcher.fetch_merged_prs(days_back=90)
    
    # Save to CSV
    fetcher.save_to_csv(prs, 'github_prs.csv')
    
    print("\n✅ Process completed successfully!")
    
    if prs:
        print(f"\nSample PR data:")
        for i, pr in enumerate(prs[:3]):  # Show first 3 PRs
            print(f"   {i+1}. #{pr['pr_number']}: {pr['title']}")
            print(f"      Author: {pr['author']}, Merged: {pr['merged_at']}")

if __name__ == "__main__":
    main()