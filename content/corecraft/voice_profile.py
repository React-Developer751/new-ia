"""Voice changes for sub-niches whose kind voice would sound wrong: a bakery is not a table-booking restaurant, yoga is not a rep-counting gym."""
from .voice_data import VOICE

_FOOD_FAQ = {f[0]: f for f in VOICE["food"]["faq"]}
_FIT_FAQ = {f[0]: f for f in VOICE["fitness"]["faq"]}

BAKERY = dict(
    who="customers", does=("bakes", "makes"), do=("bake", "make"), ing=("Baking", "Making"), come="Order",
    act=("Place an order", "See what's baked"), act_online=("Order online", "See what's baked"),
    book_how_online="Order online", book_how="Message us to place an order",
    tails=["baked fresh", "made for the occasion", "sweet and simple", "from the oven", "for every celebration"],
    closers=["Order early for a big day.", "Fresh from the oven is the best kind.", "Save a slice for later.", "Ask the team what is baked today.", "Something sweet makes any day better.",
             "Tell us the occasion and we'll help you choose.", "Every bake is better shared.", "Bring a sweet tooth."],
    invites=["Tell us the date and how many you need to feed.", "Message us the occasion and we'll suggest what suits it.", "Ask what is fresh today.", "Tell us about any dietary need before you order.",
             "Share the day you need it and we'll confirm what's possible.", "Ask for a recommendation when you visit.", "Order ahead for a celebration.", "Message us your idea and we'll talk it through."],
    feat=["Ask the team what goes into {i}; they like the question.", "A good place to start if you like {i}.", "Order {i} for the occasion, or keep it to yourself.",
          "Curious about {i}? Ask, and we'll talk you through it.", "Tell us the date and we'll say what we can do with {i}.", "{I} is better shared, so order a little more than you think you need.",
          "Pair {i} with something from the rest of the bakery.", "If {i} is why you came, say so when you order."],
    steps=[[("Choose what you like", "Start with {list2_or}, or ask the team for ideas."), ("Tell us the date", "Give us the day and the size, and we'll confirm."), ("Enjoy it fresh", "Collect it, or let someone else do the honours.")],
           [("Share your idea", "Flavour, size, message and the date."), ("We plan the bake", "We confirm the details with you."), ("Celebrate", "Slice, share and enjoy.")],
           [("Pick your treat", "Look through {list2_or} and decide."), ("{book_how}", "Tell us the day you need it."), ("Pick it up and enjoy", "Fresh and ready for the day.")]],
    faq=[("Can I order something for a particular day?", ["Tell us the date, the size and what you'd like, and we'll say what we can do.", "Message us the day you need it and we'll confirm."], None, None),
         ("How can I order something?", ["{book_how}, and tell us the date.", "Use the contact details on this page and say what you'd like."], "online_order", ["You can order online, or contact us directly.", "Online ordering is available whenever it suits you."]),
         ("Can I collect my order?", ["Ask us when you order and we'll tell you what's possible.", "Message us and we'll arrange a time."], "pickup", ["Yes, pickup is available; tell us when you'll come.", "You can pick up your order; message us the time."]),
         _FOOD_FAQ["Do you offer delivery or takeaway?"], _FOOD_FAQ["I have an allergy. Can you help?"], _FOOD_FAQ["When are you open?"], _FOOD_FAQ["Where are you?"],
         ("Can I ask about {i1}?", ["Of course; ask us what goes into it and how to order it.", "Yes; tell us what you'd like to know about {i1}."], "item", None)],
    highlights=[("Baked fresh", "Made for the day, not for the shelf."), ("Made to order", "Tell us the occasion and we'll plan around it."), ("Ask the team", "They like questions about what's baked."),
                ("For celebrations", "Share the date and the numbers."), ("Something sweet", "A treat for any day."), ("Easy to order", "Say what you'd like and we'll take it from there.")],
    blog=[("Ordering a cake for a celebration", "How early to order and what to tell the baker."), ("What to try on a first visit", "Start with {i1}, then follow your sweet tooth."),
          ("Planning a birthday spread", "Choose the day, the numbers and one bake everyone will share."), ("A short guide to {i1}", "What it is, how it is usually enjoyed and what goes with it."),
          ("Why fresh matters", "The case for {i1} on the day it is baked."), ("Pairing {i1} with the rest of the bakery", "A few simple combinations to try."),
          ("Choosing for a crowd", "Sizes, slices and ordering without worry."), ("Sweet or savoury first? A debate", "On starting with {i1} or finishing with it.")],
    cta_text=["{act1} and tell us the occasion.", "Something sweet? {act1}.", "Your order is one message away.", "Ask about {i1} when you {act1_l}.", "Tell us the date; we'll handle the rest.",
              "{act1}, or message us your plans.", "Plan a celebration around {i1}.", "Start with a treat; finish with another."],
    _generic=True,
)

YOGA = dict(
    who="students", does=("teaches", "guides", "holds"), do=("teach", "guide", "hold"), ing=("Teaching", "Guiding"), come="Practise with us for",
    act=("Start a free class", "Book a class"), act_online=("Book a class online", "See the schedule"),
    book_how_online="Book a class online", book_how="Message us to book a class",
    tails=["breath by breath", "at your own pace", "calm and steady", "on the mat", "for body and mind"],
    closers=["Show up; we'll guide the rest.", "Every body starts somewhere.", "A little practice goes a long way.", "Bring a mat if you have one.", "Teachers watch your breath, not the clock.",
             "Progress is felt before it is seen.", "No experience needed to start.", "Come once and see how it feels."],
    invites=["Tell us your goal and we'll point you to the right class.", "Ask about a first class and see if it suits you.", "Message us your schedule and we'll plan around it.",
             "Tell the teacher about any injury before you start.", "Ask what to wear and bring.", "Bring a friend; it helps to start together.", "Ask us which class is best for a beginner.",
             "Tell us how many days a week you can practise."],
    feat=["{I} is guided from the first breath to the last; ask which level suits you.", "New to {i}? Tell the teacher and they'll guide you.", "Ask what a {i} class looks like before you join.",
          "{I}: show up, follow the teacher, and notice how you feel.", "We'll explain {i} before you begin and adjust it as you go.", "Curious about {i}? Come for a class and see.",
          "Tell us your goal and we'll show you where {i} fits.", "{I} is for every level; the teacher adjusts as you go."],
    steps=[[("Book a class", "{book_how}, and tell us your goal."), ("Meet your teacher", "We'll talk about your experience and any injuries."), ("Practise and settle in", "Show up, follow the guidance and notice the change.")],
           [("Try a class", "Ask about a first class and pick a time."), ("Find your style", "We suggest {list2_or} to fit your goal and your week."), ("Keep going", "Regular classes, regular check-ins.")],
           [("Say hello", "Message us your goal and schedule."), ("Settle in and learn", "The teacher introduces {list2_or} and checks your alignment."), ("Build the habit", "Come back; practice is built class by class.")]],
    faq=[("Do I need experience?", ["No; teachers adjust every class to your level.", "Tell the teacher you are new and they'll guide you from the start."], None, None),
         ("Can I try a class first?", ["Ask us when you book and we'll tell you what is available.", "Message us and we'll arrange the first visit."], "free_trial", ["Yes, a free first class is available; ask us to book it.", "You can start with a free class."]),
         ("What should I wear and bring?", ["Comfortable clothes you can move in; bring water and a mat if you have one.", "Wear what you can stretch in; bring water."], None, None),
         _FIT_FAQ["I have an injury. Can I still train?"], _FIT_FAQ["How do I book?"], _FIT_FAQ["When are you open?"], _FIT_FAQ["Where are you?"],
         ("Can I ask about {i1}?", ["Of course; ask what a class looks like.", "Yes; tell us what you'd like to know about {i1}."], "item", None)],
    highlights=[("Teacher-led", "Someone is watching your alignment."), ("Every level", "Classes scale to you."), ("Calm space", "Slow down and breathe."), ("Easy to start", "Come once and see."),
                ("Feel the change", "Small shifts that add up."), ("Practise together", "Bring a friend.")],
    blog=[("Starting out: your first month", "What to expect, how often to come and how to ease in."), ("What to know before {i1}", "A short guide for beginners."), ("{I1} vs {i2}: which first?", "A plain comparison."),
          ("Rest matters as much as {i1}", "Sleep, food and quiet days."), ("Practice around a busy week", "How to keep the habit when life gets full."), ("Questions to ask a teacher", "Before you commit to anything."),
          ("How to notice progress", "Simple signs that tell the truth."), ("Warming up properly for {i1}", "The five minutes that protect the next hour.")],
    cta_text=["{act1} and tell us your goal.", "Try {i1} once and see.", "Your first class starts with a message.", "{act1}; we'll guide the rest.", "Ask which class suits a beginner.",
              "Ready? {act1}.", "Start with {i1}.", "Show up; we'll handle the rest."],
    _generic=True,
)

def _swap(x, pairs):
    if isinstance(x, str):
        for a, b in pairs:
            x = x.replace(a, b)
        return x
    if isinstance(x, (list, tuple)):
        return type(x)(_swap(y, pairs) for y in x)
    return x


SWEETS = {k: _swap(v, [("See what's baked", "See the sweets"), ("Ordering a cake for a celebration", "Ordering sweets for a celebration"), ("Order early for a big day", "Order early for a festival"),
                       ("Fresh from the oven", "Fresh from the kitchen"), ("Save a slice for later", "Save a piece for later"), ("Slice, share and enjoy", "Share and enjoy"), ("Planning a birthday spread", "Planning a festival spread"),
                       ("what's baked", "what's fresh"), ("what is baked today", "what is fresh today"), ("baked fresh", "made fresh"), ("Baked fresh", "Made fresh"), ("from the oven", "from the kitchen"),
                       ("We plan the bake", "We plan the order"), ("Baking", "Making"), ("bakes", "makes"), ("bake", "make"), ("Bake", "Make"), ("bakery", "shop"), ("a slice", "a piece"), ("baked", "made")])
          for k, v in BAKERY.items()}
SWEETS["act"] = ("Place an order", "See the sweets")
SWEETS["act_online"] = ("Order online", "See the sweets")
SWEETS["_generic"] = True

SCHOOL = dict(
    who="families", does=("teaches", "guides"), do=("teach", "guide"), ing=("Teaching", "Guiding"), come="Learn",
    act=("Ask about admission", "See the classes"), act_online=("Apply online", "See the classes"),
    book_how_online="Apply online", book_how="Message us to ask about admission",
    tails=["step by step", "in a caring classroom", "with time for questions", "one year at a time", "beyond the textbook"],
    closers=["Every child starts from where they are.", "Questions are welcome from parents too.", "Visit and see a classroom for yourself.", "Learning is better with encouragement.",
             "Parents are kept in the loop.", "Small steps, then bigger ones.", "Come and meet the teachers.", "Ask until it makes sense."],
    invites=["Tell us your child's age and class and we'll explain the next step.", "Ask about timings and the school day.", "Message us to arrange a visit.", "Ask how parents are kept informed.",
             "Tell us what matters most to you in a school.", "Ask what the first day looks like.", "Share your questions before you decide.", "Ask how to apply."],
    feat=["Ask how {i} fits into the school day.", "Curious about {i}? Come and see it in action.", "{I} is part of what children do here; ask how it works.", "Ask who teaches {i} and how progress is shared.",
          "New to {i}? Ask the teachers how children are eased in.", "Tell us what your child enjoys and we'll show where {i} fits.", "Ask us about {i} when you visit.", "{I}: ask how it is taught and how it is checked."],
    steps=[[("Ask about admission", "{book_how}, and tell us your child's age and class."), ("Visit the school", "Meet the teachers and see the classrooms."), ("Join the class", "We confirm the details and the first day with you.")],
           [("Tell us about your child", "Share the age, the class and anything we should know."), ("Meet the team", "We explain the school day and answer your questions."), ("Settle in", "Teachers help your child find their feet.")],
           [("Get in touch", "Message us or use the contact details on this page."), ("See for yourself", "Walk through the school and meet the teachers."), ("Begin the year", "We guide you through the first weeks.")]],
    faq=[("How do I ask about admission?", ["{book_how}, and tell us your child's age and class.", "Use the contact details on this page and tell us which class you have in mind."], "admissions",
          ["Admissions are open; use the contact details on this page to start.", "Yes, admissions are open; message us to begin."]),
         ("Can I visit the school first?", ["Of course; message us and we'll arrange a time.", "Yes; ask us for a convenient time to visit."], None, None),
         ("How are parents kept informed?", ["Ask us when you visit and we'll explain how updates are shared.", "Message us and we'll tell you how teachers keep in touch."], None, None),
         ("Which classes do you teach?", ["Ask us about the classes you have in mind and we'll explain.", "Tell us your child's age and we'll point you to the right class."], None, None),
         ("When are you open?", ["We're open {hours}.", "Our hours are {hours}."], "hours", None),
         ("Where are you?", ["We're in {city}; get in touch for directions.", "Find us in {city}. Message us and we'll send directions."], "city", None),
         ("Can I ask about {i1}?", ["Of course; ask how it is taught.", "Yes; tell us what you'd like to know about {i1}."], "item", None),
         ("Can I ask questions before I decide?", ["Of course; that's what the first conversation is for.", "Yes; ask as many as you like."], None, None)],
    highlights=[("Caring teachers", "Someone knows your child by name."), ("Every child", "Learning scaled to where they are."), ("Parents in the loop", "Updates you can rely on."), ("Visit first", "See a classroom before you decide."),
                ("Beyond the textbook", "Activities alongside lessons."), ("Easy to ask", "Questions are always welcome.")],
    blog=[("Choosing a school: questions to ask", "A short list for parents before they decide."), ("What to know before {i1}", "A short guide for families."), ("The first week: what to expect", "How children settle into a new class."),
          ("Helping your child with homework", "Routines that make evenings calmer."), ("Why {i1} matters", "A plain look at what children gain."), ("Talking to teachers", "How to get the most from a meeting."),
          ("Preparing for a new year", "Small steps that help everyone."), ("Balancing study and play", "Why both matter.")],
    cta_text=["{act1} and tell us your child's class.", "Visit and see for yourself.", "Your first question is one message away.", "{act1}; we'll explain the next step.", "Ask how {i1} works.",
              "Ready? {act1}.", "Start with {i1}; ask the rest.", "Come and meet the teachers."],
    _generic=True,
)

TEA = dict(does=("serves", "brews", "pours"), do=("serve", "brew", "pour"), ing=("Serving", "Brewing"), come="Come for",
           act=("Visit us", "See the menu"), act_online=("Order online", "See the menu"),
           invites=["Tell us when you're coming and we'll make room.", "Ask for a recommendation when you arrive.", "Ask what is freshly made today.", "Message us if you're coming with a group.",
                    "Ask what pairs well with your cup.", "Tell us if anyone has a dietary need.", "Bring a friend and ask what to try.", "Ask the team what they would order."],
           cta_text=["{act1} and ask what's fresh.", "Start with a cup; ask about {i1}.", "Your next cup is one message away.", "Ask about {i1} when you {act1_l}.", "Come as you are; we'll handle the rest.",
                     "{act1}, or message us your plans.", "Try {i1} and tell us what you think.", "Stay a while; nobody is rushing you."], _generic=True)

PROFILE_VOICE = {"bakery": BAKERY, "yoga": YOGA, "tea_cafe": TEA}
TYPE_VOICE = {"sweets": SWEETS, "school": SCHOOL}


def profile_voice(kind, profile, type_id=None):
    """The kind's voice with the sub-niche's own fields laid over it (or None when the kind voice is right as it is)."""
    over = TYPE_VOICE.get(type_id) or PROFILE_VOICE.get(profile)
    if not over:
        return None
    base = dict(VOICE[kind])
    base.update(over)
    return base
