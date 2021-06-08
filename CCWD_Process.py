#pip install pyxlsb
import pandas as pd
from datetime import date
from datetime import timedelta
import boto3
import time

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
filename = 'Allowable Cost Center Create -06082021_2'
filename_binary = filename + '.xlsb'
file = pd.read_excel(filename_binary, engine='pyxlsb')
print(file)
#removes empty rows under column name Cost Center
file.dropna(subset = ["Cost Center"], inplace=True)
#axis 1 denotes column. it removes all the empty columns
file.dropna(how='all', axis=1, inplace=True)
#sometimes we receive sub org with decimal .0, below line is to remove decimal points
file['Sup Org'] = file['Sup Org'].apply(int)
#file['Cost Center'] = file['Cost Center'].apply(int)
file.drop(file.columns[file.columns.str.contains('unnamed',case = False)],axis = 1, inplace = True)

#modifying excel sheet - Action items
file.drop(['Request number','Requestor'], inplace=True, axis=1)
file['Action'] = file['Action'].replace('Remove','delimit')
file.loc[file.Action == "delimit", 'Effective Start Date'] = yesterday
file.loc[file.Action == "delimit", 'Effective End Date'] = yesterday
file.loc[file.Action == "Add", 'Effective Start Date'] = today
file.loc[file.Action == "Add", 'Effective End Date'] = "12/31/9999"
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
    print(response['executions'][0]['status'])
    print(response['executions'][0]['startDate'])
    return response['executions'][0]['status']

stepfn_details('arn:aws:states:us-east-1:136703301440:stateMachine:10048_Prod_Rules_Engine_CostCenterHierarchy')
stepfn_details('arn:aws:states:us-east-1:136703301440:stateMachine:10048_Prod_Rules_Engine_PHTable')
stepfn_details('arn:aws:states:us-east-1:136703301440:stateMachine:10048_Prod_Rules_Engine_CCTable')
stepfn_details('arn:aws:states:us-east-1:136703301440:stateMachine:10048_Prod_Rules_Engine_OrgUnitCostCenterMapping')
#upload modified xlsx sheet t s3
s3 = boto3.resource('s3')
s3_response = s3.meta.client.upload_file(updated_file, '10048-rules-engine-prod', 'secure/Storage/Temp/CCTruthTable/Input/FullRefreshDelta/'+updated_file)
print(s3_response)
print("Uploaded to s3! Added sleep time to proceed with lambda process")
time.sleep(20)
lamb = boto3.client('lambda')    
env_var = "secure/Storage/Temp/CCTruthTable/Input/FullRefreshDelta/"+updated_file
try:
    lamb_response = lamb.update_function_configuration(
        FunctionName='10048_Prod_Rules_Engine_OUCCTableDelta',
        Environment={
            'Variables': {
                'tempInputPath': env_var,
                'bucketName': '10048-rules-engine-prod',
                'chunk_size': '1000',
                'env': 'Prod',
                'localenv': 'false',
                'FullRefreshFunctionName': '10048_Prod_Rules_Engine_OrgUnitCostCenterMapping',
                'mrdrApiCallHostAAD': 'qk4nnyxa51.execute-api.us-east-1.amazonaws.com',
                'ouccTable': '10048_Prod_RulesEngine_OrgUnitCostCenterMappingTable',
                'startIndex': '0',
                'stepFunctionName': 'arn:aws:states:us-east-1:136703301440:stateMachine:10048_Prod_Rules_Engine_OUCCTableDelta',
                'tempOutputPath': 'secure/Storage/Temp/CCTruthTable/Input/FullRefreshDelta/InputData.csv'              
            }
        }
    )
    print(lamb_response)
except Exception as e:
    print(e)
try:
    response = lamb.invoke(FunctionName='10048_Prod_Rules_Engine_OUCCTableDelta')
    print("Invoked 10048_Prod_Rules_Engine_OUCCTableDelta lambda")
except Exception as e:
    print(e)
print("Started OUCCTableDelta lambda!wait for few mins to complete")
def invoke_lambda():
    time.sleep(180)
    status = stepfn_details('arn:aws:states:us-east-1:136703301440:stateMachine:10048_Prod_Rules_Engine_OrgUnitCostCenterMapping')
    if status == "SUCCEEDED":
        try:
            print("OrgUnitCostCenterMapping step function succeeded")
            response = lamb.invoke(FunctionName='10048_Prod_RulesEngine_GenerateCostCenter')
            print("Invoked 10048_Prod_RulesEngine_GenerateCostCenter lambda")
        except Exception as e:
            print(e)
    elif status == "FAILED":
        print("OrgUnitCostCenterMapping step function failed")
    elif status == "RUNNING":
        print("OrgUnitCostCenterMapping step function status is "+status)
        print("re-checking status after few mins")
        invoke_lambda()
    else:
        print("OrgUnitCostCenterMapping step function status is "+status)
    # elif status == "RUNNING":
        # print("OrgUnitCostCenterMapping step function is running.waiting for it to complete")
        # time.sleep(120)
        # current_status = stepfn_details('arn:aws:states:us-east-1:136703301440:stateMachine:10048_Prod_Rules_Engine_OrgUnitCostCenterMapping')
        # print("OrgUnitCostCenterMapping status "+current_status)
        # if current_status == "Succeeded":
            # try:
                # print("OrgUnitCostCenterMapping step function succeeded")
                # response = lamb.invoke(FunctionName='10048_Prod_RulesEngine_GenerateCostCenter')
                # print("Invoked 10048_Prod_RulesEngine_GenerateCostCenter lambda")
            # except Exception as e:
                # print(e)
        # else:
            # print(current_status)
invoke_lambda()
    
    