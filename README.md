# snapshotanalyzer30000
A demo project that manages EC2 volume snaphshots

# About
A Project that uses Boto3 to manage EC2 instances snaphshots

# Config
shotty uses the configuration file created by Aws cli e.g.
`aws configure --profile shotty`

# Run
`pipenv run python .\shotty\shotty.py <command> <subcommand> <--project=PROJECT> `
*command* is instances, volumes, snapshots
*subcommand* depends on each command
*--project* is optional
