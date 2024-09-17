import pandas as pd

def aggregate_data(transactions_df, aggregated_orders_df):
    # Combine and clean data
    df = pd.concat([transactions_df, aggregated_orders_df], ignore_index=True)
    df.dropna(inplace=True)
    df['created_at'] = pd.to_datetime(df['created_at'])
    return df
