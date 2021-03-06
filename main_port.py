#!/usr/bin/env python
#encoding=utf-8

import sys, time, gevent
import handler_cache as mcache

import lib.secon_log_lib as log
import lib.secon_port_lib as portlib
import lib.secon_socket_lib as msglib

def worker(_id):

	_data = mcache.get_port(_id)

	domain = _data.get('domain', False)
	if not domain:
		return False

	port = _data.get('port', False)
	if not port:
		return False

	domain = domain.encode("utf-8")

	resp_time, message = portlib.check(domain, port)

	data_port = {
		'status': 0,
		'time_total': 0,
		'errmsg': message
	}

	if 0 < resp_time:
		data_port['status'] = 1
		data_port['time_total'] = float('%.3f' % resp_time)

	_data.update(data_port)

	msglib.send_msg_object(_data)

	gevent.sleep(int(_data.get('timeout', '1')))

def add_job_port(ids):
	if not ids:
		log.error('main.execute_job', '[Port] not task')
		return False
		
	threads = []
	for _id in ids:
		threads.append(gevent.spawn(worker, _id))
	try:
		gevent.joinall(threads)
	except Exception as e:
		print('This will never be reached')

if __name__ == '__main__' :

	if 1 == len(sys.argv):
		log.error('main.execute_job', 'argv[1] is None')
		sys.exit(0)
	else:
		try:
			int(sys.argv[1])
		except Exception, e:
			log.error('main.execute_job', 'argv[1] is not number')
			sys.exit(0)
		while True:
			mcache.list_port(int(sys.argv[1]), True)
			add_job_port(mcache.get_port_keys())
			time.sleep(60)
			
