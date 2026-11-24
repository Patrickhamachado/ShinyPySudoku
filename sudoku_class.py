from dataclasses import dataclass, field
from typing import Optional

import numpy as np
import matplotlib.pyplot as plt
from math import floor

from globals import fx_nuevo_sudoku, fx_invertir_bit


@dataclass
class Movimiento:
    """Registro de una jugada para deshacer o rehacer."""

    fila: int
    columna: int
    solucion: int
    posibles: int
    solucion_ant: int
    posibles_ant: int


class Sudoku:
    """Clase para manejar el estado y las jugadas de un Sudoku 9x9."""

    def __init__(self):
        self.iniciar(vacio= True)

    # ------------------------------------------------------------------
    # Estado
    # ------------------------------------------------------------------
    def iniciar(self, dificultad: float = 0.5, vacio: bool = False) -> None:
        """Inicializa un Sudoku nuevo o un tablero vacío."""
        self.solucion = np.zeros((9, 9), dtype=int)
        self.problema = np.zeros((9, 9), dtype=bool)
        self.posibles = np.zeros((9, 9), dtype=int)
        self.errores = np.zeros((9, 9), dtype=bool)

        self.deshacer: list[Movimiento] = []
        self.rehacer: list[Movimiento] = []

        self.no_movimientos = 0
        self.no_rehacer = 0
        self.terminado = False
        self.faltan = np.full(9, 9, dtype=int)

        if not vacio:
            puzzle = fx_nuevo_sudoku(dificultad)
            self.solucion = puzzle.copy()
            self.problema = puzzle > 0
            self.revisar()

    def copiar(self) -> "Sudoku":
        """Crea una copia independiente del Sudoku actual."""
        nuevo = Sudoku()
        nuevo.solucion = self.solucion.copy()
        nuevo.problema = self.problema.copy()
        nuevo.posibles = self.posibles.copy()
        nuevo.errores = self.errores.copy()

        nuevo.deshacer = self.deshacer.copy()
        nuevo.rehacer = self.rehacer.copy()

        nuevo.no_movimientos = self.no_movimientos
        nuevo.no_rehacer = self.no_rehacer
        nuevo.terminado = self.terminado
        nuevo.faltan = self.faltan.copy()

        return nuevo

    # ------------------------------------------------------------------
    # Jugadas
    # ------------------------------------------------------------------
    def play(
        self,
        llenar_con: int,
        llenar_fila: int,
        llenar_columna: int,
        definitivo: bool,
    ) -> None:
        """Llena o marca una celda, según `definitivo`.

        `llenar_fila` y `llenar_columna` usan numeración de 1 a 9,
        igual que en la versión de R.
        """
        dentro_tablero = (
            llenar_fila is not None
            and llenar_columna is not None
            and 1 <= llenar_fila <= 9
            and 1 <= llenar_columna <= 9
        )

        if not dentro_tablero:
            return

        # Si el Sudoku está resuelto, reinicia un tablero vacío.
        if self.terminado:
            self.iniciar(vacio= True)
            return

        fila = llenar_fila - 1
        columna = llenar_columna - 1

        # Solo se puede modificar una celda que no pertenece al problema.
        if self.problema[fila, columna]:
            return

        self.cambios(llenar_con, fila, columna, definitivo)

        ultimo = self.deshacer[-1]

        self.solucion[fila, columna] = ultimo.solucion
        self.posibles[fila, columna] = ultimo.posibles

        self.revisar()
        self.verificar_terminado()


    def cambios(
        self,
        llenar_con: int,
        fila: int,
        columna: int,
        definitivo: bool,
    ) -> None:
        """Registra el movimiento en el historial de deshacer."""
        self.no_movimientos += 1

        solucion_actual = int(self.solucion[fila, columna])
        posibles_actual = int(self.posibles[fila, columna])

        if definitivo:
            nueva_solucion = 0 if solucion_actual == llenar_con else llenar_con

            movimiento = Movimiento(
                fila=fila,
                columna=columna,
                solucion=nueva_solucion,
                posibles=posibles_actual,
                solucion_ant=solucion_actual,
                posibles_ant=posibles_actual,
            )
        else:
            nuevos_posibles = fx_invertir_bit(posibles_actual, llenar_con - 1)

            movimiento = Movimiento(
                fila=fila,
                columna=columna,
                solucion=solucion_actual,
                posibles=nuevos_posibles,
                solucion_ant=solucion_actual,
                posibles_ant=posibles_actual,
            )

        self.deshacer.append(movimiento)
        self.rehacer.clear()

    def deshacer_ultimo(self) -> None:
        """Deshace la última jugada."""
        if not self.deshacer:
            return

        ultimo = self.deshacer.pop()
        self.rehacer.append(ultimo)

        self.solucion[ultimo.fila, ultimo.columna] = ultimo.solucion_ant
        self.posibles[ultimo.fila, ultimo.columna] = ultimo.posibles_ant

        self.revisar()
        self.terminado = False

    def rehacer_ultimo(self) -> None:
        """Rehace la última jugada deshecha."""
        if not self.rehacer:
            return

        ultimo = self.rehacer.pop()
        self.deshacer.append(ultimo)

        self.solucion[ultimo.fila, ultimo.columna] = ultimo.solucion
        self.posibles[ultimo.fila, ultimo.columna] = ultimo.posibles

        self.revisar()
        self.verificar_terminado()

    # ------------------------------------------------------------------
    # Validación
    # ------------------------------------------------------------------
    def revisar(self) -> None:
        """Actualiza errores y números faltantes."""
        self.errores[:] = False
        self.faltan[:] = 9

        for numero in range(1, 10):
            self.faltan[numero - 1] = 9 - int((self.solucion == numero).sum())

            for tipo in ("fila", "columna", "casilla"):
                for indice_grupo in range(9):
                    filas, columnas = self._celdas_grupo(tipo, indice_grupo)

                    valores = self.solucion[filas, columnas]
                    repetidos = valores == numero

                    if repetidos.sum() > 1:
                        self.errores[filas[repetidos], columnas[repetidos]] = True


    def verificar_terminado(self) -> bool:
        """Comprueba si todas las filas, columnas y cajas suman 45."""
        suma_filas = self.solucion.sum(axis=1)
        suma_columnas = self.solucion.sum(axis=0)
        suma_casillas = np.array(
            [self.solucion[self._indices_casilla(n)].sum() for n in range(9)]
        )

        self.terminado = bool(
            (suma_filas == 45).all()
            and (suma_columnas == 45).all()
            and (suma_casillas == 45).all()
        )

        return self.terminado

    # ------------------------------------------------------------------
    # Grupos
    # ------------------------------------------------------------------
    def _filas(self) -> np.ndarray:
        return np.repeat(np.arange(9), 9)

    def _columnas(self) -> np.ndarray:
        return np.tile(np.arange(9), 9)

    def _casillas(self) -> np.ndarray:
        casillas = []

        for fila in range(9):
            for columna in range(9):
                casillas.append((fila // 3) * 3 + columna // 3)

        return np.array(casillas)

    def _indices_casilla(self, numero_casilla: int) -> tuple[np.ndarray, np.ndarray]:
        """Devuelve las coordenadas de una caja 3x3."""
        fila_inicio = (numero_casilla // 3) * 3
        columna_inicio = (numero_casilla % 3) * 3

        filas = np.arange(fila_inicio, fila_inicio + 3)
        columnas = np.arange(columna_inicio, columna_inicio + 3)

        return np.ix_(filas, columnas)

    def _celdas_grupo(
        self,
        tipo: str,
        indice_grupo: int,
    ) -> tuple[np.ndarray, np.ndarray]:
        """Devuelve las coordenadas de una fila, columna o caja 3x3."""

        if tipo == "fila":
            filas = np.full(9, indice_grupo)
            columnas = np.arange(9)
        elif tipo == "columna":
            filas = np.arange(9)
            columnas = np.full(9, indice_grupo)
        elif tipo == "casilla":
            fila_inicio = (indice_grupo // 3) * 3
            columna_inicio = (indice_grupo % 3) * 3

            filas = np.repeat(
                np.arange(fila_inicio, fila_inicio + 3),
                3,
            )
            columnas = np.tile(
                np.arange(columna_inicio, columna_inicio + 3),
                3,
            )
        else:
            raise ValueError("tipo debe ser 'fila', 'columna' o 'casilla'")

        return filas, columnas

    # ------------------------------------------------------------------
    # Visualización
    # ------------------------------------------------------------------
    def mostrar(self) -> None:
        """Muestra un resumen del estado actual."""
        print("Estado del Sudoku:")
        print(self.solucion)

        if self.deshacer:
            print("Jugadas para deshacer:")
            for movimiento in self.deshacer:
                print(movimiento)

        if self.rehacer:
            print("Jugadas para rehacer:")
            for movimiento in self.rehacer:
                print(movimiento)

    def plot(
        self,
        num_resaltar: int = 1,
        color_problema: str = "navy",
        color_error: str = "red",
        color_fondo: str = "turquoise",
    ):
        """Dibuja el Sudoku actual.

        - Resalta el número `num_resaltar` en celdas llenas y en marcas posibles.
        - Dibuja un círculo en celdas con números repetidos.
        - El círculo es azul para celdas del problema y rojo para celdas editables.
        """
        fig, ax = plt.subplots(figsize=(6, 6))
        ax.set_xlim(0.5, 27.5)
        ax.set_ylim(27.5, 0.5)
        ax.set_aspect("equal")
        ax.axis("off")

        vacio = self.solucion.sum() == 0

        # ------------------------------------------------------------------
        # Tablero vacío
        # ------------------------------------------------------------------
        if vacio:
            for coordenada in (0.5, 27.5):
                ax.plot(
                    [0.5, 27.5],
                    [coordenada, coordenada],
                    color=color_problema,
                    linewidth=4,
                )
                ax.plot(
                    [coordenada, coordenada],
                    [0.5, 27.5],
                    color=color_problema,
                    linewidth=4,
                )

            ax.text(
                14,
                11.5,
                "Press the `Play` button",
                ha="center",
                va="center",
                fontsize=20,
                fontweight="bold",
                color=color_problema,
            )
            ax.text(
                14,
                14.5,
                "to enjoy a new game!",
                ha="center",
                va="center",
                fontsize=20,
                fontweight="bold",
                color=color_problema,
            )

            return fig

        # ------------------------------------------------------------------
        # Líneas de la cuadrícula
        # ------------------------------------------------------------------
        for coordenada in np.arange(0.5, 28.0, 3):
            ax.plot(
                [0.5, 27.5],
                [coordenada, coordenada],
                color="grey",
                linewidth=1,
            )
            ax.plot(
                [coordenada, coordenada],
                [0.5, 27.5],
                color="grey",
                linewidth=1,
            )

        for coordenada in np.array([0, 9, 18, 27]) + 0.5:
            ax.plot(
                [0.5, 27.5],
                [coordenada, coordenada],
                color="black",
                linewidth=3,
            )
            ax.plot(
                [coordenada, coordenada],
                [0.5, 27.5],
                color="black",
                linewidth=3,
            )

        # ------------------------------------------------------------------
        # Celdas
        # ------------------------------------------------------------------
        for fila in range(9):
            for columna in range(9):
                x = 0.5 + columna * 3 + 1.5
                y = 0.5 + fila * 3 + 1.5

                valor = int(self.solucion[fila, columna])
                posibles = int(self.posibles[fila, columna])
                es_problema = bool(self.problema[fila, columna])
                tiene_error = bool(self.errores[fila, columna])

                if valor > 0:
                    # Resaltar el número seleccionado
                    if valor == num_resaltar:
                        ax.add_patch(
                            plt.Rectangle(
                                (x - 1.5, y - 1.5),
                                3,
                                3,
                                facecolor=color_fondo,
                                edgecolor=color_problema,
                                linewidth=3,
                                zorder=0,
                            )
                        )

                    color = color_problema if es_problema or self.terminado else "black"
                    peso = "bold" if es_problema or self.terminado else "normal"

                    ax.text(
                        x,
                        y,
                        str(valor),
                        ha="center",
                        va="center",
                        fontsize=20,
                        fontweight=peso,
                        color=color,
                        zorder=2,
                    )

                    # Círculo de error
                    if tiene_error:
                        color_circulo = color_problema if es_problema else color_error

                        ax.add_patch(
                            plt.Circle(
                                (x, y),
                                1.2,
                                fill=False,
                                edgecolor=color_circulo,
                                linewidth=3,
                                zorder=3,
                            )
                        )

                elif posibles > 0:
                    for bit_posible in range(9):
                        bit_activo = (posibles >> bit_posible) & 1

                        if not bit_activo:
                            continue

                        numero_posible = bit_posible + 1

                        xx = (bit_posible + 2) % 3
                        if xx == 2:
                            xx = -1

                        yy = floor(bit_posible / 3) - 1

                        x_posible = x + xx
                        y_posible = y + yy

                        # Resaltar el número posible seleccionado
                        if numero_posible == num_resaltar:
                            ax.add_patch(
                                plt.Rectangle(
                                    (x_posible - 0.45, y_posible - 0.45),
                                    0.9,
                                    0.9,
                                    facecolor=color_fondo,
                                    edgecolor="none",
                                    zorder=0,
                                )
                            )

                        ax.text(
                            x_posible,
                            y_posible,
                            str(numero_posible),
                            ha="center",
                            va="center",
                            fontsize=8,
                            color="black",
                            zorder=2,
                        )

        return fig
        
