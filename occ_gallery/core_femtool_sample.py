from OCC.Core.FEmTool import FEmTool_SparseMatrix, FEmTool_LinearTension, FEmTool_ListOfVectors, FEmTool_HAssemblyTable
from OCC.Core.GeomAbs import GeomAbs_C1
from OCC.Core.math import math_Vector, math_Matrix
import numpy as np


def linear_tension_example():
    # Create a Linear Tension object with 3 degrees of freedom and C1 continuity
    linear_tension = FEmTool_LinearTension(3, GeomAbs_C1)

    # Create a vector and matrix for testing
    n1 = 5
    n2 = 5
    vec_b = math_Vector(1, n1)
    mat = math_Matrix(1, n1, 1, n2)

    # Fill the vector and matrix with random values
    for i in range(vec_b.Lower(), vec_b.Upper() + 1):
        vec_b.SetValue(i, np.random.rand())
    for i in range(mat.LowerRow(), mat.UpperRow() + 1):
        for j in range(mat.LowerCol(), mat.UpperCol() + 1):
            mat.SetValue(i, j, np.random.rand())

    # Perform operations
    gradient = linear_tension.Gradient(2, vec_b)
    hessian = linear_tension.Hessian(3, 3, mat)
    value = linear_tension.Value()

    print("Gradient:", gradient)
    print("Hessian:", hessian)
    print("Value:", value)


def sparse_matrix_example():
    # Create a Sparse Matrix object
    sparse_matrix = FEmTool_SparseMatrix(True)

    # Create vectors for solving Ax = b
    n = 5
    vec_x = math_Vector(1, n)
    vec_b = math_Vector(1, n)

    # Fill vec_b with random values
    for i in range(vec_b.Lower(), vec_b.Upper() + 1):
        vec_b.SetValue(i, np.random.rand())

    # Solve the sparse matrix equation (dummy example, no actual matrix setup here)
    sparse_matrix.Solve(vec_b, vec_x)

    # Print the solution vector
    print("Solution vector x:")
    for i in range(vec_x.Lower(), vec_x.Upper() + 1):
        print(f"x[{i}] = {vec_x.Value(i)}")


def list_of_vectors_example():
    """
    Demonstrates the usage of FEmTool_ListOfVectors.
    """
    # Create an instance of FEmTool_ListOfVectors
    list_of_vectors = FEmTool_ListOfVectors()

    # Create and append math_Vector objects
    for i in range(3):
        vec = math_Vector(1, 5)  # Create a vector of size 5
        for j in range(vec.Lower(), vec.Upper() + 1):
            vec.SetValue(j, np.random.rand())  # Fill with random values
        list_of_vectors.Append(vec)

    # Iterate through the list and print the vectors
    print("List of Vectors:")
    for i in range(list_of_vectors.Size()):
        vec = list_of_vectors.Value(i + 1)  # Access vectors (1-based index)
        print(f"Vector {i + 1}:")
        for j in range(vec.Lower(), vec.Upper() + 1):
            print(f"  {vec.Value(j)}")


def h_assembly_table_example():
    """
    Demonstrates the usage of FEmTool_HAssemblyTable.
    """
    # Create an instance of FEmTool_HAssemblyTable
    assembly_table = FEmTool_HAssemblyTable()

    # Access the internal array (dummy example, as actual usage depends on OpenCASCADE setup)
    try:
        array2 = assembly_table.Array2()
        print("Accessed Array2 from FEmTool_HAssemblyTable.")
    except Exception as e:
        print(f"Error accessing Array2: {e}")


# Run examples
if __name__ == "__main__":
    # print("Running Linear Tension Example:")
    # linear_tension_example()

    # print("\nRunning Sparse Matrix Example:")
    # sparse_matrix_example()

    print("\nRunning FEmTool_ListOfVectors Example:")
    list_of_vectors_example()

    print("\nRunning FEmTool_HAssemblyTable Example:")
    h_assembly_table_example()
