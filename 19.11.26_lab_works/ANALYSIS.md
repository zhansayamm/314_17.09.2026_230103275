# Q1. MESI transitions (stride = 1)

buffer[0] and buffer[1] sit in the same cache line, so the cores fight over the line even though they never touch the same variable.
Core 0 stores to buffer[0]. The line is Invalid (I) in its cache, so it sends a Read-For-Ownership (RFO) request, gets the line, and the line goes to Modified (M). If the line was already Exclusive (E), the move to M is silent.
Core 1 stores to buffer[1]. Its copy is I, so it sends its own RFO.
Core 0 snoops the RFO, writes its dirty line back or forwards it, and its copy goes M → I. Core 1’s copy goes I → M.
Core 0’s next store finds its line in I, and the cycle repeats on every store. Shared (S) barely appears, because there are only writes and no read-sharing.
Core 1’s store sits in the store buffer and can only drain to L1 once the core owns the line (M or E). While the RFO is in flight (tens of ns), that store cannot commit, the stores behind it queue up, the buffer fills, and the core stalls.

# Q2. Measured slowdown

Mode ns per update
stride 1 2.80
stride 4 3.02
stride 8 2.73
stride 16 2.65
register-private 2.09
Slowdown stride 1 vs stride 8: 167.8 / 163.7 ms ≈ 1.025×.
Coherence penalty (stride 1 − stride 8): about 0.07 ns per update.
Memory read-modify-write cost (stride 8 − private): about 0.63 ns per update.
The false-sharing effect is weak on this machine. The loop is dominated by the xorshift dependency chain (about 2.1 ns per iteration), so memory stalls are mostly hidden. M1 cores in a cluster share an L2, which makes line transfers cheap, and macOS gives no thread pinning, so threads were unpinned.

# Q3. Stride 8 vs stride 16 and 128-byte pairing

Stride 8 gives 2.73 ns and stride 16 gives 2.65 ns, so stride 16 is about 3% faster.
The manifest reports a 128-byte cache line (Apple M1). Stride 8 (64-byte spacing) puts threads 0 and 1 in one line and threads 2 and 3 in another, so pairwise false sharing remains. Stride 16 (128-byte spacing) gives each thread its own line, and it is the first fully isolated layout.
On x86 the adjacent-line prefetcher pairs an even 64-byte line with its odd neighbour into a 128-byte sector. Two threads 64 bytes apart can land in the same pair, so a write by one core invalidates the prefetched neighbour line held by the other (a secondary invalidation). 64-byte padding can still suffer this, while 128-byte padding avoids it.

# Q4. Register promotion vs real memory stores

A compiler (LLVM) can hoist buffer[slot] out of the loop. It loads the value once before the loop, accumulates in a register, and stores once after the loop. This is legal when nothing else in the loop may alias that address. I checked a plain buffer[slot] += x loop, and it compiled exactly that way, which would remove all memory traffic and hide false sharing.
The xorshift data dependency does not prevent this. What prevents it is an opaque, practically-never-taken branch if v == 0xFFFF…FFFF: buffer[other] = x. The compiler cannot prove the branch is never taken, so it must assume buffer[other] might alias buffer[slot], and the value has to stay in memory. Numba has no volatile, so this is the workaround.
In the IR (worker_strided_accumulate.ll), the loop body contains load i64, add, and store i64 in the same basic block, with a phi for the loop counter (loop_rmw_blocks: 2). There are no Python C-API calls, so it is native i64 code.

# Q5. GIL vs nogil=True

With ordinary Python threads, the GIL lets only one thread run bytecode at a time. Two cores never store to the shared line simultaneously, so there is no cache-line ping-pong and no false sharing.
Adding threads makes it slower, not faster, because of software lock contention. Threads wait for the GIL, hand it over, and pay context-switch overhead. A single interpreted update costs tens of ns, which swamps any cache effect.
GIL contention is a software queue where threads actually wait. Cache-line contention is a hardware effect where threads run truly in parallel on different cores, but the line bounces between their caches. nogil=True releases the GIL, so the hardware effect becomes visible.
