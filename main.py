# Be naame khodaa
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from manager import Manager

M, lam, alpha, miu = 3, 100, 20, 100
rooms_service_rates = [[0.2, 0.2, 0.4], [0.4, 0.5], [1]]
patient_numbers = int(1e5)
# M, lam, alpha, miu = list(map(float, input().split()))
# M = int(M)
# rooms_service_rates = []
# for i in range(M):
#     rooms_service_rates.append(list(map(float, input().split())))

# seed = np.random.randint(1, 1000)
# np.random.seed(seed)
manager = Manager(patient_numbers=patient_numbers,
                  rooms_service_rates=rooms_service_rates,
                  enter_rate=lam,
                  reception_rate=miu,
                  patience=alpha,)
manager.run()
print('Simulation time:', manager.time)

# Reports
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)
pd.set_option('display.max_colwidth', None)
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

data_columns = ['Reception'] + ['Room %d' % i for i in range(len(manager.rooms))] + ['Rooms Average']
data = pd.DataFrame(columns=data_columns)
data.loc['4. Mean queue size'] = [manager.mean_queue_size(manager.reception_queue)] + \
                                 [manager.mean_queue_size(room.queue) for room in manager.rooms] + \
                                 [manager.rooms_mean_queue_size()]
print(data)

all_waiting_times = np.array(waiting_times[False] + waiting_times[True])
print('5. Number of patients to acheive 0.95 accuracy for mean waiting time: ', end='')
print((np.sqrt(all_waiting_times.var()) * 1.96 / (0.95 * np.mean(all_waiting_times))) ** 2)

# 6

def mean_mean_queue_size(speed):
    speedy_rooms_service_rates = [np.array(rates)*speed for rates in rooms_service_rates]
    # print(speedy_rooms_service_rates)
    speedy_manager = Manager(patient_numbers=patient_numbers,
                             rooms_service_rates=speedy_rooms_service_rates,
                             enter_rate=lam,
                             reception_rate=miu,
                             patience=alpha, )
    speedy_manager.run()
    return speedy_manager.rooms_mean_queue_size()


low = 1.0
high = 1.0
low_eps = 1.0
high_eps = 0.1
while mean_mean_queue_size(low) < low_eps:
    print('low %f not low enough' % low)
    low /= 2
while mean_mean_queue_size(2*low) > low_eps:
    print('low %f too low' % low)
    low *= 2
while mean_mean_queue_size(high) > high_eps:
    print('high %f not high enough' % high)
    high *= 2
while mean_mean_queue_size(high/2) < high_eps:
    print('high %f too high' % high)
    high /= 2
if high + 1.0 < low:
    high = low * 2

speed_values = np.linspace(low, high, 10)
mean_mean_queue_sizes = []

for speed in speed_values:
    mean_mean_queue_sizes.append(mean_mean_queue_size(speed))

plt.xlabel("Coefficient of Room Service Rates")
plt.ylabel("Mean of Rooms Mean Queue Size")
plt.plot(speed_values, mean_mean_queue_sizes)
print(speed_values)
print(mean_mean_queue_sizes)
plt.show()

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
