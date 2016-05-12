#
#  Hilbert Curves
#
#  Written by William Cheung, 04/27/2016
#
#  This post:
#      http://www.fundza.com/algorithmic/space_filling/hilbert/basics/index.html
#    may help you in understanding the algorithm below.
#


# x and y are the coordinates of the start point of current sub-curve
# xi & xj are the i & j components of the unit x vector of the frame
# which we will draw hilbert curve on, similarly yi and yj

def _hilbert_curve(x, y, xi, xj, yi, yj, n):
    if n == 0:
        return [(x, y)]

    sz = 1 << n
    sz_1 = sz - 1

    subsz = sz >> 1
    subsz_1  = subsz - 1

    ret =   _hilbert_curve(x, y,
                           yi, yj, xi, xj, n - 1)             \
          + _hilbert_curve(x + xi * subsz, y + xj * subsz,
                           xi, xj, yi, yj, n - 1)             \
          + _hilbert_curve(x + (xi + yi) * subsz, y + (xj + yj) * subsz,
                           xi, xj, yi, yj, n - 1)             \
          + _hilbert_curve(x + xi * subsz_1 + yi * sz_1, y + xj * subsz_1 + yj * sz_1,
                           -yi, -yj, -xi, -xj, n - 1)

    return ret


# get list of points on hilbert curve of n-th order
def hilbert_curve(n):
    # we start at (0, 0)
    return _hilbert_curve(0, 0, 1, 0, 0, 1, n)


print hilbert_curve(0)
print hilbert_curve(1)
print hilbert_curve(2)
print hilbert_curve(3)

