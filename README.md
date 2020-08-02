# snapshotanalyzer30000
A demo project that manages EC2 volume snaphshots

# About
A Project that uses Boto3 to manage EC2 instances snaphshots. This is part of the course 'Python for Beginners' on ACloud Guru by Robin Norwood. 
I've integrated some extra functions to his code.

# Config
shotty uses the configuration file created by Aws cli e.g.
`aws configure --profile shotty`

# Run
`pipenv run python .\shotty\shotty.py <command> <subcommand> <--profile=AWSProfileName> <--project=PROJECT> `

*command* is instances, volumes, snapshots
*subcommand* depends on each command
*--project* is optional
*--profile* is mandatory. It uses configuration file created by AWS cli 
