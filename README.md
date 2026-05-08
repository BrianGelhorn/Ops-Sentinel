# Ops-Sentinel

## Overview

Ops-Sentinel is a backend API project focused on service monitoring and incident management.

The system periodically checks configured services, detects failures, stores incident data and collects evidence related to each failure. The goal is to simulate a basic DevOps/SRE workflow involving monitoring, incident creation, evidence collection and resolution tracking.

## Features

- Service health monitoring
- Automatic incident creation with relevant information for troubleshooting when a monitored service fails
- Evidence collection for each incident
- Incident status tracking
- Resolution information storage
- PostgreSQL database integration
- Docker-based local environment

## Documentation

- [Incident Lifecycle](docs/incident-lifecycle.md)