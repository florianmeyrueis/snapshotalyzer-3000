# snapshotalyzer-3000
demo project for AWS EC2 snapshot management


# About

This is a demo project, and uses boto3 to manages AWS EC2 instance snapshots

## configuring

shotty uses  the configuration file created by the  AWS cli e.g.


`aws  confifure --profile shotty`

## Running

`pipenv run python shotty/shotty.py <command> <subcommand> --project="<project_name>"`

*command* is instances,volumes,snapshots
*subcommand* depends on command
*project_name* is a the value of tag Project 
