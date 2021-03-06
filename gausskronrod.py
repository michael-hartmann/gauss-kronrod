#!/usr/bin/python3

import bisect
from math import cos, sin, sqrt
import numpy as np
from scipy.integrate import quad

# nodes and weights for Gauss-Kronrod
gausskronrod_nodes = np.array([0.949107912342759, -0.949107912342759,
                               0.741531185599394, -0.741531185599394,
                               0.405845151377397, -0.405845151377397,
                               0.000000000000000,
                               0.991455371120813, -0.991455371120813,
                               0.864864423359769, -0.864864423359769,
                               0.586087235467691, -0.586087235467691,
                               0.207784955007898, -0.207784955007898])
gauss_weights = np.array([0.129484966168870, 0.129484966168870,
                          0.279705391489277, 0.279705391489277,
                          0.381830050505119, 0.381830050505119,
                          0.417959183673469])
kronrod_weights = np.array([0.063092092629979, 0.063092092629979,
                            0.140653259715525, 0.140653259715525,
                            0.190350578064785, 0.190350578064785,
                            0.209482141084728,
                            0.022935322010529, 0.022935322010529,
                            0.104790010322250, 0.104790010322250,
                            0.169004726639267, 0.169004726639267,
                            0.204432940075298, 0.204432940075298])


def integrate_gausskronrod(f, a, b, args=()):
    """
    This function computes $\int_a^b \mathrm{d}x f(x)$ using Gauss-Kronrod
    quadrature formula. The integral is transformed
    z  = 2 \\frac{x-a}{b-a}-1
    x  = \\frac{b-a}{2} (z+1) + a
    dz = 2 \\frac{dx}{b-a}
    dx = \\frac{b-a}{2} dz
    \int_a^b \mathrm{d}x f(x) = \\frac{b-a}{2} \int_{-1}^1 \mathrm{d}z f((z+1)*(b-a)/2+a)

    returns integral and an error estimate
    """

    assert b > a
    mid = 0.5*(b+a)
    dx = 0.5*(b-a)
    zi = mid+gausskronrod_nodes*dx
    integrand = f(zi)
    integral_G7 = np.sum(integrand[:7]*gauss_weights)
    integral_K15 = np.sum(integrand*kronrod_weights)

    error = (200*abs(integral_G7-integral_K15))**1.5

    return integral_K15*dx, dx*error


def integrate(f, a, b, args=(), minintervals=1, limit=200, tol=1e-10):
    """
    Do adaptive integration using Gauss-Kronrod.
    """
    fv = np.vectorize(f)

    intervals = []

    limits = np.linspace(a, b, minintervals+1)
    for left, right in zip(limits[:-1], limits[1:]):
        I, err = integrate_gausskronrod(fv, left, right, args)
        bisect.insort(intervals, (err, left, right, I))

    while True:
        Itotal = sum([x[3] for x in intervals])
        err2 = sum([x[0]**2 for x in intervals])
        err = sqrt(err2)

        if abs(err/Itotal) < tol:
            return Itotal, err

        # no convergence
        if len(intervals) >= limit:
            return False  # better to raise an exception

        err, left, right, I = intervals.pop()

        # split integral
        mid = left+(right-left)/2

        # calculate integrals and errors, replace one item in the list and
        # append the other item to the end of the list
        I, err = integrate_gausskronrod(fv, left, mid, args)
        bisect.insort(intervals, (err, left, mid, I))
        I, err = integrate_gausskronrod(fv, mid, right, args)
        bisect.insort(intervals, (err, mid, right, I))


if __name__ == "__main__":
    p = 100
    f = lambda x: x*sin(p*x)
    g = lambda x: -x/p*cos(p*x)+1/p**2*sin(p*x)
    a, b = 1, 4

    expected = g(b)-g(a)
    for result, esterror in (quad(f, a, b),
#                            integrate_gausskronrod(f, a, b),
                             integrate(f, a, b)):
        print("{:15.13f} {:15g} {:15g}".format(result, esterror, 1-result/expected))
