# Python_Automation_NPM_Lambda
prerequisite - AWS CLI | Python
Before running scripts in windows install AWS cli https://docs.aws.amazon.com/cli/latest/userguide/install-cliv2-windows.html
Add AWS keys using "aws configure" cmd.
Install python 3 https://www.python.org/downloads/windows/
cmd prompt cmd: python filename


test event data for s3 file processing:
{
  "Records": [
    {
      "s3": {
        "bucket": {
          "name": "9514-loaaccelerator-prod",
          "arn": "arn:aws:s3:::9514-loaaccelerator-prod"
        },
        "object": {
          "key": "PTOAccrued/MRDR.PeopleAccrualsPTO__20210219_010246.csv"
        }
      }
    }
  ]
}
