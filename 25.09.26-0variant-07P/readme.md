# HIGH-PERFORMANCE & PARALLEL COMPUTING

# Lab 1: The Fork-Join Model, Team Creation, and Thread Scoping

2.4 Step-by-Step Student Implementation Tasks:
1.Outputs are in the task1.1-outputs.txt 2.
2.Results for every P in {1, 2, 4, 8, 16, 32, 64} :
1 : --- Forking a team of 1 threads ---
[Master] Logical Rank: 0 of 1 | Native OS TID: 1855954
--- Joined thread team. Execution returned to serial master ---
0,02s user 0,01s system 63% cpu 0,049 total

2 : --- Forking a team of 2 threads ---
[Master] Logical Rank: 0 of 2 | Native OS TID: 1857441
[Worker] Logical Rank: 1 of 2 | Native OS TID: 1857442
--- Joined thread team. Execution returned to serial master ---
0,04s user 0,01s system 41% cpu 0,128 total

4 : --- Forking a team of 4 threads ---
[Master] Logical Rank: 0 of 4 | Native OS TID: 1858091
[Worker] Logical Rank: 3 of 4 | Native OS TID: 1858093
[Worker] Logical Rank: 1 of 4 | Native OS TID: 1858092
[Worker] Logical Rank: 2 of 4 | Native OS TID: 1858091
--- Joined thread team. Execution returned to serial master ---
python3 lab_openmp_fork_join.py 0,03s user 0,01s system 68% cpu 0,062 total

8 : [Worker] Logical Rank: 6 of 8 | Native OS TID: 1858616
[Worker] Logical Rank: 1 of 8 | Native OS TID: 1858613
[Worker] Logical Rank: 4 of 8 | Native OS TID: 1858615
[Worker] Logical Rank: 7 of 8 | Native OS TID: 1858617
[Worker] Logical Rank: 2 of 8 | Native OS TID: 1858612
[Worker] Logical Rank: 5 of 8 | Native OS TID: 1858614
--- Joined thread team. Execution returned to serial master ---
0,03s user 0,01s system 45% cpu 0,099 total

16 : --- Forking a team of 16 threads ---
[Master] Logical Rank: 0 of 16 | Native OS TID: 1859232
[Worker] Logical Rank: 3 of 16 | Native OS TID: 1859234
[Worker] Logical Rank: 6 of 16 | Native OS TID: 1859236
[Worker] Logical Rank: 9 of 16 | Native OS TID: 1859238
[Worker] Logical Rank: 12 of 16 | Native OS TID: 1859240
[Worker] Logical Rank: 15 of 16 | Native OS TID: 1859242
[Worker] Logical Rank: 1 of 16 | Native OS TID: 1859232
[Worker] Logical Rank: 4 of 16 | Native OS TID: 1859235
[Worker] Logical Rank: 7 of 16 | Native OS TID: 1859237
[Worker] Logical Rank: 10 of 16 | Native OS TID: 1859238
[Worker] Logical Rank: 13 of 16 | Native OS TID: 1859240
[Worker] Logical Rank: 5 of 16 | Native OS TID: 1859234
[Worker] Logical Rank: 2 of 16 | Native OS TID: 1859233
[Worker] Logical Rank: 8 of 16 | Native OS TID: 1859236
[Worker] Logical Rank: 11 of 16 | Native OS TID: 1859239
[Worker] Logical Rank: 14 of 16 | Native OS TID: 1859241
--- Joined thread team. Execution returned to serial master ---
0,03s user 0,01s system 68% cpu 0,055 total

32 : --- Forking a team of 32 threads ---
[Master] Logical Rank: 0 of 32 | Native OS TID: 1859801
[Worker] Logical Rank: 3 of 32 | Native OS TID: 1859803
[Worker] Logical Rank: 6 of 32 | Native OS TID: 1859805
[Worker] Logical Rank: 9 of 32 | Native OS TID: 1859807
[Worker] Logical Rank: 12 of 32 | Native OS TID: 1859809
[Worker] Logical Rank: 15 of 32 | Native OS TID: 1859809
[Worker] Logical Rank: 18 of 32 | Native OS TID: 1859813
[Worker] Logical Rank: 21 of 32 | Native OS TID: 1859815
[Worker] Logical Rank: 24 of 32 | Native OS TID: 1859817
[Worker] Logical Rank: 27 of 32 | Native OS TID: 1859819
[Worker] Logical Rank: 30 of 32 | Native OS TID: 1859821
[Worker] Logical Rank: 1 of 32 | Native OS TID: 1859801
[Worker] Logical Rank: 4 of 32 | Native OS TID: 1859804
[Worker] Logical Rank: 7 of 32 | Native OS TID: 1859805
[Worker] Logical Rank: 10 of 32 | Native OS TID: 1859807
[Worker] Logical Rank: 13 of 32 | Native OS TID: 1859810
[Worker] Logical Rank: 16 of 32 | Native OS TID: 1859812
[Worker] Logical Rank: 19 of 32 | Native OS TID: 1859814
[Worker] Logical Rank: 22 of 32 | Native OS TID: 1859815
[Worker] Logical Rank: 25 of 32 | Native OS TID: 1859818
[Worker] Logical Rank: 28 of 32 | Native OS TID: 1859820
[Worker] Logical Rank: 31 of 32 | Native OS TID: 1859821
[Worker] Logical Rank: 2 of 32 | Native OS TID: 1859802
[Worker] Logical Rank: 5 of 32 | Native OS TID: 1859803
[Worker] Logical Rank: 8 of 32 | Native OS TID: 1859806
[Worker] Logical Rank: 11 of 32 | Native OS TID: 1859808
[Worker] Logical Rank: 23 of 32 | Native OS TID: 1859816
[Worker] Logical Rank: 26 of 32 | Native OS TID: 1859817
[Worker] Logical Rank: 14 of 32 | Native OS TID: 1859811
[Worker] Logical Rank: 17 of 32 | Native OS TID: 1859809
[Worker] Logical Rank: 20 of 32 | Native OS TID: 1859813
[Worker] Logical Rank: 29 of 32 | Native OS TID: 1859819
--- Joined thread team. Execution returned to serial master ---
0,03s user 0,01s system 69% cpu 0,056 total

64 : --- Forking a team of 64 threads ---
[Master] Logical Rank: 0 of 64 | Native OS TID: 1860519
[Worker] Logical Rank: 3 of 64 | Native OS TID: 1860521
[Worker] Logical Rank: 1 of 64 | Native OS TID: 1860519
[Worker] Logical Rank: 5 of 64 | Native OS TID: 1860522
[Worker] Logical Rank: 4 of 64 | Native OS TID: 1860521
[Worker] Logical Rank: 6 of 64 | Native OS TID: 1860519
[Worker] Logical Rank: 2 of 64 | Native OS TID: 1860520
[Worker] Logical Rank: 12 of 64 | Native OS TID: 1860526
[Worker] Logical Rank: 9 of 64 | Native OS TID: 1860521
[Worker] Logical Rank: 15 of 64 | Native OS TID: 1860521
[Worker] Logical Rank: 18 of 64 | Native OS TID: 1860521
[Worker] Logical Rank: 21 of 64 | Native OS TID: 1860531
[Worker] Logical Rank: 24 of 64 | Native OS TID: 1860533
[Worker] Logical Rank: 7 of 64 | Native OS TID: 1860524
[Worker] Logical Rank: 27 of 64 | Native OS TID: 1860534
[Worker] Logical Rank: 13 of 64 | Native OS TID: 1860527
[Worker] Logical Rank: 10 of 64 | Native OS TID: 1860519
[Worker] Logical Rank: 16 of 64 | Native OS TID: 1860528
[Worker] Logical Rank: 30 of 64 | Native OS TID: 1860535
[Worker] Logical Rank: 19 of 64 | Native OS TID: 1860530
[Worker] Logical Rank: 8 of 64 | Native OS TID: 1860522
[Worker] Logical Rank: 33 of 64 | Native OS TID: 1860528
[Worker] Logical Rank: 22 of 64 | Native OS TID: 1860531
[Worker] Logical Rank: 36 of 64 | Native OS TID: 1860537
[Worker] Logical Rank: 39 of 64 | Native OS TID: 1860528
[Worker] Logical Rank: 11 of 64 | Native OS TID: 1860520
[Worker] Logical Rank: 45 of 64 | Native OS TID: 1860520
[Worker] Logical Rank: 28 of 64 | Native OS TID: 1860534
[Worker] Logical Rank: 42 of 64 | Native OS TID: 1860528
[Worker] Logical Rank: 51 of 64 | Native OS TID: 1860543
[Worker] Logical Rank: 32 of 64 | Native OS TID: 1860519
[Worker] Logical Rank: 31 of 64 | Native OS TID: 1860536
[Worker] Logical Rank: 44 of 64 | Native OS TID: 1860540
[Worker] Logical Rank: 49 of 64 | Native OS TID: 1860542
[Worker] Logical Rank: 46 of 64 | Native OS TID: 1860520
[Worker] Logical Rank: 25 of 64 | Native OS TID: 1860533
[Worker] Logical Rank: 60 of 64 | Native OS TID: 1860533
[Worker] Logical Rank: 29 of 64 | Native OS TID: 1860527
[Worker] Logical Rank: 43 of 64 | Native OS TID: 1860539
[Worker] Logical Rank: 41 of 64 | Native OS TID: 1860537
[Worker] Logical Rank: 48 of 64 | Native OS TID: 1860541
[Worker] Logical Rank: 53 of 64 | Native OS TID: 1860544
[Worker] Logical Rank: 14 of 64 | Native OS TID: 1860526
[Worker] Logical Rank: 20 of 64 | Native OS TID: 1860521
[Worker] Logical Rank: 34 of 64 | Native OS TID: 1860535
[Worker] Logical Rank: 17 of 64 | Native OS TID: 1860529
[Worker] Logical Rank: 57 of 64 | Native OS TID: 1860542
[Worker] Logical Rank: 40 of 64 | Native OS TID: 1860531
[Worker] Logical Rank: 63 of 64 | Native OS TID: 1860547
[Worker] Logical Rank: 26 of 64 | Native OS TID: 1860524
[Worker] Logical Rank: 37 of 64 | Native OS TID: 1860522
[Worker] Logical Rank: 38 of 64 | Native OS TID: 1860538
[Worker] Logical Rank: 23 of 64 | Native OS TID: 1860532
[Worker] Logical Rank: 54 of 64 | Native OS TID: 1860519
[Worker] Logical Rank: 35 of 64 | Native OS TID: 1860530
[Worker] Logical Rank: 55 of 64 | Native OS TID: 1860536
[Worker] Logical Rank: 52 of 64 | Native OS TID: 1860543
[Worker] Logical Rank: 58 of 64 | Native OS TID: 1860545
[Worker] Logical Rank: 56 of 64 | Native OS TID: 1860540
[Worker] Logical Rank: 61 of 64 | Native OS TID: 1860533
[Worker] Logical Rank: 47 of 64 | Native OS TID: 1860534
[Worker] Logical Rank: 50 of 64 | Native OS TID: 1860528
[Worker] Logical Rank: 59 of 64 | Native OS TID: 1860520
[Worker] Logical Rank: 62 of 64 | Native OS TID: 1860546
--- Joined thread team. Execution returned to serial master ---
0,04s user 0,02s system 60% cpu 0,092 total
