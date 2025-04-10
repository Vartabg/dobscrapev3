def filter_data(df):
    keywords = [
        "vacate", "unsafe", "collapse", "squatter", "abandoned",
        "hazard", "danger", "violation", "illegal occupancy", "order to vacate"
    ]
    search_fields = ['description', 'violation_type', 'disposition_comments']
    search_fields = [col for col in search_fields if col in df.columns]

    df['matched_field'] = ''
    mask = False

    for field in search_fields:
        field_mask = df[field].fillna('').astype(str).str.contains('|'.join(keywords), case=False)
        df.loc[field_mask, 'matched_field'] += field + ', '
        mask |= field_mask

    df['matched_field'] = df['matched_field'].str.rstrip(', ')
    return df[mask].copy()
