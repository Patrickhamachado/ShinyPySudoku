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
from sudoku_class import Sudoku
from faicons import icon_svg


# UI: Gráfica --------------
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

# Server --------------
def server(input, output, session):

  # Inicialización valores reactivos ----
  numero_activo = reactive.Value(1)
  sudoku = reactive.Value(Sudoku())
  

  # Widget inp_fill_number ----
  @render_widget
  def inp_fill_number():
    return widgets.ToggleButtons(
      options = [x for x in range(1, 10)], 
      description = "",
      disabled = False,
      button_style = 'primary', # 'success', 'warning', 'danger', etc.
      tooltips = [str(x + 1) for x in range(9)]
    )

  # observeEvent plot_click ----
  @reactive.effect
  @reactive.event(input.mi_cuadricula_click)
  def input_plot_click():

    # Capturar las coordenadas del clic del usuario en la gráfica
    click = input.mi_cuadricula_click()
    x = click["x"]
    y = click["y"]
    # Calcular celda y valores
    llenar_fila = int((y - 0.5) // 3) + 1
    llenar_columna = int((x - 0.5) // 3) + 1
    llenar_con = reactive_read(inp_fill_number.widget, "value")
    definitivo = True if input.inp_marking() == "1" else False
    # print(f"Fila, columna: {llenar_fila}, {llenar_columna}")

    # with reactive.isolate():
    
    sudoku_temp = sudoku().copiar()
    sudoku_temp.play(llenar_con, llenar_fila, llenar_columna, definitivo = definitivo)
    
    # Mensaje si Sudoku terminado
    if (sudoku_temp.terminado): 
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

    # Actualización del valor reactivo
    sudoku.set(sudoku_temp) 
    

  # Gráfico principal ----
  @render.plot
  def mi_cuadricula():
    llenar_con = reactive_read(inp_fill_number.widget, "value")
    return sudoku().plot(num_resaltar= llenar_con)

  # reactive.effect play button ----
  @reactive.effect
  @reactive.event(input.play)
  def input_play():

    # Duplicar objeto
    sudoku_temp = sudoku().copiar()

    # Revisar si ya se empezó a resolver el juego
    solucion_inicida =  sudoku_temp.solucion.sum() > (sudoku_temp.solucion * sudoku_temp.problema).sum()
    posibles_iniciados = sudoku_temp.posibles.sum() > 0
    problema_vacio = sudoku_temp.problema.sum() == 0
    
    if((not (sudoku_temp.terminado) and (solucion_inicida or posibles_iniciados)) and
        not problema_vacio):
      
      # print("Solicitar confirmación...")
      m = ui.modal(
        "Are you sure you want to lose your progress and start a new game?",
        ui.br(), ui.br(),
        title= "New game",
        easy_close= False,  
        footer= (
          ui.input_action_button("confirmar_nuevo", "Yes"),
          ui.input_action_button("cancel_nuevo", "Cancel")
        )
      )  
      ui.modal_show(m) 

    else:
      sudoku_temp.iniciar(dificultad= float(input.inp_dificultad()), vacio= False)
      # Actualización del valor reactivo
      sudoku.set(sudoku_temp)
      ui.notification_show("Enjoy your Sudoku!", type = "message", duration= 2)


  # Botón nuevo juego confirmado ----
  @reactive.effect  
  @reactive.event(input.confirmar_nuevo)  
  def __():  
    ui.modal_remove()  
    sudoku_temp = sudoku().copiar()
    sudoku_temp.iniciar(dificultad= float(input.inp_dificultad()), vacio= False)
    # Actualización del valor reactivo
    sudoku.set(sudoku_temp)

    ui.notification_show("Enjoy your new Sudoku!", type = "message", duration= 2)

  # Botón nuevo juego Cancelado ----
  @reactive.effect  
  @reactive.event(input.cancel_nuevo)  
  def __():  
    ui.modal_remove()  
    # print("Nuevo juego cancelado")

  
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
  

  ## observe sudoku(): faltantes ----
  @reactive.effect
  @reactive.event(sudoku.get)  
  def cambios_sudoku():
    llenar_con = reactive_read(inp_fill_number.widget, "value")
    faltantes = sudoku().faltan
    opciones = [(str(x + 1) + " (" + str(faltantes[x]) + ")", x + 1) for x in range(9)]

    # Actualización de los botones
    inp_fill_number.widget.options = opciones 
    inp_fill_number.widget.value = llenar_con
    
  
# Llamado de aplicación ----
app = App(app_ui, server)
