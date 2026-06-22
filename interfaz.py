import customtkinter as ctk
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.patheffects as pe
from matplotlib.lines import Line2D

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from datos import construir_grafo
from Algoritmo import ruta_minima
from mapa import POSICIONES
from mapa_base import FRONTERAS

COLOR = {
    "fondo_app":        "#10141c",
    "fondo_panel":       "#161b24",
    "fondo_card":        "#1e2531",
    "borde":             "#2b3340",
    "texto_primario":    "#edf1f6",
    "texto_secundario":  "#8b96a8",
    "acento":            "#3fa9f5",
    "acento_hover":      "#2f8fd6",
    "ruta":              "#ffa64d",
    "origen":            "#3ddc84",
    "destino":           "#ff5d6c",
    "nodo":              "#647189",
    "tierra":            "#202836",
    "tierra_borde":      "#37424f",
    "mar":               "#141a24",
    "arista":            "#3c4654",
}

F_TITULO    = ("Helvetica", 22, "bold")
F_SUBTITULO = ("Helvetica", 12)
F_ETIQUETA  = ("Helvetica", 12, "bold")
F_BOTON     = ("Helvetica", 14, "bold")
F_NUMERO    = ("Helvetica", 28, "bold")
F_TEXTO     = ("Helvetica", 13)
F_CHICA     = ("Helvetica", 11)
F_BADGE     = ("Helvetica", 11, "bold")

VELOCIDAD_PROMEDIO_KMH = 90
LIMITES_MAPA = (4, 18.5, 39, 50)


class Aplicacion(ctk.CTk):

    def __init__(self):
        super().__init__()

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.title("Ruta Óptima Entre Ciudades")
        self.geometry("1360x820")
        self.minsize(1080, 650)
        self.configure(fg_color=COLOR["fondo_app"])

        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.grafo = construir_grafo()
        self.ciudades = sorted(self.grafo.keys())
        self.grafo_nx = self._construir_networkx()

        self.origen = ctk.StringVar(value="Roma")
        self.destino = ctk.StringVar(value="Viena")

        self._crear_panel_lateral()
        self._crear_panel_mapa()

        self.calcular()

    def _crear_panel_lateral(self):

        self.panel = ctk.CTkScrollableFrame(
            self, width=330, fg_color=COLOR["fondo_panel"], corner_radius=0,
            scrollbar_button_color=COLOR["fondo_panel"],
            scrollbar_button_hover_color=COLOR["borde"],
        )
        self.panel.grid(row=0, column=0, sticky="nswe")
        self.panel.grid_columnconfigure(0, weight=1)

        # --- Encabezado ---
        ctk.CTkLabel(
            self.panel, text="Ruta Óptima", font=F_TITULO,
            text_color=COLOR["texto_primario"], anchor="w",
        ).grid(row=0, column=0, sticky="we", padx=22, pady=(26, 2))

        ctk.CTkLabel(
            self.panel, text="Camino más corto entre ciudades europeas",
            font=F_SUBTITULO, text_color=COLOR["texto_secundario"], anchor="w",
        ).grid(row=1, column=0, sticky="we", padx=22, pady=(0, 18))

        self._separador(2)

        ctk.CTkLabel(
            self.panel, text="ORIGEN", font=F_ETIQUETA,
            text_color=COLOR["texto_secundario"], anchor="w",
        ).grid(row=3, column=0, sticky="we", padx=22, pady=(18, 6))

        self.combo_origen = ctk.CTkComboBox(
            self.panel, values=self.ciudades, variable=self.origen,
            height=38, corner_radius=8, fg_color=COLOR["fondo_card"],
            border_color=COLOR["borde"], button_color=COLOR["acento"],
            button_hover_color=COLOR["acento_hover"],
            dropdown_fg_color=COLOR["fondo_card"], font=F_TEXTO,
        )
        self.combo_origen.grid(row=4, column=0, sticky="we", padx=22)

        ctk.CTkButton(
            self.panel, text="⇄  Intercambiar", width=140, height=28,
            fg_color="transparent", hover_color=COLOR["fondo_card"],
            text_color=COLOR["acento"], font=F_CHICA,
            command=self._intercambiar,
        ).grid(row=5, column=0, pady=8)

        ctk.CTkLabel(
            self.panel, text="DESTINO", font=F_ETIQUETA,
            text_color=COLOR["texto_secundario"], anchor="w",
        ).grid(row=6, column=0, sticky="we", padx=22, pady=(2, 6))

        self.combo_destino = ctk.CTkComboBox(
            self.panel, values=self.ciudades, variable=self.destino,
            height=38, corner_radius=8, fg_color=COLOR["fondo_card"],
            border_color=COLOR["borde"], button_color=COLOR["acento"],
            button_hover_color=COLOR["acento_hover"],
            dropdown_fg_color=COLOR["fondo_card"], font=F_TEXTO,
        )
        self.combo_destino.grid(row=7, column=0, sticky="we", padx=22)

        ctk.CTkButton(
            self.panel, text="Calcular ruta", height=44, corner_radius=10,
            fg_color=COLOR["acento"], hover_color=COLOR["acento_hover"],
            font=F_BOTON, command=self.calcular,
        ).grid(row=8, column=0, sticky="we", padx=22, pady=(18, 4))

        self._separador(9)

        self.contenedor_resultado = ctk.CTkFrame(self.panel, fg_color="transparent")
        self.contenedor_resultado.grid(row=10, column=0, sticky="we", padx=22, pady=(16, 24))
        self.contenedor_resultado.grid_columnconfigure(0, weight=1)

    def _separador(self, fila):
        ctk.CTkFrame(
            self.panel, height=1, corner_radius=0, fg_color=COLOR["borde"],
        ).grid(row=fila, column=0, sticky="we", padx=22)

    def _crear_panel_mapa(self):

        contenedor = ctk.CTkFrame(self, fg_color=COLOR["fondo_app"], corner_radius=0)
        contenedor.grid(row=0, column=1, sticky="nswe")
        contenedor.grid_rowconfigure(0, weight=1)
        contenedor.grid_columnconfigure(0, weight=1)

        self.figura = plt.Figure(figsize=(9, 7), dpi=100)
        self.figura.patch.set_facecolor(COLOR["fondo_app"])
        self.ax = self.figura.add_subplot(111)
        self.figura.subplots_adjust(left=0.02, right=0.98, top=0.95, bottom=0.02)

        self.canvas = FigureCanvasTkAgg(self.figura, master=contenedor)
        self.canvas.get_tk_widget().configure(bg=COLOR["fondo_app"], highlightthickness=0)
        self.canvas.get_tk_widget().grid(row=0, column=0, sticky="nswe", padx=18, pady=18)

    def _intercambiar(self):
        a, b = self.origen.get(), self.destino.get()
        self.origen.set(b)
        self.destino.set(a)
        self.calcular()

    def _construir_networkx(self):
        G = nx.Graph()
        for ciudad in self.grafo:
            G.add_node(ciudad)
        for origen, vecinos in self.grafo.items():
            for destino, peso in vecinos.items():
                if not G.has_edge(origen, destino):
                    G.add_edge(origen, destino, weight=peso)
        return G

    def calcular(self):
        origen = self.origen.get()
        destino = self.destino.get()

        for widget in self.contenedor_resultado.winfo_children():
            widget.destroy()

        if origen == destino:
            self._mostrar_aviso("Selecciona dos ciudades distintas.")
            self.dibujar_grafo(None)
            return

        ruta, costo = ruta_minima(self.grafo, origen, destino)

        if not ruta:
            self._mostrar_aviso("No existe una ruta posible entre esas ciudades.")
            self.dibujar_grafo(None)
            return

        self._mostrar_resultado(ruta, costo)
        self.dibujar_grafo(ruta)

    def _mostrar_aviso(self, texto):
        ctk.CTkLabel(
            self.contenedor_resultado, text=texto, font=F_TEXTO,
            text_color=COLOR["destino"], wraplength=270, justify="left",
        ).grid(row=0, column=0, sticky="w")

    def _mostrar_resultado(self, ruta, costo):

        cont = self.contenedor_resultado

        tarjeta = ctk.CTkFrame(cont, fg_color=COLOR["fondo_card"], corner_radius=12)
        tarjeta.grid(row=0, column=0, sticky="we")
        tarjeta.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            tarjeta, text="DISTANCIA TOTAL", font=F_CHICA,
            text_color=COLOR["texto_secundario"],
        ).grid(row=0, column=0, sticky="w", padx=18, pady=(16, 0))

        ctk.CTkLabel(
            tarjeta, text=f"{costo:,.0f} km".replace(",", "."),
            font=F_NUMERO, text_color=COLOR["texto_primario"],
        ).grid(row=1, column=0, sticky="w", padx=18, pady=(0, 4))

        horas = costo / VELOCIDAD_PROMEDIO_KMH
        h = int(horas)
        m = round((horas - h) * 60)
        if m == 60:
            h, m = h + 1, 0

        ctk.CTkLabel(
            tarjeta,
            text=f"≈ {h} h {m} min en auto  ·  {VELOCIDAD_PROMEDIO_KMH} km/h prom.",
            font=F_CHICA, text_color=COLOR["texto_secundario"],
        ).grid(row=2, column=0, sticky="w", padx=18, pady=(0, 16))

        ctk.CTkLabel(
            cont, text=f"RECORRIDO  ·  {len(ruta)} ciudades", font=F_ETIQUETA,
            text_color=COLOR["texto_secundario"],
        ).grid(row=1, column=0, sticky="w", pady=(18, 10))

        lista = ctk.CTkFrame(cont, fg_color="transparent")
        lista.grid(row=2, column=0, sticky="we")
        lista.grid_columnconfigure(1, weight=1)

        fila = 0
        for i, ciudad in enumerate(ruta):

            if i == 0:
                color_punto = COLOR["origen"]
            elif i == len(ruta) - 1:
                color_punto = COLOR["destino"]
            else:
                color_punto = COLOR["ruta"]

            ctk.CTkLabel(
                lista, text=str(i + 1), width=26, height=26, corner_radius=13,
                fg_color=color_punto, text_color=COLOR["fondo_app"], font=F_BADGE,
            ).grid(row=fila, column=0, padx=(0, 10), pady=2, sticky="w")

            ctk.CTkLabel(
                lista, text=ciudad, font=F_TEXTO,
                text_color=COLOR["texto_primario"], anchor="w",
            ).grid(row=fila, column=1, sticky="w", pady=2)

            fila += 1

            if i < len(ruta) - 1:
                tramo = self.grafo[ruta[i]][ruta[i + 1]]
                ctk.CTkLabel(
                    lista, text=f"↓ {tramo} km", font=F_CHICA,
                    text_color=COLOR["texto_secundario"],
                ).grid(row=fila, column=1, sticky="w")
                fila += 1

    def dibujar_grafo(self, ruta):

        self.ax.clear()
        self.ax.set_facecolor(COLOR["mar"])

        for poligonos in FRONTERAS.values():
            for poly in poligonos:
                xs = [p[0] for p in poly]
                ys = [p[1] for p in poly]
                self.ax.fill(
                    xs, ys, facecolor=COLOR["tierra"],
                    edgecolor=COLOR["tierra_borde"], linewidth=1, zorder=1,
                )

        G = self.grafo_nx
        pos = {ciudad: (lon, lat) for ciudad, (lon, lat) in POSICIONES.items()}

        nx.draw_networkx_edges(
            G, pos, ax=self.ax, width=1.3, alpha=0.55,
            edge_color=COLOR["arista"],
        )

        rutaset = set(ruta) if ruta else set()

        colores_nodo, tamanos_nodo = [], []
        for ciudad in G.nodes():
            if ruta and ciudad == ruta[0]:
                colores_nodo.append(COLOR["origen"]); tamanos_nodo.append(480)
            elif ruta and ciudad == ruta[-1]:
                colores_nodo.append(COLOR["destino"]); tamanos_nodo.append(480)
            elif ciudad in rutaset:
                colores_nodo.append(COLOR["ruta"]); tamanos_nodo.append(380)
            else:
                colores_nodo.append(COLOR["nodo"]); tamanos_nodo.append(230)

        nx.draw_networkx_nodes(
            G, pos, ax=self.ax, node_color=colores_nodo, node_size=tamanos_nodo,
            edgecolors=COLOR["fondo_app"], linewidths=1.4,
        )

        if ruta:
            aristas_ruta = [(ruta[i], ruta[i + 1]) for i in range(len(ruta) - 1)]
            nx.draw_networkx_edges(
                G, pos, ax=self.ax, edgelist=aristas_ruta, width=4.2,
                edge_color=COLOR["ruta"],
            )
            for i, ciudad in enumerate(ruta):
                x, y = pos[ciudad]
                self.ax.annotate(
                    str(i + 1), (x, y), color=COLOR["fondo_app"], fontsize=8.5,
                    fontweight="bold", ha="center", va="center", zorder=5,
                )

        # Etiquetas de ciudades, siempre legibles sobre el fondo
        for ciudad, (x, y) in pos.items():
            destacar = ciudad in rutaset
            self.ax.annotate(
                ciudad, (x, y), xytext=(0, 11), textcoords="offset points",
                ha="center", fontsize=9 if destacar else 8,
                fontweight="bold" if destacar else "normal",
                color=COLOR["texto_primario"] if destacar else COLOR["texto_secundario"],
                path_effects=[pe.withStroke(linewidth=2.6, foreground=COLOR["fondo_app"])],
                zorder=6,
            )

        leyenda = [
            Line2D([0], [0], marker="o", color="none", markerfacecolor=COLOR["origen"], markersize=9, label="Origen"),
            Line2D([0], [0], marker="o", color="none", markerfacecolor=COLOR["destino"], markersize=9, label="Destino"),
            Line2D([0], [0], marker="o", color="none", markerfacecolor=COLOR["ruta"], markersize=9, label="Ruta"),
            Line2D([0], [0], marker="o", color="none", markerfacecolor=COLOR["nodo"], markersize=9, label="Otras ciudades"),
        ]
        self.ax.legend(
            handles=leyenda, loc="lower left", frameon=False, fontsize=8.5,
            labelcolor=COLOR["texto_secundario"],
        )

        self.ax.set_title(
            "Red de Ciudades Europeas", color=COLOR["texto_primario"],
            fontsize=13, fontweight="bold", pad=12,
        )

        lon_min, lon_max, lat_min, lat_max = LIMITES_MAPA
        self.ax.set_xlim(lon_min, lon_max)
        self.ax.set_ylim(lat_min, lat_max)
        self.ax.set_aspect("equal")
        self.ax.axis("off")

        self.canvas.draw()


if __name__ == "__main__":
    app = Aplicacion()
    app.mainloop()
