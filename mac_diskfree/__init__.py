from __future__ import division, print_function

import os
import re
import sys
from pprint import pformat, pprint

from mac_diskfree.util import run, linesof
from mac_diskfree.disk import Disk, disk_info


# Set debugging if the local environment has DEBUG set something True
DEBUG = True if os.getenv('DEBUG') else False


def _list_disks_mount(**kwargs):
	"""lists mounted disks using the `mount` command"""

	stdout = run('mount')
	disks = []

	for line in [ l for l in linesof(stdout) if l.startswith('/dev/') ]:
		# all lines that have a local device
		dev, mountpoint = line.split(' on ', 2)
		mountpoint = re.sub('\\s*\\(.*?\\)\\s*$', '', mountpoint)
		disk = Disk(dev, mountpoint, **kwargs)

		disks.append(disk)

	return disks
		

def list_disks(strategy=_list_disks_mount, *args, **kwargs):
	"""gets a list of disks using the specified callable"""
	return strategy(*args, **kwargs)



