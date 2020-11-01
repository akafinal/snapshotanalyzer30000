# snapshotanalyzer30000
A demo project that manages EC2 volume snapshots

# About
A Project that uses Boto3 to manage EC2 instances snaphshots. This is part of the course 'Python for Beginners' on ACloud Guru (https://acloud.guru/learn/python-for-beginners) by Robin Norwood(https://www.linkedin.com/in/robin-norwood/). 
I've integrated some extra functions to his code:

1. Add 'age' parameter to the 'snapshot' command that takes an age in days and only snapshots volumes whose last successful snapshot is older than that many days, e.g. “shotty instances snapshot —age 7 —project Valkyrie” 

2. Add an “instance” argument to the appropriate commands, so they only target one instance. e.g. “shotty volumes list —instance=i-0123456789abcdef” 

3. After a snapshot, only start instances that were running before the snapshot was taken.

# Config
shotty uses the configuration file created by Aws cli e.g.
`aws configure --profile shotty`

# Run
`pipenv run python .\shotty\shotty.py <command> <subcommand> <--profile=AWSProfileName> <--project=PROJECT> `

*command* is instances, volumes, snapshots

*subcommand* depends on each command

*--project* is optional

*--profile* is mandatory. It uses the configuration files created by AWS cli, e.g. shotty
