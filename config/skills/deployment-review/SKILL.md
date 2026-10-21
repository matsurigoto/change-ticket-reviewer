---
name: deployment-review
description: Department-manager review of a change ticket's deployment readiness.
---
# Deployment review skill
Approve only if the ticket clearly covers:
1. **Monitoring** – what metrics/alerts watch the release, who is on call.
2. **Deployment process** – ordered steps, window, tooling, owner.
3. **Deployment method** – e.g. rolling/blue-green/canary; impact on customers.
4. **Verification** – concrete post-deploy checks and success criteria.
5. **Rollback** – trigger conditions and tested steps.
Reject with one reason per missing or vague item.
