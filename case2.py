from datetime import datetime, timedelta

if 'CustomerID' in input_data.keys():
    # Launch the query to the Shopify restful API through CustomerID
    url = 'https://' + input_data['shopname'] + '.myshopify.com/admin/orders.json?id=' + input_data['CustomerID'] +  '&order=created_at+desc&fields=total_price&financial_status=paid&limit=2'
    orders = requests.get(url, auth=(input_data['apikey'], input_data['password'])).json()

    if len(orders['orders']) >= 2:
        total_price = float(orders['orders'][1]['total_price'])
        return {'total_price' : total_price}
    else:
        return {'total_price' : 0}
else:
    return {'total_price' : 0}