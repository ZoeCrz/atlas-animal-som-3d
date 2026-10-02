"""Validación compartida entre Streamlit y Python dentro del navegador."""
import json
import unicodedata
from features import FEATURES, ECOSYSTEMS, EMOJIS

MAX_CUSTOM_ANIMALS = 200

def normalized_name(name: str) -> str:
    return unicodedata.normalize("NFC", name).strip().casefold()


def validate_animal(animal: dict) -> dict:
    if not isinstance(animal, dict):
        raise ValueError("Cada animal debe ser un objeto JSON.")
    name = animal.get("name")
    if not isinstance(name, str) or not name.strip() or len(name.strip()) > 60:
        raise ValueError("El nombre debe contener entre 1 y 60 caracteres.")
    if any(unicodedata.category(c).startswith("C") for c in name):
        raise ValueError("El nombre no puede contener caracteres de control.")
    if animal.get("emoji") not in EMOJIS:
        raise ValueError("Elige un emoji del catálogo compatible.")
    if animal.get("ecosystem") not in ECOSYSTEMS:
        raise ValueError("El ecosistema no pertenece al catálogo.")
    values = animal.get("features")
    if not isinstance(values, list) or len(values) != len(FEATURES):
        raise ValueError("Debes definir exactamente 20 características.")
    for value, feature in zip(values, FEATURES):
        if isinstance(value, bool) or not isinstance(value, (float, int)) or value not in feature.scale:
            raise ValueError(f"Valor fuera de escala en {feature.label}.")
    # Solo se conservan campos conocidos; las coordenadas siempre se recalculan.
    return {"name": unicodedata.normalize("NFC", name).strip(), "emoji": animal["emoji"],
            "ecosystem": animal["ecosystem"], "features": [float(v) for v in values],
            "scientific_name": str(animal.get("scientific_name", ""))[:120]}


def validate_collection(animals: list, existing: list = ()) -> list[dict]:
    if not isinstance(animals, list):
        raise ValueError("La colección debe ser una lista de animales.")
    names = {normalized_name(a["name"]) for a in existing}
    emojis = {a["emoji"] for a in existing}
    result = []
    for animal in animals:
        item = validate_animal(animal)
        key = normalized_name(item["name"])
        if key in names:
            raise ValueError(f"El nombre {item['name']} ya existe.")
        if item["emoji"] in emojis:
            raise ValueError(f"El emoji {item['emoji']} ya identifica otro animal. Elige un emoji animal distinto.")
        names.add(key)
        emojis.add(item["emoji"])
        result.append(item)
    return result


def export_custom(animals: list[dict]) -> str:
    return json.dumps({"schema_version": 1, "feature_keys": [f.key for f in FEATURES],
                       "animals": animals}, ensure_ascii=False, indent=2)


def import_custom(raw: bytes, base: list[dict]) -> list[dict]:
    if len(raw) > 1_000_000:
        raise ValueError("El archivo no puede superar 1 MB.")
    try:
        payload = json.loads(raw.decode("utf-8-sig"))
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise ValueError("El archivo debe contener JSON válido en UTF-8.") from exc
    if not isinstance(payload, dict) or payload.get("schema_version") != 1:
        raise ValueError("Versión de archivo no compatible.")
    if payload.get("feature_keys") != [f.key for f in FEATURES]:
        raise ValueError("El orden de las características no coincide con este proyecto.")
    animals = payload.get("animals")
    if not isinstance(animals, list) or len(animals) > MAX_CUSTOM_ANIMALS:
        raise ValueError(f"Se permiten hasta {MAX_CUSTOM_ANIMALS} animales personalizados.")
    return validate_collection(animals, base)
