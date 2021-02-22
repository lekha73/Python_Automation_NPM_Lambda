import boto3
import requests

client=boto3.client('lambda')

lambdas = ["9514_Dev_HRMicroservicesHub_LeaveEntitlement", "9514_Dev_HRMicroservicesHub_LOAQuestionnaire", "9514_Dev_HRMicroservicesHub_PTOBalance", "9514_Dev_HRMicroservicesHub_UnpaidTime"]
for lamb in lambdas:
    response=client.get_function(
        FunctionName=lamb
    )
    Lambda_URL=response["Code"]["Location"]
    print(Lambda_URL)
    r = requests.get(Lambda_URL, stream=True)
    print(r)
    filename = lamb + ".zip"
    print(filename)
    # open method to open a file on your system and write the contents
    with open(filename, "wb") as fd:
        for chunk in r.iter_content(chunk_size=128):
            fd.write(chunk)

