from __future__ import annotations
import json, os, re
from .config import OPENAI_API_KEY, OPENAI_MODEL

def fallback_summary(title:str,text:str)->dict:
    clean=' '.join(re.sub(r'\s+',' ',text or '').split())
    sentences=re.split(r'(?<=[.!?다요])\s+',clean)
    useful=[s for s in sentences if len(s)>=25][:3]
    summary=' '.join(useful)[:650] or title
    return {'title':title,'summary':summary,'background':'','significance':'','positions':[],'unverifiedDetails':[],'nextSchedule':''}

def ai_summary(title:str,text:str,category:str)->dict:
    if not OPENAI_API_KEY: return fallback_summary(title,text)
    try:
        from openai import OpenAI
        client=OpenAI(api_key=OPENAI_API_KEY)
        prompt=(f"다음 공식자료 또는 뉴스 후보를 사실에만 근거해 한국어 JSON으로 요약하라. 원문에 없는 정보를 추가하지 말라.\n"
                f"분류: {category}\n제목: {title}\n본문: {text[:9000]}\n"
                f"반환 키: title, summary, background, significance, positions, unverifiedDetails, nextSchedule. summary는 2~4문장, background/significance는 각 1~3문장.")
        resp=client.responses.create(model=OPENAI_MODEL,input=prompt)
        raw=resp.output_text.strip(); raw=re.sub(r'^```json|```$','',raw).strip()
        obj=json.loads(raw)
        if not obj.get('summary'): raise ValueError('empty summary')
        return {**fallback_summary(title,text),**obj}
    except Exception:
        return fallback_summary(title,text)
