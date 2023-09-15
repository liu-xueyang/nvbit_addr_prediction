# -*- coding: utf-8 -*-
"""OutputFileScripting.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1o1SA_c9g35frU3k8SwHSZybJ94eh4CD3
"""

import re
import numpy as np
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("-i", help="input file", 
	type=str, dest="input", default = "./traces/bfs_chesapeake.out")
args= parser.parse_args()


with open(args.input, 'r') as f:
    contents = f.read()

blocks = contents.split('MEMTRACE:')[1:]

cta_id = [] #List of Unique CTA IDs
warps = [] #Warp IDs, in sequential order
data = [] #Storing the set of 32 hexadecimal based address values for each CTA_ID, Warp_ID pair.

addrFootprint = {} #Dictionary to store all relevant information based on CTA_ID only.

for block in blocks:
  cta_local = re.findall(r'CTA (\d+)', block)[0]
  cta_id.append(int(cta_local))
  warp_id = re.findall(r'warp (\d+)', block)[0]
  warps.append(int(warp_id))
  hex_values = re.findall(r"0x[0-9a-fA-F]{14}", block)
  print(hex_values)
  data.append(hex_values[1])
  
  if int(cta_local) in addrFootprint:
    addrFootprint[int(cta_local)].add(hex_values[1])
  else:
    addrFootprint.setdefault(int(cta_local), set())
    addrFootprint[int(cta_local)].add(hex_values[1])

#Enumerating the different Unique CTA IDs in order of how they're called.
uniqueCTA = list(addrFootprint.keys())
print("Unique CTAs are:")
print(uniqueCTA)

#Printing out the address footprints for the first 5 unique CTA IDs as stored in addrFootprint.

print("Unique CTA footprint size (in 256B sectors)")
if len(uniqueCTA) > 5:
  for i in range(0, 5):
    print(uniqueCTA[i], len(addrFootprint[uniqueCTA[i]]))
else:
  for i in range(0, len(uniqueCTA)):
    print(uniqueCTA[i], len(addrFootprint[uniqueCTA[i]]))

# Storing the starting address for each unique CTA ID

# startAddrCTAunique = []
# for element in addrFootprint:
#   startAddrCTAunique.append(int(addrFootprint[element][0], 0))

# Converting the set of addresses for CTA ID = 63 from Hexadecimal to Integer. 

# testAddrInt = []
# for hexWords in addrFootprint[63]:
#   testAddrInt.append(int(hexWords, 0))

# # Plotting the address range for CTA ID = 63
# import matplotlib.pyplot as plt
# x = [i for i in range(0, len(testAddrInt))]
# plt.plot(x, testAddrInt)
# plt.savefig("CTA63.png")
# plt.close()

# Start Simple FTL based on CTA footprint
# Configuration (MQSim default)
C = 8 # Channel
W = 4 # Way (Chip)
D = 2 # Die
P = 2 # Plane  
P_size = 2048 * 256 # number of pages per plane

total_P = C * W * D * P
Dist_sum = np.zeros(total_P)
Dist_sum = np.reshape(Dist_sum, (C,W,D,P))
Dist = np.zeros(total_P)
Dist = np.reshape(Dist, (C,W,D,P))
cnt = 0

for cta in uniqueCTA: # sequentially loop through ctas based on appearance order
  cnt = cnt + 1
  for addr in addrFootprint[cta]:
    addrInt = int(addr, 0)
    CID = addrInt % C
    WID = int(addrInt/C) % W
    DID = int(addrInt/C/W) % D
    PID = int(addrInt/C/W/D) % P
    # print(CID)
    # print
    Dist[CID][WID][DID][PID] = Dist[CID][WID][DID][PID] + 1

  if cnt % 10000 == 0:
    cnt = 0
    # Record meta sum
    Dist_sum = Dist_sum + Dist
    # most frequently accessed CID, WID, DID, PID
    # corresponding frequency
    total_access = np.sum(Dist)
    max_PID = np.argmax(Dist)
    freq_P = np.amax(Dist)/total_access

    Die_Dist = np.sum(Dist, axis=3)
    max_DID = np.argmax(Die_Dist)
    freq_D = np.amax(Die_Dist)/total_access

    Way_Dist = np.sum(Die_Dist, axis=2)
    max_WID = np.argmax(Way_Dist)
    freq_W = np.amax(Way_Dist)/total_access
    var_W = Way_Dist.var()

    Channel_Dist = np.sum(Way_Dist, axis=1)
    max_CID = np.argmax(Channel_Dist)
    freq_C = np.amax(Channel_Dist)/total_access
    var_C = Channel_Dist.var()
    print(f'CTA{cta:.0f},{total_access:.0f},{var_C:.3f},{max_CID:.0f},{freq_C:.3f},{var_W:.3f},{max_WID:.0f},{freq_W:.3f}')
    print("Channel")
    print(Channel_Dist)
    print("Way")
    print(Way_Dist)
  
  # evenness of distribution: summing up N consecutive CTAs and show distribution of channel, way and die

  # if cta % 500 >= 10 and cta % 500 < 50:
  #   print(f'CTA{cta:.0f},{total_access:.0f},{var_C:.3f},{max_CID:.0f},{freq_C:.3f},{var_W:.3f},{max_WID:.0f},{freq_W:.3f}')
  #   if cta % 500 == 10:
  #     print("Channel")
  #     print(Channel_Dist)
  #     print("Way")
  #     print(Way_Dist)
      # print("Die")
      # print(Die_Dist)
Dist_sum = Dist_sum + Dist
# print(Dist_sum)
Die_Dist = np.sum(Dist_sum, axis=3)
Way_Dist = np.sum(Die_Dist, axis=2)
Channel_Dist = np.sum(Way_Dist, axis=1)
# print("Channel")
# print(Channel_Dist)
# print("Way")
# print(Way_Dist)