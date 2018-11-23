
import numpy as np

#       image = numpy array
#   step_size = (width step size, height step size)  -> tuple input
# window_size = (width window size, height window size) -> tuple input 
#     padding = automatically adding zeros to image array if window size and step size not  
#               compatible with image size


def slice_image(image, window_size, step_size, padding = True):

	pxlValueType = image.dtype
	image = np.array(image, dtype = pxlValueType)
	
	is_RGB = image.ndim == 3
	image_width = image.shape[1]
	image_height = image.shape[0]
	
	window_width = window_size[0]
	window_height = window_size[1]
	wStep_size = step_size[0]
	hStep_size = step_size[1]

	if padding == False:
		(wStep_nums, w_remain) = divmod((image_width - window_width), wStep_size)
		(hStep_nums, h_remain) = divmod((image_height - window_height), hStep_size)
		if w_remain == 0 and h_remain == 0:
			#slice image into small pieces
			img = []
			for i in range(0, hStep_nums+1):
				for j in range(0, wStep_nums+1):
					xhead = j*wStep_size
					xtail = j*wStep_size + window_width
					yhead = i*hStep_size
					ytail = i*hStep_size + window_height
					sliced_img   = image[yhead: ytail, xhead: xtail] 
					img.append(sliced_model)
		else:
			raise ValueError('window_size and step_size not suit to the image size if not padding', \
				'(image_size-winsow_size) % step_size should be 0')

	if padding == True:
		
		(wStep_nums, w_remain) = divmod((image_width - window_width), wStep_size)
		(hStep_nums, h_remain) = divmod((image_height - window_height), hStep_size)

		# image image_width padding
		if w_remain != 0:
			wNumPadding = wStep_size-w_remain
			if is_RGB:
				zero_padding = np.zeros((image_height, wNumPadding, 3))
			else:
				zero_padding = np.zeros((image_height, wNumPadding))
			zero_padding = np.array(zero_padding, dtype = pxlValueType)
			image = np.append(image, zero_padding, axis = 1)
			wStep_nums += 1
		# image image_height padding
		if h_remain != 0:
			hNumPadding = hStep_size-h_remain
			if w_remain == 0:
				wNumPadding = 0
			if is_RGB:
				zero_padding = np.zeros((hNumPadding, image_width+wNumPadding, 3))
			else: 
				zero_padding = np.zeros((hNumPadding, image_width+wNumPadding))
			zero_padding = np.array(zero_padding, dtype = pxlValueType)
			image = np.append(image, zero_padding, axis = 0)
			hStep_nums += 1
        #slice image into small pieces
		img = []
		for i in range(0, hStep_nums+1):
			for j in range(0, wStep_nums+1):
				xhead = j*wStep_size
				xtail = j*wStep_size + window_width
				yhead = i*hStep_size
				ytail = i*hStep_size + window_height
				sliced_img = image[yhead: ytail, xhead: xtail] 
				img.append(sliced_img)
	return img

if __name__ == '__main__':

	import numpy as np
	import scipy.misc
	image = scipy.misc.imread('C:\\Users\DIRL\Desktop\Hemo_model_8bit\Hemo_model_png\Hemo_pure_model_01.png')
	img = slice_image(image, (220,630), (500,500), padding=True)

	for i in range(0,len(img)):
		scipy.misc.imsave('C:\\Users\DIRL\Desktop\\test\{}.jpg'.format(i), img[i])












