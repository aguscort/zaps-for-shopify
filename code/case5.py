from datetime import datetime, timedelta

users = []
message = ''

# Launch the query to the Shopify restful API 
url = 'https://' + input_data['shopname'] + '.myshopify.com/admin/customers.json?fields=id,first_name,last_name,email,last_order_id&order=created_at+desc'
customers = requests.get(url, auth=(input_data['apikey'], input_data['password'])).json()

for item in range(len(customers['customers'])):
    if customers['customers'][item]['last_order_id'] is not None: 
        url = 'https://' + input_data['shopname'] + '.myshopify.com/admin/orders/' + str(customers['customers'][item]['last_order_id']) + '.json?fields=created_at'
        order = requests.get(url, auth=(input_data['apikey'], input_data['password'])).json()

        # Get the differenece
        timeDifference = datetime.now() - datetime.strptime(str(order['order']['created_at'][0:19]), '%Y-%m-%dT%H:%M:%S')

        if int(timeDifference.days) >= int(input_data['daysThreshold']):
            users.append({'customer_id': customers['customers'][item]['id'],  'days' : int(timeDifference.days) , 'thresholdReached': True})
            message = message + str(customers['customers'][item]['first_name']) + ' ' + str(customers['customers'][item]['last_name']) + ' ordered a purchase ' + str(timeDifference.days) + ' days ago.\n'

return {'message'  : ('No Customers found', message)[message == '']}