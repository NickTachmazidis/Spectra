"""Labels class used in the GUI."""

from enum import Enum


class Label(Enum):
    NONE = "None", "", ""
    RAMAN = "Raman", "Raman Shift (cm⁻¹)", "Intensity →"
    IR_REF = "IR (Ref)", "Wavenumber (cm⁻¹)", "Reflectance Coefficient"
    IR_Abs = "IR (Abs)", "Wavenumber (cm⁻¹)", "Absorbance"
    IR_TRANS = "IR (Trans)", "Wavenumber (cm⁻¹)", "Transmittance (%)"
    UV_VIS = "UV-Vis", "Wavelength (nm)", "Absorbance"
    REFL = "Reflectance", "Wavelength (nm)", "Reflectance (%)"
    XRF = "XRF", "Energy (keV)", "Counts"
    XRD = "XRD", "2θ (degrees)", "Intensity"

    @classmethod
    def return_value(cls, value: str) -> tuple[str, str, str]:
        """Return label, x and y data based on value."""
        for i in cls._value2member_map_:
            if value in i:
                x, y = i[1], i[2]
                return x, y