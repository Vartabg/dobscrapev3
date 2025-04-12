import pandas as pd

def generate_summary_statistics(df: pd.DataFrame) -> dict:
    """
    Return counts of violations by borough, type, and age tier.

    Parameters:
        df (pd.DataFrame): DataFrame containing violation data.
            Required columns: 'borough', 'violation_type', 'age_in_days'

    Returns:
        dict: Summary statistics as a dictionary containing:
            - 'violations_by_borough': Counts of violations grouped by borough
            - 'violations_by_type': Counts of violations grouped by type
            - 'violations_by_age_tier': Counts of violations grouped by age tiers
    """
    if not {'borough', 'violation_type', 'age_in_days'}.issubset(df.columns):
        raise ValueError("DataFrame must contain 'borough', 'violation_type', and 'age_in_days' columns.")

    # Violations grouped by borough
    violations_by_borough = df['borough'].value_counts().to_dict()

    # Violations grouped by type
    violations_by_type = df['violation_type'].value_counts().to_dict()

    # Define age tiers
    bins = [0, 30, 90, 180, 365, float('inf')]
    labels = ['0-30 days', '31-90 days', '91-180 days', '181-365 days', 'Over a year']
    df['age_tier'] = pd.cut(df['age_in_days'], bins=bins, labels=labels, right=False)

    # Violations grouped by age tier
    violations_by_age_tier = df['age_tier'].value_counts().sort_index().to_dict()

    # Compile results into a dictionary
    summary_statistics = {
        'violations_by_borough': violations_by_borough,
        'violations_by_type': violations_by_type,
        'violations_by_age_tier': violations_by_age_tier
    }

    return summary_statistics