# semester-to-ad
Semesterregistrerte students from FS to AD 
# mq-to-ldap-service

Denne tjenesten kjører oppdatering av Active Directory (AD) basert data fra FS-api

Merk at AD-gruppene "SG-Users-Emp" og "SG-Users-Ass" genereres av et uavhengig powershell-script (ref Anders og Bård). 

## Getting started 

### Prerequisites

#### Docker 

Install Docker. If Docker fails to start, you may need to tweak the permissions setting on the Docker executable file. See [this link](https://stackoverflow.com/a/47168278/9475028) for info.
Under "Shared Drive", make sure to check the "C" drive, to enable mounting folders into the Docker containers. 

### Set up the local environment

Create a file name `local.env` and place it on the project's root. Sample content:

    api_key=changeme

## Start the application

TODO

# Testing

To run unit tests, issue this command:

    for command in down up; do docker-compose.exe -f docker-compose.unittesting.yml $command; done

