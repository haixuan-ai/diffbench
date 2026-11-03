"""参赛适配器协议：run(scenario, dt) -> 统一状态 dict；不做任何打分。"""
from __future__ import annotations
import platform


class Adapter:
    name = "base"
    def version(self) -> str: raise NotImplementedError
    def available(self) -> tuple[bool, str]: return True, ""
    def meta(self) -> dict: return {"name": self.name, "version": self.version(), "python": platform.python_version()}
    def run(self, scenario: dict, dt: float) -> dict: raise NotImplementedError


def empty_states():
    return {"t": [], "pos": [], "quat": [], "vel": [], "angvel": [], "steps_per_sec": 0.0, "config": {}}
