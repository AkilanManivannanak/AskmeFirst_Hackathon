"""validate_q is the quality gate for every interview card. A card that fails it goes to the next model or the backup."""
import pytest

from main import validate_q

REQUEST = "make a flyer for my bakery grand opening"


def card(**kw):
    d = {"question": "What date and time is the opening?", "why": "So the flyer has the exact details.",
         "field": "key_details", "suggestions": ["Saturday 9am", "Sunday noon", "Next Friday evening"]}
    d.update(kw)
    return d


def test_good_card_passes():
    d = card()
    validate_q(["key_details", "style"], [], REQUEST)(d)
    assert d["field"] == "key_details"


def test_rejects_a_reworded_repeat_on_the_same_topic():
    gate = validate_q(["style"], [("style", "Which colors and fonts do you like?")], REQUEST)
    with pytest.raises(ValueError, match="repeats"):
        gate(card(field="style", question="What colors should it use?"))


def test_rejects_a_near_copy_from_any_topic():
    gate = validate_q(["style"], [("audience", "What date and time is the opening?")], REQUEST)
    with pytest.raises(ValueError, match="repeats"):
        gate(card(field="style"))


@pytest.mark.parametrize("missing", ["question", "why"])
def test_rejects_missing_question_or_reason(missing):
    with pytest.raises(ValueError, match="missing"):
        validate_q(["key_details"], [], REQUEST)(card(**{missing: "  "}))


def test_rejects_the_word_prompt():
    # The people this is for should never see AI jargon.
    with pytest.raises(ValueError, match="prompt"):
        validate_q(["key_details"], [], REQUEST)(card(why="This helps the prompt."))


def test_needs_three_real_suggestions():
    with pytest.raises(ValueError, match="3 suggestions"):
        validate_q(["key_details"], [], REQUEST)(card(suggestions=["Saturday", "  ", ""]))


def test_keeps_only_three_suggestions_trimmed():
    d = card(suggestions=[" Saturday 9am ", "Sunday noon", "Friday 5pm", "Monday"])
    validate_q(["key_details"], [], REQUEST)(d)
    assert d["suggestions"] == ["Saturday 9am", "Sunday noon", "Friday 5pm"]


def test_off_list_topic_is_moved_to_an_open_one():
    d = card(field="weather")
    validate_q(["format", "style"], [], REQUEST)(d)
    assert d["field"] == "format"
