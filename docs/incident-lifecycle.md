# Incident Lifecycle

Ops-Sentinel models a simple incident management workflow for monitored HTTP services. A monitor checks a configured service, compares the observed result against the expected result, and creates or updates incident data when the check fails.

## 1. Monitor configuration

A monitor defines:

- a human-readable title;
- monitor type, currently `http`;
- check interval in seconds;
- target URL;
- expected HTTP status code.

The scheduler periodically selects monitors that are due to run and starts a check for each one.

## 2. Detection

During an HTTP check, Ops-Sentinel validates:

- whether the request completed;
- the observed HTTP status code;
- whether the observed status matches the configured expected status.

A passing check does not create a new incident.

A failing check can be classified as one of several failure types, for example:

- timeout error;
- connection error;
- network error;
- protocol error;
- redirect error;
- client error;
- server error;
- unexpected status error.

## 3. Trigger

When the observed result does not match the expected result, the incident stores trigger data:

- trigger type;
- expected status;
- observed status when available;
- failed attempt count.

If the same monitor keeps failing with the same incident type, Ops-Sentinel increments the failed attempt count instead of creating a duplicate incident for the same failure type.

## 4. Evidence

Each incident stores operational evidence to help with review and troubleshooting:

- response time in milliseconds when available;
- CPU usage percentage;
- memory usage percentage;
- error message.

This evidence is meant to give context to the failure, not to replace manual investigation.

## 5. Incident creation

An incident contains:

- affected monitor or service;
- incident title;
- incident type;
- severity;
- summary;
- source;
- trigger data;
- evidence;
- resolution details.

New incidents start with status `open`.

## 6. Manual acknowledgement and resolution

Incident resolution is manual by design.

Ops-Sentinel does not mark an incident as `resolved` automatically just because a later monitor check succeeds. A successful check only confirms that the service responded correctly at that moment. For intermittent failures, automatic resolution could hide a real issue before the root cause is understood.

An operator can update the incident when there is enough context to do so. Resolution details can include:

- action taken;
- action result;
- resolution date.

Supported statuses are:

- `open`;
- `acknowledged`;
- `resolved`.

## 7. Goal

The goal is to simulate a practical DevOps/SRE workflow:

1. detect a service problem;
2. create an incident;
3. collect trigger and evidence data;
4. let an operator investigate;
5. close the incident manually when the issue is understood or resolved.
