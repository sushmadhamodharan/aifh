__author__ = 'jheaton'

import os
import sys
import numpy as np
from scipy.optimize import minimize

# Find the AIFH core files
aifh_dir = os.path.dirname(os.path.abspath(__file__))
aifh_dir = os.path.abspath(aifh_dir + os.sep + ".." + os.sep + "lib" + os.sep + "aifh")
sys.path.append(aifh_dir)

from normalize import Normalize
from rbf_network import RbfNetwork
from error import ErrorCalculation
from equilateral import Equilateral


# find the Iris data set
irisFile = os.path.dirname(os.path.realpath(__file__))
irisFile = os.path.abspath(irisFile + "../../datasets/iris.csv")

# Read the Iris data set.
print('Reading CSV file: ' + irisFile)
norm = Normalize()
iris_work = norm.load_csv(irisFile)

# Extract the original iris species so we can display during the final validation.
ideal_species = [row[4] for row in iris_work]

# Setup the first four fields to "range normalize" between -1 and 1.
for i in range(0, 4):
    norm.make_col_numeric(iris_work, i)
    norm.norm_col_range(iris_work, i, 0, 1)

# Discover all of the classes for column #4, the iris species.
classes = norm.build_class_map(iris_work, 4)
inv_classes = {v: k for k, v in classes.items()}

# Normalize iris species using equilateral
norm.norm_col_equilateral(iris_work, 4, classes, 0, 1)


# Display the resulting data
#norm.display_data(result)

training = np.array(iris_work)
training_input = training[:, 0:4]
training_ideal = training[:, 4:6]

# Create an RBF network.  There are four inputs and two outputs.
# There are also five RBF functions used internally.
# You can experiment with different numbers of internal RBF functions.
# However, the input and output must match the data set.
network = RbfNetwork(4, 5, 2)
network.reset()

best_score = sys.float_info.max


def score_funct(x):
    global best_score
    global input_data
    global output_data
    network.copy_memory(x)
    actual_output = []
    for input_data in training_input:
        output_data = network.compute_regression(input_data)
        actual_output.append(output_data)

    result = ErrorCalculation.mse(np.array(actual_output), training_ideal)
    if result < best_score:
        best_score = result
        print("Score: " + str(result))
    return result

x0 = network.longTermMemory[:]
print(score_funct(x0))
res = minimize(score_funct, x0, method='nelder-mead', tol=0.0001, options={'disp': True, 'maxiter': 5000})
print(score_funct(res.x))

# Create an equilateral table for 3 classes (species of iris) and between the range 0 to 1.  This is used
# to decide the two output nodes into a species number.
eq = Equilateral(3, 0, 1)

# Display the final validation.  We show all of the iris data as well as the predicted species.
for i in xrange(0, len(training_input)):
    input_data = training_input[i]
    # Compute the output from the RBF network
    output_data = network.compute_regression(input_data)
    ideal_data = training_ideal[i]
    # Decode the two output neurons into a class number.
    class_id = eq.decode(output_data)
    print(str(input_data) + " -> " + inv_classes[class_id] + ", Ideal: " + ideal_species[i])

print(res.x)