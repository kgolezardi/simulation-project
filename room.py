import numpy as np

from waiting_queue import WaitingQueue


class Room:
    def __init__(self, manager, service_rates):
        self.manager = manager
        self.num_doctors = len(service_rates)
        self.service_rates = service_rates
        self.doctors_patient = [None for i in range(self.num_doctors)]
        self.queue = WaitingQueue()

    @property
    def time(self):
        return self.manager.time

    def push(self, patient):
        patient.enter_room_time = self.time
        available_doctors = [i for i in range(self.num_doctors) if self.doctors_patient[i] is None]
        if len(available_doctors) > 0:
            doctor_num = np.random.choice(available_doctors)
            self.visit(doctor_num, patient)
        else:
            self.enter_queue(patient)

    def doctor_ready(self, doctor_num):
        patient = self.doctors_patient[doctor_num]
        self.manager.finalize_patient(patient)

        if self.queue.empty():
            self.doctors_patient[doctor_num] = None
        else:
            self.visit(doctor_num, self.queue.pop(self.time))

    def remove_patient(self, patient):
        self.queue.remove(self.time, patient)
        self.manager.finalize_patient(patient)

    def visit(self, doctor_num, patient):
        self.doctors_patient[doctor_num] = patient
        patient.visit_start_time = self.time
        self.manager.push_doctor_ready_event(self, doctor_num)

    def enter_queue(self, patient):
        self.queue.push(self.time, patient)
        self.manager.push_room_bored_event(patient, self)
