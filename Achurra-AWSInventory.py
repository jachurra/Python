#!/usr/bin/env python3.6
# By Juan Achurra
# Head of Cloud Support for Hertz Global
# Role based all organizational dynamic accounts instance inventory 
# Joshua: Shall we play a game?

import boto3
import csv
import os
import datetime
import ast
os.system('date +%Y-%m-%d')
sts = boto3.client('sts')
sns = boto3.client('sns')
mycomm = "aws organizations list-accounts --profile OrgRead --output text  --query 'Accounts[?Status==`ACTIVE`][Id,Name]' > accounts.csv"
print(mycomm)
os.system (mycomm)
with open('accounts.csv') as csv_file:
    csv_reader = csv.reader(csv_file, delimiter='\t')
    act = ''
    accounts =''
    line_count = 0
    for row in csv_reader:
         act = "'"+row[0]+"'"+ ':'+"'"+row[1] +"'"
         if line_count == 0:
            accounts = accounts + act
            line_count += 1
         else:
            accounts = accounts +","+ act
            line_count += 1
accounts = ast.literal_eval("{" + accounts + "}")

print(accounts)
myregion = 'us-east-1'  #raw_input("Region to Use: ")
with open('awsinstances.csv', mode='w') as csv_file:
    writer = csv.writer(csv_file)
    writer.writerow(['InstanceID', 'Instance Type', 'Host', 'Region', 'State', 'ImageID', 'Valid', 'RootDeviceName', 'ImageName','ImageDesc','VpcId', 'PrvIPadd', 'PublicIPAdd', 'Platform', 'AZ', 'PatchGrp', 'CostCenter','Account'])
    miss = []            
    for id, account2 in accounts.items():
        
            if account2 != "Joshua":
                account = account2
                arn = 'arn:aws:iam::' +id+':role/your-role'
                # Assume Role
                print(arn)
                try:
                    response = sts.assume_role(RoleArn=arn, RoleSessionName='your-role')
                    # Retrieve temp credentials
                    AccessKey = response['Credentials']['AccessKeyId']
                    SecretKey = response['Credentials']['SecretAccessKey']
                    SessionToken = response['Credentials']['SessionToken']
                    # Start session
                    session = boto3.session.Session(
                        aws_access_key_id=AccessKey,
                        aws_secret_access_key=SecretKey,
                        aws_session_token=SessionToken,
                        region_name='us-east-1'
                    )
                except:
                    print('Access Role is missing from account ' + id + ':' + account2)
                    misslog = 'Access Role is missing from account ' + id + ':' + account2
                    miss.append(misslog)
                    continue
            def generate(key, value): 
                """
                Creates a nicely formatted Key(Value) item for output
                """
                return '{}="{}"'.format(key, value)
            
            client = session.client('ec2', region_name=myregion, verify=False)
            
        
            ec2_regions = [region['RegionName'] for region in client.describe_regions()['Regions']]
        
            for region in ec2_regions:
                conn = session.resource('ec2', region_name=region, verify=False)
                instances = conn.instances.filter()
                
                for instance in instances:
                    state = instance.state["Name"]
                    imageid = instance.image_id
                    images = conn.Image(imageid)
                    myflag = "Valid"
                    try: 
                        print(images.root_device_name)
                        print(images.name)
                        print(images.description)
                    except:
                        # use a valid AMI
                        images = conn.Image('ami-1234567890123456')
                        myflag="Null"
                    
                    AZ = instance.placement["AvailabilityZone"]
                    tags = instance.tags
                    try:
                        names = ','.join(str(a) for a in [tag.get('Value') for tag in tags if tag.get('Key') == 'Name'])
                    except:
                        names = "Unknown"
                    try:
                        PatchGrp = ','.join(str(a) for a in [tag.get('Value') for tag in tags if tag.get('Key') == 'Patch Group'])
                    except:
                        PatchGrp = "Unknown"
                    try:
                        CostctrPrj = ','.join(str(a) for a in [tag.get('Value') for tag in tags if tag.get('Key') == 'CostCenter-Project'])
                    except:
                        CostctrPrj = "Unknown"
                    myprivate=str(instance.private_ip_address)
                    mypublic = str(instance.public_ip_address)
                    try:
                        ImgRoot = images.root_device_name
                    except:
                        ImgRoot = "Unknown"
                    try:
                        ImgName = images.name
                    except:
                        ImgName = "Unknown"
                    try:
                        ImgDesc = images.description
                    except:
                        ImgDesc = "Unknown"
                    if instance.platform == 'windows':
                        myplat='Windows'
                    else:
                        myplat = 'Non-Windows'
                    print (instance.id)
                    print (instance.instance_type)
                    print (names)
                    print (region)
                    print (state) 
                    print (imageid)
                    print (myflag)
                    print(ImgRoot)
                    print(ImgName)
                    print(ImgDesc)
                    print(instance.vpc_id)
                    print(instance.private_ip_address)
                    print(instance.public_ip_address)
                    print(myplat)
                    print(AZ)
                    print(PatchGrp)
                    print(CostctrPrj)
                    print ("******************************************** INSTANCES ******************************************************")
                    mylist = instance.id, instance.instance_type, names, region, state, imageid, myflag, ImgRoot,ImgName,ImgDesc, instance.vpc_id, myprivate, mypublic, myplat, AZ, PatchGrp,CostctrPrj, account
                    
                    writer.writerow(mylist)
print (miss)
with open('missing.csv', mode='w') as csv_file_write:
        writer = csv.writer(csv_file_write)
        writer.writerow(miss)

