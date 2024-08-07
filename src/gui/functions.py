"""Functions for the GUI app."""

from collections import namedtuple
from typing import Callable

import matplotlib.pyplot as plt
import mplcursors
import numpy as np
import pandas as pd
from matplotlib.axes import Axes
from matplotlib.lines import Line2D
from matplotlib.widgets import Cursor

from PyQt5 import QtCore
from PyQt5 import QtWidgets

from ..classes.peaks import Peaks
from ..exceptions.exception import CustomException
from ..functions.canvas import canvas_clear
from ..functions.canvas import canvas_get_zoom
from ..functions.canvas import canvas_remove
from ..functions.canvas import canvas_restore_zoom
from ..functions.canvas import canvas_update
from ..functions.data_process import csv_to_dataframe
from ..functions.utils import add_spectrum
from ..functions.utils import get_file
from ..functions.utils import get_handles
from ..functions.utils import label_options


class QtFunctions:
    """Function class for the GUI app."""

    def plot(self, df: pd.DataFrame, label: str, ax: Axes, state: str = "Add") -> Axes:
        """Plots the pd.DataFrame object to the Canvas."""
        try:
            ax = df.plot(
                ax=ax,
                x=0,
                y=1,
                lw=self.settings.general.lw,
                legend=self.legend,
                label=label,
            )

            # Convert DataFrame to Spectrum object
            sp = add_spectrum(ax.lines[-1])
            self.curves.update({sp.label: sp})

            if self.legend:
                self.add_legend()
            if state == "Load":
                self.curves[list(self.curves)[-1]].loaded = True

            self.cursor: Cursor = canvas_update(
                self.canvas, self.xlabel, self.ylabel, self.title
            )

            self.update_spectrum_table()

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

            input_file = get_file(self.settings.general.path)
            df, label = csv_to_dataframe(
                input_file=input_file, sep=self.sep, engine=self.engine
            )
            self.title = label

            # keep the old x and y limits
            old_x_lim, old_y_lim = canvas_get_zoom(self.canvas)

            canvas_clear(self.canvas.axes)
            self.plot(df=df, label=label, ax=self.canvas.axes, state="Load")

            # keep the new x and y limits
            new_x_lim, new_y_lim = canvas_get_zoom(self.canvas)

            new = self.curves[list(self.curves)[-1]]
            new.loaded = True

            self.undo_stack.append(
                ("Load", last, new, old_x_lim, old_y_lim, new_x_lim, new_y_lim)
            )
        except Exception as e:
            raise CustomException(e)

    def add_plot(self) -> None:
        """Adds another line to the Canvas"""
        try:
            prev = self.added[-1]
            input_file = get_file(self.settings.general.path)

            # keep the old x and y limits
            old_x_lim, old_y_lim = canvas_get_zoom(self.canvas)

            df, label = csv_to_dataframe(
                input_file=input_file, sep=self.sep, engine=self.engine
            )
            self.plot(df=df, label=label, ax=self.canvas.axes, state="Add")

            # keep the new x and y limits
            new_x_lim, new_y_lim = canvas_get_zoom(self.canvas)

            new = self.curves[list(self.curves)[-1]]

            self.undo_stack.append(
                ("Add Plot", prev, new, old_x_lim, old_y_lim, new_x_lim, new_y_lim)
            )

            self.added.append(new)
            self.cursor: Cursor = canvas_update(
                self.canvas, self.xlabel, self.ylabel, self.title
            )

        except Exception as e:
            raise CustomException(e)

    def df_p_plot(self, ax: Axes) -> Peaks:
        """Adds peaks to the Canvas"""
        try:
            # keep the old x and y limits
            old_x_lim, old_y_lim = canvas_get_zoom(self.canvas)

            pks = ax.scatter(
                x=self.df_p['p_x'],
                y=self.df_p['p_y'],
                c='red',
                s=2,
                zorder=3,
                label="peak_user"
            )

            pks_obj = Peaks(pks)

            self.update_peaks_table()
            self.cursor: Cursor = canvas_update(
                self.canvas, self.xlabel, self.ylabel, self.title
            )

            # restore zoom
            canvas_restore_zoom(self.canvas, old_x_lim, old_y_lim)
            return pks_obj
        except Exception as e:
            raise CustomException(e)

    def plot_demo(self) -> None:
        df = pd.DataFrame({"x": self.x, "y": self.y}, dtype="float")
        self.plot(df=df, label=self.label, ax=self.canvas.axes, state="Load")

    ## Data processing ##
    def process_data(self, function: Callable, params) -> None:
        """Call the data processing functions
        to the visible (checked) Spectrum objects.
        """
        try:
            for i in self.curves.values():
                if i.tristate == 1:
                    actions = function(i, params)
                    self.undo_stack.append(actions)

            # Recompute the data limits
            self.canvas.axes.relim()

            # Update using the new data limits
            self.canvas.axes.autoscale_view()

            self.cursor: Cursor = canvas_update(
                self.canvas, self.xlabel, self.ylabel, self.title
            )
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

    def edit_form(self) -> None:
        try:
            fig, ax = plt.subplots(nrows=1, ncols=1)
            for i in self.curves.values():
                if i.tristate == 1:
                    ax.plot(
                        i.x_data, i.y_data, lw=self.settings.general.lw, label=i.label
                    )

            if self.legend:
                handles: list[Line2D] = get_handles(ax)
                ax.legend(handles=handles)

            if self.x_rev:
                ax.invert_xaxis()

            if self.y_rev:
                ax.invert_yaxis()

            plt.title(self.title)
            plt.xlabel(self.xlabel)
            plt.ylabel(self.ylabel)

            c = mplcursors.cursor(multiple=True)

            @c.connect("add")
            def _(selection):
                xi, _ = selection.target
                selection.annotation.set_bbox(None)
                selection.annotation.arrow_patch.set(arrowstyle="-", linewidth=0.4)
                selection.annotation.set(
                    text=int(xi), color=selection.artist.get_color(), size=12
                )

            plt.show()
        except Exception as e:
            raise CustomException(e)

    def reverse_axis(self, axis) -> None:
        try:
            if axis == "X":
                self.canvas.axes.invert_xaxis()
                if not self.x_rev:
                    self.x_rev = True
                else:
                    self.x_rev = False
            else:
                self.canvas.axes.invert_yaxis()
                if not self.y_rev:
                    self.y_rev = True
                else:
                    self.y_rev = False

            self.undo_stack.append((f"Reverse {axis}", None))
            self.cursor: Cursor = canvas_update(
                self.canvas, self.xlabel, self.ylabel, self.title
            )

        except Exception as e:
            raise CustomException(e)

    # Undo redo
    def undo(self) -> None:
        if self.undo_stack:
            actions = self.undo_stack.pop()
            self.redo_stack.append(actions)

            if actions[0] == "Load":
                if not actions[1] == "":
                    canvas_remove(actions[2].curve)
                    self.canvas.axes.add_line(actions[1].curve)

                    # restore zoom
                    canvas_restore_zoom(self.canvas, actions[3], actions[4])

                    self.load_list.append(actions[2])
                    self.curves = dict()
                    self.curves.update({actions[1].label: actions[1]})

            elif actions[0] == "Add Plot":
                canvas_remove(actions[2].curve)

                # restore zoom
                canvas_restore_zoom(self.canvas, actions[3], actions[4])

                self.curves.pop(actions[2].id)

            elif actions[0] == "Smooth":
                actions[3].y = actions[1]

            elif actions[0] == "Baseline":
                actions[3].y = actions[1]

            elif actions[0] == "Peaks":
                actions[2].peaks.remove()
                actions[2].delete_peaks()
                self.update_peaks_table()

            elif actions[0] == "Normalize Min-Max":
                actions[3].y = actions[1]

            elif actions[0] == "Normalize Z":
                actions[3].y = actions[1]

            elif actions[0] == "Reverse X":
                self.canvas.axes.invert_xaxis()

            elif actions[0] == "Reverse Y":
                self.canvas.axes.invert_yaxis()

            elif actions[0] == "Label":
                self.xlabel = actions[1][0]
                self.ylabel = actions[1][1]

            elif actions[0] == "New_my_peak":
                self.df_p = self.df_p.drop(self.df_p.tail(1).index).reset_index(
                    drop=True
                )
                actions[2].remove()

            elif actions[0] == "Delete_my_peak":
                self.df_p = pd.concat([self.df_p, actions[1]]).reset_index(drop=True)
                actions[2].add_to_axes(self.canvas.axes)

            elif actions[0] == "Clear Table":
                # TODO
                peaks_user =[]
                for path_coll in actions[1]:
                    if path_coll.get_label() == "peak_user":
                        data = path_coll.get_offsets().data
                        peaks_user.append((data[0][0], data[0][1]))
                    
                    peaks = Peaks(path_coll)
                    # TODO: check functionality with spectrum
                    # spectrum.add_peaks(peaks)
                    peaks.add_to_axes(self.canvas.axes)

                self.df_p = pd.DataFrame(peaks_user, columns=["p_x", "p_y"]) 

            self.cursor: Cursor = canvas_update(
                self.canvas, self.xlabel, self.ylabel, self.title
            )
            self.update_spectrum_table()
            self.update_peaks_table()

    def redo(self) -> None:
        if self.redo_stack:
            actions = self.redo_stack.pop()
            self.undo_stack.append(actions)

            if actions[0] == "Load":
                if not actions[1] == "":
                    canvas_remove(actions[1].curve)
                    self.canvas.axes.add_line(actions[2].curve)

                    # restore zoom
                    canvas_restore_zoom(self.canvas, actions[5], actions[6])

                    new = self.load_list.pop()
                    self.curves = dict()
                    self.curves.update({new.label: new})

            elif actions[0] == "Add Plot":
                self.canvas.axes.add_line(actions[2].curve)

                # restore zoom
                canvas_restore_zoom(self.canvas, actions[5], actions[6])

                self.curves.update({actions[2].label: actions[2]})

            elif actions[0] == "Smooth":
                actions[3].y = actions[2]

            elif actions[0] == "Baseline":
                actions[3].y = actions[2]

            elif actions[0] == "Peaks":
                actions[1].add_to_axes(self.canvas.axes)
                actions[2].add_peaks(actions[1])
                self.update_peaks_table()

            elif actions[0] == "Normalize Min-Max":
                actions[3].y = actions[2]

            elif actions[0] == "Normalize Z":
                actions[3].y = actions[2]

            elif actions[0] == "Reverse X":
                self.canvas.axes.invert_xaxis()

            elif actions[0] == "Reverse Y":
                self.canvas.axes.invert_yaxis()

            elif actions[0] == "Label":
                self.xlabel = actions[2][0]
                self.ylabel = actions[2][1]

            elif actions[0] == "New_my_peak":
                self.df_p = pd.concat([self.df_p, actions[1]])
                actions[2].add_to_axes(self.canvas.axes)

            elif actions[0] == "Delete_my_peak":
                self.df_p = self.df_p.drop(self.df_p.tail(1).index).reset_index(drop=True)
                actions[2].remove()
                self.update_peaks_table()
            
            elif actions[0] == "Clear Table":
                # TODO
                print(actions, self.canvas.axes.collections)

            self.cursor: Cursor = canvas_update(
                self.canvas, self.xlabel, self.ylabel, self.title
            )
            self.update_spectrum_table()
            self.update_peaks_table() # check it

    ## Checkbox ##
    def chkbox_clicked(self, row, col) -> None:
        if self.table.item(row, col).checkState() == QtCore.Qt.Unchecked:
            for i in self.curves.values():
                if i.label == self.table.item(row, col).text():
                    i.invisible()
                if i.has_peaks:
                    if i.peaks.name == self.table.item(row, col).text():
                        i.peaks.invisible()

        if self.table.item(row, col).checkState() == QtCore.Qt.Checked:
            for i in self.curves.values():
                if i.label == self.table.item(row, col).text():
                    i.visible()
                if i.has_peaks:
                    if i.peaks.name == self.table.item(row, col).text():
                        i.peaks.visible()

        if self.table.item(row, col).checkState() == 1:
            for i in self.curves.values():
                if i.label == self.table.item(row, col).text():
                    i.disabled()

        self.cursor: Cursor = canvas_update(
            self.canvas, self.xlabel, self.ylabel, self.title
        )

    ## Legend Checkbox ##
    def add_legend(self) -> None:
        if self.legend_checkBox.isChecked():
            self.legend = True
            handles: list[Line2D] = get_handles(self.canvas.axes)
            self.canvas.axes.legend(handles=handles)
        else:
            self.legend = False
            self.canvas.axes.legend().set_visible(False)

        self.cursor: Cursor = canvas_update(
            self.canvas, self.xlabel, self.ylabel, self.title
        )

    ## Spinbox ##
    def spinbox_value_changed(self, axis: str) -> None:
        value_y = self.doubleSpinBox_y_axis.value()
        value_x = self.doubleSpinBox_x_axis.value()
        for i in self.curves.values():
            if i.tristate == 1:
                if axis == "y":
                    i.y_data += value_y
                    i.curve.set_ydata(i.y_data)
                elif axis == "x":
                    i.x_data += value_x
                    i.curve.set_xdata(i.x_data)
        self.cursor: Cursor = canvas_update(
            self.canvas, self.xlabel, self.ylabel, self.title
        )

    ## Tables ##
    def clear_peaks_table(self) -> None:
        try:
            old_table = dict()
            # Get the column count and iterate through the columns
            column_count = self.table_peaks.columnCount()
            for column in range(column_count):
                # Get the column header text
                header = self.table_peaks.horizontalHeaderItem(column).text()
                print(header)
                # Iterate through allthe rows and get the data for that column
                temp = []
                for row in range(self.table_peaks.rowCount()):
                    item = self.table_peaks.item(row, column)
                    print(item)
                    if item is not None and item.text() != "":
                        temp.append(item.text())
                old_table[header] = temp
            
            # Clear the table
            self.table_peaks.setRowCount(0)
            self.table_peaks.setColumnCount(1)

            if self.canvas.axes.collections:
                prev_coll = []
                for path_coll in self.canvas.axes.collections:
                    prev_coll.append(path_coll)
                    path_coll.remove()
            else:
                prev_coll = []

            self.df_p = pd.DataFrame(columns=["p_x", "p_y"])

            prev_obj = dict()
            for spectrum in self.curves.values():
                # TODO: check with my peaks
                if spectrum.has_peaks:
                    prev_obj.update({spectrum: spectrum.peaks})
                    # delete the peaks_object from the canvas
                    spectrum.peaks.remove()                    
                    # delete the peaks_object from the Spectrum Object
                    spectrum.delete_peaks()

            self.undo_stack.append(("Clear Table", prev_coll, prev_obj, old_table))

            self.cursor: Cursor = canvas_update(
                self.canvas, self.xlabel, self.ylabel, self.title
            )
            self.update_spectrum_table()
        except Exception as e:
            raise CustomException(e)

    def update_spectrum_table(self) -> None:
        """Updates the spectrum table."""
        try:
            self.table.setRowCount(0)
            self.table.insertRow(0)
            self.table.setRowCount(len(self.curves))

            for i, j in enumerate(self.curves.values()):
                # Update Spectrum column
                if not j.label.startswith("peak_"):
                    chkBoxItem = QtWidgets.QTableWidgetItem(j.label)
                    chkBoxItem.setFlags(
                        QtCore.Qt.ItemIsUserCheckable
                        | QtCore.Qt.ItemIsUserTristate
                        | QtCore.Qt.ItemIsEnabled
                    )
                    chkBoxItem.setCheckState(QtCore.Qt.Checked)
                    self.table.setItem(i, 0, chkBoxItem)
                    # Update Peaks column
                    if j.has_peaks:
                        chkBoxItem = QtWidgets.QTableWidgetItem(f"peak_{j.label}")
                        chkBoxItem.setFlags(
                            QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEnabled
                        )
                        chkBoxItem.setCheckState(QtCore.Qt.Checked)
                        self.table.setItem(i, 1, chkBoxItem)
        except Exception as e:
            raise CustomException(e)

    def update_peaks_table(self) -> None:
        """Updates the peaks table."""
        try:
            # Clear rows and columns
            self.table_peaks.setRowCount(0)
            self.table_peaks.setColumnCount(1)

            if not self.df_p.empty:
                my_peaks = [str(int(i)) for i in self.df_p["p_x"].tolist()]
            else:
                my_peaks = []

            # Initialize a numedtuple for spectrum peaks x data and labels
            spectrum_peaks_labels = namedtuple("SpectrumPeaks",["peaks_x", "label"])

            spectrum_peaks_labels_list = [
                spectrum_peaks_labels(peaks_x=curve.peaks.x, label=curve.label) 
                for curve in self.curves.values()
                if curve.has_peaks
                ]

            # Update Spectrum Peaks
            if spectrum_peaks_labels_list:
                # Set row count
                m = max([peak.peaks_x.size for peak in spectrum_peaks_labels_list])
                self.table_peaks.setRowCount(m)
                # Set column count
                self.table_peaks.setColumnCount(len(spectrum_peaks_labels_list) + 1)
                # Add the header labels
                self.table_peaks.setHorizontalHeaderLabels(["My_peaks"] + [spectrum.label for spectrum in spectrum_peaks_labels_list])

                for col, data in enumerate(spectrum_peaks_labels_list, start=1):
                    pks = [str(int(i)) for i in np.sort(data.peaks_x)]
                    for num, v in enumerate(pks):
                        self.table_peaks.setItem(
                            num, col, QtWidgets.QTableWidgetItem(v)
                        )
            # Update My_peaks
            if my_peaks:
                if not spectrum_peaks_labels_list:
                    self.table_peaks.insertRow(0)
                    self.table_peaks.setHorizontalHeaderLabels(["My_peaks"])
                    self.table_peaks.setRowCount(len(self.df_p))
                for i in range(len(my_peaks)):
                    self.table_peaks.setItem(
                        i, 0, QtWidgets.QTableWidgetItem(my_peaks[i])
                    )
        except Exception as e:
            raise CustomException(e)

    def save_table(self) -> None:
        """Saves the peaks table to a CSV file."""
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
                    if item is not None and item.text() != "":
                        df.at[row, col_headers[col]] = item.text()

            # Save into a CSV file
            f = QtWidgets.QFileDialog.getSaveFileName(
                parent=None,
                caption="Save File",
                directory=self.dir,
                filter="Comma Separated Values (*.csv)",
            )[0]

            # in case the user wants the default separator unchanged
            sep = "," if self.sep is None else self.sep

            df.to_csv(f, sep, index=False)

        except Exception as e:
            raise CustomException(e)

    ## Labels ##
    def add_label(self) -> None:
        try:
            prev = self.labels[-1]
            new = self.dropbox_lbl.currentText()

            self.xlabel, self.ylabel = label_options(new)
            self.undo_stack.append(
                ("Label", label_options(prev), (self.xlabel, self.ylabel))
            )
            self.labels.append(new)
            self.cursor: Cursor = canvas_update(
                self.canvas, self.xlabel, self.ylabel, self.title
            )
        except Exception as e:
            raise CustomException(e)
        