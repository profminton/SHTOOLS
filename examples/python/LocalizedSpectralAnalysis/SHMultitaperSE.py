"""
This script tests the localized spectral analysis routines
"""
import numpy as np
import pyshtools as pysh

pysh.utils.figstyle()


def main():
    test_MultitaperSE()


def test_MultitaperSE():
    print('\n---- testing SHReturnTapersM ----')
    theta0_deg = 20.
    theta0 = np.radians(theta0_deg)
    lmax = 10
    orderM = 2
    print('creating spherical cap tapers with:', end=' ')
    print('size {:1.0f} deg, bandwidth {:d}, order {:d}'
          .format(theta0_deg, lmax, orderM))
    tapers, concentrations = \
        pysh.spectralanalysis.SHReturnTapersM(theta0, lmax, orderM)
    print('first 3 taper concentrations:')
    print(concentrations[:3])

    print('\n---- testing SHReturnTapers ----')
    theta0_deg = 20.
    theta0 = np.radians(theta0_deg)
    lmax = 20
    print('creating spherical cap tapers of', end=' ')
    print('size {:1.0f} deg with bandwidth {:d}'.format(theta0_deg, lmax))
    tapers, concentrations, taperorder = \
        pysh.spectralanalysis.SHReturnTapers(theta0, lmax)
    print('first 10 taper concentrations:')
    print(concentrations[:10])

    print('\n---- testing SHMultiTaperSE ----')
    lmax = 80
    ntapers = 3
    tapersk = tapers[:, :ntapers]
    torders = taperorder[:ntapers]
    coeffs = np.random.normal(size=(2, lmax + 1, lmax + 1))
    localpower, localpower_sd = \
        pysh.spectralanalysis.SHMultiTaperSE(coeffs, tapersk, torders)
    print('total power:', np.sum(localpower))

    print('\n---- testing SHMultiTaperCSE ----')
    lmax = 80
    ntapers = 3
    tapersk = tapers[:, :ntapers]
    torders = taperorder[:ntapers]
    coeffs1 = np.random.normal(size=(2, lmax + 1, lmax + 1))
    coeffs2 = 0.5 * (coeffs1 + np.random.normal(size=(2, lmax + 1, lmax + 1)))
    print(coeffs1.shape, coeffs2.shape, tapersk.shape)
    localpower, localpower_sd = \
        pysh.spectralanalysis.SHMultiTaperCSE(coeffs1, coeffs2, tapersk,
                                              torders)
    print('total power:', np.sum(localpower))

    print('\n---- testing SHLocalizedAdmitCorr ----')
    lat = 90.
    lon = 0.
    k = 3
    admit, corr, dadmit, dcorr = \
        pysh.spectralanalysis.SHLocalizedAdmitCorr(coeffs1, coeffs2, tapers,
                                                   taperorder, lat, lon, k=k)
    print(admit)

    print('\n---- testing ComputeDm ----')
    theta0_deg = 20.
    theta0 = np.radians(theta0_deg)
    lmax = 10
    m = 2
    Dm = pysh.spectralanalysis.ComputeDm(lmax, m, theta0)
    print(Dm[:3, :3])

    print('\n---- testing ComputeDG82 ----')
    theta0_deg = 20.
    theta0 = np.radians(theta0_deg)
    lmax = 10
    m = 2
    DG82 = pysh.spectralanalysis.ComputeDG82(lmax, m, theta0)
    print(DG82[:3, :3])

    print('\n---- testing SHFindLWin ----')
    theta0_deg = 20.
    theta0 = np.radians(theta0_deg)
    m = 2
    ntapers = 3
    minconcentration = 0.8
    lmax = pysh.spectralanalysis.SHFindLWin(theta0, m, minconcentration,
                                            taper_number=ntapers)
    print(lmax)

    print('\n---- testing SHBiasK ----')
    lmax = 80
    power_unbiased = 1. / (1. + np.arange(lmax + 1))**2
    power_biased = pysh.spectralanalysis.SHBiasK(tapers, power_unbiased)
    print((power_biased[:lmax + 1] / power_unbiased)[:5])

    print('\n---- testing SHBias ----')
    lmax = 80
    power_unbiased = 1. / (1. + np.arange(lmax + 1))**2
    power_biased = pysh.spectralanalysis.SHBias(tapers[:, 2], power_unbiased)
    print(tapers.shape)
    print((power_biased[:lmax + 1] / power_unbiased)[:5])

    print('\n---- testing SHBiasAdmitCorr ----')
    lmax = 80
    Stt = 1. / (1. + np.arange(lmax + 1))**2
    Sgg = 1. / (1. + np.arange(lmax + 1))**2
    Sgt = 0.5 / (1. + np.arange(lmax + 1))**2
    admit, corr = pysh.spectralanalysis.SHBiasAdmitCorr(Sgt, Sgg, Stt,
                                                        tapers[:, 2])
    print(corr)


# ==== EXECUTE SCRIPT ====
if __name__ == "__main__":
    main()
