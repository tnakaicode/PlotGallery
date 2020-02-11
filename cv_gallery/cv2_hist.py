# https://opencv-python-tutroals.readthedocs.io/en/latest/py_tutorials/py_ml/py_kmeans/py_kmeans_opencv/py_kmeans_opencv.html#kmeans-opencv
import numpy as np
import cv2
from matplotlib import pyplot as plt

plt.figure()
x = np.random.randint(25, 100, 25)
y = np.random.randint(175, 255, 25)
z = np.hstack((x, y))
z = z.reshape((50, 1))
z = np.float32(z)
plt.hist(z, 256, [0, 256])

#
# Now we apply the KMeans function.
# Before that we need to specify the criteria.
# My criteria is such that,
# whenever 10 iterations of algorithm is ran, or an accuracy of epsilon = 1.0 is reached, stop the algorithm and return the answer.

plt.figure()

# Define criteria = ( type, max_iter = 10 , epsilon = 1.0 )
criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)

# Set flags (Just to avoid line break in the code)
flags = cv2.KMEANS_RANDOM_CENTERS

# Apply KMeans
compactness, labels, centers = cv2.kmeans(z, 2, None, criteria, 10, flags)

#
# This gives us the compactness, labels and centers.
# In this case, I got centers as 60 and 207.
# Labels will have the same size as that of test data where each data will be labelled as ‘0’,‘1’,‘2’ etc. depending on their centroids.
# Now we split the data to different clusters depending on their labels.

A = z[labels == 0]
B = z[labels == 1]

#
# Now we plot A in Red color and B in Blue color and their centroids in Yellow color.

# Now plot 'A' in red, 'B' in blue, 'centers' in yellow
plt.hist(A, 256, [0, 256], color='r')
plt.hist(B, 256, [0, 256], color='b')
plt.hist(centers, 32, [0, 256], color='y')

#
# In previous example,
# we took only height for t-shirt problem.
# Here, we will take both height and weight, ie two features.

#
# Remember, in previous case, we made our data to a single column vector.
# Each feature is arranged in a column, while each row corresponds to an input test sample.

#
# For example, in this case,
# we set a test data of size 50x2, which are heights and weights of 50 people.
# First column corresponds to height of all the 50 people and
# second column corresponds to their weights.
#
# First row contains two elements where first one is the height of first person and
# second one his weight.
# Similarly remaining rows corresponds to heights and weights of other people.
# Check image below:

X = np.random.randint(25, 50, (25, 2))
Y = np.random.randint(60, 85, (25, 2))
Z = np.vstack((X, Y))

# convert to np.float32
Z = np.float32(Z)

# define criteria and apply kmeans()
criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
ret, label, center = cv2.kmeans(
    Z, 2, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)

# Now separate the data, Note the flatten()
A = Z[label.ravel() == 0]
B = Z[label.ravel() == 1]

plt.figure()
plt.scatter(A[:, 0], A[:, 1])
plt.scatter(B[:, 0], B[:, 1], c='r')
plt.scatter(center[:, 0], center[:, 1], s=80, c='y', marker='s')
plt.xlabel('Height'), plt.ylabel('Weight')
plt.show()

#
# Color Quantization is the process of reducing number of colors in an image.
# One reason to do so is to reduce the memory.
# Sometimes, some devices may have limitation such that it can produce only limited number of colors.
# In those cases also, color quantization is performed.
# Here we use k-means clustering for color quantization.

#
# There is nothing new to be explained here.
# There are 3 features, say, R,G,B.
# So we need to reshape the image to an array of Mx3 size (M is number of pixels in image).
# And after the clustering, we apply centroid values (it is also R,G,B) to all pixels, such that resulting image will have specified number of colors.
# And again we need to reshape it back to the shape of original image.
# Below is the code:

img = cv2.imread('home.jpg')
Z = img.reshape((-1, 3))

# convert to np.float32
Z = np.float32(Z)

# define criteria, number of clusters(K) and apply kmeans()
criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
K = 16
ret, label, center = cv2.kmeans(
    Z, K, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)

# Now convert back into uint8, and make original image
center = np.uint8(center)
res = center[label.flatten()]
res2 = res.reshape((img.shape))

cv2.imshow('res2', res2)
cv2.waitKey(0)
cv2.destroyAllWindows()
