"""
Safety-net content used only when no AI provider answers in time.
Domain-aware so the flow still feels relevant: the request is sorted into a
category, and every question names the person's own request.
"""
import re

CATEGORIES = [
    ("career", r"\b(resume|cv|cover letter|job|interview|linkedin|career|portfolio|hiring)\b"),
    ("presentation", r"\b(presentation|slides?|slideshow|deck|pitch|talk|keynote|ppt|pptx|powerpoint|google slides)\b"),
    ("finance", r"\b(budget|finances?|financial|money|tax(es)?|invest(ing|ment)?|savings?|expenses?|loan|debt|retirement|pricing)\b"),
    ("social", r"\b(instagram|facebook|tiktok|social media|posts?|captions?|newsletter|youtube)\b"),
    ("visual", r"\b(flyer|poster|logo|image|illustration|picture|banner|graphic|design|invitation|sign|menu|brochure|card|photo|website|web page|landing page|portrait|video thumbnail)\b"),
    ("event", r"\b(party|wedding|trip|reunion|event|birthday|dinner|vacation|travel|celebration|meeting|conference|itinerary|workshop)\b"),
    ("education", r"\b(lesson|teach|study|class|homework|course|kids|students|exam|curriculum|tutor)\b"),
    ("business", r"\b(business|startup|shop|store|marketing|sales|customers|brand|company|side hustle|restaurant)\b"),
    ("research", r"\b(research|compare|find|best|options|understand|explain|review|choose|learn about)\b"),
    ("writing", r"\b(letter|email|message|note|speech|essay|article|story|toast|complaint|bio|eulogy)\b"),
]

WHY = {
    "audience": "Knowing exactly who it is for shapes every word and choice.",
    "purpose": "A clear goal tells the AI what to prioritize.",
    "key_details": "Specific facts are what make the result yours instead of generic.",
    "format": "Length and format decide how much the AI writes and how it is laid out.",
    "style": "The right tone decides whether it connects with people.",
    "avoid": "Clear limits keep the result accurate and give you something to check.",
}

# category -> slot -> (question template, [3 suggestions]);  {T} = "your <request>"
BANK = {
    "career": {
        "audience": ("Which role or employer is {T} aimed at?", ["A specific job posting I found", "A promotion at my current company", "Any role in my field"]),
        "key_details": ("Which achievements should {T} highlight?", ["Projects I led and their results", "Certifications and training", "Years of experience and key skills"]),
        "purpose": ("What should a hiring manager think after reading {T}?", ["This person can lead a team", "They learn fast and adapt", "They have exactly the right experience"]),
        "format": ('How long should {T} be, and is there a deadline?', ['One page', 'Two pages', 'Due this week']),
        "style": ("What tone fits your field for {T}?", ["Formal and traditional", "Modern and concise", "Warm and personable"]),
        "avoid": ("Is there anything {T} should leave out?", ["Personal details like age", "Buzzwords and clichés", "Older, unrelated jobs"]),
    },
    "presentation": {
        "audience": ("Who will be watching {T}?", ["My team at work", "Parents and teachers", "Potential partners or donors"]),
        "key_details": ("What main points must {T} cover?", ["The problem and our solution", "Results and key numbers", "Next steps and what we need"]),
        "purpose": ("What should the audience do after {T}?", ["Approve the plan", "Volunteer or donate", "Understand the update"]),
        "format": ('How many slides should {T} have, and will you present it live?', ['About 10 slides, presented live', '5 slides, sent by email', 'A 15-minute talk with slides']),
        "style": ("What style suits {T}?", ["Clean, few words per slide", "Visual, with photos and charts", "Formal and data-driven"]),
        "avoid": ("Is there anything {T} should avoid?", ["Too much text on slides", "Technical jargon", "Running over time"]),
    },
    "finance": {
        "audience": ("Who will be using {T}?", ["Just me", "My partner and me", "My whole household"]),
        "key_details": ("What numbers do you already know for {T}?", ["Monthly take-home income", "Rent and regular bills", "Debts and monthly payments"]),
        "purpose": ("What goal should {T} help you reach?", ["Save a set amount each month", "Pay off a debt faster", "See where my money goes"]),
        "format": ('What period should {T} cover, and in what format?', ['One month, as a table', 'A full year, month by month', 'A simple one-page summary']),
        "style": ("How detailed should {T} be?", ["Simple, on one page", "Detailed by category", "A table I can update monthly"]),
        "avoid": ("Is there anything {T} should avoid?", ["Complicated financial terms", "Guessing numbers I did not give", "Recommending specific investments"]),
    },
    "social": {
        "audience": ("Who do you want to reach with {T}?", ["Local customers", "People who share my interest", "Friends and family"]),
        "key_details": ("What news or message should {T} share?", ["A new product or offer", "An upcoming event", "A behind-the-scenes story"]),
        "purpose": ("What should people do after seeing {T}?", ["Visit the shop or website", "Comment or share", "Book or sign up"]),
        "format": ('Which platform is {T} for, and how many posts?', ['Instagram, 5 posts', 'Facebook, one per week', 'LinkedIn, 3 posts']),
        "style": ("What voice fits {T}?", ["Friendly and casual", "Inspiring and warm", "Short and witty"]),
        "avoid": ("Is there anything {T} should avoid?", ["Too many hashtags", "Sounding like an advertisement", "Emojis"]),
    },
    "visual": {
        "audience": ("Who should notice {T}?", ["Neighbors walking past", "Customers scrolling online", "Families in my community"]),
        "key_details": ("What words or facts must appear on {T}?", ["Name, date and location", "Prices or a special offer", "Phone number or website"]),
        "purpose": ("What should people do after seeing {T}?", ["Visit or attend", "Call or message me", "Remember the name"]),
        "format": ('What size and format should {T} be?', ['Printed letter-size flyer', 'Square social media post', 'Large poster for a window']),
        "style": ("What look and colors suit {T}?", ["Warm and friendly colors", "Clean and minimal", "Bold and eye-catching"]),
        "avoid": ("Is there anything {T} should not show or say?", ["Crowded, hard-to-read text", "A generic stock-photo look", "Overly bright colors"]),
    },
    "event": {
        "audience": ("Who is coming to {T}, and roughly how many?", ["Close family, about 20 people", "Friends and coworkers", "A mix of ages, including kids"]),
        "key_details": ("What is already decided for {T}?", ["The date and city", "The budget", "The venue, or a few options"]),
        "purpose": ("What would make {T} a success for you?", ["Everyone feels welcome and relaxed", "It stays within budget", "Smooth timing, no stress"]),
        "format": ('When and where is {T}, and what is the budget?', ['A Saturday in July, at home, about 500 dollars', 'A rented hall, about 2,000 dollars', 'Not decided yet']),
        "style": ("What atmosphere do you want for {T}?", ["Elegant and calm", "Casual and fun", "Traditional and meaningful"]),
        "avoid": ("Is there anything to avoid for {T}?", ["Going over budget", "Long travel times", "Foods some guests cannot eat"]),
    },
    "education": {
        "audience": ("Who is {T} for, and what level are they?", ["Children aged 8 to 10", "High school students", "Adult beginners"]),
        "key_details": ("What should learners be able to do after {T}?", ["Explain one core idea clearly", "Apply it in real life", "Pass the upcoming test"]),
        "purpose": ("How much time is there for {T}?", ["A single 45-minute class", "A week of short sessions", "Self-paced at home"]),
        "format": ('How long is {T}, and what materials do you have?', ['45 minutes, whiteboard only', 'One hour, with laptops', 'A week of short sessions']),
        "style": ("How should {T} feel?", ["Playful, with activities", "Structured, step by step", "Discussion-based"]),
        "avoid": ("Is there anything {T} should avoid?", ["Long lectures", "Materials we do not have", "Advanced vocabulary"]),
    },
    "business": {
        "audience": ("Who are the customers for {T}?", ["Local families", "Small business owners", "Young professionals"]),
        "key_details": ("What makes {T} different from competitors?", ["Personal, attentive service", "Better prices", "Years of experience"]),
        "purpose": ("What result do you want from {T}?", ["More customers", "A clear plan to get started", "Higher sales"]),
        "format": ('What format and length should {T} be?', ['A one-page summary', 'A detailed 5-page plan', 'A short pitch I can say aloud']),
        "style": ("How should {T} come across?", ["Trustworthy and professional", "Friendly and local", "Premium and polished"]),
        "avoid": ("Is there anything {T} should avoid?", ["Promises I cannot keep", "Industry jargon", "Copying competitors"]),
    },
    "research": {
        "audience": ("Who will rely on {T}?", ["Just me, to make a decision", "A family member", "My manager or team"]),
        "key_details": ("What do you already know or prefer about {T}?", ["A few options I have heard of", "My budget or limits", "Nothing yet, starting fresh"]),
        "purpose": ("What decision should {T} help you make?", ["Choose the best option", "Understand the basics", "Know the risks before deciding"]),
        "format": ('How long should {T} be, and when do you need it?', ['A one-page summary', 'A detailed comparison table', 'Quick answer for today']),
        "style": ("How would you like {T} presented?", ["Short summary with a recommendation", "Side-by-side comparison table", "Plain-language explanation"]),
        "avoid": ("Is there anything {T} should avoid?", ["Unreliable sources", "Unexplained jargon", "Sales pitches"]),
    },
    "writing": {
        "audience": ("Who will receive {T}?", ["Someone I know well", "A company or official", "A group of people"]),
        "key_details": ("What key points must {T} include?", ["What happened and when", "What I am asking for", "Important dates or numbers"]),
        "purpose": ("What outcome do you want from {T}?", ["A quick reply or action", "To be clearly understood", "To keep a good relationship"]),
        "format": ('How long should {T} be?', ['A short paragraph', 'About one page', 'A brief message']),
        "style": ("What tone should {T} have?", ["Polite but firm", "Warm and personal", "Formal and brief"]),
        "avoid": ("Is there anything {T} should avoid?", ["Sounding angry", "Too much detail", "Threats or ultimatums"]),
    },
    "general": {
        "audience": ("Who is {T} for?", ["Customers or clients", "Friends or family", "My team or colleagues"]),
        "key_details": ("What details must {T} include?", ["Names, dates and places", "Numbers or prices", "Something only I know"]),
        "purpose": ("What should {T} achieve?", ["Get people to take action", "Explain something clearly", "Save me time"]),
        "format": ('What length and format should {T} be?', ['Short and simple', 'About one page', 'Detailed, with sections']),
        "style": ("How should {T} look or sound?", ["Warm and friendly", "Clean and professional", "Bold and energetic"]),
        "avoid": ("Is there anything {T} should avoid?", ["Jargon", "Exaggerated claims", "Generic filler"]),
    },
}

DRAFT_STEP = {
    "career": ("AI tailors each section", "Rewrites your experience to match the role."),
    "presentation": ("AI outlines the slides", "One clear idea per slide, in a logical order."),
    "finance": ("AI organizes your numbers", "Sorts income and spending into clear categories."),
    "social": ("AI writes the posts", "Short captions in your voice, ready to publish."),
    "visual": ("AI designs it", "Layout, wording and colors from your choices."),
    "event": ("AI builds the plan", "Timeline, checklist and budget in one place."),
    "education": ("AI builds the lesson", "Steps, activities and a quick check for understanding."),
    "business": ("AI drafts the plan", "Customers, offer and next steps, in plain language."),
    "research": ("AI researches and compares", "Gathers options and summarizes the trade-offs."),
    "writing": ("AI drafts the text", "Clear, well-structured wording in your tone."),
    "general": ("AI drafts it", "A first version built from your choices."),
}

DELIVERABLE = {
    "career": "a polished, one-page resume or document in clean, copy-ready text",
    "presentation": "a slide-by-slide outline with a title, three bullet points and speaker notes for each slide",
    "finance": "a clear table with categories, monthly amounts and totals, followed by three practical suggestions",
    "social": "three ready-to-post captions, each with a suggested image idea",
    "visual": "the finished design as a single image, followed by the exact text used so it can be edited",
    "event": "a step-by-step plan with a timeline, a checklist and an estimated budget",
    "education": "a complete lesson plan with objectives, timed activities and materials",
    "business": "a one-page plan with clear headings and next steps",
    "research": "a short summary with a recommendation, followed by a comparison table and sources",
    "writing": "the finished text, ready to send",
    "general": "the finished result, ready to use",
}


def categorize(request: str) -> str:
    for name, pattern in CATEGORIES:
        if re.search(pattern, request, re.I):
            return name
    return "general"


def your_thing(request: str) -> str:
    t = request.strip().rstrip(".?!")
    t = re.sub(r"^(please\s+)?(can you\s+)?(help me\s+)?(i wanted to|i want to|i need to|i'd like to|i would like to|i wanted|i want|i need)?\s*"
               r"(make|create|write|design|build|plan|do|draft|prepare|update|research|get|find|start|launch|organize|set up|put together|come up with|figure out|improve|fix)?\s*", "", t, flags=re.I)
    t = re.sub(r"^(a|an|the|my|some)\s+", "", t, flags=re.I)
    t = re.sub(r"\bmy\b", "your", t, flags=re.I)
    t = re.sub(r"\bI\b", "you", t)
    words = t.split()
    if not words:
        return "this"
    short = " ".join(words[:8])
    return short if short.lower().startswith("your ") else "your " + short


NOUN = {"career": "your resume", "presentation": "your presentation", "finance": "your budget", "social": "your posts",
        "visual": "your design", "event": "your event", "education": "your lesson", "business": "your plan",
        "research": "your research", "writing": "your message", "general": "it"}


def fallback_question(request: str, slot: str) -> tuple[str, str, list[str]]:
    cat = categorize(request)
    q, sugg = BANK.get(cat, BANK["general"]).get(slot, BANK["general"][slot])
    q = q.replace("{T}", NOUN.get(cat, "it"))
    return q[0].upper() + q[1:], WHY[slot], list(sugg)
