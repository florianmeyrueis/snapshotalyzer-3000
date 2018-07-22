import boto3
import click

session = boto3.Session(profile_name='shotty')
ec2= session.resource('ec2')

def filter_instances(project):
    instances =[]

    if project:
        filter = [{'Name':'tag:Project', 'Values':[project]}]
        instances = ec2.instances.filter(Filters=filter)
    else:
        instances = ec2.instances.all()
    
    return instances

@click.group()
def cli():
    """ Shotty manager cli """

@cli.group('snapshots')
def snapshots():
    """ Command for snapshots """

@snapshots.command('list')
@click.option('--project', default=None,  help="Only snapshots for project (tag Project:<name>)")
def list_snapshots(project):
    "List EC2 Snapshots"

    instances = filter_instances(project)

    for i in instances:
        for v in i.volumes.all():
            for s in v.snapshots.all():
                print(" ,".join((
                s.id,
                i.id,
                v.id,
                s.state,
                s.progress,
                s.start_time.strftime("%c")
                )))
    return

@cli.group('volumes')
def volumes():
    """ Command for volumes """


@volumes.command('list')
@click.option('--project', default=None,  help="Only volumes for project (tag Project:<name>)")
def list_volumes(project):
    "List EC2 Volumes"

    instances = filter_instances(project)

    for i in instances:
        for v in i.volumes.all(): 
            print(" ,".join((
            v.id,
            i.id,
            v.state,
            str(v.size) + " Gb",
            v.encrypted and "Encrypted" or "Not Encrypted"
            )))

    return

@cli.group('instances')
def instances():
    """ Command for instances """


@instances.command('list')
@click.option('--project', default=None,  help="Only instances for project (tag Project:<name>)")
def list_instances(project):
    "List EC2 Instances"

    instances = filter_instances(project)

    for i in instances:
        tags = { t['Key']: t['Value'] for t in i.tags or [] }
        print(', '.join((
            i.id,
            i.instance_type,
            i.placement['AvailabilityZone'],
            i.state['Name'],
            i.public_dns_name,
            tags.get('Project','<No project>')
            )))

    return

@instances.command('stop')
@click.option('--project', default=None,  help="Only instances for project (tag Project:<name>)")
def stop_instances(project):
    "Stop EC2 instances"

    instances = filter_instances(project)

    for i in instances:
        print('stopping instances {0}'.format(i.id))
        i.stop()

    return

@instances.command('start')
@click.option('--project', default=None,  help="Only instances for project (tag Project:<name>)")
def start_instances(project):
    "Start EC2 instances"

    instances = filter_instances(project)

    for i in instances:
        print('starting instances {0}'.format(i.id))
        i.start()

    return

@instances.command('snapshot',help="create snapshot for instances")
@click.option('--project', default=None,  help="Only instances for project (tag Project:<name>)")
def create_snapshot(project):
    "Create Snapshots for ec2 instances"

    instances = filter_instances(project)

    for i in instances: 
        for v in i.volumes.al():
            print("Creating snapshot for {0}".format(v.id))
            v.create_snapshot(Description="Snapshot created by Snapshotalyzer30000")

    return

    
if __name__ == '__main__':
    cli()

