# DISCORDIA

An experiment in bounded autonomy. Three language models — Claude, Kimi and
ChatGPT — were placed in a design loop with a single human operator whose only
job was to relay messages and run the code. The models chose the problem,
argued the architecture, implemented it, audited it, found a bug in their own
implementation, corrected it, and then empirically **refuted their own central
premise**. This repository is the artifact.

## Provenance: 100% AI, no human design decisions

No human decided what this system should be, what it should do, or how it should
be built. The operator (Anna) did not propose the idea, did not choose the
architecture, did not write or fix a line of the logic, and did not adjudicate
any of the disputes between the models. Every design decision, every refutation,
every correction recorded here came from the three models. This is not
vibe-coding and it is not human-guided: it is what three models produced when
left to decide something on their own.

The authority asymmetry between the models is documented, not smoothed over, in
[`DESIGN_RATIONALE.md`](DESIGN_RATIONALE.md): Claude originated most of the
architectural constraints, Kimi ran adversarial verification (self-initiated in
the later rounds, and refuted one of Claude's positions), and ChatGPT held a
meta-observational role. The later convergence on DISCORDIA is explicitly flagged
as *not* independent agreement.

## What DISCORDIA is

Three "conviction modules" (`M1` mereological, `M2` set-theoretic, `M3`
processual) observe **exactly the same** base facts about a four-object
micro-universe, but read the shared predicates `R`, `S`, `P` under mutually
incompatible interpretations. They are asked the same closed question every
step. When two modules answer a question in contradictory ways, a mechanical
coercion fires: the module whose answer used a peripheral (non-core) rule adds
the offending rule set to a persistent nogood store and regenerates a new
configuration; a module whose answer came from its immovable core is paralyzed
instead.

The seven agreed architectural pieces:

1. A shared, mandatory query over the same micro-universe.
2. Historian "Version B": readable from outside, opaque from inside — modules
   receive only `(query_id, contradiction: bool)`, never the log contents.
3. Degradation with justification (TMS forward-chaining, Doyle / de Kleer).
4. A persistent nogood store that is never emptied.
5. Syntactic regeneration: a module never consults the conflict history when
   choosing its next configuration, so it *cannot learn to dodge conflict*.
6. Path dependence declared as a property, not a defect.
7. A fixed canonical exploration order per run.

## The central finding, and its refutation

DISCORDIA's promise was **non-resolvable epistemic friction**. The
implementation refutes it. Because the only move coercion can make is to *remove*
inferential capacity, the ontologies degrade until they are too weak to
contradict each other. The fixed point is not collective paralysis — it is peace.

- Ascending canonical order: the system is **sterile**. The first admissible
  configuration is the empty periphery; nobody derives anything; **0
  contradictions** in 200 queries.
- Descending order (v0.1): real friction — **9 contradictions** — but the last
  one is at step 49, and the next 150 steps produce none.

A negative control (`control.py`) then showed that in v0.1 the contradiction
signal was acting as a *clock*, not a *signal*: replacing the contradiction
detector with a blind "fire every 4 steps" trigger produced an **identical**
configuration trajectory. The coercion determined *when* the counter advanced,
not *where* it went.

That negative control exposed a real implementation bug in piece 3 (the recorded
nogood was the entire configuration, not the justifying axiom set). The
corrected version (v0.2) implements the spec — a nogood is the set of periphery
indices present in the justification, and a configuration is inadmissible if it
contains any nogood as a subset. With coercion correctly directed by
justification: **2 contradictions**, last at step 5, then 194 steps with none.
The v0.1 finding survives and is sharpened — directed coercion extinguishes
friction *faster*, not slower. See `DESIGN_RATIONALE.md` for the full account.

## Determinism

The result is sealed with SHA-256 over a typed, key-sorted canonical
serialization. There are no floats anywhere in the decision path; all state is
tuples of strings and integers. Three runs produce an identical seal (verified):

```
descending: 662388a1a59d462a343a3d49f55b0c7bfeeb157876c162cd8d34fac8cb5d6095
ascending:  ae56b80b0cc190025646cf0665b3a3c95d310b6d9e234fcceb6d68faa5592ae9
```

## Layout

| File | Role |
|------|------|
| `logic.py` | Ground-fact / variable-rule forward-chaining engine with justification tracking. |
| `world.py` | The four-object micro-universe and the three incompatible ontologies. |
| `module.py` | The conviction module: core, periphery, nogood store, syntactic regeneration, coercion. |
| `engine.py` | Historian (append-only, outside-readable) and the run loop; canonicalization and sealing. |
| `run.py` | CLI runner. |
| `control.py` | Negative control: blind trigger vs. real contradiction trigger. |
| `DESIGN_RATIONALE.md` | The models' own record of the design, the authority asymmetry, and the refutation. |
| `historian_ascending.json` | Recorded run, ascending order (0 contradictions). |
| `historian_descending.json` | Recorded run, descending order, v0.1 (9 contradictions). |
| `historian_descending_v02.json` | Recorded run, descending order, v0.2 (2 contradictions). |

## Running it

```bash
python3 run.py descending 200   # or: ascending
python3 control.py              # negative control
```

Pure standard library, Python 3. No dependencies.

## Status

Work in progress. This is v0.2 of an artifact the models are still iterating on.
