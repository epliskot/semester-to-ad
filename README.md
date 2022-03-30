# semester-to-ad
Semesterregistrerte students from FS to AD 
# semester-to-ad
Denne tjenesten kjører oppdatering av Active Directory (AD) basert data fra FS-api. Denne integrasjonen gjør uttrekk fra FS for studenter, for ønskede stedskoder. F.eks. alle studenter på Handelshøgskolen. Endepunktet som benyttes i Fsapi er semesterregistrering.


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

