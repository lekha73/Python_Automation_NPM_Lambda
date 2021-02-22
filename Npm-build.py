import os
import subprocess
import boto3

apis = ['leaveentitlement', 'loaquestionnaire', 'ptobalance', 'unpaidtime']
for api in apis:
    #print(api)
    #double \ is added since single \ is considered as an escape character in python
    path = os.path.join("C:\\Users\\lekha.p.s.DIR\\Documents\\HR Git Code\\HRMicroservicesHub_9514\\9514_HRMicroservicesHub_REBAR_Service\\", api)
    print(path)
    os.chdir(path)
    #'r' is mentioned before path to consider whole path as raw string. \ is escape characcter in python
    #os.chdir(r"C:\Users\lekha.p.s.DIR\Documents\HR Git Code\HRMicroservicesHub_9514\9514_HRMicroservicesHub_REBAR_Service\leaveentitlement")

    #updating access keys
    dynamodb_file = open('src\\dynamoconfig.json', 'r')
    data = dynamodb_file.read()
    #data.replace('old', 'new')
    data_accesskey = data.replace('', '')
    data_secretkey = data_accesskey.replace('', '')
    dynamodb_file.close()
    dynamodb_file = open("src\\dynamoconfig.json", "wt")
    dynamodb_file.write(data_secretkey)
    dynamodb_file.close()
    print("Access keys are updated!")
    
    cwd=os.getcwd()
    print("Current working directory is:", cwd)
    
    #Creating npm build files
    subprocess.run('npm run package-dev', shell=True)
    
#Updating Lambda code
#Entitlement
os.chdir(r"C:\Users\lekha.p.s.DIR\Documents\HR Git Code\HRMicroservicesHub_9514\9514_HRMicroservicesHub_REBAR_Service\leaveentitlement\package\9514-Leaveentitlement-sls-pkg-dev")
subprocess.run('aws lambda update-function-code --function-name 9514_Dev_HRMicroservicesHub_LeaveEntitlement --zip-file fileb://LeaveEntil-9514.zip')
print("LE lambda updated!")

#LOA
os.chdir(r"C:\Users\lekha.p.s.DIR\Documents\HR Git Code\HRMicroservicesHub_9514\9514_HRMicroservicesHub_REBAR_Service\loaquestionnaire\package\9514-Loaquestionnaire-sls-pkg-dev")
subprocess.run('aws lambda update-function-code --function-name 9514_Dev_HRMicroservicesHub_LOAQuestionnaire --zip-file fileb://LOAQuestion-9514.zip')
print("LOA lambda updated!")

#PTO
os.chdir(r"C:\Users\lekha.p.s.DIR\Documents\HR Git Code\HRMicroservicesHub_9514\9514_HRMicroservicesHub_REBAR_Service\ptobalance\package\9514-Ptobalance-sls-pkg-dev")
subprocess.run('aws lambda update-function-code --function-name 9514_Dev_HRMicroservicesHub_PTOBalance --zip-file fileb://PTOBalance-9514.zip')
print("PTO lambda updated!")

#Unpaidtime
os.chdir(r"C:\Users\lekha.p.s.DIR\Documents\HR Git Code\HRMicroservicesHub_9514\9514_HRMicroservicesHub_REBAR_Service\unpaidtime\package\9514-Unpaidtime-sls-pkg-dev")
subprocess.run('aws lambda update-function-code --function-name 9514_Dev_HRMicroservicesHub_UnpaidTime --zip-file fileb://Unpaidtime-9514.zip')
print("Unpaidtime lambda updated!")
