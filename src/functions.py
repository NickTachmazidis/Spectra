# Core
import os
# GUI
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import QFileDialog
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as Canvas
# Data/visualisation
import pandas as pd
import numpy as np
from matplotlib.widgets import Cursor
from matplotlib.lines import Line2D
import matplotlib.pyplot as plt
import mplcursors
from scipy import sparse
from scipy.signal import savgol_filter, find_peaks
# src
from .spectra import Spectrum
from .exception import CustomException


class Funcs():

# canvas
    def add_cursor(self,
        ax: Canvas,
        hl: bool = True,
        vl: bool = True,
        color: str = 'red',
        lw: float = 0.8) -> Cursor:
        """Adds a Cursor object to the Axes."""
        self.cursor = Cursor(
                ax,
                horizOn=hl,
                vertOn=vl,
                color=color,
                linewidth=lw,
                label='cursor')
        return self.cursor

    def canvas_clear(self) -> None:
        """Clears the Canvas object."""
        self.canvas.axes.cla()

    def canvas_update(self) -> None:
        """Updates the Canvas object."""
        try:
            self.canvas.draw_idle()
            self.canvas.axes.set_xlabel(self.xlabel)
            self.canvas.axes.set_ylabel(self.ylabel)
            self.canvas.axes.set_title(self.title)
        except Exception as e:
            raise CustomException(e)

    def get_file(self) -> str:
        """Opens a popup dialog to load the file."""
        try:
            input_file = QFileDialog.getOpenFileName(
                                None,
                                'Choose files',
                                self.settings.general.path,
                                "Data file (*.csv)")[0]
            return input_file
        except Exception as e:
            raise CustomException(e)
            
    def csv_to_dataframe(self, input_file: str) -> (pd.DataFrame, str):
        """Converts the CSV file to a pd.DataFrame object."""
        try:
            label = input_file.split('/')[-1].replace('.csv','')
            df = pd.read_csv(input_file, 
                            sep=self.settings.general.sep,
                            dtype='float')
            return df, label
        except Exception as e:
            raise CustomException(e)

    def plot(self, df, label, state='Add') :
        """Plots the pd.DataFrame object to the Canvas."""
        try:
            ax = df.plot(
                ax=self.canvas.axes,
                x=0,
                y=1,
                lw=self.settings.general.lw,
                legend=self.legend,
                label=label)
            
            #Convert DataFrame to Spectrum object
            sp, sp_id = self.add_spectrum(ax.lines[-1])
            self.curves.update({sp_id: sp})
            if self.legend:
                self.add_legend()
            if state == 'Load':
                self.curves[list(self.curves)[-1]].loaded = True
            else:
                pass
            self.canvas_update()
            self.update_spectrum_table()
            self.add_cursor(self.canvas.axes)
            return ax
        except Exception as e:
            raise CustomException(e)

    def load(self) -> None:
        """Loads the File."""
        try:
            if self.curves:
                for i in self.curves.values():
                    if i.loaded:
                        self.load_list.append(i)
                last = self.curves.pop(list(self.curves)[-1])
                self.curves = dict()
            
            input_file = self.get_file()
            self.title = input_file.split('/')[-1].replace('.csv','')
            df, label = self.csv_to_dataframe(input_file)
            self.canvas_clear()
            self.plot(df, label,'Load')
            new = self.curves[list(self.curves)[-1]]
            new.loaded = True
            self.undo_stack.append(('Load', last, new))
        except Exception as e:
            raise CustomException(e)

    def add_spectrum(self, curve: Line2D) -> (Spectrum, int):
        """Creates a Spectrum object."""
        try:
            sp = Spectrum(curve)
            sp_id = sp.id
            return sp, sp_id
        except Exception as e:
            raise CustomException(e)

    def add_plot(self) -> None:
        """Adds another line to the Canvas"""
        try:
            prev = self.added[-1]
            input_file = self.get_file()
            df, label = self.csv_to_dataframe(input_file)
            self.plot(df,label)
            new = self.curves[list(self.curves)[-1]]
            self.undo_stack.append(('Add Plot', prev, new))
            self.added.append(new)
            self.canvas_update()
        except Exception as e:
            raise CustomException(e)

    def df_p_plot(self) -> None:
        """Adds peaks to the Canvas"""
        try:
            self.df_p.plot(
                    ax=self.canvas.axes, 
                    x=0,
                    y=1,
                    marker='o',
                    c='r',
                    s=10,
                    kind='scatter',
                    label='peak_user',
                    legend=False)

            self.update_peaks_table()
            self.canvas_update()
        except Exception as e:
            raise CustomException(e)
    
    def plot_demo(self) -> None:
        df = pd.DataFrame({'x':self.x,'y':self.y}, dtype='float')
        self.plot(df, self.label, 'Load')

# data processing
    def smoothing(self):
        """Smooths the lines."""
        try:
            for i in self.curves.values():
                if i.tristate == 1:
                    prev = np.copy(i.y_data)
                    
                    i.y_smooth = savgol_filter(
                                    x=i.y(),
                                    window_length=self.settings.smooth.window_length,
                                    polyorder=self.settings.smooth.polyorder,
                                    deriv=self.settings.smooth.deriv,
                                    delta=self.settings.smooth.delta,
                                    axis=self.settings.smooth.axis)

                    i.y_data = i.y_smooth
                    i.line().set_ydata(i.y_smooth)
                    self.undo_stack.append(('Smooth', prev, i.y_smooth, i))
            self.canvas_update()
        except Exception as e:
            raise CustomException(e)

    def peaks_find(self):
        """Finds peaks in the lines."""
        try:
            for i in self.curves.values():
                if i.tristate == 1:
                    if i.peaks:
                        self.canvas.axes.lines.remove(i.peaks_object)
                        i.peaks_data = []
                        i.peaks_object = False

                    peaks, _ = find_peaks(
                                x=i.y(),
                                height=self.settings.peaks.height,
                                threshold=self.settings.peaks.threshold,
                                distance=self.settings.peaks.distance,
                                prominence=self.settings.peaks.prominence,
                                width=self.settings.peaks.width)

                    if peaks.size > 0:
                        i.peaks = True
                        pks = self.canvas.axes.plot(
                            i.x()[peaks],
                            i.y()[peaks],
                            'ro',
                            ms= 2,
                            label= f"peak_{i.label()}")[-1]
                        i.peaks_object = pks
                        self.undo_stack.append(('Peaks', pks, i))
            
            self.canvas_update()
            self.update_spectrum_table()
            self.update_peaks_table()
        
        except Exception as e:
            raise CustomException(e)

    def prom_change(self):
        """Changes the prominence parameter for peaks_find function."""
        try:
            prev = self.prom
            self.prom = float(self.lineEdit_prominence.text())
        except ValueError:
            self.prom = prev

    def baseline(self) -> None:
        """Removes the baseline from the lines.
        Based on "Asymmetric Least Squares Smoothing" paper
        by P. Eilers and H. Boelens in 2005.
        """
        try:
            for i in self.curves.values():
                if i.tristate == 1:
                    prev = np.copy(i.y_data)
                    y_ = i.y_data
                    lam = self.settings.baseline.lam
                    p = self.settings.baseline.p
                    niter = self.settings.baseline.niter
                    L = len(y_)
                    D = sparse.diags([1,-2,1],[0,-1,-2], shape=(L,L-2))
                    # Precompute this term since it does not depend on `w`
                    D = lam * D.dot(D.transpose()) 
                    w = np.ones(L)
                    W = sparse.spdiags(w, 0, L, L)
                    for _ in range(niter):
                        # Do not create a new matrix, just update diagonal values
                        W.setdiag(w) 
                        Z = W + D
                        z = sparse.linalg.spsolve(Z, w*i.y_data)
                        w = p * (i.y_data > z) + (1-p) * (i.y_data < z)
                    i.y_baseline = abs(z-y_)
                    i.y_data = i.y_baseline
                    i.line().set_ydata(i.y_baseline)
                    self.undo_stack.append(('Baseline', prev, i.y_baseline, i))

            self.canvas_update()
        except Exception as e:
            raise CustomException(e)

    def edit_form(self) -> None:
        try:
            fig, ax = plt.subplots(nrows=1, ncols=1)
            for i in self.curves.values():
                if i.tristate == 1:
                    ax.plot(i.x(), i.y(), lw=self.settings.general.lw, label=i.label())

            if self.legend:
                handles,_ = ax.get_legend_handles_labels()
                handles = [i for i in handles if not (
                    i.get_label() =='cursor' or i.get_label().startswith('peak_'))]
                ax.legend(handles=handles)

            if self.x_rev:
                ax.invert_xaxis()
            
            if self.y_rev:
                ax.invert_yaxis()

            plt.title(self.title)
            plt.xlabel(self.xlabel)
            plt.ylabel(self.ylabel)

            c = mplcursors.cursor(multiple=True)
            @c.connect('add')
            def _(selection):
                xi, _ = selection.target
                selection.annotation.set_bbox(None)
                selection.annotation.arrow_patch.set(arrowstyle='-',linewidth=.4)
                selection.annotation.set(text=int(xi),color=selection.artist.get_color(),size=12)
            
            plt.show()
        except Exception as e:
            raise CustomException(e)

    def norm_min_max(self) -> None:
        try:
            for i in self.curves.values():
                if i.tristate == 1:
                    prev = np.copy(i.y_data)
                    i.y_normalized = (i.y() - i.y().min()) /(i.y().max() - i.y().min())
                    i.y_data = i.y_normalized
                    i.line().set_ydata(i.y_normalized)
                    self.undo_stack.append(
                        ('Normalize Min-Max', prev, i.y_normalized, i))
            self.canvas_update()
        except Exception as e:
            raise CustomException(e)

    def norm_z(self) -> None:
        try:
            for i in self.curves.values():
                if i.tristate == 1:
                    prev = np.copy(i.y_data)
                    i.y_normalized_z = (i.y() - i.y().mean()) / i.y().std()
                    i.y_data = i.y_normalized_z
                    i.line().set_ydata(i.y_normalized_z)
                    self.undo_stack.append(('Normalize Z', prev, i.y_normalized_z, i))
            self.canvas_update()
        except Exception as e:
            raise CustomException(e)

    def reverse_y(self) -> None:
        try:
            self.canvas.axes.invert_yaxis()
            if not self.y_rev:
                self.y_rev = True
            else:
                self.y_rev = False
            self.undo_stack.append(('Reverse Y', None))
            self.canvas_update()
        except Exception as e:
            raise CustomException(e)

    def reverse_x(self) -> None:
        try:
            self.canvas.axes.invert_xaxis()
            if not self.x_rev:
                self.x_rev = True
            else:
                self.x_rev = False
            self.undo_stack.append(('Reverse X', None, None))
            self.canvas_update()
        except Exception as e:
            raise CustomException(e)
    
# Undo redo
    def undo(self) -> None:
        if self.undo_stack:
            actions = self.undo_stack.pop()
            self.redo_stack.append(actions)

            if actions[0] == 'Load':
                if not actions[1] == '':
                    self.canvas.axes.lines.remove(actions[2].line())
                    self.canvas.axes.lines.append(actions[1].line())
                    self.load_list.append(actions[2])
                    self.curves = dict()
                    self.curves.update({actions[1].id: actions[1]})

            elif actions[0] == 'Add Plot':
                self.canvas.axes.lines.remove(actions[2].line())
                self.curves.pop(actions[2].id)

            elif actions[0] == 'Smooth':
                actions[3].line().set_ydata(actions[1])
                actions[3].y_data = actions[1]

            elif actions[0] == 'Baseline':
                actions[3].line().set_ydata(actions[1])
                actions[3].y_data = actions[1]

            elif actions[0] == 'Peaks':
                self.canvas.axes.lines.remove(actions[2].peaks_object)
                actions[2].delete_peaks()
                self.update_peaks_table()

            elif actions[0] == 'Normalize Min-Max':
                actions[3].line().set_ydata(actions[1])
                actions[3].y_data = actions[1]

            elif actions[0] == 'Normalize Z':
                actions[3].line().set_ydata(actions[1])
                actions[3].y_data = actions[1]

            elif actions[0] == 'Reverse X':
                self.canvas.axes.invert_xaxis()

            elif actions[0] == 'Reverse Y':
                self.canvas.axes.invert_yaxis()

            elif actions[0] == 'Label':
                self.xlabel = actions[1][0]
                self.ylabel = actions[1][1]

            elif actions[0] == 'New_my_peak':
                self.df_p = self.df_p.drop(
                    self.df_p.tail(1).index).reset_index(drop=True)
                self.canvas.axes.collections[-1].remove()

            elif actions[0] == 'Delete_my_peak':
                self.df_p = self.df_p.append(actions[1]).reset_index(drop=True)
                self.df_p_plot()
            
            elif actions[0] == 'Clear Table':
                self.canvas.axes.collections = actions[1]
                for k,v in actions[2].items():
                    k.add_peaks(v)
                    self.canvas.axes.lines.append(v)

            self.canvas_update()
            self.update_spectrum_table()
            self.update_peaks_table()

    def redo(self) -> None:
        if self.redo_stack:
            actions = self.redo_stack.pop()
            self.undo_stack.append(actions)

            if actions[0] == 'Load':
                if not actions[1] == '':
                    self.canvas.axes.lines.remove(actions[1].line())
                    self.canvas.axes.lines.append(actions[2].line())
                    new = self.load_list.pop()
                    self.curves = dict()
                    self.curves.update({new.id: new})

            elif actions[0] == 'Add Plot':
                self.canvas.axes.lines.append(actions[2].line())
                self.curves.update({actions[2].id:actions[2]})
            
            elif actions[0] == 'Smooth':
                actions[3].line().set_ydata(actions[2])
                actions[3].y_data = actions[2]

            elif actions[0] == 'Baseline':
                actions[3].line().set_ydata(actions[2])
                actions[3].y_data = actions[2]

            elif actions[0] == 'Peaks':
                self.canvas.axes.lines.append(actions[1])
                actions[2].add_peaks(actions[1])
                self.update_peaks_table()

            elif actions[0] == 'Normalize Min-Max':
                actions[3].line().set_ydata(actions[2])
                actions[3].y_data = actions[2]

            elif actions[0] == 'Normalize Z':
                actions[3].line().set_ydata(actions[2])
                actions[3].y_data = actions[2]

            elif actions[0] == 'Reverse X':
                self.canvas.axes.invert_xaxis()

            elif actions[0] == 'Reverse Y':
                self.canvas.axes.invert_yaxis()

            elif actions[0] == 'Label':
                self.xlabel = actions[2][0]
                self.ylabel = actions[2][1]

            elif actions[0] == 'New_my_peak':
                self.df_p = self.df_p.append(actions[1]).reset_index(drop=True)
                self.df_p_plot()

            elif actions[0] == 'Delete_my_peak':
                self.df_p = self.df_p.drop(
                    self.df_p.tail(1).index).reset_index(drop=True)
                self.canvas.axes.collections[-1].remove()
                self.update_peaks_table()

            self.canvas_update()
            self.update_spectrum_table()

# Spinbox - Checkbox

    def chkbox_clicked(self,row,col) -> None:

        if self.table.item(row,col).checkState() == QtCore.Qt.Unchecked:
            for i in self.curves.values():
                if i.label() == self.table.item(row,col).text():
                    i.invisible()
                if i.peaks:
                    if i.peaks_object.get_label() == self.table.item(row,col).text():
                        i.peaks_object.set_visible(False)

        if self.table.item(row,col).checkState() == QtCore.Qt.Checked:
            for i in self.curves.values():
                if i.label() == self.table.item(row,col).text():
                    i.visible()
                if i.peaks:
                    if i.peaks_object.get_label() == self.table.item(row,col).text():
                        i.peaks_object.set_visible(True)

        if self.table.item(row,col).checkState() == 1:
            for i in self.curves.values():
                if i.label() == self.table.item(row,col).text():
                    i.disabled()
                    
        self.canvas_update()

    def spinbox_value_changed(self, axis) -> None:
            value_y = self.doubleSpinBox_y_axis.value()
            value_x = self.doubleSpinBox_x_axis.value()
            for i in self.curves.values():
                if i.tristate == 1:
                    if axis == 'y':
                        i.y_data += value_y
                        i.line().set_ydata(i.y_data)
                    elif axis == 'x':
                        i.x_data += value_x
                        i.line().set_xdata(i.x_data)
            self.canvas_update()
# Legend
    def add_legend(self) -> None:
        if self.legend_checkBox.isChecked():
            self.legend = True
            handles,_ = self.canvas.axes.get_legend_handles_labels()
            handles = [i for i in handles if not (
                i.get_label() == 'cursor' or i.get_label().startswith('peak_'))]
            self.canvas.axes.legend(handles=handles)
        else:
            self.legend = False
            self.canvas.axes.legend().set_visible(False)
        
        self.canvas_update()

# Tables
    def clear_peaks_table(self) -> None:
        try:
            self.table_peaks.setRowCount(0)
            self.table_peaks.setColumnCount(1)
            
            if self.canvas.axes.collections:
                prev_coll = self.canvas.axes.collections
                for collection in self.canvas.axes.collections:
                    collection.remove()
            else:
                prev_coll = []
            # self.canvas.axes.collections = []
            
                print(self.canvas.axes.collections)
            # self.canvas.axes.collections.remove()
            self.df_p = pd.DataFrame(columns=['p_x','p_y'])

            prev_obj = dict()
            for i in self.curves.values():
                if i.peaks:
                    prev_obj.update({i: i.peaks_object})
                    for line in self.canvas.axes.lines:
                        if line == i.peaks_object:
                            line.remove()
                    # self.canvas.axes.lines.remove(i.peaks_object)
                    i.delete_peaks()
            
            self.undo_stack.append(('Clear Table', prev_coll, prev_obj))
            self.canvas_update()
            self.update_spectrum_table()
        except Exception as e:
            raise CustomException(e)

    def update_spectrum_table(self) -> None:
        try:
            self.table.setRowCount(0)
            self.table.insertRow(0)
            self.table.setRowCount(len(self.curves))

            for i,j in enumerate(self.curves.values()):
                # Update Spectrum column
                if not j.label().startswith('peak_'):
                    chkBoxItem = QtWidgets.QTableWidgetItem(j.label())
                    chkBoxItem.setFlags(
                        QtCore.Qt.ItemIsUserCheckable | 
                        QtCore.Qt.ItemIsUserTristate | 
                        QtCore.Qt.ItemIsEnabled)
                    chkBoxItem.setCheckState(QtCore.Qt.Checked)
                    self.table.setItem(i, 0, chkBoxItem)
                    # Update Peaks column
                    if j.peaks:
                        chkBoxItem = QtWidgets.QTableWidgetItem(f"peak_{j.label()}")
                        chkBoxItem.setFlags(
                            QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEnabled)
                        chkBoxItem.setCheckState(QtCore.Qt.Checked)
                        self.table.setItem(i, 1, chkBoxItem)
        except Exception as e:
            raise CustomException(e)

    def update_peaks_table(self) -> None:
        try:
            self.table_peaks.setRowCount(0)     # clear rows
            self.table_peaks.setColumnCount(1)  # clear columns
            if not self.df_p.empty:
                my_peaks  = [str(int(i)) for i in self.df_p['p_x'].tolist()]
            else:
                my_peaks = []
            
            sp_peaks  = []
            sp_labels = []
            for i in self.curves.values():
                if i.peaks:
                    sp_peaks.append(i.peaks_object.get_xdata())
                    sp_labels.append(i.label())

            # Update Spectrum Peaks
            if sp_peaks:
                # setting row count
                m = max([i.size for i in sp_peaks]) 
                self.table_peaks.setRowCount(m)
                # setting column count
                self.table_peaks.setColumnCount(len(sp_peaks)+1)
                # Adding the header labels
                self.table_peaks.setHorizontalHeaderLabels(['My_peaks'] + sp_labels)
                
                for col, xdata in enumerate(sp_peaks, start=1):
                    pks = [str(int(i)) for i in np.sort(xdata)]
                    for num, v in enumerate(pks):
                        self.table_peaks.setItem(num,
                                                 col,
                                                 QtWidgets.QTableWidgetItem(v))
            # Update My_peaks
            if my_peaks:
                if not sp_peaks:          
                    self.table_peaks.insertRow(0)
                    self.table_peaks.setHorizontalHeaderLabels(['My_peaks'])
                    self.table_peaks.setRowCount(len(self.df_p))
                for i in range(len(my_peaks)):
                    self.table_peaks.setItem(i,
                                             0,
                                             QtWidgets.QTableWidgetItem(my_peaks[i]))
        except Exception as e:
            raise CustomException(e)

    def save_table(self) -> None:
        try:
            # Setting Column Headers
            col_headers = []
            for i in range(self.table_peaks.model().columnCount()):
                col_headers.append(self.table_peaks.horizontalHeaderItem(i).text())
            
            # Initialize a DataFrame with columns            
            df = pd.DataFrame(columns=col_headers)

            # Add Peak Data to the DataFrame
            for row in range(self.table_peaks.rowCount()):
                for col in range(self.table_peaks.columnCount()):
                    item = self.table_peaks.item(row, col)
                    if item is not None and item.text() != '':
                        df.at[row, col_headers[col]] = item.text()

            # Save into a CSV file
            f = QtWidgets.QFileDialog.getSaveFileName(
                                None,
                                'Save File',
                                self.dir,
                                'Comma Separated Values (*.csv)')[0]
            if self.sep is None:
                df.to_csv(f, sep=',', index=False)
            else:
                df.to_csv(f, self.sep, index=False)
        except Exception as e:
            raise CustomException(e)
        
# Labels
    def add_label(self) -> None:
        try:
            prev = self.labels[-1]
            new = self.dropbox_lbl.currentText()
            
            self.xlabel, self.ylabel = self.label_options(new)
            self.undo_stack.append(('Label', 
                                    self.label_options(prev), 
                                    (self.xlabel, self.ylabel)))
            self.labels.append(new)
            self.canvas_update()
        except Exception as e:
            raise CustomException(e)

    def label_options(self,label: str) -> (str,str):
        if label == 'None':
            x, y = '', ''
        elif label == 'Raman':
            x, y = 'Raman Shift (cm⁻¹)', 'Intensity →'
        elif label == 'IR (Ref)':
            x, y = 'Wavenumber (cm⁻¹)', 'Reflectance Coefficient'
        elif label == 'IR (Abs)':
            x, y = 'Wavenumber (cm⁻¹)', 'Absorbance'
        elif label == 'IR (Trans)':
            x, y = 'Wavenumber (cm⁻¹)', 'Transmittance (%)'
        elif label == 'UV-Vis':
            x, y = 'Wavelength (nm)', 'Absorbance'
        elif label == 'Reflectance':
            x, y = 'Wavelength (nm)', 'Reflectance (%)'
        elif label == 'XRF':
            x, y = 'Energy (keV)', 'Counts'
        elif label == 'XRD':
            x, y = '2θ (degrees)', 'Intensity'
        return x,y

# Settings Window
    def open_settings(self) -> None:
        try:
            self.settings_ui.lineEdit_title.setText(self.title)

            x_bounds = self.canvas.axes.get_xlim()
            self.settings_ui.lineEdit_xaxis_left.setText(str(x_bounds[0]))
            self.settings_ui.lineEdit_xaxis_right.setText(str(x_bounds[1]))
            self.settings_ui.lineEdit_xaxis_label.setText(self.xlabel)

            y_bounds = self.canvas.axes.get_ylim()
            self.settings_ui.lineEdit_yaxis_bottom.setText(str(y_bounds[0]))
            self.settings_ui.lineEdit_yaxis_top.setText(str(y_bounds[1]))
            self.settings_ui.lineEdit_yaxis_label.setText(self.ylabel)
            
            self.settings_ui.update_dropdown(self.curves)
            self.settings_ui.show()
        
        except Exception as e:
            raise CustomException(e)

# Save spectrum
    def save_as(self) -> None:
        try:
            dfs = []
            for i in self.curves.values():
                if i.tristate == 1:
                    title = i.label()
                    df = pd.DataFrame({'x': i.x(), 'y': i.y()})
                    if i.peaks:
                        df['peaks_x'] = pd.Series(i.peaks_object.get_xdata())
                        df['peaks_y'] = pd.Series(i.peaks_object.get_ydata())
                dfs.append((title,df))

            file = str(QtWidgets.QFileDialog.getExistingDirectory(
                self, "Select Directory"))
            
            sep = self.settings.general.sep
            
            if sep is None:
                sep = ','

            for i in dfs:
                path = self.check_path(file, i[0])
                i[1].to_csv(path_or_buf=path,
                            sep=str(sep),
                            index=False)
        except Exception as e:
            raise CustomException(e)

    def check_path(self,file: str, title: str) -> str:
        path = os.path.join(file,f"{title}.csv")
        counter = 1
        while os.path.exists(path):
            path = os.path.join(file, f"{title}_({str(counter)}).csv")
            counter += 1
        return path