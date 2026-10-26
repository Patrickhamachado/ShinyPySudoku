# Load data and compute static values

# from win32.win32security import SE_INC_WORKING_SET_NAME
from shiny import App, reactive, render, ui 
import matplotlib.pyplot as plt
import numpy as np
from shinywidgets import output_widget, render_widget, reactive_read
import ipywidgets as widgets
from globals import instructions, fx_plot, fx_nuevo_sudoku, fx_invertir_bit
from sudoku import ClassicSudoku, DiagonalSudoku
from sudoku.base_sudoku import PuzzleGenerator
from faicons import icon_svg


# UI: Gráfica
app_ui = ui.page_navbar(

  ui.nav_panel("Game", 

    # Script para detectar las teclas
    ui.tags.script("""
        document.addEventListener('keyup', function(event) {
            // Ignorar si la tecla se está manteniendo presionada (repetición del sistema)
            if (event.repeat) return;
            // Enviar el nombre de la tecla a Shiny a través del input personalizado 'tecla_global'
            Shiny.setInputValue('tecla_global', {
                key: event.key,
                code: event.code,
                timestamp: new Date().getTime()
            }, {priority: 'event'});
        });
    """),

    # Add Font Awesome CSS in the head
    ui.tags.head(
        ui.tags.link(
            rel = "stylesheet",
            href = "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.7.2/css/all.min.css",
        )
    ),

    ui.layout_columns(

      ui.input_action_button("play", label = "Play",
        icon = ui.tags.i(class_ = "fa-solid fa-play-circle"),
        width="240px",
        class_="btn-primary",
        style = "margin-top: 16px;", 
      ),

      ui.input_selectize("inp_dificultad", "Level:",
        # {16: "Very easy", 28:"Easy", 41: "Medium", 49: "Hard", 57: "Very hard"},
        {0.2: "Very easy", 0.35:"Easy", 0.5: "Medium", 0.6: "Hard", 0.7: "Very hard"},
        selected = 0.5
      ),

      ui.input_radio_buttons("inp_marking", "Action:",
        {"1": "Fill", "2": "Mark"},
        inline = True
      )
    ),

    output_widget("inp_fill_number"),
    
    # ui.output_text("out_fill_number"),  # Ocultar
    # ui.hr(),

    ui.output_plot("mi_cuadricula", click = True), # Habilita la captura de clics
    # ui.output_text("info_clic")        # Ocultar
    
  ),

  ui.nav_panel("?", ui.markdown(instructions)),

  title = ui.h2("Shiny Sudoku"), 
  id = "navbar"
)

# Server
def server(input, output, session):

  # Inicialización valores reactivos ----
  numero_activo = reactive.Value(1)
  # sudoku_problema = reactive.Value(PuzzleGenerator.make_puzzle(ClassicSudoku, 9, 0.5).board)
  # sudoku_solucion = reactive.Value([[0 for x in range(9)]] * 9)
  # sudoku_posibles = reactive.Value([[0 for x in range(9)]] * 9)
  # sudoku_resuelto = reactive.Value(False)
  sudoku_problema = reactive.Value(np.zeros((9, 9), dtype= int))
  sudoku_solucion = reactive.Value(np.zeros((9, 9), dtype= int))
  sudoku_posibles = reactive.Value(np.zeros((9, 9), dtype= int))
  sudoku_resuelto = reactive.Value(False)
  
  # Observar cuando el usuario presiona una tecla ----
  @reactive.effect
  def _():
      evento = input.tecla_global()
      if evento is not None:
        name = evento.get("key", "")
        code = evento.get("code", "")
      
        # Identificar si se trata de un número
        if name in ["1", "2", "3", "4", "5", "6", "7", "8", "9"]:
          # Actualizar la variable reactiva
          numero_activo.set(int(name))
          # Actualizar directamente el valor del widget de ipywidgets en Python
          inp_fill_number.widget.value = int(name)

        # Identificar si se trata de un comando para cambiar la Acción
        elif name in ["Shift", "Control"]:
          # AISLAR LA LECTURA usando el contexto with de Python
          with reactive.isolate():
              actual_marking = input.inp_marking()
          
          cambiar = "2" if actual_marking == "1" else "1"

          ui.update_radio_buttons(
              "inp_marking", 
              selected = cambiar # Nuevo valor seleccionado
          )


  # Widget inp_fill_number ----
  @render_widget
  def inp_fill_number():
    return widgets.ToggleButtons(
      options = [x for x in range(1, 10)], 
      description = '',
      disabled = False,
      button_style = 'primary', # 'success', 'warning', 'danger', etc.
      tooltips = [str(x + 1) for x in range(9)], 
      icons = ["play-circle", "two"]
    )

  # Salida texto out_fill_number - mostrando el valor del número seleccionado - Ocultar ----
  @render.text
  def out_fill_number():
    val = reactive_read(inp_fill_number.widget, "value")
    return f"The value of the inp_fill_number is: {val}"
    
  # Gráfico principal mi_cuadricula ----
  @render.plot
  def mi_cuadricula():
    return fx_plot(sudoku_problema(), sudoku_solucion(), sudoku_posibles(), sudoku_resuelto())

  
  # observeEvent plot_click ----
  @reactive.effect
  @reactive.event(input.mi_cuadricula_click)
  def input_plot_click():

    # Si ya se resolvió el juego, mostrar pantalla inicial
    if(sudoku_resuelto()):
      sudoku_problema.set(np.zeros((9, 9), dtype= int))
      sudoku_solucion.set(np.zeros((9, 9), dtype= int))
      sudoku_posibles.set(np.zeros((9, 9), dtype= int))
      sudoku_resuelto.set(False)

    # with reactive.isolate():
    definitivo = True if input.inp_marking() == "1" else False
    problema = sudoku_problema().copy()
    solucion = sudoku_solucion().copy()
    solucion_actual = solucion.copy()
    posibles = sudoku_posibles().copy()
    posibles_actual = posibles.copy()

    # Capturar las coordenadas del clic del usuario en la gráfica
    click = input.mi_cuadricula_click()
    x = click["x"]
    y = click["y"]
    # Calcular celda y valores
    llenar_fila = int((y - 0.5) // 3)
    llenar_columna = int((x - 0.5) // 3)
    llenar_con = reactive_read(inp_fill_number.widget, "value")
    
    # Actualizar solucion o posibles
    if ((llenar_fila >= 0) and (llenar_fila < 9) and
        (llenar_columna >= 0) and (llenar_columna < 9) ):

      # Revisar si es una celda modificable
      if (problema[llenar_fila, llenar_columna] == 0):

        if (definitivo):
          # Editar la matriz de números fijos
          if (solucion[llenar_fila, llenar_columna] == llenar_con):
            solucion[llenar_fila, llenar_columna] = 0
          else:
            solucion[llenar_fila, llenar_columna] = llenar_con
                      
          # Actualizar el valor reactivo si hubo cambios
          if (not np.array_equal(solucion_actual, solucion)):
            sudoku_solucion.set(solucion)
            
            # Corroborar si ya está solucionado o está vacío
            suma_filas = np.sum(solucion, axis= 1)
            suma_columnas = np.sum(solucion, axis= 0)
            terminado = np.all(suma_filas == 45) and np.all(suma_columnas == 45)
            
            # Mensaje si Sudoku terminado
            if (terminado and not sudoku_resuelto()): 
              ui.show_toast(
                ui.toast(
                    "You have solved the Sudoku just fine!",
                    header= ui.toast_header(
                        "Congrats !!", status=None, icon= icon_svg("circle-check")
                    ),
                    # icon= icon_svg("hands-clapping"),
                    type= "primary",
                    id= "toast_victoria",
                    duration_s= 0,
                    position= "middle center",
                )
              )
              sudoku_resuelto.set(True)

        else:
          if (solucion[llenar_fila, llenar_columna] == 0):
            
            # Editar la matriz de números opcionados
            actual = posibles[llenar_fila, llenar_columna]
            actual = fx_invertir_bit(actual, llenar_con - 1)
            posibles[llenar_fila, llenar_columna] = actual
            
            # Actualizar el valor reactivo
            sudoku_posibles.set(posibles)
            
  
  # Texto para mostrar el click en el gráfico: info_clic ----
  @render.text
  def info_clic():
    # Capturar las coordenadas del clic del usuario en la gráfica
    click = input.mi_cuadricula_click()
    if click is None:
      return "Haz clic en cualquier celda de la cuadrícula..."
    
    x = click["x"]
    y = click["y"]
    
    # Calcular celda
    col = int((x - 0.5) // 3)
    row = int((y - 0.5) // 3)
    
    if 0 <= col < 9 and 0 <= row < 9:
      return f"Clic detectado: Fila {row + 1}, Columna {col + 1} (Coordenadas X: {x:.2f}, Y: {y:.2f})"
    else:
      return "Hiciste clic fuera de la cuadrícula principal."

  # reactive.effect play button ----
  @reactive.effect
  @reactive.event(input.play)
  def input_play():

    # Revisar si ya se empezó a resolver el juego
    solucion_inicida = not np.array_equal(sudoku_problema(), sudoku_solucion())
    posibles_iniciados = not np.array_equal(sudoku_posibles(), np.zeros((9, 9), dtype= int))
    problema_vacio = np.array_equal(sudoku_problema(), np.zeros((9, 9), dtype= int))
    
    if((not (sudoku_resuelto()) and (solucion_inicida or posibles_iniciados)) and
        not problema_vacio):
      
      # print("Solicitar confirmación...")
      m = ui.modal(
        "Are you sure you want to lose your progress and start a new game?",
        ui.br(), ui.br(),
        # ui.input_action_button("confirmar_nuevo", "Yes"),
        # ui.input_action_button("cancel_nuevo", "Cancel"),
        title= "New game",
        easy_close= False,  
        footer= (
          ui.input_action_button("confirmar_nuevo", "Yes"),
          ui.input_action_button("cancel_nuevo", "Cancel")
        )
      )  
      ui.modal_show(m) 

    else:
      # print("Iniciar juego sin tema")
      # print(f"Iniciar juego - Dificultad: {input.inp_dificultad()}")
      # nuevo_sudoku = PuzzleGenerator.make_puzzle(ClassicSudoku, 9, float(input.inp_dificultad())).board
      nuevo_sudoku = fx_nuevo_sudoku(float(input.inp_dificultad()))
      sudoku_problema.set(nuevo_sudoku.copy())
      sudoku_solucion.set(nuevo_sudoku.copy())
      sudoku_posibles.set(np.zeros((9, 9), dtype= int))
      sudoku_resuelto.set(False)
      ui.notification_show("Enjoy your Sudoku!", type = "message", duration= 2)


  # Botón nuevo juego confirmado ----
  @reactive.effect  
  @reactive.event(input.confirmar_nuevo)  
  def __():  
    ui.modal_remove()  
    # print("Inicio confirmado")
    # print(f"Iniciar juego - Dificultad: {input.inp_dificultad()}")
    nuevo_sudoku = fx_nuevo_sudoku(float(input.inp_dificultad()))
    sudoku_problema.set(nuevo_sudoku.copy())
    sudoku_solucion.set(nuevo_sudoku.copy())
    sudoku_posibles.set(np.zeros((9, 9), dtype= int))
    sudoku_resuelto.set(False)
    ui.notification_show("Enjoy your new Sudoku!", type = "message", duration= 2)

  # Botón nuevo juego Cancelado ----
  @reactive.effect  
  @reactive.event(input.cancel_nuevo)  
  def __():  
    ui.modal_remove()  
    # print("Nuevo juego cancelado")
    

# Llamado de aplicación ----
app = App(app_ui, server)
