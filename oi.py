import tkinter as tk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Dados para o gráfico
labels = ['Lucro', 'Prejuízo']
sizes = [0, 19]
colors = ['#66c2a5', '#fc8d62']
explode = (0, 0.1)  # Explode a fatia do prejuízo

# Criar a figura e o eixo do gráfico de pizza
fig = Figure(figsize=(5, 5), dpi=100)
ax = fig.add_subplot(111)
ax.pie(sizes, explode=explode, labels=labels, colors=colors, autopct='%1.1f%%',
       shadow=True, startangle=90)

# Aspect ratio igual para garantir que a pizza seja desenhada como um círculo
ax.axis('equal')

# Criar a janela
root = tk.Tk()
root.title('Lucro/Prejuízo do Produto')

# Criar o canvas para exibir o gráfico na interface
canvas = FigureCanvasTkAgg(fig, master=root)
canvas_widget = canvas.get_tk_widget()
canvas_widget.pack()

# Função para fechar a janela
def fechar_janela():
    root.destroy()

# Adicionar um botão para fechar a janela
fechar_btn = tk.Button(root, text='Fechar', command=fechar_janela)
fechar_btn.pack()

# Iniciar o loop de eventos
root.mainloop()
