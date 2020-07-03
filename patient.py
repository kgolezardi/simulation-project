class Patient:
    def __init__(self, corona, patience):
        self.corona = corona
        self.patience = patience
        self.enter_time = None
        self.check_in_time = None
        self.enter_room_time = None
        self.visit_start_time = None
        self.exit_time = None

    def in_reception_queue(self):
        return self.check_in_time is None

    def visited_doctor(self):
        return self.visit_start_time is not None

    @property
    def healthy(self):
        return not self.corona

    def __str__(self):
        attributes = ('enter_time', 'check_in_time', 'enter_room_time', 'visit_start_time', 'exit_time')
        res = []
        for attribute in attributes:
            value = self.__getattribute__(attribute)
            res.append(attribute + '=' + ('%.2f' % value if value else '----'))
        res.append(str(self.corona))
        return '   '.join(res)

    @property
    def spent_time(self):
        return self.exit_time - self.enter_time

    @property
    def bored(self):
        return self.exit_time is not None and self.visit_start_time is None

    @property
    def waiting_time(self):
        if self.bored:
            return self.patience
        return self.check_in_time - self.enter_time + \
            self.visit_start_time - self.enter_room_time
