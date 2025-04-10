#!/usr/bin/env python3
"""
Dobscrape v4 - DOB Violations Scraper
Asynchronous scraper module for fetching DOB violations
"""

import asyncio
import datetime
import aiohttp
import pandas as pd
from urllib.parse import quote

# Constants for the scraper
NYC_OPEN_DATA_API = "https://data.cityofnewyork.us/resource/3h2n-5cm9.json"
MAX_LIMIT = 50000  # Maximum records per request
START_DATE = "2024-01-01T00:00:00.000"
TARGET_BOROUGHS = ["BROOKLYN", "QUEENS"]

async def fetch_violations(session, offset=0):
    """
    Fetch a batch of violations from the NYC Open Data API
    
    Args:
        session: aiohttp client session
        offset: Starting offset for pagination
        
    Returns:
        List of violation records
    """
    # Build the query with proper filters based on the actual CSV structure
    params = {
        "$where": f"issue_date >= '{START_DATE}' AND (boro = 'BROOKLYN' OR boro = 'QUEENS')",
        "$limit": MAX_LIMIT,
        "$offset": offset,
        "status": "ACTIVE"  # We only want active violations
    }
    
    try:
        async with session.get(NYC_OPEN_DATA_API, params=params) as response:
            if response.status == 200:
                return await response.json()
            else:
                error_text = await response.text()
                print(f"API Error ({response.status}): {error_text}")
                return []
    except Exception as e:
        print(f"Network error: {e}")
        return []

async def fetch_all_violations():
    """
    Fetch all violations with pagination
    
    Returns:
        List of all violation records
    """
    all_violations = []
    offset = 0
    
    async with aiohttp.ClientSession() as session:
        while True:
            batch = await fetch_violations(session, offset)
            
            if not batch:
                break
                
            all_violations.extend(batch)
            
            # If we got fewer records than the limit, we've reached the end
            if len(batch) < MAX_LIMIT:
                break
                
            offset += MAX_LIMIT
            
    return all_violations

def clean_violations_data(violations):
    """
    Clean and format violations data
    
    Args:
        violations: List of violation records
        
    Returns:
        Cleaned pandas DataFrame
    """
    if not violations:
        return pd.DataFrame()
        
    # Convert to DataFrame
    df = pd.DataFrame(violations)
    
    # Define exact columns to match the CSV structure
    expected_columns = [
        'boro', 'block', 'lot', 'issue_date', 'violation_type_code',
        'violation_number', 'house_number', 'street', 'disposition_date',
        'disposition_comments', 'status', 'severity'
    ]
    
    # Only keep columns that exist in the data
    existing_columns = [col for col in expected_columns if col in df.columns]
    
    # If we have no matching columns, keep all columns
    if not existing_columns:
        print("Warning: None of the expected columns found in data, keeping all columns")
    else:
        df = df[existing_columns]
    
    # Convert issue_date to datetime if it exists
    if 'issue_date' in df.columns:
        try:
            df['issue_date'] = pd.to_datetime(df['issue_date']).dt.strftime('%Y-%m-%d')
        except Exception as e:
            print(f"Warning: Could not convert issue_date: {e}")
    
    # Convert other date fields if they exist
    if 'disposition_date' in df.columns:
        try:
            df['disposition_date'] = pd.to_datetime(df['disposition_date'], errors='coerce').dt.strftime('%Y-%m-%d')
        except Exception as e:
            print(f"Warning: Could not convert disposition_date: {e}")
    
    # Add a date_collected column with today's date
    df['date_collected'] = datetime.datetime.now().strftime('%Y-%m-%d')
    
    return df

def scrape_violations():
    """
    Main function to scrape and process violations
    
    Returns:
        DataFrame of processed violations
    """
    # Run the async fetch function in the event loop
    violations = asyncio.run(fetch_all_violations())
    
    # Clean and format the data
    violations_df = clean_violations_data(violations)
    
    return violations_df

if __name__ == "__main__":
    # For testing the module directly
    result = scrape_violations()
    if not result.empty:
        print(f"Found {len(result)} violations")
        result.to_csv("violations.csv", index=False)
    else:
        print("No violations found")
