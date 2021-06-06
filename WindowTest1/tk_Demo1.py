from tkinter import *
from tkinter import ttk

def calculate(*args):
    value=float(feet.get())
    meters.set(int(0.3048 * value * 10000.0 + 0.5)/10000.0)

Wind1 = Tk()
Wind1.title='windowtest'

panel = ttk.Frame(Wind1,padding='3 3 12 12')
panel.grid(column=0,row=0,sticky=(N,W,E,S))
Wind1.columnconfigure(0,weight=1)
Wind1.rowconfigure(0,weight=1)

feet=StringVar()
feet_entry=ttk.Entry(panel,width=7,textvariable=feet)
feet_entry.grid(column=2,row=1,sticky=(W,E))

meters=StringVar()
ttk.Label(panel,textvariable=meters).grid(column=2,row=2,sticky=(W,E))

ttk.Button(panel,text='calculate',command=calculate).grid(column=3,row=3,sticky=W)

ttk.Label(panel,text='feet').grid(column=3,row=1,sticky=W)
ttk.Label(panel,text='is equivalent to').grid(column=1,row=2,sticky=E)
ttk.Label(panel,text='meters').grid(column=3,row=2,sticky=W)

for child in panel.winfo_children():
    child.grid_configure(padx=5,pady=5)
feet_entry.focus()
Wind1.bind('<Return>',calculate)

Wind1.mainloop()