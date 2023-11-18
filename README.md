# Genetic-Sudoku-Algorithm
Utilizes a genetic algorithm to solve a 4x4 sudoku.

Contains two selection methods - Rank Based Selection and Tournament Selection.

Tournament selection proves to be slower in terms of generations per second but is overall faster as it is more efficient in each generation compared to rank-based selection where it is much faster in creating generations but worse at getting the right solution.

Tournament selection also does not seem to have the issue of pre-mature convergence as rank-based selection did as well as that it manages to get out of local minima much quicker than rank-based selection.
