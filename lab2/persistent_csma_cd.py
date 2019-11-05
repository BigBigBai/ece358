from classes.lan_des import LAN_DES

for A in [5]:
    print('A =', A)
    for N in [20, 40, 60, 80, 100]:
        lan_des = LAN_DES(N, A, 1000)
        lan_des.run_des()