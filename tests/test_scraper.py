import aiohttp
import asyncio
import json

NYC_OPEN_DATA_API = "https://data.cityofnewyork.us/resource/3h2n-5cm9.json"

async def test_api_connection():
    """Test if we can connect to the NYC Open Data API"""
    params = {
        "$limit": 5,
        "$where": "issue_date >= '2020-01-01' AND boro IN ('3','4')"
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            print("Connecting to NYC Open Data API...")
            async with session.get(NYC_OPEN_DATA_API, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ Successfully connected to API")
                    print(f"✅ Received {len(data)} records")
                    
                    # Print first record for inspection
                    if data and len(data) > 0:
                        print("\nSample record:")
                        print(json.dumps(data[0], indent=2))
                    return True
                else:
                    print(f"❌ API returned status {response.status}")
                    print(f"Response: {await response.text()}")
                    return False
    except Exception as e:
        print(f"❌ Error connecting to API: {str(e)}")
        return False

if __name__ == "__main__":
    print("\n=== NYC DOB API Connection Test ===\n")
    loop = asyncio.get_event_loop()
    result = loop.run_until_complete(test_api_connection())
    
    if result:
        print("\n✅ API Test Successful! Your scraper should be able to fetch data.")
    else:
        print("\n❌ API Test Failed. Please check your internet connection and API access.")
    
    print("\n=== Test Complete ===")
