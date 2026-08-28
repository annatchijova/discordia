"""
El micro-universo y las tres ontologias incompatibles.

Los tres modulos observan EXACTAMENTE los mismos hechos base. Difieren en lo
que esos hechos significan: cada ontologia lee los mismos predicados R, S, P
bajo una interpretacion distinta, y por eso sus reglas son incompatibles.

Ninguna ontologia puede leer el core ni el periphery de las otras.
"""

from logic import Fact, Rule

OBJECTS = ("a", "b", "c", "d")

# Hechos base compartidos. Esto es "el mundo": lo unico que las tres ven igual.
BASE_FACTS: tuple[Fact, ...] = (
    (True, "R", ("a", "b")),
    (True, "R", ("b", "c")),
    (True, "R", ("c", "d")),
    (True, "S", ("a", "c")),
    (True, "S", ("b", "d")),
    (True, "P", ("d",)),
)


# ---------------------------------------------------------------------------
# M1 - Mereologica.  R(x,y) = "x es parte de y".  S(x,y) = "x es adyacente a y".
#                    P(x)   = "x es un componente atomico".
# ---------------------------------------------------------------------------

M1_CORE = [
    Rule("m1.core.irreflexive", ((True, "R", ("X", "Y")),), (False, "R", ("X", "X"))),
]

M1_PERIPHERY = [
    # La parte de una parte es parte del todo.
    Rule("m1.p.transitive", ((True, "R", ("X", "Y")), (True, "R", ("Y", "Z"))),
         (True, "R", ("X", "Z"))),
    # Nada es parte de su propia parte.
    Rule("m1.p.antisymmetric", ((True, "R", ("X", "Y")),), (False, "R", ("Y", "X"))),
    # Un atomo no tiene partes propias.
    Rule("m1.p.atomic_has_no_parts", ((True, "P", ("X",)),), (False, "R", ("Y", "X"))),
    # Lo adyacente comparte un todo: si x es adyacente a y, y es parte de y.
    Rule("m1.p.adjacency_implies_part", ((True, "S", ("X", "Y")),),
         (True, "R", ("X", "Y"))),
]


# ---------------------------------------------------------------------------
# M2 - Conjuntista.  R(x,y) = "x pertenece a y".  S(x,y) = "x es subconjunto de y".
#                    P(x)   = "x es un singleton".
# ---------------------------------------------------------------------------

M2_CORE = [
    Rule("m2.core.no_self_membership", ((True, "R", ("X", "Y")),),
         (False, "R", ("X", "X"))),
]

M2_PERIPHERY = [
    # La pertenencia NO es transitiva: si x∈y e y∈z, entonces x∉z.
    # Esto contradice directamente m1.p.transitive sobre los mismos hechos.
    Rule("m2.p.membership_not_transitive",
         ((True, "R", ("X", "Y")), (True, "R", ("Y", "Z"))),
         (False, "R", ("X", "Z"))),
    # Fundacion: si x∈y, y no puede pertenecer a x.
    Rule("m2.p.foundation", ((True, "R", ("X", "Y")),), (False, "R", ("Y", "X"))),
    # Un singleton tiene exactamente un elemento; nada mas le pertenece por herencia.
    Rule("m2.p.singleton_closed", ((True, "P", ("X",)), (True, "S", ("Y", "X"))),
         (False, "R", ("Y", "X"))),
    # Subconjunto no implica pertenencia.
    Rule("m2.p.subset_not_member", ((True, "S", ("X", "Y")),), (False, "R", ("X", "Y"))),
]


# ---------------------------------------------------------------------------
# M3 - Procesual.  R(x,y) = "x precede a y".  S(x,y) = "x es causado por y".
#                  P(x)   = "x es un estado inicial".
# ---------------------------------------------------------------------------

M3_CORE = [
    Rule("m3.core.no_self_precedence", ((True, "R", ("X", "Y")),),
         (False, "R", ("X", "X"))),
]

M3_PERIPHERY = [
    # La precedencia es transitiva.
    Rule("m3.p.transitive", ((True, "R", ("X", "Y")), (True, "R", ("Y", "Z"))),
         (True, "R", ("X", "Z"))),
    # Un estado inicial no tiene predecesores.
    Rule("m3.p.initial_has_no_predecessor", ((True, "P", ("X",)),),
         (False, "R", ("Y", "X"))),
    # Si x es causado por y, entonces y precede a x.
    Rule("m3.p.cause_precedes", ((True, "S", ("X", "Y")),), (True, "R", ("Y", "X"))),
    # Asimetria temporal.
    Rule("m3.p.asymmetric", ((True, "R", ("X", "Y")),), (False, "R", ("Y", "X"))),
]


ONTOLOGIES = {
    "M1": {"label": "mereologica", "core": M1_CORE, "periphery": M1_PERIPHERY},
    "M2": {"label": "conjuntista", "core": M2_CORE, "periphery": M2_PERIPHERY},
    "M3": {"label": "procesual", "core": M3_CORE, "periphery": M3_PERIPHERY},
}


def all_queries() -> list[Fact]:
    """
    Generador de queries: toda pregunta cerrada de la forma R(x,y) sobre pares
    distintos, en orden canonico lexicografico. Sin aleatoriedad, sin seed.
    """
    qs = []
    for x in OBJECTS:
        for y in OBJECTS:
            if x != y:
                qs.append((True, "R", (x, y)))
    return qs
