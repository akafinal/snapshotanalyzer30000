import boto3
import botocore
import click
import datetime
from datetime import datetime, timezone

def filter_project_instances(project):
    'Filter EC2 instances'
    instances = []
    if project:
        filters = [{'Name':'tag:Project', 'Values':[project]}]
        instances = ec2.instances.filter(Filters=filters)
    else:
        instances = ec2.instances.all()

    return instances
def filter_instanceId_instances(instance_id):
    'Filter EC2 instances by ID'
    instances = []
    filters = [{'Name':'instance-id', 'Values':[instance_id]}]
    if instance_id:
        instances = ec2.instances.filter(Filters=filters)
    else:
        instances = ec2.instances.all()
    return instances

def has_no_snapshots(volume):
    snapshots = volume.snapshots.all()
    return snapshots

def has_pending_snapshots(volume):
    snapshots = list(volume.snapshots.all())
    return snapshots[0].state == 'pending'

def calculate_snapshots_age(volume,age):
    snapshots = list(volume.snapshots.all())
    now = datetime.now(timezone.utc)
    diff = now - snapshots[0].start_time
    mins = diff.seconds/60
    return mins >= float(age)

@click.group()
@click.option('--profile', default = None, help='Select the AWS profile')
def cli(profile):
    "Shotty manages snapshots"
    session = boto3.Session(profile_name=profile)
    ec2_cli = session.resource('ec2')
    global ec2
    ec2 = ec2_cli

@cli.group('volumes')
def volumes():
    'Commands for volumes'
@volumes.command('list')
@click.option('--instance', default = None,
help = 'List volume(s) of a specific instance')
@click.option('--project', default=None, help='List volumes by project tag')
def list_volumes(project, instance):
    'List EC2 volumes'
    if project:
        instances = filter_project_instances(project)
    else:
        instances = filter_instanceId_instances(instance)

    for i in instances:
        for v in i.volumes.all():
            print(', '.join((
            v.id,
            i.id,
            v.state,
            str(v.size) + 'GiB(s)',
            v.encrypted and 'Encrypted' or 'Not Encrypted'
            )))
    return



@cli.group('instances')
def instances():
    'Commands for instances'


@instances.command('start')
@click.option('--instance', default = None,
help = 'Start instances by instance-id')
@click.option('--force', is_flag=True, default=False,
help = 'Force start all instances')
@click.option('--project', default=None,
help='Start instances by project tag, e.g. --project = <project name>')
def start_instances(project,force,instance):
    'Start EC2 instances'
    if not force and not project and not instance:
        print('--force is needed when performing tasks on all instances')
        return
    elif project:
        instances = filter_project_instances(project)
    else:
        instances = filter_instanceId_instances(instance)

    for i in instances:

            print('Starting {0}...'.format(i.id) )
            try:
                i.start()
            except botocore.exceptions.ClientError as e:
                print('Unable to start {0}. '.format(i.id) + str(e))

    return

@instances.command('stop')
@click.option('--instance', default=None,
help = 'Stop instances by instance-id')
@click.option('--force', is_flag=True, default= False,
help = 'Enable stopping all instances, use with caution')
@click.option('--project', default=None,
help='Stop instances by project tag, e.g. -project = <project name>')

def stop_instances(project,force,instance):
    'Stop EC2 instances'
    if not force and not project and not instance:
        print('--force is needed when performing tasks on all instances')
        return
    elif project:
        instances = filter_project_instances(project)
    else:
        instances = filter_instanceId_instances(instance)

    for i in instances:
        print('Stopping {0}...'.format(i.id) )
        try:
            i.stop()
        except botocore.exceptions.ClientError as e:
            print('Unable to stop {0}. '.format(i.id) + str(e))
    return

@instances.command('list')
@click.option('--project', default=None,
help='List instances by project tag, e.g. -project = <project name>')
def list_instances(project):
    'List EC2 instances'
    instances = filter_project_instances(project)
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

@instances.command('snapshot', help = 'Create snapshots of all volumes')
@click.option('--instance', default=None,
help = 'Create snapshots for one instance')
@click.option('--force', is_flag=True, default = False,
help = 'Force snapshotting all existing volumes')
@click.option('--project', default = None,
help='create snapshots by project tag, e.g. -project = <project name>')
@click.option('--age', default=None,
help='Only take a new snapshot based on the age of the most recent snapshot')

def create_snapshots(project, force, instance, age):
    'Create snapshots for EC2 instances'
    if not force and not project and not instance:
        print('--force is needed when performing tasks on all instances')
        return
    elif project:
        instances = filter_project_instances(project)
    else:
        instances = filter_instanceId_instances(instance)

    inst = []
    for i in instances:
        if i.state['Name'] == 'running': inst.append(i)

        for v in i.volumes.all():
            if has_no_snapshots(v):
                print('Stopping {0}'.format(i.id))
                i.stop()
                i.wait_until_stopped()
                print('Creating a snapshot of {0}...'.format(v.id))
                v.create_snapshot(Description = 'Created by SnapshotAlyzer30000')
            elif has_pending_snapshots(v):
                print('Skipping {0}, another snapshot is in progress'.format(v.id))
            elif calculate_snapshots_age(v,age):
                print('Stopping {0}'.format(i.id))
                i.stop()
                i.wait_until_stopped()
                try:
                    print('Creating a snapshot of {0}...'.format(v.id))
                    v.create_snapshot(Description = 'Created by SnapshotAlyzer30000')
                except botocore.exceptions.ClientError as e:
                    print('Unable to snapshot {0}. '.format(v.id) + str(e))
            else:
                print('The most recent snapshot is not {0} mins old'.format(age))

    for i in inst:
         print('Starting instances that were running before {0}'.format(i.id))
         i.start()
        #i.wait_until_running()
    print("Job's done!")
    return

@instances.command('reboot', help = 'Reboot EC2 instances')
@click.option('--project', default = None,
help = 'Reboot instances by project tag')
@click.option('--force', default = False, is_flag = True,
help = 'Force rebooting all instances')
@click.option('--instance', default = None,
help='Reboot a specific instance, e.g. --instance <instance_id>')
def reboot_instances(project,force,instance):
    if not force and not project and not instance:
        print('--force is needed when performing tasks on all instances')
        return
    elif project:
        instances = filter_project_instances(project)
    else:
        instances = filter_instanceId_instances(instance)

    for i in instances:
        print('Rebooting {0}...'.format(i.id))
        try:
            i.reboot()
        except botocore.exceptions.ClientError as e:
            print('Unable to reboot {0}. '.format(i.id) + str(e))
    return

@cli.group('snapshots')
def snapshots():
    """Commands for snapshots"""

@snapshots.command('list')
@click.option('--all', 'list_all', default = False, is_flag=True,
help = 'List all snapshots, not only the most recent one', show_default=True)
@click.option('--project', default = None,
help='List snapshots by project tag, e.g. -project = <project name>')
@click.option('--instance', default = None,
help='List snapshots from one instance')
def list_snapshots(project,list_all,instance):
    'List snapshots'
    if project:
        instances = filter_project_instances(project)
    else:
        instances = filter_instanceId_instances(instance)

    for i in instances:
        for v in i.volumes.all():
            for s in v.snapshots.all():
                print(', '. join((
                    s.id,
                    v.id,
                    i.id,
                    s.state,
                    s.progress,
                    s.start_time.strftime('%c')
                )))
                if s.state == 'completed' and not list_all: break

    return

if __name__ == '__main__':
    cli()
