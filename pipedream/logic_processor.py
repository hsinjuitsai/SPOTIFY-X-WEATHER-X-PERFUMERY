def handler(pd: "pipedream"):
    """Pipedream adapter. Safety-critical decisions are deterministic."""
    from math import fabs

    source = pd.steps["code"]["$return_value"]
    state = pd.steps["session_manager"]["$return_value"]
    records = pd.steps["get_all_records"]["$return_value"] or []

    def fields(record):
        return record.get("fields", record)

    by_name = {}
    for record in records:
        row = fields(record)
        name = row.get("Name") or row.get("name") or row.get("Scent")
        if name:
            by_name[str(name).casefold()] = row

    def number(row, names, default):
        for name in names:
            if row.get(name) is not None:
                try:
                    return float(row[name])
                except (TypeError, ValueError):
                    pass
        return float(default)

    def clamp(value, low, high):
        return max(low, min(high, value))

    exclusions = [x.strip().casefold() for x in str(state.get("exclusions", "")).split(",") if x.strip() and x.strip().casefold() != "none"]
    temperature = float(source.get("Weather_Temp") or 24)
    humidity = float(source.get("Weather_Humid") or 60)
    energy = clamp(float(source.get("energy") or 0.5), 0, 1)
    valence = clamp(float(source.get("valence") or 0.5), 0, 1)

    previous_energy = state.get("previous_energy")
    previous_valence = state.get("previous_valence")
    delta = 0.0
    if previous_energy is not None and previous_valence is not None:
        delta = (fabs(energy - float(previous_energy)) + fabs(valence - float(previous_valence))) / 2 * 100

    thermal_target = clamp((temperature - 18) / 14 * 10, 0, 10)
    texture_target = clamp((humidity - 35) / 50 * 10, 0, 10)
    calm_target = (1 - energy) * 10
    pierce_target = valence * 10
    ranked = []

    for slot, scent_name in state.get("slots", {}).items():
        row = by_name.get(str(scent_name).casefold(), {})
        searchable = " ".join(str(v) for v in row.values()).casefold() + " " + str(scent_name).casefold()
        excluded = any(term in searchable for term in exclusions)
        cold = number(row, ("cold", "Cold", "冷暖", "Cooling"), 5)
        dry = number(row, ("dry", "Dry", "乾爽"), 5)
        calm = number(row, ("calm", "Calm", "安定"), 5)
        pierce = number(row, ("pierce", "Pierce", "穿透"), 5)
        intensity = number(row, ("intensity", "Intensity", "強度"), 4)
        thermal = 100 - abs(cold - thermal_target) * 10
        texture = 100 - abs(dry - texture_target) * 10
        emotion = ((100 - abs(calm - calm_target) * 10) + (100 - abs(pierce - pierce_target) * 10)) / 2
        score = -1 if excluded else round(clamp(thermal * .35 + texture * .25 + emotion * .40, 0, 100), 2)
        ranked.append({"slot": slot, "name": scent_name, "score": score, "intensity": intensity, "excluded": excluded})

    ranked.sort(key=lambda item: item["score"], reverse=True)
    ratios = {slot: 0 for slot in state.get("slots", {})}
    safe = [item for item in ranked if not item["excluded"]][:3]
    for item, ratio in zip(safe, (60, 20, 20)):
        ratios[item["slot"]] = ratio
    if safe:
        ratios[safe[0]["slot"]] += 100 - sum(ratios.values())

    fan_speed = round(25 + energy * 45)
    if delta > 40:
        fan_speed += 10
    if safe and safe[0]["intensity"] <= 3:
        fan_speed += 10
    elif safe and safe[0]["intensity"] >= 5:
        fan_speed -= 10
    fan_speed = round(clamp(fan_speed, 0, 100))

    current_song = source.get("song", "Unknown")
    return {
        "metrics": {
            "current_song": current_song,
            "previous_song": state.get("previous_song"),
            "is_song_changed": current_song != state.get("previous_song"),
            "energy": energy,
            "valence": valence,
            "temperature": temperature,
            "humidity": humidity,
            "delta": round(delta, 2),
            "elapsed_minutes": state.get("elapsed_minutes", 0),
            "is_learning_mode": state.get("elapsed_minutes", 0) < 30,
        },
        "decision": {"ratios": ratios, "fan_speed": fan_speed},
        "rankings": ranked,
    }

