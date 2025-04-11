import asyncio
import datetime
import aiohttp
import pandas as pd

NYC_OPEN_DATA_API = "https://data.cityofnewyork.us/resource/3h2n-5cm9.json"
MAX_LIMIT = 50000
START_DATE = "20240101"

FINAL_COLUMNS = [
    'boro', 'block', 'lot', 'issue_date',
    'house_number', 'street', 'violation_category', 'violation_type'
]

async def fetch_violations(session, offset=0):
    params = {
        "$where": f"issue_date >= '{START_DATE}' AND boro IN ('3','4') AND violation_category NOT LIKE '%DISMISSED%'",
        "$limit": MAX_LIMIT,
        "$offset": offset
    }
    try:
        async with session.get(NYC_OPEN_DATA_API, params=params) as response:
            if response.status == 200:
                return await response.json()
            else:
                print(f"API returned status {response.status}")
                return []
    except Exception as e:
        print(f"Error during API call: {e}")
        return []

async def fetch_all_violations():
    all_violations = []
    offset = 0
    async with aiohttp.ClientSession() as session:
        while True:
            print(f"Fetching batch at offset {offset}...")
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
    df = df[[col for col in FINAL_COLUMNS if col in df.columns]]
    if 'issue_date' in df.columns:
        df['issue_date'] = pd.to_datetime(df['issue_date'], format="%Y%m%d", errors='coerce')
        df = df.sort_values(by='issue_date', ascending=False)
        df['issue_date'] = df['issue_date'].dt.strftime('%Y-%m-%d')
    df['date_collected'] = datetime.datetime.now().strftime('%Y-%m-%d')
    return df

def scrape_violations():
    violations = asyncio.run(fetch_all_violations())
    return clean_violations_data(violations)

if __name__ == "__main__":
    print("Fetching violations from NYC Open Data...")
    df = scrape_violations()
    print(f"Fetched {len(df)} records")

    if not df.empty:
        print("Saving to violations.csv...")
        df.to_csv("violations.csv", index=False)
        print("Done.")
    else:
        print("⚠️ No records found. This may indicate an API or filter issue.")

    print("=== Sample Output ===")
    print(df.head(5))