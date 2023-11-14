# Guide for Code Review

[TOC]

## Files Structure

The structure of this file is shown as follows:

```cmd
│  README.pdf
│  README.md
│
├─truth_evaluation
│  │  truth_infer.py
│  │
│  └─datasets
│          dataset_high_quality.csv
│          dataset_low_quality.csv
│          dataset_medium_quality.csv
│
└─uav_trajectory
        map.csv
        map.py
        path.py
```

The containing of each file are as follows:

1. **README.pdf** briefly introduces the structure of source code files and key data structures of our proposed systems. 

2. The folder **truth_evaluation** contains the file **truth_infer.py** and the folder **datasets**. **truth_infer.py** contains the following implementation of algorithms:
   a. Algorithm 1 Reliable Workers Classification
   
   b. Algorithm 2 Undefined Workers Classification
   
   c. Algorithm 3 Data Rectification by Machine Learning
   
   d. Algorithm 4 Iteration Truth Discovery 
   
   The **datasets** contain three quality datasets we used in the manuscript. The part of **dataset_high_quality.csv** is shown as follows:
   
   ```csv
   gt	user1	user2	user3	user4	user5
   28.55119903	27.87786859	27.89936947	34.86767609	29.04753966	30.01016166	
   39.92188155	39.78593313	38.85783919	35.68673048	43.86292874	40.71191991	
   39.40345105	39.44086045	39.60038573	29.86960854	34.53012805	38.98069685	
   36.97482581	38.42923133	38.93395694	40.63846012	36.97385648	38.80765742	
   23.99748973	24.66933405	23.08311091	32.40757726	26.88268983	27.54469656
   ```
   
   The first line is the label of the data. **gt** is the term "ground truth" in short. Obviously, **user1**, **user2**, and so on represent different workers. The remaining rows correspond to data from different sensing tasks. For example, the ground truth of sensing task $t_1$ is 28.55119903 and $t_1$'s data reported by worker $s_1$ is 27.87786859.
   
3. The folder **uav_trajectory** contains the files **map.csv**, **map.py** and **path.py**. **map.py**  generates the map containing locations of different sensing tasks, and **map.csv** is the result of running **map.py**. **path.py** contains Algorithm 5 UAV trajectory planning. The part of **map.csv** is shown as follows:

   ```csv
   142.8215205	140.5067346	9
   146.8677301	67.98565093	6
   21.95286622	62.52956227	8
   132.8226375	20.67388633	9
   104.6058872	113.8240295	6
   ```

   Each line contains three data. The first and second data refer to the x and y coordinates of a sensing task. The third data represents how many undefined workers report data for a certain sensing task. For instance, the location of sensing task $t_1$ is (142.8215205, 140.5067346). And there are nine undefined workers who have reported data of $t_1$.
## Key Data Structures

**Attention:** Before reading this part, We highly recommend you read the source code first because we added detailed comments for our code. We also highly recommend you read the manuscript before reviewing the code.

### path.py

#### data, task_list, tasks_list, new_tasks_list, final_path

```python
## Example
[{'x': 46.420015053668095, 'y': 69.087533463288, 'num_udef': 10}, {'x': 11.439751345995337, 'y': 31.88790891606388, 'num_udef': 10}, {'x': 40.683788420613816, 'y': 130.27094372483668, 'num_udef': 10}, {'x': 139.04190514730524, 'y': 103.28950912176558, 'num_udef': 10}, {'x': 11.569016874227083, 'y': 126.30494914487142, 'num_udef': 9}, {'x': 106.566877793638, 'y': 86.0925406862251, 'num_udef': 9}, {'x': 134.10945533565197, 'y': 104.79665717297071, 'num_udef': 9}, ...]
```

These lists are the lists of dictionaries. Each dictionary in the list contains three key: value pairs.  The keys **x** and **y** refer to the location of a sensing task. And the key **num_udef** represents the number of undefined workers.  

#### all_final_path

```python
## Example
[{'UAV': 0, 'path': [{'x': 11.439751345995337, 'y': 31.88790891606388, 'num_udef': 10}, {'x': 24.109347053828394, 'y': 44.54547865712879, 'num_udef': 9}, {'x': 10.992448300735768, 'y': 52.707441560516735, 'num_udef': 9}, {'x': 35.37299998726546, 'y': 78.9604281906786, 'num_udef': 8}, {'x': 46.420015053668095, 'y': 69.087533463288, 'num_udef': 10}, {'x': 48.37656693667548, 'y': 100.50481812043233, 'num_udef': 9}, {'UAV': 1, 'path': [{'x': 36.77742170003314, 'y': 24.755835891343065, 'num_udef': 8}, ...]
```

This list is the list of dictionaries. Each dictionary in list contains two key: value pairs. The key **UAV** refers to the number of UAVs. And the key **path** represents a list, which is the same as data structures **data** and **task_list** shown above.

### truth_infer.py

#### user_data, user_test

```python
## Example
{'user1': [27.87786859, 39.78593313, 39.44086045, 38.42923133, 24.66933405, 40.63841488, 39.82446759, 39.74728942, 25.99547285, ...], 'user2': [27.89936947, 38.85783919, 39.60038573, 38.93395694, ...], ...}
```

These two dictionaries contain many key: value pairs. Each key corresponds to a certain worker. The value is a list, which contains the workers' data samples for each sensing task.

#### all_task_gt

```python
## Example
[28.55119903, 39.92188155, 39.40345105, 36.97482581, 23.99748973, 38.42683295, 36.56777056, 37.63113571, 26.43663702, 27.66190049, 37.88322438, 24.98003024, 23.71519142, 23.55117271, 29.09411091, 38.47234885, 39.13756428, 22.08834881, 28.48697606, 35.3543741, 27.16590148, 31.79161152, 24.39855075, 33.92613957, 30.5964231, 22.58570966, 24.16524089, 36.57007302, 20.705749, 23.71326212, 20.83228764, 34.51849029, 23.94537383, 30.77085535, 27.89779457, 30.21749351, 29.55435636, 21.98082407, 30.20028803, 35.7698564, 24.99076219, 37.99684738, 39.95075369, 30.05645763, 26.37182666, 21.54289711, 24.47800137, 24.55496041, 29.7675875, 25.13930562]
```

The **all_task_gt** is a list, containing the ground truths of all sensing tasks. For example, the first sensing task's ground truth is 28.55119903, i.e. $v^g_1 = 28.55119903$.

#### excellent_user, ml_user

```python
## Example
['user1', 'user2', 'user4', 'user5', 'user6', 'user7', 'user8', 'user9', 'user10', 'user11', 'user12', 'user13', 'user14', 'user16', 'user17', 'user18', 'user19', 'user20', 'user21', 'user22', 'user23', 'user25', 'user26', 'user27', 'user28', 'user29', 'user30', 'user31', 'user32', 'user33', 'user34', 'user35', 'user36', 'user38', 'user39', 'user40', 'user24', 'user41', 'user42', 'user43', 'user44', 'user45', 'user46', 'user47', 'user49', 'user50', 'user51', 'user52', 'user53', 'user54', 'user55', 'user56', 'user57', 'user58', 'user59', 'user60', 'user61', 'user62', 'user63', 'user64', 'user65', 'user66', 'user67', 'user68']
```

The lists **excellent_user** and **ml_user** contains workers' name. For example, the list shown above is an example of **excellent_user**, which means user1, user2, and so on are reliable workers.

#### user_model_map

```python
## Example
{'user3': LinearRegression(), 'user15': LinearRegression(), 'user24': LinearRegression(), 'user37': LinearRegression(), 'user41': LinearRegression(), 'user42': LinearRegression(), 'user43': LinearRegression(), 'user44': LinearRegression(), 'user45': LinearRegression(), 'user46': LinearRegression(), 'user47': LinearRegression(), 'user48': LinearRegression(), 'user49': LinearRegression(), 'user50': LinearRegression(), 'user51': LinearRegression(), 'user52': LinearRegression(), 'user53': LinearRegression(), 'user54': LinearRegression(), 'user55': LinearRegression(), 'user56': LinearRegression(), 'user57': LinearRegression(), 'user58': LinearRegression(), 'user59': LinearRegression(), 'user60': LinearRegression(), 'user61': LinearRegression(), 'user62': LinearRegression(), 'user63': LinearRegression(), 'user64': LinearRegression(), 'user65': LinearRegression(), 'user66': LinearRegression(), 'user67': LinearRegression(), 'user68': LinearRegression(), 'user69': LinearRegression(), 'user70': LinearRegression(), 'user71': LinearRegression(), 'user72': LinearRegression(), 'user73': LinearRegression(), 'user74': LinearRegression(), 'user75': LinearRegression(), 'user76': LinearRegression(), 'user77': LinearRegression(), 'user78': LinearRegression(), 'user79': LinearRegression(), 'user80': LinearRegression(), 'user81': LinearRegression(), 'user82': LinearRegression(), 'user83': LinearRegression(), 'user84': LinearRegression(), 'user85': LinearRegression(), 'user86': LinearRegression(), 'user87': LinearRegression(), 'user88': LinearRegression(), 'user89': LinearRegression(), 'user90': LinearRegression(), 'user91': LinearRegression(), 'user92': LinearRegression(), 'user93': LinearRegression(), 'user94': LinearRegression(), 'user95': LinearRegression(), 'user96': LinearRegression(), 'user97': LinearRegression(), 'user98': LinearRegression(), 'user99': LinearRegression(), 'user100': LinearRegression()}
```

The list **user_model_map** contains many key: value pairs. The key represents the name of the workers, and the corresponding value is the workers' rectification model.
