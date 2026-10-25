from sudoku import ClassicSudoku, DiagonalSudoku
from sudoku.base_sudoku import PuzzleGenerator


# Classic Sudoku

puzzle = ClassicSudoku(size = 9)
print("Puzzle:")
print(puzzle)

solution = puzzle.solve()
print("Solved:")
print(solution)


# Diagonal Sudoku

puzzle = DiagonalSudoku(size=9)
solution = puzzle.solve()

# Generating Puzzles

puzzle = PuzzleGenerator.make_puzzle(
    sudoku_cls = ClassicSudoku,
    size = 9,
    difficulty = 0.5,
    ensure_unique = True
)
print(puzzle)
solution = puzzle.solve()

# Impresión del board

for fila, sublista in enumerate(solution.board):
    for columna, elemento in enumerate(sublista):
        print(f"datos[{fila + 1}][{columna + 1}] = {elemento}")

for fila, sublista in enumerate(solution.board):
    print(f"Fila [{fila + 1}] = ", end = " ")
    for elemento in sublista:
        print(elemento, end=" ")
    print()


# Manejo de bits --------
# Leer un bit
posicion = 0
valor = 0b1010  # 10 en decimal
bit = (valor >> posicion) & 1
print((valor >> 0) & 1)  # 0
print((valor >> 1) & 1)  # 1
print((valor >> 3) & 1)  # 1

# Escribir un bit en 1
valor = valor | (1 << posicion)

valor = 0b1010


valor = valor | (1 << posicion)

print(bin(valor))  # 0b1011

# Módulo ----

if 1:
    print("Si")
else:
    print("No")
    