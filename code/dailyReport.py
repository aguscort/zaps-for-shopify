from datetime import datetime, timedelta
import json

# New var
output_data = {}
ordersToday = []
ordersCurrentMonth = []
ordersFormerMonth = []
arr_todays_sales = []
errorQueryShopify = False
errorQueryShipstation = False

# Output var
todays_sales  = 0.0                 # Check
monthly_sales = 0.0                 # Check
last_month_sales_same_period = 0.0  # Check
total_orders = 0                    # Check
number_of_visitors = 0

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


def dateTreatment():
    # Date treatment
    date = datetime.now()
    datetoday = date.strftime('%Y-%m-%d')
    datetomorrow = datetime.now() + timedelta(days=1)
    datetomorrow = datetomorrow.strftime('%Y-%m-%d')
    try:
        datelastmonth = (date - timedelta(days=date.day)).replace(day=date.day)
    except ValueError:
        datelastmonth = date.replace(month=date.month, day=1) - timedelta(days=1)

    datelastmonth = datelastmonth.strftime('%Y-%m-%d')
    return datetoday, datetomorrow, datelastmonth

def getMedian(lst):
    n = len(lst)
    if n < 1:
            return None
    if n % 2 == 1:
            return sorted(lst)[n//2]
    else:
            return sum(sorted(lst)[n//2-1:n//2+1])/2.0

def getOrdersPeriod(tool, created_at_min, created_at_max):
    if tool == 'shopify':
        url = 'https://' + input_data['shopname'] + '.myshopify.com/admin/orders.json?order=created_at+desc&fields=id,fulfillment_service,total_price,created_at&financial_status=paid&created_at_min="' + created_at_min  +  'T00:00:00-00:00"&created_at_max="' + created_at_max  +  'T00:00:00-00:00"' 
        return requests.get(url, auth=(input_data['apikey'], input_data['password'])).json()
    elif tool == 'shipstation':
        url = 'https://ssapi.shipstation.com/orders?createDateStart=' + created_at_min + '&createDateEnd=' + created_at_max + '&pageSize=500'        
        return requests.get(url, auth=(input_data['apikey_shipstation'], input_data['password_shipstation'])).json()
    else:
        return None

def getOrdersToday(tool, created_at):
    if tool == 'shopify':
        url = 'https://' + input_data['shopname'] + '.myshopify.com/admin/orders.json?order=created_at+desc&fields=id,line_items,customer,fulfillment_service,total_price,created_at&financial_status=paid&created_at_min="' + created_at  +  'T00:00:00-00:00"' 
        return requests.get(url, auth=(input_data['apikey'], input_data['password'])).json()
    elif tool == 'shipstation':
        url = 'https://ssapi.shipstation.com/orders?createDateStart=' +  created_at 
        return requests.get(url, auth=(input_data['apikey_shipstation'], input_data['password_shipstation'])).json()
    else:
        return None

def getCustomer(customer_id):
    url = 'https://' + input_data['shopname'] + '.myshopify.com/admin/customers/' + customer_id + '.json?fields=id,orders_count'
    return requests.get(url, auth=(input_data['apikey'], input_data['password'])).json()

def getCustomerOrders(customer_id):
    url = 'https://' + input_data['shopname'] + '.myshopify.com/admin/orders.json?customer_id=' + customer_id +  '&order=created_at+desc&fields=id,created_at,total_price,subtotal_price&financial_status=paid&limit=2' 
    return requests.get(url, auth=(input_data['apikey'], input_data['password'])).json()

def categorizeSale(order, new_customers, first_time_reorders, converted_by_samples, wonback_customers):
    customer = getCustomer(str(order['customer']['id']))
    orders = getCustomerOrders(str(order['customer']['id']))

    if int(customer['customer']['orders_count']) == 1: # is New Customer?
        new_customers += 1
    else:
        if int(customer['customer']['orders_count']) == 2: # is First Reorder? (and not from samples)
            if float(orders['orders'][1]['subtotal_price']) == 0.0: # Search for a special case, first order were samples
                converted_by_samples += 1     
            else:
                first_time_reorders += 1
        else:  # More than 2 orders...
            timeDifference = datetime.now() - datetime.strptime(str(orders['orders'][1]['created_at'][0:19]), '%Y-%m-%dT%H:%M:%S')
            if int(timeDifference.days) >= int(input_data['daysThreshold']): # is Wonback Customer?
                wonback_customers += 1
            else:
                if float(orders['orders'][1]['subtotal_price']) == 0.0: # Last Order was a Sample
                    converted_by_samples += 1
                else: # No special case: no need to count into any category
                    pass
    return new_customers, first_time_reorders, converted_by_samples, wonback_customers

# Get Dates
datetoday, datetomorrow, datelastmonth = dateTreatment()

# Get the info from the API
##############
#
# SHIPSTATION
#
##############
try:
    ordersToday = getOrdersPeriod('shipstation', datetoday, datetomorrow)     
    ordersCurrentMonth = getOrdersPeriod('shipstation', datetoday[:8] + '01', datetoday) 
    ordersFormerMonth = getOrdersPeriod('shipstation', datelastmonth[:8] + '01', datelastmonth)
except:
    errorQueryShipstation = True

if errorQueryShipstation is False:
    for order in range(len(ordersToday['orders'])):
        if (ordersToday['orders'][order]['advancedOptions']['source']) == 'web':
            if input_data['takeInfoFromShopify'] == 'False':
                arr_todays_sales.append (float(ordersToday['orders'][order]['orderTotal']))
                todays_sales += float(ordersToday['orders'][order]['orderTotal'])
                total_orders += 1            
                online_orders += 1
                online_sales += float(ordersToday['orders'][order]['orderTotal'])
                errorQueryShopify = True
                for product in range(len(ordersToday['orders'][order]['items'])):
                    product_name = str(ordersToday['orders'][order]['items'][product]['name']) 
                    if product_name.find('Varnish') != -1:
                        units_of_varnish_sold += int(ordersToday['orders'][order]['items'][product]['quantity']) 
                    elif product_name.find('Prophy') != -1:    
                        units_of_prophy_sold += int(ordersToday['orders'][order]['items'][product]['quantity'])                
                errorQueryShopify = True       
            else:                
                pass
        else:
            arr_todays_sales.append (float(ordersToday['orders'][order]['orderTotal']))
            todays_sales += float(ordersToday['orders'][order]['orderTotal'])
            total_orders += 1            
            manual_orders += 1
            manual_sales += float(ordersToday['orders'][order]['orderTotal'])    
            for product in range(len(ordersToday['orders'][order]['items'])):
                product_name = str(ordersToday['orders'][order]['items'][product]['name']) 
                if product_name.find('Varnish') != -1:
                    units_of_varnish_sold += int(ordersToday['orders'][order]['items'][product]['quantity']) 
                elif product_name.find('Prophy') != -1:    
                    units_of_prophy_sold += int(ordersToday['orders'][order]['items'][product]['quantity'])

    # Check all monthly orders
    for order in range(len(ordersCurrentMonth['orders'])):
        monthly_sales += float(ordersCurrentMonth['orders'][order]['orderTotal'])

    # Check all last period orders
    for order in range(len(ordersFormerMonth['orders'])):
        last_month_sales_same_period += float(ordersFormerMonth['orders'][order]['orderTotal'])
                                              
                                              
##############
#
# SHOPIFY
#
##############
if input_data['takeInfoFromShopify'] == 'True':
    try:
        ordersToday = getOrdersToday('shopify', datetoday)    
        # ordersCurrentMonth = getOrdersPeriod('shopify', datetoday[:8] + '01', datetoday) #datetime.now().strftime('%Y-%m-%d'))
        # ordersFormerMonth = getOrdersPeriod('shopify', datelastmonth[:8] + '01', datelastmonth) #datetime.now().strftime('%Y-%m-%d'))
    except:
        errorQueryShopify = True

    if errorQueryShopify == False:
        # Check all orders
        url = 'https://store.zapier.com/api/records?secret=' + input_data['storage_key']
        ordersToday = requests.get(url).json()        
        for item in ordersToday:
            try:
                order = dict(ordersToday[item])
                arr_todays_sales.append (float(order['order']['total_price']))
                todays_sales += float(order['order']['total_price'])
                total_orders += 1
                online_orders += 1
                online_sales += float(order['order']['total_price'])
                # Filter orders with a min value
                if float(order['order']['total_price']) > float(input_data['min_value']):
                    new_customers, first_time_reorders, converted_by_samples, wonback_customers = categorizeSale (order['order'], new_customers, first_time_reorders, converted_by_samples, wonback_customers)
                for product in range(len(order['order']['line_items'])):
                    product_name = str(order['order']['line_items'][product]['name']) 
                    if product_name.find('Varnish') != -1:
                        units_of_varnish_sold += int(order['order']['line_items'][product]['quantity']) 
                    elif product_name.find('Prophy') != -1:    
                        units_of_prophy_sold += int(order['order']['line_items'][product]['quantity'])
            except ValueError:
                pass
            except KeyError:
                pass
        # for order in range(len(ordersToday['orders'])):
        #     arr_todays_sales.append (float(ordersToday['orders'][order]['total_price']))
        #     todays_sales += float(ordersToday['orders'][order]['total_price'])
        #     total_orders += 1
        #     online_orders += 1
        #     online_sales += float(ordersToday['orders'][order]['total_price'])        
        #     # Filter orders with a min value
        #     if float(ordersToday['orders'][order]['total_price']) > float(input_data['min_value']):
        #         new_customers, first_time_reorders, converted_by_samples, wonback_customers = categorizeSale (ordersToday['orders'][order], new_customers, first_time_reorders, converted_by_samples, wonback_customers)
        #     for product in range(len(ordersToday['orders'][order]['line_items'])):
        #         product_name = str(ordersToday['orders'][order]['line_items'][product]['name']) 
        #         if product_name.find('Varnish') != -1:
        #             units_of_varnish_sold += int(ordersToday['orders'][order]['line_items'][product]['quantity']) 
        #         elif product_name.find('Prophy') != -1:    
        #             units_of_prophy_sold += int(ordersToday['orders'][order]['line_items'][product]['quantity'])
                        
if len(arr_todays_sales) == 0:
    arr_todays_sales.append(0.0)                        

# Building the response
if not (errorQueryShopify == True and errorQueryShipstation == True):
    output_data['date_report'] = datetime.strptime(datetoday,'%Y-%m-%d').strftime('%d-%m-%Y')
    output_data['todays_sales'] = "{:0,.2f}".format(todays_sales)
    output_data['monthly_sales'] = "{:0,.2f}".format(monthly_sales)
    output_data['last_month_sales_same_period'] = "{:0,.2f}".format(last_month_sales_same_period)
    output_data['total_orders'] = total_orders
    output_data['highest_sale'] = sorted(arr_todays_sales)[-1]
    output_data['median_sale'] = getMedian(arr_todays_sales)
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

output_data['errorQueryShipstation'] = 'Error while querying SHIPSTATION' if errorQueryShipstation == True else 'Query to SHIPSTATION succesful' 
output_data['errorQueryShopify'] = 'Error while querying SHOPIFY' if errorQueryShopify == True else 'Query to SHOPIFY succesful'

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
    'errorQueryShipstation' : output_data['errorQueryShipstation'], \
    'errorQueryShopify' : output_data['errorQueryShopify'] }