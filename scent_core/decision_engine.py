from .models import Capsule, Context, Decision


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def _excluded(capsule: Capsule, exclusions: tuple[str, ...]) -> bool:
    text = " ".join((capsule.name, *capsule.ingredients)).casefold()
    return any(term.strip().casefold() in text for term in exclusions if term.strip())


def _score(capsule: Capsule, context: Context) -> float:
    thermal_target = _clamp((context.temperature - 18) / 14 * 10, 0, 10)
    texture_target = _clamp((context.humidity - 35) / 50 * 10, 0, 10)
    calm_target = (1 - _clamp(context.energy, 0, 1)) * 10
    pierce_target = _clamp(context.valence, 0, 1) * 10
    thermal = 100 - abs(capsule.cold - thermal_target) * 10
    texture = 100 - abs(capsule.dry - texture_target) * 10
    emotion = ((100 - abs(capsule.calm - calm_target) * 10) +
               (100 - abs(capsule.pierce - pierce_target) * 10)) / 2
    return round(_clamp(thermal * .35 + texture * .25 + emotion * .40, 0, 100), 2)


def decide(capsules: list[Capsule], context: Context) -> Decision:
    if not capsules:
        raise ValueError("At least one capsule is required")
    ranked = []
    for capsule in capsules:
        score = -1.0 if _excluded(capsule, context.exclusions) else _score(capsule, context)
        ranked.append({"slot": capsule.slot, "name": capsule.name, "score": score})
    ranked.sort(key=lambda item: float(item["score"]), reverse=True)

    ratios = {capsule.slot: 0 for capsule in capsules}
    safe = [item for item in ranked if float(item["score"]) >= 0][:3]
    for item, ratio in zip(safe, (60, 20, 20)):
        ratios[str(item["slot"])] = ratio
    if safe:
        ratios[str(safe[0]["slot"])] += 100 - sum(ratios.values())

    fan = round(25 + _clamp(context.energy, 0, 1) * 45)
    if context.delta_percent > 40:
        fan += 10
    winner = next((c for c in capsules if safe and c.slot == safe[0]["slot"]), None)
    if winner and winner.intensity <= 3:
        fan += 10
    elif winner and winner.intensity >= 5:
        fan -= 10
    fan = round(_clamp(fan * _clamp(context.health_multiplier, 0, 1), 0, 100))
    thermal = "warm" if context.temperature >= 27 else "cool" if context.temperature <= 20 else "neutral"
    return Decision(ratios, ranked, fan, context.elapsed_minutes < 30, thermal)

