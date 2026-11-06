1.Conjugate Gradient / iterative solvers (e.g. Jacobi).
The number of iterations grows with the grid size N, so total runtime grows even if work per core is constant.
Each iteration also needs global dot-product reductions, which cost O(log P).
2.FFT / parallel sorting (all-to-all communication).
Every node must exchange data with every other node.
Time is limited by bisection bandwidth, which doesn’t grow as fast as P, so communication time increases with P.
Gustafson assumes the serial and overhead time stay constant as the problem grows. Here, growing the problem changes the algorithm’s cost (more iterations) or the communication pattern (more data movement), so runtime isn’t constant.
