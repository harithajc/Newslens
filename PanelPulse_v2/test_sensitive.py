import comic


HEADLINES = [
    ("Truck crash leaves five people injured on highway", True),
    ("Two people killed in late-night road accident", True),
    ("Local resident dies after a long illness", True),
    ("Police investigate murder of shop owner", True),
    ("Fire destroys homes in crowded neighborhood", True),
    ("Flooding forces families to leave riverside homes", True),
    ("Cyclone damages houses along the coast", True),
    ("Earthquake shakes city, residents report damage", True),
    ("Landslide blocks road after heavy rain", True),
    ("Explosion injures workers at industrial site", True),
    ("Wildfire spreads across the forest reserve", True),
    ("Stampede at event leaves several people injured", True),
    ("Election campaign focuses on jobs and education", True),
    ("Political parties announce a joint rally", True),
    ("Opposition questions the new government decision", True),
    ("Centre faces questions over delimitation plan", True),
    ("Lok Sabha debate continues over the bill", True),
    ("PARLIAMENT debate continues late into the night", True),
    ("Candidate releases manifesto ahead of the vote", True),
    ("Akhilesh Yadav hits out at the campaign strategy", True),
    ("Rahul Gandhi and Mamata Banerjee attend the rally", True),
    ("Devotees gather at temple for evening puja", True),
    ("Pilgrimage route to gurdwara reopens after repairs", True),
    ("Aarti and Deepam celebrations captured in videos", True),
    (
        "Gen Z, farmers angry: Akhilesh says Centre using delimitation "
        "to divert attention",
        True,
    ),
    (
        "Vetrivel, Veeravel: Historic lighting of Deepam, celebrations "
        "captured in videos",
        True,
    ),
    (
        "Trump admin may raise tariffs on many countries including India "
        "and China: Report",
        False,
    ),
    ("Central bank holds interest rates as inflation eases", False),
    ("India wins cricket series after close final", False),
    ("City hospital opens a new wing for children", False),
    ("Rain expected across the region this weekend", False),
    ("Court publishes annual report on case backlogs", False),
    ("New school library opens to students", False),
    ("Central bank announces a change to its lending policy", False),
    ("Campaigner wins local award for community work", False),
]


def run_tests():
    wrong = []
    for headline, expected in HEADLINES:
        actual = comic.is_sensitive(headline, "")
        if actual != expected:
            wrong.append((headline, expected, actual))

    sensitive_plan = comic.panel_plan("newspaper", sensitive=True)
    assert sensitive_plan[0]["scene"] == "newspaper_calm"
    assert sensitive_plan[3]["scene"] == "closing_calm"
    assert all(panel["scene"] != "checkmark" for panel in sensitive_plan)
    assert all(panel["mood"] != "happy" for panel in sensitive_plan)

    correct = len(HEADLINES) - len(wrong)
    print(f"{correct} correct out of {len(HEADLINES)}")
    for headline, expected, actual in wrong:
        print(f"Wrong: {headline!r} (expected {expected}, got {actual})")
    return not wrong


if __name__ == "__main__":
    raise SystemExit(0 if run_tests() else 1)
