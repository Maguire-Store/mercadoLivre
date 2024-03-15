import tkinter as tk

root = tk.Tk()

screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

print(f"Resolution: {screen_width}x{screen_height}")

root.mainloop()
