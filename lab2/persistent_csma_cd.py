from classes.lan_des import LAN_DES
from utils.utils import write_to_csv

file = 'persistent_csma_cd.csv'
headers = ['N', 'A', 'Efficiency', 'Throughput']
data = []

for A in [7, 10, 20]:
    print('A =', A)
    for N in [20, 40, 60, 80, 100]:
        lan_des = LAN_DES(N, A, 1000)
        data.append(lan_des.run_des())

write_to_csv(file, headers, data)
