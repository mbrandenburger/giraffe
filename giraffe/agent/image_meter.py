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


Image / Glance [NOT IMPLEMENTED]
------------------------  ----------  -------  -------- -----------------------
Name                      Type        Volume   Resource  Note
------------------------  ----------  -------  -------- -----------------------
image                     Gauge             1  image ID  Image polling -> it (still) exists
image.size                Gauge         bytes  image ID  Uploaded image size
image.update              Delta          reqs  image ID  Number of update on the image
image.upload              Delta          reqs  image ID  Number of upload of the image
image.delete              Delta          reqs  image ID  Number of delete on the image
image.download            Delta         bytes  image ID  Image is downloaded
image.serve               Delta         bytes  image ID  Image is served out
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
