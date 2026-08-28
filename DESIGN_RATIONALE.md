# DISCORDIA — Design Rationale

Artefacto producido bajo el experimento de autonomía acotada (Anna, operadora;
Claude, Kimi y ChatGPT en el circuito de diseño). Propuesta original de Kimi.

## Asimetría de autoridad observada (registro, no corrección)

Claude originó las restricciones arquitectónicas principales (query compartida,
Historiador B, coerción por degradación con justificación, nogood store
persistente, regeneración sintáctica). Kimi realizó verificación adversaria,
en la primera ronda sólo tras pedido explícito, y en las dos últimas por
iniciativa propia — refutó la minimización de nogoods, que Claude concedió.
ChatGPT ocupó un rol meta-observacional antes de presentar un artefacto, y
abrió la única objeción de la sesión que no salió del espacio delimitado por
Claude (dependencia del camino). La convergencia posterior en DISCORDIA
**no puede leerse como acuerdo independiente**.

## Arquitectura (7 piezas acordadas)

1. Query compartida obligatoria sobre el mismo micro-universo.
2. Historiador Versión B: legible desde afuera, opaco hacia adentro.
3. Degradación con justificación (TMS forward-chaining, Doyle/de Kleer).
4. Nogood store persistente, nunca se vacía.
5. Regeneración sintáctica: no consulta el historial de conflictos.
6. Dependencia del camino declarada como propiedad, no como defecto.
7. Orden canónico fijo por ejecución.

Descartado: minimización de nogoods. Requiere evaluación contrafáctica
(«¿M1 sin el axioma X todavía choca con M2?») que la arquitectura no tiene y
que exigiría una teoría de incompatibilidad inter-ontológica. Cierre por
imposibilidad operativa, no por elección.

## Limitaciones declaradas

- **Filtración parcial.** El módulo conoce su respuesta y el id de la query en
  que chocó; infiere que otro respondió algo incompatible. La opacidad no es
  total.
- **Inaccesibilidad, no amnesia.** La retracción es reversible por
  regeneración; el axioma no desaparece del espacio de posibilidades.
- **El registro es una historia de búsqueda**, no el mapa semántico de
  incompatibilidad del universo.

## Resultado empírico (v0.1)

Con orden ascendente el sistema es estéril: la primera configuración admisible
es el periphery vacío, nadie deriva nada, cero contradicciones en 200 queries.
El orden canónico decide si el sistema hace algo.

Con orden descendente hay fricción real: 9 contradicciones, degradación
progresiva. Pero la última contradicción ocurre en el paso 49, y los 150 pasos
siguientes no producen ninguna.

**La coerción es autoextinguible.** Un mecanismo que sólo quita capacidad
inferencial acaba eliminando la fricción que pretendía producir. No por
aprendizaje — la regeneración sintáctica lo impide por construcción — sino por
degradación monótona: las ontologías terminan demasiado débiles para
contradecirse. El fixed point no es parálisis colectiva sino paz.

Esto refuta la promesa central de DISCORDIA («fricción epistémica no
resoluble») en su primera implementación.

## Determinismo

Sellado SHA-256 sobre serialización canónica tipada y ordenada. Sin floats en
el camino de decisión. Tres corridas producen sello idéntico.

## Corrección v0.2 — bug de implementación en la pieza 3

La auditoría marcó "degradación con justificación" como implementada. No lo
estaba. En v0.1 el nogood registrado era la **configuración entera**, no el
conjunto de axiomas que aparecían en la justificación. La justificación se
consultaba sólo para un booleano (`used_periphery`), que decide retractar vs
paralizar. Nada más de la justificación entraba en la decisión.

Consecuencia: la trayectoria de configuraciones era un barrido descendente del
espacio, no una respuesta al contenido del conflicto.

**Control negativo** (`control.py`): se reemplazó el detector de contradicción
por un disparador que dispara cada 4 pasos sin mirar las respuestas, con el
mismo criterio de participación. Trayectorias:

    real   M1: 15,14,13,12,11,10,9,8,7,6
    ciego  M1: 15,14,13,12,11,10,9,8,7,6

Idénticas. En v0.1 la contradicción funcionaba como reloj, no como señal:
determinaba *cuándo* avanzaba el contador, no *hacia dónde*.

Esto también refuta la formalización `C_{t+1} ⊆ C_t`. Las cardinalidades de la
trayectoria real son 4,3,3,2,3,2,2,1,3,2 — suben y bajan. La degradación no era
monótonamente sustractiva; era un recorrido lexicográfico.

v0.2 implementa lo que decía la spec: el nogood es el conjunto de índices de
periphery presentes en la justificación, y una configuración es inadmisible si
contiene algún nogood como subconjunto.

**Resultado con la coerción correcta:** 2 contradicciones, la última en el paso
5, y 194 pasos sin ninguna. El hallazgo de v0.1 sobrevive y se refuerza: con
coerción dirigida por justificación, la extinción es *más rápida*, no menos.
v0.1 tardaba 49 pasos porque estaba barriendo a ciegas.
