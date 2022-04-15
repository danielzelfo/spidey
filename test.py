import timeit
import time

timesl = 5

start = timeit.default_timer()

time.sleep(3)


newtime = timesl - timeit.default_timer() + start

print(newtime)