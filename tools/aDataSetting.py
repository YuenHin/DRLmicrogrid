import numpy as np

from scipy.interpolate import make_interp_spline

font_size_tick = 15
font_size_label = 18
font_size_title = 20
line_weight = 1.5
pic_weight = 6.8
pic_high = 5.2
pic_rc = 75

pad = 20


def smooth(x, y, num):
    x_smooth = np.linspace(x.min(), x.max(), num)
    y_smooth = make_interp_spline(x, y)(x_smooth)
    return x_smooth, y_smooth

