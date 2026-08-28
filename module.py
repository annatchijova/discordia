"""
Modulo de conviccion.

Mantiene un core inamovible y una configuracion activa de periphery.
Recibe del Historiador un unico bit: contradiction=True, mas el id de la query.
Nunca ve el contenido del Historiador ni las respuestas de los otros modulos.

Regeneracion sintactica: la siguiente configuracion se elige recorriendo el
espacio de subconjuntos de periphery en orden canonico ascendente sobre el
bitmask, saltando las que estan en el nogood store y las internamente
inconsistentes. NO consulta el historial de conflictos mas alla de ese filtro,
y NO usa el id de la query. Por construccion, el modulo no puede aprender a
esquivar conflictos.
"""

from typing import List, Optional, Set, Tuple

from logic import Fact, Rule, derive, negate

YES = "YES"
NO = "NO"
ABSTAIN = "ABSTAIN"
PARALYSIS = "PARALYSIS"


class ConvictionModule:
    def __init__(self, name: str, label: str, core: List[Rule], periphery: List[Rule],
                 base_facts: Tuple[Fact, ...], order: str = "descending"):
        self.name = name
        self.order = order
        self.label = label
        self.core = core
        self.periphery = periphery
        self.base_facts = base_facts

        # Nogood store persistente: nunca se vacia.
        # v0.2: un nogood es el CONJUNTO de indices de periphery que aparecieron
        # en la justificacion del choque, no la configuracion entera.
        self.nogoods: Set[frozenset] = set()
        self.paralyzed = False
        self.config: Optional[int] = None
        self.regenerations = 0
        self._regenerate()

    # -- espacio de configuraciones -----------------------------------------

    def _rules_for(self, mask: int) -> List[Rule]:
        active = [r for i, r in enumerate(self.periphery) if mask & (1 << i)]
        return self.core + active

    def _admissible(self, mask: int) -> bool:
        active = frozenset(i for i in range(len(self.periphery)) if mask & (1 << i))
        for ng in self.nogoods:
            if ng <= active:
                return False
        _, consistent = derive(self.base_facts, self._rules_for(mask))
        return consistent

    def _regenerate(self) -> None:
        """Primera configuracion admisible en orden canonico ascendente."""
        space = 1 << len(self.periphery)
        candidates = range(space) if self.order == "ascending" else range(space - 1, -1, -1)
        for mask in candidates:
            if self._admissible(mask):
                self.config = mask
                self.regenerations += 1
                return
        self.config = None
        self.paralyzed = True

    # -- responder ----------------------------------------------------------

    def answer(self, query: Fact) -> Tuple[str, frozenset, bool]:
        """
        Devuelve (respuesta, justificacion, uso_periphery).

        YES si deriva la query, NO si deriva su negacion, ABSTAIN si ninguna.
        """
        if self.paralyzed or self.config is None:
            return PARALYSIS, frozenset(), False

        facts, _ = derive(self.base_facts, self._rules_for(self.config))
        neg = negate(query)

        if query in facts:
            just = facts[query]
            verdict = YES
        elif neg in facts:
            just = facts[neg]
            verdict = NO
        else:
            return ABSTAIN, frozenset(), False

        periphery_names = {r.name for r in self.periphery}
        used_periphery = bool(just & periphery_names)
        return verdict, just, used_periphery

    # -- coercion -----------------------------------------------------------

    def apply_contradiction(self, used_periphery: bool,
                            justification: frozenset = frozenset()) -> str:
        """
        Coercion mecanica. Se invoca cuando el Historiador emitio
        contradiction=True y este modulo participo del choque.

        Si la respuesta uso al menos una regla de periphery: la configuracion
        actual entra al nogood store y el modulo regenera.
        Si la respuesta salio solo del core: el modulo entra en paralisis.
        """
        if self.paralyzed:
            return "already_paralyzed"
        if used_periphery:
            names = {r.name: i for i, r in enumerate(self.periphery)}
            culprits = frozenset(names[n] for n in justification if n in names)
            self.nogoods.add(culprits)
            self._regenerate()
            return "paralyzed_after_retraction" if self.paralyzed else "retracted"
        self.paralyzed = True
        self.config = None
        return "paralyzed_core_conflict"

    def state(self) -> dict:
        return {
            "module": self.name,
            "label": self.label,
            "config": self.config,
            "active_rules": sorted(
                r.name for i, r in enumerate(self.periphery)
                if self.config is not None and self.config & (1 << i)
            ),
            "nogood_count": len(self.nogoods),
            "paralyzed": self.paralyzed,
            "regenerations": self.regenerations,
        }
