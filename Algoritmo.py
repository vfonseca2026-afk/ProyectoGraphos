import heapq

def dijkstra(grafo, origen):

    distancias = {nodo: float("inf") for nodo in grafo}
    anteriores = {nodo: None for nodo in grafo}

    distancias[origen] = 0

    cola_prioridad = [(0, origen)]

    while cola_prioridad:

        distancia_actual, ciudad_actual = heapq.heappop(
            cola_prioridad
        )

        if distancia_actual > distancias[ciudad_actual]:
            continue

        for vecino, peso in grafo[ciudad_actual].items():

            nueva_distancia = (
                distancias[ciudad_actual] + peso
            )

            if nueva_distancia < distancias[vecino]:

                distancias[vecino] = nueva_distancia
                anteriores[vecino] = ciudad_actual

                heapq.heappush(
                    cola_prioridad,
                    (nueva_distancia, vecino)
                )

    return distancias, anteriores


def obtener_ruta(anteriores, origen, destino):

    ruta = []
    actual = destino

    while actual is not None:
        ruta.append(actual)
        actual = anteriores[actual]

    ruta.reverse()

    if ruta and ruta[0] == origen:
        return ruta

    return []


def ruta_minima(grafo, origen, destino):

    distancias, anteriores = dijkstra(
        grafo,
        origen
    )

    ruta = obtener_ruta(
        anteriores,
        origen,
        destino
    )

    return ruta, distancias[destino]

if __name__ == "__main__":

    from datos import construir_grafo

    grafo = construir_grafo()

    origen = "Roma"
    destino = "Viena"

    ruta, costo = ruta_minima(
        grafo,
        origen,
        destino
    )

    print("Origen:", origen)
    print("Destino:", destino)
    print()

    print("Ruta óptima:")
    print(" → ".join(ruta))

    print()
    print("Costo total:", costo, "km")