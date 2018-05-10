import matplotlib

from PIL import Image
from pylab import *
from matplotlib import pyplot as plt


def get_coo(photo):
    im = array(Image.open(photo))
    imshow(im)
    matplotlib.rcParams['interactive'] == True
    print('Please click 2 points')
    x = ginput(2)
    print('you clicked:', x)
    # show()
    return x
