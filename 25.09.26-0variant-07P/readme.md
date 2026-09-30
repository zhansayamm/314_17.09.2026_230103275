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

# 2.5 Analytical Questions & Lab Report Prompts

1.1 Explain why the thread IDs print in non-sequential order across consecutive runs. Which component of the operating system and CPU architecture governs this behavior?

The thread IDs print in non-sequential order because thread execution scheduling is handled by the operating system's preemptive scheduler (on macOS, the XNU/Mach kernel scheduler), not by the program itself. When multiple threads are created, the OS scheduler decides which thread runs on which CPU core and for how long (a "time slice" or "quantum"), based on factors like priority, load balancing across cores, and I/O wait states. Since worker_task includes time.sleep(0.001 \* (thread_id % 3)), some threads voluntarily yield the CPU for different durations, causing the scheduler to resume them in an order that depends on real-time timing rather than the order they were logically created (thread_id). Additionally, due to Python's Global Interpreter Lock (GIL), only one thread executes Python bytecode at a time, and the GIL's own scheduling policy (which releases and reacquires the lock periodically) interacts with the OS scheduler to further randomize execution order.

1.2 What performance penalty occurs when P exceeds the number of physical hardware cores? Explain the concepts of context switching, thread state preservation, and cache thrashing
When the number of threads (P) exceeds the number of physical cores, the OS must time-share the available cores among more threads than can run simultaneously. This introduces three penalties:
Context Switching: The CPU must repeatedly stop executing one thread and switch to another. Each switch requires saving the current thread's register state, program counter, and stack pointer, then loading another thread's saved state — this overhead consumes CPU cycles that do no useful work.
Thread State Preservation: To resume a thread correctly later, the OS must preserve its full execution context (registers, memory pointers, thread-local storage) in the process control block. The more threads are oversubscribed, the more frequently this save/restore cycle happens, increasing overhead relative to actual computation.
Cache Thrashing: Each core has a small, fast L1/L2 cache holding recently used data. When the scheduler switches which thread runs on a core, the new thread's data likely isn't in cache yet ("cold cache"), forcing expensive reloads from L3 cache or main memory. With many threads competing for the same cores, cache lines are evicted and reloaded constantly, causing a sharp drop in effective throughput — this is cache thrashing.
Together, these effects mean wall-clock time grows non-linearly once P > physical core count, rather than staying flat or improving.

1.3 In OpenMP, what is the role of the implicit barrier at the end of a parallel region? What hazards would arise if worker threads continued executing into subsequent code blocks before reaching the barrier?
The implicit barrier at the end of an OpenMP parallel region forces all threads in the team to wait until every thread has finished its portion of the parallel work, before any thread is allowed to proceed past that point. This guarantees a well-defined synchronization boundary: the master thread only resumes serial execution once all worker threads have completed and rejoined.
If threads were allowed to continue into subsequent code blocks without this barrier, several hazards would arise:
Race conditions on shared data: A fast thread might read a shared variable that a slower thread hasn't finished writing yet, producing incorrect or non-deterministic results.
Incomplete results used prematurely: Downstream computation might consume partial or stale data from the parallel region, since not all contributions have been committed.
Non-reproducible program behavior: Program correctness would depend on arbitrary thread scheduling timing rather than logical program order, making bugs extremely hard to reproduce and debug.
In the Python code, this barrier is emulated by calling f.result() on every future — this blocks the main thread until each worker has completed, replicating OpenMP's implicit synchronization.

1.4 Contrast a hardware execution thread (Hyper-Threading / SMT) with an operating system kernel thread and a language-level green/virtual thread

Hardware thread (SMT/Hyper-Threading) - A physical CPU core is duplicated at the register/instruction-fetch level to expose two (or more) logical execution contexts per core. These logical threads share the same execution units (ALUs, cache), so true parallel computation is limited — SMT mainly hides latency (e.g., during cache misses) by letting another logical thread's instructions fill idle execution slots.
OS kernel thread - A scheduling unit managed directly by the operating system kernel. Each kernel thread has its own stack, register state, and is independently scheduled onto a physical/logical core by the OS scheduler. Context switches between kernel threads require a trap into kernel mode, making them relatively expensive compared to lighter-weight alternatives. Python's threading module creates kernel threads (visible as native OS TIDs in the lab output).
Language-level green/virtual thread - A lightweight thread implemented and scheduled entirely in user space by a language runtime (e.g., Go's goroutines, Java's virtual threads, Erlang processes), without direct 1:1 mapping to OS kernel threads. Many green threads can be multiplexed onto a small number of kernel threads, making context switching far cheaper (no kernel trap needed) and allowing millions of concurrent green threads, at the cost of the runtime needing its own scheduler.

# 3.4 Step-by-Step Student Implementation Tasks

Task 2.1: Race Condition Quantification :
===== Task 2.1: Race Condition Quantification (Forced Manifestation) =====
P | Time (s) | Pi (calculated) | Absolute Error

---

1 | 0.0946 | 3.141592653592 | 2.10e-12
2 | 0.0885 | 1.288402217529 | 1.85e+00
4 | 0.1575 | 0.721073999075 | 2.42e+00
8 | 0.2199 | 0.271668783860 | 2.87e+00
At P=1, no race condition can occur since only one thread accesses total_sum, so the error remains at normal floating-point rounding noise (~2.10e-12). At P≥2, the calculated Pi value diverges drastically from the true value, and the absolute error grows sharply with increasing P (1.85 at P=2, up to 2.87 at P=8).
This happens because of the lost update problem: each thread performs the update in three unsynchronized steps — read total_sum, compute the new value, then write it back. When multiple threads execute this sequence concurrently without synchronization, one thread's write can overwrite another thread's update that occurred in between, silently discarding it. As P increases, more threads compete simultaneously for the same shared variable, increasing both the frequency of these read-write collisions and the total number of updates lost. Consequently, a growing fraction of the 4/(1+x²) terms never get incorporated into the final sum, which explains why the numerical error scales upward with the number of threads.

Task 2.2: Critical Section Overhead :
===== Task 2.2: Critical Section Overhead =====
Serial Baseline: Pi = 3.141592653590 | Time = 0.0770s | Error = 2.89e-14

P | Time (s) | Pi | Error | Ideal Time (s) | Lock Overhead %

1 | 0.2366 | 3.141592653590 | 2.89e-14 | 0.0770 | 207.4%
2 | 0.1871 | 3.141592653590 | 1.73e-13 | 0.0385 | 386.3%
4 | 0.1883 | 3.141592653590 | 5.24e-14 | 0.0192 | 879.0%
8 | 0.1985 | 3.141592653590 | 1.60e-14 | 0.0096 | 1963.7%

While the critical section guarantees correctness (Pi error stays within normal floating-point precision at every P), it completely eliminates the performance benefit of parallelism. Even at P=1, overhead reaches 207% due to the fixed cost of lock acquire/release calls. As P increases, execution time stays essentially flat (~0.19–0.20s) instead of decreasing, because the lock is acquired on every single iteration (1,000,000 times), forcing all threads to serialize access to total_sum one at a time. This turns the "parallel" computation back into an effectively sequential one, with additional mutex management overhead on top — explaining why lock contention overhead grows dramatically (up to ~1964% at P=8) rather than shrinking as more threads are added.

Task 2.3: Strong Scaling Benchmark:
===== Task 2.3: Strong Scaling Benchmark (Parallel Reduction) =====
Serial Baseline: Pi = 3.141592653590 | Avg Time (5 trials) = 0.0942s
Hardware logical cores detected: 8

## P | Trial Times (s) | Avg Time (s) | Speedup S(P) | Efficiency E(P)

1 | 0.0956, 0.0950, 0.0950, 0.0950, 0.0949 | 0.0951 | 0.99 | 99.09%
2 | 0.0501, 0.0492, 0.0500, 0.0491, 0.0495 | 0.0496 | 1.90 | 95.05%
4 | 0.0274, 0.0262, 0.0257, 0.0255, 0.0274 | 0.0264 | 3.57 | 89.16%
8 | 0.0200, 0.0187, 0.0195, 0.0168, 0.0166 | 0.0183 | 5.15 | 64.35%
16 | 0.0193, 0.0176, 0.0166, 0.0197, 0.0197 | 0.0186 | 5.07 | 31.70% (capped at 8)

The benchmark shows near-linear speedup up to P=4 (efficiency ≥89%), consistent with Amdahl's Law for a workload with a very small serial fraction. Efficiency drops sharply at P=8 (64.35%) as fixed overheads (thread spawning, JIT dispatch, final reduction-tree merge) become proportionally larger relative to the shrinking per-thread workload. At P=16, execution time plateaus at the same level as P=8 because the machine only has 8 logical cores — Numba silently caps actual thread usage at 8, so the reported efficiency (31.70%) is an artifact of dividing by P=16 rather than reflecting true additional parallelism; this illustrates the hard ceiling imposed by physical hardware resources on strong scaling.

Task 2.4: Speedup & Efficiency Modeling:
P S(P) actual S(P) ideal E(P)
1 0.99 1 99.09%
2 1.90 2 95.05%
4 3.57 4 89.16%
8 5.15 8 64.35%
16 5.07 16 31.70%

# 3.5 Analytical Questions & Lab Report Prompts

2.1 Explain at the CPU assembly level what occurs during a non-atomic read-modify-write operation (e.g., LOAD, ADD, STORE). Why does thread interleaving cause lost updates in Variant A?
A high-level statement like total_sum += value compiles into (at minimum) three separate machine instructions:
LOAD R1, [total_sum] ; load current value from memory into a register
ADD R1, R1, value ; add the term to the register
STORE [total_sum], R1 ; write the updated register back to memory
Each of these three instructions executes independently and can be interrupted between any of them — there is no hardware guarantee that all three complete as a single indivisible unit. If Thread A executes LOAD and is then preempted (context switch) before executing STORE, Thread B can execute its own complete LOAD-ADD-STORE sequence on the same memory address in the meantime. When Thread A resumes, it still holds the stale value it loaded earlier in its register, computes on top of that stale value, and writes back a result that overwrites Thread B's update entirely — Thread B's contribution to the sum is permanently lost even though it executed correctly. This is exactly why Variant A's calculated Pi diverges further from the true value as P increases: more concurrent threads mean more opportunities for this LOAD/STORE interleaving to occur, and each occurrence discards one thread's computed term from the final sum.

2.2 Why is a binary reduction tree O(log P) significantly superior in
scaling compared to a centralized critical section O(P)?
In a centralized critical section (Variant B), every one of the P threads must acquire the same single lock to update the shared accumulator, meaning all updates are fully serialized — the total synchronization cost grows linearly, O(P), because threads literally queue up one after another regardless of how many cores are available. Doubling P doubles the number of threads waiting in that single queue, so contention (and wasted waiting time) scales directly with thread count.
A binary reduction tree, by contrast, gives each thread its own private, lock-free local accumulator during the main computation phase — no synchronization happens at all while the bulk of the work is done. Only at the end do partial sums get combined, and this combination happens in pairs simultaneously across multiple tree levels: P partial sums become P/2 after one combining step, then P/4, then P/8, and so on, requiring only ⌈log₂P⌉ sequential combining steps total. Since each level's pairwise combinations can happen in parallel with each other, the synchronization overhead scales with O(log P) instead of O(P) — for P=64, that's only 6 combining steps instead of 64 threads queuing for one lock. This is why reduction trees scale dramatically better as thread count grows.

2.3 According to Amdahl's Law, if 5% of a program's execution time is
strictly serial (non-parallelizable), what is the theoretical maximum speedup achievable with an
infinite number of processors? If your measured speedup flattens earlier, what secondary
architectural factors are responsible?
Amdahl's Law states:
$$S(P) = \frac{1}{(1-f) + \frac{f}{P}}$$
where f is the parallelizable fraction. If the serial fraction is 5% (f = 0.95 parallelizable), then as P → ∞, the parallel term f/P vanishes, leaving:
$$S(\infty) = \frac{1}{1 - 0.95} = \frac{1}{0.05} = 20\times$$
So the theoretical maximum speedup is 20x, regardless of how many processors are added — the strictly serial 5% becomes an absolute floor on total execution time.
In my measured results (Task 2.3), speedup flattened much earlier, around P=8, at only ~5.15x rather than approaching 20x. Several secondary architectural factors explain this earlier-than-theoretical plateau:
Memory bandwidth saturation: all cores share the same memory bus/last-level cache; beyond a certain thread count, cores stall waiting for data rather than computing.
Thread management overhead: spawning, scheduling, and joining threads costs real time that isn't part of the "useful" parallel fraction assumed by the idealized Amdahl model.
Reduction/synchronization overhead: even the O(log P) tree-combining step at the end of calc_pi_reduction adds real, non-zero serial time that grows (slowly) with P.
Physical core limit: the test machine has only 8 logical cores, so beyond P=8 there is no additional hardware parallelism available at all — the OS must time-share the same 8 cores among more software threads, adding scheduling overhead without any computational benefit.
Cache effects: splitting work into smaller per-thread chunks as P grows can increase cache misses relative to the single large sequential pass.

2.4 How do modern 64-bit multi-core processors implement
atomic memory updates at the hardware bus level (e.g., bus snooping, MESI cache locking, LOAD-
LINK/STORE-CONDITIONAL)?
Modern multi-core CPUs implement atomicity through a combination of cache coherence protocols and specialized instructions, rather than locking the entire memory bus (which older single-core-era architectures did via a literal LOCK# bus signal):
MESI Protocol & Cache Line Locking: Each cache line is tagged with one of four states — Modified, Exclusive, Shared, Invalid. To perform an atomic update (e.g., LOCK ADD on x86), the core must first acquire the cache line in the Exclusive or Modified state, which requires broadcasting an invalidation request to all other cores' caches holding that line. Other cores' copies transition to Invalid, guaranteeing only one core can modify the line at a time. The atomic instruction locks that specific cache line for the duration of the read-modify-write, rather than locking the entire shared bus.
Bus Snooping: Every core's cache controller continuously "snoops" (monitors) the shared interconnect/bus for read and write broadcasts from other cores. This lets a core detect immediately when another core has modified a cache line it also holds, triggering the MESI state transition (e.g., Shared → Invalid) needed to maintain coherence.
LOAD-LINK / STORE-CONDITIONAL (LL/SC): Used on architectures like ARM and RISC-V (as an alternative to x86's LOCK-prefixed instructions), LOAD-LINK reads a memory location and registers a "reservation" on that address. STORE-CONDITIONAL only succeeds in writing back if no other core has written to that address since the LOAD-LINK — otherwise the store fails and software must retry the whole operation in a loop. This avoids ever locking the bus or cache line for an extended period; it optimistically assumes no conflict and detects violations after the fact.
Together, these mechanisms let atomic operations (atomic directive, hardware compare-and-swap, etc.) execute correctly across cores without stalling the entire system bus, unlike older bus-locking approaches — which is why #pragma omp atomic is significantly cheaper than #pragma omp critical: it relies on fast, localized cache-line-level hardware locking (MESI) or optimistic LL/SC retry, rather than a full OS-level mutex.

# 4.5 Analytical Questions & Lab Report Prompts

3.1 Why does dynamic scheduling with chunk size C = 1
exhibit poor performance despite offering theoretically perfect load balancing? Identify the exact
hardware resource being contested.
With C=1, every single row requires a separate trip to the shared work queue: queue.get_nowait(), followed later by queue.task_done(). Each of these queue operations requires acquiring an internal lock to safely coordinate access across threads — in CPython this lock interacts directly with the GIL (Global Interpreter Lock). With P threads all hammering the same queue for a tiny, cheap unit of work (one row), the overhead of repeatedly acquiring and releasing this lock, plus the GIL handoff between threads, can exceed the actual computation time per chunk. The contested hardware/software resource here is specifically the queue's internal lock (and by extension the GIL) — threads spend more time waiting to synchronize access to this single shared coordination point than doing useful Mandelbrot computation. This is the classic trade-off: finer granularity gives theoretically perfect balance (any leftover work is always small), but the synchronization overhead per unit of work dominates when the chunk is too small.

3.2 In static scheduling, which thread ranks typically become
stragglers when rendering the central section of the Mandelbrot set? Explain using the geometry
of the complex plane.
The Mandelbrot set's densest, most computationally expensive region (points requiring the full 1000 iterations before failing to escape) is concentrated near the vertical center of the complex plane — around the real axis and the large connected "cardioid and bulb" body of the set, roughly in the vertical middle third of the rendered image (since the set is symmetric about the real axis and centered near the origin). With contiguous static row partitioning (the default prange behavior, or equal-sized contiguous blocks), the threads assigned to the middle rows of the image — i.e., the threads with middle-ranked thread IDs (for P threads numbered 0 to P-1, roughly threads at index P/2 − 1 and P/2) — inherit the rows passing through the densest part of the set. These middle-rank threads become the stragglers, while thread rank 0 (top rows) and thread rank P-1 (bottom rows) typically finish early, since the top and bottom edges of the rendered view are mostly empty space outside the set (fast-escaping points).

3.3 Describe the mathematical mechanism of OpenMP's
schedule(guided, chunk). How does it combine the low overhead of static scheduling with the
dynamic adaptation of small chunking?
schedule(guided, chunk) dynamically computes chunk sizes that exponentially decrease over the course of execution. At any point, when a thread requests new work, the size of the next chunk handed out is approximately:
$$\text{chunk\_size} = \max\left(\text{chunk}, \left\lceil \frac{\text{remaining\_iterations}}{P} \right\rceil\right)$$
where remaining_iterations is whatever portion of the total loop has not yet been assigned, and P is the thread count. Initially, when almost all iterations remain unassigned, this formula produces large chunks (similar to static scheduling), minimizing the number of trips to the shared work queue and keeping synchronization overhead low. As execution progresses and remaining_iterations shrinks, the formula automatically produces progressively smaller chunks, down to the specified minimum chunk size. This tapering means that near the end of the loop, when load imbalance would otherwise leave some threads badly overloaded with a large leftover block, the remaining work is broken into fine-grained pieces that can be distributed evenly among any threads still working — exactly when fine balancing matters most, and exactly when the overhead of small chunks matters least (since there's little total work left, the relative synchronization cost is small too).

3.4 Formulate a rule-of-thumb heuristic for
software engineers: under what workload characteristics should one select Static vs. Dynamic vs.
Guided loop scheduling?
Static: Use when per-iteration cost is uniform or highly predictable, and the total iteration count is known in advance. Since there's no runtime coordination overhead, this is the fastest option whenever load imbalance is not a concern — e.g., dense matrix operations, uniform pixel filters, or any loop where every iteration does roughly the same amount of work. Rule of thumb: "If all iterations cost about the same, always use static — any other scheduler only adds overhead without benefit."
Dynamic: Use when per-iteration cost is highly unpredictable or irregular, and there is no known pattern to exploit — e.g., processing a queue of tasks of wildly varying, essentially random size, or workloads where the cost distribution changes at runtime based on input data. Choose a chunk size large enough to amortize queue overhead (not C=1, per Question 3.1) but small enough to still balance load — often found empirically by benchmarking a few chunk sizes. Rule of thumb: "If iteration cost is unpredictable and chunk overhead can be kept small relative to chunk work, use dynamic."
Guided: Use when per-iteration cost is non-uniform but has some spatial/temporal structure (like the Mandelbrot set, where cost varies smoothly across the image rather than randomly) — guided's large-to-small taper minimizes overhead early on while still catching stragglers late in execution. It's a strong default choice when you're unsure whether static or dynamic is better, since it adapts automatically without requiring you to hand-tune a fixed chunk size. Rule of thumb: "When workload imbalance exists but follows a gradual/structured pattern rather than pure randomness, prefer guided over dynamic — you get most of dynamic's balancing benefit with less scheduling overhead."
