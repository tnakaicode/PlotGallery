#!/usr/bin/env python
# coding: utf-8

# # Load image
# 
# Image processing often works on gray scale images that were stored as PNG files. How do we import / export that
#  file into {{{python}}}?
# 
#  * Here is a recipy to do this with Matplotlib using the {{{imread}}} function (your image is called {{{lena.png}}}). 
# 
# <pre><code>
# from pylab import imread, imshow, gray, mean
# a = imread('lena.png')
#  # generates a RGB image, so do
# aa=mean(a,2) # to get a 2-D array
# imshow(aa)
# gray()
# </code></pre>
# 
# This permits to do some processing for further exporting such as for
# [:Cookbook/Matplotlib/converting_a_matrix_to_a_raster_image:converting a matrix to a raster image]. In the newest version of pylab (check that your {{{pylab.matplotlib.__version__}}} is superior to {{{'0.98.0'}}}) you get directly a 2D numpy array if the image is grayscale.
# 
# 
# * to write an image, do 
# <code>
# import Image
# mode = 'L'
# size= (256, 256)
# imNew=Image.new(mode , size)
# mat = numpy.random.uniform(size = size)
# data = numpy.ravel(mat)
# data = numpy.floor(data * 256)
# 
# imNew.putdata(data)
# imNew.save("rand.png")
# </code>
# 
#  * this kind of functions live also under {{{scipy.misc}}}, see for instance {{{scipy.misc.imsave}}} to create a color image:
#  <code>
# from scipy.misc import imsave
# import numpy
# a = numpy.zeros((4,4,3))
# a[0,0,:] = [128, 0 , 255]
# imsave('graybackground_with_a_greyish_blue_square_on_top.png',a)
# </code>
# 
# 
#  * to define the range, use:
# <code>
# from scipy.misc import toimage
# import numpy
# a = numpy.random.rand(25,50) #between 0. and 1.
# toimage(a, cmin=0., cmax=2.).save('low_contrast_snow.png')
# </code>
# (adapted from http://telin.ugent.be/~slippens/drupal/scipy_unscaledimsave )
# 
# 
#  * there was another (more direct) method suggested by http://jehiah.cz/archive/creating-images-with-numpy
