from dataclasses import dataclass
from typing import Optional, Iterable

@dataclass
class General:
    path: str
    sep: str
    engine: str
    lw: float

@dataclass
class Smooth:
    window_length: int
    polyorder: int
    deriv: int
    delta: float
    axis: int

@dataclass
class Baseline:
  lam: int
  p: float
  niter: int

@dataclass
class Peaks:
  height: Optional[int | float | Iterable]
  threshold: Optional[int | float | Iterable]
  distance: Optional[int | float]
  prominence: Optional[int | float | Iterable]
  width: Optional[int | float | Iterable]

@dataclass
class Shortcuts:
  Load: str
  Baseline: str
  Smoothing: str
  Peaks: str
  Undo: str
  Redo: str
  Edit: str
  Add_Plot: str
  Reverse_X: str
  Reverse_Y: str
  Save_As: str
  Settings: str
  Normalize: str
  Normalize_Z: str

@dataclass
class Config:
    general: General
    smooth: Smooth
    baseline: Baseline
    peaks: Peaks
    shortcuts: Shortcuts