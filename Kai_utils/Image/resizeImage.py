import numpy as np
import scipy.misc

def resize(image, re_size, base_on = 'width'):

	if base_on == 'width':
		width = image.shape[1]
		scale = re_size/ width
	if base_on == 'height':
		height = image.shape[0]
		scale = re_size/ height

	resized_img = scipy.misc.imresize(image, scale)

	return resized_img