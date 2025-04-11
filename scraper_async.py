import asyncio
import datetime
import aiohttp
import pandas as pd

NYC_OPEN_DATA_API = "https://data.cityofnewyork.us/resource/3h2n-5cm9.json"
MAX_LIMIT = 50000

FINAL_COLUMNS = [
    'boro', 'block', 'lot', 'issue_date',
    'house_number', 'street', 'violation_category', 'violation_type'
]

def get_lead_type(issue_date):
    today = pd.Timestamp.today().normalize()
    delta = today - issue_date
    if delta.days > 180:
        return "Old"
    elif delta.days > 30:
        return "Warm"
    else:
        return "New"

async def fetch_violations(session, offset=0, start_date="2020-01-01"):
    params = {
        "$where": f"issue_date >= '{start_date}' AND boro IN ('3','4') AND lower(violation_type) LIKE '%unsafe%'",
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

async def fetch_all_violations(start_date="2020-01-01"):
    all_violations = []
    offset = 0
    async with aiohttp.ClientSession() as session:
        while True:
            print(f"Fetching batch at offset {offset}...")
            batch = await fetch_violations(session, offset, start_date=start_date)
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
    if "issue_date" in df.columns:
        df["issue_date"] = pd.to_datetime(df["issue_date"], format="%Y%m%d", errors="coerce")
        df["Lead Type"] = df["issue_date"].apply(get_lead_type)
        df.sort_values(by="issue_date", ascending=False, inplace=True)
        df["issue_date"] = df["issue_date"].dt.strftime("%Y-%m-%d")
    df["date_collected"] = datetime.datetime.now().strftime("%Y-%m-%d")
    return df

def scrape_violations(start_date="2020-01-01"):
    violations = asyncio.run(fetch_all_violations(start_date=start_date))
    return clean_violations_data(violations)

if __name__ == "__main__":
    print("Fetching violations from NYC Open Data...")
    df = scrape_violations()
    print(f"Fetched {len(df)} records")
    if not df.empty:
        df.to_excel("violations_dashboard.xlsx", index=False)
        print("Saved to violations_dashboard.xlsx")
    else:
        print("⚠️ No records found.")
    print("=== Sample Output ===")
    print(df.head(5))