"""
import tkinter as tk
from tkinter.constants import *

window = tk.Tk()

frame_navigator = tk.PanedWindow(window, orient=VERTICAL)

frame_navigator.configure(background="white", width=300, height=300)
frame_navigator.pack_propagate(0)

searchbox = tk.Listbox(frame_navigator)
frame_navigator.add(searchbox)

template = tk.Listbox(frame_navigator, exportselection=True)
frame_navigator.add(template)

frame_navigator.pack(side=tk.TOP, expand=2, fill=tk.BOTH)

window.mainloop()

import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from numpy import array, arange, sin, pi
import tkinter as tk

root = tk.Tk()
root_panel = tk.Frame(root)
root_panel.pack(side="bottom", fill="both", expand="yes")

btn_panel = tk.Frame(root_panel, height=35)
btn_panel.pack(side='top', fill="both", expand="yes")

#img_arr = mpimg.imread('img/pic.jpg')
#imgplot = plt.imshow(img_arr)

#here is the example of how I embed matplotlib graph in Tkinter,
#basically, I want to do the same with the image (imgplot)
f = Figure()
a = f.add_subplot(111)
t = arange(0.0, 3.0, 0.01)
s = sin(2*pi*t)
a.plot(t, s)

canvas = FigureCanvasTkAgg(f, master=root)
#canvas.show()
canvas.get_tk_widget().pack(side="top", fill="both", expand=1)
canvas._tkcanvas.pack(side="top", fill="both", expand=1)

root.mainloop()


from tkinter import *
import pandas as pd
import matplotlib.pyplot as plt
from PIL import ImageTk, Image

def generate_plot():
    rate = float(entry_1.get())
    years_saving = int(entry_2.get())
    initial_savings = float(entry_3.get())
    yearly_contribution = float(entry_4.get())

    model = pd.DataFrame({'time': range(years_saving)})
    model['simple_exp'] = [initial_savings*rate**year for year in model['time']]
    model['yearly_invest'] = model['simple_exp'] + [yearly_contribution*(rate**year - 1)/(rate-1) for year in model['time']]

    final = model['yearly_invest'].sort_values(ascending= False).iloc[0]

    label_5 = Label(frame, text=f"You would have saved INR {final} by retirement")
    label_5.grid(row=0, column=0)

    plt.plot(model['time'], model['yearly_invest'])
    plt.title('Retirement Savings')
    plt.xlabel('Time in Years)')
    plt.ylabel('INR (Lacs)')
    plt.savefig('plot.png')

    load = Image.open('plot.png')
    render = ImageTk.PhotoImage(load)
    img = Label(frame, image = render)
    img.image = render
    img.grid(row=1, column=0)   
    # my_label = Label(frame, image = my_img)
    # my_label.grid(row=1, column=0)

    # img = ImageTk.PhotoImage(Image.open('plot.png'))
    # img_label = Label(frame, image = img)
    # img_label.grid(row=1, column=0)

root = Tk()

label_1 = Label(root, text = 'INTEREST RATE(%)')
label_2 = Label(root, text = 'NUMBER OF YEARS IN SAVINGS')
label_3 = Label(root, text = 'INITIAL CORPUS (INR LACS)')
label_4 = Label(root, text = 'YEARLY CONTRIBUTION (INR LACS')
frame = Frame(root, width=300, height=300)
button = Button(root, text="GENERATE PLOT", command = generate_plot, padx = 5, pady=5)

entry_1 = Entry(root)
entry_2 = Entry(root)
entry_3 = Entry(root)
entry_4 = Entry(root)

label_1.grid(row=0, column=0, pady=5, padx=5)
entry_1.grid(row=0, column=1, pady=5, padx=5)

label_2.grid(row=1, column=0, pady=5, padx=5)
entry_2.grid(row=1, column=1, pady=5, padx=5)

label_3.grid(row=2, column=0, pady=5, padx=5)
entry_3.grid(row=2, column=1, pady=5, padx=5)

label_4.grid(row=3, column=0, pady=5, padx=5)
entry_4.grid(row=3, column=1, pady=5, padx=5)

button.grid(row=4,column=0, columnspan=2, pady=20, padx=5)

frame.grid(row=5, column=0, columnspan = 2, padx = 5, pady = 5)

root.mainloop()


from tkinter import *
from tkinter import font

root = Tk()
root.title('Font Families')
fonts=list(font.families())
fonts.sort()

def populate(frame):
    '''Put in the fonts'''
    listnumber = 1
    for item in fonts:
        label = "listlabel" + str(listnumber)
        label = Label(frame,text=item,font=(item, 16)).pack()
        listnumber += 1

def onFrameConfigure(canvas):
    '''Reset the scroll region to encompass the inner frame'''
    canvas.configure(scrollregion=canvas.bbox("all"))

canvas = Canvas(root, borderwidth=0, background="#ffffff")
frame = Frame(canvas, background="#ffffff")
vsb = Scrollbar(root, orient="vertical", command=canvas.yview)
canvas.configure(yscrollcommand=vsb.set)

vsb.pack(side="right", fill="y")
canvas.pack(side="left", fill="both", expand=True)
canvas.create_window((4,4), window=frame, anchor="nw")

frame.bind("<Configure>", lambda event, canvas=canvas: onFrameConfigure(canvas))

populate(frame)

root.mainloop()



import tkinter as tk
import platform

# ************************
# Scrollable Frame Class
# ************************
class ScrollFrame(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent) # create a frame (self)

        self.canvas = tk.Canvas(self, borderwidth=0, background="#ffffff")          #place canvas on self
        self.viewPort = tk.Frame(self.canvas, background="#ffffff")                    #place a frame on the canvas, this frame will hold the child widgets 
        self.vsb = tk.Scrollbar(self, orient="vertical", command=self.canvas.yview) #place a scrollbar on self 
        self.canvas.configure(yscrollcommand=self.vsb.set)                          #attach scrollbar action to scroll of canvas

        self.vsb.pack(side="right", fill="y")                                       #pack scrollbar to right of self
        self.canvas.pack(side="left", fill="both", expand=True)                     #pack canvas to left of self and expand to fil
        self.canvas_window = self.canvas.create_window((4,4), window=self.viewPort, anchor="nw",            #add view port frame to canvas
                                  tags="self.viewPort")

        self.viewPort.bind("<Configure>", self.onFrameConfigure)                       #bind an event whenever the size of the viewPort frame changes.
        self.canvas.bind("<Configure>", self.onCanvasConfigure)                       #bind an event whenever the size of the canvas frame changes.
            
        self.viewPort.bind('<Enter>', self.onEnter)                                 # bind wheel events when the cursor enters the control
        self.viewPort.bind('<Leave>', self.onLeave)                                 # unbind wheel events when the cursorl leaves the control

        self.onFrameConfigure(None)                                                 #perform an initial stretch on render, otherwise the scroll region has a tiny border until the first resize

    def onFrameConfigure(self, event):                                              
        '''Reset the scroll region to encompass the inner frame'''
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))                 #whenever the size of the frame changes, alter the scroll region respectively.

    def onCanvasConfigure(self, event):
        '''Reset the canvas window to encompass inner frame when required'''
        canvas_width = event.width
        self.canvas.itemconfig(self.canvas_window, width = canvas_width)            #whenever the size of the canvas changes alter the window region respectively.

    def onMouseWheel(self, event):                                                  # cross platform scroll wheel event
        if platform.system() == 'Windows':
            self.canvas.yview_scroll(int(-1* (event.delta/120)), "units")
        elif platform.system() == 'Darwin':
            self.canvas.yview_scroll(int(-1 * event.delta), "units")
        else:
            if event.num == 4:
                self.canvas.yview_scroll( -1, "units" )
            elif event.num == 5:
                self.canvas.yview_scroll( 1, "units" )
    
    def onEnter(self, event):                                                       # bind wheel events when the cursor enters the control
        if platform.system() == 'Linux':
            self.canvas.bind_all("<Button-4>", self.onMouseWheel)
            self.canvas.bind_all("<Button-5>", self.onMouseWheel)
        else:
            self.canvas.bind_all("<MouseWheel>", self.onMouseWheel)

    def onLeave(self, event):                                                       # unbind wheel events when the cursorl leaves the control
        if platform.system() == 'Linux':
            self.canvas.unbind_all("<Button-4>")
            self.canvas.unbind_all("<Button-5>")
        else:
            self.canvas.unbind_all("<MouseWheel>")



# ********************************
# Example usage of the above class
# ********************************

class Example(tk.Frame):
    def __init__(self, root):

        tk.Frame.__init__(self, root)
        self.scrollFrame = ScrollFrame(self) # add a new scrollable frame.
        
        # Now add some controls to the scrollframe. 
        # NOTE: the child controls are added to the view port (scrollFrame.viewPort, NOT scrollframe itself)
        for row in range(100):
            a = row
            tk.Label(self.scrollFrame.viewPort, text="%s" % row, width=3, borderwidth="1", 
                     relief="solid").grid(row=row, column=0)
            t="this is the second column for row %s" %row
            tk.Button(self.scrollFrame.viewPort, text=t, command=lambda x=a: self.printMsg("Hello " + str(x))).grid(row=row, column=1)

        # when packing the scrollframe, we pack scrollFrame itself (NOT the viewPort)
        self.scrollFrame.pack(side="top", fill="both", expand=True)
    
    def printMsg(self, msg):
        print(msg)

if __name__ == "__main__":
    root=tk.Tk()
    Example(root).pack(side="top", fill="both", expand=True)
    root.mainloop()


import tkinter as tk
from tkinter.filedialog import askopenfilename

def UploadAction(event=None):
    filename = askopenfilename()
    # Cut path to the file off
    filename = filename.split('/')[len(filename.split('/'))-1]
    print('Selected:', filename)
    label1['text'] = filename

root= tk.Tk()
    
button1 = tk.Button(text='Click Me', command=UploadAction, bg='brown', fg='white')
button1.pack(padx=2, pady=5)
label1 = tk.Label(text='Please choose a file')
label1.pack(padx=2, pady=2)

root.mainloop()


import tkinter as tk


def populate(frame):
    '''Put in some fake data'''
    for row in range(100):
        tk.Label(frame, text="%s" % row, width=3, borderwidth="1", 
                 relief="solid").grid(row=row, column=0)
        t="this is the second column for row %s" %row
        tk.Label(frame, text=t).grid(row=row, column=1)


def onFrameConfigure(canvas):
    '''Reset the scroll region to encompass the inner frame'''
    canvas.configure(scrollregion=canvas.bbox("all"))

root = tk.Tk()
canvas = tk.Canvas(root, borderwidth=0, background="#ffffff")
frame = tk.Frame(canvas, background="#ffffff")
vsb = tk.Scrollbar(root, orient="vertical", command=canvas.yview)
canvas.configure(yscrollcommand=vsb.set)

vsb.grid(row=0, column=1, sticky="ns")
canvas.grid(row=0, column=0, sticky="nsew")
#vsb.pack(side="right", fill="y")
#canvas.pack(side="left", fill="both", expand=True)
canvas.create_window((16,16), window=frame, anchor="nw")

frame.bind("<Configure>", lambda event, canvas=canvas: onFrameConfigure(canvas))

populate(frame)

root.mainloop()

import tkinter as tk
from tkinter import *
from tkinter import ttk
my_w = tk.Tk()
my_w.geometry("400x200")
my_tabs = ttk.Notebook(my_w, padding=20)  # declaring

tab0 = ttk.Frame(my_tabs)
tab1 = ttk.Frame(my_tabs)
tab2 = ttk.Frame(my_tabs)
r1 = tk.PhotoImage(file='../figures/time_series_plots/+3.3V_Imon_time_series_plot.png')
y1 = tk.PhotoImage(file='../figures/time_series_plots/+5.2V_Imon_time_series_plot.png')
g1 = tk.PhotoImage(file='../figures/time_series_plots/+10V_Imon_time_series_plot.png')
my_tabs.add(tab0, text='Tab-0', image=r1, compound='bottom')
my_tabs.add(tab1, text='Tab-1', image=y1, compound='top')
my_tabs.add(tab2, text='Tab-2', image=g1, compound='right')
my_tabs.pack(expand=1, fill="both")

font1 = ('times', 24, 'normal')
l1 = tk.Label(tab0, text='I am tab-0', bg='yellow', font=font1)
l1.place(relx=0.4, rely=0.2)  # using place


l2 = tk.Label(tab1, text='I am tab-1', bg='yellow', font=font1)
l2.place(relx=0.4, rely=0.2)  # using place
l3 = tk.Label(tab2, text='I am tab-2', bg='yellow', font=font1)
l3.place(relx=0.4, rely=0.2)  # using place

my_w.mainloop()  # Keep the window open


import tkinter as Tkinter
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure


class Application():
    def __init__(self, master):

        master.columnconfigure(0, weight=1)
        master.rowconfigure(0, weight=1)
        frame2 = Tkinter.Frame(master, bg='red')
        frame2.grid(row=0, column=0, sticky='nsew')
        frame2.columnconfigure(0, weight=1)
        frame2.rowconfigure(0, weight=1)

        frame2a = Tkinter.Frame(frame2, bg='blue')
        frame2a.grid(row=0, column=0, sticky='nsew')
        frame2a.columnconfigure(0, weight=1)
        frame2a.rowconfigure(0, weight=1)

        frame2b = Tkinter.Frame(frame2, bg='green')
        frame2b.grid(row=1, column=0, sticky='nsew')
        frame2b.columnconfigure(0, weight=1)
        frame2b.rowconfigure(1, weight=1)

        # add plot
        fig = Figure(figsize=(9.5, 5.2), facecolor='white')
        fig.add_subplot(111)
        canvas = FigureCanvasTkAgg(fig, master=frame2b)

        canvas.get_tk_widget().pack(side='top', fill='both', expand=1)


if __name__ == '__main__':

    root = Tkinter.Tk()
    root.geometry("200x200")
    app = Application(root)
    root.mainloop()


from tkinter import ttk
import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib
matplotlib.use('TkAgg')


class My_GUI:

    def __init__(self, master):
        self.master = master
        master.title("Dashboard")
        f = Figure(figsize=(5, 5), dpi=100)
        a = f.add_subplot(111)
        a.scatter([1, 2, 3, 4, 5, 6, 7, 8], [5, 6, 1, 3, 8, 9, 3, 5])
        canvas1 = FigureCanvasTkAgg(f, master)
        canvas1.draw()
        canvas1.get_tk_widget().pack(side="top", fill='both', expand=True)


root = tk.Tk()
gui = My_GUI(root)
root.mainloop()

# Mouse scroll thingy
import tkinter as tk


class Example(tk.Frame):
    def __init__(self, root):
        tk.Frame.__init__(self, root)
        self.canvas = tk.Canvas(
            self, width=400, height=400, background="bisque")
        self.xsb = tk.Scrollbar(self, orient="horizontal",
                                command=self.canvas.xview)
        self.ysb = tk.Scrollbar(self, orient="vertical",
                                command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.ysb.set,
                              xscrollcommand=self.xsb.set)
        self.canvas.configure(scrollregion=(0, 0, 1000, 1000))

        self.xsb.grid(row=1, column=0, sticky="ew")
        self.ysb.grid(row=0, column=1, sticky="ns")
        self.canvas.grid(row=0, column=0, sticky="nsew")
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # This is what enables scrolling with the mouse:
        self.canvas.bind("<ButtonPress-1>", self.scroll_start)
        self.canvas.bind("<B1-Motion>", self.scroll_move)

    def scroll_start(self, event):
        self.canvas.scan_mark(event.x, event.y)

    def scroll_move(self, event):
        self.canvas.scan_dragto(event.x, event.y, gain=1)


if __name__ == "__main__":
    root = tk.Tk()
    Example(root).pack(fill="both", expand=True)
    root.mainloop()


fig = plt.figure(figsize=(6, 6))
grid = plt.GridSpec(4, 4, hspace=0.2, wspace=0.2)
main_ax = fig.add_subplot(grid[:-1, 1:])
y_hist = fig.add_subplot(grid[:-1, 0], xticklabels=[], sharey=main_ax)
x_hist = fig.add_subplot(grid[-1, 1:], yticklabels=[], sharex=main_ax)

# scatter points on the main axes
main_ax.plot(x, y, 'ok', markersize=3, alpha=0.2)

# histogram on the attached axes
x_hist.hist(x, 40, histtype='stepfilled',
            orientation='vertical', color='gray')
x_hist.invert_yaxis()

y_hist.hist(y, 40, histtype='stepfilled',
            orientation='horizontal', color='gray')
y_hist.invert_xaxis()


from torch import norm


fig = plt.figure(num=None, figsize=(5,5),
                 facecolor='w', edgecolor='k')
fig.subplots_adjust(left=0.01, right=0.99, top=0.99,
                    bottom=0.01, wspace=0., hspace=0)

gs = plt.GridSpec(4, 4, hspace=0.02, wspace=0.02)
axs1 = fig.add_subplot(gs[0:-1, :-1])
y_hist = fig.add_subplot(gs[:-1, -1], xticklabels=[], sharey=axs1)
x_hist = fig.add_subplot(gs[-1, 1:], yticklabels=[], sharex=axs1)

counts, xedges, yedges, im = axs1.hist2d(df_slice_sci["x_val"], df_slice_sci["y_val"], bins=50,
           range=[[0.31, 0.62], [0.31, 0.61]], cmin=1, density=True, cmap='Blues', norm=mpl.colors.LogNorm())

fig.colorbar(im, ax=axs1)
# Number of data along x-axis
xn = [np.nansum(counts[i, :]) for i in range(counts.shape[0])]
# Number of data along y-axis
yn = [np.nansum(counts[:, i]) for i in range(counts.shape[1])]

# Add step plot of x-axis
x_hist.step(xedges[:-1], xn, color='k', lw=1)
# Add step plot of y-axis
y_hist.step(yn, yedges[:-1], color='k', lw=1)
plt.show()
#plt.colorbar()

import tkinter as tk


def get_curr_screen_geometry():
    '''
    Workaround to get the size of the current screen in a multi-screen setup.

    Returns:
        geometry (str): The standard Tk geometry string.
            [width]x[height]+[left]+[top]
    '''
    root = tk.Tk()
    root.update_idletasks()
    root.attributes('-fullscreen', True)
    root.state('iconic')
    geometry = root.winfo_geometry()
    root.destroy()
    return geometry

get_curr_screen_geometry()

import tkinter as tk
root = tk.Tk()

width_px = root.winfo_screenwidth()
height_px = root.winfo_screenheight()
width_mm = root.winfo_screenmmwidth()
height_mm = root.winfo_screenmmheight()
# 2.54 cm = in
width_in = width_mm / 25.4
height_in = height_mm / 25.4
width_dpi = width_px/width_in
height_dpi = height_px/height_in

print('Width: %i px, Height: %i px' % (width_px, height_px))
print('Width: %i mm, Height: %i mm' % (width_mm, height_mm))
print('Width: %f in, Height: %f in' % (width_in, height_in))
print('Width: %f dpi, Height: %f dpi' % (width_dpi, height_dpi))

import ctypes
user32 = ctypes.windll.user32
user32.SetProcessDPIAware()
[w, h] = [user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)]
print('Size is %f %f' % (w, h))

curr_dpi = w*96/width_px
print('Current DPI is %f' % (curr_dpi))

import platform
import os
if platform.system() == 'Windows':
    import tkinter as tk
    root = tk.Tk()

    width_px = root.winfo_screenwidth()
    height_px = root.winfo_screenheight()
    width_mm = root.winfo_screenmmwidth()
    height_mm = root.winfo_screenmmheight()
    # 2.54 cm = in
    width_in = width_mm / 25.4
    height_in = height_mm / 25.4
    width_dpi = width_px/width_in
    height_dpi = height_px/height_in

    print('Width: %i px, Height: %i px' % (width_px, height_px))
    print('Width: %i mm, Height: %i mm' % (width_mm, height_mm))
    print('Width: %f in, Height: %f in' % (width_in, height_in))
    print('Width: %f dpi, Height: %f dpi' % (width_dpi, height_dpi))

    import ctypes
    user32 = ctypes.windll.user32
    user32.SetProcessDPIAware()
    [w, h] = [user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)]
    print('Size is %f %f' % (w, h))

    curr_dpi = w*96/width_px
    print('Current DPI is %f' % (curr_dpi))

elif platform.system() == 'Linux':
    
    # Get the system resolution and size for an ubuntu machine and save it to a variable
    os.system('xrandr | grep "mm" > screen_info.txt')
    #xx = os.system('xrandr')


# Use lambda function to pass the function as an argument
lambda_func = lambda x, y: test_func(x, y)


from tkinter import *

# a subclass of Canvas for dealing with resizing of windows
class ResizingCanvas(Canvas):
    def __init__(self,parent,**kwargs):
        Canvas.__init__(self,parent,**kwargs)
        self.bind("<Configure>", self.on_resize)
        self.height = self.winfo_reqheight()
        self.width = self.winfo_reqwidth()

    def on_resize(self,event):
        # determine the ratio of old width/height to new width/height
        wscale = float(event.width)/self.width
        hscale = float(event.height)/self.height
        self.width = event.width
        self.height = event.height
        # resize the canvas 
        self.config(width=self.width, height=self.height)
        # rescale all the objects tagged with the "all" tag
        self.scale("all",0,0,wscale,hscale)

def main():
    root = Tk()
    myframe = Frame(root)
    myframe.pack(fill=BOTH, expand=YES)
    mycanvas = ResizingCanvas(myframe,width=850, height=400, bg="red", highlightthickness=0)
    mycanvas.pack(fill=BOTH, expand=YES)

    # add some widgets to the canvas
    mycanvas.create_line(0, 0, 200, 100)
    mycanvas.create_line(0, 100, 200, 0, fill="red", dash=(4, 4))
    mycanvas.create_rectangle(50, 25, 150, 75, fill="blue")

    # tag all of the drawn widgets
    mycanvas.addtag_all("all")
    root.mainloop()

if __name__ == "__main__":
    main()
"""

