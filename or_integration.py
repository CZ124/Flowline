from pyomo.environ import *
from data_cleaning import cleaned_orders, cleaned_inventories, cleaned_returns
from faker_data import products, num_products
import pandas as pd
import math


HOLDING_COST_PER_UNIT = 0.05
LABOUR_COST_PER_HOUR = 20
DELAY_COST_PER_DAY = 5 # additional cost per hour delayed
RETURN_PROCESSING_COST_PER_ORDER = 3
REORDER_COST = 15

sku_list = [products[_].sku_id for _ in range(num_products)]

def calculate_product_demand(orders_last_month_df, month_num):
    demands_df = orders_last_month_df[orders_last_month_df['Bulk Order Flag'] != 1].groupby('Product Ordered')['Units Ordered'].sum().reset_index(name='Demand')
    demands_df.to_csv(f'month_{month_num}/month_{month_num}_demands.csv')
    return demands_df

demands_month_1 = calculate_product_demand(cleaned_orders[2], 1) # in reality we would use the month before but for this simulation we are just using the month 3 data
demands_month_2 = calculate_product_demand(cleaned_orders[0], 2)
demands_month_3 = calculate_product_demand(cleaned_orders[1], 3)

demands = [demands_month_1, demands_month_2,demands_month_3]

def EOQ_calc(demands_df, sku, order_cost, holding_cost):
    demand = demands_df.loc[demands_df['Product Ordered'] == sku, 'Demand']
    if demand.empty:
        return 0
    demand = demand.sum()
    EOQ = sqrt((2 * demand * 12 * order_cost) / (holding_cost * 12))
    return EOQ

def inventory_flow(sku_list, EOQ, inventory_df, returns_df, demand_df):
    inventory_df_indexed = inventory_df.set_index("Product SKU ID")
    returns_df_indexed = returns_df.set_index("Returned Item")
    demand_df_indexed = demand_df.set_index("Product Ordered")

    returns_agg = returns_df_indexed.groupby("Returned Item")["Units Returned"].sum()
    demand_agg = demand_df_indexed.groupby("Product Ordered")["Demand"].sum()


    summary = []

    for sku in sku_list:
        start_stock = inventory_df_indexed["Product Stock"].get(sku, 0)
        reorder_point = inventory_df_indexed["Product Reorder Point"].get(sku, 0)
        returns = returns_agg.get(sku, 0)
        demand = demand_agg.get(sku, 0)

        available_stock = start_stock + returns
        shortage = max(0, demand - available_stock)
        end_stock = max(0, available_stock - demand)

        reordered = end_stock <= reorder_point
        units_ordered = EOQ(demand_df, sku, REORDER_COST, HOLDING_COST_PER_UNIT) if reordered else 0

        summary.append({
            "SKU": sku,
            "Start Stock": start_stock,
            "Demand": demand,
            "Returns": returns,
            "End Stock": end_stock,
            "Shortage?": shortage > 0,
            "Shortage Units": shortage,
            "Reordered?": reordered,
            "EOQ Ordered": math.ceil(units_ordered)
        })

    return pd.DataFrame(summary)

month_2_summary = inventory_flow(sku_list, EOQ_calc, cleaned_inventories[1], cleaned_returns[1], demands_month_2)
print(month_2_summary)

def calc_order_delay_costs(orders_df, inventory_df):
    order_cost = 0
    for _, row in orders_df.iterrows():
        ordered_item = row['Product Ordered']
        num_item_ordered = row['Units Ordered']
        delay_days = row['Delivery Delay Days']

        matched_product = inventory_df[inventory_df['Product SKU ID'] == ordered_item]

        if not matched_product.empty:
            item_unit_price = matched_product['Product Price'].values[0]
        else:
            item_unit_price = 0

        order_cost += num_item_ordered * item_unit_price
        order_cost -= delay_days * DELAY_COST_PER_DAY

    return order_cost

            



def simulate_fixed_quantity(inventory_df, orders_df, demand_df):
    stock = inventory_df.copy()
    total_cost, orders_placed, stockouts = 0,0,0

    for i, row in stock.iterrows():
        current_inv = row['Product Stock']
        reorder_point = row['Product Reorder Point']

        sku = row['Product SKU ID']
        matched_demand_row = demand_df[demand_df['Product Ordered'] == sku]
        if not matched_demand_row.empty:
            demand = matched_demand_row['Demand'].values[0]
        else:
            demand = 0        


        if current_inv < demand:
            stockouts +=1

        if current_inv < reorder_point:
            reorder_qty = 50
            orders_placed += 1
            current_inv += reorder_qty
            total_cost += REORDER_COST
        
        current_inv -= demand
        total_cost += current_inv * HOLDING_COST_PER_UNIT
    
    total_cost -= calc_order_delay_costs(orders_df, inventory_df)
    return total_cost, stockouts, orders_placed

    
def simulate_eoq(inventory_df, orders_df, demand_df, eoq_function):
    stock = inventory_df.copy()
    total_cost, orders_placed, stockouts = 0,0,0

    for i, row in stock.iterrows():
        current_inv = row['Product Stock']
        reorder_point = row['Product Reorder Point']

        sku = row['Product SKU ID']
        matched_demand_row = demand_df[demand_df['Product Ordered'] == sku]
        if not matched_demand_row.empty:
            demand = matched_demand_row['Demand'].values[0]
        else:
            demand = 0   

        if current_inv < demand:
            stockouts +=1

        if current_inv < reorder_point:
            reorder_qty = eoq_function(demand_df, row['Product SKU ID'], REORDER_COST, HOLDING_COST_PER_UNIT)
            orders_placed += 1
            current_inv += reorder_qty
            total_cost += REORDER_COST
        
        current_inv -= demand
        total_cost += current_inv * HOLDING_COST_PER_UNIT
    
    total_cost -= calc_order_delay_costs(orders_df, inventory_df)
    return total_cost, stockouts, orders_placed

def simulate_min_max(inventory_df, orders_df, demand_df, min_level=1, max_level=20):
    stock = inventory_df.copy()
    total_cost, orders_placed, stockouts = 0,0,0

    for i, row in stock.iterrows():
        current_inv = row['Product Stock']
        reorder_point = row['Product Reorder Point']
        
        sku = row['Product SKU ID']
        matched_demand_row = demand_df[demand_df['Product Ordered'] == sku]
        if not matched_demand_row.empty:
            demand = matched_demand_row['Demand'].values[0]
        else:
            demand = 0   

        if current_inv < demand:
            stockouts +=1

        if current_inv < reorder_point:
            reorder_qty = max_level - current_inv
            orders_placed += 1
            current_inv += max_level
            total_cost += REORDER_COST
        
        current_inv -= demand
        total_cost += current_inv * HOLDING_COST_PER_UNIT
    
    total_cost -= calc_order_delay_costs(orders_df, inventory_df)
    return total_cost, stockouts, orders_placed

results = []

for month in range(3):
    #cleaned_orders, cleaned_inventories, cleaned_returns
    orders_df = cleaned_orders[month]
    inventory_df = cleaned_inventories[month]
    demand_df = demands[month]


    # Fixed quantity
    cost1, stockouts1, reorders1 = simulate_fixed_quantity(inventory_df, orders_df, demand_df)
    results.append(['Fixed-50', cost1, stockouts1, reorders1])

    # EOQ
    cost2, stockouts2, reorders2 = simulate_eoq(inventory_df, orders_df, demand_df, EOQ_calc)
    results.append(['EOQ', cost2, stockouts2, reorders2])

    # Min/Max
    cost3, stockouts3, reorders3 = simulate_min_max(inventory_df, orders_df, demand_df)
    results.append(['Min/Max', cost3, stockouts3, reorders3])

    # Display result table
    df_results = pd.DataFrame(results, columns=['Policy', 'Total Cost', 'Stockouts', 'Orders Placed'])
    print(df_results)












    