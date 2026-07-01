from pirl_nav.evaluation import (
    average_clearance,
    detour_ratio,
    jerk_proxy,
    shield_intervention_rate,
    success_from_done,
)


def test_detour_ratio_uses_straight_line_reference() -> None:
    assert detour_ratio(path_length=12.0, straight_line_distance=10.0) == 1.2


def test_jerk_proxy_uses_velocity_command_changes() -> None:
    actions = [[0.0, 0.0], [1.0, 0.0], [1.0, 1.0]]

    assert jerk_proxy(actions, dt=0.5) == 2.0


def test_average_clearance_ignores_infinite_empty_map_value() -> None:
    assert average_clearance([float("inf"), 2.0, 4.0]) == 3.0


def test_success_and_shield_rate_helpers() -> None:
    assert success_from_done(terminated=True, truncated=False, collision=False) is True
    assert success_from_done(terminated=True, truncated=False, collision=True) is False
    assert shield_intervention_rate(shield_intervention_count=2, steps=10) == 0.2
