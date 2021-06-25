#pip install pyxlsb
import pandas as pd
from datetime import date
from datetime import timedelta
import boto3
import time
import sys

boto3.setup_default_session(profile_name='RulesEngineProd')
#prerequisite getting today's & yesterday's date to update the sheet
today = date.today()
yesterday = today - timedelta(days = 1)
processed_date = date.today()
#format the dates after calculating yesterday's date. if you format before calculation you will get an 
#error unsupported operand type(s) for -: 'str' and 'datetime.timedelta'
today = today.strftime("%m/%d/%Y")
yesterday = yesterday.strftime("%m/%d/%Y")
processed_date = processed_date.strftime("%Y/%m/%d")
processed_date = processed_date.replace("/", "")

#reading file add engine detail to read xlsb binary file (not required for xlsx file)
filename = 'Allowable Cost Center Create -06252021'
filename_binary = filename + '.xlsb'
file = pd.read_excel(filename_binary, engine='pyxlsb')
print(file)
#removes empty rows under column name Cost Center
file.dropna(subset = ["Cost Center"], inplace=True)
#axis 1 denotes column. it removes all the empty columns
file.dropna(how='all', axis=1, inplace=True)
#sometimes we receive sub org with decimal .0, below line is to remove decimal points
file['Sup Org'] = file['Sup Org'].apply(int)
file.drop(file.columns[file.columns.str.contains('unnamed',case = False)],axis = 1, inplace = True)

#modifying excel sheet - Action items
try:
    file.drop(['Request number','Requestor'], inplace=True, axis=1)
except KeyError:
    print("No Request Number & Requestor column")
file['Action'] = file['Action'].replace('Remove','delimit')
file.loc[file.Action == "delimit", 'Effective Start Date'] = yesterday
file.loc[file.Action == "delimit", 'Effective End Date'] = yesterday
file.loc[file.Action == "Add", 'Effective Start Date'] = today
file.loc[file.Action == "Add", 'Effective End Date'] = "12/31/9999"
file['Cost Center'] = file['Cost Center'].astype(str).replace('\.0', '', regex=True)
file['Cost Center'] = file['Cost Center'].apply(lambda x: '{0:0>10}'.format(x))
print(file)
#print(file.info())

#uploading changes in new file, set index=false to remove row index (0,1,2..)
updated_file = filename+"-"+processed_date+'.xlsx'
file.to_excel(updated_file, index=False)

#boto3 sfn steps to check last executed status and date
sfn = boto3.client('stepfunctions')

def stepfn_details(stepfunction_name):
    print(stepfunction_name)
    response = sfn.list_executions(
    stateMachineArn=stepfunction_name,
    maxResults=1
    )
    exec_status = response['executions'][0]['status']
    print(response['executions'][0]['status'])
    print(response['executions'][0]['startDate'])
    return response['executions'][0]['status']
    if exec_status == "FAILED":
        sys.exit()

stepfn_details('arn:aws:states:us-east-1:136703301440:stateMachine:stepfn_name')
#upload modified xlsx sheet t s3
s3 = boto3.resource('s3')
s3_response = s3.meta.client.upload_file(updated_file, 's3-bucket', 'sub-folder/'+updated_file)
print(s3_response)
print("Uploaded to s3! Added sleep time to proceed with lambda process")
time.sleep(20)
lamb = boto3.client('lambda')    
env_var = "subfolder/"+updated_file
try:
    lamb_response = lamb.update_function_configuration(
        FunctionName='lambda_name',
        Environment={
            'Variables': {
                'tempInputPath': env_var,
                'chunk_size': '1000',
                'env': 'Prod',
                'localenv': 'false',            
            }
        }
    )
    print(lamb_response)
except Exception as e:
    print(e)
try:
    response = lamb.invoke(FunctionName='lambdaname')
    print("Invoked lambda")
except Exception as e:
    print(e)
print("Started lambda!wait for few mins to complete")
def invoke_lambda():
    time.sleep(360)
    status = stepfn_details('arn:aws:states:us-east-1:136703301440:stateMachine:stfn')
    if status == "SUCCEEDED":
        try:
            print("step function succeeded")
            response = lamb.invoke(FunctionName='lambdaname')
            print("Invoked lambda")
        except Exception as e:
            print(e)
    elif status == "FAILED":
        print("step function failed")
    elif status == "RUNNING":
        print("step function status is "+status)
        print("re-checking status after few mins")
        invoke_lambda()
    else:
        print("step function status is "+status)
invoke_lambda()
print("Downloading S3 files")
time.sleep(20)
s3_client = boto3.client('s3')
def download_S3file(path, local_filename):
    s3 = boto3.resource('s3')
    s3File = s3_client.list_objects_v2(
        Bucket='s3-bucket',
        Prefix=path
    )   
    S3Filename = s3File['Contents'][-1]['Key']
    print (s3File['Contents'][-1]['LastModified'])
    print(S3Filename)
    s3.meta.client.download_file('s3-bucket', S3Filename, local_filename)
    return S3Filename
download_S3file('subfolder/', 'audit.txt')
print("downloaded audit file")
S3Filename=download_S3file('subfolder/', 'CostCenter.xml')
print("downloaded final xml file")  
def delete_S3File(S3Filename):
    response = s3_client.delete_object(Bucket='s3-bucket',Key=S3Filename)
    print("S3 File deleted")
print("deleting xml file "+S3Filename)
delete_S3File(S3Filename)
