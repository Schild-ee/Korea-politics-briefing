from __future__ import annotations
from datetime import datetime
from .models import validate_issue

def verify_issue(issue:dict)->dict:
    validate_issue(issue)
    for k in ('occurredAt','updatedAt'):
        datetime.fromisoformat(issue[k])
    if len(issue.get('summary',''))>1200: issue['summary']=issue['summary'][:1200]
    if not issue.get('sources'): raise ValueError('source required')
    return issue
