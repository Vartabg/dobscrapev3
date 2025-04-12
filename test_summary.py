import pandas as pd
from violations_utils import generate_summary_statistics

df = pd.read_excel("violations.xlsx")
summary = generate_summary_statistics(df)

print(summary)
