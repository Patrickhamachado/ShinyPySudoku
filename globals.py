
# Librerías ----------
import matplotlib.pyplot as plt
import numpy as np
from math import floor, ceil
from sudoku import ClassicSudoku, DiagonalSudoku
from sudoku.base_sudoku import PuzzleGenerator


# Funciones ----------

## fx_plot: Para imprimir el Sudoku ----
def fx_plot(
  # problema = [[0 for x in range(9)]] * 9, 
  # solucion = None, 
  # posibles = [[0 for x in range(9)]] * 9, 

  problema = np.zeros((9, 9), dtype=int), 
  solucion = None, 
  posibles = np.zeros((9, 9), dtype=int), 

  terminado = False,
  color_problema = "navy", 
  color_error = "red"):
    """Imprimir la cuadrícula y los números del Sudoku"""

    # Si arranca la app y no hay datos, inicializa limpiamente aquí
    if problema is None:
      problema = [[0 for x in range(9)]] * 9
    if isinstance(problema, list):
      problema = [[0 if valor is None else valor for valor in fila] for fila in problema ]
      problema = np.array(problema, dtype= int)

    if solucion is None:
      solucion = problema.copy()
    if posibles is None:
      posibles = [[0 for x in range(9)]] * 9

    # Corroborar si el Sudoku está vacío
    vacio = (problema.sum() == 0)
    
    # Cuadro 27x27
    fig, ax = plt.subplots(figsize=(6, 6))
    ax.set_xlim(0.5, 27.5)
    ax.set_ylim(27.5, 0.5)
    ax.set_aspect('equal')
    ax.axis('off')

    # Dibujar el marco
    if (vacio):
      # Dibujar líneas gruesas
      thick_coords = np.array([0, 27]) + 0.5
      for coord in thick_coords:
          ax.plot([0.5, 27.5], [coord, coord], color= color_problema, linewidth= 4)
          ax.plot([coord, coord], [0.5, 27.5], color= color_problema, linewidth= 3)
      
      # Mensaje de iniciar el Sudoku
      ax.text(5 * 3 - 1, 3.5 * 3 + 1, "Press the `Play` button",
        ha= 'center', va= 'center',
        fontsize= 20, fontweight= 'bold',
        color= color_problema  
      )
      ax.text(5 * 3 - 1, 4.5 * 3 + 1, "to enjoy a new game!",
        ha= 'center', va= 'center',
        fontsize= 20, fontweight= 'bold',
        color= color_problema  
      )

      return fig

    # Dibujar líneas finas y gruesas
    fine_coords = np.arange(0.5, 28.0, 3)
    for coord in fine_coords:
      ax.plot([0.5, 27.5], [coord, coord], color='grey', linewidth=1)
      ax.plot([coord, coord], [0.5, 27.5], color='grey', linewidth=1)
        
    thick_coords = np.array([0, 9, 18, 27]) + 0.5
    for coord in thick_coords:
      ax.plot([0.5, 27.5], [coord, coord], color='black', linewidth=3)
      ax.plot([coord, coord], [0.5, 27.5], color='black', linewidth=3)
    
    # Dibujar el problema
    # Imprimir los números de la matriz problema (siempre que no sean 0 ni None)
    if problema is not None:
        for row in range(9):
            for col in range(9):
                valor = solucion[row][col]
                color = color_problema if (problema[row][col] > 0) or terminado else "black"
                negrilla = 'bold' if (problema[row][col] > 0) or terminado else 'normal'

                # Calcular el centro de la celda en las coordenadas del gráfico
                # Como el eje Y está invertido (27.5 a 0.5):
                # Fila 0 está arriba (cerca de 0.5 + 1.5 = 2.0)
                x = 0.5 + col * 3 + 1.5
                y = 0.5 + row * 3 + 1.5
                
                # Verificar que el valor sea válido para imprimir
                if valor is not None and valor != 0:                  
                    ax.text(
                        x, y, str(valor),
                        ha='center', va='center',
                        fontsize= 20, fontweight= negrilla,
                        color= color  
                    )
                else:
                  # Marcar  los números posibles
                  actual = posibles[row][col]
                  if (actual > 0):
                    # print(f"Bits celda [{row + 1},{col + 1}]:")

                    for bit_posible in range(9):
                      bit_activo = (actual >> bit_posible) & 1
                      if bit_activo:
                        xx = (bit_posible + 2) % 3 if ((bit_posible + 2) % 3) < 2 else -1
                        yy = floor(bit_posible / 3) - 1
                        # print(f"    Bit {bit_posible + 1}, x, y: [{xx}, {yy}]")


                        ax.text(
                            x + xx, y + yy, str(bit_posible + 1),
                            ha='center', va='center',
                            fontsize= 8, fontweight= "normal",
                            color= "black"  
                        )
      
    return fig

# Test ------
# fx_plot()
# ss1 = PuzzleGenerator.make_puzzle(ClassicSudoku, 9, 0.5)
# ss1 = fx_nuevo_sudoku(0.7)
# fx_plot(ss1)
# fx_plot(ss1, ss1)
# fx_plot(problema= [[x for x in range(1, 10)]] + [[0 for x in range(9)]] * 8, 
#   solucion= [[x for x in range(1, 10)]] + [[9 - x for x in range(9)]] + [[0 for x in range(9)]] * 6 + 
#     [[x for x in range(1, 10)]], 
#   posibles= [[273] + [0 for x in range(8)]] * 9
#   )
# fx_plot(ss1.board, ss1.solve().board)
# fx_plot(ss1.board, ss1.solve().board, terminado = True)
# fx_plot(
#   PuzzleGenerator.make_puzzle(ClassicSudoku, 9, 0.5).board,
#   np.zeros((9, 9), dtype= int),
#   np.zeros((9, 9), dtype= int),
#   False
# )



## fx_plot: Para imprimir el Sudoku ----
def fx_nuevo_sudoku(dificultad = 0.5):
  """Crear un Sudoku nuevo"""
  juego = PuzzleGenerator.make_puzzle(ClassicSudoku, 9, dificultad)
  # print(juego)
  juego = [[0 if valor is None else valor for valor in fila] for fila in juego.board ]
  juego = np.array(juego, dtype= int)
  return(juego)

# Test
fx_nuevo_sudoku()


## fx_leer_bit: Leer un bit de un entero ----
def fx_leer_bit(entero, posicion): 
  """Lee el bit de la posición indicada.
  """
  return ((entero >> posicion) & 1) > 0

# Test
fx_leer_bit(273, 4)
fx_leer_bit(273, 5)
[ x + 1 if fx_leer_bit(273, x) else 0 for x in range(9) ]


## fx_escribir_bit: Escribir en un bit de un entero ----
def fx_escribir_bit(entero, posicion, escribir_01): 
  """Escribe el bit en la posición indicada.
  """
  escribir_01 = 1 if escribir_01 > 0 else 0
  entero = entero & ~(1 << posicion)      # primero lo pone en 0
  return  entero | (escribir_01 << posicion)

# Test
# [fx_escribir_bit(0, x, 1) for x in range(9)]
# [fx_escribir_bit(0, x, True) for x in range(9)]
# [fx_escribir_bit(511, x, 0) for x in range(9)]
# [fx_escribir_bit(511, x, False) for x in range(9)]
# fx_escribir_bit(fx_escribir_bit(fx_escribir_bit(0, 0, 1), 4, 1), 8, 1)
# fx_escribir_bit(fx_escribir_bit(fx_escribir_bit(0, 0, 1), 4, 1), 8, True)
# fx_escribir_bit(273, 4, 0)


## fx_invertir_bit: Invierte el bit de un entero ----
def fx_invertir_bit(entero, posicion):
    """Invierte el bit en la posición indicada.

    Si el bit es 0, lo vuelve 1.
    Si el bit es 1, lo vuelve 0.
    """
    return entero ^ (1 << posicion)

# Test
[fx_invertir_bit(511, x) for x in range(9)]
[fx_invertir_bit(273, x) for x in range(9)]
fx_invertir_bit(273, 4)
fx_invertir_bit(fx_invertir_bit(273, 4), 4)


# Constantes -------------

# Instructions
instructions = """
### Instructions
1. Select the number you want to use for filling or marking in the upper selection buttons
  **TIP:** Press a number on the keyboard to select it
2. In the button **`Action`** select if you want to Fill or Mark
  **TIP:** Press **`[Ctrl]`** or **`[Shift]`** on the keyboard to toggle the selection
3. Click in the field you want to fill or mark with the selected number
4. Enjoy!
"""