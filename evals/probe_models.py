"""List the Gemini models your key can call, and optionally test which ones really work for the
agent (function calling) and what their free-tier daily limit is.

    set -a; source ../.env; set +a                         # from backend/, loads the key (not printed)
    uv run python ../evals/probe_models.py                 # list only: free, uses no quota
    uv run python ../evals/probe_models.py --probe NAME1 NAME2 ...   # 1 tiny request per model

Prints a ready-to-paste GEMINI_MODELS line for the models that passed.
"""

import argparse
import os
import re

from google import genai
from google.genai import types

TOOL = types.Tool(
    function_declarations=[
        types.FunctionDeclaration(
            name="get_weather",
            description="Weather for a city",
            parameters_json_schema={
                "type": "object",
                "properties": {"city": {"type": "string"}},
                "required": ["city"],
            },
        )
    ]
)


def list_models(client: genai.Client) -> list[str]:
    names = []
    for m in client.models.list():
        name = (m.name or "").removeprefix("models/")
        if "generateContent" in (m.supported_actions or []) and name.startswith("gemini"):
            names.append(name)
    return sorted(names)


def probe(client: genai.Client, model: str) -> tuple[bool, str]:
    cfg = types.GenerateContentConfig(
        tools=[TOOL],
        automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
        max_output_tokens=64,
    )
    try:
        r = client.models.generate_content(
            model=model, contents="What is the weather in Paris? Use the tool.", config=cfg
        )
    except Exception as e:
        msg = str(e)
        code = getattr(e, "code", "?")
        if code == 429:
            limit = re.search(r"limit: (\d+)", msg)
            per = "PerDay" in msg
            return (
                False,
                f"quota exhausted now (limit {limit.group(1) if limit else '?'}"
                f"{'/day' if per else '/min'})",
            )
        if code == 404:
            return False, "not available to this key"
        return False, f"error {code}: {msg[:120]}"
    calls = [p for c in r.candidates or [] for p in (c.content.parts or []) if p.function_call]
    return True, "ok, function calling works" if calls else "ok, but did not call the tool"


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--probe", nargs="*", help="model names to test (1 request each)")
    args = ap.parse_args()
    key = os.environ.get("GEMINI_API_KEY")
    if not key:
        raise SystemExit("GEMINI_API_KEY is not set (source your .env first)")
    client = genai.Client(api_key=key)

    if args.probe is None:
        print("models this key can use for generateContent:")
        for n in list_models(client):
            print(f"  {n}")
        print("\nnext: check each one's requests/day at https://aistudio.google.com/rate-limit,")
        print("then test candidates with --probe NAME ...")
        return

    good = []
    for name in args.probe:
        ok, note = probe(client, name)
        print(f"{'PASS' if ok else 'FAIL'}  {name:<40} {note}")
        if ok:
            good.append(name)
    print("\nGEMINI_MODELS=" + ",".join(good))


if __name__ == "__main__":
    main()
