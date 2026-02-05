# Agent → Server Report API

## Endpoint
POST /api/agent/report

## Payload schema

```json
{
  "agent": {
    "id": "string",
    "hostname": "string",
    "ip": "string",
    "os": "string",
    "os_version": "string"
  },
  "policy": {
    "name": "string",
    "version": "string"
  },
  "timestamp": "ISO-8601 UTC",
  "results": [
    {
      "check_id": "string",
      "title": "string",
      "status": "pass|fail|error",
      "severity": "low|medium|high|critical",
      "evidence": "string",
      "recommendation": "string|null"
    }
  ]
}
