def calculate_verdict(rule_score: float, ml_probability: float) -> dict:
    """
    Calculate the final threat verdict using a weighted combination of
    rule-engine score (deterministic) and ML probability (statistical).

    Rules get 70% weight (interpretable signals), ML gets 30% supplementary weight.

    Thresholds:
      - Dangerous: rule_score >= 50 OR combined >= 48 OR (has_rules AND combined >= 40)
      - Suspicious: rule_score >= 15 OR combined >= 18 OR ml_probability >= 0.55
      - Safe: clean input with rule_score == 0 and low ML probability
    """
    ml_score = ml_probability * 100
    combined_score = (0.70 * rule_score) + (0.30 * ml_score)

    has_rule_signals = rule_score > 0

    # Dangerous: high severity rule signals or high combined score
    if rule_score >= 50 or combined_score >= 48 or (has_rule_signals and combined_score >= 40):
        verdict = "Dangerous"
        confidence = round(min(96.0, max(80.0, max(combined_score, rule_score))), 1)

    # Suspicious: any rule indicators detected (rule_score >= 15) or moderate ML confidence
    elif rule_score >= 15 or combined_score >= 18 or ml_probability >= 0.55:
        verdict = "Suspicious"
        calc_conf = 55.0 + max(rule_score, combined_score) * 0.45
        confidence = round(max(55.0, min(76.0, calc_conf)), 1)

    # Safe: no rule triggers detected and low ML probability
    else:
        verdict = "Safe"
        confidence = round(min(96.0, max(82.0, 92.0 - combined_score * 0.5)), 1)

    return {
        "verdict": verdict,
        "confidence": confidence,
        "combined_score": round(combined_score, 1)
    }
