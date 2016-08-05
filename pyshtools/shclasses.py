"""
Class interface for SHTOOLS.

pyshtools defines several classes that facilitate the interactive
examination of geographical gridded data and their associated
spherical harmonic coefficients. Subclasses are used to handle different
internal data types and superclasses are used to implement interface
functions and documentation.

pyshtools class structure:

    SHCoeffs
        SHRealCoeffs
        SHComplexCoeffs

    SHGrid
        DHRealGrid
        DHComplexGrid
        GLQRealGrid
        GLQComplexGrid

    SHWindow
        SHWindowCap
        SHWindowMask

For more information, see the documentation for the top level classes.
"""

from __future__ import absolute_import as _absolute_import
from __future__ import division as _division
from __future__ import print_function as _print_function

import numpy as _np
import matplotlib as _mpl
import matplotlib.pyplot as _plt

from . import _SHTOOLS as _shtools


# =============================================================================
# =========    COEFFICIENT CLASSES    =========================================
# =============================================================================

class SHCoeffs(object):
    """
    Spherical Harmonics Coefficient class.

    The coefficients of this class can be initialized using one of the
    three constructor methods:

    >>> x = SHCoeffs.from_array(numpy.zeros((2, lmax+1, lmax+1)))
    >>> x = SHCoeffs.from_random(powerspectrum[0:lmax+1])
    >>> x = SHCoeffs.from_file('fname.dat')

    The normalization convention of the input coefficents is specified
    by the normalization and csphase parameters, which take the following
    values:

    normalization : '4pi' (default), geodesy 4-pi normalized.
                  : 'ortho', orthonormalized.
                  : 'schmidt', Schmidt semi-normalized.

    csphase       : 1 (default), exlcude the Condon-Shortley phase factor.
                  : -1, include the Condon-Shortley phase factor.

    See the documentation for each constructor method for further options.

    Once initialized, each class instance defines the following class
    attributes:

    lmax          : The maximum spherical harmonic degree of the coefficients.
    coeffs        : The raw coefficients with the specified normalization and
                    phase conventions.
    normalization : The normalization of the coefficients: '4pi', 'ortho', or
                    'schmidt'.
    csphse        : Defines whether the Condon-Shortley phase is used (1)
                    or not (-1).
    mask          : A boolean mask that is True for the permissible values of
                    degree l and order m.
    kind          : The coefficient data type: either 'complex' or 'real'.

    Each class instance provides the following methods:

    get_degrees()         : Return an array listing the spherical harmonic
                            degrees from 0 to lmax.
    get_powerperdegree()  : Return an array with the power per degree spectrum.
    get_powerperband()    : Return an array with the power per log_{bandwidth}
                            spectrum.
    get_coeffs()          : Return an array of spherical harmonics coefficients
                            with a different normalization convention.
    rotate()              : Rotate the coordinate system used to express the
                            spherical harmonics coefficients and return a new
                            class instance.
    return_coeffs()       : Return the current class instance as a new instance
                            using a different normalization convention.
    expand()              : Evaluate the coefficients on a spherical grid and
                            return a new SHGrid class instance.
    make_complex()        : Convert a real SHCoeffs class instance to a complex
                            class instance.
    make_real()           : Convert a complex SHCoeffs class instance to a real
                            class instance.
    plot_powerperdegree() : Plot the power per degree spectrum.
    plot_powerperband()   : Plot the power per log_{bandwidth}(degree)
                            spectrum.
    info()                : Print a summary of the data stored in the SHCoeffs
                            instance.
    """

    def __init__(self):
        """Unused constructor of the super class."""
        print('Initialize the class using one of the class methods:\n'
              '>>> SHCoeffs.from_array?\n'
              '>>> SHCoeffs.from_random?\n')
        pass

    # ---- factory methods:
    @classmethod
    def from_zeros(self, lmax, normalization='4pi', csphase=1, kind='real'):
        """
        Initialize class with zero from degree 0 to lmax.

        Usage
        -----

        x = SHCoeffs.from_array(lmax, [normalization, csphase])

        Parameters
        ----------

        lmax          : The highest harmonic degree l of the coefficients
        normalization : '4pi' (default), 'ortho' or 'schmidt' for geodesy 4pi
                        normalized, orthonormalized, or Schmidt semi-normalized
                        coefficients, respectively.
        csphase       : 1 (default) if the coefficients exclude the Condon-
                        Shortley phase factor, or -1 if they include it.
        """
        if kind.lower() not in set(['real', 'complex']):
            raise ValueError(
                "Kind must be 'real' or 'complex'. " +
                "Input value was {:s}."
                .format(repr(kind))
                )

        if normalization.lower() not in set(['4pi', 'ortho', 'schmidt']):
            raise ValueError(
                "The normalization must be '4pi', 'ortho' " +
                "or 'schmidt'. Input value was {:s}."
                .format(repr(normalization))
                )

        if csphase != 1 and csphase != -1:
            raise ValueError(
                "csphase must be either 1 or -1. Input value was {:s}."
                .format(repr(csphase))
                )

        for cls in self.__subclasses__():
            if cls.istype(kind):
                nl = lmax + 1
                coeffs = _np.zeros((2, nl, nl))
                return cls(coeffs, normalization=normalization.lower(),
                           csphase=csphase)

    @classmethod
    def from_array(self, coeffs, normalization='4pi', csphase=1):
        """
        Initialize the coefficients from an input numpy array.

        Usage
        -----

        x = SHCoeffs.from_array(array, [normalization, csphase])

        Parameters
        ----------

        array         : numpy array of size (2, lmax+1, lmax+1).
        normalization : '4pi' (default), 'ortho' or 'schmidt' for geodesy 4pi
                        normalized, orthonormalized, or Schmidt semi-normalized
                        coefficients, respectively.
        csphase       : 1 (default) if the coefficients exclude the Condon-
                        Shortley phase factor, or -1 if they include it.
        """
        if _np.iscomplexobj(coeffs):
            kind = 'complex'
        else:
            kind = 'real'

        if type(normalization) != str:
            raise ValueError('normalization must be a string. ' +
                             'Input type was {:s}'
                             .format(str(type(normalization))))

        if normalization.lower() not in set(['4pi', 'ortho', 'schmidt']):
            raise ValueError(
                "The normalization must be '4pi', 'ortho' " +
                "or 'schmidt'. Input value was {:s}."
                .format(repr(normalization))
                )

        if csphase != 1 and csphase != -1:
            raise ValueError(
                "csphase must be either 1 or -1. Input value was {:s}."
                .format(repr(csphase))
                )

        for cls in self.__subclasses__():
            if cls.istype(kind):
                return cls(coeffs, normalization=normalization.lower(),
                           csphase=csphase)

    @classmethod
    def from_random(self, power, kind='real', normalization='4pi', csphase=1):
        """
        Initialize the coefficients using Gaussian random variables.

        Usage
        -----

        x = SHCoeffs.from_random(power, [kind, normalization, csphase])

        Parameters
        ----------

        power         : numpy array of the power spectrum of size (lmax+1).
        kind          : 'real' (default) or 'complex' output coefficients.
        normalization : '4pi' (default), 'ortho' or 'schmidt' for geodesy 4pi
                        normalized, orthonormalized, or Schmidt semi-normalized
                        coefficients, respectively.
        csphase       : 1 (default) if the coefficients exclude the Condon-
                        Shortley phase factor, or -1 if they include it.
        """
        if type(normalization) != str:
            raise ValueError('normalization must be a string. ' +
                             'Input type was {:s}'
                             .format(str(type(normalization))))

        if normalization.lower() not in set(['4pi', 'ortho', 'schmidt']):
            raise ValueError(
                "The input normalization must be '4pi', 'ortho' " +
                "or 'schmidt'. Provided value was {:s}"
                .format(repr(normalization))
                )

        if csphase != 1 and csphase != -1:
            raise ValueError(
                "csphase must be 1 or -1. Input value was {:s}"
                .format(repr(csphase))
                )

        if kind.lower() not in set(['real', 'complex']):
            raise ValueError(
                "kind must be 'real' or 'complex'. " +
                "Input value was {:s}.".format(repr(kind)))

        nl = len(power)
        l = _np.arange(nl)

        if kind.lower() == 'real':
            coeffs = _np.random.normal(size=(2, nl, nl))
        elif kind.lower() == 'complex':
            coeffs = (_np.random.normal(size=(2, nl, nl)) +
                      1j * _np.random.normal(size=(2, nl, nl)))

        if normalization.lower() == '4pi':
            coeffs *= _np.sqrt(
                power / (2.0 * l + 1.0))[_np.newaxis, :, _np.newaxis]
        elif normalization.lower() == 'ortho':
            coeffs *= _np.sqrt(
                4.0 * _np.pi * power / (2.0 * l + 1.0)
                )[_np.newaxis, :, _np.newaxis]
        elif normalization.lower() == 'schmidt':
            coeffs *= _np.sqrt(power)[_np.newaxis, :, _np.newaxis]

        for cls in self.__subclasses__():
            if cls.istype(kind):
                return cls(coeffs, normalization=normalization.lower(),
                           csphase=csphase)

    @classmethod
    def from_file(self, fname, lmax, format='shtools', kind='real',
                  normalization='4pi', csphase=1, **kwargs):
        """
        Initialize the coefficients from input file.

        Usage
        -----

        x = SHCoeffs.from_file(filename, lmax, [format, kind, normalization,
                                                csphase, skip])

        Parameters
        ----------

        filename      : Name of the file, including path.
        lmax          : Maximum spherical harmonic degree to read from the
                        file.
        format        : 'shtools' (default).
        kind          : Output 'real' (default) or 'complex' coefficients.
        normalization : '4pi' (default), 'ortho' or 'schmidt' for geodesy 4pi
                        normalized, orthonormalized, or Schmidt semi-normalized
                        coefficients, respectively.
        csphase       : 1 (default) if the coefficients exclude the Condon-
                        Shortley phase factor, or -1 if they include it.
        skip          : Number of lines to skip at the beginning of the file.

        Description
        -----------

        If format='shtools' spherical harmonic coefficients are read from an
        ascii-formatted file. The maximum spherical harmonic degree that is
        read is determined by the input value lmax. If the optional value skip
        is specified, parsing of the file will commence after the first skip
        lines.

        Each line of the file must contain

        l, m, cilm[0, l, m], cilm[1, l, m]

        For each value of increasing l, increasing from zero, all the angular
        orders are listed in inceasing order, from 0 to l.

        For more information, see SHRead.

        """
        if type(normalization) != str:
            raise ValueError('normalization must be a string. ' +
                             'Input type was {:s}'
                             .format(str(type(normalization))))

        if normalization.lower() not in set(['4pi', 'ortho', 'schmidt']):
            raise ValueError(
                "The input normalization must be '4pi', 'ortho' " +
                "or 'schmidt'. Provided value was {:s}"
                .format(repr(normalization))
                )
        if csphase != 1 and csphase != -1:
            raise ValueError(
                "csphase must be 1 or -1. Input value was {:s}"
                .format(repr(csphase))
                )

        if format.lower() == 'shtools':
            if kind.lower() == 'real':
                coeffs, lmax = _shtools.SHRead(fname, lmax, **kwargs)
            else:
                raise NotImplementedError(
                    "kind={:s} not yet implemented".format(repr(kind)))
        else:
            raise NotImplementedError(
                "format={:s} not yet implemented".format(repr(format)))

        for cls in self.__subclasses__():
            if cls.istype(kind):
                return cls(coeffs, normalization=normalization.lower(),
                           csphase=csphase)

    # ---- Extract data ----
    def get_degrees(self):
        """
        Return a numpy array with the harmonic degrees from 0 to lmax.

        Usage
        -----

        degrees = x.get_degrees()

        Returns
        -------

        degrees : numpy ndarray of size (lmax+1).
        """
        return _np.arange(self.lmax + 1)

    def get_powerperdegree(self):
        """
        Return a numpy array with the power per degree l spectrum.

        Usage
        -----

        power = x.get_powerperdegree()

        Returns
        -------

        power : numpy ndarray of size (lmax+1).
        """
        return self._powerperdegree()

    def get_powerperband(self, bandwidth):
        """
        Return the power per log_{bandwidth}(degree) spectrum.

        Usage
        -----

        power = x.get_powerperband()

        Returns
        -------

        power : numpy ndarray of size (lmax+1).
        """
        ls = self.get_degrees()
        return self._powerperdegree() * ls * _np.log(bandwidth)

    # ---- Set individual coefficient
    def set_coeffs(self, values, ls, ms):
        """
        Set coefficients in-place to specified values.

        Usage
        -----

        x.set_coeffs(values, ls, ms)

        Parameters
        ----------

        values : one or several coefficient values
        ls: the degree/s of the coefficients that should be set
        ms: the order/s of the coefficients that should be set
        """
        # make sure that the type is correct
        values = _np.array(values)
        ls = _np.array(ls)
        ms = _np.array(ms)

        mneg_mask = (ms < 0).astype(_np.int)
        self.coeffs[mneg_mask, ls, _np.abs(ms)] = values

    # ---- Return coefficients with a different normalization convention ----
    def get_coeffs(self, normalization='4pi', csphase=1, lmax=None):
        """
        Return spherical harmonics coefficients as a numpy array.

        Usage
        -----

        coeffs = x.get_coeffs([normalization, csphase, lmax])

        Returns
        -------

        coeffs : numpy ndarray of size (2, lmax + 1, lmax + 1).

        Parameters
        ----------

        normalization : Normalization of the output coefficients:
                        '4pi' (default), 'ortho' or 'schmidt' for geodesy 4pi
                        normalized, orthonormalized, or Schmidt semi-normalized
                        coefficients, respectively.
        csphase       : Output Condon-Shortley phase convention: 1 (default)
                        to exlcude the phase factor, or -1 to include it.
        lmax          : Maximum spherical harmonic degree to output.
                        Default is x.lmax.
        """
        if type(normalization) != str:
            raise ValueError('normalization must be a string. ' +
                             'Input type was {:s}'
                             .format(str(type(normalization))))

        if normalization.lower() not in set(['4pi', 'ortho', 'schmidt']):
            raise ValueError(
                "normalization must be '4pi', 'ortho' " +
                "or 'schmidt'. Provided value was {:s}"
                .format(repr(normalization))
                )
        if csphase != 1 and csphase != -1:
            raise ValueError(
                "csphase must be 1 or -1. Input value was {:s}"
                .format(repr(csphase))
                )

        if lmax is not None:
            if lmax > self.lmax:
                raise ValueError('Output lmax is greater than the maximum ' +
                                 'degree of the coefficients. ' +
                                 'Output lmax = {:d}, lmax of coefficients ' +
                                 '= {:d}'.format(lmax, self.lmax))
        if lmax is None:
            lmax = self.lmax

        return self._get_coeffs(
            output_normalization=normalization.lower(),
            output_csphase=csphase, lmax=lmax)

    # ---- Rotate the coordinate system ----
    def rotate(self, alpha, beta, gamma, degrees=True, dj_matrix=None):
        """
        Rotate the coordinate return rotated Coefficient class.

        Usage
        -----

        SHCoeffsInstance = x.rotate(alpha, beta, gamma, [degrees, dj_matrix])

        Parameters
        ----------

        alpha, beta, gamma : The three Euler rotation angles in degrees.
        degrees            : True (default) if the Euler angles are in degrees,
                             False if they are in radians.
        dj_matrix          : The djpi2 rotation matrix (default=None), computed
                             by a call to djpi2.

        Description
        -----------
        This method will take the spherical harmonic coefficients of a
        function, rotate the coordinate frame by the three Euler anlges, and
        output the spherical harmonic coefficients of the rotated function.

        The rotation of a coordinate system or body can be viewed in two
        complementary ways involving three successive rotations. Both methods
        have the same initial and final configurations, and the angles listed
        in both schemes are the same.

        Scheme A:

        (I) Rotation about the z axis by alpha.
        (II) Rotation about the new y axis by beta.
        (III) Rotation about the new z axis by gamma.

        Scheme B:

        (I) Rotation about the z axis by gamma.
        (II) Rotation about the initial y axis by beta.
        (III) Rotation about the initial z axis by alpha.

        The rotations can further be viewed either as a rotation of the
        coordinate system or the physical body. For a rotation of the
        coordinate system without rotation of the physical body, use

        (alpha, beta, gamma).

        For a rotation of the physical body without rotation of the coordinate
        system, use

        (-gamma, -beta, -alpha).

        To perform the inverse transform of (alpha, beta, gamma), use

        (-gamma, -beta, -alpha).

        Note that this routine uses the "y convention", where the second
        rotation is with respect to the new y axis. If alpha, beta, and gamma
        were orginally defined in terms of the "x convention", where the second
        rotation was with respect to the new x axis, the Euler angles according
        to the y convention would be

        alpha_y=alpha_x-pi/2, beta_x=beta_y, and gamma_y=gamma_x+pi/2.
        """
        if degrees:
            angles = _np.radians([alpha, beta, gamma])
        else:
            angles = _np.array([alpha, beta, gamma])

        rot = self._rotate(angles, dj_matrix)
        return rot

    # ---- Convert spherical harmonic coefficients to a different normalization
    def return_coeffs(self, normalization='4pi', csphase=1, lmax=None):
        """
        Return a class instance with a different normalization convention.

        Usage
        -----

        SHCoeffsInstance = x.return_coeffs([normalization, csphase, lmax])

        Parameters
        ----------

        normalization : Normalization of the output class: '4pi' (default),
                        'ortho' or 'schmidt' for geodesy 4pi normalized,
                        orthonormalized, or Schmidt semi-normalized
                        coefficients, respectively.
        csphase       : Output Condon-Shortley phase convention: 1 (default)
                        to exlcude the phase factor, or -1 to include it.
        lmax          : Maximum spherical harmonic degree to output.
                        Default is x.lmax.
        """
        if type(normalization) != str:
            raise ValueError('normalization must be a string. ' +
                             'Input type was {:s}'
                             .format(str(type(normalization))))

        if normalization.lower() not in set(['4pi', 'ortho', 'schmidt']):
            raise ValueError(
                "normalization must be '4pi', 'ortho' " +
                "or 'schmidt'. Provided value was {:s}"
                .format(repr(normalization))
                )
        if csphase != 1 and csphase != -1:
            raise ValueError(
                "csphase must be 1 or -1. Input value was {:s}"
                .format(repr(csphase))
                )

        coeffs = self.get_coeffs(normalization=normalization.lower(),
                                 csphase=csphase, lmax=lmax)
        return SHCoeffs.from_array(coeffs,
                                   normalization=normalization.lower(),
                                   csphase=csphase)

    # ---- Expand the coefficients onto a grid ----
    def expand(self, grid='DH', **kwargs):
        """
        Evaluate the coefficients on a spherical grid.

        Usage
        -----

        SHGridInstance = x.expand([grid, lmax, lmax_calc, zeros])

        Parameters
        ----------

        grid      : 'DH' or 'DH1' for an equisampled lat/lon grid with
                    nlat=nlon, 'DH2' for an equidistant lat/lon grid with
                    nlon=2*nlat, or 'GLQ' for a Gauss-Legendre quadrature grid.
        lmax      : The maximum spherical harmonic degree, which determines the
                    grid spacing of the output grid. Default is x.lmax.
        lmax_calc : The maximum spherical harmonic degree to use when
                    evaluating the function. Default is x.lmax.
        zeros     : The cos(colatitude) nodes used in the Gauss-Legendre
                    Quadrature grids. Default is None.

        Description
        -----------

        For more information concerning the spherical harmonic expansions, and
        the properties of the output grids, see the documentation for
        SHExpandDH, SHExpandDHC, SHExpandGLQ and SHExpandGLQC.
        """
        if type(grid) != str:
            raise ValueError('grid must be a string. ' +
                             'Input type was {:s}'
                             .format(str(type(grid))))

        if grid.upper() == 'DH' or grid.upper() == 'DH1':
            gridout = self._expandDH(sampling=1, **kwargs)
        elif grid.upper() == 'DH2':
            gridout = self._expandDH(sampling=2, **kwargs)
        elif grid.upper() == 'GLQ':
            gridout = self._expandGLQ(zeros=None, **kwargs)
        else:
            raise ValueError(
                "grid must be 'DH', 'DH1', 'DH2', or 'GLQ'. " +
                "Input value was {:s}".format(repr(grid)))

        return gridout

    # ---- plotting routines ----
    def plot_powerperdegree(self, loglog=True, show=True, fname=None):
        """
        Plot the power per degree spectrum.

        Usage
        -----

        x.plot_powerperdegree([loglog, show, fname])

        Parameters
        ----------

        loglog : If True (default), use log-log axis.
        show   : If True (default), plot to the screen.
        fname  : If present, save the image to the file.
        """
        power = self.get_powerperdegree()
        ls = self.get_degrees()

        fig, ax = _plt.subplots(1, 1)
        ax.set_xlabel('degree l')
        ax.set_ylabel('power per degree')
        if loglog:
            ax.set_xscale('log')
            ax.set_yscale('log')
            ax.grid(True, which='both')
            ax.plot(ls[1:], power[1:], label='power per degree l')
        if show:
            _plt.show()
        if fname is not None:
            fig.savefig(fname)
        return fig, ax

    def plot_powerperband(self, bandwidth=2, show=True, fname=None):
        """
        Plot the power per log_{bandwidth}(degree) spectrum.

        Usage
        -----

        x.plot_powerperband([loglog, show, fname])

        Parameters
        ----------

        bandwidth : The bandwidth, default = 2.
        loglog    : If True (default), use log-log axis.
        show      : If True (default), plot to the screen.
        fname     : If present, save the image to the file
        """
        power = self.get_powerperband(bandwidth)
        ls = self.get_degrees()

        fig, ax = _plt.subplots(1, 1)
        ax.set_xlabel('degree l')
        ax.set_ylabel('bandpower')
        ax.set_xscale('log', basex=bandwidth)
        ax.set_yscale('log', basey=bandwidth)
        ax.grid(True, which='both')
        ax.plot(ls[1:], power[1:], label='power per degree l')
        fig.tight_layout(pad=0.1)
        if show:
            _plt.show()
        if fname is not None:
            fig.savefig(fname)
        return fig, ax

    def info(self):
        """
        Print a summary of the data stored in the SHCoeffs instance.

        Usage
        -----

        x.info()
        """
        print('kind = {:s}\nnormalization = {:s}\n'
              'csphase = {:d}\nlmax = {:d}'.format(
                  repr(self.kind), repr(self.normalization), self.csphase,
                  self.lmax))


# ================== REAL SPHERICAL HARMONICS ================

class SHRealCoeffs(SHCoeffs):
    """Real Spherical Harmonics Coefficient class."""

    @staticmethod
    def istype(kind):
        """Test if class is Real or Complex."""
        return kind == 'real'

    def __init__(self, coeffs, normalization='4pi', csphase=1):
        """Initialize Real SH Coefficients."""
        lmax = coeffs.shape[1] - 1
        # ---- create mask to filter out m<=l ----
        mask = _np.zeros((2, lmax + 1, lmax + 1), dtype=_np.bool)
        mask[0, 0, 0] = True
        for l in _np.arange(lmax + 1):
            mask[:, l, :l + 1] = True
        mask[1, :, 0] = False

        self.mask = mask
        self.lmax = lmax
        self.coeffs = _np.copy(coeffs)
        self.coeffs[_np.invert(mask)] = 0.
        self.kind = 'real'
        self.normalization = normalization
        self.csphase = csphase

    def make_complex(self):
        """
        Convert real to the complex coefficient class.

        Normalization and phase conventions are kept unchanged.

        Usage
        -----

        SHComplexCoeffsInstance = x.make_complex()
        """
        rcomplex_coeffs = _shtools.SHrtoc(self.coeffs,
                                          convention=1, switchcs=0)

        # These coefficients are using real floats, and need to be
        # converted to complex form.
        complex_coeffs = _np.zeros((2, self.lmax+1, self.lmax+1),
                                   dtype='complex')
        complex_coeffs[0, :, :] = (rcomplex_coeffs[0, :, :] + 1j *
                                   rcomplex_coeffs[1, :, :])
        complex_coeffs[1, :, :] = complex_coeffs[0, :, :].conjugate()
        for m in self.get_degrees():
            if m % 2 == 1:
                complex_coeffs[1, :, m] = - complex_coeffs[1, :, m]

        return SHCoeffs.from_array(complex_coeffs,
                                   normalization=self.normalization,
                                   csphase=self.csphase)

    def _powerperdegree(self):
        """Return the power per degree l spectrum."""
        if self.normalization == '4pi':
            return _shtools.SHPowerSpectrum(self.coeffs)
        elif self.normalization == 'schmidt':
            power = _shtools.SHPowerSpectrum(self.coeffs)
            l = self.get_degrees()
            power /= (2.0 * l + 1.0)
            return power
        elif self.normalization == 'ortho':
            return _shtools.SHPowerSpectrum(self.coeffs) / (4.0 * _np.pi)
        else:
            raise ValueError(
                "Normalization must be '4pi', 'ortho', or 'schmidt'. " +
                "Input value was {:s}".format(repr(self.normalization)))

    def _get_coeffs(self, output_normalization, output_csphase, lmax):
        """Return coefficients with a different normalization convention."""
        coeffs = _np.copy(self.coeffs[:, :lmax+1, :lmax+1])
        degrees = _np.arange(lmax + 1)

        if self.normalization == output_normalization:
            pass
        elif (self.normalization == '4pi' and
              output_normalization == 'schmidt'):
            for l in degrees:
                coeffs[:, l, :l+1] *= _np.sqrt(2.0 * l + 1.0)
        elif self.normalization == '4pi' and output_normalization == 'ortho':
            coeffs *= _np.sqrt(4.0 * _np.pi)
        elif (self.normalization == 'schmidt' and
              output_normalization == '4pi'):
            for l in degrees:
                coeffs[:, l, :l+1] /= _np.sqrt(2.0 * l + 1.0)
        elif (self.normalization == 'schmidt' and
              output_normalization == 'ortho'):
            for l in degrees:
                coeffs[:, l, :l+1] *= _np.sqrt(4.0 * _np.pi / (2.0 * l + 1.0))
        elif self.normalization == 'ortho' and output_normalization == '4pi':
            coeffs /= _np.sqrt(4.0 * _np.pi)
        elif (self.normalization == 'ortho' and
              output_normalization == 'schmidt'):
            for l in degrees:
                coeffs[:, l, :l+1] *= _np.sqrt((2.0 * l + 1.0) /
                                               (4.0 * _np.pi))

        if output_csphase != self.csphase:
            for m in degrees:
                if m % 2 == 1:
                    coeffs[:, :, m] = - coeffs[:, :, m]

        return coeffs

    def _rotate(self, angles, dj_matrix):
        """Rotate the coefficients by the Euler angles alpha, beta, gamma."""
        if dj_matrix is None:
            dj_matrix = _shtools.djpi2(self.lmax + 1)

        # The coefficients need to be 4pi normalized with csphase = 1
        coeffs = _shtools.SHRotateRealCoef(
            self.get_coeffs(normalization='4pi', csphase=1), angles, dj_matrix)

        # Convert 4pi normalized coefficients to the same normalization
        # as the unrotated coefficients.
        if self.normalization != '4pi' or self.csphase != 1:
            temp = SHCoeffs.from_array(coeffs, kind='real')
            tempcoeffs = temp.get_coeffs(
                normalization=self.normalization, csphase=self.csphase)
            return SHCoeffs.from_array(
                tempcoeffs, normalization=self.normalization,
                csphase=self.csphase)
        else:
            return SHCoeffs.from_array(coeffs)

    def _expandDH(self, sampling, **kwargs):
        """Evaluate the coefficients on a Driscoll and Healy (1994) grid."""
        if self.normalization == '4pi':
            norm = 1
        elif self.normalization == 'schmidt':
            norm = 2
        elif self.normalization == 'ortho':
            norm = 4
        else:
            raise ValueError(
                "Normalization must be '4pi', 'ortho', or 'schmidt'. " +
                "Input value was {:s}".format(repr(self.normalization)))

        data = _shtools.MakeGridDH(self.coeffs, sampling=sampling, norm=norm,
                                   csphase=self.csphase, **kwargs)
        gridout = SHGrid.from_array(data, grid='DH')
        return gridout

    def _expandGLQ(self, zeros, **kwargs):
        """Evaluate the coefficients on a Gauss Legendre quadrature grid."""
        if self.normalization == '4pi':
            norm = 1
        elif self.normalization == 'schmidt':
            norm = 2
        elif self.normalization == 'ortho':
            norm = 4
        else:
            raise ValueError(
                "Normalization must be '4pi', 'ortho', or 'schmidt'. " +
                "Input value was {:s}".format(repr(self.normalization)))

        if zeros is None:
            zeros, weights = _shtools.SHGLQ(self.lmax)

        data = _shtools.MakeGridGLQ(self.coeffs, zeros, norm=norm,
                                    csphase=self.csphase, **kwargs)
        gridout = SHGrid.from_array(data, grid='GLQ')
        return gridout


# =============== COMPLEX SPHERICAL HARMONICS ================

class SHComplexCoeffs(SHCoeffs):
    """Complex Spherical Harmonics Coefficients class."""

    @staticmethod
    def istype(kind):
        """Check if class has kind 'real' or 'complex'."""
        return kind == 'complex'

    def __init__(self, coeffs, normalization='4pi', csphase=1):
        """Initialize Complex coefficients."""
        lmax = coeffs.shape[1] - 1
        # ---- create mask to filter out m<=l ----
        mask = _np.zeros((2, lmax + 1, lmax + 1), dtype=_np.bool)
        mask[0, 0, 0] = True
        for l in _np.arange(lmax + 1):
            mask[:, l, :l + 1] = True
        mask[1, :, 0] = False

        self.mask = mask
        self.lmax = lmax
        self.coeffs = _np.copy(coeffs)
        self.coeffs[_np.invert(mask)] = 0.
        self.kind = 'complex'
        self.normalization = normalization
        self.csphase = csphase

    def make_real(self):
        """
        Convert the complex to the real harmonic coefficient class.

        Usage
        -----

        SHRealCoeffsInstance = x.make_real()
        """
        # First test if the coefficients correspond to a real grid.
        # This is not very elegant. Also, the equality condition
        # is probably not robust to round off errors.
        for l in self.get_degrees():
            if self.coeffs[0, l, 0] != self.coeffs[0, l, 0].conjugate():
                raise RuntimeError('Complex coefficients do not correspond ' +
                                   'to a real field. l = {:d}, m = 0: {:e}'
                                   .format(l, self.coeffs[0, l, 0]))

            for m in _np.arange(1, l + 1):
                if m % 2 == 1:
                    if (self.coeffs[0, l, m] != -
                            self.coeffs[1, l, m].conjugate()):
                        raise RuntimeError('Complex coefficients do not ' +
                                           'correspond to a real field. ' +
                                           'l = {:d}, m = {:d}: {:e}, {:e}'
                                           .format(l, m, self.coeffs[0, l, 0],
                                                   self.coeffs[1, l, 0]))
                else:
                    if (self.coeffs[0, l, m] !=
                            self.coeffs[1, l, m].conjugate()):
                        raise RuntimeError('Complex coefficients do not ' +
                                           'correspond to a real field. ' +
                                           'l = {:d}, m = {:d}: {:e}, {:e}'
                                           .format(l, m, self.coeffs[0, l, 0],
                                                   self.coeffs[1, l, 0]))

        coeffs_rc = _np.zeros((2, self.lmax + 1, self.lmax + 1))
        coeffs_rc[0, :, :] = self.coeffs[0, :, :].real
        coeffs_rc[1, :, :] = self.coeffs[0, :, :].imag
        real_coeffs = _shtools.SHctor(coeffs_rc, convention=1,
                                      switchcs=0)
        return SHCoeffs.from_array(real_coeffs,
                                   normalization=self.normalization,
                                   csphase=self.csphase)

    def _powerperdegree(self):
        """Return the power per degree l spectrum."""
        if self.normalization == '4pi':
            return _shtools.SHPowerSpectrumC(self.coeffs)
        elif self.normalization == 'schmidt':
            power = _shtools.SHPowerSpectrumC(self.coeffs)
            l = self.get_degrees()
            power /= (2.0 * l + 1.0)
            return power
        elif self.normalization == 'ortho':
            return _shtools.SHPowerSpectrumC(self.coeffs) / (4.0 * _np.pi)
        else:
            raise ValueError(
                "Normalization must be '4pi', 'ortho', or 'schmidt'. " +
                "Input value was {:s}".format(repr(self.normalization)))

    def _get_coeffs(self, output_normalization, output_csphase, lmax):
        """Return coefficients with a different normalization convention."""
        coeffs = _np.copy(self.coeffs[:, :lmax+1, :lmax+1])
        degrees = _np.arange(lmax + 1)

        if self.normalization == output_normalization:
            pass
        elif (self.normalization == '4pi' and
              output_normalization == 'schmidt'):
            for l in degrees:
                coeffs[:, l, :l+1] *= _np.sqrt(2.0 * l + 1.0)
        elif self.normalization == '4pi' and output_normalization == 'ortho':
            coeffs *= _np.sqrt(4.0 * _np.pi)
        elif (self.normalization == 'schmidt' and
              output_normalization == '4pi'):
            for l in degrees:
                coeffs[:, l, :l+1] /= _np.sqrt(2.0 * l + 1.0)
        elif (self.normalization == 'schmidt' and
              output_normalization == 'ortho'):
            for l in degrees:
                coeffs[:, l, :l+1] *= _np.sqrt(4.0 * _np.pi / (2.0 * l + 1.0))
        elif self.normalization == 'ortho' and output_normalization == '4pi':
            coeffs /= _np.sqrt(4.0 * _np.pi)
        elif (self.normalization == 'ortho' and
              output_normalization == 'schmidt'):
            for l in degrees:
                coeffs[:, l, :l+1] *= _np.sqrt((2.0 * l + 1.0) /
                                               (4.0 * _np.pi))

        if output_csphase != self.csphase:
            for m in degrees:
                if m % 2 == 1:
                    coeffs[:, :, m] = - coeffs[:, :, m]

        return coeffs

    def _rotate(self, angles, dj_matrix):
        """Rotate the coefficients by the Euler angles alpha, beta, gamma."""
        # Note that the current method is EXTREMELY inefficient. The complex
        # coefficients are expanded onto real and imaginary grids, each of
        # the two components are rotated separately as real data, they rotated
        # real data are re-expanded on new real and complex grids, they are
        # combined to make a complex grid, and the resultant is expanded
        # in complex spherical harmonics.
        if dj_matrix is None:
            dj_matrix = _shtools.djpi2(self.lmax + 1)

        cgrid = self.expand(grid='DH')
        rgrid, igrid = cgrid.data.real, cgrid.data.imag
        rgridcoeffs = _shtools.SHExpandDH(rgrid, norm=1, sampling=1, csphase=1)
        igridcoeffs = _shtools.SHExpandDH(igrid, norm=1, sampling=1, csphase=1)

        rgridcoeffs_rot = _shtools.SHRotateRealCoef(
            rgridcoeffs, angles, dj_matrix)
        igridcoeffs_rot = _shtools.SHRotateRealCoef(
            igridcoeffs, angles, dj_matrix)

        rgrid_rot = _shtools.MakeGridDH(rgridcoeffs_rot, norm=1,
                                        sampling=1, csphase=1)
        igrid_rot = _shtools.MakeGridDH(igridcoeffs_rot, norm=1,
                                        sampling=1, csphase=1)
        grid_rot = rgrid_rot + 1j * igrid_rot

        if self.normalization == '4pi':
            norm = 1
        elif self.normalization == 'schmidt':
            norm = 2
        elif self.normalization == 'ortho':
            norm = 4
        else:
            raise ValueError(
                "Normalization must be '4pi', 'ortho', or 'schmidt'")

        coeffs_rot = _shtools.SHExpandDHC(grid_rot, norm=norm,
                                          csphase=self.csphase)

        return SHCoeffs.from_array(coeffs_rot,
                                   normalization=self.normalization,
                                   csphase=self.csphase)

    def _expandDH(self, sampling, **kwargs):
        """Evaluate the coefficients on a Driscoll and Healy (1994) grid."""
        if self.normalization == '4pi':
            norm = 1
        elif self.normalization == 'schmidt':
            norm = 2
        elif self.normalization == 'ortho':
            norm = 4
        else:
            raise ValueError(
                "Normalization must be '4pi', 'ortho', or 'schmidt'. " +
                "Input value was {:s}".format(repr(self.normalization)))

        data = _shtools.MakeGridDHC(self.coeffs, sampling=sampling,
                                    norm=norm, csphase=self.csphase, **kwargs)
        gridout = SHGrid.from_array(data, grid='DH')
        return gridout

    def _expandGLQ(self, zeros, **kwargs):
        """Evaluate the coefficients on a Gauss-Legendre quadrature grid."""
        if self.normalization == '4pi':
            norm = 1
        elif self.normalization == 'schmidt':
            norm = 2
        elif self.normalization == 'ortho':
            norm = 4
        else:
            raise ValueError(
                "Normalization must be '4pi', 'ortho', or 'schmidt'. " +
                "Input value was {:s}".format(repr(self.normalization)))

        if zeros is None:
            zeros, weights = _shtools.SHGLQ(self.lmax)

        data = _shtools.MakeGridGLQC(self.coeffs, zeros, norm=norm,
                                     csphase=self.csphase, **kwargs)
        gridout = SHGrid.from_array(data, grid='GLQ')
        return gridout


# ========================================================================
# ======      GRID CLASSES      ==========================================
# ========================================================================

class SHGrid(object):
    """
    Class for spatial gridded data on the sphere.

    Grids can be initialized from:

    >>> x = SHGrid.from_array(array)
    >>> x = SHGrid.from_file('fname.dat')

    The class instance defines the following class attributes:

    data       : Gridded array of the data.
    nlat, nlon : The number of latitude and longitude bands in the grid.
    lmax       : The maximum spherical harmonic degree that can be resolved
                 by the grid sampling.
    sampling   : For Driscoll and Healy grids, the longitudinal sampling
                 of the grid. Either nlong = nlat or nlong = 2 * nlat.
    kind       : Either 'complex' or 'real' for the data type.
    grid       : Either 'DH' or 'GLQ' for Driscoll and Healy grids or Gauss-
                 Legendre Quadrature grids.
    zeros      : The cos(colatitude) nodes used with Gauss-Legendre
                 Quadrature grids. Default is None.
    weights    : The latitudinal weights used with Gauss-Legendre
                 Quadrature grids. Default is None.

    Each class instance provides the following methods:

    get_lats()     : Return a vector containing the latitudes of each row
                     of the gridded data.
    get_lons()     : Return a vector containing the longitudes of each column
                     of the gridded data.
    expand()       : Expand the grid into spherical harmonics.
    plot_rawdata() : Plot the raw data using a simple cylindrical projection.
    info()         : Print a summary of the data stored in the SHGrid
                     instance.
    """

    def __init__():
        """Use a constructor to intialize."""
        pass

    # ---- factory methods
    @classmethod
    def from_array(self, array, grid='DH'):
        """
        Initialize the grid of the class instance from an input array.

        Usage
        -----

        x = SHGrid.from_array(array, [grid])

        Parameters
        ----------

        array : numpy array of size (nlat, nlon)
        grid : 'DH' (default) or 'GLQ' for Driscoll and Healy grids or Gauss
                Legendre Quadrature grids, respectively.
        """
        if _np.iscomplexobj(array):
            kind = 'complex'
        else:
            kind = 'real'

        if type(grid) != str:
            raise ValueError('grid must be a string. ' +
                             'Input type was {:s}'
                             .format(str(type(grid))))

        if grid.upper() not in set(['DH', 'GLQ']):
            raise ValueError(
                "grid must be 'DH' or 'GLQ'. Input value was {:s}."
                .format(repr(grid))
                )

        for cls in self.__subclasses__():
            if cls.istype(kind) and cls.isgrid(grid):
                return cls(array)

    @classmethod
    def from_file(self, fname, kind='real', grid='DH'):
        """Initialize the grid of the object from a file."""
        raise NotImplementedError('Not implemented yet')

    # ---- operators ----
    def __add__(self, grid):
        """Add two similar grids."""
        if self.grid == grid.grid and self.data.shape == grid.data.shape:
            data = self.data + grid.data
            return SHGrid.from_array(data, grid=self.grid)

    def __mul__(self, grid):
        """Multiply two similar grids."""
        if self.grid == grid.grid and self.data.shape == grid.data.shape:
            data = self.data * grid.data
            return SHGrid.from_array(data, grid=self.grid)

    def __sub__(self, grid):
        """Subtract two similar grids."""
        if self.grid == grid.grid and self.data.shape == grid.data.shape:
            data = self.data * grid.data
            return SHGrid.from_array(data, grid=self.grid)

    # ---- Extract grid properties ----
    def get_lats(self):
        """
        Return the latitudes (in degrees) of each row of the gridded data.

        Usage
        -----

        lats = x.get_lats()

        Returns
        -------

        lats : numpy array of size nlat containing the latitude (in degrees)
               of each row of the gridded data.
        """
        return self._get_lats()

    def get_lons(self):
        """
        Return the longitudes (in degrees) of each column of the gridded data.

        Usage
        -----

        lons = x.get_lon()

        Returns
        -------

        lons : numpy array of size nlon containing the longitude (in degrees)
               of each column of the gridded data.
        """
        return self._get_lons()

    # ---- Plotting routines ----
    def plot_rawdata(self, show=True, fname=None):
        """
        Plot the raw data using a simple cylindrical projection.

        Usage
        -----

        x.plot_rawdata([show, fname])

        Parameters
        ----------

        show   : If True (default), plot the image to the screen.
        fname  : If present, save the image to the file.
        """
        fig, ax = self._plot_rawdata()
        if show:
            _plt.show()
        if fname is not None:
            fig.savefig(fname)

    def expand(self, normalization='4pi', csphase=1, **kwargs):
        """
        Expand the grid into spherical harmonics.

        Usage
        -----

        SHCoeffsInstance = x.expand([normalization, csphase, lmax_calc])

        Parameters
        ----------

        normalization : '4pi' (default), geodesy 4-pi normalized
                      : 'ortho', orthonormalized
                      : 'schmidt', Schmidt semi-normalized)
        csphase       : 1  (default), exlcude the Condon-Shortley phase factor
        lmax_calc     : maximum spherical harmonic degree to return.
                        Default is x.lmax.
        """
        if type(normalization) != str:
            raise ValueError('normalization must be a string. ' +
                             'Input type was {:s}'
                             .format(str(type(normalization))))

        if normalization.lower() not in set(['4pi', 'ortho', 'schmidt']):
            raise ValueError(
                "The normalization must be '4pi', 'ortho' " +
                "or 'schmidt'. Input value was {:s}."
                .format(repr(normalization))
                )

        if csphase != 1 and csphase != -1:
            raise ValueError(
                "csphase must be either 1 or -1. Input value was {:s}."
                .format(repr(csphase))
                )

        return self._expand(normalization=normalization, csphase=csphase,
                            **kwargs)

    def info(self):
        """
        Print a summary of the data stored in the SHGrid instance.

        Usage
        -----

        x.info()
        """
        print('kind = {:s}\ngrid = {:s}\n'.format(repr(self.kind),
                                                  repr(self.grid)), end='')
        if self.grid == 'DH':
            print('sampling = {:d}\n'.format(self.sampling), end='')
        print('nlat = {:d}\nnlon = {:d}\nlmax = {:d}'.format(self.nlat,
                                                             self.nlon,
                                                             self.lmax))


# ---- Real Driscoll and Healy grid class ----

class DHRealGrid(SHGrid):
    """Class for real Driscoll and Healy (1994) grids."""

    @staticmethod
    def istype(kind):
        return kind == 'real'

    @staticmethod
    def isgrid(grid):
        return grid == 'DH'

    def __init__(self, array):
        self.nlat, self.nlon = array.shape

        if self.nlat % 2 != 0:
            raise ValueError('Input arrays for DH grids must have an even ' +
                             'number of latitudes: nlat = {:d}'
                             .format(self.nlat)
                             )
        if self.nlon == 2 * self.nlat:
            self.sampling = 2
        elif self.nlat == self.nlon:
            self.sampling = 1
        else:
            raise ValueError('Input array has shape (nlat={:d},nlon={:d})\n'
                             .format(self.nlat, self.nlon) +
                             'but needs nlat=nlon or nlat=2*nlon'
                             )

        self.lmax = int(self.nlat / 2 - 1)
        self.data = array
        self.grid = 'DH'
        self.kind = 'real'

    def _get_lats(self):
        """Return the latitudes (in degrees) of the gridded data."""
        lats = _np.linspace(90.0, -90.0 + 180.0 / self.nlat, num=self.nlat)
        return lats

    def _get_lons(self):
        """Return the longitudes (in degrees) of the gridded data."""
        lons = _np.linspace(0.0, 360.0 - 360.0 / self.nlon, num=self.nlon)
        return lons

    def _expand(self, normalization, csphase, **kwargs):
        """Expand the grid into real spherical harmonics."""
        if normalization.lower() == '4pi':
            norm = 1
        elif normalization.lower() == 'schmidt':
            norm = 2
        elif normalization.lower() == 'ortho':
            norm = 4
        else:
            raise ValueError(
                "The normalization must be '4pi', 'ortho' " +
                "or 'schmidt'. Input value was {:s}."
                .format(repr(normalization))
                )

        cilm = _shtools.SHExpandDH(self.data, norm=norm, csphase=csphase,
                                   sampling=self.sampling,
                                   **kwargs)
        coeffs = SHCoeffs.from_array(cilm,
                                     normalization=normalization.lower(),
                                     csphase=csphase)
        return coeffs

    def _plot_rawdata(self):
        """Plot the raw data using a simply cylindrical projection."""
        fig, ax = _plt.subplots(1, 1)
        ax.imshow(self.data, origin='upper', extent=(0., 360., -90., 90.))
        ax.set_title('Driscoll and Healy Grid')
        ax.set_xlabel('longitude')
        ax.set_ylabel('latitude')
        fig.tight_layout(pad=0.5)
        return fig, ax


# ---- Complex Driscoll and Healy grid class ----
class DHComplexGrid(SHGrid):
    """
    Class for complex Driscoll and Healy (1994) grids.
    """
    @staticmethod
    def istype(kind):
        return kind == 'complex'

    @staticmethod
    def isgrid(grid):
        return grid == 'DH'

    def __init__(self, array):
        self.nlat, self.nlon = array.shape

        if self.nlat % 2 != 0:
            raise ValueError('Input arrays for DH grids must have an even ' +
                             'number of latitudes: nlat = {:d}'
                             .format(self.nlat)
                             )
        if self.nlon == 2 * self.nlat:
            self.sampling = 2
        elif self.nlat == self.nlon:
            self.sampling = 1
        else:
            raise ValueError('Input array has shape (nlat={:d},nlon={:d})\n' +
                             'but needs nlat=nlon or nlat=2*nlon'
                             .format(self.nlat, self.nlon)
                             )

        self.lmax = int(self.nlat / 2 - 1)
        self.data = array
        self.grid = 'DH'
        self.kind = 'complex'

    def _get_lats(self):
        """
        Return a vector containing the latitudes (in degrees) of each row
        of the gridded data.
        """
        lats = _np.linspace(90.0, -90.0 + 180.0 / self.nlat, num=self.nlat)
        return lats

    def _get_lons(self):
        """
        Return a vector containing the longitudes (in degrees) of each row
        of the gridded data.
        """
        lons = _np.linspace(0., 360.0 - 360.0 / self.nlon, num=self.nlon)
        return lons

    def _expand(self, normalization, csphase, **kwargs):
        """Expand the grid into real spherical harmonics."""
        if normalization.lower() == '4pi':
            norm = 1
        elif normalization.lower() == 'schmidt':
            norm = 2
        elif normalization.lower() == 'ortho':
            norm = 4
        else:
            raise ValueError(
                "The normalization must be '4pi', 'ortho' " +
                "or 'schmidt'. Input value was {:s}."
                .format(repr(normalization))
                )

        cilm = _shtools.SHExpandDHC(self.data, norm=norm, csphase=csphase,
                                    **kwargs)
        coeffs = SHCoeffs.from_array(cilm,
                                     normalization=normalization.lower(),
                                     csphase=csphase)
        return coeffs

    def _plot_rawdata(self):
        """Plot the raw data using a simply cylindrical projection."""
        fig, ax = _plt.subplots(2, 1)
        ax.flat[0].imshow(self.data.real, origin='upper',
                          extent=(0., 360., -90., 90.))
        ax.flat[0].set_title('Driscoll and Healy Grid (real component)')
        ax.flat[0].set_xlabel('longitude')
        ax.flat[0].set_ylabel('latitude')
        ax.flat[1].imshow(self.data.imag, origin='upper',
                          extent=(0., 360., -90., 90.))
        ax.flat[1].set_title('Driscoll and Healy Grid (imaginary component)')
        ax.flat[1].set_xlabel('longitude')
        ax.flat[1].set_ylabel('latitude')
        fig.tight_layout(pad=0.5)
        return fig, ax


# ---- Real Gaus Legendre Quadrature grid class ----

class GLQRealGrid(SHGrid):
    """
    Class for real Gauss-Legendre Quadrature grids.
    """
    @staticmethod
    def istype(kind):
        return kind == 'real'

    @staticmethod
    def isgrid(grid):
        return grid == 'GLQ'

    def __init__(self, array, zeros=None, weights=None):
        self.nlat, self.nlon = array.shape
        self.lmax = self.nlat - 1

        if self.nlat != self.lmax + 1 or self.nlon != 2 * self.lmax + 1:
            raise ValueError('Input array has shape (nlat={:d}, nlon={:d})\n' +
                             'but needs (nlat={:d}, {:d})'
                             .format(self.nlat, self.nlon, self.lmax+1,
                                     2*self.lmax+1)
                             )

        if zeros is None or weights is None:
            self.zeros, self.weights = _shtools.SHGLQ(self.lmax)
        else:
            self.zeros = zeros
            self.weights = weights

        self.data = array
        self.grid = 'GLQ'
        self.kind = 'real'

    def _get_lats(self):
        """
        Return a vector containing the latitudes (in degrees) of each row
        of the gridded data.
        """
        lats = 90. - _np.arccos(self.zeros) * 180. / _np.pi
        return lats

    def _get_lons(self):
        """
        Return a vector containing the longitudes (in degrees) of each column
        of the gridded data.
        """
        lons = _np.linspace(0.0, 360.0 - 360.0 / self.nlon, num=self.nlon)
        return lons

    def _expand(self, normalization, csphase, **kwargs):
        """Expand the grid into real spherical harmonics."""
        if normalization.lower() == '4pi':
            norm = 1
        elif normalization.lower() == 'schmidt':
            norm = 2
        elif normalization.lower() == 'ortho':
            norm = 4
        else:
            raise ValueError(
                "The normalization must be '4pi', 'ortho' " +
                "or 'schmidt'. Input value was {:s}."
                .format(repr(normalization))
                )

        cilm = _shtools.SHExpandGLQ(self.data, self.weights, self.zeros,
                                    norm=norm, csphase=csphase, **kwargs)
        coeffs = SHCoeffs.from_array(cilm,
                                     normalization=normalization.lower(),
                                     csphase=csphase)
        return coeffs

    def _plot_rawdata(self):
        """Plot the raw data using a simply cylindrical projection."""

        fig, ax = _plt.subplots(1, 1)
        ax.imshow(self.data, origin='upper')
        ax.set_title('Gauss-Legendre Quadrature Grid')
        ax.set_xlabel('longitude index')
        ax.set_ylabel('latitude index')
        fig.tight_layout(pad=0.5)
        return fig, ax


# ---- Complex Gaus Legendre Quadrature grid class ----

class GLQComplexGrid(SHGrid):
    """
    Class for complex Gauss Legendre Quadrature grids.
    """
    @staticmethod
    def istype(kind):
        return kind == 'complex'

    @staticmethod
    def isgrid(grid):
        return grid == 'GLQ'

    def __init__(self, array, zeros=None, weights=None):
        self.nlat, self.nlon = array.shape
        self.lmax = self.nlat - 1

        if self.nlat != self.lmax + 1 or self.nlon != 2 * self.lmax + 1:
            raise ValueError('Input array has shape (nlat={:d}, nlon={:d})\n' +
                             'but needs (nlat={:d}, {:d})'
                             .format(self.nlat, self.nlon, self.lmax+1,
                                     2*self.lmax+1)
                             )

        if zeros is None or weights is None:
            self.zeros, self.weights = _shtools.SHGLQ(self.lmax)
        else:
            self.zeros = zeros
            self.weights = weights

        self.data = array
        self.grid = 'GLQ'
        self.kind = 'complex'

    def _get_lats(self):
        """
        Return a vector containing the latitudes (in degrees) of each row
        of the gridded data.
        """
        lats = 90. - _np.arccos(self.zeros) * 180. / _np.pi
        return lats

    def _get_lons(self):
        """
        Return a vector containing the longitudes (in degrees) of each column
        of the gridded data.
        """
        lons = _np.linspace(0., 360. - 360. / self.nlon, num=self.nlon)
        return lons

    def _expand(self, normalization, csphase, **kwargs):
        """Expand the grid into real spherical harmonics."""
        if normalization.lower() == '4pi':
            norm = 1
        elif normalization.lower() == 'schmidt':
            norm = 2
        elif normalization.lower() == 'ortho':
            norm = 4
        else:
            raise ValueError(
                "The normalization must be '4pi', 'ortho' " +
                "or 'schmidt'. Input value was {:s}."
                .format(repr(normalization))
                )

        cilm = _shtools.SHExpandGLQC(self.data, self.weights, self.zeros,
                                     norm=norm, csphase=csphase, **kwargs)
        coeffs = SHCoeffs.from_array(cilm,
                                     normalization=normalization.lower(),
                                     csphase=csphase)
        return coeffs

    def _plot_rawdata(self):
        """Plot the raw data using a simply cylindrical projection."""

        fig, ax = _plt.subplots(2, 1)
        ax.flat[0].imshow(self.data.real, origin='upper')
        ax.flat[0].set_title('Gauss-Legendre Quadrature Grid (real component)')
        ax.flat[0].set_xlabel('longitude index')
        ax.flat[0].set_ylabel('latitude index')
        ax.flat[1].imshow(self.data.imag, origin='upper')
        ax.flat[1].set_title('Gauss-Legendre Quadrature Grid ' +
                             '(imaginary component)')
        ax.flat[1].set_xlabel('longitude index')
        ax.flat[1].set_ylabel('latitude index')
        fig.tight_layout(pad=0.5)
        return fig, ax


# ========================================================================
# ======      SPHERICAL HARMONICS WINDOW FUNCTION CLASS      =============
# ========================================================================

class SHWindow(object):
    """
    Class for spatio-spectral localization windows developed in spherical
    harmonics. The windows can be initialized from:

    >>>  x = SHWindow.from_cap(theta, lmax, [clat, clon, nwin])
    >>>  x = SHWindow.from_mask(SHGrid)

    Each class instance defines the following class attributes:

    kind            : Either 'cap' or 'mask'.
    tapers          : Matrix containing the spherical harmonic coefficients
                      (in packed form) of either the unrotated spherical cap
                      localization windows or the localization windows
                      corresponding to the input mask.
    coeffs          : Array of spherical harmonic coefficients of the
                      rotated spherical cap localization windows. These are
                      '4pi' normalized and do not use the Condon-Shortley phase
                      factor.
    eigenvalues     : Concentration factors of the localization windows.
    orders          : The angular orders for each of the spherical cap
                      localization windows.
    weights         : Taper weights used with the multitaper spectral analyses.
                      Defaut is None.
    lmax            : Spherical harmonic bandwidth of the localization windows.
    theta           : Angular radius of the spherical cap localization domain
                      (default in degrees).
    theta_degrees   : True (default) if theta is in degrees.
    nwin            : Number of localization windows. Default is (lmax + 1)**2
    clat, clon      : Latitude and longitude of the center of the rotated
                      spherical cap localization windows (default in degrees).
    coord_degrees   : True (default) if clat and clon are in degrees.

    Each class instance provides the following methods:

    get_coeffs()          : Return an array of the spherical harmonic
                            coefficients for taper i, where i = 0 is the best
                            concentrated, optionally using a different
                            normalization convention.
    get_degrees()         : Return an array containing the spherical harmonic
                            degrees of the localization windows, from 0 to
                            lmax.
    get_powerperdegree()  : Return the power per degree spectra for one or more
                            of the localization windows.
    get_couplingmatrix()  : Return the coupling matrix of the first nwin
                            localization windows.
    get_grid()            : Return as an array a grid of taper i, where i = 0
                            is the best concentrated window.
    get_multitaperpowerspectrum()      : Return the multitaper power spectrum
                                         estimate and uncertainty for the input
                                         SHCoeffs class instance.
    get_multitapercrosspowerspectrum() : Return the multitaper cross-power
                                         spectrum estimate and uncertainty for
                                         two input SHCoeffs class instances.
    return_coeffs()       : Return the spherical harmonic coefficients of taper
                            i, where i = 0 is the best concentrated, as a new
                            SHCoeffs class instance, optionally using a
                            different normalization convention.
    return_grid()         : Return as a new SHGrid instance a grid of taper i,
                            where i = 0 is the best concentrated window.
    rotate()              : Rotate the spherical cap tapers, originally located
                            at the north pole, to clat and clon and save the
                            spherical harmonic coefficients in coeffs.
    plot_windows()        : Plot the best concentrated localization windows
                            using a simple cylindrical projection.
    plot_powerperdegree() : Plot the power spectra of the best concentrated
                            localization windows.
    plot_couplingmatrix() : Plot the multitaper coupling matrix.
    info()                : Print a summary of the data stored in the SHWindow
                            instance.
    """

    def __init__(self):
        """Initialize with a factory method."""
        pass

    # ---- factory methods:
    @classmethod
    def from_cap(self, theta, lmax, clat=None, clon=None, nwin=None,
                 theta_degrees=True, coord_degrees=True, dj_matrix=None,
                 weights=None):
        """
        Construct spherical cap localization windows.

        Usage
        -----

        x = SHWindow.from_cap(theta, lmax, [clat, clon, nwin, theta_degrees,
                                            coord_degrees, dj_matrix, weights])

        Parameters
        ----------

        theta          : Angular radius of the spherical cap localization
                         domain (default in degrees).
        lmax           : Spherical harmonic bandwidth of the localization
                         windows.
        clat, clon     : Latitude and longitude of the center of the rotated
                         spherical cap localization windows (default in
                         degrees).
        nwin           : Number of localization windows. Default = (lmax+1)**2
        theta_degrees  : True (default) if theta is in degrees.
        coord_degrees  : True (default) if clat and clon are in degrees.
        dj_matrix      : The djpi2 rotation matrix (default=None), computed
                         by a call to djpi2.
        weights        : Taper weights used with the multitaper spectral
                         analyses. Default is None.
        """

        if theta_degrees:
            tapers, eigenvalues, taper_order = _shtools.SHReturnTapers(
                theta, lmax)
        else:
            tapers, eigenvalues, taper_order = _shtools.SHReturnTapers(
                _np.radians(theta), lmax)

        return SHWindowCap(theta, tapers, eigenvalues, taper_order,
                           clat, clon, nwin, theta_degrees, coord_degrees,
                           dj_matrix, weights)

    @classmethod
    def from_mask(self, dh_mask, lmax, nwin=None, weights=None):
        """
        Construct localization windows that are optimally concentrated within
        the region specified by a mask.

        Usage
        -----

        x = SHWindow.from_mask(dh_mask, lmax, [nwin])

        Parameters
        ----------

        dh_mask  : A Driscoll and Healy (1994) sampled grid describing the
                   concentration region R. All elements should either be 1
                   (for inside the concentration region) or 0 (for outside the
                   concentration region). The grid must have dimensions
                   nlon = nlat or nlon = 2 * nlat, where nlat is even.
        lmax     : The spherical harmonic bandwidth of the localization
                   windows.
        nwin     : The number of best concentrated eigenvalues and
                   eigenfunctions to return. Default is (lmax + 1)**2.
        weights  : Taper weights used with the multitaper spectral analyses.
                   Default is None.
        """
        if nwin is None:
            nwin = (lmax + 1)**2
        else:
            if nwin > (lmax + 1)**2:
                raise ValueError('nwin must be less than or equal to ' +
                                 '(lmax + 1)**2. lmax = {:d} and nwin = {:d}'
                                 .format(lmax, nwin))

        if dh_mask.shape[0] % 2 != 0:
            raise ValueError('The number of latitude bands in dh_mask ' +
                             'must be even. nlat = {:d}'
                             .format(dh_mask.shape[0]))
        if (dh_mask.shape[1] != dh_mask.shape[0] and
                dh_mask.shape[1] != 2 * dh_mask.shape[0]):
            raise ValueError('dh_mask must be dimensioned as (n, n) or ' +
                             '(n, 2 * n). Input shape is ({:d}, {:d})'
                             .format(dh_mask.shape[0], dh_mask.shape[1]))

        tapers, eigenvalues = _shtools.SHReturnTapersMap(dh_mask, lmax,
                                                         ntapers=nwin)
        return SHWindowMask(tapers, eigenvalues, weights)

    def get_degrees(self):
        """
        Return a numpy array listing the spherical harmonic degrees of the
        localization windows from 0 to lmax.

        Usage
        -----

        degrees = x.get_degrees()

        Returns
        -------

        degrees : numpy ndarray of size (lmax+1).
        """
        return _np.arange(self.lmax + 1)

    def get_coeffs(self, itaper, normalization='4pi', csphase=1):
        """
        Return the spherical harmonics coefficients of taper i as a numpy
        array, where itaper = 0 is the best concentrated.

        Usage
        -----

        coeffs = x.get_coeffs(itaper, [normalization, csphase])

        Returns
        -------

        coeffs : numpy ndarray of size (2, lmax + 1, lmax + 1).

        Parameters
        ----------

        itaper        : Taper number, where itaper = 0 is the best
                        concentrated.
        normalization : Normalization of the output coefficients:
                        '4pi' (default), 'ortho' or 'schmidt' for geodesy 4pi
                        normalized, orthonormalized, or Schmidt semi-normalized
                        coefficients, respectively.
        csphase       : Output Condon-Shortley phase convention: 1 (default)
                        to exlcude the phase factor, or -1 to include it.
        """
        if type(normalization) != str:
            raise ValueError('normalization must be a string. ' +
                             'Input type was {:s}'
                             .format(str(type(normalization))))

        if normalization.lower() not in set(['4pi', 'ortho', 'schmidt']):
            raise ValueError(
                "normalization must be '4pi', 'ortho' " +
                "or 'schmidt'. Provided value was {:s}"
                .format(repr(output_normalization))
                )
        if csphase != 1 and csphase != -1:
            raise ValueError(
                "csphase must be 1 or -1. Input value was {:s}"
                .format(repr(csphase))
                )

        return self._get_coeffs(
            itaper, normalization=normalization.lower(), csphase=csphase)

    def get_grid(self, itaper, grid='DH2', zeros=None):
        """
        Evaluate the coefficients of taper i on a spherical grid, where i = 0
        is the best concentrated.

        Usage
        -----

        gridout = x.get_grid(itaper, [grid, zeros])

        Parameters
        ----------

        grid      : 'DH' or 'DH1' for an equisampled lat/lon grid with
                    nlat = nlon, 'DH2' for an equidistant lat/lon grid with
                    nlon = 2 * nlat, or 'GLQ' for a Gauss-Legendre quadrature
                    grid.
        zeros     : The cos(colatitude) nodes used in the Gauss-Legendre
                    Quadrature grids. Default is None.

        Description
        -----------

        For more information concerning the spherical harmonic expansions and
        the properties of the output grids, see the documentation for
        SHExpandDH and SHExpandGLQ.
        """
        if type(grid) != str:
            raise ValueError('grid must be a string. ' +
                             'Input type was {:s}'
                             .format(str(type(grid))))

        if grid.upper() == 'DH' or grid.upper() == 'DH1':
            gridout = _shtools.MakeGridDH(self.get_coeffs(itaper), sampling=1,
                                          norm=1, csphase=1)
        elif grid.upper() == 'DH2':
            gridout = _shtools.MakeGridDH(self.get_coeffs(itaper), sampling=2,
                                          norm=1, csphase=1)
        elif grid.upper() == 'GLQ':
            if zeros is None:
                zeros, weights = _shtools.SHGLQ(self.lmax)

            gridout = _shtools.MakeGridGLQ(self.get_coeffs(itaper), zeros,
                                           norm=1, csphase=1)
        else:
            raise ValueError(
                "grid must be 'DH', 'DH1', 'DH2', or 'GLQ'. " +
                "Input value was {:s}".format(repr(grid)))

        return gridout

    def return_coeffs(self, itaper, normalization='4pi', csphase=1):
        """
        Return the spherical harmonic coefficients of taper i, where itaper = 0
        is the best concentrated, as new SHCoeffs instance and with an
        optionally different normalization convention.

        Usage
        -----

        SHCoeffsInstance = x.return_coeffs(itaper, [normalization, csphase])

        Parameters
        ----------

        itaper        : Taper number, where itaper = 0 is the best
                        concentrated.
        normalization : Normalization of the output class: '4pi' (default),
                        'ortho' or 'schmidt' for geodesy 4pi-normalized,
                        orthonormalized, or Schmidt semi-normalized
                        coefficients, respectively.
        csphase       : Output Condon-Shortley phase convention: 1 (default)
                        to exlcude the phase factor, or -1 to include it.
        """
        if type(normalization) != str:
            raise ValueError('normalization must be a string. ' +
                             'Input type was {:s}'
                             .format(str(type(normalization))))

        if normalization.lower() not in set(['4pi', 'ortho', 'schmidt']):
            raise ValueError(
                "normalization must be '4pi', 'ortho' " +
                "or 'schmidt'. Provided value was {:s}"
                .format(repr(normalization))
                )
        if csphase != 1 and csphase != -1:
            raise ValueError(
                "csphase must be 1 or -1. Input value was {:s}"
                .format(repr(csphase))
                )

        coeffs = self.get_coeffs(itaper, normalization=normalization.lower(),
                                 csphase=csphase)
        return SHCoeffs.from_array(coeffs,
                                   normalization=normalization.lower(),
                                   csphase=csphase)

    def return_grid(self, itaper, grid='DH2', zeros=None):
        """
        Evaluate the coefficients of taper i on a spherical grid, where i = 0
        is the best concentrated, and return a new class instance of SHGrid.

        Usage
        -----

        SHGridInstance = x.return_grid(itaper, [grid, zeros])

        Parameters
        ----------

        grid      : 'DH' or 'DH1' for an equisampled lat/lon grid with
                    nlat = nlon, 'DH2' for an equidistant lat/lon grid with
                    nlon = 2 * nlat, or 'GLQ' for a Gauss-Legendre quadrature
                    grid.
        zeros     : The cos(colatitude) nodes used in the Gauss-Legendre
                    Quadrature grids. Default is None.

        Description
        -----------

        For more information concerning the spherical harmonic expansions and
        the properties of the output grids, see the documentation for
        SHExpandDH and SHExpandGLQ.
        """
        if type(grid) != str:
            raise ValueError('grid must be a string. ' +
                             'Input type was {:s}'
                             .format(str(type(grid))))

        if (grid.upper() == 'DH' or grid.upper() == 'DH1' or
                grid.upper() == 'DH2'):
            return SHGrid.from_array(self.get_grid(itaper, grid=grid.upper()),
                                     grid='DH')
        elif grid.upper() == 'GLQ':
            if zeros is None:
                zeros, weights = _shtools.SHGLQ(self.lmax)

            return SHGrid.from_array(self.get_grid(itaper, grid=grid.upper(),
                                                   zeros=zeros),
                                     grid='GLQ')
        else:
            raise ValueError(
                "grid must be 'DH', 'DH1', 'DH2', or 'GLQ'. " +
                "Input value was {:s}".format(repr(grid)))

        return gridout

    def get_multitaperpowerspectrum(self, clm, k, **kwargs):
        """"
        Return the multitaper power spectrum estimate and uncertainty for the
        input SHCoeffs class instance.

        Usage
        -----

        mtse, sd = x.get_multitaperpowerspectrum(clm, k, [lmax, taper_wt, clat,
                                                          clon, coord_degrees])

        Parameters
        ----------
        mtse          : The localized multitaper power spectrum estimate.
        sd            : The standard error of the localized multitaper power
                        spectral estimates.
        clm           : Input SHCoeffs class instance containing the spherical
                        harmonic coefficients of the global field to analyze.
        k             : The number of tapers to be utilized in performing the
                        multitaper spectral analysis.
        lmax          : The maximum spherical harmonic degree of clm to use.
                        Default is clm.lmax.
        taper_wt      : The weights used in calculating the multitaper spectral
                        estimates and standard error. Default is None.
        clat, clon    : Latitude and longitude of the center of the spherical-
                        cap localization windows. Default is the north pole.
        coord_degrees : True (default) if clat and clon are in degrees.
        """
        return self._get_multitaperpowerspectrum(clm, k, **kwargs)

    def get_multitapercrosspowerspectrum(self, clm, slm, k, **kwargs):
        """"
        Return the multitaper cross power spectrum estimate and uncertainty
        for two input SHCoeffs class instances.

        Usage
        -----

        mtse, sd = x.get_multitapercrosspowerspectrum(
                      clm, slm, k, [lmax, taper_wt, clat, clon, coord_degrees])

        Parameters
        ----------
        mtse          : The localized multitaper power spectrum estimate.
        sd            : The standard error of the localized multitaper power
                        spectral estimates.
        clm           : Input SHCoeffs class instance containing the spherical
                        harmonic coefficients of the first global field to
                        analyze.
        slm           : Input SHCoeffs class instance containing the spherical
                        harmonic coefficients of the second global field to
                        analyze.
        k             : The number of tapers to be utilized in performing the
                        multitaper spectral analysis.
        lmax          : The maximum spherical harmonic degree of clm to use.
                        Default is clm.lmax.
        taper_wt      : The weights used in calculating the multitaper spectral
                        estimates and standard error. Default is None.
        clat, clon    : Latitude and longitude of the center of the spherical-
                        cap localization windows. Default is the north pole.
        coord_degrees : True (default) if clat and clon are in degrees.
        """
        return self._get_multitapercrosspowerspectrum(clm, slm, k, **kwargs)

    def get_powerperdegree(self, itaper=None, nwin=None):
        """
        Return the power per degree spectra for one or more of the
        localization windows.

        Usage
        -----

        power = x.get_powerperdegree([itaper, nwin])

        Parameters
        ----------

        power   : A matrix with each column containing the power spectrum
                  of a localization window, and where the windows are arranged
                  with increasing concentration factors. If itaper is set,
                  only a single vector is returned, whereas if nwin is set, the
                  first nwin spectra are returned.
        itaper  : The taper number of the output power spectrum, where i = 0
                  corresponds to the best concentrated taper.
        nwin    : The number of best concentrated localization window power
                  spectra to return.
        """
        nl = self.tapers.shape[0]

        if itaper is None:
            if nwin is None:
                nwin = self.nwin
            power = _np.zeros((nl, nwin))

            for i in range(nwin):
                coeffs = self.get_coeffs(i)
                power[:, i] = _shtools.SHPowerSpectrum(coeffs)
        else:
            power = _np.zeros((nl))
            coeffs = self.get_coeffs(itaper)
            power = _shtools.SHPowerSpectrum(coeffs)

        return power

    def get_couplingmatrix(self, lmax, nwin=None, weights=None):
        """
        Return the coupling matrix of the first nwin tapers. This matrix
        relates the global power spectrum to the expectation of the localized
        multitaper spectrum.

        Usage
        -----

        Mmt = x.get_couplingmatrix(lmax, [nwin, weights])

        Parameters
        ----------

        lmax    : Spherical harmonic bandwidth of the global power spectrum.
        nwin    : Number of tapers used in the mutlitaper spectral analysis.
                  Default = x.nwin
        weights : Taper weights used with the multitaper spectral analyses.
                  Defaut is x.weights.
        """
        if weights is not None:
            if nwin is not None:
                if len(weights) != nwin:
                    raise ValueError(
                        'Length of weights must be equal to nwin. ' +
                        'len(weights) = {:d}, nwin = {:d}'.format(len(weights),
                                                                  nwin))
            else:
                if len(weights) != self.nwin:
                    raise ValueError(
                        'Length of weights must be equal to nwin. ' +
                        'len(weights) = {:d}, nwin = {:d}'.format(len(weights),
                                                                  self.nwin))

        return self._get_couplingmatrix(lmax, nwin=nwin, weights=weights)

    def plot_windows(self, nwin, show=True, fname=None):
        """
        Plot the best-concentrated localization windows.

        Usage
        -----

        x.plot_windows(nwin, [show, fname])

        Parameters
        ----------

        nwin   : The number of localization windows to plot.
        show   : If True (default), plot the image to the screen.
        fname  : If present, save the image to the file.
        """
        maxcolumns = 5
        ncolumns = min(maxcolumns, nwin)
        nrows = _np.ceil(nwin / ncolumns).astype(int)
        figsize = ncolumns * 2.4, nrows * 1.2 + 0.5
        fig, axes = _plt.subplots(nrows, ncolumns, figsize=figsize)

        for ax in axes[:-1, :].flatten():
            for xlabel_i in ax.get_xticklabels():
                xlabel_i.set_visible(False)
        for ax in axes[:, 1:].flatten():
            for ylabel_i in ax.get_yticklabels():
                ylabel_i.set_visible(False)

        for itaper in range(min(self.nwin, nwin)):
            evalue = self.eigenvalues[itaper]
            ax = axes.flatten()[itaper]
            ax.imshow(self.get_grid(itaper), origin='upper',
                      extent=(0., 360., -90., 90.))
            ax.set_title('concentration: {:2.2f}'.format(evalue))

        fig.tight_layout(pad=0.5)

        if show:
            _plt.show()
        if fname is not None:
            fig.savefig(fname)

    def plot_powerspectra(self, nwin, show=True, fname=None):
        """
        Plot the power spectra of the best-concentrated localization windows.

        Usage
        -----

        x.plot_powerspectra(nwin, [show, fname])

        Parameters
        ----------

        nwin   : The number of localization windows to plot.
        show   : If True (default), plot the image to the screen.
        fname  : If present, save the image to the file.
        """
        if nwin is None:
            nwin = self.nwin

        degrees = self.get_degrees()
        power = self.get_powerperdegree()

        maxcolumns = 5
        ncolumns = min(maxcolumns, nwin)
        nrows = _np.ceil(nwin / ncolumns).astype(int)
        fig, axes = _plt.subplots(nrows, ncolumns)

        for ax in axes[:-1, :].flatten():
            for xlabel_i in ax.get_xticklabels():
                xlabel_i.set_visible(False)
        for ax in axes[:, 1:].flatten():
            for ylabel_i in ax.get_yticklabels():
                ylabel_i.set_visible(False)

        for itaper in range(min(self.nwin, nwin)):
            evalue = self.eigenvalues[itaper]
            ax = axes.flatten()[itaper]
            ax.set_xlabel('degree l')
            ax.set_ylabel('power per degree')
            ax.set_yscale('log')
            ax.grid(True, which='both')
            ax.plot(degrees[0:], power[0:, itaper])
            ax.set_title('concentration: {:2.2f}'.format(evalue))

        fig.tight_layout(pad=0.5)

        if show:
            _plt.show()
        if fname is not None:
            fig.savefig(fname)

    def plot_couplingmatrix(self, lmax, nwin=None, weights=None, show=True,
                            fname=None):
        """
        Plot the multitaper coupling matrix. This matrix relates the global
        power spectrum to the expectation of the localized multitaper spectrum.

        Usage
        -----

        x.plot_couplingmatrix(lmax, [nwin, weights, show, fname])

        Parameters
        ----------

        lmax    : Spherical harmonic bandwidth of the global power spectrum.
        nwin    : Number of tapers used in the mutlitaper spectral analysis.
                  Default = x.nwin
        weights : Taper weights used with the multitaper spectral analyses.
                  Defaut is x.weights.
        show    : If True (default), plot the image to the screen.
        fname   : If present, save the image to the file.
        """
        figsize = _mpl.rcParams['figure.figsize']
        figsize[0] = figsize[1]
        fig = _plt.figure(figsize=figsize)
        ax = fig.add_subplot(111)
        ax.imshow(self.get_couplingmatrix(lmax, nwin=nwin, weights=weights))
        ax.set_xlabel('output power')
        ax.set_ylabel('input power')
        fig.tight_layout(pad=0.1)

        if show:
            _plt.show()
        if fname is not None:
            fig.savefig(fname)

    def info(self):
        """
        Print a summary of the data stored in the SHWindow instance.

        Usage
        -----

        x.info()
        """
        self._info()


class SHWindowCap(SHWindow):
    """Class for localization windows concentrated within a spherical cap."""

    @staticmethod
    def istype(kind):
        return kind == 'cap'

    def __init__(self, theta, tapers, eigenvalues, taper_order,
                 clat, clon, nwin, theta_degrees, coord_degrees, dj_matrix,
                 weights):
        self.kind = 'cap'
        self.theta = theta
        self.clat = clat
        self.clon = clon
        self.lmax = tapers.shape[0] - 1
        self.theta_degrees = theta_degrees
        self.coord_degrees = coord_degrees
        self.dj_matrix = dj_matrix
        self.weights = weights

        if nwin is not None:
            self.nwin = nwin
        else:
            self.nwin = tapers.shape[1]

        if self.nwin > (self.lmax + 1)**2:
            raise ValueError('nwin must be less than or equal to ' +
                             '(lmax+1)**2. nwin = {:s} and lmax = {:s}.'
                             .format(repr(self.nwin), repr(self.lmax)))

        self.tapers = tapers[:, :self.nwin]
        self.eigenvalues = eigenvalues[:self.nwin]
        self.orders = taper_order[:self.nwin]

        if self.clat is None and self.clon is None:
            # ---- If the windows aren't rotated, don't store them.
            self.coeffs = None

        else:
            # ---- Rotate center of windows to the given coordinates ----
            self.rotate(clat=self.clat, clon=self.clon,
                        coord_degrees=self.coord_degrees,
                        dj_matrix=self.dj_matrix)

    def _taper2coeffs(self, itaper):
        """
        Return the spherical harmonic coefficients of the unrotated taper i
        as an array, where i = 0 is the best concentrated.
        """
        taperm = self.orders[itaper]
        coeffs = _np.zeros((2, self.lmax + 1, self.lmax + 1))
        if taperm < 0:
            coeffs[1, :, abs(taperm)] = self.tapers[:, itaper]
        else:
            coeffs[0, :, abs(taperm)] = self.tapers[:, itaper]

        return coeffs

    def _get_coeffs(self, itaper, normalization='4pi', csphase=1):
        """
        Return the spherical harmonic coefficients of taper i as an
        array, where i = 0 is the best concentrated.
        """
        if self.coeffs is None:
            coeffs = _np.copy(self._taper2coeffs(itaper))
        else:
            coeffs = _shtools.SHVectorToCilm(self.coeffs[itaper, :])

        if normalization == 'schmidt':
            for l in range(self.lmax + 1):
                coeffs[:, l, :l+1] *= _np.sqrt(2.0 * l + 1.0)
        elif normalization == 'ortho':
            coeffs *= _np.sqrt(4.0 * _np.pi)

        if csphase == -1:
            for m in range(self.lmax + 1):
                if m % 2 == 1:
                    coeffs[:, :, m] = - coeffs[:, :, m]

        return coeffs

    def rotate(self, clat, clon, coord_degrees=True, dj_matrix=None):
        """"
        Rotate the spherical-cap windows centered on the north pole to clat
        and clon, and save the spherical harmonic coefficients in the
        attribute coeffs.

        Usage
        -----

        x.rotate(clat, clon [coord_degrees, dj_matrix])

        Parameters
        ----------

        clat, clon    : Latitude and longitude of the center of the rotated
                        spherical-cap localization windows (default in
                        degrees).
        coord_degrees : True (default) if clat and clon are in degrees.
        dj_matrix     : The djpi2 rotation matrix (default=None), computed
                        by a call to djpi2.

        Description
        -----------

        This function will take the spherical-cap localization windows
        centered at the north pole (and saved in the attributes tapers and
        orders), rotate each function to the coordinate (clat, clon), and save
        the spherical harmonic coefficients in the attribute coeffs. Each
        column of coeffs contains a single window, and is ordered according to
        the convention in SHCilmToVector.
        """
        self.coeffs = _np.zeros((self.nwin, (self.lmax + 1)**2))
        self.clat = clat
        self.clon = clon
        self.coord_degrees = coord_degrees

        if self.coord_degrees:
            angles = _np.radians(_np.array([0., -(90. - clat), -clon]))
        else:
            angles = _np.array([0., -(_np.pi/2. - clat), -clon])

        if dj_matrix is None:
            if self.dj_matrix is None:
                self.dj_matrix = _shtools.djpi2(self.lmax + 1)
                dj_matrix = self.dj_matrix
            else:
                dj_matrix = self.dj_matrix

        for i in range(self.nwin):
            if ((coord_degrees is True and clat == 90. and clon == 0.) or
                    (coord_degrees is False and clat == _np.pi/2. and
                     clon == 0.)):
                coeffs = self._taper2coeffs(i)
                self.coeffs[i, :] = _shtools.SHCilmToVector(coeffs)

            else:
                coeffs = _shtools.SHRotateRealCoef(self._taper2coeffs(i),
                                                   angles, dj_matrix)
                self.coeffs[i, :] = _shtools.SHCilmToVector(coeffs)

    def _get_couplingmatrix(self, lmax, nwin=None, weights=None):
        """Return the coupling matrix of the first nwin tapers."""
        if nwin is None:
            nwin = self.nwin

        if weights is None:
            weights = self.weights

        if weights is None:
            return _shtools.SHMTCouplingMatrix(lmax, self.tapers**2, k=nwin)
        else:
            return _shtools.SHMTCouplingMatrix(lmax, self.tapers**2, k=nwin,
                                               taper_wt=self.weights)

    def _get_multitaperpowerspectrum(self, clm, k, clat=None, clon=None,
                                     coord_degrees=True, lmax=None,
                                     taper_wt=None):
        """
        Return the multitaper power spectrum estimate and uncertainty for an
        input SHCoeffs class instance.
        """
        if lmax is None:
            lmax = clm.lmax

        if (clat is not None and clon is not None and clat == self.clat and
                clon == self.clon and coord_degrees is self.coord_degrees):
            # use the already stored coeffs
            pass
        elif (clat is None and clon is None) and \
                (self.clat is not None and self.clon is not None):
            # use the already stored coeffs
            pass
        else:
            if clat is None:
                clat = self.clat
            if clon is None:
                clon = self.clon
            if (clat is None and clon is not None) or \
                    (clat is not None and clon is None):
                raise ValueError('clat and clon must both be input. ' +
                                 'clat = {:s}, clon = {:s}'
                                 .format(repr(clat), repr(clon)))
            if clat is None and clon is None:
                self.rotate(clat=90., clon=0., coord_degrees=True)
            else:
                self.rotate(clat=clat, clon=clon, coord_degrees=coord_degrees)

        sh = clm.get_coeffs(normalization='4pi', csphase=1, lmax=lmax)

        if taper_wt is None:
            return _shtools.SHMultiTaperMaskSE(sh, self.coeffs, lmax=lmax, k=k)
        else:
            return _shtools.SHMultiTaperMaskSE(sh, self.coeffs, lmax=lmax, k=k,
                                               taper_wt=taper_wt)

    def _get_multitapercrosspowerspectrum(self, clm, slm, k, clat=None,
                                          clon=None, coord_degrees=True,
                                          lmax=None, taper_wt=None):
        """
        Return the multitaper cross-power spectrum estimate and uncertainty for
        two input SHCoeffs class instances.
        """
        if lmax is None:
            lmax = min(clm.lmax, slm.lmax)

        if (clat is not None and clon is not None and clat == self.clat and
                clon == self.clon and coord_degrees is self.coord_degrees):
            # use the already stored coeffs
            pass
        elif (clat is None and clon is None) and \
                (self.clat is not None and self.clon is not None):
            # use the already stored coeffs
            pass
        else:
            if clat is None:
                clat = self.clat
            if clon is None:
                clon = self.clon
            if (clat is None and clon is not None) or \
                    (clat is not None and clon is None):
                raise ValueError('clat and clon must both be input. ' +
                                 'clat = {:s}, clon = {:s}'
                                 .format(repr(clat), repr(clon)))
            if clat is None and clon is None:
                self.rotate(clat=90., clon=0., coord_degrees=True)
            else:
                self.rotate(clat=clat, clon=clon, coord_degrees=coord_degrees)\

        sh1 = clm.get_coeffs(normalization='4pi', csphase=1, lmax=lmax)
        sh2 = slm.get_coeffs(normalization='4pi', csphase=1, lmax=lmax)

        if taper_wt is None:
            return _shtools.SHMultiTaperMaskCSE(sh1, sh2, self.coeffs,
                                                lmax1=lmax, lmax2=lmax, k=k)
        else:
            return _shtools.SHMultiTaperMaskCSE(sh1, sh2, self.coeffs,
                                                lmax1=lmax, lmax2=lmax, k=k,
                                                taper_wt=taper_wt)

    def _info(self):
        """Print a summary of the data in the SHWindow instance."""
        print('kind = {:s}\n'.format(repr(self.kind)), end='')

        if self.theta_degrees:
            print('theta = {:f} degrees\n'.format(self.theta), end='')
        else:
            print('theta = {:f} radians'.format(self.theta), end='')

        print('lmax = {:d}\n'.format(self.lmax), end='')
        print('nwin = {:d}\n'.format(self.nwin), end='')

        if self.clat is not None:
            if self.coord_degrees:
                print('clat = {:f} degrees\n'.format(self.clat), end='')
            else:
                print('clat = {:f} radians\n'.format(self.clat), end='')
        else:
            print('clat is not specified')

        if self.clon is not None:
            if self.coord_degrees:
                print('clon = {:f} degrees\n'.format(self.clon), end='')
            else:
                print('clon = {:f} radians\n'.format(self.clon), end='')
        else:
            print('clon is not specified')

        if self.dj_matrix is not None:
            print('dj_matrix is stored')
        else:
            print('dj_matrix is not stored')

        if self.weights is None:
            print('Taper weights are not set.')
        else:
            print('Taper weights are set.')


class SHWindowMask(SHWindow):
    """
    Class for localization windows concentrated within a specified mask and
    for a given spherical harmonic bandwidth.
    """

    @staticmethod
    def istype(kind):
        return kind == 'mask'

    def __init__(self, tapers, eigenvalues, weights):
        self.kind = 'mask'
        self.lmax = _np.sqrt(tapers.shape[0]).astype(int) - 1
        self.weights = weights
        self.nwin = tapers.shape[1]
        self.tapers = tapers
        self.eigenvalues = eigenvalues

    def _get_coeffs(self, itaper, normalization='4pi', csphase=1):
        """
        Return the spherical harmonic coefficients of taper i as an
        array, where i = 0 is the best concentrated.
        """
        coeffs = _shtools.SHVectorToCilm(self.tapers[:, itaper])

        if normalization == 'schmidt':
            for l in range(self.lmax + 1):
                coeffs[:, l, :l+1] *= _np.sqrt(2.0 * l + 1.0)
        elif normalization == 'ortho':
            coeffs *= _np.sqrt(4.0 * _np.pi)

        if csphase == -1:
            for m in range(self.lmax + 1):
                if m % 2 == 1:
                    coeffs[:, :, m] = - coeffs[:, :, m]

        return coeffs

    def _get_couplingmatrix(self, lmax, nwin=None, weights=None):
        """Return the coupling matrix of the first nwin tapers."""
        if nwin is None:
            nwin = self.nwin

        if weights is None:
            weights = self.weights

        tapers_power = _np.zeros((self.lmax+1, nwin))
        for i in range(nwin):
            tapers_power[:, i] = _shtools.SHPowerSpectrum(self.get_coeffs(i))

        if weights is None:
            return _shtools.SHMTCouplingMatrix(lmax, tapers_power, k=nwin)
        else:
            return _shtools.SHMTCouplingMatrix(lmax, tapers_power, k=nwin,
                                               taper_wt=self.weights)

    def _get_multitaperpowerspectrum(self, clm, k, lmax=None, taper_wt=None):
        """
        Return the multitaper power spectrum estimate and uncertainty for an
        input SHCoeffs class instance.
        """

        if lmax is None:
            lmax = clm.lmax

        sh = clm.get_coeffs(normalization='4pi', csphase=1, lmax=lmax)

        if taper_wt is None:
            return _shtools.SHMultiTaperMaskSE(sh, self.tapers, lmax=lmax, k=k)
        else:
            return _shtools.SHMultiTaperMaskSE(sh, self.tapers, lmax=lmax,
                                               k=k, taper_wt=taper_wt)

    def _get_multitapercrosspowerspectrum(self, clm, slm, k, lmax=None,
                                          taper_wt=None):
        """
        Return the multitaper cross-power spectrum estimate and uncertainty for
        two input SHCoeffs class instances.
        """

        if lmax is None:
            lmax = min(clm.lmax, slm.lmax)

        sh1 = clm.get_coeffs(normalization='4pi', csphase=1, lmax=lmax)
        sh2 = slm.get_coeffs(normalization='4pi', csphase=1, lmax=lmax)

        if taper_wt is None:
            return _shtools.SHMultiTaperMaskCSE(sh1, sh2, self.tapers,
                                                lmax=lmax, k=k)
        else:
            return _shtools.SHMultiTaperMaskCSE(sh1, sh2, self.tapers,
                                                lmax=lmax, k=k,
                                                taper_wt=taper_wt)

    def _info(self):
        """Print a summary of the data in the SHWindow instance."""
        print('kind = {:s}\n'.format(repr(self.kind)), end='')

        print('lmax = {:d}\n'.format(self.lmax), end='')
        print('nwin = {:d}\n'.format(self.nwin), end='')

        if self.weights is None:
            print('Taper weights are not set.')
        else:
            print('Taper weights are set.')