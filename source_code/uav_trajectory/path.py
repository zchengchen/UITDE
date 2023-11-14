import numpy as np
import matplotlib.pyplot as plt
import math
import copy

x = [] # x coordinate of sensing tasks.
y = [] # y coordinate of sensing tasks.
num_undef_worker = [] # The number of undefined workers had reported data of a certain sensing task.
data = [] # Data is loaded from map.csv, which contains the locations of tasks and the number of undefined workers. You can read the details in README.
flight_duration = 800 # The flight duration of UAVs. The scale is 1: 10m. So if flight_duration = 800, it means the maximum flight distance of UAVs is 8km.
num_available_UAVs = 5 # The number of UAVs available for collecting data.

# Load data from map.csv. 
csv_data = np.loadtxt('map.csv', delimiter=',')
for i in range(0, len(csv_data)):
    x.append(csv_data[i][0])
    y.append(csv_data[i][1])
    num_undef_worker.append(int(csv_data[i][2]))
    data.append({"x": csv_data[i][0], "y": csv_data[i][1], "num_udef": int(csv_data[i][2])}) # "num_udef" refers to number of undefined workers.
data.sort(key=lambda x: x["num_udef"], reverse=True) # Sort the data for later binary search.
# print(data)


max_udef = data[0]["num_udef"] # After sorting the list, the first term of the list data is the sensing task for which the most number of undefined workers report data.
max_tasks = len(data) # How many tasks need to be collected data.

# A function used for calcualting distance of the trajectory. There is an example of task_list in README.
def distance(task_list):
    prev_x = 0.0
    prev_y = 0.0
    result = 0.0
    for i in range(0, len(task_list)):
        cur_x = task_list[i]["x"]
        cur_y = task_list[i]["y"]
        result += math.sqrt((cur_x - prev_x) ** 2 + (cur_y - prev_y) ** 2)
        prev_x = cur_x
        prev_y = cur_y
    return result

all_final_path = [] # This list will contains the final trajectories of all UAVs. You can find details of all_final_path in README.
# Finding the optimal path by binary search and greedy algorithm.
for uav in range(0, num_available_UAVs):
    final_path = [] # This list will contains the final trajectory for a certain UAV. You can find details in README.
    l = 0
    r = len(data)
    # Binary search
    while l < r:
        mid = int((l + r) / 2)
        tasks_list = copy.deepcopy(data[0: mid + 1]) # Select the first mid sensing tasks with largest number of undefined workers reported data.
        new_tasks_list = [] # This list is used for storing the latest trajectory.
        num_task = len(tasks_list) # The number of tasks in tasks_list.
        # [+] Begin to search for the nearest sensing task and add it in the trajectory new_tasks_list ===
        # The start point of each UAV is (0, 0).
        prev_x = 0.0
        prev_y = 0.0
        for i in range(0, num_task):
            min_distance = float("inf")
            min_x = 0.0
            min_y = 0.0
            num = 0.0
            for j in range(0, len(tasks_list)):
                cur_x = tasks_list[j]["x"]
                cur_y = tasks_list[j]["y"]
                dist = math.sqrt((cur_x - prev_x) ** 2 + (cur_y - prev_y) ** 2)
                if dist < min_distance:
                    min_x = cur_x
                    min_y = cur_y
                    num = tasks_list[j]["num_udef"]
                    min_distance = dist
        # [-] End Searching for the nearest sensing tasks ===
        # The result is (min_x, min_y), which is the location certain UAV will move to.
            tasks_list.remove({"x": min_x, "y": min_y, "num_udef": num})
            new_tasks_list.append({"x": min_x, "y": min_y, "num_udef": num})
            # The start point of the UAV is updated to (min_x, min_y).
            prev_x = min_x
            prev_y = min_y
        # Calculate the distance of new trajectory.
        new_distance = distance(new_tasks_list)
        if new_distance < flight_duration: 
            final_path = copy.deepcopy(new_tasks_list) # Update the trajectory.
            l = mid + 1
        else:
            r = mid
    # Store the trajectory for a certain UAV.
    all_final_path.append({"UAV": uav, "path": final_path})
    # Some sensing tasks are collected by UAVs so these tasks need to be removed from data.
    for i in range(0, len(final_path)):
        data.remove(final_path[i])

# A function used for visualiza map and trajectories of UAVs.
def visual_map(all_final_path):
    plt.scatter(x, y, s=[n*10 for n in num_undef_worker])
    plt.xlabel('x coordinate', fontsize=18)
    plt.ylabel('y coordinate', fontsize=18)
    plt.rc('font',family='Times New Roman')
    plt.plot([0], [0], linestyle='-', linewidth=1, marker='*', color="r", markersize=15, label='start')
    uav_name = len(all_final_path)
    for i in range(0, uav_name):
        label_name = "UAV" + str(i + 1)
        path_x = [0]
        path_y = [0]
        for j in range(0, len(all_final_path[i]["path"])):
            path_x.append(all_final_path[i]["path"][j]['x'])
            path_y.append(all_final_path[i]["path"][j]['y'])
        path_x.append(0)
        path_y.append(0)
        plt.plot(path_x, path_y, linestyle='-', linewidth=2, marker='d', markersize=0, label=label_name)
    plt.legend()
    plt.show()

# A function used for calculating the energy cost of UAVs.
def energy(all_final_path):
    e = 0
    for i in range(0, len(all_final_path)):
        path = [[0,0]]
        for j in range(0, len(all_final_path[i]["path"])):
            path.append([all_final_path[i]["path"][j]['x'], all_final_path[i]["path"][j]['y']])
        path.append([0,0])
        distance = 0
        for j in range(0, len(path) - 1):
            distance += math.sqrt((path[j][0]-path[j+1][0])**2 + (path[j][1]-path[j+1][1])**2)
        e += (10 * distance + (2.25 * (len(path) - 2)))
    e /= (100 - len(data))
    return e

# calulate the energy consumption per sensing tasks
# print(energy(all_final_path)) 

# print the trajectories of each UAV
# print(all_final_path)

# calculate the number of UAVs the MCS application need to collect all data
# num_uav = 0
# print(all_final_path)
# for i in range(0, len(all_final_path)):
#     path = all_final_path[i]["path"]
#     if len(path) != 0:
#         num_uav += 1
# print(num_uav)

# visualize the trajectories of all UAVs
visual_map(all_final_path) 