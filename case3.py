from datetime import datetime, timedelta

if 'CustomerID' in input_data.keys():

    # Launch the query to the Shopify restful API through CustomerID
    url = 'https://' + input_data['shopname'] + '.myshopify.com/admin/orders.json?customer_id=' + input_data['CustomerID'] +  '&created_at=%2310001&financial_status=paid&limit=2'
    orders = requests.get(url, auth=(input_data['apikey'], input_data['password'])).json()

    if len(orders['orders']) >= 2:
        dateLastOrder = str(orders['orders'][1]['created_at'][0:19])
        total_price = float(orders['orders'][1]['total_price'])

        # Get the differenece
        timeDifference = datetime.now() - datetime.strptime(dateLastOrder, '%Y-%m-%dT%H:%M:%S')

        # Threshold reached?
        if int(timeDifference.days) >= int(input_data['daysThreshold']):
            return {'days': timeDifference.days, 'total_price' : total_price, 'thresholdReached': True}
        else:
            return {'days': timeDifference.days, 'total_price' : total_price, 'thresholdReached': False}        
    else:
        return {'days': 0 , 'total_price' : 0, 'thresholdReached': False}
    
else:
    return {'days': 0 , 'total_price' : 0, 'thresholdReached': False}