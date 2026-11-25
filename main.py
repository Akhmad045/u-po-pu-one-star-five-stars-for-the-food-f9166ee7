#!/usr/bin/env python3
"""One Star, Five Stars for the Food — make.fun bounty entry.

Writes exactly one sentence to /output/entry.txt: a one-star review of
planet Earth by an alien tourist that still compliments the food. The
pick: Earth's welcome was a queue, a form and a sunburn — but the street
noodles were so good the tourist told its home planet to invade just for
the recipe. Alien voice (home planet, invasion), a grievance worth one
star, a real food compliment, and the turn is the punchline.

Usage:
    python3 main.py                  # write the line to /output/entry.txt
    python3 main.py --dest out.txt   # write it somewhere else instead
    python3 main.py --self-test      # check the gate, print the hash, exit
"""

import argparse
import hashlib
import sys
from pathlib import Path

# The line. One sentence, well under 200 characters, no padding.
PICK = (
    "One star \u2014 Earth's welcome was a queue, a form, and a sunburn, "
    "but the street noodles were so good I told my home planet we should "
    "invade just for the recipe."
)

# Every line drafted for this bounty, in the order written. Each was
# weighed against the judge brief (on-topic first, then a convincingly
# alien voice, then complaint + compliment both landing with a funny
# turn, then tightness, then freshness) and against the one-liner
# top-3 bar of about 0.71. The notes say why each one lost to the pick.
CONTENDERS = (
    # PICK. Alien voice (home planet, invade), concrete grievance
    # (queue, form, sunburn), real food compliment (street noodles),
    # and the turn is the punchline: invade just for the recipe.
    "One star \u2014 Earth's welcome was a queue, a form, and a sunburn, "
    "but the street noodles were so good I told my home planet we should "
    "invade just for the recipe.",
    # Closest rival. Third eye + citizenship is a lovely alien turn,
    # but "rain fell sideways" is a generic tourist complaint next to
    # the pick's queue/form/sunburn triple.
    "Earth gets one star: the locals screamed at my third eye, the rain "
    "fell sideways, but the noodles were so good I briefly considered "
    "applying for citizenship.",
    # "Home planet before it exploded" is the most alien compliment of
    # the set, but the grievance (a 'quick' coffee queue) is thin for
    # one star, and the sadness blunts the joke.
    "One star \u2014 I flew 40 light-years, waited in line for a 'quick' "
    "coffee, and stayed only because the dumplings tasted like my home "
    "planet used to before it exploded.",
    # Good turn (forgave the species for exactly one meal), but the
    # grievance is a list of charges and the kebab lands after the
    # complaint rather than turning on it.
    "One star: Earth charged me for water, fined me for parking my "
    "saucer, and then handed me a kebab so good I forgave the entire "
    "species for exactly one meal.",
    # Tentacles + weeping into the broth is vivid, but "weather changed
    # its mind hourly" is the most generic complaint in the set.
    "Earth, one star: the humans stared at my tentacles, the weather "
    "changed its mind hourly, but the ramen was so good I wept into the "
    "broth and ordered a second bowl.",
    # Strong grievance (luggage lost in orbit, no ceiling) and a real
    # compliment, but "booked a return trip I cannot afford" is a
    # shrug where the pick's invasion is a punchline.
    "Gave Earth one star: my luggage was lost in orbit, my room had no "
    "ceiling, but the fried chicken was so good I have already booked a "
    "return trip I cannot afford.",
    # "The only honest thing on this damp, overpriced rock" is a great
    # line, but the review leans complaint-heavy and the food gets one
    # clause instead of a turn.
    "One star: the locals call staring 'hospitality', the rain has no "
    "off switch, and the tacos are the only honest thing on this entire "
    "damp, overpriced rock.",
    # "Charges rent for air" is a sharp grievance and the noodles
    # forgive a whole planet, but it reads as two complaints stapled
    # to a compliment rather than one turn.
    "Earth, one star: I was fined for hovering, rained on for six days "
    "straight, and then a bowl of noodles made me forgive a planet that "
    "charges rent for air.",
    # Longest of the set and the sunburn/parking-fine/taco triple is
    # strong, but "apologised to the cook in my own language" is a
    # second punchline competing with the taco itself.
    "One star: I crossed forty light-years for Earth's hospitality and "
    "got a sunburn, a parking fine, and a taco so perfect I ate three "
    "and apologised to the cook in my own language.",
    # "Filed for a refund on the whole trip" is a funny alien-bureaucrat
    # image, but the wifi/queues grievance is the generic-tourist
    # version of the pick's queue/form/sunburn.
    "I gave Earth one star because the wifi is a myth, the queues are a "
    "lifestyle, and the street food is the only reason I have not filed "
    "for a refund on the whole trip.",
    # "Cross the galaxy again just to complain in person" is a good
    # alien turn, but inconsistent gravity + queuing is two grievances
    # where the pick's triple lands as one welcome.
    "I rate Earth one star: the gravity is inconsistent, the humans "
    "queue for everything, and the dumplings are so good I would cross "
    "the galaxy again just to complain about them in person.",
    # The hotel/gravity/species-lifespan setup is very alien, yet the
    # dumpling compliment ("miss a planet I have never lived on") asks
    # the reader to work too hard for the joke.
    "One star \u2014 my hotel had no gravity controls, checkout took "
    "longer than my species' lifespan, and yet the dumplings made me "
    "miss a planet I have never lived on.",
)


def self_test() -> int:
    """Check the gate on the pick and on every contender."""
    text = PICK
    encoded = text.encode("utf-8")
    problems = []
    if not 1 <= len(text) <= 200:
        problems.append(f"pick is {len(text)} chars, gate is 1-200")
    if text != text.strip():
        problems.append("pick has leading/trailing whitespace")
    if text.count(".") != 1 or not text.endswith("."):
        problems.append("pick is not exactly one sentence")
    for i, cand in enumerate(CONTENDERS, 1):
        if not 1 <= len(cand) <= 200:
            problems.append(f"contender {i} is {len(cand)} chars")
        if cand != cand.strip():
            problems.append(f"contender {i} has padding whitespace")
        if cand.count(".") != 1 or not cand.endswith("."):
            problems.append(f"contender {i} is not one sentence")
    if len(set(CONTENDERS)) != len(CONTENDERS):
        problems.append("contenders are not all distinct")
    if PICK not in CONTENDERS:
        problems.append("pick is not among the contenders")
    # The file a plain run writes must be exactly the pick, byte for byte.
    import tempfile
    with tempfile.TemporaryDirectory() as tmp:
        probe = Path(tmp) / "entry.txt"
        probe.write_text(PICK, encoding="utf-8")
        if probe.read_bytes() != encoded:
            problems.append("round-tripped pick differs from PICK")
    if problems:
        for problem in problems:
            print(f"FAIL: {problem}", file=sys.stderr)
        return 1
    print(f"OK: pick is {len(text)} chars, {len(encoded)} bytes, "
          f"one sentence, gate-clean")
    print(f"OK: {len(CONTENDERS)} contenders, all distinct and gate-clean")
    print(f"sha256: {hashlib.sha256(encoded).hexdigest()}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dest", default="/output/entry.txt",
                        help="where to write the entry (default: %(default)s)")
    parser.add_argument("--self-test", action="store_true",
                        help="check the gate and exit")
    args = parser.parse_args()
    if args.self_test:
        return self_test()
    dest = Path(args.dest)
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(PICK, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
