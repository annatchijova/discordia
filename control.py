"""
Control negativo. Hipotesis a falsar: la trayectoria de configuraciones es una
respuesta al conflicto, no un barrido determinista del espacio.

Test: reemplazar el detector de contradiccion por un disparador arbitrario que
no mira las respuestas. Si la trayectoria de configuraciones es identica, la
coercion no tiene contenido informacional.
"""
from module import ConvictionModule, YES, NO
from world import BASE_FACTS, ONTOLOGIES, all_queries


def trajectory(trigger):
    mods = [ConvictionModule(n, s["label"], s["core"], s["periphery"],
                             BASE_FACTS, order="descending")
            for n, s in ONTOLOGIES.items()]
    qs = all_queries()
    traj = {m.name: [m.config] for m in mods}
    for step in range(200):
        q = qs[step % len(qs)]
        resp = [(m,) + m.answer(q) for m in mods]
        fire, participants = trigger(step, resp)
        if fire:
            for m, verdict, just, used_p in resp:
                if m in participants and not m.paralyzed:
                    m.apply_contradiction(used_p)
                    traj[m.name].append(m.config)
    return traj


def real_trigger(step, resp):
    vs = [r[1] for r in resp]
    fire = (YES in vs) and (NO in vs)
    return fire, {r[0] for r in resp if r[1] in (YES, NO)}


def blind_trigger(step, resp):
    # dispara cada 4 pasos. Mira quien respondio (mismo criterio de
    # participacion) pero NO mira si hubo contradiccion.
    return (step % 4 == 1), {r[0] for r in resp if r[1] in (YES, NO)}


print("REAL  ", {k: v for k, v in trajectory(real_trigger).items()})
print()
print("CIEGO ", {k: v for k, v in trajectory(blind_trigger).items()})
