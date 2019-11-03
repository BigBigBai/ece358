from classes.lan_des import LAN_DES

for A in [7, 10, 20]:
    print('A =', A)
    for N in [20, 40, 60, 80, 100]:
        lan_des = LAN_DES(N, A, 1000)
        lan_des.run_des()