# Core
from typing import Callable

import matplotlib.pyplot as plt
import mplcursors
import numpy as np
import pandas as pd

# Data/visualisation
from matplotlib.axes import Axes
from matplotlib.lines import Line2D
from matplotlib.widgets import Cursor

# GUI
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import QFileDialog

# src
from src.exception import CustomException
from src.gui.canvas import Canvas
from src.utils import add_spectrum, check_path, get_handles, label_options


class Funcs:
    ## Canvas ##

    def add_cursor(
        self,
        ax: Canvas,
        hl: bool = True,
        vl: bool = True,
        color: str = "red",
        lw: float = 0.8,
    ) -> Cursor:
        """Adds a Cursor object to the Axes."""
        cursor = Cursor(
            ax, horizOn=hl, vertOn=vl, color=color, linewidth=lw, label="cursor"
        )
        return cursor

    def canvas_clear(self) -> None:
        """Clears the Canvas object."""
        self.canvas.axes.cla()

    def canvas_update(self) -> None:
        """Updates the Canvas object."""
        try:
            # Remove cursor
            for i in self.canvas.axes.lines:
                if i.get_label() == "cursor":
                    i.remove()

            self.canvas.draw_idle()
            self.canvas.axes.set_xlabel(self.xlabel)
            self.canvas.axes.set_ylabel(self.ylabel)
            self.canvas.axes.set_title(self.title)
            self.cursor = self.add_cursor(self.canvas.axes)

        except Exception as e:
            raise CustomException(e)

    def canvas_remove(self, obj: Line2D) -> None:
        """Removes a Line2D obj from the canvas."""
        idx = self.canvas.axes.lines.index(obj)
        self.canvas.axes.lines[idx].remove()

    def canvas_get_zoom(self) -> tuple[tuple[float, float], tuple[float, float]]:
        """Returns the current x and y limits."""
        x_lim = self.canvas.axes.get_xlim()
        y_lim = self.canvas.axes.get_ylim()
        return x_lim, y_lim

    def canvas_restore_zoom(
        self, x_lim: tuple[float, float], y_lim: tuple[float, float]
    ) -> None:
        """Restores the x and y limits."""
        self.canvas.axes.set_xlim(x_lim)
        self.canvas.axes.set_ylim(y_lim)

    def get_file(self) -> str:
        """Opens a popup dialog to load the file."""
        try:
            input_file = QFileDialog.getOpenFileName(
                parent=None,
                caption="Choose files",
                directory=self.settings.general.path,
                filter="Data file (*.csv)",
            )[0]
            return input_file
        except Exception as e:
            raise CustomException(e)

    def csv_to_dataframe(
        self, input_file: str, sep: str, engine: str
    ) -> tuple[pd.DataFrame, str]:
        """Converts the CSV file to a pd.DataFrame object."""
        try:
            label = input_file.split("/")[-1].replace(".csv", "")
            df = pd.read_csv(input_file, sep=sep, engine=engine, dtype="float")
            return df, label
        except Exception as e:
            raise CustomException(e)

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
            sp, sp_id = add_spectrum(ax.lines[-1])
            self.curves.update({sp_id: sp})

            if self.legend:
                self.add_legend()
            if state == "Load":
                self.curves[list(self.curves)[-1]].loaded = True

            self.canvas_update()
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

            input_file = self.get_file()
            df, label = self.csv_to_dataframe(
                input_file=input_file,
                sep=self.sep,
                engine=self.engine
            )
            self.title = label

            # keep the old x and y limits
            old_x_lim, old_y_lim = self.canvas_get_zoom()

            self.canvas_clear()
            self.plot(df=df, label=label, ax=self.canvas.axes, state="Load")

            # keep the new x and y limits
            new_x_lim, new_y_lim = self.canvas_get_zoom()

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
            input_file = self.get_file()

            # keep the old x and y limits
            old_x_lim, old_y_lim = self.canvas_get_zoom()

            df, label = self.csv_to_dataframe(
                input_file=input_file, sep=self.sep, engine=self.engine
            )
            self.plot(df=df, label=label, ax=self.canvas.axes, state="Add")

            # keep the new x and y limits
            new_x_lim, new_y_lim = self.canvas_get_zoom()

            new = self.curves[list(self.curves)[-1]]

            self.undo_stack.append(
                ("Add Plot", prev, new, old_x_lim, old_y_lim, new_x_lim, new_y_lim)
            )

            self.added.append(new)
            self.canvas_update()
        except Exception as e:
            raise CustomException(e)

    def df_p_plot(self, ax) -> None:
        """Adds peaks to the Canvas"""
        try:
            # keep the old x and y limits
            old_x_lim, old_y_lim = self.canvas_get_zoom()

            self.df_p.plot(
                ax=ax,
                x=0,
                y=1,
                marker="o",
                c="r",
                s=10,
                kind="scatter",
                label="peak_user",
                legend=False,
            )

            self.update_peaks_table()
            self.canvas_update()

            # restore zoom
            self.canvas_restore_zoom(old_x_lim, old_y_lim)

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

    def edit_form(self) -> None:
        try:
            fig, ax = plt.subplots(nrows=1, ncols=1)
            for i in self.curves.values():
                if i.tristate == 1:
                    ax.plot(i.x_data, i.y_data, lw=self.settings.general.lw, label=i.label)

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
            self.canvas_update()

        except Exception as e:
            raise CustomException(e)

    # Undo redo
    def undo(self) -> None:
        if self.undo_stack:
            actions = self.undo_stack.pop()
            self.redo_stack.append(actions)

            if actions[0] == "Load":
                if not actions[1] == "":
                    self.canvas_remove(actions[2].curve)
                    self.canvas.axes.add_line(actions[1].curve)

                    # restore zoom
                    self.canvas_restore_zoom(actions[3], actions[4])

                    self.load_list.append(actions[2])
                    self.curves = dict()
                    self.curves.update({actions[1].id: actions[1]})

            elif actions[0] == "Add Plot":
                self.canvas_remove(actions[2].curve)

                # restore zoom
                self.canvas_restore_zoom(actions[3], actions[4])

                self.curves.pop(actions[2].id)

            elif actions[0] == "Smooth":
                actions[3].change_y(actions[1])

            elif actions[0] == "Baseline":
                actions[3].change_y(actions[1])

            elif actions[0] == "Peaks":
                self.canvas_remove(actions[2].peaks_object)
                actions[2].delete_peaks()
                self.update_peaks_table()

            elif actions[0] == "Normalize Min-Max":
                actions[3].change_y(actions[1])

            elif actions[0] == "Normalize Z":
                actions[3].change_y(actions[1])

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
                self.canvas.axes.collections[-1].remove()

            elif actions[0] == "Delete_my_peak":
                self.df_p = pd.concat([self.df_p, actions[1]]).reset_index(drop=True)
                self.df_p_plot(ax=self.canvas.axes)

            elif actions[0] == "Clear Table":
                self.canvas.axes.collections = actions[1]

                for k, v in actions[2].items():
                    k.add_peaks(v)
                    self.canvas.axes.lines.append(v)

            self.canvas_update()
            self.update_spectrum_table()
            self.update_peaks_table()

    def redo(self) -> None:
        if self.redo_stack:
            actions = self.redo_stack.pop()
            self.undo_stack.append(actions)

            if actions[0] == "Load":
                if not actions[1] == "":
                    self.canvas_remove(actions[1].curve)
                    self.canvas.axes.add_line(actions[2].curve)

                    # restore zoom
                    self.canvas_restore_zoom(actions[5], actions[6])

                    new = self.load_list.pop()
                    self.curves = dict()
                    self.curves.update({new.id: new})

            elif actions[0] == "Add Plot":
                self.canvas.axes.add_line(actions[2].curve)

                # restore zoom
                self.canvas_restore_zoom(actions[5], actions[6])

                self.curves.update({actions[2].id: actions[2]})

            elif actions[0] == "Smooth":
                actions[3].change_y(actions[2])

            elif actions[0] == "Baseline":
                actions[3].change_y(actions[2])

            elif actions[0] == "Peaks":
                self.canvas.axes.add_line(actions[1])
                actions[2].add_peaks(actions[1])
                self.update_peaks_table()

            elif actions[0] == "Normalize Min-Max":
                actions[3].change_y(actions[2])

            elif actions[0] == "Normalize Z":
                actions[3].change_y(actions[2])

            elif actions[0] == "Reverse X":
                self.canvas.axes.invert_xaxis()

            elif actions[0] == "Reverse Y":
                self.canvas.axes.invert_yaxis()

            elif actions[0] == "Label":
                self.xlabel = actions[2][0]
                self.ylabel = actions[2][1]

            elif actions[0] == "New_my_peak":
                self.df_p = pd.concat([self.df_p, actions[1]])
                self.df_p_plot(self.canvas.axes)

            elif actions[0] == "Delete_my_peak":
                self.df_p = self.df_p.drop(self.df_p.tail(1).index).reset_index(
                    drop=True
                )
                self.canvas.axes.collections[-1].remove()
                self.update_peaks_table()

            self.canvas_update()
            self.update_spectrum_table()

    ## Checkbox ##
    def chkbox_clicked(self, row, col) -> None:
        if self.table.item(row, col).checkState() == QtCore.Qt.Unchecked:
            for i in self.curves.values():
                if i.label == self.table.item(row, col).text():
                    i.invisible()
                if i.peaks:
                    if i.peaks_object.get_label() == self.table.item(row, col).text():
                        i.peaks_object.set_visible(False)

        if self.table.item(row, col).checkState() == QtCore.Qt.Checked:
            for i in self.curves.values():
                if i.label == self.table.item(row, col).text():
                    i.visible()
                if i.peaks:
                    if i.peaks_object.get_label() == self.table.item(row, col).text():
                        i.peaks_object.set_visible(True)

        if self.table.item(row, col).checkState() == 1:
            for i in self.curves.values():
                if i.label == self.table.item(row, col).text():
                    i.disabled()

        self.canvas_update()

    ## Legend Checkbox ##
    def add_legend(self) -> None:
        if self.legend_checkBox.isChecked():
            self.legend = True
            handles: list[Line2D] = get_handles(self.canvas.axes)
            self.canvas.axes.legend(handles=handles)
        else:
            self.legend = False
            self.canvas.axes.legend().set_visible(False)

        self.canvas_update()

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
        self.canvas_update()

    ## Tables ##
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

            self.df_p = pd.DataFrame(columns=["p_x", "p_y"])

            prev_obj = dict()
            for i in self.curves.values():
                if i.peaks:
                    prev_obj.update({i: i.peaks_object})
                    # delete the peaks_object from the canvas
                    idx = self.canvas.axes.lines.index(i.peaks_object)
                    self.canvas.axes.lines[idx].remove()
                    # delete the peaks_object from the Spectrum Object
                    i.delete_peaks()

            self.undo_stack.append(("Clear Table", prev_coll, prev_obj))
            self.canvas_update()
            self.update_spectrum_table()
        except Exception as e:
            raise CustomException(e)

    def update_spectrum_table(self) -> None:
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
                    if j.peaks:
                        chkBoxItem = QtWidgets.QTableWidgetItem(f"peak_{j.label}")
                        chkBoxItem.setFlags(
                            QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEnabled
                        )
                        chkBoxItem.setCheckState(QtCore.Qt.Checked)
                        self.table.setItem(i, 1, chkBoxItem)
        except Exception as e:
            raise CustomException(e)

    def update_peaks_table(self) -> None:
        try:
            self.table_peaks.setRowCount(0)  # clear rows
            self.table_peaks.setColumnCount(1)  # clear columns
            if not self.df_p.empty:
                my_peaks = [str(int(i)) for i in self.df_p["p_x"].tolist()]
            else:
                my_peaks = []

            sp_peaks = []  # list for spectrum peaks x data
            sp_labels = []  # list for spectrum label
            for i in self.curves.values():
                if i.peaks:
                    sp_peaks.append(i.peaks_object.get_xdata())
                    sp_labels.append(i.label)

            # Update Spectrum Peaks
            if sp_peaks:
                # Set row count
                m = max([i.size for i in sp_peaks])
                self.table_peaks.setRowCount(m)
                # Set column count
                self.table_peaks.setColumnCount(len(sp_peaks) + 1)
                # Add the header labels
                self.table_peaks.setHorizontalHeaderLabels(["My_peaks"] + sp_labels)

                for col, xdata in enumerate(sp_peaks, start=1):
                    pks = [str(int(i)) for i in np.sort(xdata)]
                    for num, v in enumerate(pks):
                        self.table_peaks.setItem(
                            num, col, QtWidgets.QTableWidgetItem(v)
                        )
            # Update My_peaks
            if my_peaks:
                if not sp_peaks:
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
                filter="Comma Separated Values (*.csv)"
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
            self.canvas_update()
        except Exception as e:
            raise CustomException(e)

    ## Settings Window ##
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

    ## Save spectrum ##
    def save_as(self) -> None:
        try:
            dfs = []
            for i in self.curves.values():
                if i.tristate == 1:
                    title = i.label
                    df = pd.DataFrame({"x": i.x_data, "y": i.y_data})
                    if i.peaks:
                        df["peaks_x"] = pd.Series(i.peaks_object.get_xdata())
                        df["peaks_y"] = pd.Series(i.peaks_object.get_ydata())
                dfs.append((title, df))

            file = str(
                QtWidgets.QFileDialog.getExistingDirectory(self, "Select Directory")
            )

            sep = self.sep

            if sep is None or len(sep) > 1:
                sep = ","

            for i in dfs:
                path = check_path(file, i[0])
                i[1].to_csv(path_or_buf=path, sep=sep, index=False)

        except Exception as e:
            raise CustomException(e)
