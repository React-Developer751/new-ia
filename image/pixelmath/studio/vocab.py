"""Extra matcher vocabulary added on top of each niche's own lists (applied by niches.load_all()).

Found by running blind client-style prompts through the matcher: Roman-letter Hindi (kheton, kitaabon, dant), short plain phrases ("teeth cleaning",
"puppies for sale"), plural forms, and a few businesses that sound like a niche but are not ("shipyard", "ski resort", honey farm).
{niche_id: {"strong": (...), "weak": (...), "avoid": (...)}}. Keep entries specific: a bare generic word here would summon the wrong niche.
"""
EXTRA = {
    "agriculture-farm": {"weak": ("kheti", "kheton", "fasal", "crop field", "crops"), "avoid": ("madhumakkhi", "honey", "beekeeping", "मधुमक्खी", "शहद")},
    "bike-showroom": {"weak": ("motorbikes", "bikes", "motorcycles")},
    "car-showroom": {"avoid": ("motorbike", "motorbikes", "motorcycle", "motorcycles", "scooter", "two wheeler", "दोपहिया", "दुपहिया")},
    "event-party": {"avoid": ("hot air balloon", "hot air balloons", "balloon ride", "air balloon", "गर्म हवा के गुब्बारे")},
    "barber": {"strong": ("gents haircut", "gents hair cut", "mens haircut", "men's haircut", "gents hair")},
    "bookstore": {"strong": ("kitaabon ki dukaan", "kitabon ki dukaan", "kitaab ki dukaan", "book shop")},
    "cafe": {"weak": ("cappuccino", "croissant", "latte", "espresso")},
    "car-wash": {"strong": ("car washing", "car washing service", "vehicle washing")},
    "catering": {"strong": ("banquet table", "chafing dishes")},
    "cleaning": {"weak": ("mopping", "mop", "spray bottles", "housekeeping", "cleaner in uniform", "sweeping")},
    "coaching-tuition": {"weak": ("equation", "jee", "neet", "teacher explains")},
    "consulting": {"strong": ("business consultants", "management consultants", "business consulting")},
    "dental": {"strong": ("teeth cleaning", "dant ke doctor", "dant doctor"), "weak": ("teeth", "dant", "dantaon")},
    "digital-agency": {"weak": ("campaign", "campaign mockups", "brainstorming", "social media campaign")},
    "fashion-boutique": {"strong": ("designer wear", "ladies designer wear", "designer kapde", "designer kapdon"), "weak": ("designer", "kapdon", "kapde")},
    "hotel": {"avoid": ("ski", "snowy slopes", "skiing")},
    "logistics": {"avoid": ("vessel", "shipyard", "ship yard", "shipbuilding")},
    "petshop": {"strong": ("puppies for sale", "pups for sale", "aquarium shop", "aquarium store", "aquarium ki dukaan", "ornamental fish", "fish tank shop", "एक्वेरियम की दुकान"),
               "weak": ("puppies", "puppy", "kittens")},
    "restaurant": {"weak": ("dining hall", "khane", "khana", "dining")},
    "skin-clinic": {"strong": ("glow treatment", "facial and glow"), "weak": ("facial", "glow")},
}


def apply(niches):
    for nid, extra in EXTRA.items():
        n = niches.get(nid)
        if n is None:
            raise KeyError("vocab for unknown niche %s" % nid)
        for field in ("strong", "weak", "avoid"):
            add = tuple(w for w in extra.get(field, ()) if w not in getattr(n, field))
            if add:
                setattr(n, field, getattr(n, field) + add)
