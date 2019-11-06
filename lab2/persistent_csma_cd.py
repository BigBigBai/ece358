from classes.lan_des import LAN_DES

for A in [12]:
    print('A =', A)
    for N in [60]:
        lan_des = LAN_DES(N, A, 1000)
        lan_des.run_des()