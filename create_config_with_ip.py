from netaddr import iter_iprange
from itertools import chain
#Interface UNIT number range
COUNT = range (0, 100)
#GRE N/W between CPE and MPE
DUTIP = iter_iprange('2000:0:0:0:83:1:0:0', '2000:0:0:0:83:1:ffff:0', step=65536)
NBIP = iter_iprange('2000:0:0:0:83:1:0:1', '2000:0:0:0:83:1:ffff:1', step=65536)

print("set protocols bgp group IBGP-SCALED-ROUTES-V6 type internal")
print("set protocols bgp group IBGP-SCALED-ROUTES-V6 local-address 2000::10:0:0:3")
print("set protocols bgp group IBGP-SCALED-ROUTES-V6 family inet6 unicast")
print("set protocols bgp group IBGP-SCALED-ROUTES-V6 apply-groups-except bgp-multipath")
#looping all of above to produce output
for count, dutip, nbip in zip(COUNT,DUTIP, NBIP):
    print("set interfaces ae1 unit 0 family inet6 address " + str(dutip) + "/127")
    print("set protocols bgp group IBGP-SCALED-ROUTES-V6 neighbor " + str(nbip))
