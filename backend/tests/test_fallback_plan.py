"""fallback_plan is the offline plan used when no AI provider answers. It must stay faithful to the answers."""
from main import PlanIn, Turn, fallback_plan


def make(**kw):
    history = [
        Turn(field="audience", question="Who is it for?", answer="Neighbors and local families"),
        Turn(field="avoid", question="Anything to avoid?", answer="I don't know"),
        Turn(field="key_details", question="Key facts?", answer="Opening Saturday 9am, 12 Court St"),
    ]
    return fallback_plan(PlanIn(request="make a flyer for my bakery grand opening", history=history, **kw))


def test_uses_the_persons_own_answers():
    plan = make()
    assert "Neighbors and local families" in plan["brief"]
    assert "Opening Saturday 9am, 12 Court St" in plan["brief"]


def test_unsure_answers_are_not_shown_as_choices():
    values = [c["value"] for c in make()["choices"]]
    assert "I don't know" not in values
    assert "Neighbors and local families" in values


def test_steps_mark_who_decides():
    owners = [s["owner"] for s in make()["steps"]]
    assert owners == ["you", "you", "ai", "ai", "you"]


def test_change_request_is_applied_and_listed():
    plan = make(change_request="make it more playful")
    assert "make it more playful" in plan["brief"]
    assert plan["changes"] == ["Applied your request: make it more playful"]


def test_visual_requests_go_to_the_image_tool():
    assert make()["best_tool"] == "chatgpt"
