# BEACON COMPUTING INITIATIVE
**Developer Seal:** CJB-DEV-2026

# BCI Nexus Architecture

## Core Components

- BCILock: authentication and endpoint enforcement.
- BCIBot: containerized Ollama inference and constrained agents.
- BCISentinel: network telemetry and observation.

## Integration Contracts

- Evidence is read-only unless a separately authorized executor is used.
- Model output is never an authorization token.
- Network scans require an explicitly approved scope.
- Authentication and enforcement remain outside model control.
- Events are auditable and verifiable.

## Initial Inference Endpoint

- Ollama model: bci-secops:unified
- Docker endpoint: 127.0.0.1:11435
- Host fallback: 127.0.0.1:11434

These are development configuration references,
not production deployment guarantees.
