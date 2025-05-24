from faker_data import orders, inventories, returns
import pandas as pd
from datetime import datetime
import csv
import os
import contextlib


# clean data
def clean_data(df):
    df = df.copy()
    
    # drop duplicates
    df.drop_duplicates(inplace=True)
    

    for col in df.columns:
        col_lower_name = col.lower()

        # clean up text capitalization
        if 'name' in col_lower_name:
            df[col] = df[col].str.strip().str.title()

        # reformat dates to keep consistent date format
        if 'date' in col_lower_name:
            df[col] = pd.to_datetime(df[col], errors='coerce')
        
        if 'days' in col_lower_name:
            df.loc[df[col] > 30, col] = 30

        if 'units' in col_lower_name:
            df['Bulk Order Flag'] = df[col] >= 15
        
        if 'stock' in col_lower_name:
            df.loc[df[col] < 0, col] = 0


        if df[col].isnull().any():
            df[f"is_missing_{col}"] = df[col].isnull().astype(int)

            # autofill flad missing values as 0
            if 'flag' in col_lower_name:
                df[col] = df[col].fillna(0)
            
            elif 'id' in col_lower_name:
                df[col] = df[col].astype(str)
            
            elif 'price' in col_lower_name:
                df[col] = df[col].astype(float)
            
            elif 'days' in col_lower_name:
                df[col] = df[col].fillna(df[col].mean()).round(0)
            
            elif df[col].dtype in ['float64', 'int64']:
                df[col] = df[col].fillna(df[col].mean()).round(2)

            else:
                df[col] = df[col].fillna('MISSING')

    
    return df

def print_df_info(df):
    print(df.describe())
    print(df.info())

os.makedirs('month_1', exist_ok=True)
os.makedirs('month_2', exist_ok=True)
os.makedirs('month_3', exist_ok=True)

cleaned_orders = []
cleaned_inventories = []
cleaned_returns = []


for i in range(3):
    orders_df = orders[i]
    inventory_df = inventories[i]
    returns_df = returns[i]

    cleaned_orders_df = clean_data(orders_df)
    cleaned_orders_df.to_csv(f'month_{i+1}/month_{i+1}_cleaned_orders.csv')
    with open('df_info_log.txt', 'a') as f:
        with contextlib.redirect_stdout(f):
            print_df_info(cleaned_orders_df)
    cleaned_orders.append(cleaned_orders_df)

    cleaned_inventory_df = clean_data(inventory_df)
    cleaned_inventory_df.to_csv(f'month_{i+1}/month_{i+1}_cleaned_inventory.csv')
    with open('df_info_log.txt', 'a') as f:
        with contextlib.redirect_stdout(f):
            print_df_info(cleaned_inventory_df)
    cleaned_inventories.append(cleaned_inventory_df)

    cleaned_returns_df = clean_data(returns_df)
    cleaned_returns_df.to_csv(f'month_{i+1}/month_{i+1}_cleaned_returns.csv')
    with open('df_info_log.txt', 'a') as f:
        with contextlib.redirect_stdout(f):
            print_df_info(cleaned_returns_df)
    cleaned_returns.append(cleaned_returns_df)


