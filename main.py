# Be naame khodaa
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from manager import Manager

M, lam, alpha, miu = 3, 5, 50, 5
rooms_service_rates = [[1, 2, 3], [4, 5], [6]]
# M, lam, alpha, miu = list(map(float, input().split()))
# M = int(M)
# rooms_service_rates = []
# for i in range(M):
#     rooms_service_rates.append(list(map(float, input().split())))

# seed = np.random.randint(1, 1000)
# np.random.seed(seed)
manager = Manager(patient_numbers=int(1e3),
                  rooms_service_rates=rooms_service_rates,
                  enter_rate=lam,
                  reception_rate=miu,
                  patience=alpha,)
manager.run()
print('Simulation time:', manager.time)

# Reports
data = pd.DataFrame(columns=['Healthy', 'Corona', 'All'])
spent_times = {True: [], False: []}
waiting_times = {True: [], False: []}
response_times = {True: [], False: []}
bored_count = 0
for patient in manager.patients:
    spent_times[patient.corona].append(patient.spent_time)
    waiting_times[patient.corona].append(patient.waiting_time)
    if patient.visited_doctor():
        response_times[patient.corona].append(patient.response_time)
    if patient.bored():
        bored_count += 1
data.loc['1. Spent time'] = [np.mean(spent_times[False]), np.mean(spent_times[True]),
                             np.mean(spent_times[False] + spent_times[True])]
data.loc['2. Waiting time'] = [np.mean(waiting_times[False]), np.mean(waiting_times[True]),
                               np.mean(waiting_times[False] + waiting_times[True])]
print(data)

print('3. Bored count average:', bored_count / manager.time)

data_columns = ['Reception'] + ['Room %d' % i for i in range(len(manager.rooms))]
data = pd.DataFrame(columns=data_columns)
data.loc['4. Mean queue size'] = [manager.mean_queue_size(manager.reception_queue)] + \
                                 [manager.mean_queue_size(room.queue) for room in manager.rooms]
print(data)

all_waiting_times = np.array(waiting_times[False] + waiting_times[True])
print('5. Number of patients to acheive 0.95 accuracy for mean waiting time: ', end='')
print((np.sqrt(all_waiting_times.var()) * 1.96 / (0.95 * np.mean(all_waiting_times))) ** 2)

# 6

# Extra 1, 2, 3

titles = ['Response', 'Waiting', 'Spent']
measured_times_list = [response_times, waiting_times, spent_times]
for title, measured_times in zip(titles, measured_times_list):
    fig, axs = plt.subplots(1, 2)
    fig.suptitle('Histogram of ' + title + ' Time')
    axs[0].set_title('Healthy')
    axs[0].hist(measured_times[False], bins='rice')
    axs[1].set_title('Corona')
    axs[1].hist(measured_times[True], bins='rice')
plt.show()

# Extra 4, 5

labels = ['All', 'Corona', 'Healthy']
healths = [None, False, True]
for label, health in zip(labels, healths):
    summerized_patients_log = manager.summerize_log(manager.get_patients_log(), health=health)
    x = [time for time, count in summerized_patients_log]
    y = [count for time, count in summerized_patients_log]
    plt.plot(x, y, label=label)
plt.title('Ex4. Number of present patients in the system over time')
plt.legend()
plt.show()

titles = ['Reception'] + ['Room %d' % i for i in range(len(manager.rooms))]
queues = [manager.reception_queue] + [room.queue for room in manager.rooms]
for title, queue in zip(titles, queues):
    labels = ['All', 'Corona', 'Healthy']
    healths = [None, False, True]
    for label, health in zip(labels, healths):
        summerized_log = manager.summerize_log(queue.log, health)
        x = [time for time, count in summerized_log]
        y = [count for time, count in summerized_log]
        plt.plot(x, y, label=label)
    plt.title('Ex5. Queue length over time: %s' % title)
    plt.legend()
    plt.show()
