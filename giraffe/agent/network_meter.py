"""
In giraffe (as known from ceilometer), three type of meters are defined:

----------  -------------------------------------------------------------------
Type        Definition
----------  -------------------------------------------------------------------
Cumulative  Increasing over time (e.g., instance hours)
Gauge       Discrete items (e.g., running instances)
            and fluctuating values (e.g., disk I/O)
Delta       Changing over time (bandwidth)
----------  -------------------------------------------------------------------


Meters (by components) that are [not yet] implemented:


Network / Quantum [NOT IMPLEMENTED]
------------------------  ----------  -------  -------- -----------------------
Name                      Type        Volume   Resource  Note
------------------------  ----------  -------  -------- -----------------------
network                   Gauge             1  netw ID   Duration of network
network.create            Delta       request  netw ID   Creation requests for this network
network.update            Delta       request  netw ID   Update requests for this network
subnet                    Gauge             1  subnt ID  Duration of subnet
subnet.create             Delta       request  subnt ID  Creation requests for this subnet
subnet.update             Delta       request  subnt ID  Update requests for this subnet
port                      Gauge             1  port ID   Duration of port
port.create               Delta       request  port ID   Creation requests for this port
port.update               Delta       request  port ID   Update requests for this port
router                    Gauge             1  rtr ID    Duration of router
router.create             Delta       request  rtr ID    Creation requests for this router
router.update             Delta       request  rtr ID    Update requests for this router
ip.floating               Gauge             1  ip ID     Duration of floating ip
ip.floating.create        Delta             1  ip ID     Creation requests for this floating ip
ip.floating.update        Delta             1  ip ID     Update requests for this floating ip
------------------------  ----------  -------  -------- -----------------------


Naming convention
-----------------
If you plan on adding meters, please follow the convention bellow:

1. Always use '.' as separator and go from least to most discriminent word.
   For example, do not use ephemeral_disk_size but disk.ephemeral.size

2. When a part of the name is a variable, it should always be at the end and
   start with a ':'. For example do not use <type>.image but image:<type>, 
   where type is your variable name.
"""

pass
