from scent_core import Capsule, Context, decide


CAPSULES = [
    Capsule("slot_a", "Spice Market", intensity=5),
    Capsule("slot_b", "Amber Wood"),
    Capsule("slot_c", "Jaffa Clementine", intensity=3),
    Capsule("slot_d", "Floral Musk"),
]


def context(**changes):
    values = dict(temperature=25, humidity=60, valence=.6, energy=.7, elapsed_minutes=10)
    values.update(changes)
    return Context(**values)


def test_ratios_total_one_hundred():
    result = decide(CAPSULES, context())
    assert sum(result.ratios.values()) == 100
    assert sorted(result.ratios.values(), reverse=True) == [60, 20, 20, 0]


def test_excluded_capsule_is_zero():
    result = decide(CAPSULES, context(exclusions=("Amber",)))
    assert result.ratios["slot_b"] == 0


def test_learning_period_uses_persisted_elapsed_minutes():
    assert decide(CAPSULES, context(elapsed_minutes=29)).learning_mode is True
    assert decide(CAPSULES, context(elapsed_minutes=30)).learning_mode is False


def test_health_reset_stops_fan():
    assert decide(CAPSULES, context(health_multiplier=0)).fan_speed == 0

