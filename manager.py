import numpy as np

from enums import Event, Log
from patient import Patient
from pqueue import PriorityQueue
from room import Room
from waiting_queue import WaitingQueue


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

    def mean_queue_size(self, queue):
        summerized = self.summerize_log(queue.log)
        area = 0
        for i in range(1, len(summerized)):
            area += (summerized[i][0] - summerized[i - 1][0]) * summerized[i - 1][1]
        return area / self.time

    def get_patients_log(self):
        logs = []
        for patient in self.patients:
            logs.append((Log.ENTER, patient.healthy, patient.enter_time))
            logs.append((Log.EXIT, patient.healthy, patient.exit_time))
        logs.sort(key=lambda x: x[2])
        return logs

    @staticmethod
    def summerize_log(log, health=None):
        points = []
        count = 0
        last_time = 0
        for event, healthy, time in log:
            if time != last_time:
                points.append((last_time, count))
            last_time = time
            if health is not None and healthy != health:
                continue
            if event == Log.ENTER:
                count += 1
            else:
                count -= 1
        points.append((last_time, count))
        return points
