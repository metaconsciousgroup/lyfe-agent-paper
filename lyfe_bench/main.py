import json

from collections import namedtuple
from pathlib import Path

from lyfe_bench.benchmarks.env import BenchmarkEnv
from lyfe_bench.environments.testbed_env import env as Env
from lyfe_bench.utils.get_specs import get_specs

MOCKACTIONPATH = Path("./tests/")

WorldTime = namedtuple("WorldTime", ["year", "month", "day", "hour"])
default_world_time = WorldTime(2020, 1, 1, 7)


def run_env(
    mock_action=None
):
    with open(MOCKACTIONPATH / "talk.json", "r") as f:
        actions = json.load(f)

    env = Env(
        agents=['agent_0'],
        frame_rate=10,
        sim_speed=100,
        location=False,
    )
    env.reset()

    observation = env.get_observations(0)
    assert set(["time", "visible_creatures", "message", "item", "talk", "nearby_creature"]) <= set(observation.keys()), "Observation keys are not correct"
    action = actions[0]
    env.set_action(0, action)


def run_bench():
    specs = get_specs("info/get_info/basic_get_info")
    BenchmarkEnv(
        agents=['agent_0'],
        env_specs=specs["env"],
        eval_specs=specs["evaluation"],
    )


if __name__ == "__main__":
    run_env()
    run_bench()