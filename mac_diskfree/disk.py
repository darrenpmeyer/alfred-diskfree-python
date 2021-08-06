from __future__ import division

from collections import OrderedDict
import re

from mac_diskfree.util import run, linesof

def _disk_info_diskutil(disk):
	"""uses `diskutil info` to get information about a Disk object"""
	stdout = run(['diskutil', 'info', disk.device])
	info = {}

	get_bytes = lambda s : int(re.search('\\((\\d+)\\s+Bytes\\)', s).group(1))

	for line in [ l for l in linesof(stdout) if l.count(':') ]:
		# only process lines that have a k/v pair separated by :
		(key, value) = [ i.strip() for i in line.split(':', 2) ]
		key = re.sub('[^a-z0-9]+', '_', key.lower())
		info[key] = value

	disk.size_bytes = get_bytes(
		info['container_total_space'] if 'container_total_space' in info else info['volume_total_space'])
	disk.free_bytes = get_bytes(
		info['container_free_space'] if 'container_free_space' in info else info['volume_free_space'])

	disk.name = info['volume_name']

	if info['protocol'].startswith('USB'):
		disk.type = 'USB'
	elif info['device_location'] == 'Internal' and info['solid_state'] == "Yes":
		disk.type = 'SSD'
	else:
		disk.type = 'Generic'

	setattr(disk, '_info', info)




def disk_info(disk, strategy=_disk_info_diskutil, *args, **kwargs):
	"""updates Disk object `disk` with information using strategy `strategy`"""
	strategy(disk, *args, **kwargs)


_tmdirectory = None
def timemachine_directory():
	global _tmdirectory
	
	if _tmdirectory is None:
		_tmdirectory = linesof(run(['tmutil', 'machinedirectory']))
	
	return _tmdirectory


class Disk(object):
	def __init__(self, device, mountpoint=None, info_util=disk_info, **kwargs):
		self.device=device
		self.mountpoint=mountpoint

		self._name = None
		self._type = None
		self._size_bytes = None
		self._free_bytes = None
		self._is_timemachine = None

		self._info_util = info_util


	@property
	def name(self):
		if self._name is None:
			self.getinfo()

		return self._name
	
	@name.setter
	def name(self, value):
		self._name = value

	@property
	def type(self):
		if self._name is None:
			self.getinfo()

		return self._type

	@type.setter
	def type(self, value):
		self._type = value
	
	@property
	def size_bytes(self):
		if self._size_bytes is None:
			self.getinfo()

		return self._size_bytes

	@size_bytes.setter
	def size_bytes(self, value):
		self._size_bytes = int(value)
	
	
	@property
	def free_bytes(self):
		if self._free_bytes is None:
			self.getinfo()

		return self._free_bytes

	@free_bytes.setter
	def free_bytes(self, value):
		self._free_bytes = int(value)

	def __repr__(self):
		return '{classname}<{value}>'.format(
			classname=self.__class__.__name__,
			value={ k:v for (k,v) in self.__dict__.items() if not k.startswith('__') })

	@property
	def is_timemachine(self):
		if self._is_timemachine is None:
			self.check_timemachine()

		return self._is_timemachine
	


	@staticmethod
	def _human_size(numbytes, unit='auto'):
		units = OrderedDict()
		units['GB'] = 1000**3
		units['MB'] = 1000**2
		units['KB'] = 1000
		units['B']  = 1


		if unit == 'auto':
			for (u,divisor) in units.items():
				unit = u
				if float(numbytes)/divisor > 1:
					break

		if unit == None:
			return numbytes

		return "{value:.1f} {unit}".format(value=float(numbytes)/units[unit], unit=unit)



	def size(self, unit='auto'):
		"""Reports human_readable size of device"""
		if self.size_bytes is None:
			self.getinfo()

		return Disk._human_size(self.size_bytes, unit=unit)

	def free(self, unit='auto'):
		"""Reports human_readable free space on device"""
		if self.free_bytes is None:
			self.getinfo()

		return Disk._human_size(self.free_bytes, unit=unit)

	def used(self, unit='auto'):
		"""Reports human_readable used sapce on device"""
		if self.size_bytes is None or self.free_bytes is None:
			self.getinfo()

		return Disk._human_size(self.size_bytes - self.free_bytes, unit=unit)

	def getinfo(self, strategy=None):
		strategy = self._info_util if strategy is None else strategy
		return strategy(self)

	def check_timemachine(self):
		for line in timemachine_directory():
			if line.startswith(self.mountpoint):
				self._is_timemachine = True
				break

		if self._is_timemachine is None or self.mountpoint == '/':
			self._is_timemachine = False

		return self._is_timemachine
