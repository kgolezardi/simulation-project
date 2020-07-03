import enum

import numpy as np
import pandas as pd

from patient import Patient
from pqueue import PriorityQueue
from room import Room
from waiting_queue import WaitingQueue


class Event(enum.Enum):
    ENTER = 0
    RECEPTION_READY = 1
    DOCTOR_READY = 2
    BORED_IN_RECEPTION = 3
    BORED_IN_ROOM = 4


class Manager:
    def __init__(self, patient_numbers, rooms_service_rates, enter_rate, reception_rate, patience):
        self.patients_remained = patient_numbers
        self.enter_rate = enter_rate
        self.patience = patience
        self.reception_rate = reception_rate

        self.patients = []
        self.rooms = []
        for service_rates in rooms_service_rates:
            self.rooms.append(Room(self, service_rates))

        self.reception_queue = WaitingQueue()
        self.reception_patient = None

        self.time = 0
        self.events = PriorityQueue()
        self.push_enter_event()

    def run(self):
        while not self.events.empty():
            event_time, event = self.events.pop()
            self.time = event_time
            if event[0] == Event.ENTER:
                self.patients_remained -= 1
                patient = Patient(np.random.randint(10) == 0, self.patience)
                self.patients.append(patient)
                patient.enter_time = self.time
                if self.reception_patient is None:
                    self.check_in(patient)
                else:
                    self.enter_reception_queue(patient)
                if self.patients_remained:
                    self.push_enter_event()

            elif event[0] == Event.RECEPTION_READY:
                # Assign patient to rooms
                patient = self.reception_patient
                sorted_rooms = sorted([(self.rooms[i].queue.size(), i) for i in range(len(self.rooms))])
                candidate_rooms = [x[1] for x in sorted_rooms if x[0] == sorted_rooms[0][0]]
                room_num = np.random.choice(candidate_rooms)
                self.rooms[room_num].push(patient)

                # Check in next patient in reception queue
                if self.reception_queue.empty():
                    self.reception_patient = None
                else:
                    self.check_in(self.reception_queue.pop(self.time))

            elif event[0] == Event.DOCTOR_READY:
                room, doctor_num = event[1], event[2]
                room.doctor_ready(doctor_num)

            elif event[0] == Event.BORED_IN_RECEPTION:
                patient = event[1]
                if patient.in_reception_queue():
                    self.reception_queue.remove(self.time, patient)
                    self.finalize_patient(patient)

            elif event[0] == Event.BORED_IN_ROOM:
                patient, room = event[1], event[2]
                if not patient.visited_doctor():
                    room.remove_patient(patient)
            else:
                raise ValueError("Event '%s' not supported" % event[0].name)

    def check_in(self, patient):
        self.reception_patient = patient
        self.push_reception_ready_event()
        patient.check_in_time = self.time

    def enter_reception_queue(self, patient):
        self.reception_queue.push(self.time, patient)
        self.push_reception_bored_event(patient)

    def push_enter_event(self):
        enter_interval = np.random.exponential(1 / self.enter_rate)
        self.events.push(self.time + enter_interval, (Event.ENTER,))

    def push_reception_ready_event(self):
        reception_duration = np.random.exponential(1 / self.reception_rate)
        self.events.push(self.time + reception_duration, (Event.RECEPTION_READY,))

    def push_doctor_ready_event(self, room, doctor_num):
        visit_duration = np.random.exponential(1 / room.service_rates[doctor_num])
        self.events.push(self.time + visit_duration, (Event.DOCTOR_READY, room, doctor_num))

    def push_reception_bored_event(self, patient):
        self.events.push(self.time + patient.patience, (Event.BORED_IN_RECEPTION, patient))

    def push_room_bored_event(self, patient, room):
        waited_duration = patient.check_in_time - patient.enter_time
        self.events.push(self.time + patient.patience - waited_duration, (Event.BORED_IN_ROOM, patient, room))

    def finalize_patient(self, patient):
        patient.exit_time = self.time
        # print('Bye bye %s' % patient)

    def report(self):
        data = pd.DataFrame(columns=['Healthy', 'Corona', 'All'])
        spent_times = {True: [], False: []}
        waiting_times = {True: [], False: []}
        bored_count = 0
        for patient in self.patients:
            spent_times[patient.corona].append(patient.spent_time)
            waiting_times[patient.corona].append(patient.waiting_time)
            if patient.bored:
                bored_count += 1
        data.loc['1. Spent time'] = [np.mean(spent_times[False]), np.mean(spent_times[True]),
                                     np.mean(spent_times[False] + spent_times[True])]
        data.loc['2. Waiting time'] = [np.mean(waiting_times[False]), np.mean(waiting_times[True]),
                                       np.mean(waiting_times[False] + waiting_times[True])]
        print(data)

        # FIXME: what the hell is bored count?!
        print('3. Bored count:', bored_count)

        data_columns = ['Reception'] + ['Room %d' % i for i in range(len(self.rooms))]
        data = pd.DataFrame(columns=data_columns)
        data.loc['4. Mean queue size'] = [self.mean_queue_size(self.reception_queue)] + \
                                         [self.mean_queue_size(room.queue) for room in self.rooms]
        print(data)

    def mean_queue_size(self, queue):
        summerized = queue.summerize_log()
        area = 0
        for i in range(1, len(summerized)):
            area += (summerized[i][0] - summerized[i - 1][0]) * summerized[i - 1][1]
        return area / self.time