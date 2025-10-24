#!/usr/bin/env python3
"""
Bug Data Processing Script
Processes bug_data.csv according to specified requirements:
- Remove duplicates
- Convert 'Date' to datetime
- Normalize 'Severity' to uppercase
- Add column 'is_escaped_defect' where user_type == 'external'
- Save to 'cleaned_bug_data.csv'
"""

import pandas as pd
import os
from datetime import datetime

def process_bug_data():
    """
    Process the bug data CSV file according to requirements
    """
    # File paths
    input_file = 'bug_data.csv'
    output_file = 'cleaned_bug_data.csv'
    
    print(f"Reading {input_file}...")
    
    try:
        # Read the CSV file
        df = pd.read_csv(input_file)
        print(f"Original data shape: {df.shape}")
        print(f"Original columns: {list(df.columns)}")
        print("\nFirst few rows:")
        print(df.head())
        
        # Remove duplicates
        print(f"\nRemoving duplicates...")
        original_count = len(df)
        df = df.drop_duplicates()
        print(f"Removed {original_count - len(df)} duplicate rows")
        print(f"Data shape after removing duplicates: {df.shape}")
        
        # Convert 'Date' to datetime
        if 'Date' in df.columns:
            print(f"\nConverting 'Date' column to datetime...")
            df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
            print(f"Date column converted. Sample dates: {df['Date'].head()}")
        else:
            print("\nWarning: 'Date' column not found in the data")
            print(f"Available columns: {list(df.columns)}")
        
        # Normalize 'Priority' to uppercase (equivalent to Severity)
        if 'Priority' in df.columns:
            print(f"\nNormalizing 'Priority' column to uppercase...")
            df['Priority'] = df['Priority'].astype(str).str.upper()
            print(f"Priority values: {df['Priority'].unique()}")
        elif 'Severity' in df.columns:
            print(f"\nNormalizing 'Severity' column to uppercase...")
            df['Severity'] = df['Severity'].astype(str).str.upper()
            print(f"Severity values: {df['Severity'].unique()}")
        else:
            print("\nWarning: Neither 'Priority' nor 'Severity' column found in the data")
            print(f"Available columns: {list(df.columns)}")
        
        # Add column 'is_escaped_defect' based on external reporters
        # First let's examine the Reporter and Channel columns to identify external users
        if 'Reporter' in df.columns:
            print(f"\nAnalyzing 'Reporter' column to identify external users...")
            reporter_values = df['Reporter'].unique()
            print(f"Unique reporters (first 10): {reporter_values[:10]}")
            
        if 'Channel' in df.columns:
            print(f"\nAnalyzing 'Channel' column to identify external channels...")
            channel_values = df['Channel'].unique()
            print(f"Channel values: {channel_values}")
            
            # Assume external defects come from customer-facing channels like 'customer', 'support', 'external'
            # You may need to adjust this logic based on your specific data
            external_channels = ['customer', 'support', 'external', 'client']
            df['is_escaped_defect'] = df['Channel'].str.lower().isin(external_channels)
            escaped_count = df['is_escaped_defect'].sum()
            print(f"Found {escaped_count} escaped defects based on external channels")
        elif 'user_type' in df.columns:
            print(f"\nAdding 'is_escaped_defect' column based on user_type...")
            df['is_escaped_defect'] = df['user_type'] == 'external'
            escaped_count = df['is_escaped_defect'].sum()
            print(f"Found {escaped_count} escaped defects (external user types)")
        else:
            print("\nWarning: Cannot determine external users from available columns")
            print(f"Available columns: {list(df.columns)}")
            # Default to False for all rows
            df['is_escaped_defect'] = False
            print("Setting all 'is_escaped_defect' values to False")
        
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
        print(df.isnull().sum())
        
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
    
    print("Bug Data Processing Script")
    print("=" * 50)
    
    # Process the data
    cleaned_data = process_bug_data()
    
    if cleaned_data is not None:
        print("\n✅ Processing completed successfully!")
    else:
        print("\n❌ Processing failed!")