#Questions:
#1 Look at your row for 16 threads. Why didn't your 8-core CPU run twice as fast as 8
threads?
In Python tasks are compited in a row because of the GLI. That's why the 8th and 16th threads's runtimes = 11.3-11.5. We don't have here a real parallelism. GIL keeps only ony task in active. More threads , then more overheads. So this actually shows, why we have a slow efficiancy by the end not speed ups.

#
