import cv2
import numpy as np

import matplotlib.pyplot as plt

from numpy import rot90


class vision():
    def __int__(self):
        pass


def combine_gen(x1, y1, x2, y2):
    i = 0
    j = 0
    while i < len(x1) or j < len(x2):
        if j == len(x2) or x1[i] < x2[j]:
            yield x1[i], y1[i]
            i += 1
        else:
            yield x2[j], y2[j]
            j += 1


def combine_lists(x1, y1, x2, y2):
    xy = list(combine_gen(x1, y1, x2, y2))
    x = [v[0] for v in xy]
    y = [v[1] for v in xy]
    return x, y


def calculate_drop_size(cnt):
    cntf = cnt.squeeze().astype('float')
    x = cntf[:, 0].squeeze().tolist()
    y = cntf[:, 1].squeeze().tolist()

    # split into left and right half
    a = np.argmin(y)
    b = np.argmax(y)
    (a, b) = (min((a, b)), max((a, b)))
    x1 = x[a:b + 1]
    y1 = y[a:b + 1]
    x2 = x[b:] + x[:a + 1]
    y2 = y[b:] + y[:a + 1]
    x2.reverse()
    y2.reverse()

    # add missing points on left half
    y1m = [v for v in y2 if v not in y1]
    x1m = np.interp(y1m, y1, x1)
    y1i, x1i = combine_lists(y1, x1, y1m, x1m)

    # add missing points on right half
    y2m = [v for v in y1 if v not in y2]
    x2m = np.interp(y2m, y2, x2)
    y2i, x2i = combine_lists(y2, x2, y2m, x2m)

    # integration
    V = 0
    for i in range(len(y1i) - 1):
        ya = y1i[i]
        yb = y1i[i + 1]
        if ya != yb:
            ia = len(y2i) - 1 - y2i[::-1].index(ya)
            ib = y2i.index(yb)
            ra = (x2i[ia] - x1i[i]) / 2
            rb = (x2i[ib] - x1i[i + 1]) / 2
            dy = yb - ya
            if ra == rb:
                dV = (ra ** 2 * np.pi * dy)
            else:
                dV = 1 / 3 * np.pi * (rb ** 3 - ra ** 3) / ((rb - ra) / dy)
            V += dV
            # V = integral from y1 to y2 over pi * r(y)^2 * dr   (where dr/dy == const per segment)
            #   = 1/3 * pi * (r2^3-r1^3) / (dr/dy)
    return V, cv2.moments(cnt)['m00']


def running_average(x, N):
    try:
        return np.convolve(x, np.ones((N,)) / N)[(N - 1):]
    except:
        return 0


def calculate_drop_params(cnt, im):
    try:

        roi = im[200:, :]

        volume, area = calculate_drop_size(cnt)
        diameter = 2 * np.sqrt(area / np.pi)
        m = cv2.moments(cnt)
        x = m['m10'] / area
        y = m['m01'] / area
        angle = np.abs(np.arctan(x / y)) / np.pi * 180
        r = cv2.minEnclosingCircle(cnt)[1]
        roundness = area / (np.pi * r ** 2)
        ix = int(m['m10'] / area)
        iy = int(y)
        im2 = roi[iy, ix - 50:ix + 50].astype('float') / 255
        d = np.abs(np.diff(im2))
        sharpness = np.max(running_average(d, 2)) * 2

        return {
            'diameter': diameter,
            'area': area,
            'volume': volume,
            'angle': angle,
            'roundness': roundness,
            'sharpness': sharpness,
            'x': x,
            'y': y
        }
    except:
        pass


def get_all_drops(im, y0=200):
    thres = 95

    roi = im[y0:, :]
    ret, thresh = cv2.threshold(255 - roi, thres, 255, cv2.THRESH_BINARY)
    cntim, contours, h = cv2.findContours(np.copy(thresh), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    contours = [cnt for cnt in contours if len(cnt) > 2]

    if len(contours) <= 10:
        return [calculate_drop_params(cnt, im) for cnt in contours]


def calculate_drop_params_cara(cnt):
    try:
        volume, area = calculate_drop_size(cnt)
        m = cv2.moments(cnt)
        x = m['m10'] / area
        y = m['m01'] / area

        return (volume * 0.4532 ** 3 / 1000), x, y  # calibrated measure

        # with 50mm spacer : 0.4532
        # with std lens : 0.9495

    except:
        print('ERROR : def calculate_drop_params_cara(cnt):')
        pass


def get_all_drops_cara(im, y0=200):
    roi = im[y0:, :]

    thres = 95

    ret, thresh = cv2.threshold(255 - roi, thres, 255, cv2.THRESH_BINARY)
    cntim, contours, h = cv2.findContours(np.copy(thresh), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours = [cnt for cnt in contours if len(cnt) > 2]

    if len(contours) <= 10:
        return [calculate_drop_params_cara(cnt) for cnt in contours]


# -------------------------------------------------------------------------

# detect if there is someting runing out of the nozzle ( const flow ) 
# -------------------------------------------------------------------------
def nozzleFlow_detection(im, y0=200, x0=250):
    # return = val : size of the liquid steam
    # return = -2  : no stream at all
    # return = -1  : drop
    # ------------------------------------------------------------------------

    lenght = 300
    hight = 500

    try:
        roi = im[y0:y0 + lenght, x0:x0 + hight]

        imEdge = cv2.Canny(roi, 80, 200)

        # flow detection == 3 line throw the give image (lenght and hight)
        dist1, fidx, lidx = PointtoPoint(imEdge[50: 51, :], 1)
        dist2, fidx2, lidx2 = PointtoPoint(imEdge[120: 121, :], 1)
        dist3, fidx3, lidx3 = PointtoPoint(imEdge[250: 251, :], 1)

        dist_mean = np.mean([dist1, dist2, dist3])

        if dist_mean < 0:
            return -2
        elif dist_mean < 65 and dist_mean > 45:
            return dist_mean
        elif dist_mean > 65 or dist_mean < 45:
            return -1
    except:
        pass


# ---------------------------------------------------------------------------
#  Inspect the tip of the nozzle to check if there is a contamination 
# ---------------------------------------------------------------------------
def nozzle_clean(im, y0=0, x0=0, samples=10):
    # ---------------------------------------------------------------------------
    # return 1 : nozzle clean
    # return -1 : nozzle contaminated

    i = 0

    dist = []

    roi = im[:300, 465:530]  # resize useful image

    imEdge = cv2.Canny(roi, 80, 150)

    step = len(im) % samples

    while i < samples + 1:
        idx = i * step
        dist.append(PointtoPoint(imEdge[:, idx: idx + 1], 0))

        i += 1
    x = []
    x += [point[1] for point in dist if point[0] >= 0]

    Xpos = np.sum(x) / len(x)

    histim = im[int(Xpos) - 20: int(Xpos) + 20, 200:800]

    val = Extracthist_mean(histim, 1)

    if val < 100:
        return 1
    else:
        return -1

        # cv2.imshow('treshImg', histim)
    # cv2.waitKey(0)


# ---------------------------------------------------------------------------
# Inspect the image to detect if there is a large drop dripping of the nozzle
# ---------------------------------------------------------------------------
def nozzle_driping(im, y0=200, x0=0):
    # ---------------------------------------------------------------------------
    # return =  1 : nozzle isn't droping
    # return = -1 : nozzle is droping

    lenght = 600
    hight = 1200

    full = im[y0:y0 + lenght, x0:x0 + hight]

    ret, th2 = cv2.threshold(255 - full, 100, 255, cv2.THRESH_BINARY)

    cntim, contours, h = cv2.findContours(np.copy(th2), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if len(contours) == 0:
        return 1
    else:
        return -1

    # ---------------------------------------------------------------------------


# calculate the distance between two point in a image sample Line of pixel 1x lenght
# ---------------------------------------------------------------------------
def PointtoPoint(line, rot=0):
    # ---------------------------------------------------------------------------
    # return >0  : distance between two line ( pixel in image sample)
    # return  0  : only one line (pixel in the image sample)
    # return -1  : no line in the image sample

    if rot == 1:
        L1 = np.asarray(rot90(line), dtype="uint8")
    else:
        L1 = np.asarray(line, dtype="uint8")

        # find first idx
    fidx = -1
    lidx = -1

    if np.sum(L1) > 100:

        i = 0
        while fidx == -1:
            if (L1[i] > 100):
                fidx = i
            i = i + 1

            # find last index
        i = 1
        while lidx == -1:
            if (L1[len(L1) - i] > 100):
                lidx = len(L1) - i
            i = i + 1
    else:
        return -1, fidx, lidx

    return (lidx - fidx), fidx, lidx


# ---------------------------------------------------------------------------
# calculate the distance between two point in a image sample:
# ---------------------------------------------------------------------------
def Extracthist_mean(img, showhist=0):
    # ---------------------------------------------------------------------------
    # return = val : mean value if the histogram in the given region

    i = 0  # loop counter
    hist_mean = 0

    gus = plt.hist(img.ravel(), 256, [0, 255])

    histval = gus[0]

    for val in histval:
        hist_mean = hist_mean + val * i
        i = i + 1

    hist_mean = hist_mean / sum(histval)

    if showhist == 1:
        plt.title('Histogram for gray scale picture')
        plt.show()

    return hist_mean


# ---------------------------------------------------------------------------
# return >0  : distance between two line ( pixel in image sample) 
# return = 0 : only one line (pixel in the image sample)  
# return -1  : no line in the image sample


##-----------------------------------------------------------------------------
# meansur the size of a nown part in the image to convert the pxl/mm relation for drop volume calculation
##-----------------------------------------------------------------------------
def ref_calibration(im):
    reflength = 50  # micro metre

    print('start calibration')

    lenght = 50
    hight = 500

    roi = im[0:lenght, int(0.6 * hight):int(1.4 * hight)]

    try:

        imEdge = cv2.Canny(roi, 85, 135, apertureSize=3)

        cv2.imshow('raw', im)
        cv2.waitKey(0)

        cv2.imshow('drop', imEdge)
        cv2.waitKey(0)

        mean = []

        x, y = imEdge.shape

        for i in range(1, x):

            dist, fidx, lidx = PointtoPoint(imEdge[i: i + 1, :], 1)

            if dist > 0:
                mean.append(dist)
    except:
        pass

    pxDist = sum(mean) / len(mean)

    print('distance in pixel : %f' % pxDist)
    print('real world distance : %f' % reflength)

    conv = reflength / pxDist

    print('conversion : %f [micro meter/ pixel ]' % conv)

    print('stop calibration ')

    def myround(x, base=0.001):

        return base * round(float(x) / base)

    return myround(conv)
