import boto3
import click

session = boto3.Session(profile_name='shotty')
ec2 = session.resource('ec2')
def filter_instances(project):
    'Filter EC2 instances'
    instances = []
    if project:
        filters = [{'Name':'tag:Project', 'Values':[project]}]
        instances = ec2.instances.filter(Filters=filters)
    else:
        instances = ec2.instances.all()

    return instances

@click.group()
def cli():
    'Commands for instances'

@cli.command('start')
@click.option('--project', default=None, help='Start instances by project tag, e.g. -project = <project name>')
def start_instances(project):
    'Start EC2 instances'
    instances = filter_instances(project)
    for i in instances:
        print('Starting {0}...'.format(i.id) )
        i.start()
    return

@cli.command('stop')
@click.option('--project', default=None, help='Stop instances by project tag, e.g. -project = <project name>')
def stop_instances(project):
    'Stop EC2 instances'
    instances = filter_instances(project)
    for i in instances:
        print('Stopping {0}...'.format(i.id) )
        i.stop()
    return

@cli.command('list')
@click.option('--project', default=None, help='List instances by project tag, e.g. -project = <project name>')
def list_instances(project):
    'List EC2 instances'
    instances = filter_instances(project)
    for i in instances:
        tags = {t['Key']:t['Value'] for t in i.tags or {}}
        print(', '.join((
        i.id,
        i.instance_type,
        i.placement['AvailabilityZone'],
        i.state['Name'],
        i.public_dns_name,
        tags.get('Project', '<no project>')
    )))

    return

if __name__ == '__main__':
    cli()
