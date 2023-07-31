"""
DNS Server
Based on https://gist.github.com/pklaus/b5a7876d4d2cf7271873
"""

import dnslib
import socketserver
import threading
import time

import HostsManager



def dns_response(data):
	request = dnslib.DNSRecord.parse(data)
	
	qname = request.q.qname
	qn = str(qname)
	qtype = request.q.qtype
	qt = dnslib.QTYPE[qtype]
	
	print(f'{qn = }')

	reply = dnslib.DNSRecord(dnslib.DNSHeader(id=request.header.id, qr=1, aa=1, ra=1), q=request.q)

	domain = HostsManager.get_domain(qn)

	if domain:
		if qn == domain.domain or qn.endswith('.' + domain.domain):
			for name, rrs in domain.RECORDS.items():
				if name == qn:
					for rdata in rrs:
						rqt = rdata.__class__.__name__
						if qt in ['*', rqt]:
							reply.add_answer(dnslib.RR(rname=qname, rtype=getattr(dnslib.QTYPE, rqt), rclass=1, ttl=domain.TTL, rdata=rdata))

			for rdata in domain.NS_RECORDS:
				reply.add_ar(dnslib.RR(rname=domain.domain, rtype=dnslib.QTYPE.NS, rclass=1, ttl=domain.TTL, rdata=rdata))

			reply.add_auth(dnslib.RR(rname=domain.domain, rtype=dnslib.QTYPE.SOA, rclass=1, ttl=domain.TTL, rdata=domain.SOA_RECORD))
	else:
		reply.header.rcode = getattr(dnslib.RCODE,'NXDOMAIN')


	return reply.pack()


class MyDNSHandler(socketserver.BaseRequestHandler):
	def get_data(self):
		return self.request[0] .strip()

	def send_data(self, data):
		return self.request[1].sendto(data, self.client_address)

	def handle(self):
		print('request (%s:%s)' % self.client_address)
		try:
			data = self.get_data()
			resp = dns_response(data)
			self.send_data(resp)
		except Exception as e:
			print('Error:', e)


class MyDNSServer():
	def __init__(self):
		HostsManager.load()

	def __del__(self):
		HostsManager.save()

	def start(self):
		self.svr = socketserver.ThreadingUDPServer(('', 53), MyDNSHandler)
		self.thread = threading.Thread(target=self.svr.serve_forever, daemon=True)
		self.thread.start()
		print('start DNS server')
		print('to exit press Ctrl+C')

	def stop(self):
		self.svr.shutdown()


def main():
	try:
		server = MyDNSServer()
		server.start()
		while True:
			time.sleep(1)
	except KeyboardInterrupt:
		server.stop()


if __name__ == '__main__':
	main()
