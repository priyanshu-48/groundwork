"""A deterministic stand-in for the language model: searches for the question and answers with the
best match. It exists so the app (and its end-to-end test) runs with no API key. It is not smart
and the UI says so; nothing about it should be mistaken for a real answer."""

import re
from collections.abc import AsyncIterator

from app.agent.llm import LLMResponse, Message, StreamItem, ToolSpec, call, say

_DOC = re.compile(r'<document ref="(C\d+)" file="([^"]+)" page="(\d+)">\n(.*?)\n</document>', re.S)


class DemoLLM:
    async def generate(
        self, system: str, messages: list[Message], tools: list[ToolSpec]
    ) -> LLMResponse:
        question = next((m.text for m in reversed(messages) if m.role == "user"), "")
        last = messages[-1]
        if last.role != "tool":  # first turn: look the question up
            return call("search_documents", query=question[:500], top_k=3)
        match = _DOC.search(last.tool_results[0].text)
        if not match:
            return say("I couldn't find anything relevant in your documents. (Demo mode.)")
        ref, filename, page, body = match.groups()
        excerpt = " ".join(body.split())[:240]
        return say(
            f"Closest match is {filename}, page {page}: {excerpt} [{ref}] "
            "(Demo mode: no language model is answering.)"
        )

    async def generate_stream(
        self, system: str, messages: list[Message], tools: list[ToolSpec]
    ) -> AsyncIterator[StreamItem]:
        resp = await self.generate(system, messages, tools)
        for word in resp.text.split(" "):
            yield word + " "
        yield resp
