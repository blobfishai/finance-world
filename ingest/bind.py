#!/usr/bin/env python3
"""Strict binding of a TaskSpec to the world. Three outcomes, no fourth."""
from capability import World

def bind(spec, world: World):
    missing_caps = [c for c in spec.capabilities
                    if c not in world.tables and c not in world.servers]
    if missing_caps:
        spec.bind_status = "missing_capability"
        spec.bind_detail = "world lacks: " + ", ".join(sorted(missing_caps))
        return spec
    absent = []
    for e in spec.entities:
        if world.find_entity(e) is None:
            nm = world.near_misses(e)
            hint = f" (near: {nm[0][1]})" if nm else ""
            absent.append(f"{e}{hint}")
    if absent:
        spec.bind_status = "absent_entity"
        spec.bind_detail = ("question names entities this world does not have: "
                            + "; ".join(absent)
                            + " — ship as an empty-answer trap or reject; never rebind")
        return spec
    spec.bind_status = "bound"
    return spec
