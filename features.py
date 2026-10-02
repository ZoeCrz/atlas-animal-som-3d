"""Diccionario único de las 20 características, compartido por datos y formulario."""
from dataclasses import dataclass


@dataclass(frozen=True)
class Feature:
    key: str
    label: str
    options: tuple[str, ...]
    help: str

    @property
    def scale(self) -> tuple[float, ...]:
        # Se respetan las escalas literales solicitadas, incluida la de 4 opciones.
        return {2: (0., 1.), 3: (0., .5, 1.),
                4: (0., .33, .66, 1.), 5: (0., .25, .5, .75, 1.)}[len(self.options)]


FEATURES = (
    Feature("longitud", "Longitud corporal", ("Menos de 10 cm", "10 a menos de 40 cm", "40 a menos de 100 cm", "1 a menos de 3 m", "3 m o más"), "Longitud aproximada del adulto, sin envergadura. Los límites inferiores están incluidos."),
    Feature("masa", "Masa corporal", ("Menos de 0.1 kg", "0.1 a menos de 1 kg", "1 a menos de 10 kg", "10 a menos de 100 kg", "100 kg o más"), "Masa representativa del adulto; no describe todos los sexos y poblaciones."),
    Feature("longevidad", "Longevidad potencial", ("Menos de 1 año", "1 a menos de 5 años", "5 a menos de 15 años", "15 a menos de 40 años", "40 años o más"), "Categoría orientativa de longevidad potencial, no esperanza de vida promedio."),
    Feature("patas", "Patas locomotoras", ("Sin patas", "Dos", "Cuatro", "Seis", "Ocho o más"), "No se cuentan brazos de pulpos ni aletas. Es una escala ordinal de cantidad, no de velocidad."),
    Feature("agua", "Dependencia acuática", ("Terrestre", "Agua ocasional", "Semiacuático", "Mayormente acuático", "Totalmente acuático"), "Desde vida terrestre hasta vida permanentemente en el agua."),
    Feature("vuelo", "Capacidad de vuelo", ("No vuela", "Planea", "Vuelo activo"), "El planeo se diferencia del vuelo propulsado."),
    Feature("trepa", "Capacidad de trepar", ("No trepa", "Ocasional", "Habitual"), "Capacidad funcional para desplazarse por árboles o superficies verticales."),
    Feature("movilidad", "Movilidad terrestre", ("Nula", "Muy baja", "Baja", "Moderada", "Alta"), "Capacidad relativa en tierra; no equivale a una velocidad medida en km/h."),
    Feature("natacion", "Capacidad de nadar", ("Nula", "Limitada", "Moderada", "Alta", "Especializada"), "Capacidad relativa de desplazarse en el agua."),
    Feature("vegetales", "Componente vegetal de dieta", ("Nulo o mínimo", "Bajo", "Mixto", "Predominante", "Casi exclusivo"), "Fracción aproximada de alimento de origen vegetal. Evita ordenar artificialmente etiquetas como carnívoro e insectívoro."),
    Feature("especializacion", "Especialización alimentaria", ("Generalista", "Preferencias leves", "Dieta restringida", "Muy especializado"), "Escala didáctica desde dieta amplia hasta dependencia de pocos alimentos."),
    Feature("socialidad", "Vida en grupo", ("Solitario", "Parejas o encuentros", "Grupos pequeños", "Colonias o grupos grandes"), "Patrón típico simplificado; puede cambiar durante reproducción o migración."),
    Feature("nocturnidad", "Actividad nocturna", ("Principalmente diurno", "Mixto o crepuscular", "Principalmente nocturno"), "Patrón de actividad predominante del adulto."),
    Feature("frio", "Adaptación al frío", ("Muy baja", "Baja", "Moderada", "Alta", "Polar"), "Adaptación ecológica aproximada; no es una temperatura mínima medida."),
    Feature("humedad", "Dependencia de humedad", ("Baja", "Moderada", "Alta", "Agua o humedad constante"), "Desde ambientes secos hasta necesidad permanente de agua o humedad."),
    Feature("endotermia", "Endotermia predominante", ("No", "Sí"), "Producción interna de calor predominante: mamíferos y aves. Se simplifican casos especiales."),
    Feature("vertebras", "Columna vertebral", ("No", "Sí"), "Distingue vertebrados e invertebrados."),
    Feature("huevos", "Puesta de huevos", ("No", "Sí"), "La especie pone huevos; no se confunde con desarrollo interno de huevos."),
    Feature("pelaje", "Presencia de pelaje", ("No", "Sí"), "Pelaje de mamíferos; no se cuentan pelos aislados de cetáceos ni setas de artrópodos."),
    Feature("plumaje", "Presencia de plumaje", ("No", "Sí"), "Plumas presentes en el adulto, incluso aves que no vuelan."),
)

ECOSYSTEMS = ("Bosque templado", "Pradera", "Desierto", "Ártico", "Antártico", "Selva tropical", "Agua dulce", "Océano", "Costa", "Aéreo")
# Solo animales completos o rostros animales. No hay huellas, alimentos ni objetos.
# Los emojis adicionales quedan disponibles para animales nuevos y no se repiten.
EMOJIS = ("🐺", "🦊", "🦌", "🦬", "🐪", "🦘", "🐿️", "🦔", "🦦", "🦫", "🦭", "🫎", "🐧", "🐬", "🐋", "🐳", "🦈", "🐠", "🐙", "🦑", "🪼", "🦀", "🦞", "🐢", "🐊", "🐡", "🐸", "🦎", "🪲", "🐍", "🦅", "🦉", "🦜", "🦢", "🦩", "🦚", "🦃", "🦇", "🦥", "🦋", "🐝", "🐜", "🕷️", "🦂", "🐌", "🦡", "🦝", "🦍", "🦧", "🐼", "🐨", "🐗", "🐏", "🐑", "🐂", "🐃", "🦓", "🦒", "🐘", "🦏", "🦛", "🦆", "🪿", "🕊️", "🐦", "🐓", "🐒", "🐕", "🐈", "🐎", "🐐", "🐖", "🐇", "🐻")


def feature_dictionary() -> list[dict]:
    return [{"Característica": f.label, "Clave": f.key, "Opciones": len(f.options),
             "Escala": " · ".join(f"{v:g} = {o}" for v, o in zip(f.scale, f.options)),
             "Criterio": f.help} for f in FEATURES]
