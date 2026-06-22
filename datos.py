CIUDADES = {
    "Roma",
    "Nápoles",
    "Perugia",
    "Pescara",
    "Florencia",
    "Bari",
    "Pisa",
    "Bolonia",
    "Génova",
    "Venecia",
    "Milán",
    "Niza",
    "Zúrich",
    "Múnich",
    "Viena"
}

CONEXIONES = [
    ("Roma",      "Nápoles",    226),
    ("Roma",      "Perugia",    173),
    ("Roma",      "Pescara",    208),
    ("Roma",      "Florencia",  275),
    ("Nápoles",   "Bari",       261),
    ("Perugia",   "Florencia",  151),
    ("Pescara",   "Bari",       310),
    ("Pescara",   "Perugia",    251),
    ("Florencia", "Pisa",       84),
    ("Florencia", "Bolonia",    105),
    ("Pisa",      "Génova",     163),
    ("Bolonia",   "Venecia",    161),
    ("Bolonia",   "Milán",      214),
    ("Génova",    "Milán",      142),
    ("Génova",    "Niza",       194),
    ("Milán",     "Venecia",    278),
    ("Milán",     "Zúrich",     279),
    ("Venecia",   "Viena",      582),
    ("Zúrich",    "Múnich",     310),
    ("Múnich",    "Viena",      401),
]

def construir_grafo():
    grafo = {ciudad: {} for ciudad in CIUDADES}
    for origen, destino, distancia in CONEXIONES:
        grafo[origen][destino] = distancia
        grafo[destino][origen] = distancia 
    return grafo

if __name__ == "__main__":
    grafo = construir_grafo()

    print(f"Número de ciudades (vértices): {len(CIUDADES)}")
    print(f"Número de conexiones (aristas): {len(CONEXIONES)}")
    print()

    print("Ciudades y sus conexiones:")
    for ciudad, vecinos in grafo.items():
        if vecinos:
            lista = ", ".join(f"{v} ({d} km)" for v, d in vecinos.items())
        else:
            lista = "(sin conexiones directas)"
        print(f"  {ciudad:12} → {lista}")
