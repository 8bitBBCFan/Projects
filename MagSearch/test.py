from tkinter import *      
root = Tk()      
canvas = Canvas(root, width = 1000, height = 1000)     
canvas.pack()      
img = PhotoImage(file="/home/pi/Documents/MagPi+Magnifier.png")      
canvas.create_image(20,20, anchor=NW, image=img)      
mainloop()
