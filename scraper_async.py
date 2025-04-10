import aiohttp
import asyncio
import pandas as pd

class DOBScraperAsync:
    def __init__(self, batch_size=1000, max_records=50000):
        self.base_url = "https://data.cityofnewyork.us/resource/3h2n-5cm9.json"
        self.batch_size = batch_size
        self.max_records = max_records

    async def fetch_batch(self, session, offset):
        params = {
            "$limit": self.batch_size,
            "$offset": offset,
            "$where": "violation_category LIKE '%ACTIVE%' AND boro IN('BK','QN')"
        }
        async with session.get(self.base_url, params=params) as response:
            return await response.json()

    async def fetch_all(self):
        async with aiohttp.ClientSession() as session:
            tasks = []
            for offset in range(0, self.max_records, self.batch_size):
                tasks.append(self.fetch_batch(session, offset))
            results = await asyncio.gather(*tasks)
            return [record for batch in results for record in batch]

    def run_scraper(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        data = loop.run_until_complete(self.fetch_all())
        loop.close()
        return pd.DataFrame(data)
