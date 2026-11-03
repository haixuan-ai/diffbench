# Adding an engine

Implement `diffbench.adapters.base.Adapter`:
```python
class MyEngine(Adapter):
    name = "my_engine"
    def version(self): return "my_engine 1.2.3 (config summary)"
    def available(self): return (True, "")          # or (False, "reason") if not installed
    def run(self, scenario, dt) -> dict:             # scenario: one dict from spec.scenarios()
        ...  # return {"t":[...], "pos":[[[x,y,z] per body] per sample], "quat":[wxyz...], "vel":[COM linear], "angvel":[world frame], "steps_per_sec": float, "config": {...}}
```
Sample every `spec.sample_every(dt)` steps (≈ 100 Hz output). Register it in `adapters/__init__.py`. Rules: engine defaults only; align only what Protocol B aligns; read state after forward kinematics; validate conventions with `free_fall` and `projectile_spin` first (both must give ~0 error for any correct adapter). Never compute scores in the adapter. Closed-source engines can join through an HTTP service with the same response format.
