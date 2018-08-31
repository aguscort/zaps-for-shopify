from datetime import datetime, timedelta
import json

# New var
output_data = {}
orders_today = []
orders_current_month = []
orders_former_month = []
arr_todays_sales = []
error_query_shopify = False
error_query_shipstation = False

# Output var
todays_sales  = 0.0                 # Check
monthly_sales = 0.0                 # Check
last_month_sales_same_period = 0.0  # Check
total_orders = 0                    # Check

online_orders = 0                   # Check
online_sales = 0.0                  # Check
manual_orders = 0                   # Check
manual_sales = 0.0                  # Check

new_customers = 0                   # Check
first_time_reorders = 0             # Check
converted_by_samples = 0            # Check
wonback_customers = 0               # Check

highest_sale = 0.0                  # Check
median_sale = 0.0                   # Check
avg_sale = 0.0                      # Check

units_of_varnish_sold = 0           # Check
units_of_prophy_sold = 0            # Check


def date_treatment():
    # Date treatment
    date = datetime.utcnow() - timedelta(hours=8)
    datetoday = date.strftime('%Y-%m-%d')
    datetomorrow = date + timedelta(days=1)
    datetomorrow = datetomorrow.strftime('%Y-%m-%d')
    try:
        datelastmonth = (date - timedelta(days=date.day)).replace(day=date.day)
    except ValueError:
        datelastmonth = date.replace(month=date.month, day=1) - timedelta(days=1)

    datelastmonth = datelastmonth.strftime('%Y-%m-%d')
    return datetoday, datetomorrow, datelastmonth


def get_median(lst):
    n = len(lst)
    if n < 1:
            return None
    if n % 2 == 1:
            return sorted(lst)[n//2]
    else:
            return sum(sorted(lst)[n//2-1:n//2+1])/2.0


def get_orders_period(tool, created_at_min, created_at_max):
    if tool == 'shopify':
        url = 'https://' + input_data['shopname'] + '.myshopify.com/admin/orders.json?order=created_at+desc&fields=id,fulfillment_service,total_price,created_at&financial_status=paid&created_at_min="' + created_at_min  +  'T00:00:00-00:00"&created_at_max="' + created_at_max  +  'T00:00:00-00:00"' 
        return requests.get(url, auth=(input_data['apikey'], input_data['password'])).json()
    elif tool == 'shipstation':
        url = 'https://ssapi.shipstation.com/orders?createDateStart=' + created_at_min + '&createDateEnd=' + created_at_max + '&pageSize=500'        
        return requests.get(url, auth=(input_data['apikey_shipstation'], input_data['password_shipstation'])).json()
    else:
        return None


def get_orders_today(tool, created_at):
    if tool == 'shopify':
        url = 'https://' + input_data['shopname'] + '.myshopify.com/admin/orders.json?order=created_at+desc&fields=id,line_items,customer,fulfillment_service,total_price,created_at&financial_status=paid&created_at_min="' + created_at  +  'T00:00:00-00:00"' 
        return requests.get(url, auth=(input_data['apikey'], input_data['password'])).json()
    elif tool == 'shipstation':
        url = 'https://ssapi.shipstation.com/orders?createDateStart=' +  created_at 
        return requests.get(url, auth=(input_data['apikey_shipstation'], input_data['password_shipstation'])).json()
    else:
        return None


def get_customer(customer_id):
    url = 'https://' + input_data['shopname'] + '.myshopify.com/admin/customers/' + customer_id + '.json?fields=id,orders_count'
    return requests.get(url, auth=(input_data['apikey'], input_data['password'])).json()


def get_customer_orders(customer_id):
    url = 'https://' + input_data['shopname'] + '.myshopify.com/admin/orders.json?customer_id=' + customer_id +  '&order=created_at+desc&fields=id,created_at,total_price,subtotal_price&financial_status=paid&limit=2' 
    return requests.get(url, auth=(input_data['apikey'], input_data['password'])).json()


def categorize_purchase(order, new_customers, first_time_reorders, converted_by_samples, wonback_customers):
    customer = get_customer(str(order['customer']['id']))
    orders = get_customer_orders(str(order['customer']['id']))

    if int(customer['customer']['orders_count']) == 1: # is New Customer?
        new_customers += 1
    else:
        if int(customer['customer']['orders_count']) == 2: # is First Reorder? (and not from samples)
            if float(orders['orders'][1]['subtotal_price']) == 0.0: # Search for a special case, first order were samples
                converted_by_samples += 1     
            else:
                first_time_reorders += 1
        else:  # More than 2 orders...
            date = datetime.utcnow() - timedelta(hours=8)
            timeDifference = date - datetime.strptime(str(orders['orders'][1]['created_at'][0:19]), '%Y-%m-%dT%H:%M:%S')
            if int(timeDifference.days) >= int(input_data['days_threshold']): # is Wonback Customer?
                wonback_customers += 1
            else:
                if float(orders['orders'][1]['subtotal_price']) == 0.0: # Last Order was a Sample
                    converted_by_samples += 1
                else: # No special case: no need to count into any category
                    pass
    return new_customers, first_time_reorders, converted_by_samples, wonback_customers


# Get Dates
datetoday, datetomorrow, datelastmonth = date_treatment()

# Get info from SHIPSTATION
try:
    orders_today = get_orders_period('shipstation', datetoday, datetomorrow)     
    orders_current_month = get_orders_period('shipstation', datetoday[:8] + '01', datetoday) 
    orders_former_month = get_orders_period('shipstation', datelastmonth[:8] + '01', datelastmonth)
except:
    error_query_shipstation = True

if error_query_shipstation is False:
    for order in range(len(orders_today['orders'])):
        if (orders_today['orders'][order]['advancedOptions']['source']) == 'web':
            if input_data['take_info_from_shopify'] == 'False':
                arr_todays_sales.append (float(orders_today['orders'][order]['orderTotal']))
                todays_sales += float(orders_today['orders'][order]['orderTotal'])
                total_orders += 1            
                online_orders += 1
                online_sales += float(orders_today['orders'][order]['orderTotal'])
                error_query_shopify = True
                for product in range(len(orders_today['orders'][order]['items'])):
                    product_name = str(orders_today['orders'][order]['items'][product]['name']) 
                    if product_name.find('Varnish') != -1:
                        units_of_varnish_sold += int(orders_today['orders'][order]['items'][product]['quantity']) 
                    elif product_name.find('Prophy') != -1:    
                        units_of_prophy_sold += int(orders_today['orders'][order]['items'][product]['quantity'])                
                error_query_shopify = True       
            else:                
                pass
        else:
            arr_todays_sales.append (float(orders_today['orders'][order]['orderTotal']))
            todays_sales += float(orders_today['orders'][order]['orderTotal'])
            total_orders += 1            
            manual_orders += 1
            manual_sales += float(orders_today['orders'][order]['orderTotal'])    
            for product in range(len(orders_today['orders'][order]['items'])):
                product_name = str(orders_today['orders'][order]['items'][product]['name']) 
                if product_name.find('Varnish') != -1:
                    units_of_varnish_sold += int(orders_today['orders'][order]['items'][product]['quantity']) 
                elif product_name.find('Prophy') != -1:    
                    units_of_prophy_sold += int(orders_today['orders'][order]['items'][product]['quantity'])

    # Check all monthly orders
    for order in range(len(orders_current_month['orders'])):
        monthly_sales += float(orders_current_month['orders'][order]['orderTotal'])

    # Check all last period orders
    for order in range(len(orders_former_month['orders'])):
        last_month_sales_same_period += float(orders_former_month['orders'][order]['orderTotal'])
                                              
# Get info from SHOPIFY
if input_data['take_info_from_shopify'] == True or input_data['take_info_from_shopify'] == 'True': 
    if error_query_shopify == False:
        # Check all orders
        url = 'https://store.zapier.com/api/records?secret=' + input_data['storage_key']
        orders_today = requests.get(url).json() 
        for item in dict.keys(orders_today):            
            if str(item) != 'date':
                order = orders_today[item]
                print(str(order['total_price']) + ' '+ str(order['created_at']))
                arr_todays_sales.append (float(order['total_price']))
                todays_sales += float(order['total_price'])
                total_orders += 1
                online_orders += 1
                online_sales += float(order['total_price'])
                # Filter orders with a min value
                if float(order['total_price']) > float(input_data['min_value']):
                    new_customers, first_time_reorders, converted_by_samples, wonback_customers = categorize_purchase (order, new_customers, first_time_reorders, converted_by_samples, wonback_customers)
                for product in range(len(order['line_items'])):
                    product_name = str(order['line_items'][product]['name']) 
                    if product_name.find('Varnish') != -1:
                        units_of_varnish_sold += int(order['line_items'][product]['quantity']) 
                    elif product_name.find('Prophy') != -1:    
                        units_of_prophy_sold += int(order['line_items'][product]['quantity'])  

                       
if len(arr_todays_sales) == 0:
    arr_todays_sales.append(0.0)                        

# Building the response
if not (error_query_shopify == True and error_query_shipstation == True):
    output_data['date_report'] = datetime.strptime(datetoday,'%Y-%m-%d').strftime('%d-%m-%Y')
    output_data['todays_sales'] = "{:0,.2f}".format(todays_sales)
    output_data['monthly_sales'] = "{:0,.2f}".format(monthly_sales)
    output_data['last_month_sales_same_period'] = "{:0,.2f}".format(last_month_sales_same_period)
    output_data['total_orders'] = total_orders
    output_data['highest_sale'] = sorted(arr_todays_sales)[-1]
    output_data['median_sale'] = get_median(arr_todays_sales)
    output_data['avg_sale'] = "{:0,.2f}".format(sum(arr_todays_sales)/len(arr_todays_sales))
    output_data['manual_orders'] = manual_orders
    output_data['manual_sales'] = "{:0,.2f}".format(manual_sales)
    output_data['online_orders'] = online_orders
    output_data['online_sales'] = "{:0,.2f}".format(online_sales)
    output_data['new_customers'] = new_customers
    output_data['first_time_reorders'] = first_time_reorders
    output_data['converted_by_samples'] = converted_by_samples 
    output_data['wonback_customers'] = wonback_customers
    output_data['units_of_varnish_sold'] = units_of_varnish_sold
    output_data['units_of_prophy_sold'] = units_of_prophy_sold

output_data['error_query_shipstation'] = 'Error while querying SHIPSTATION' if error_query_shipstation == True else 'Query to SHIPSTATION succesful' 
output_data['error_query_shopify'] = 'Error while querying SHOPIFY' if error_query_shopify == True else 'Query to SHOPIFY succesful'

return {'date_report' : output_data['date_report'],  \
    'todays_sales' : output_data['todays_sales'],  \
    'monthly_sales' : output_data['monthly_sales'], \
    'last_month_sales_same_period' : output_data['last_month_sales_same_period'], \
    'total_orders' : output_data['total_orders'], \
    'highest_sale' : output_data['highest_sale'], \
    'median_sale' : output_data['median_sale'], \
    'avg_sale' : output_data['avg_sale'], \
    'manual_orders' : output_data['manual_orders'], \
    'manual_sales' : output_data['manual_sales'], \
    'online_orders' : output_data['online_orders'], \
    'online_sales' : output_data['online_sales'], \
    'new_customers' : output_data['new_customers'], \
    'first_time_reorders' : output_data['first_time_reorders'], \
    'converted_by_samples' : output_data['converted_by_samples'], \
    'wonback_customers' : output_data['wonback_customers'], \
    'units_of_varnish_sold' : output_data['units_of_varnish_sold'], \
    'units_of_prophy_sold' : output_data['units_of_prophy_sold'], \
    'error_query_shipstation' : output_data['error_query_shipstation'], \
    'error_query_shopify' : output_data['error_query_shopify'] }