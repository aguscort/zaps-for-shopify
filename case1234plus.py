from datetime import datetime, timedelta

isNewCustomer = False
isFirstReorder = False
isWonbackCustomer = False
isWonbackCustomerAfterSample = False
timeDifference = datetime.now() - datetime.now() 
dateLastOrder = None
total_price_former_order = 0.0
days = 0
subject = ''

def getCustomer(customer_id):
    url = 'https://' + input_data['shopname'] + '.myshopify.com/admin/customers/' + customer_id + '.json?fields=id,first_name,last_name,email,orders_count'
    return requests.get(url, auth=(input_data['apikey'], input_data['password'])).json()


def getOrders(customer_id):
    url = 'https://' + input_data['shopname'] + '.myshopify.com/admin/orders.json?customer_id=' + customer_id +  '&order=created_at+desc&fields=created_at,total_price,subtotal_price&financial_status=paid&limit=2' 
    return requests.get(url, auth=(input_data['apikey'], input_data['password'])).json()


if 'CustomerID' in input_data.keys():
    customers = getCustomer(input_data['CustomerID'])
    orders = getOrders(input_data['CustomerID'])
    
    if int(customers['customer']['orders_count']) == 1: # is New Customer?
        isNewCustomer = True
        subject = 'New Customer'
    else:
        dateLastOrder = str(orders['orders'][1]['created_at'][0:19])
        total_price_former_order = orders['orders'][1]['total_price']        
        if int(customers['customer']['orders_count']) == 2: # is First Reorder? (and not from samples)
            if and float(orders['orders'][1]['subtotal_price']) == 0.0: # Search for a special case, first order were samples
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
                    subject = 'Wonback Customer from Samples'                    
                else: # No special case: no need to sent any email
                    pass


return {'isNewCustomer' : isNewCustomer, \
        'isFirstReorder' : isFirstReorder, \
        'isWonbackCustomer' : isWonbackCustomer, \
        'isWonbackCustomerAfterSample' : isWonbackCustomerAfterSample, \
        'date_last_order' : dateLastOrder, \
        'total_price_former_order' : total_price_former_order, \
        'days' : int(timeDifference.days), \
        'subject' : subject}