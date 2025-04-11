import pandas as pd
import folium
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter

def build_address(row):
    parts = [str(row.get('house_number', '')), str(row.get('street', ''))]
    boro_map = {'3': 'Brooklyn', '4': 'Queens'}
    boro = boro_map.get(str(row.get('boro')), '')
    if boro:
        parts.append(boro)
    parts.append('New York, NY')
    return ', '.join(part for part in parts if part)

def geocode_addresses(df):
    geolocator = Nominatim(user_agent="dobscrape")
    geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1)
    df['full_address'] = df.apply(build_address, axis=1)
    df['location'] = df['full_address'].apply(geocode)
    df['latitude'] = df['location'].apply(lambda loc: loc.latitude if loc else None)
    df['longitude'] = df['location'].apply(lambda loc: loc.longitude if loc else None)
    return df.drop(columns=['location'])

def create_map(df, output_html="violations_map.html"):
    df = df.dropna(subset=['latitude', 'longitude'])
    start_coords = (40.7128, -74.0060)  # NYC default
    map_ = folium.Map(location=start_coords, zoom_start=11)
    for _, row in df.iterrows():
        popup_text = f"{row['house_number']} {row['street']}<br>{row['violation_type']}"
        folium.Marker(
            location=(row['latitude'], row['longitude']),
            popup=popup_text,
            icon=folium.Icon(color='blue', icon='info-sign')
        ).add_to(map_)
    map_.save(output_html)
    print(f"Map saved to {output_html}")

if __name__ == "__main__":
    print("Loading violations.csv...")
    df = pd.read_csv("violations.csv")
    df = geocode_addresses(df)
    df.to_csv("violations_geocoded.csv", index=False)
    create_map(df)