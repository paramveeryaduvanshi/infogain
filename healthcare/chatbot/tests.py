# from django.test import TestCase

# Create your tests here.


# d = {"Query": "What is the Sex of Patient 1 from the provided dataset?"}
# if list(d.keys())[0] == 'Query':
#     print("yes")
# else:
#     print("No")


d = {"where": {"Patient_Number": [2,4]}, "where_document": ["Sex","Blood_Pressure"]}

if 'where' in d.keys():
    print(d['where'].values())
    print(d['where'].keys())
    
