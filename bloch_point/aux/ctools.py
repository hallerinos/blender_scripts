import math

def color_fun(h):
    if 0 <= h < 60:
        return h / 60
    elif 60 <= h < 180:
        return 1
    elif 240 <= h <= 360:
        return 0
    elif 180 <= h < 240:
        return 4 - h / 60
    return 0

def hsv_to_rgb(n, in_v, in_h):
    nom = math.sqrt(n[0]**2 + n[1]**2 + n[2]**2) + 1e-10
    f = math.atan2(n[1]/nom, n[0]/nom)
    h = 360 * in_h + (1 - 2*in_h) * (f if f >= 0 else 2*math.pi + f) * 180/math.pi
    h = h % 360
    
    m1 = 1 - abs(n[2])/nom if (1 - 2*in_v) * n[2]/nom < 0 else 1
    m2 = 0 if (1 - 2*in_v) * n[2]/nom < 0 else abs(n[2])/nom
    
    max_v = 0.5 + nom * (m1 - 0.5)
    min_v = 0.5 - nom * (0.5 - m2)
    d_v = max_v - min_v
    
    rgb = list(n)
    rgb[0] = color_fun((h + 120) % 360) * d_v + min_v
    rgb[1] = color_fun(h % 360) * d_v + min_v
    rgb[2] = color_fun((h - 120) % 360) * d_v + min_v
    
    return rgb