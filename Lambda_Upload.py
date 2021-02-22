import os
import subprocess
import boto3

#aws lambda update-function-code --function-name MyLambdaFunction --zip-file fileb://my-deployment-package.zip

os.chdir(r"C:\Users\lekha.p.s.DIR\Documents\HR Git Code\HRMicroservicesHub_9514\9514_HRMicroservicesHub_REBAR_Service\leaveentitlement\package\9514-Leaveentitlement-sls-pkg-dev")

cwd=os.getcwd()
print("Current working directory is:", cwd)

subprocess.run('aws lambda update-function-code --function-name 9514_Dev_HRMicroservicesHub_LeaveEntitlement --zip-file fileb://LeaveEntil-9514.zip')
print("lambda updated!")