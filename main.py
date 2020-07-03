# Be naame khodaa
import numpy as np

from manager import Manager

M, lam, alpha, miu = list(map(float, input().split()))
M = int(M)
rooms_service_rates = []
for i in range(M):
    rooms_service_rates.append(list(map(float, input().split())))

seed = np.random.randint(1, 1000)
# seed = 740
print(seed)
np.random.seed(seed)
manager = Manager(patient_numbers=int(1e5),
                  rooms_service_rates=rooms_service_rates,
                  enter_rate=lam,
                  reception_rate=miu,
                  patience=alpha,)
manager.run()
print(manager.time)
manager.report()
