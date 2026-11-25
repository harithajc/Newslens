import re

# 1. Keywords for each topic
TOPIC_WORDS = {
    "health":  ["health", "hospital", "doctor", "disease", "vaccine", "virus",
                "cancer", "dengue", "flu", "medicine", "patient", "surgery"],
    "weather": ["rain", "flood", "cyclone", "storm", "heatwave", "weather",
                "monsoon", "fog", "temperature"],
    "school":  ["school", "college", "exam", "student", "university",
                "education", "teacher", "neet", "jee"],
    "law":     ["court", "high court", "supreme court", "judge", "bail",
                "jail", "verdict", "ruling", "petition", "tribunal", "law"],
    "sports":  ["cricket", "match", "tournament", "league", "goal", "century",
                "wicket", "batter", "bowler", "ipl", "olympic", "medal"],
    "money":   ["price", "rupee", "inflation", "economy", "economic", "gdp",
                "tax", "bank", "loan", "debt", "budget", "stock", "sensex",
                "nifty", "fuel", "petrol", "diesel", "gold", "market", "jobs"],
    "warning": ["accident", "crash", "fire", "blast", "killed", "kills",
                "death", "rams", "earthquake", "alert", "outbreak"],
    "transport": ["train", "bus", "flight", "airport", "railway", "metro",
                  "station", "road", "bridge", "traffic", "vehicle"],
}

# 2. Count keyword hits for each topic and pick the winner
def pick_topic(headline, summary=""):
    # the headline is repeated, so it counts double
    text = ((headline + " ") * 2 + summary).lower()
    best_topic, best_score = "newspaper", 0      # "newspaper" = no clear topic
    for topic, words in TOPIC_WORDS.items():
        score = 0
        for word in words:
            # \b = word boundary, so "tax" does not match "taxi"
            # s? lets the word end with an optional "s"
            score += len(re.findall(r"\b" + re.escape(word) + r"s?\b", text))
        if score > best_score:
            best_topic, best_score = topic, score
    return best_topic

# 3. Plan the 4 panels: which scene and which robot mood in each
def panel_plan(topic):
    scene = "magnifier" if topic == "newspaper" else topic
    if topic == "warning":
        # sad or serious news: the robot stays calm, never cheerful
        moods = ["neutral", "thinking", "thinking", "neutral"]
    else:
        moods = ["neutral", "surprised", "thinking", "happy"]
    scenes = ["newspaper", scene, scene, "checkmark"]
    return [{"scene": s, "mood": m} for s, m in zip(scenes, moods)]

# ---- Tests: (headline, summary, topic I expect) ----
tests = [
    ("$135 billion in debt, still getting loans: Who is keeping Pakistan afloat, and why", "", "money"),
    ("Azam Khan walks out of Dasna jail after getting interim bail", "", "law"),
    ("Chhattisgarh-born, MP-groomed batter Harpreet hits century for UAE", "", "sports"),
    ("Telangana former CM KCR's long-time attendant, another youth killed as truck rams bike", "", "warning"),
    ("Why Economic Stats Don't Answer Young Indians' Questions", "", "money"),
    ("Heavy rain floods streets, schools shut for two days", "", "weather"),
    ("Customs seize 11 air rifles from passengers at Kochi airport", "", "newspaper"),
    ("IndiGo joins Air India, Akasa in suspending Saudi flights until November 30", "", "newspaper"),
    ("The taxi driver won the case", "", "law"),
]

for headline, summary, expected in tests:
    topic = pick_topic(headline, summary)
    result = "OK  " if topic == expected else "DIFF"
    print(f"{result} expected={expected:9} got={topic:9} | {headline[:60]}")

print()
print("Plan for a money story:")
for i, p in enumerate(panel_plan("money"), start=1):
    print(f"  panel {i}: scene={p['scene']}, mood={p['mood']}")