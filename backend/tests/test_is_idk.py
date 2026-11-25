"""is_idk decides when an answer means "I'm not sure", which switches the card to suggestions."""
import pytest

from main import is_idk


@pytest.mark.parametrize("answer", ["I don't know", "i dont know.", "  IDK!  ", "Not sure?", "skip", ""])
def test_unsure_answers(answer):
    assert is_idk(answer)


@pytest.mark.parametrize("answer", ["Neighbors and families", "not sure about the colors yet, maybe blue", "I know exactly"])
def test_real_answers_are_kept(answer):
    assert not is_idk(answer)
