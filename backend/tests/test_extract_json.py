"""extract_json turns a raw model reply into a dict. Every interview card goes through it."""
import pytest

from main import extract_json


def test_plain_json():
    assert extract_json('{"question": "Who is it for?"}') == {"question": "Who is it for?"}


def test_strips_code_fences():
    assert extract_json('```json\n{"done": true}\n```') == {"done": True}


def test_strips_hidden_thinking():
    reply = '<think>maybe {"wrong": 1}</think>{"field": "audience"}'
    assert extract_json(reply) == {"field": "audience"}


def test_ignores_chatter_around_json():
    assert extract_json('Sure! Here it is: {"why": "so it fits"} Hope that helps.') == {"why": "so it fits"}


def test_allows_raw_newlines_inside_strings():
    assert extract_json('{"brief": "line one\nline two"}') == {"brief": "line one\nline two"}


@pytest.mark.parametrize("bad", ["", None, "no json here", "```\n```"])
def test_raises_when_no_json(bad):
    with pytest.raises(ValueError):
        extract_json(bad)
