import numpy as np
import cv2
import matplotlib.pyplot as plt


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


def get_all_drops(im, y0=200):
    thres = 95

    roi = im[y0:, :]
    ret, thresh = cv2.threshold(255 - roi, thres, 255, cv2.THRESH_BINARY)
    cntim, contours, h = cv2.findContours(np.copy(thresh), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    contours = [cnt for cnt in contours if len(cnt) > 2]

    if len(contours) <= 10:
        return [calculate_drop_params(cnt, im) for cnt in contours]


def running_average(x, n):
    try:
        return np.convolve(x, np.ones((n,)) / n)[(n - 1):]
    except:
        return 0


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


def extract_histogram_mean(img, show_hist=0):
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

    if show_hist == 1:
        plt.title('Histogram for gray scale picture')
        plt.show()

    return hist_mean


def main():
    videoCapture = cv2.VideoCapture(
        '/Users/tylerjaacks/Documents/Projects/Class Projects/TestData/DropVideo_09h_31m_48s.avi')

    dp = 1
    minDistBetweenCircles = 20
    higherThreshold = 50
    accumThreshold = 30
    minRadius = 0
    maxRadius = 0

    while True:
        ret, image = videoCapture.read()

        current_frame = videoCapture.get(cv2.CAP_PROP_POS_FRAMES)
        total_frames = videoCapture.get(cv2.CAP_PROP_FRAME_COUNT)

        if current_frame >= total_frames:
            break

        orig_image = np.copy(image)
        output = image.copy()
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        grayBlurred = cv2.blur(gray, (3, 3))

        tmp = get_all_drops(grayBlurred)

        cv2.imshow('frame', grayBlurred)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cv2.destroyAllWindows()


if __name__ == '__main__':
    main()
