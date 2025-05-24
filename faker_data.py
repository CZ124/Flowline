from faker import Faker
import numpy as np
import pandas as pd
import random
from datetime import datetime
from datetime import timedelta
from dateutil.relativedelta import relativedelta
import os




faker = Faker()
np.random.seed(50)

n = 200

# products
class Product:
    def __init__(self, name, size, sku_id, price, category, image_url, rating, stock, reorder_point):
        self.name = name
        self.size = size
        self.sku_id = sku_id
        self.price = price
        self.category = category
        self.image_url = image_url
        self.rating = rating
        self.stock = stock
        self.reorder_point = reorder_point

        
def generate_fake_product(_):
    clothing_categories = {
        "Tops": ["T-Shirt", "Blouse", "Sweater", "Hoodie", "Tank Top"],
        "Bottoms": ["Jeans", "Shorts", "Skirt", "Leggings", "Trousers"],
        "Outerwear": ["Jacket", "Coat", "Blazer", "Trench Coat"],
        "Dresses/One-Pieces": ["Casual Dress", "Maxi Dress", "Wrap Dress", "Jumpsuit", "Romper"],
        "Footwear": ["Sneakers", "Boots", "Flats", "Sandals"],
        "Accessories": ["Belt", "Hat", "Scarf", "Socks"]
    }
    category_sku_codes = {
        'Tops':'TOP-',
        'Bottoms':'BTM-',
        'Outerwear':'OUT-',
        'Dresses/One-Pieces':'ONP-',
        'Footwear':'FOT-',
        'Accessories':'ACC-'
    }

    sizes = ['S','M','L']

    category = random.choice(list(clothing_categories.keys()))
    product_type = random.choice(clothing_categories[category])

    brand = faker.company()

    products = []

    price = round(random.uniform(30.0, 500.0), 2)
    image_url = faker.image_url()
    

    for size in sizes:
        name = brand+" "+product_type+" "+size
        rating = round(random.uniform(1.0, 5.0), 1)
        stock = random.randint(0,10)
        reorder_point = random.randint(2,6)
        
        sku_id = 'SKU-'+category_sku_codes[category]+str(_).zfill(3)+'-'+size

        products.append(Product(name, size, sku_id, price, category, image_url, rating, stock, reorder_point))

    return products

def generate_random_date_in_month(start_date):
    end_date = (start_date + relativedelta(months=1)) - timedelta(days=1)
    return faker.date_between(start_date=start_date, end_date=end_date)
 
month_1_start = datetime.now().replace(day=1)
month_2_start = (month_1_start+timedelta(days=32)).replace(day=1)
month_3_start = (month_2_start+timedelta(days=32)).replace(day=1)


# Generate a list of fake products
num_products = 50

def create_products(num_products):
    products = []
    for _ in range(num_products):
        products += generate_fake_product(_+1)
    
    return products



# orders
def create_orders(products, start_date):
    delay_range = list(range(-9,10))
    delay_weights = [
        1, 2, 4, 6, 10, 14, 20, 26, 30,  # -9 to -1
        35,                             # 0 (on time)
        30, 26, 20, 14, 10, 6, 4, 2, 1   # +1 to +9
    ]

    names = [faker.name() for _ in range(n)]
    emails = [faker.email() for _ in range(n)]
    address = [faker.address() for _ in range(n)]
    postcode = [faker.postcode() for _ in range(n)]
    product_ordered = [products[random.randint(0,49)].sku_id for _ in range(n)]
    order_id = [faker.bothify(text='ORD-###') for _ in range(n)]
    order_date = [generate_random_date_in_month(start_date) for _ in range(n)]
    units_ordered = [random.randint(1,5) for _ in range(n)]
    fulfillment_days = [random.randint(1,25) for _ in range(n)]
    return_stuatus = [random.randint(0,1) for _ in range(n)]
    delivery_delays = [random.choices(delay_range, weights=delay_weights, k=1)[0] for _ in range(n)]

    

    orders_df = pd.DataFrame({
        'Name':names,
        'Email':emails,
        'Address':address,
        'Postal Code':postcode,
        'Product Ordered': product_ordered,
        'Order ID': order_id,
        'Order Date': order_date,
        'Units Ordered': units_ordered,
        'Fulfillment Days': fulfillment_days,
        'Delivery Delay Days':delivery_delays,
        'Return Status': return_stuatus
    })
    
    return orders_df

# inventory
def create_inventory(products, num_products):
    product_names = [products[_].name for _ in range(num_products)] 
    product_sku_id = [products[_].sku_id for _ in range(num_products)]
    product_price = [products[_].price for _ in range(num_products)]
    product_category = [products[_].category for _ in range(num_products)]
    product_image_url  = [products[_].image_url for _ in range(num_products)]
    product_rating = [products[_].rating for _ in range(num_products)]
    product_stock = [products[_].stock for _ in range(num_products)]
    product_reorder_point = [products[_].reorder_point for _ in range(num_products)]
    stockout_flag = [1 if products[_].stock < products[_].reorder_point else 0 for _ in range(num_products)]


    inventory_df = pd.DataFrame({
        'Product Name': product_names,
        'Product SKU ID': product_sku_id,
        'Product Price': product_price,
        'Product Category': product_category,
        'Product Image URL': product_image_url,
        'Product Rating': product_rating,
        'Product Stock': product_stock,
        'Product Reorder Point': product_reorder_point,
        'Stockout Flag': stockout_flag

    })

    return inventory_df

# returns
def create_returns(products, orders_df):
    refund_reasons = [
        "Wrong size",
        "Item damaged",
        "Wrong item sent",
        "Arrived too late",
        "Changed mind",
        "Poor quality",
        "???"
    ]
    reason_weights = [0.35, 0.15, 0.10, 0.10, 0.1, 0.1, 0.15]

    resolutions = [
        "Refund",
        "Exchange - Size",
        "Exchange - Item",
        "Store Credit",
        "Partial Refund",
        "No Action"
    ]
    resol_weights = [0.50, 0.20, 0.10, 0.10, 0.05, 0.05]

    num_refunds = 50
    
    orders = [orders_df.iloc[random.randint(0,199)] for _ in range(num_refunds)]
    return_id = ['RET'+order['Order ID'][3:] for order in orders]
    order_id = [order['Order ID'] for order in orders]
    returned_item = [order['Product Ordered'] for order in orders]
    refund_reason = [random.choices(refund_reasons, weights=reason_weights, k=1)[0] for _ in range(num_refunds)]
    resolution = [random.choices(resolutions, weights=resol_weights, k=1)[0] for _ in range(num_refunds)]
    processing_days = [random.randint(1,3) for _ in range(num_refunds)]
    return_date = [
    min(order["Order Date"] + timedelta(days=random.randint(1, 7)),
        (order["Order Date"] + relativedelta(months=1)).replace(day=1) - timedelta(days=1))
    for order in orders
    ]



    returns_df = pd.DataFrame({
        'Return ID':return_id,
        'Order ID':order_id,
        'Return Date':return_date,
        'Returned Item':returned_item,
        'Refund Reason':refund_reason,
        'Resolution':resolution,
        'Processing Days':processing_days
    })

    return returns_df

os.makedirs('month_1', exist_ok=True)
os.makedirs('month_2', exist_ok=True)
os.makedirs('month_3', exist_ok=True)

month = 1
orders = []
inventories = []
returns = []

for start_date in [month_1_start, month_2_start, month_3_start]:

    products = create_products(num_products)
    orders_df = create_orders(products, start_date)
    inventory_df = create_inventory(products, num_products)
    returns_df = create_returns(products, orders_df)

    # adding some outliers
    outlier_indices = orders_df.sample(frac=0.05).index
    orders_df.loc[outlier_indices, "Fulfillment Days"] += np.random.randint(30, 60, size=len(outlier_indices))

    bulk_indices = orders_df.sample(frac=0.005).index
    orders_df.loc[bulk_indices, "Units Ordered"] = np.random.randint(50, 100, size=len(bulk_indices))

    # 2% missing Order ID
    orders_df.loc[orders_df.sample(frac=0.02).index, "Order ID"] = None

    # 1% missing Fulfillment Days
    orders_df.loc[orders_df.sample(frac=0.01).index, "Fulfillment Days"] = None

    # 3% missing Delivery Delay Days
    orders_df.loc[orders_df.sample(frac=0.03).index, "Delivery Delay Days"] = None

    # 3% missing Processing Days
    returns_df.loc[returns_df.sample(frac=0.05).index, "Processing Days"] = None

    orders.append(orders_df)
    inventories.append(inventory_df)
    returns.append(returns_df)

    # create csvs
    orders_df.to_csv(f'month_{month}/month_{month}_orders.csv')
    inventory_df.to_csv(f'month_{month}/month_{month}_inventory.csv')
    returns_df.to_csv(f'month_{month}/month_{month}_returns.csv')

    month+=1
