# Incident Lifecycle

Ops-Sentinel detects failures in monitored services and creates incidents with trigger data, evidence and resolution information.

## 1. Detection

A monitor periodically checks a configured service URL.

The check validates:
- HTTP status code
- response availability
- configured expected status

## 2. Trigger

If the observed result does not match the expected result given in the monitor, Ops-Sentinel creates a trigger containing:
- expected status
- observed status
- failed attempts
- trigger type

## 3. Evidence

Each incident stores evidence such as:
- response time
- CPU usage
- memory usage
- error message when available

## 4. Incident creation

An incident is created with:
- affected service
- severity
- source
- summary
- status

## 5. Resolution

When the problem is fixed, the incident can be updated with:
- action taken
- resolution date
- action result

## Goal

The objective is to simulate a basic incident management workflow similar to real DevOps/SRE environments.