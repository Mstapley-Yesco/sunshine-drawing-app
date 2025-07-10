def find_best_matches(data, target_sq_ft, target_changers, bonfire, trv, ethanol, nitro, top_n=3):
    def score(row):
        score = 0

        # 🔢 Square footage: weight by closeness (smaller difference is better)
        score += abs(row["sq_ft"] - target_sq_ft) * 2

        # 🔢 Price changers: exact match preferred
        score += abs(row["price_changers"] - target_changers) * 10

        # ✅ Panel mismatch penalties
        if row.get("has_bonfire", False) != bonfire:
            score += 5
        if row.get("has_trv", False) != trv:
            score += 5
        if row.get("has_ethanol", False) != ethanol:
            score += 5
        if row.get("has_nitro", False) != nitro:
            score += 5

        return score

    # 🧮 Apply scoring to each row
    scored = data.copy()
    scored["score"] = scored.apply(score, axis=1)

    # 🎯 Return top N matches with lowest scores
    return scored.sort_values("score").head(top_n)
