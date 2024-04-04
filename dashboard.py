import tkinter as tk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Dados do Produto 1
labels = ['Preço de Compra', 'Imposto', 'Comissão', 'Lucro R$']
valores = [168.53, 23.07, 49.42, 88.48]

# Criar janela
root = tk.Tk()
root.title("Indicadores do Produto 1")

# Criar Canvas
canvas = tk.Canvas(root, width=600, height=400)
canvas.pack()

# Criar gráfico de pizza
fig, ax = plt.subplots()
wedges, texts, autotexts = ax.pie(valores, labels=labels, autopct='%1.1f%%', startangle=90)
ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle
ax.set_title('Indicadores do Produto 1')

# Adicionar legenda ao lado do gráfico
ax.legend(wedges, labels, title="Indicadores:", loc="center left", bbox_to_anchor=(1, 0, 0.5, 1))

# Adicionar gráfico ao Canvas
canvas = FigureCanvasTkAgg(fig, master=canvas)
canvas.draw()
canvas.get_tk_widget().pack()

root.mainloop()
