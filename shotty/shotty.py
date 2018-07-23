import boto3
import botocore
import click

#session = boto3.Session(profile_name='shotty')
#ec2 = session.resource('ec2')



def filter_instances(project):
    instances =[]

    if project:
        filter = [{'Name':'tag:Project', 'Values':[project]}]
        instances = ec2.instances.filter(Filters=filter)
    else:
        instances = ec2.instances.all()
    
    return instances

def has_pending_snapshot(volume):
    snapshots=list(volume.snapshots.all())
    return snapshots and snapshots[0].state == 'pending'



@click.group()
@click.option('--profile', default='shotty',  help="Allow different aws profile")
def cli(profile):
    " Shotty manager cli "
    global ec2
    try:
        session = boto3.Session(profile_name=profile)
        ec2 = session.resource('ec2')
    except botocore.exceptions.ProfileNotFound as e:
        print("Connection not possible : {0}".format(str(e)))
        quit()        

    return 

@cli.group('snapshots')
def snapshots():
    """ Command for snapshots """

@snapshots.command('list')
@click.option('--project', default=None,  help="Only snapshots for project (tag Project:<name>)")
@click.option('--all', 'list_all', default=None, is_flag=True, help="List all snapshots for each volume, not just the most recent")
def list_snapshots(project,list_all):
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

                if s.state == 'completed' and not list_all: 
                    break

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
@click.option('--force', 'force', default=None, is_flag=True, help="Required to stop all instances")
def stop_instances(project,force):
    "Stop EC2 instances"

    instances = filter_instances(project)

    if project or force:
        for i in instances:
            print('stopping instances {0}'.format(i.id))
            try: 
                i.stop()
            except botocore.exceptions.ClientError as e:
                print("Could not stop {0}. ".format(i.id) + str(e) ) 
                continue
    else : 
        print("Can't stop all instances without a force option. Use project!")

    return

@instances.command('start')
@click.option('--project', default=None,  help="Only instances for project (tag Project:<name>)")
@click.option('--force', 'force', default=None, is_flag=True, help="Required to start all instances")
def start_instances(project,force):
    "Start EC2 instances"

    instances = filter_instances(project)

    if project or force: 
        for i in instances:
            print('starting instances {0}'.format(i.id))
            try:
                i.start()
            except botocore.exceptions.ClientError as e:
                print("Could not start {0}. ".format(i.id) + str(e) )
                continue
    else :
        print("Can't start all instances without a force option. Use project!")
    return

@instances.command('reboot')
@click.option('--project', default=None,  help="Only instances for project (tag Project:<name>)")
@click.option('--force', 'force', default=None, is_flag=True, help="Required to stop all instances")
def reboot_instances(project,force):
    "Reboot EC2 instances"

    instances = filter_instances(project)

    if project or force:
        for i in instances:
            print('Rebooting instance {0}'.format(i.id))
            try:
                i.reboot()
            except botocore.exceptions.ClientError as e:
                print("Could not reboot {0}. ".format(i.id) + str(e) )
                continue
    else: 
        print("Can't reboot all instances without a force option. Use project!")
    return

@instances.command('snapshot',help="create snapshot for instances")
@click.option('--project', default=None,  help="Only instances for project (tag Project:<name>)")
@click.option('--force', 'force', default=None, is_flag=True, help="Required to stop all instances")
def create_snapshot(project,force):
    "Create Snapshots for ec2 instances"

    instances = filter_instances(project)
    if project or force:
        for i in instances: 
            print("Stopping instance {0}".format(i.id))

            i.stop()
            i.wait_until_stopped()

            for v in i.volumes.all():
                if has_pending_snapshot(v):
                    print("Skipping {0}, snapshot already in progree".format(v.id))
                    continue
                print("Creating snapshot for {0}".format(v.id))
                v.create_snapshot(Description="Snapshot created by Snapshotalyzer30000")

            print("Starting instance {0}".format(i.id))

            i.start()
            i.wait_until_running()

        print("Job's done!")
    else: 
        print("Can't snapshot all instances without a force option. Use project!")
    return

    
if __name__ == '__main__':
    cli()
    

