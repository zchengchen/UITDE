from os import terminal_size
import sys
import csv
from types import DynamicClassAttribute
import numpy as np
from numpy.core.fromnumeric import sort
from numpy.core.records import array
from numpy.lib.function_base import diff
from sklearn import linear_model
from sklearn.linear_model import LinearRegression
import matplotlib.pyplot as plt
import random

standard_p = 0.4 # \alpha_{min}.
task_num = 1000 # The number of sensing tasks. We generate 1000 sensing tasks in total.
uav_task = 100 # The number of sensing tasks for which UAV collected data. It is also the number of data in the training and test set.
user_num = 100 # The number of workers. We assume there are 100 workers collecting data in total.
err = 3 # Acceptable observation error. \epsilon_m.
# You can change the dataset here.
filename = r'./datasets/dataset_high_quality.csv' 
# filename = r'./datasets/dataset_medium_quality.csv'
# filename = r'./datasets/dataset_low_quality.csv'
time_step = 100 # There are 100 sensing tasks in each time step. It means there are 10 time steps in total.

# A function used to count which workers report data correctly.
def search(user_data, allocate_list, data_tj, numj):
    rigth_list = []
    for i in range(0, len(data_tj)):
        for j in range(0, len(allocate_list)):
            if(abs(user_data[allocate_list[j]][numj] - data_tj[i]) < 1e-3):
                rigth_list.append(allocate_list[j])
                break
    return rigth_list

# Our purposed truth data evaluation method.
# beta: \beta, a decaying factor. 
# uav_task: The number of sensing tasks for which UAVs collected data.
# standard_p: \alpha_{min}.
def UITDE(beta,  uav_task, standard_p):
    user_data = {}
    sum_err = 0.0
    user_accuracy = {}
    all_task_gt = []
    excellent_user = []
    ml_user = []
    user_model_map = {}
    user_weight = {}
    user_data = {}
    user_accuracy = {}
    all_task_gt = []
    user_weight = {}
    user_ans_num = {}
    user_right_num = {}
    user_sigma = {}
    # [+] Initialize the parameters and data of workers (or users).
    for i in range(1,user_num+1):
        s = 'user' + str(i)
        user_data[s] = 0
        # Attention: user whoes id is in [0, 70] is not the spammer.
        if i <= 70:
            user_sigma[s] = 0
        user_accuracy[s] = 0
        user_weight[s] = 1
        user_ans_num[s] = 0
        user_right_num[s] = 0
    # [-] End of initialization.
    # Load workers' data from datasets.
    with open(filename, encoding='utf-8') as f:
        reader = csv.reader(f)
        rows = [row for row in reader]
        for i in range(1,task_num+1):
            all_task_gt.append(float(rows[i][0]))
        for i in range(1,user_num+1):
            single_user_data = []
            for j in range(1,task_num+1):
                single_user_data.append(float(rows[j][i]))
            user_data['user'+str(i)] = single_user_data
    # Attention: user whoes id is in [0, 70] is not the spammer.
    # [+] The first worker classification. This part classifies workers into two parts: S^{Reliable} and S^{Undefined}. 
    # The workers in S^{Reliable} (i.e. Reliable Workers) are stored in the list excellent_user.
    # The workers in S^{Undefined} (i.e. Undefined Workers) are stored in the list ml_user (ml means machine learning).
    for i in range(1, user_num + 1):
        user_id = 'user' + str(i)
        for j in range(0,uav_task):
            if(abs(user_data[user_id][j]-all_task_gt[j]) < err):
                user_right_num[user_id] += 1 # The number of correct data from workers.
            user_ans_num[user_id] += 1 # The number of sensing tasks workers report data.
        user_accuracy[user_id] = user_right_num[user_id]/user_ans_num[user_id] # Calculate the accuracy for each worker.
        if(user_accuracy[user_id] < standard_p):
            # These workers should be classified as undefined workers.
            # Initialize their data again for following rectification.
            user_accuracy[user_id] = 0
            user_ans_num[user_id] = 0
            user_right_num[user_id] = 0
            ml_user.append(user_id)
        else:
            excellent_user.append(user_id) # This list stores reliable workers who do not need rectification.
    # print(user_data)
    # print(all_task_gt)
    # [-] End of the first worker classification.
    # [+] Data Rectification.
    # Obtain Eq. (12) for each undefined worker. 
    uav_train_num = 10
    uav_test_num = uav_task - uav_train_num
    for i in range(0, len(ml_user)):
        model = linear_model.LinearRegression()
        model.fit(np.array(user_data[ml_user[i]][0:uav_train_num]).reshape(-1,1),
            np.array(all_task_gt[0:uav_train_num]).reshape(-1,1))
        user_model_map[ml_user[i]] = model # Store the model (i.e. Eq. (12)) for each undefined worker.
    # Try to rectify data.
    user_test = {} # The dictionary user_test stores the rectification results for each undefined workers. The details and example about it are shown in README.
    for i in range(0, len(ml_user)):
        pred_data = []
        # Data Rectification.
        for j in range(uav_train_num + 1, uav_task + 1):
            pred_data.append((user_model_map[ml_user[i]].predict([[user_data[ml_user[i]][j-1]]]))[0][0])
        # Store the rectification result for each undefined worker.
        user_test[ml_user[i]] = pred_data
    # [+] The second worker classification. This part classifies undefined workers into rectifiable workers and spammers.
    for i in range(0, len(ml_user)):
        for j in range(0, uav_test_num):
            if(abs(user_test[ml_user[i]][j] - all_task_gt[j + uav_train_num]) < err):
                user_right_num[ml_user[i]] += 1 # The number of correct data from workers.
            user_ans_num[ml_user[i]] += 1 # The number of sensing tasks workers report data.
        user_accuracy[ml_user[i]] = user_right_num[ml_user[i]] / user_ans_num[ml_user[i]] # Calculate the accuracy for each worker.
        if(user_accuracy[ml_user[i]] >= standard_p):
            excellent_user.append(ml_user[i]) # The list excellent_user now contains all accurate workers (S^{Accurate}) and rectificable workers (S^{Rectifiable}).
    # print(user_model_map)
    # [-] End of second worker classification.
    # Rectify data for following 900 sensing tasks.
    for j in range(0, task_num):
        for i in range(0, len(excellent_user)):
            if excellent_user[i] in ml_user:
                user_data[excellent_user[i]][j] = (user_model_map[excellent_user[i]].predict([[user_data[excellent_user[i]][j]]]))[0][0]
    # Recalculate the number of tasks answered correctly by all workers and their accuracy.
    for i in range(1, user_num + 1):
        user_id = 'user' + str(i)
        for j in range(0, uav_task):
            if(abs(user_data[user_id][j] - all_task_gt[j]) < err):
                user_right_num[user_id] += 1
            user_ans_num[user_id] += 1
    # Between task_num_beg and task_num_end all the tasks in a certain time step are included. [task_num_beg, task_num_end)
    task_num_beg = 100 
    task_num_end = task_num_beg + time_step
    old_accuracy = {}
    # print(user_test)
    # print(excellent_user)
    # To update each worker's accuracy in later nine time steps, we need to calcualte ITD result.
    # Store the previous time step's accuracy.
    for i in range(0, len(excellent_user)):
        user_id = excellent_user[i]
        user_ans_num[user_id] = 0
        user_right_num[user_id] = 0
        old_accuracy[user_id] = user_accuracy[user_id] # History accuracy in previous time step.
    # Calculate the results for each time step separately.
    # Before calculate the result for next time step, demote the workers that do not meet reliable requirement.
    while task_num_beg + time_step <= task_num:
        for user_id in excellent_user:
            user_accuracy[user_id] = beta*old_accuracy[user_id] + (1-beta)*user_accuracy[user_id]
            old_accuracy[user_id] = user_accuracy[user_id]
            if(user_accuracy[user_id] < standard_p):
                excellent_user.remove(user_id) # Action: Demote (shown in Fig. 3).
            user_ans_num[user_id] = 0
            user_right_num[user_id] = 0
        truth = [] # This list is used for ITD.
        old_truth = [] # This list is used for ITD.
        # Calculate ITD result for each sensing task in current time step.
        for i in range(0, time_step):
            tmp = 0.0
            data_tj = [] # Data samples for the sensing task t_j.
            tmp_alloc = 50 # The number of workers allocated to report data.
            allocate_list = [] # The list store the workers who report data.
            # Task allocation: ramdonly allocate a sensing task to tmp_alloc reliable workers.
            while tmp_alloc > 0:
                r = random.randint(0, len(excellent_user) - 1)
                s = excellent_user[r]
                allocate_list.append(s)
                tmp_alloc -= 1
            # Store the data samples (from workers in allocate_list) in data_tj.
            for j in range(0, len(allocate_list)):
                tmp += user_data[allocate_list[j]][i + task_num_beg]
                user_ans_num[allocate_list[j]] += 1
                data_tj.append(user_data[allocate_list[j]][i + task_num_beg])
            old_truth.append(0)
            truth.append(tmp / len(allocate_list))
            num_remain = len(allocate_list) # The number of remaining workers. During ITD, some data samples may be removed.
            eps = 1e-1
            # [+] Iteration Truth Discovery (ITD).
            # This part is mainly corresponding to line 9~27 Algorithm 4 Iteration Truth Discovery.
            while abs(truth[i]-old_truth[i]) >= eps and num_remain >= 1:
                if num_remain == 1:
                    break
                data_tj.sort()
                old_truth[i] = truth[i]
                mindata = data_tj[0]
                maxdata = data_tj[len(data_tj) - 1]
                max_offset = 0
                if maxdata - old_truth[i] > old_truth[i] - mindata:
                    max_offset = maxdata
                    data_tj.remove(data_tj[len(data_tj)-1])
                else:
                    max_offset = mindata
                    data_tj.remove(data_tj[0])
                truth[i] = (old_truth[i] * num_remain - max_offset) / (num_remain - 1.0) # Line 21 in Algorithm 4 Iteration Truth Discovery.
                num_remain -= 1
            # [-] Iteration Truth Discovery (ITD).
            right_list = search(user_data, allocate_list, data_tj, i + task_num_beg) # The list right_list stores the workers who report data correctly for (i + task_num_beg)-th sensing task.
            # Calculate accuracy for each worker who participates in reporting data.
            for j in range(0, len(allocate_list)):
                user_id = allocate_list[j]
                if user_id in right_list:
                    user_right_num[user_id] += 1
                user_accuracy[user_id] = user_right_num[user_id] / user_ans_num[user_id]
            # Calculate MAE.
            sum_err += abs(truth[i] - all_task_gt[i + task_num_beg])
        task_num_beg = task_num_end
        task_num_end = task_num_beg + time_step
        mae = sum_err / 900 # Mean Absolute Error (MAE).
    return mae

# High
print(UITDE(0.5, 100, 0.5))
# Medium
# print(UITDE(0.4, 100, 0.4))
# Low
# print(UITDE(0.1, 100, 0.4))