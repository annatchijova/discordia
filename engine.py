"""
Historiador y runner.

El Historiador es legible desde afuera y opaco hacia adentro (Version B).
Los modulos reciben solamente (query_id, contradiction: bool). El contenido
del registro -- que respondio cada uno, que nogood se genero -- no es
accesible para ellos.

Filtracion parcial declarada: un modulo conoce su propia respuesta y el id de
la query en que choco. De ahi puede inferir que al menos otro modulo respondio
algo incompatible. La opacidad no es total. Se declara aqui en lugar de
presentarse como si lo fuera.

Dependencia del camino declarada: el conjunto de nogoods producido depende del
orden canonico de exploracion. Es una historia de busqueda bajo un orden fijo,
no el mapa semantico de incompatibilidad del universo.
"""

import hashlib
import json
from typing import List, Tuple

from logic import Fact
from module import ABSTAIN, NO, PARALYSIS, YES, ConvictionModule
from world import BASE_FACTS, ONTOLOGIES, all_queries

CANONICALIZE_VERSION = 1
EXPLORATION_ORDER = "ascending_bitmask"


def fact_str(f: Fact) -> str:
    sign = "" if f[0] else "¬"
    return f"{sign}{f[1]}({','.join(f[2])})"


def canonicalize(obj):
    if isinstance(obj, bool):
        return {"__bool__": obj}
    if isinstance(obj, int):
        return {"__int__": str(obj)}
    if isinstance(obj, str):
        return {"__str__": obj}
    if obj is None:
        return {"__null__": True}
    if isinstance(obj, (list, tuple)):
        return {"__list__": [canonicalize(x) for x in obj]}
    if isinstance(obj, dict):
        return {"__dict__": {k: canonicalize(obj[k]) for k in sorted(obj)}}
    raise TypeError(f"no canonicalizable: {type(obj)}")


def seal(payload) -> str:
    blob = json.dumps(canonicalize(payload), sort_keys=True,
                      ensure_ascii=False, separators=(",", ":"))
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()


class Historian:
    """Append-only. Nadie de adentro lo lee."""

    def __init__(self):
        self.entries: List[dict] = []

    def record(self, entry: dict) -> None:
        self.entries.append(entry)

    def contradiction_count(self) -> int:
        return sum(1 for e in self.entries if e["contradiction"])


def run(max_queries: int = 1000, order: str = "descending") -> dict:
    modules = [
        ConvictionModule(name, spec["label"], spec["core"], spec["periphery"],
                         BASE_FACTS, order=order)
        for name, spec in ONTOLOGIES.items()
    ]
    historian = Historian()
    queries = all_queries()

    step = 0
    terminated = "max_queries"
    while step < max_queries:
        query = queries[step % len(queries)]
        query_id = f"q{step:04d}"

        responses = []
        for m in modules:
            verdict, just, used_p = m.answer(query)
            responses.append((m, verdict, just, used_p))

        # Deteccion de contradiccion: existe un par con veredictos opuestos.
        verdicts = {r[0].name: r[1] for r in responses}
        has_yes = any(v == YES for v in verdicts.values())
        has_no = any(v == NO for v in verdicts.values())
        contradiction = has_yes and has_no

        historian.record({
            "query_id": query_id,
            "query": fact_str(query),
            "answers": {m.name: v for m, v, _, _ in responses},
            "justifications": {m.name: sorted(j) for m, _, j, _ in responses},
            "contradiction": contradiction,
            "nogoods_created": [],
            "configs_before": {m.name: m.config for m, _, _, _ in responses},
        })

        if contradiction:
            created = []
            for m, verdict, just, used_p in responses:
                if verdict in (YES, NO):
                    before = m.config
                    outcome = m.apply_contradiction(used_p, just)
                    created.append({
                        "module": m.name,
                        "nogood": sorted(just) if outcome.startswith(("retracted", "paralyzed_after")) else None,
                        "config_before": before,
                        "outcome": outcome,
                    })
            historian.entries[-1]["nogoods_created"] = created

        if all(m.paralyzed for m in modules):
            terminated = "collective_paralysis"
            step += 1
            break

        active = [m for m in modules if not m.paralyzed]
        if len(active) < 2:
            terminated = "insufficient_disputants"
            step += 1
            break

        step += 1

    final_state = [m.state() for m in modules]
    payload = {
        "canonicalize_version": CANONICALIZE_VERSION,
        "exploration_order": order,
        "base_facts": [fact_str(f) for f in BASE_FACTS],
        "steps": step,
        "terminated": terminated,
        "contradictions": historian.contradiction_count(),
        "final_state": final_state,
        "log": historian.entries,
    }
    return {"payload": payload, "seal": seal(payload), "historian": historian}
