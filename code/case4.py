from datetime import datetime, timedelta

if 'CustomerID' in input_data.keys():

    # Launch the query to the Shopify restful API through CustomerID
    url = 'https://' + input_data['shopname'] + '.myshopify.com/admin/orders.json?customer_id=' + input_data['CustomerID'] +  '&created_at=%2310001&financial_status=paid&limit=2'
    orders = requests.get(url, auth=(input_data['apikey'], input_data['password'])).json()

    if len(orders['orders']) >= 2: # Not a new customer
        # if it's a sample, subtotal_price should be cero
        # Check if another criteria should be applied
        subtotal_price = float(orders['orders'][1]['subtotal_price'])
        if subtotal_price == 0:
            return {'sample': True} # Price is zero
        else:
            return {'sample': False} # Price is not zero
    else:
        return {'sample': False} # First purchase
    
else:
    return {'sample': False} # No data input