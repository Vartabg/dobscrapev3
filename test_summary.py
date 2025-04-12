import pandas as pd
from violations_utils import generate_summary_statistics

df = pd.read_excel("violations.xlsx")

# Rename columns to expected ones
df = df.rename(columns={
    'boro': 'borough'
})

# Calculate age_in_days from issue_date
df['issue_date'] = pd.to_datetime(df['issue_date'], errors='coerce')
df['age_in_days'] = (pd.Timestamp.today() - df['issue_date']).dt.days

# Now run the summary
summary = generate_summary_statistics(df)
print(summary)
