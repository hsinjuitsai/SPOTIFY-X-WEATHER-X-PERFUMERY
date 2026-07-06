from dataclasses import dataclass, field


@dataclass(frozen=True)
class Capsule:
    slot: str
    name: str
    cold: float = 5.0
    dry: float = 5.0
    calm: float = 5.0
    pierce: float = 5.0
    intensity: float = 4.0
    ingredients: tuple[str, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class Context:
    temperature: float
    humidity: float
    valence: float
    energy: float
    elapsed_minutes: int
    delta_percent: float = 0.0
    exclusions: tuple[str, ...] = field(default_factory=tuple)
    health_multiplier: float = 1.0


@dataclass(frozen=True)
class Decision:
    ratios: dict[str, int]
    rankings: list[dict[str, float | str]]
    fan_speed: int
    learning_mode: bool
    thermal_state: str

