# iriscast-pipeline

This is a set of scripts and config files I used during the IRISCAST project. A project to collect energy usage metrics from multiple HPC facilities

Essentially I set up numerous data pipelines to collect energy usage information and ingest it into OpenSearch

The scripts include

- Tests for PowerTOP to collect energy usage information at the process-level
- Tests for Nvidia SMI to collect GPU energy usage information 
- Filebeats and Logstash configuration files for reading csvs of power metrics from different sites/facilities (csvs not included) 


# Run Opensearch

```
cd ~/<repo>/opensearch
docker-compose up
```
change the docker-compose script to point to directories with correct csv files


# Run Logstash and Filebeats
```
cd ~/<repo>
docker-compose up
```
