"""Common utility functions"""

import subprocess


LINESEP = "\n"     # newline
FIELDSEP = "\x20"  # space char


def run(command, raw=False, encoding='utf8', *args, **kwargs):
	"""Runs `command` using subprocess.Popen() and captures STDOUT

	additional args and kwargs will be passed on to Popen's call.

	If `raw` is `True`, then will return the constructed Popen directly;
	otherwise, will return the resulting stdout

	Specify `encoding` if something other than utf8 output is desired
	(no effect if `raw` is `True`); `None` will result in raw bytes
	"""
	proc = subprocess.Popen(command, stdout=subprocess.PIPE)
	
	if raw:
		return proc

	stdout = proc.communicate()[0]
	if encoding is None:
		return stdout

	return stdout.decode(encoding)


def fieldsof(string, fieldsep=FIELDSEP):
	return string.split(fieldsep)


def linesof(string, linesep=LINESEP):
	return string.split(linesep)