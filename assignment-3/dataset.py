"""
Dataset for Assignment 3: Resumable Agent with Basic Self-Check.
Contains 4 technical postmortem / incident reports to process one by one.
"""

from typing import List, Dict

INCIDENT_REPORTS: List[Dict[str, str]] = [
    {
        "id": "INC-101",
        "title": "Auth Service JWT Secret Rotation Outage",
        "raw_text": (
            "At 14:00 UTC, an automated secret rotation pipeline updated the signing key for JWT tokens in production. "
            "However, the verification service cached the public key with a 24-hour TTL without subscribing to rotation webhooks. "
            "This caused all subsequent user API requests to fail authentication with HTTP 401 Unauthorized. "
            "Downtime: 22 minutes. Root cause: Desynchronized cache invalidation between token signer and token verifier. "
            "Remediation: Implement dual-key verification window and pub/sub rotation event listener."
        )
    },
    {
        "id": "INC-102",
        "title": "Postgres Connection Pool Exhaustion on Payments API",
        "raw_text": (
            "At 09:15 UTC, a sudden flash-sale event drove a 6x surge in checkout requests. "
            "Each checkout handler acquired a database connection prior to calling an external payment gateway with a 30s timeout. "
            "Slow gateway responses caused all 150 database connections in the PgBouncer pool to be held open in idle-in-transaction state. "
            "Downtime: 45 minutes. Root cause: Premature connection acquisition across slow external network boundaries. "
            "Remediation: Refactor checkout workflow to defer database transaction until external gateway authorization returns."
        )
    },
    {
        "id": "INC-103",
        "title": "Redis Cluster Eviction Storm Causing Cache Stampede",
        "raw_text": (
            "At 18:30 UTC, memory utilization on primary Redis node redis-01 exceeded 95% maxmemory threshold. "
            "The eviction policy was set to volatile-lru, but newly written session keys lacked TTL expirations, triggering continuous key scanning. "
            "Node CPU spiked to 100%, causing cluster failover timeout and dropping cache hit ratio from 94% to 8%. "
            "Downtime: 38 minutes. Root cause: Unbounded keys written without TTLs causing CPU-blocking eviction cycles. "
            "Remediation: Enforce strict TTL linting in Redis client and switch to allkeys-lru with active defragmentation."
        )
    },
    {
        "id": "INC-104",
        "title": "S3 Bucket Permission Policy Misconfiguration in Asset Ingestion",
        "raw_text": (
            "At 03:00 UTC, a Terraform deployment updated IAM roles for the media processing worker cluster. "
            "A missing 's3:PutObjectTagging' action in the least-privilege IAM policy caused ingestion uploads to fail silent validation. "
            "Asset processing queues backed up to 85,000 pending items. "
            "Downtime: 15 minutes. Root cause: Incomplete IAM permissions block applied during policy refactor. "
            "Remediation: Add automated IAM policy simulation tests to pre-merge CI/CD pipelines."
        )
    }
]
