# Agente Anti Vibe Coding

Agente de IA que acompaña el proceso del **Anti Vibe Coding Challenge**: en vez de
pedirle código a una IA a ciegas, mejora el prompt, genera el código, lo audita y
deja un informe para que lo valides vos.

## Qué hace

1. **Mejora el prompt**: toma uno vago (ej. "Haceme un carrito de compras") y lo vuelve concreto.
2. **Genera el código**: crea los archivos de la app a partir del prompt mejorado.
3. **Audita el código**: detecta requisitos incumplidos, bugs, riesgos y arma una checklist de pruebas.
4. **Arma el informe** (`INFORME.md`) con las secciones del TP: prompt original, prompt mejorado,
   qué información se agregó, riesgos, código, validación.

La sección **Validación personal** queda para completarla a mano: la idea del desafío es
que vos pruebes y entiendas el código.

## Instalación

```bash
git clone <url-de-tu-repo>
cd anti-vibe-agent
python -m venv venv
source venv/bin/activate        # En Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env            # y pegá tu ANTHROPIC_API_KEY adentro
```

La clave se saca en https://console.anthropic.com

## Uso

```bash
python agente.py "Haceme una app de Pokémon con favoritos"
```

Los resultados quedan en `salida/<nombre-de-la-app>/` con el código y el `INFORME.md`.

## Estructura

```
agente.py          # el agente (pipeline de 4 pasos)
requirements.txt   # dependencias
.env.example       # plantilla de configuración
.gitignore         # evita subir la clave y las salidas
```

## Importante

- Nunca subas tu `.env` a GitHub (ya está en `.gitignore`).
- El agente puede equivocarse: revisá siempre el código antes de usarlo.
