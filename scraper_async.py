import asyncio
import datetime
import aiohttp
import pandas as pd

NYC_OPEN_DATA_API = "https://data.cityofnewyork.us/resource/3h2n-5cm9.json"
MAX_LIMIT = 50000
START_DATE = "20240101"  # Must match the format used by the API (YYYYMMDD)

async def fetch_violations(session, offset=0):
    params = {
        "$where": f"violation_category NOT LIKE '%DISMISSED%' AND issue_date >= '{START_DATE}' AND (boro = 'BROOKLYN' OR boro = 'QUEENS')",
        "$limit": MAX_LIMIT,
        "$offset": offset
    }
    try:
        async with session.get(NYC_OPEN_DATA_API, params=params) as response:
            if response.status == 200:
                return await response.json()
            else:
                return []
    except Exception:
        return []

async def fetch_all_violations():
    all_violations = []
    offset = 0
    async with aiohttp.ClientSession() as session:
        while True:
            batch = await fetch_violations(session, offset)
            if not batch:
                break
            all_violations.extend(batch)
            if len(batch) < MAX_LIMIT:
                break
            offset += MAX_LIMIT
    return all_violations

def clean_violations_data(violations):
    if not violations:
        return pd.DataFrame()
    df = pd.DataFrame(violations)
    expected_columns = [
        'boro', 'block', 'lot', 'issue_date', 'violation_type_code',
        'violation_number', 'house_number', 'street', 'disposition_date',
        'disposition_comments', 'status', 'severity'
    ]
    existing_columns = [col for col in expected_columns if col in df.columns]
    if existing_columns:
        df = df[existing_columns]
    if 'issue_date' in df.columns:
        df['issue_date'] = pd.to_datetime(df['issue_date'], format="%Y%m%d", errors='coerce').dt.strftime('%Y-%m-%d')
    if 'disposition_date' in df.columns:
        df['disposition_date'] = pd.to_datetime(df['disposition_date'], errors='coerce').dt.strftime('%Y-%m-%d')
    df['date_collected'] = datetime.datetime.now().strftime('%Y-%m-%d')
    return df

def scrape_violations():
    violations = asyncio.run(fetch_all_violations())
    return clean_violations_data(violations)

if __name__ == "__main__":
    df = scrape_violations()
    if not df.empty:
        print(f"Fetched {len(df)} records")
        df.to_csv("violations.csv", index=False)
    else:
        print("No records found")