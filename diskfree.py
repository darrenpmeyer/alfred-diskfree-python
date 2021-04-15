#!/usr/bin/python -u
# from pprint import pprint, pformat
import json
import os

import mac_diskfree

disktype_map = {
	'Generic': 'Generic-Drive-icon',
	'USB': 'USB-HD-Drive-icon',
	'TimeMachine': 'Time-Machine-Drive-icon',
	'SSD': 'SSD-Drive-icon'
}

disks = [ d for d in mac_diskfree.list_disks()\
	if not d.mountpoint.startswith('/private/')\
	and not d.mountpoint.startswith('/System/Volumes/') ]

alfred_items = []
for disk in disks:
	pct_free = float(disk.free(unit=None))/int(disk.size(unit=None))*100
	pct_used = float(disk.used(unit=None))/int(disk.size(unit=None))*100
	item = {
		'title': '{free} ({pct:.1f}%) free on {volume}'.format(free=disk.free(), pct=pct_free, volume=disk.name),
		'subtitle': '{total} total - {used} ({pct:.1f}%) used'.format(total=disk.size(), used=disk.used(), pct=pct_used),
		'arg': disk.mountpoint,
	}

	if disk.is_timemachine:
		disk.type = 'TimeMachine'

	if disk.type in disktype_map:
		item['icon'] = {'path': os.path.join('icons', disktype_map[disk.type] + ".png")}
	else:
		item['icon'] = {'type': 'fileicon', 'path': disk.mountpoint}

	alfred_items.append(item)

print(json.dumps({'items': alfred_items}, indent=3))

# for disk in disks:
# 	print("{vol} ({type}{tm}): {used} of {size} ({pct_used:.1f}%) used, {free} free.".format(
# 		vol=disk.name, type=disk.type,
# 		tm=' TimeMachine disk' if disk.type == 'USB' and disk.is_timemachine else '',
# 		size=disk.size(), used=disk.used(), free=disk.free(),
# 		pct_used=float(disk.used(None))/int(disk.size(None))*100
# 	))
# 	print("INFO: {info}".format(info=pformat(disk._info, indent=3)))