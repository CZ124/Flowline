from pyomo.environ import *
from data_cleaning import cleaned_orders, cleaned_inventories, cleaned_returns

HOLDING_COST_PER_UNIT = 0.05
LABOUR_COST_PER_HOUR = 20
DELAY_COST_PER_HOUR = 5 # additional cost per hour delayed
RETURN_PROCESSING_COST_PER_ORDER = 3
REORDER_COST = 15

def calculate_product_demand(orders_last_month_df, month_num):
    demands_df = orders_last_month_df[orders_last_month_df['Bulk Order Flag'] != 1].groupby('Product Ordered')['Units Ordered'].sum().reset_index(name='Demand')
    demands_df.to_csv(f'month_{month_num}/month_{month_num}_demands.csv')
    return demands_df

demands_month_1 = calculate_product_demand(cleaned_orders[2], 1) # in reality we would use the month before but for this simulation we are just using the month 3 data
demands_month_2 = calculate_product_demand(cleaned_orders[0], 2)
demands_month_3 = calculate_product_demand(cleaned_orders[1], 3)

def EOQ_calc(demands_df, sku, order_cost, holding_cost):
    demand = demands_df.loc[demands_df['Product Ordered'] == sku, 'Demand'].iloc[0]
    EOQ = sqrt((2 * demand * 12 * order_cost) / (holding_cost * 12))
    return EOQ

sku = str(demands_month_2['Product Ordered'][0])
print(EOQ_calc(demands_month_2, sku, REORDER_COST, HOLDING_COST_PER_UNIT))




    