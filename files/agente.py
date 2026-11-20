"""
Agente Anti Vibe Coding
-----------------------
Pipeline de 4 pasos:
  1. Mejora un prompt vago.
  2. Genera el código a partir del prompt mejorado.
  3. Audita el código (qué falla, qué falta, qué es riesgoso).
  4. Arma un informe con el mismo formato del TP.

Uso:
  python agente.py "Haceme un carrito de compras"
  python agente.py            (te pide el prompt por consola)
"""
import argparse
import os
import re
import sys
from datetime import datetime

from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

MODELO = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-5-5")
cliente = Anthropic()  # lee ANTHROPIC_API_KEY del entorno


def preguntar(sistema: str, usuario: str, max_tokens: int = 4000) -> str:
    """Hace una llamada simple al modelo y devuelve el texto."""
    respuesta = cliente.messages.create(
        model=MODELO,
        max_tokens=max_tokens,
        system=sistema,
        messages=[{"role": "user", "content": usuario}],
    )
    return "".join(b.text for b in respuesta.content if b.type == "text")


def extraer_tag(texto: str, tag: str) -> str:
    m = re.search(rf"<{tag}>(.*?)</{tag}>", texto, re.DOTALL)
    return m.group(1).strip() if m else ""


# ---------------------------------------------------------------- Paso 1
def mejorar_prompt(prompt_original: str) -> dict:
    sistema = (
        "Sos un experto en ingeniería de prompts para generar aplicaciones web. "
        "Respondé siempre en español rioplatense."
    )
    usuario = f"""Prompt original: "{prompt_original}"

Mejoralo para que una IA genere una app útil y sin ambigüedades.
Tené en cuenta: tecnología a usar, qué datos/API, funciones concretas,
manejo de errores, responsive, estructura del código y qué NO hay que incluir.

Respondé EXACTAMENTE con estas tres etiquetas:
<prompt_mejorado>el prompt completo y listo para usar</prompt_mejorado>
<informacion_agregada>qué le agregaste al original y por qué</informacion_agregada>
<riesgos>qué podía salir mal con el prompt original</riesgos>"""
    texto = preguntar(sistema, usuario)
    return {
        "prompt_mejorado": extraer_tag(texto, "prompt_mejorado") or prompt_original,
        "informacion_agregada": extraer_tag(texto, "informacion_agregada"),
        "riesgos": extraer_tag(texto, "riesgos"),
    }


# ---------------------------------------------------------------- Paso 2
def generar_codigo(prompt_mejorado: str) -> dict:
    sistema = "Sos un desarrollador web que escribe código simple, claro y comentado."
    usuario = f"""{prompt_mejorado}

Devolvé cada archivo con este formato exacto, sin texto extra:
=== ARCHIVO: nombre.ext ===
contenido del archivo"""
    texto = preguntar(sistema, usuario, max_tokens=8000)

    archivos = {}
    partes = re.split(r"=== ARCHIVO: (.+?) ===", texto)
    # partes = [basura, nombre1, contenido1, nombre2, contenido2, ...]
    for i in range(1, len(partes) - 1, 2):
        nombre = os.path.basename(partes[i].strip())  # evita rutas raras
        contenido = re.sub(r"^```\w*\n|\n```\s*$", "", partes[i + 1].strip())
        if nombre:
            archivos[nombre] = contenido
    return archivos


# ---------------------------------------------------------------- Paso 3
def auditar(prompt_mejorado: str, archivos: dict) -> str:
    sistema = (
        "Sos un revisor de código estricto pero constructivo. "
        "Respondé en español rioplatense. No inventes problemas: "
        "citá la función o línea donde ves cada uno."
    )
    codigo = "\n\n".join(f"### {n}\n{c}" for n, c in archivos.items())
    usuario = f"""Requisitos pedidos:
{prompt_mejorado}

Código generado:
{codigo}

Armá una auditoría en markdown con estas secciones:
## Requisitos cumplidos / no cumplidos
## Problemas encontrados (ordenados por gravedad: alta, media, baja)
## Riesgos de seguridad y robustez
## Checklist de pruebas manuales (casilleros [ ] para tildar)
## Explicación simple de cómo funciona el código"""
    return preguntar(sistema, usuario, max_tokens=5000)


# ---------------------------------------------------------------- Paso 4
def armar_informe(original, mejora, archivos, auditoria) -> str:
    bloques = [f"# Informe Anti Vibe Coding\n\n_Generado el {datetime.now():%d/%m/%Y %H:%M}_\n"]
    bloques.append(f"## Prompt original\n\n> {original}\n")
    bloques.append(f"## Prompt mejorado\n\n{mejora['prompt_mejorado']}\n")
    bloques.append(f"## Qué información agregué\n\n{mejora['informacion_agregada']}\n")
    bloques.append(f"## Riesgos del prompt original\n\n{mejora['riesgos']}\n")
    bloques.append("## Código generado\n\nArchivos: " + ", ".join(archivos) + "\n")
    bloques.append(f"## Validación (auditoría del agente)\n\n{auditoria}\n")
    bloques.append(
        "## Validación personal\n\n_Completá esta parte a mano: probá el código, "
        "tildá la checklist y anotá qué entendiste y qué cambiarías._\n"
    )
    return "\n".join(bloques)


def nombre_carpeta(texto: str) -> str:
    base = re.sub(r"[^a-z0-9]+", "-", texto.lower()).strip("-")[:30] or "app"
    return f"{base}-{datetime.now():%H%M%S}"


def main():
    parser = argparse.ArgumentParser(description="Agente Anti Vibe Coding")
    parser.add_argument("prompt", nargs="?", help="Prompt original (vago)")
    args = parser.parse_args()

    if not os.getenv("ANTHROPIC_API_KEY"):
        sys.exit("Falta ANTHROPIC_API_KEY. Copiá .env.example a .env y pegá tu clave.")

    original = args.prompt or input("Prompt original: ").strip()
    if not original:
        sys.exit("Necesito un prompt.")

    print("1/4 Mejorando el prompt...")
    mejora = mejorar_prompt(original)

    print("2/4 Generando el código...")
    archivos = generar_codigo(mejora["prompt_mejorado"])
    if not archivos:
        sys.exit("El modelo no devolvió archivos con el formato esperado. Probá de nuevo.")

    print("3/4 Auditando el código...")
    auditoria = auditar(mejora["prompt_mejorado"], archivos)

    print("4/4 Armando el informe...")
    informe = armar_informe(original, mejora, archivos, auditoria)

    carpeta = os.path.join("salida", nombre_carpeta(original))
    os.makedirs(carpeta, exist_ok=True)
    for nombre, contenido in archivos.items():
        with open(os.path.join(carpeta, nombre), "w", encoding="utf-8") as f:
            f.write(contenido)
    with open(os.path.join(carpeta, "INFORME.md"), "w", encoding="utf-8") as f:
        f.write(informe)

    print(f"\nListo. Todo guardado en: {carpeta}/")


if __name__ == "__main__":
    main()
