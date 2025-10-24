#!/usr/bin/env python3
"""
Zendesk Issues Processing Script
Processes zendesk_issues.csv according to requirements:
- Convert 'Date' to datetime format  
- Normalize 'Type of ticket' (equivalent to Severity)
- Add column 'is_customer_issue' based on available criteria
- Save to 'cleaned_zendesk_issues.csv'
"""

import pandas as pd
import os
from datetime import datetime

def process_zendesk_data():
    """
    Process the Zendesk issues CSV file according to requirements
    """
    # File paths
    input_file = 'zendesk_issues.csv'
    output_file = 'cleaned_zendesk_issues.csv'
    
    print(f"Reading {input_file}...")
    
    try:
        # Read the header line manually (line 6, 0-indexed = 5)
        with open(input_file, 'r') as f:
            lines = f.readlines()
            header_line = lines[5].strip()
        
        # Define the correct column names based on manual inspection
        column_names = [
            'Date', 'Time', 'Zendesk Ticket', 'Assignee', 
            'Initial analysis Resolution Comments', 'Caused due to this release ?',
            'Type of ticket', 'UI / BE Side', 'Jira Id', 'Feature/Component',
            'Is this Regression /Escape Bug', 'Is Test case available?',
            'If test case availble, reason for Miss?', 'Is Test Cases Added Now - Zephyr ID',
            'Automation status'
        ]
        
        # Read the CSV file starting from row 7 (0-indexed = 6) with custom column names
        df = pd.read_csv(input_file, skiprows=6, names=column_names, low_memory=False)
        print(f"Original data shape: {df.shape}")
        print(f"Original columns: {list(df.columns)}")
        print("\nFirst few rows:")
        print(df.head())
        
        # Clean column names (remove extra spaces)
        df.columns = df.columns.str.strip()
        print(f"\nCleaned columns: {list(df.columns)}")
        
        # Remove empty rows
        original_count = len(df)
        df = df.dropna(how='all')
        print(f"Removed {original_count - len(df)} completely empty rows")
        print(f"Data shape after cleaning: {df.shape}")
        
        # Convert 'Date' to datetime format
        if 'Date' in df.columns:
            print(f"\nConverting 'Date' column to datetime...")
            # Handle various date formats
            df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
            valid_dates = df['Date'].notna().sum()
            print(f"Successfully converted {valid_dates} dates")
            print(f"Date range: {df['Date'].min()} to {df['Date'].max()}")
        else:
            print("\nWarning: 'Date' column not found in the data")
            print(f"Available columns: {list(df.columns)}")
        
        # Normalize 'Type of ticket' (equivalent to Severity)
        ticket_type_col = None
        for col in ['Type of ticket', 'Type']:
            if col in df.columns:
                ticket_type_col = col
                break
        
        if ticket_type_col:
            print(f"\nNormalizing '{ticket_type_col}' column to uppercase...")
            df[ticket_type_col] = df[ticket_type_col].astype(str).str.upper().str.strip()
            print(f"Ticket type values: {df[ticket_type_col].unique()}")
        else:
            print(f"\nWarning: 'Type of ticket' column not found")
            print(f"Available columns: {list(df.columns)}")
        
        # Add column 'is_customer_issue' based on available criteria
        print(f"\nAnalyzing data to determine customer issues...")
        
        # Strategy: Look for external/customer indicators in available columns
        df['is_customer_issue'] = False
        
        # Check Assignee column for external indicators
        if 'Assignee' in df.columns:
            print(f"Analyzing 'Assignee' column...")
            assignee_values = df['Assignee'].dropna().unique()
            print(f"Unique assignees (first 10): {assignee_values[:10]}")
            
            # Assume external assignees might indicate customer issues
            # This logic can be adjusted based on your business rules
            external_keywords = ['customer', 'external', 'client', 'support']
            df['is_customer_issue'] = df['Assignee'].str.lower().str.contains(
                '|'.join(external_keywords), na=False
            )
            customer_count = df['is_customer_issue'].sum()
            print(f"Found {customer_count} potential customer issues based on assignee")
        
        # Additional logic: Check if ticket URL or comments indicate customer issues
        if 'Initial analysis Resolution Comments' in df.columns:
            print(f"Analyzing comments for customer indicators...")
            customer_keywords = ['customer', 'client', 'user reported', 'external']
            customer_in_comments = df['Initial analysis Resolution Comments'].str.lower().str.contains(
                '|'.join(customer_keywords), na=False
            )
            # Combine with existing logic (OR operation)
            df['is_customer_issue'] = df['is_customer_issue'] | customer_in_comments
            total_customer_issues = df['is_customer_issue'].sum()
            print(f"Total customer issues identified: {total_customer_issues}")
        
        # Save to cleaned CSV
        print(f"\nSaving cleaned data to {output_file}...")
        df.to_csv(output_file, index=False)
        print(f"Successfully saved {len(df)} rows to {output_file}")
        
        # Summary
        print(f"\n=== PROCESSING SUMMARY ===")
        print(f"Input file: {input_file}")
        print(f"Output file: {output_file}")
        print(f"Final data shape: {df.shape}")
        print(f"Final columns: {list(df.columns)}")
        
        # Data quality check
        print(f"\n=== DATA QUALITY CHECK ===")
        print(f"Missing values per column:")
        missing_summary = df.isnull().sum()
        for col, missing_count in missing_summary.items():
            if missing_count > 0:
                print(f"  {col}: {missing_count}")
        
        # Customer issues summary
        if 'is_customer_issue' in df.columns:
            customer_count = df['is_customer_issue'].sum()
            total_count = len(df)
            percentage = (customer_count / total_count * 100) if total_count > 0 else 0
            print(f"\n=== CUSTOMER ISSUES ANALYSIS ===")
            print(f"Total issues: {total_count}")
            print(f"Customer issues: {customer_count}")
            print(f"Customer issue rate: {percentage:.1f}%")
        
        return df
        
    except FileNotFoundError:
        print(f"Error: Could not find {input_file}")
        print("Please make sure the file exists in the current directory")
        return None
    except Exception as e:
        print(f"Error processing data: {str(e)}")
        return None

if __name__ == "__main__":
    # Change to the script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    print("Zendesk Issues Processing Script")
    print("=" * 50)
    
    # Process the data
    cleaned_data = process_zendesk_data()
    
    if cleaned_data is not None:
        print("\n✅ Processing completed successfully!")
    else:
        print("\n❌ Processing failed!")