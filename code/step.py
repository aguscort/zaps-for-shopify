import json
import requests

a = []
code_10852530001159 = ''
code_10852530001166 = ''
code_10852530001104 = ''
code_10852530001128 = ''
code_10852530001111 = ''   


def GetStorage(access_token):
    url = 'https://store.zapier.com/api/records?secret=' + access_token
    return requests.get(url).json()


try:
    a = GetStorage(input_data['access_token_lines'])
    store = StoreClient(input_data['access_token_lines'])
    for i in a:
        if input_data['order_id'] == a[i]['Order']:
            if a[i]['Code'] == '10852530001159':
                code_10852530001159 = a[i]['Qty']
            elif a[i]['Code'] == '10852530001166':
                code_10852530001166 = a[i]['Qty']               
            elif a[i]['Code'] == '10852530001104':
                code_10852530001104 = a[i]['Qty']
            elif a[i]['Code'] == '10852530001128':
                code_10852530001128 = a[i]['Qty']
            elif a[i]['Code'] == '10852530001111':
                code_10852530001111 = a[i]['Qty'] 
            #store.delete(a[i])               
except:
    pass

return { '10852530001159': code_10852530001159, \
    '10852530001166': code_10852530001166, \
    '10852530001104': code_10852530001104, \
    '10852530001128': code_10852530001128, \
    '10852530001111': code_10852530001111 }