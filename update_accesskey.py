import os

os.chdir(r"C:\Users\lekha.p.s.DIR\Documents\HR Git Code\HRMicroservicesHub_9514\9514_HRMicroservicesHub_REBAR_Service\leaveentitlement")

cwd=os.getcwd()
print("Current working directory is:", cwd)

dynamodb_file = open('src\\dynamoconfig.json', 'r')
data = dynamodb_file.read()
data_accesskey = data.replace('abc', 'abcd')
data_secretkey = data_accesskey.replace('abc', 'abcdE')
dynamodb_file.close()
dynamodb_file = open("src\\dynamoconfig.json", "wt")
dynamodb_file.write(data_secretkey)
dynamodb_file.close()