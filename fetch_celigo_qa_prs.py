#!/usr/bin/env python3
"""
Fetch merged pull requests from celigo/celigo-qa-automation repository
for the last 160 days and save to cleaned_github_prs.csv

Usage:
    export GITHUB_TOKEN='your_token_here'
    python3 fetch_celigo_qa_prs.py
"""

import requests
import pandas as pd
import os
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import sys

def fetch_github_prs(token: str, owner: str, repo: str, days_back: int = 160) -> List[Dict]:
    """
    Fetch merged pull requests from GitHub repository
    
    Args:
        token: GitHub Personal Access Token
        owner: Repository owner (e.g., 'celigo')
        repo: Repository name (e.g., 'celigo-qa-automation')
        days_back: Number of days to look back (default: 160)
    
    Returns:
        List of PR dictionaries
    """
    headers = {
        'Authorization': f'token {token}',
        'Accept': 'application/vnd.github.v3+json',
        'User-Agent': 'CeligoQAPRFetcher/1.0'
    }
    
    # Calculate cutoff date
    cutoff_date = datetime.now() - timedelta(days=days_back)
    cutoff_iso = cutoff_date.isoformat() + 'Z'
    
    print(f"🔍 Fetching merged PRs from {owner}/{repo}")
    print(f"📅 Looking for PRs merged since: {cutoff_date.strftime('%Y-%m-%d')}")
    
    # Test repository access first
    repo_url = f'https://api.github.com/repos/{owner}/{repo}'
    response = requests.get(repo_url, headers=headers)
    
    if response.status_code == 404:
        print(f"❌ Repository {owner}/{repo} not found or not accessible")
        print("💡 Possible issues:")
        print("   - Repository doesn't exist")
        print("   - Repository is private and token lacks access")
        print("   - Token doesn't have 'repo' scope")
        return []
    elif response.status_code != 200:
        print(f"❌ Error accessing repository: HTTP {response.status_code}")
        return []
    
    repo_info = response.json()
    print(f"✅ Repository found: {repo_info['full_name']}")
    print(f"   Private: {repo_info['private']}")
    print(f"   Description: {repo_info.get('description', 'No description')}")
    
    # Fetch pull requests
    all_prs = []
    page = 1
    
    while True:
        print(f"📄 Fetching page {page}...")
        
        url = f'https://api.github.com/repos/{owner}/{repo}/pulls'
        params = {
            'state': 'closed',
            'sort': 'updated',
            'direction': 'desc',
            'per_page': 100,
            'page': page
        }
        
        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            
            prs = response.json()
            
            if not prs:
                print("📄 No more PRs found")
                break
            
            # Process PRs on this page
            page_merged_prs = []
            for pr in prs:
                # Skip if not merged
                if not pr.get('merged_at'):
                    continue
                
                # Parse merge date
                merged_at = datetime.fromisoformat(pr['merged_at'].replace('Z', '+00:00'))
                
                # Check if within our date range
                if merged_at < cutoff_date.replace(tzinfo=merged_at.tzinfo):
                    print(f"⏰ Reached PRs older than {days_back} days, stopping")
                    return all_prs
                
                # Extract PR data
                pr_data = {
                    'pr_number': pr['number'],
                    'title': pr['title'],
                    'author': pr['user']['login'],
                    'created_at': pr['created_at'],
                    'merged_at': pr['merged_at'],
                    'labels': ','.join([label['name'] for label in pr.get('labels', [])])
                }
                
                page_merged_prs.append(pr_data)
            
            all_prs.extend(page_merged_prs)
            print(f"✅ Found {len(page_merged_prs)} merged PRs on page {page}")
            
            # Check if we have more pages
            if len(prs) < 100:
                print("📄 Reached end of results")
                break
                
            page += 1
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Error fetching PRs: {e}")
            break
    
    print(f"🎯 Total merged PRs found: {len(all_prs)}")
    return all_prs

def save_to_csv(prs: List[Dict], filename: str = 'cleaned_github_prs.csv') -> None:
    """Save PR data to CSV file"""
    
    # Define expected columns
    columns = ['pr_number', 'title', 'author', 'created_at', 'merged_at', 'labels']
    
    if not prs:
        # Create empty CSV with correct headers
        df = pd.DataFrame(columns=columns)
        df.to_csv(filename, index=False)
        print(f"📄 Created empty {filename} (no merged PRs found)")
        return
    
    # Create DataFrame and ensure column order
    df = pd.DataFrame(prs)
    df = df.reindex(columns=columns)
    
    # Save to CSV
    df.to_csv(filename, index=False)
    print(f"💾 Saved {len(prs)} PRs to {filename}")
    
    # Show summary statistics
    if len(prs) > 0:
        print(f"\n📊 Summary:")
        print(f"   Total PRs: {len(prs)}")
        print(f"   Date range: {df['merged_at'].min()} to {df['merged_at'].max()}")
        print(f"   Unique authors: {df['author'].nunique()}")
        
        # Show top authors
        author_counts = df['author'].value_counts().head(5)
        print(f"   Top authors:")
        for author, count in author_counts.items():
            print(f"     - {author}: {count} PRs")

def main():
    """Main execution function"""
    print("🚀 Celigo QA Automation PR Fetcher")
    print("=" * 50)
    
    # Configuration
    REPO_OWNER = 'celigo'
    REPO_NAME = 'celigo-qa-automation'
    DAYS_BACK = 160
    OUTPUT_FILE = 'cleaned_github_prs.csv'
    
    # Get token from environment
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
        sys.exit(1)
    
    # Test authentication
    headers = {'Authorization': f'token {token}'}
    response = requests.get('https://api.github.com/user', headers=headers)
    
    if response.status_code != 200:
        print(f"❌ Authentication failed: HTTP {response.status_code}")
        sys.exit(1)
    
    user_info = response.json()
    print(f"✅ Authenticated as: {user_info.get('login', 'Unknown')}")
    
    # Fetch PRs
    print(f"\n📥 Fetching PRs from {REPO_OWNER}/{REPO_NAME} (last {DAYS_BACK} days)")
    prs = fetch_github_prs(token, REPO_OWNER, REPO_NAME, DAYS_BACK)
    
    # Save results
    save_to_csv(prs, OUTPUT_FILE)
    
    if prs:
        print(f"\n🎉 Successfully fetched and saved PR data!")
        print(f"📁 Output file: {OUTPUT_FILE}")
        
        # Show sample data
        print(f"\n📝 Sample PRs:")
        for i, pr in enumerate(prs[:3]):
            print(f"   {i+1}. #{pr['pr_number']}: {pr['title']}")
            print(f"      👤 {pr['author']} | ⏰ {pr['merged_at']}")
    else:
        print(f"\n⚠️  No merged PRs found in the last {DAYS_BACK} days")
        print(f"📁 Empty CSV created: {OUTPUT_FILE}")

if __name__ == "__main__":
    main()