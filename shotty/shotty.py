import boto3
session = boto3.Session(profile_name='shotty')
ec2 = session.resource('ec2')
instances = ec2.instances.all()

if __name__ == '__main__':
    for i in instances:
        print(i)
