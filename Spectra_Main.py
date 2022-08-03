import sys
import os
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QTabWidget, QPlainTextEdit, QTextEdit, QLabel, QGridLayout, QHBoxLayout, \
                            QMainWindow, QApplication, QVBoxLayout, QWidget, QPushButton, QLineEdit, QFileDialog
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
from matplotlib.widgets import Cursor 
import matplotlib as mpl
import matplotlib.pyplot as plt
import mplcursors

import pandas as pd
import numpy as np
from scipy import sparse
from scipy import signal
from scipy.sparse.linalg import spsolve
from scipy.signal import savgol_filter

import seaborn as sns

# Choose dpi for image
mpl.rcParams['figure.dpi'] = 160 


# Change style in plot 
sns.set_style("darkgrid",{
            'xtick.color':'#999999',
            'ytick.color':'#999999',
            'xtick.labelsize': .5,
            'ytick.labelsize': .5,
            'font.family':'serif',
            'axes.grid': True,
            })


DIR = r'C:'

class Canvas(FigureCanvasQTAgg):
    def __init__(self, parent=None, width=5, height=5, dpi=160):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        super(Canvas, self).__init__(fig)
        def onframe(event):
            self.setCursor(Qt.BlankCursor)
        fig.canvas.mpl_connect('figure_enter_event',onframe)

class App(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle('Spectra')
        self.resize(900,600)

        self.table_widget = MyTableWidget(self)
        self.setCentralWidget(self.table_widget)
        
        self.show()
    
class MyTableWidget(QWidget):
    
    def __init__(self, parent):
        super().__init__()
        self.layout = QVBoxLayout()

        # Create the maptlotlib FigureCanvas object, which defines a single set of axes as self.axes.
        self.canvas = Canvas(self, width=8, height=6, dpi=100)
        
        # Initialize a simple DataFrame
        self.x  = [1,2,3]
        self.y  = [1,2,3]
        self.title  = ''
        self.xlabel = ''
        self.ylabel = ''
        self.df = pd.DataFrame({'x':self.x,'y':self.y})

        # Plotting the DataFrame, passing in the matplotlib Canvas axes.
        self.Plot()

        # Toolbar
        toolbar = NavigationToolbar(self.canvas, self)

        # Text Editor
        self.text_edit = QTextEdit()
        # Text Editor
        self.plaintext_edit = QPlainTextEdit()

        # Button 1: Load
        self.button1 = QPushButton('Load')
        self.button1.setToolTip('Loads spectra') #adds description
        self.button1.setShortcut('Ctrl+L')
        self.button1.clicked.connect(lambda : self.load())
        # Button 2: Baseline 
        self.button2 = QPushButton('Baseline')
        self.button2.setToolTip('Applies baseline correction') 
        self.button2.setShortcut('Ctrl+B')
        self.button2.clicked.connect(lambda : self.baseline_als_optimized())
        # Button 3: Save txt 
        self.button3 = QPushButton('Save txt')
        self.button3.setToolTip('Saves the text as .txt')
        self.button3.setShortcut('Ctrl+S')
        self.button3.clicked.connect(lambda : self.save_txt())
        # Button 4: Smoothing 
        self.button4 = QPushButton('Smoothing')
        self.button4.setToolTip('Removes noise from spectrum')
        self.button4.setShortcut('Ctrl+Q')
        self.button4.clicked.connect(lambda : self.smoothing())
        # Button 5: Peak find 
        self.button5 = QPushButton('Peaks')
        self.button5.setToolTip('Automatic peak finding algorithm')
        self.button5.setShortcut('Ctrl+P')
        self.button5.clicked.connect(lambda: self.peak_find())
        # Button 6: Clear txt 
        self.button6 = QPushButton('clear txt')
        self.button6.setToolTip('Clears the text')
        self.button6.setShortcut('Ctrl+C')
        self.button6.clicked.connect(lambda : self.clear_txt())
        # Button 7: axes - Raman
        self.button7 = QPushButton('Raman')
        self.button7.setToolTip('Adds a label for Raman Spectroscopy')
        self.button7.setShortcut('Ctrl+R')
        self.button7.clicked.connect(lambda: self.raman_label())
        # Button 8: axes - IR (Absobance)
        self.button8 = QPushButton('IR (Abs)',self)
        self.button8.setToolTip('Adds a label for IR Spectroscopy in Absorbance mode')
        self.button8.setShortcut('Ctrl+A')
        self.button8.clicked.connect(lambda: self.ir_a_label())
        # Button 9: axes - IR (reflectance)
        self.button9 = QPushButton('IR (Ref)',self)
        self.button9.setToolTip('Adds a label for IR Spectroscopy in Reflectance mode')
        self.button9.setShortcut('Ctrl+I')
        self.button9.clicked.connect(lambda: self.ir_r_label())
        # Button 10: axes - UV-Vis
        self.button10 = QPushButton('UV-Vis',self)
        self.button10.setToolTip('Adds a label for UV-Vis Spectroscopy')
        self.button10.setShortcut('Ctrl+U')
        self.button10.clicked.connect(lambda: self.uv_label())
        # Button 11: Reverse y axis
        self.button11 = QPushButton('Reverse y',self)
        self.button11.setToolTip('Reverses the y axis')
        self.button11.setShortcut('Ctrl+Backspace')
        self.button11.clicked.connect(lambda: self.reverse_y())
        # Button 12: Undo 
        self.button12 = QPushButton('Undo',self)
        self.button12.setToolTip('Undoes all change to the loaded spectrum')
        self.button12.setShortcut('Ctrl+Z')
        self.button12.clicked.connect(lambda: self.undo_plot())
        # Button 13: Edit Form
        self.button13 = QPushButton('Edit',self)
        self.button13.setToolTip('Opens spectrum in a new window that can apply pinpoint peaks')
        self.button13.setShortcut('Ctrl+E')
        self.button13.clicked.connect(lambda: self.editform())
        # Button 14: Reverse x axis
        self.button14 = QPushButton('Reverse x',self)
        self.button14.setToolTip('Reverses the x axis')
        self.button14.setShortcut('Ctrl+Delete')
        self.button14.clicked.connect(lambda: self.reverse_x())
        #Button 15: Add_Plot
        self.button15 = QPushButton('Add Plot',self)
        self.button15.setToolTip('Adds another plot')
        self.button15.setShortcut('Ctrl+Q')
        self.button15.clicked.connect(lambda: self.Add_Plot())

        # Initialize tab screen
        self.mtab = QTabWidget()
        self.tab1 = QWidget()
        self.tab2 = QWidget()
        
        # Initialize tabs
        self.mtab.addTab(self.tab1,"Tab 1")
        self.mtab.addTab(self.tab2,"Tab 2")

        # Tab1
        self.tab1.layout = QVBoxLayout(self)
        self.tab1.layout.addWidget(self.canvas)
        self.tab1.layout.addWidget(toolbar)
        # Sublayout 1
        sublayout = QGridLayout()
        sublayout.addWidget(self.text_edit,0,0)
        sublayout.addWidget(self.button3,1,0)
        sublayout.addWidget(self.plaintext_edit,0,1)
        sublayout.addWidget(self.button6,1,1)
        # Sublayout 2
        sub2 = QVBoxLayout()
        sublayout.addLayout(sub2,0,2)
        sub2.addWidget(self.button13)
        sub2.addWidget(self.button2)
        sub2.addWidget(self.button4)
        sub2.addWidget(self.button5)
        # Sublayout 3
        sub3 = QVBoxLayout()
        sublayout.addLayout(sub3,0,3)
        sub3.addWidget(self.button7)
        sub3.addWidget(self.button8)
        sub3.addWidget(self.button9)
        sub3.addWidget(self.button10)
        # Sublayout 4
        sub4 = QVBoxLayout()
        sublayout.addLayout(sub4,0,4)
        sub4.addWidget(self.button11)
        sub4.addWidget(self.button14)
        sub4.addWidget(self.button12)
        sub4.addWidget(self.button15)

        # Button for "prominence" for Peaks Find
        self.button_p2 = QPushButton('Change')
        self.button_p2.setToolTip('Change prominence for Peaks Find')
        self.button_p2.clicked.connect(lambda: self.p_change())
        self.text_p2 = QLineEdit(self)
        self.text_p2.setPlaceholderText('prominence')
        
        # Sublayout 5
        sub5 = QVBoxLayout()
        sublayout.addLayout(sub5,0,5)
        sub5.addWidget(self.button1)
        sub5.addWidget(self.text_p2)
        sub5.addWidget(self.button_p2)
        sub5.addWidget(self.button14)
        # Sublayout 6
        sub6 = QVBoxLayout()
        sublayout.addLayout(sub6,0,6)

        # Adds All Layouts to Tab1
        self.tab1.layout.addLayout(sublayout)
        self.tab1.setLayout(self.tab1.layout)

        # Tab 2
        self.tab2.layout = QHBoxLayout()
        tab2_sub = QGridLayout()

        # Savitzky-Golay Labels
        lbl_1 = QLabel('Savitzky-Golay')
        lbl_2 = QLabel('win_l')
        lbl_3 = QLabel('pol_ord')
        lbl_4 = QLabel('der')
        lbl_5 = QLabel('δ')
        lbl_6 = QLabel('axis')

        # Savitzky-Golay Functions
        self.text_winl = QLineEdit(self)
        self.text_winl.setPlaceholderText('window length') 
        self.button_winl = QPushButton('OK')
        self.button_winl.clicked.connect(lambda: self.winl_change())
        self.text_pol = QLineEdit(self)
        self.text_pol.setPlaceholderText('polyorder')
        self.button_pol = QPushButton('OK')
        self.button_pol.clicked.connect(lambda: self.poly_change())
        self.text_der = QLineEdit(self)
        self.text_der.setPlaceholderText('derivative')
        self.button_der = QPushButton('OK')
        self.button_pol.clicked.connect(lambda: self.derivative_change())
        self.text_delta = QLineEdit(self)
        self.text_delta.setPlaceholderText('δ')
        self.button_delta = QPushButton('OK')
        self.button_pol.clicked.connect(lambda: self.delta_change())
        self.text_axis = QLineEdit(self)
        self.text_axis.setPlaceholderText('axis')
        self.button_axis = QPushButton('OK')
        self.button_axis.clicked.connect(lambda: self.axis_change())

        savgol_l = QGridLayout()
        tab2_sub.addLayout(savgol_l,*(0,0))

        # Savitzky-Golay Alignment 
        savgol_l.addWidget(lbl_1,0,1)        
        savgol_l.addWidget(lbl_2,1,0)
        savgol_l.addWidget(self.text_winl,1,1)
        savgol_l.addWidget(self.button_winl,1,2)
        savgol_l.addWidget(lbl_3,2,0)
        savgol_l.addWidget(self.text_pol,2,1)
        savgol_l.addWidget(self.button_pol,2,2)        
        savgol_l.addWidget(lbl_4,3,0)
        savgol_l.addWidget(self.text_der,3,1)
        savgol_l.addWidget(self.button_der,3,2)        
        savgol_l.addWidget(lbl_5,4,0)
        savgol_l.addWidget(self.text_delta,4,1)
        savgol_l.addWidget(self.button_delta,4,2)     
        savgol_l.addWidget(lbl_6,5,0)
        savgol_l.addWidget(self.text_axis,5,1)
        savgol_l.addWidget(self.button_axis,5,2)

        # Find Peaks Labels
        lbl_7 = QLabel('Find Peaks')
        lbl_8 = QLabel('height')
        lbl_9 = QLabel('threshold')
        lbl_10 = QLabel('distance')
        lbl_11 = QLabel('prominence')
        lbl_12 = QLabel('width')

        # Find Peaks Functions
        self.button_h = QPushButton('OK')
        self.button_h.clicked.connect(lambda: self.h_change())
        self.text_h = QLineEdit(self)
        self.text_h.setPlaceholderText('height')       
        self.button_thr = QPushButton('OK')
        self.button_thr.clicked.connect(lambda: self.thr_change())
        self.text_thr = QLineEdit(self)
        self.text_thr.setPlaceholderText('threshold')
        self.button_d = QPushButton('OK')
        self.button_d.clicked.connect(lambda: self.d_change())
        self.text_d = QLineEdit(self) 
        self.text_d.setPlaceholderText('distance')       
        self.button_p = QPushButton('OK')
        self.button_p.clicked.connect(lambda: self.p_change())
        self.text_p = QLineEdit(self)
        self.text_p.setPlaceholderText('prominence')
        self.button_w = QPushButton('OK')
        self.button_w.clicked.connect(lambda: self.w_change())
        self.text_w = QLineEdit(self) 
        self.text_w.setPlaceholderText('width')
        
        fp_l = QGridLayout()
        tab2_sub.addLayout(fp_l,0,1)

        #Find Peaks Alignment
        fp_l.addWidget(lbl_7,0,0)
        fp_l.addWidget(lbl_8,1,0)
        fp_l.addWidget(lbl_9,2,0)
        fp_l.addWidget(lbl_10,3,0)
        fp_l.addWidget(lbl_11,4,0)
        fp_l.addWidget(lbl_12,5,0)
        
        fp_l.addWidget(self.text_h,1,1)
        fp_l.addWidget(self.button_h,1,2)
        fp_l.addWidget(self.text_thr,2,1)
        fp_l.addWidget(self.button_thr,2,2)
        fp_l.addWidget(self.text_d,3,1)
        fp_l.addWidget(self.button_d,3,2)
        fp_l.addWidget(self.text_p,4,1)
        fp_l.addWidget(self.button_p,4,2)
        fp_l.addWidget(self.text_w,5,1)
        fp_l.addWidget(self.button_w,5,2)

        self.tab2.layout.addLayout(tab2_sub)
        self.tab2.setLayout(self.tab2.layout)

        #Add tabs to widget
        self.layout.addWidget(self.mtab)
        self.setLayout(self.layout)

        ## Variables        
        # Plot
        self.p   = []
        self.p1  = []
        self.p2  = []
        self.txt = []
        # Find peaks
        self.h    = None
        self.thr  = None
        self.d    = 1
        self.prom = 0.001
        self.w    = None
        # Savgol 
        self.win_length = 51
        self.poly       = 3
        self.der        = 0
        self.delta      = 1.0
        self.axis       = -1
        # Reverse
        self.rev_y = True
        self.rev_x = True

        def onclick(event):
            global peaks
            if event.button == 1 and event.dblclick: #Add marks for peaks with left double click
                self.p1.append(event.xdata)
                self.p2.append(event.ydata)
                peaks = str('{:.2f}').format(event.xdata)
                self.txt.append(peaks)
                self.p.append(event.xdata)
                self.canvas.axes.plot(self.p1,self.p2,'ro',ms=4)
                self.canvas.draw_idle()             
                self.text_edit.setPlainText(peaks)
                self.plaintext_edit.appendPlainText(peaks)
            if event.button == 3: #Delete marks for peaks with right click
                if self.p != []:
                    self.p.pop()
                    self.p1.pop()
                    self.p2.pop()
                    self.txt.pop()
                    self.text_edit.setPlainText('peak deleted')
                    self.plaintext_edit.undo()
                    self.plaintext_edit.setPlainText('\n'.join(self.txt))
                    try:
                        self.Plot()
                        self.canvas.axes.plot(self.p1,self.p2,'ro',ms=4)
                        self.canvas.draw_idle()
                    except:
                        print('right click error')
                else:
                    self.text_edit.setPlainText('empty')                   
        self.canvas.mpl_connect('button_press_event', onclick)

    def add_cursor(self):
        self.cursor = Cursor(self.canvas.axes,horizOn=True,vertOn=True,color='red',linewidth=0.8)
    def clear_txt(self):
        self.text_edit.clear()
        self.plaintext_edit.clear()
        self.p = []
    def save_txt(self):
        try:
            filename = QFileDialog.getSaveFileName(self,'Save File',DIR,'txt (*.txt)')
            with open(filename[0],'w') as f:
                txt = self.plaintext_edit.toPlainText()
                f.write(txt)
        except FileNotFoundError:
            pass
    def reverse_y(self):
        if self.rev_y == False:
            self.canvas.axes.invert_yaxis()
            self.rev_y = True
        elif self.rev_y == True:
            self.canvas.axes.invert_yaxis()
            self.rev_y = False
        self.canvas.draw_idle()
    def reverse_x(self):
        if self.rev_x == False:
            self.canvas.axes.invert_xaxis()
            self.rev_x = True
        elif self.rev_x == True:
            self.canvas.axes.invert_xaxis()
            self.rev_x = False
        self.canvas.draw_idle()       
    def undo_plot(self):
        try:
            self.p1=[]
            self.p2=[]
            self.p =[]
            self.csv_to_dataframe()
            self.Plot()
            self.canvas.axes.set_xlabel('')
            self.canvas.axes.set_ylabel('')
            self.clear_txt()
        except AttributeError:
            pass
    def Plot(self):
            #Clearing the previous graph
            self.canvas.axes.cla()
            #Plotting the new graph,setting up labels & restarting the cursor
            self.df.plot(ax=self.canvas.axes,x='x',y='y',title=self.title,legend=False, linewidth=0.5)
            #Adding Labels & Cursor
            self.canvas.axes.set_xlabel(self.xlabel)
            self.canvas.axes.set_ylabel(self.ylabel)
            self.canvas.draw_idle()
            self.add_cursor()
    def csv_to_dataframe(self):
        # Changing the Directory and making a title w/ the file
        self.filename = self.input_file.split('/')[-1]
        self.title = self.filename.split('.csv')[0]
        self.dir = '/'.join(self.input_file.split('/')[:-1])            
        os.chdir(self.dir)
        # Csv to dataframe
        df = open(self.input_file,'r')
        self.df = pd.read_csv(df,sep='\t',dtype='float')
        self.x = self.df['x']
        self.y = self.df['y']
    def load(self):
        # Loading the file
        try:
            self.input_file = QFileDialog.getOpenFileName(self,'Choose files',DIR,"Data file (*.csv)")[0]
            self.csv_to_dataframe()
            self.Plot()
        except OSError:
            pass
    def Add_Plot(self):
        try:
            input_file = QFileDialog.getOpenFileName(self,'Choose files',DIR,"Data file (*.csv)")[0]
            direc = '/'.join(input_file.split('/')[:-1])            
            os.chdir(direc)
            new_data = open(input_file,'r')
            new_df = pd.read_csv(new_data,sep='\t',dtype='float')
            new_df.plot(ax=self.canvas.axes,x= 'x',y = 'y',title=self.title,legend=False,grid=True, linewidth=0.5)
            self.canvas.draw_idle()
        except OSError:
            pass
    def baseline_als_optimized(self):
        # reference: https://stackoverflow.com/questions/29156532/python-baseline-correction-library
        try:
            y = self.y
            lam = 1e4
            p = 0.001
            niter = 10
            L = len(y)
            D = sparse.diags([1,-2,1],[0,-1,-2], shape=(L,L-2))
            D = lam * D.dot(D.transpose()) # Precompute this term since it does not depend on `w`
            w = np.ones(L)
            W = sparse.spdiags(w, 0, L, L)
            for _ in range(niter):
                W.setdiag(w) # Do not create a new matrix, just update diagonal values
                Z = W + D
                z = spsolve(Z, w*y)
                w = p * (y > z) + (1-p) * (y < z)
            self.y = abs(z-y)
            self.df = pd.DataFrame({'x':self.x,'y':self.y})
            self.Plot()
        except TypeError:
            pass
    def editform(self):
        try:
            plt.plot(self.x,self.y, linewidth=0.5)
            plt.grid(True)
            plt.title(self.title)
            plt.xlabel(self.xlabel)
            plt.ylabel(self.ylabel)
            c = mplcursors.cursor(multiple=True)
            @c.connect('add')
            def _(selection):
                xi, _ = selection.target
                selection.annotation.set_bbox(None)
                selection.annotation.arrow_patch.set(arrowstyle='-',linewidth=.4)
                selection.annotation.set(text=int(xi),color=selection.artist.get_color(),size=8)
            if self.rev_y == False:
                plt.gca().invert_yaxis()
            if self.rev_x == False:
                plt.gca().invert_xaxis()
            plt.draw()
            plt.show()
            
        except TypeError:
            print('Retry')
            pass
    def smoothing(self):
        try:
            y = savgol_filter(self.y, self.win_length,self.poly)
            self.y = pd.Series(y)
            self.df = pd.DataFrame({'x':self.x,'y':self.y})
            self.Plot()
        except TypeError:
            pass
    def peak_find(self):
        try:
            peaks, _ = signal.find_peaks(self.y, height = self.h, threshold = self.thr , distance = self.d,prominence= self.prom,width=self.w)
            self.p = self.x[peaks].dropna().to_list()
            self.Plot()
            self.p1 = self.x[peaks].to_list()
            self.p2 = self.y[peaks].to_list()
            self.canvas.axes.plot(self.p1,self.p2,'ro',ms=4)
            self.txt = [str(int(i)) for i in self.p]
            self.plaintext_edit.appendPlainText('\n'.join(self.txt))
            self.text_edit.setPlainText(','.join(self.txt))
        except TypeError:
            print('Error')
    def raman_label(self):
        self.xlabel, self.ylabel = 'Raman Shift cm⁻¹', 'Intensity →'
        self.canvas.axes.set_xlabel(self.xlabel)
        self.canvas.axes.set_ylabel(self.ylabel)
        self.canvas.draw_idle()
    def ir_r_label(self):
        self.xlabel, self.ylabel = 'Wavenumber cm⁻¹', 'Reflectance Coefficient'
        self.canvas.axes.set_xlabel(self.xlabel)
        self.canvas.axes.set_ylabel(self.ylabel)
        self.canvas.draw_idle()
    def ir_a_label(self):
        self.xlabel, self.ylabel = 'Wavenumber cm⁻¹', 'Absorbance'
        self.canvas.axes.set_xlabel(self.xlabel)
        self.canvas.axes.set_ylabel(self.ylabel)
        self.canvas.draw_idle()
    def uv_label(self):
        self.xlabel, self.ylabel = 'Wavelength (nm)', 'Absorbance'
        self.canvas.axes.set_xlabel(self.xlabel)
        self.canvas.axes.set_ylabel(self.ylabel)
        self.canvas.draw_idle()
    def h_change(self):
        try:
            self.h = float(self.text_h.text())
            print(self.h)
        except ValueError:
            self.h = None
            print(self.h)
    def thr_change(self):
        try:
            self.thr = float(self.text_thr.text())
            print(self.thr)
        except ValueError:
            self.thr = None
            print(self.thr)
    def p_change(self):
        try:
            self.prom = float(self.text_p2.text())
            print(self.prom)
        except ValueError:
            self.prom = None
            print(self.prom)
    def d_change(self):
        try:
            self.d = float(self.text_d.text())
            print(self.d)
        except ValueError:
            self.d = None
            print(self.d)
    def w_change(self):
        try:
            self.w = float(self.text_w.text())
            print(self.w)
        except ValueError:
            self.w = None
            print(self.w)
    def winl_change(self):
        try:
            self.win_length = int(self.text_winl.text())
        except ValueError:
            self.win_length = 51
    def poly_change(self):
        try:
            self.poly = int(self.text_pol.text())
        except ValueError:
            self.poly = 3       
    def derivative_change(self):
        try:
            self.der = int(self.text_der.text())
        except ValueError:
            self.delta = 0
    def delta_change(self):
        try:
            self.delta = float(self.text_delta.text())
        except ValueError:
            self.delta = 1.0
    def axis_change(self):
        try:
            self.axis = int(self.text_axis.text())
        except ValueError:
            self.axis = -1

if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = App()
    w.show()
    sys.exit(app.exec_())
