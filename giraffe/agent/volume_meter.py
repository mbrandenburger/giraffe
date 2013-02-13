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


Volume [Block Storage] / Cinder [NOT IMPLEMENTED]
------------------------  ----------  -------  -------- -------------------
Name                      Type        Volume   Resource  Note
------------------------  ----------  -------  -------- -------------------
volume                    Gauge             1  vol ID    Duration of volune
volume.size               Gauge            GB  vol ID    Size of volume
------------------------  ----------  -------  -------- -------------------


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
