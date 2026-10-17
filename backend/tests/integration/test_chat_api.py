import dataclasses
import json
import re
import uuid
from typing import Any

from fastapi.testclient import TestClient

from app.agent.llm import FakeLLM, LLMResponse, Message, call, say
from app.services.gemini import LLMUnavailable
from app.worker.runner import process_one
from tests.helpers import make_pdf, seed

PW = "a-long-enough-password"


def signup(c: TestClient) -> tuple[dict[str, str], str]:
    r = c.post(
        "/auth/signup",
        json={"org_name": "Acme", "email": f"u-{uuid.uuid4().hex[:8]}@example.com", "password": PW},
    )
    h = {"Authorization": f"Bearer {r.json()['access_token']}"}
    return h, c.get("/auth/me", headers=h).json()["org_id"]


def new_conv(c: TestClient, h: dict[str, str]) -> str:
    r = c.post("/conversations", headers=h, json={})
    assert r.status_code == 201, r.text
    return str(r.json()["id"])


def parse_sse(body: str) -> list[tuple[str, dict[str, Any]]]:
    events = []
    for block in body.strip().split("\n\n"):
        lines = dict(line.split(": ", 1) for line in block.splitlines())
        events.append((lines["event"], json.loads(lines["data"])))
    return events


def chat(c: TestClient, h: dict[str, str], conv: str, content: str = "hello?"):  # type: ignore[no-untyped-def]
    return c.post(f"/chat/{conv}/messages", headers=h, json={"content": content})


def set_llm(c: TestClient, llm: Any) -> None:
    c.app.state.agent_deps = dataclasses.replace(c.app.state.agent_deps, llm=llm)  # type: ignore[attr-defined]


async def _ingest(deps: Any, org: str, text: str) -> None:
    await seed(deps, uuid.UUID(org), make_pdf([text]), "contract", "acme-contract.pdf")
    while await process_one(deps, "w"):
        pass


def ingest(c: TestClient, org: str, text: str) -> None:
    c.portal.call(_ingest, c.app.state.agent_deps, org, text)  # type: ignore[attr-defined,union-attr]


def ref_in(messages: list[Message]) -> str:
    return re.findall(r'ref="(C\d+)"', messages[-1].tool_results[0].text)[0]


# ----------------------------------------------------------------------- the stream


def test_events_arrive_in_order_tokens_add_up_and_the_answer_is_validated(
    client: TestClient,
) -> None:
    h, _ = signup(client)
    conv = new_conv(client, h)
    set_llm(client, FakeLLM([call("search_documents", query="x"), say("Hello there [C99]")]))

    r = chat(client, h, conv)

    assert r.status_code == 200
    assert r.headers["content-type"].startswith("text/event-stream")
    assert r.headers["cache-control"] == "no-cache"
    events = parse_sse(r.text)
    kinds = [k for k, _ in events]
    assert kinds[:2] == ["step", "step"] and kinds[-3:] == ["answer", "citations", "done"]
    assert {k for k in kinds[2:-3]} == {"token"}
    streamed = "".join(d["text"] for k, d in events if k == "token")
    assert streamed == "Hello there [C99]"  # raw stream, before validation
    answer = next(d for k, d in events if k == "answer")
    assert answer["text"] == "Hello there"  # the invented citation never reaches the final text
    done = events[-1][1]
    assert done["status"] == "ok" and done["message_id"] and done["run_id"]
    assert "answer" not in done and "steps" not in done  # sent as their own events already


def test_citations_carry_file_page_and_snippet(client: TestClient) -> None:
    h, org = signup(client)
    ingest(client, org, "Payment Terms. Net 45 applies to Acme Corp invoices.")
    conv = new_conv(client, h)
    set_llm(
        client,
        FakeLLM(
            [
                call("search_documents", query="payment terms"),
                lambda m: say(f"Net 45 [{ref_in(m)}]"),
            ]
        ),
    )
    events = parse_sse(chat(client, h, conv).text)
    (cite,) = next(d for k, d in events if k == "citations")["items"]
    assert cite["filename"] == "acme-contract.pdf" and cite["page"] == 1
    assert "Net 45" in cite["snippet"] and cite["ref"] == "C1"


def test_a_model_outage_still_ends_with_a_done_event(client: TestClient) -> None:
    class Down:
        async def generate(self, *_a: object, **_k: object) -> LLMResponse:
            raise LLMUnavailable("no usable model left")

        async def generate_stream(self, *_a: object, **_k: object):  # type: ignore[no-untyped-def]
            raise LLMUnavailable("no usable model left")
            yield ""  # pragma: no cover  (makes this an async generator)

    h, _ = signup(client)
    conv = new_conv(client, h)
    set_llm(client, Down())
    events = parse_sse(chat(client, h, conv).text)
    assert events[-1][0] == "done" and events[-1][1]["status"] == "error"
    assert "try again" in next(d for k, d in events if k == "answer")["text"]


def test_demo_mode_answers_from_the_documents_with_a_citation(client: TestClient) -> None:
    h, org = signup(client)
    ingest(client, org, "Termination. Either party may end this Agreement on sixty days notice.")
    conv = new_conv(client, h)
    # no set_llm: AI_PROVIDER=fake gives the deterministic DemoLLM
    events = parse_sse(chat(client, h, conv, "How much notice to terminate?").text)
    answer = next(d for k, d in events if k == "answer")["text"]
    assert "acme-contract.pdf" in answer and "sixty days" in answer and "Demo mode" in answer
    assert next(d for k, d in events if k == "citations")["items"][0]["ref"] == "C1"
    assert any(k == "token" for k, _ in events)


# ------------------------------------------------------------- errors before streaming


def test_requires_a_token(client: TestClient) -> None:
    assert client.post(f"/chat/{uuid.uuid4()}/messages", json={"content": "hi"}).status_code == 401
    assert client.get("/conversations").status_code == 401
    assert client.post("/conversations", json={}).status_code == 401


def test_another_orgs_conversation_is_a_404_not_a_stream(client: TestClient) -> None:
    ha, _ = signup(client)
    hb, _ = signup(client)
    conv = new_conv(client, ha)
    assert chat(client, hb, conv).status_code == 404
    assert client.get(f"/conversations/{conv}/messages", headers=hb).status_code == 404
    assert chat(client, ha, str(uuid.uuid4())).status_code == 404


def test_message_length_is_validated(client: TestClient) -> None:
    h, _ = signup(client)
    conv = new_conv(client, h)
    assert chat(client, h, conv, "").status_code == 422
    assert chat(client, h, conv, "x" * 2001).status_code == 422
    assert client.post(f"/chat/{conv}/messages", headers=h, json={}).status_code == 422


def test_chat_is_unavailable_without_a_model_but_the_rest_still_works(client: TestClient) -> None:
    h, _ = signup(client)
    conv = new_conv(client, h)
    client.app.state.agent_deps = None  # type: ignore[attr-defined]
    assert chat(client, h, conv).status_code == 503
    assert client.get("/meta").json() == {"chat": "unavailable"}
    assert client.get("/documents", headers=h).status_code == 200  # uploads and listing unaffected


def test_meta_says_honestly_what_is_answering(client: TestClient) -> None:
    assert client.get("/meta").json() == {"chat": "demo"}  # AI_PROVIDER=fake in tests
    set_llm(client, FakeLLM([]))
    assert client.get("/meta").json() == {"chat": "model"}


# --------------------------------------------------------------- conversations API


def test_history_lists_messages_with_citations_and_titles_the_conversation(
    client: TestClient,
) -> None:
    h, org = signup(client)
    ingest(client, org, "Payment Terms. Net 30 applies.")
    conv = new_conv(client, h)
    set_llm(
        client,
        FakeLLM([call("search_documents", query="terms"), lambda m: say(f"Net 30 [{ref_in(m)}]")]),
    )
    chat(client, h, conv, "What are   the payment terms?")

    msgs = client.get(f"/conversations/{conv}/messages", headers=h).json()
    assert [m["role"] for m in msgs] == ["user", "assistant"]
    assert msgs[0]["content"] == "What are   the payment terms?"
    assert msgs[1]["citations"][0]["filename"] == "acme-contract.pdf"
    assert [x["tool"] for x in msgs[1]["steps"]] == ["search_documents"]  # what the agent did
    assert msgs[1]["steps"][0]["args"]["query"] == "terms" and msgs[1]["model"] == "fake-model"
    assert msgs[0]["steps"] is None  # user messages have no run
    listed = client.get("/conversations", headers=h).json()
    assert listed[0]["id"] == conv and listed[0]["title"] == "What are the payment terms?"


def test_conversations_are_listed_newest_first_and_only_for_their_org(client: TestClient) -> None:
    ha, _ = signup(client)
    hb, _ = signup(client)
    first, second = new_conv(client, ha), new_conv(client, ha)
    new_conv(client, hb)
    assert [c["id"] for c in client.get("/conversations", headers=ha).json()] == [second, first]
    assert len(client.get("/conversations", headers=hb).json()) == 1
