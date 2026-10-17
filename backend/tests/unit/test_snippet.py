from app.agent.loop import relevant_snippet

CHUNK = (
    "Section 15. Severability. If any provision is found unenforceable, the remaining provisions "
    "continue in full effect. Section 16. Limitation of Liability. The total aggregate liability "
    "of either party arising out of this Agreement shall not exceed USD 250,000. Section 17. "
    "Governing Law. This Agreement is governed by the laws of the State of Delaware. " * 2
)


def test_short_chunks_are_returned_whole() -> None:
    assert relevant_snippet("Net 45 applies.", "Terms are net 45 [C1]") == "Net 45 applies."


def test_picks_the_sentence_that_supports_the_answer_not_the_opening() -> None:
    snip = relevant_snippet(CHUNK, "The liability cap is USD 250,000 [C1].")
    assert "shall not exceed USD 250,000" in snip
    assert not snip.startswith("Section 15")  # the chunk's opening is not what we cite
    assert snip.startswith("... ")  # and the reader can tell it was cut out of a longer text


def test_falls_back_to_the_opening_when_nothing_matches() -> None:
    snip = relevant_snippet(CHUNK, "Completely unrelated zebra words [C1]")
    assert snip.startswith("Section 15.") and not snip.startswith("... ")


def test_is_capped_and_never_empty() -> None:
    long_sentence = "alpha " * 200 + "."
    snip = relevant_snippet(long_sentence, "alpha", limit=100)
    assert 0 < len(snip) <= 103 and snip.endswith("...")
