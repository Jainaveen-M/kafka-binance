
import json
# t = "[{'price': '0.06194000', 'qty': '28733.20000000', 'commission': '0.00000000', 'commissionAsset': 'USDT', 'tradeId': 125643}]"

# t = json.dumps(t)

# data = json.loads(t)

# data = data.replace("'",'"')

# data = json.loads(data)

# new_tran_data = [{
#                             "price":12,
#                             "qty":123,
#                             "commission":1234,
#                             "commissionAsset":12345,
#                             "tradeId":123456
#                         }]

# data.append(new_tran_data)

# new_tran_data = [{
#                             "price":12,
#                             "qty":123,
#                             "commission":1234,
#                             "commissionAsset":12345,
#                             "tradeId":123456
#                         }]

# data.append(new_tran_data)



# print(type(data))

# print(data)






# t = "[]"
t = "{'price': '0.06194000', 'qty': '28733.20000000', 'commission': '0.00000000', 'commissionAsset': 'USDT', 'tradeId': 125643}"
# t = json.dumps(t)
# t = json.loads(t)
t = json.loads(t.replace("'", '"'))

new_tran_data = {
                            "price":12,
                            "qty":123,
                            "commission":1234,
                            "commissionAsset":12345,
                            "tradeId":123456
                        }
t.append(new_tran_data)
print(t)
print(type(t))