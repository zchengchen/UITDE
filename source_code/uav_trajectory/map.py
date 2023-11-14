import random
import matplotlib.pyplot as plt
import numpy as np
import math

x = [] # x coordinate of sensing tasks.
y = [] # y coordinate of sensing tasks.
num_undef_worker = [] # The number of undefined workers had reported data of a certain sensing task.
area = 2.25 # We set up a 150*150 map in our manuscript, so the area of the map is 2.25 km^2 (the scale is 1: 10m).
num_tasks = int(area / 2.25 * 100.0) # The number of sensing tasks increases proportionally with the size of the map. The original map is 2.25 km^2 and contains 100 sensing tasks.

for i in range(0, num_tasks): # 100 sensing tasks in 150 * 150 map.
    # Ramdonly generate x and y coordiates for a certain sensing task.
    x.append(random.random() * (math.sqrt(area) * 1000.0 / 10.0))
    y.append(random.random() * (math.sqrt(area) * 1000.0 / 10.0))
    # We assume that the closer to the center point the higher the number of undefined workers [Gao et al. 2023].
    # H. Gao, J. Feng, Y. Xiao, B. Zhang and W. Wang, "A UAV-Assisted Multi-Task Allocation Method for Mobile Crowd Sensing," in IEEE Transactions on Mobile Computing, vol. 22, no. 7, pp. 3790-3804, 1 July 2023, doi: 10.1109/TMC.2022.3147871.
    num_undef_worker.append(random.randint(min(10, int(200/((x[i]-75)**2 + (y[i]-75)**2))), 10))

# Output coordinates to map.csv.
with open("map.csv", "w") as f:
    for i in range(0, num_tasks):
        f.write(str(x[i]) + ", " + str(y[i]) + ", " + str(num_undef_worker[i]) + "\n")

# # Code for visualize map.
# plt.scatter(x, y, s=[n*10 for n in num_undef_worker])
# plt.xlabel('x coordinate', fontsize=18)
# plt.ylabel('y coordinate', fontsize=18)
# plt.grid()
# plt.rc('font',family='Times New Roman')
# plt.xlim(0, 155)
# plt.ylim(0, 155)
# plt.show()