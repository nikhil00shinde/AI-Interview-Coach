"""
The ONLY file that talks to a model provider.
"""

import os 
import sys 

from openai import OpenAI


MODEL = os.environ.get("OPENAI_MODEL","gpt-4o-mini")



_client = None 

# First define the client 
def _get_client():
    global _client 
    if _client is None:
        _client = OpenAI()
    return _client 


def stream_chat(messages, temperature=0.7, show=True):
    # 
    stream = _get_client().chat.completions.create(
        model=MODEL,
        messages=messages,
        temperature=temperature,
        stream=True
    )

    pieces = []
    for chunk in stream:
        # Some stream events carry no choices; skip those defensively
        if not chunk.choices:
            continue 
        # When streaming, the new text lives in 'delta', not 'message'
        token = chunk.choices[0].delta.content or ""
        pieces.append(token)
        if show:
            sys.stdout.write(token)
            sys.stdout.flush()
    
    if show:
        print()
    
    return "".join(pieces)
