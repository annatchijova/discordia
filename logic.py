"""
Motor de inferencia: hechos ground, reglas con variables, forward chaining
con registro de justificaciones (qué reglas produjeron cada hecho).

Sin floats en ninguna parte. Todo el estado es tuplas de strings y enteros,
por lo que el resultado es exactamente reproducible.
"""

from typing import Dict, FrozenSet, Iterable, List, Optional, Tuple

# Un hecho ground es (signo, predicado, args)
#   signo: True = afirmado, False = negado
#   ejemplo: (True, "R", ("a", "b"))  ==  R(a,b)
#            (False, "R", ("a", "a")) == ¬R(a,a)
Fact = Tuple[bool, str, Tuple[str, ...]]

# Un literal de regla puede tener variables (strings que empiezan con mayúscula)
Literal = Tuple[bool, str, Tuple[str, ...]]

VARS = ("X", "Y", "Z")


def is_var(term: str) -> bool:
    return term in VARS


class Rule:
    """premisas -> conclusion, con variables universalmente cuantificadas."""

    __slots__ = ("name", "premises", "conclusion")

    def __init__(self, name: str, premises: Tuple[Literal, ...], conclusion: Literal):
        self.name = name
        self.premises = premises
        self.conclusion = conclusion

    def __repr__(self) -> str:
        return f"Rule({self.name})"


def _unify(lit: Literal, fact: Fact, binding: Dict[str, str]) -> Optional[Dict[str, str]]:
    """Intenta unificar un literal con un hecho ground bajo un binding parcial."""
    if lit[0] != fact[0] or lit[1] != fact[1] or len(lit[2]) != len(fact[2]):
        return None
    new = dict(binding)
    for lt, ft in zip(lit[2], fact[2]):
        if is_var(lt):
            if lt in new:
                if new[lt] != ft:
                    return None
            else:
                new[lt] = ft
        elif lt != ft:
            return None
    return new


def _ground(lit: Literal, binding: Dict[str, str]) -> Optional[Fact]:
    args = []
    for t in lit[2]:
        if is_var(t):
            if t not in binding:
                return None
            args.append(binding[t])
        else:
            args.append(t)
    return (lit[0], lit[1], tuple(args))


def negate(f: Fact) -> Fact:
    return (not f[0], f[1], f[2])


def derive(
    base_facts: Iterable[Fact],
    rules: List[Rule],
    max_iterations: int = 64,
) -> Tuple[Dict[Fact, FrozenSet[str]], bool]:
    """
    Forward chaining a punto fijo.

    Devuelve (hechos -> justificacion, consistente).

    La justificacion de un hecho es el conjunto de nombres de reglas usadas en
    la cadena de derivacion completa que lo produjo. Un hecho base tiene
    justificacion vacia.

    consistente = False si se derivo un hecho y su negacion.

    El orden de exploracion es determinista: los hechos se procesan ordenados
    y las reglas en el orden en que fueron declaradas.
    """
    facts: Dict[Fact, FrozenSet[str]] = {}
    for f in base_facts:
        facts[f] = frozenset()

    for _ in range(max_iterations):
        added = False
        # Snapshot ordenado: el orden de iteracion no puede filtrarse al resultado.
        current = sorted(facts.keys())
        for rule in rules:
            bindings: List[Tuple[Dict[str, str], FrozenSet[str]]] = [({}, frozenset())]
            for prem in rule.premises:
                nxt: List[Tuple[Dict[str, str], FrozenSet[str]]] = []
                for binding, just in bindings:
                    for fact in current:
                        u = _unify(prem, fact, binding)
                        if u is not None:
                            nxt.append((u, just | facts[fact]))
                bindings = nxt
                if not bindings:
                    break
            for binding, just in bindings:
                concl = _ground(rule.conclusion, binding)
                if concl is None:
                    continue
                new_just = just | {rule.name}
                if concl not in facts:
                    facts[concl] = new_just
                    added = True
                elif len(new_just) < len(facts[concl]):
                    # Preferimos la justificacion mas corta; desempate lexicografico
                    # para que el resultado no dependa del orden de descubrimiento.
                    facts[concl] = new_just
                    added = True
                elif len(new_just) == len(facts[concl]) and sorted(new_just) < sorted(facts[concl]):
                    facts[concl] = new_just
                    added = True
        if not added:
            break

    consistent = True
    for f in facts:
        if negate(f) in facts:
            consistent = False
            break

    return facts, consistent
