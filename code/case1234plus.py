from datetime import datetime, timedelta

isNewCustomer = False
isFirstReorder = False
isWonbackCustomer = False
isWonbackCustomerAfterSample = False
timeDifference = datetime.now() - datetime.now() 
dateLastOrder = None
dateLastOrderPretty = None
total_price_former_order = 0.0
total_daily_sales = 0.0
days = 0
subject = ''
utm_data = {}

def getCustomer(customer_id):
    url = 'https://' + input_data['shopname'] + '.myshopify.com/admin/customers/' + customer_id + '.json?fields=id,first_name,last_name,email,orders_count'
    return requests.get(url, auth=(input_data['apikey'], input_data['password'])).json()


def getOrders(customer_id):
    url = 'https://' + input_data['shopname'] + '.myshopify.com/admin/orders.json?customer_id=' + customer_id +  '&order=created_at+desc&fields=created_at,total_price,subtotal_price,landing_site&financial_status=paid&limit=2' 
    return requests.get(url, auth=(input_data['apikey'], input_data['password'])).json()

def parseLangingPage(landing_page):
    utm_data = {}    
    if landing_page.find('utm_campaign') != -1 and landing_page.find('utm_medium') !=-1 and landing_page.find('utm_source') != -1:
        for i in range(len(landing_page.split("&"))):            
            utm_data[landing_page.split("&")[i].split("=")[0]] = landing_page.split("&")[i].split("=")[1]
    return utm_data

def getOrdersToday(created_at):
    total_daily_sales = 0.0
    url = 'https://' + input_data['shopname'] + '.myshopify.com/admin/orders.json?order=created_at+desc&fields=id,total_price,created_at&financial_status=paid&created_at_min="' + datetime.now().strftime('%Y-%m-%d')  +  'T00:00:00-00:00"' 
    orders = requests.get(url, auth=(input_data['apikey'], input_data['password'])).json()
    for order in range(len(orders['orders'])):
        total_daily_sales += float(orders['orders'][order]['total_price'])
        #print (str(orders['orders'][order]['created_at']))
    return total_daily_sales


if 'CustomerID' in input_data.keys():
    customers = getCustomer(input_data['CustomerID'])
    orders = getOrders(input_data['CustomerID'])
    utm_data = parseLangingPage(str(orders['orders'][0]['landing_site']))
    total_daily_sales = getOrdersToday(str(orders['orders'][0]['created_at'][0:10]))    
    
    if int(customers['customer']['orders_count']) == 1: # is New Customer?
        isNewCustomer = True
        subject = 'New Customer'
    else:
        dateLastOrder = str(orders['orders'][1]['created_at'][0:19])
        dateLastOrderPretty = dateLastOrderPretty = datetime.strptime(dateLastOrder, '%Y-%m-%dT%H:%M:%S').strftime('%b %d, %Y')
        total_price_former_order = orders['orders'][1]['total_price']        
        if int(customers['customer']['orders_count']) == 2: # is First Reorder? (and not from samples)
            if float(orders['orders'][1]['subtotal_price']) == 0.0: # Search for a special case, first order were samples
                isWonbackCustomerAfterSample = True
                subject = 'Wonback Customer from Samples'                    
            else:
                isFirstReorder = True
                subject = 'First Reorder'
        else:  # More than 2 orders...
            timeDifference = datetime.now() - datetime.strptime(dateLastOrder, '%Y-%m-%dT%H:%M:%S')

            if int(timeDifference.days) >= int(input_data['daysThreshold']): # is Wonback Customer?
                isWonbackCustomer = True
                subject = 'Wonback Customer'
            else:
                if float(orders['orders'][1]['subtotal_price']) == 0.0: # Last Order was a Sample
                    isWonbackCustomerAfterSample = True
                    subject = 'Convert from Samples'                    
                else: # No special case: no need to sent any email
                    pass


return {'isNewCustomer' : isNewCustomer, \
        'isFirstReorder' : isFirstReorder, \
        'isWonbackCustomer' : isWonbackCustomer, \
        'isWonbackCustomerAfterSample' : isWonbackCustomerAfterSample, \
        'date_last_order' : dateLastOrderPretty, \
        'total_price_former_order' : total_price_former_order, \
        'days' : int(timeDifference.days), \
        'subject' : subject, \
        'total_daily_sales' : total_daily_sales, \
        'utm_data' : utm_data }