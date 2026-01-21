#!/usr/bin/env python3
"""AI agent scaffold that uses OpenRouter SDK as primary and a local fallback.

This is a safe, minimal scaffold. The real implementation would include
prompt templates, safety checks, and offline model integration.
"""
import os
import logging
import argparse

logger = logging.getLogger('ai_agent')

OPENROUTER_API_KEY_ENV = 'OPENROUTER_API_KEY'


def call_openrouter(prompt: str):
    # Try to import openrouter SDK; if not present, raise
    try:
        import openrouter
        client = openrouter.OpenRouter(api_key=os.environ.get(OPENROUTER_API_KEY_ENV))
        resp = client.complete(prompt=prompt)
        return resp.get('text')
    except Exception as e:
        logger.warning('OpenRouter SDK unavailable or failed: %s', e)
        raise


def local_fallback(prompt: str):
    # Very small local fallback (placeholder)
    return f"(local) Echo: {prompt[:200]}"


def respond(prompt: str):
    # Try primary then fallback
    if os.environ.get(OPENROUTER_API_KEY_ENV):
        try:
            return call_openrouter(prompt)
        except Exception:
            logger.info('Falling back to local model')
    return local_fallback(prompt)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--prompt', required=True)
    args = parser.parse_args()
    print(respond(args.prompt))
