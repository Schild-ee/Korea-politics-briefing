from __future__ import annotations
from pathlib import Path
import json, os, tempfile
from .models import validate_issue

def load_data(path:Path)->dict:
    if not path.exists(): return {'meta':{},'issues':[]}
    return json.loads(path.read_text(encoding='utf-8'))

def atomic_save(path:Path,payload:dict)->None:
    for i in payload.get('issues',[]): validate_issue(i)
    path.parent.mkdir(parents=True,exist_ok=True)
    fd,tmp=tempfile.mkstemp(prefix=path.name+'.',dir=path.parent)
    try:
        with os.fdopen(fd,'w',encoding='utf-8') as f: json.dump(payload,f,ensure_ascii=False,indent=2)
        os.replace(tmp,path)
    finally:
        if os.path.exists(tmp): os.unlink(tmp)
