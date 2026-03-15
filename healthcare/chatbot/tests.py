# from django.test import TestCase

# Create your tests here.


# d = {"Query": "What is the Sex of Patient 1 from the provided dataset?"}
# if list(d.keys())[0] == 'Query':
#     print("yes")
# else:
#     print("No")


# d = {"where": {"Patient_Number": [2,4]}, "where_document": ["Sex","Blood_Pressure"]}

# if 'where' in d.keys():
#     print(d['where'].values())
#     print(d['where'].keys())


level1_response = {"Query": "SELECT COUNT(*) FROM Dataset1 WHERE Smoking = 'Yes' AND Sex = 'Male'"}
sql_query_result = [{"COUNT(*)": 514}]
user_info = [level1_response, {"Query_output": sql_query_result[0]}]
print(user_info)
