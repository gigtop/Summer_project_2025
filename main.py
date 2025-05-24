import json
f = 'main_derectory/content.json'
# with open(f) as jfile:
#     data = json.load(jfile)
#     print(data,"\n\n\n")
# import json

# returns JSON object as a dictionary
data = json.load(f)

# Iterating through the json list
for i in data['emp_details']:
    print(i)

# Closing file
f.close()