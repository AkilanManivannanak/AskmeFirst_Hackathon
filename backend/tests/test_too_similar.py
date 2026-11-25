"""too_similar stops the interview from asking the same question twice in different words."""
from main import too_similar

REQUEST = "make a flyer for my bakery grand opening"


def test_same_question_reworded_is_caught():
    assert too_similar("Which colors and fonts do you prefer?", ["What colors and fonts would you prefer?"], REQUEST)


def test_different_topic_is_allowed():
    assert not too_similar("What date and time is the opening?", ["Which colors and fonts do you prefer?"], REQUEST)


def test_words_from_the_request_do_not_count_as_overlap():
    # Both mention "bakery" and "flyer", which come from the request itself.
    assert not too_similar("Who should read the bakery flyer?", ["What prices go on the bakery flyer?"], REQUEST)


def test_first_question_is_never_a_repeat():
    assert not too_similar("Who is this for?", [], REQUEST)


def test_partial_overlap_still_counts_as_a_repeat():
    # Half the meaningful words match (colors), so asking again would annoy the person.
    assert too_similar("What colors should it use?", ["Which colors and fonts do you like?"], REQUEST)


def test_small_overlap_is_allowed():
    # One shared word out of many is a new question, not a repeat.
    assert not too_similar(
        "What colors match the opening day decorations and balloons?",
        ["Which colors feel right for families and kids?"],
        REQUEST,
    )
