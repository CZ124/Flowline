from faker_data import orders_df, inventory_df, returns_df
import pandas as pd

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
            df['Bulk Order Flag'] = df[col] >= 30
        
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


cleaned_orders_df = clean_data(orders_df)
cleaned_orders_df.to_csv('cleaned_orders.csv')
print_df_info(cleaned_orders_df)

cleaned_inventory_df = clean_data(inventory_df)
cleaned_inventory_df.to_csv('cleaned_inventory.csv')
print_df_info(cleaned_inventory_df)

cleaned_returns_df = clean_data(returns_df)
cleaned_returns_df.to_csv('cleaned_returns.csv')
print_df_info(cleaned_returns_df)


