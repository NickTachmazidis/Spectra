
from matplotlib.axes import Axes
from matplotlib.lines import Line2D
from matplotlib.widgets import Cursor
from src.exceptions.exception import CustomException
from src.gui.canvas import Canvas


def add_cursor(
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

def remove_cursor(axes: Axes) -> None:
    """Remove cursor line from plot."""
    for i in axes.lines:
        if i.get_label() == "cursor":
            i.remove()

def canvas_clear(axes: Axes) -> None:
    """Clears the Axes in the Canvas object."""
    axes.cla()


def canvas_update(canvas: Canvas, xlabel: str, ylabel: str, title: str) -> Cursor:
    """Updates the Canvas object."""
    try:
        remove_cursor(canvas.axes)
        
        canvas.draw_idle()
        
        canvas.axes.set_xlabel(xlabel)
        canvas.axes.set_ylabel(ylabel)
        canvas.axes.set_title(title)
        
        cursor: Cursor = add_cursor(canvas.axes)
        return cursor
    except Exception as e:
        raise CustomException(e)

def canvas_remove(obj: Line2D) -> None:
    """Removes a Line2D obj from the canvas."""
    obj.remove()

def canvas_get_zoom(canvas: Canvas) -> tuple[tuple[float, float], tuple[float, float]]:
    """Returns the current x and y limits."""
    x_lim = canvas.axes.get_xlim()
    y_lim = canvas.axes.get_ylim()
    return x_lim, y_lim

def canvas_restore_zoom(
    canvas: Canvas, x_lim: tuple[float, float], y_lim: tuple[float, float]
) -> None:
    """Restores the x and y limits."""
    canvas.axes.set_xlim(x_lim)
    canvas.axes.set_ylim(y_lim)