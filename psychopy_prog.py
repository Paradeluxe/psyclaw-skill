obj = "{\n\"1\": [3, 4, 5, 6],\n\"2\": [6, 7, 8, 9],\n\"3\": [9, 10, 11]\n}"




import json
result = json.loads(obj)
# 只要values
values = list(result.values())
print(values)
