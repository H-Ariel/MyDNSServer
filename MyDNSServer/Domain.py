import dnslib


class DomainName(str):
	def __getattr__(self, item):
		return DomainName(item + '.' + self)


class Domain:
	def __init__(self, domain, ip='127.0.0.1'):
		if domain == '': raise Exception('empty domain')
		if domain[-1] != '.': domain += '.'

		self.domain = DomainName(domain)
		self.IP = ip
		self.TTL = 60 * 5
		self.SOA_RECORD = dnslib.SOA(
			mname=self.domain.ns1, # primary name server
			times=(
				201307231, # serial number
				60 * 60 * 1, # refresh
				60 * 60 * 3, # retry
				60 * 60 * 24, # expire
				60 * 60 * 1, # minimum
				)
			)
		self.NS_RECORDS = [dnslib.NS(self.domain.ns1), dnslib.NS(self.domain.ns2)]
		self.RECORDS = {
			self.domain: [dnslib.A(self.IP), dnslib.AAAA((0,) * 16), self.SOA_RECORD] + self.NS_RECORDS,
			self.domain.ns1: [dnslib.A(self.IP)],
			self.domain.ns2: [dnslib.A(self.IP)],
			self.domain.www: [dnslib.A(self.IP)],
			}

	def __eq__(self, other):
		if isinstance(other, str):
			return other == self.domain or other == self.IP
		elif isinstance(other, self.__class__):
			return other.domain == self.domain and other.IP == self.IP
		return False
