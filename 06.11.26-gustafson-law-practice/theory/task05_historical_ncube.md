Experiment: Gustafson, Montry, and Benner (Sandia, 1988) ran three real applications on a 1,024-processor nCUBE 10 (beam stress analysis, wave motion, fluid flow with baffles) and achieved scaled speedups of roughly 1,000×.
Why it seemed impossible: with s ≈ 0.4%, Amdahl gives S = 1 / (0.004 + 0.996/1024) ≈ 201, and an absolute cap of 250.
How the ceiling was removed: the grid size was increased together with P. Serial work (I/O, setup) stayed nearly constant in absolute time, while parallel work grew. The serial fraction measured on the parallel machine was about 0.4-0.8%.
Verification: S = 1024 − 0.004·1023 ≈ 1020, consistent with the measurements.
Conclusion: Amdahl’s Law holds for fixed-size problems, but it does not describe real HPC practice, where problem size grows with the machine.
