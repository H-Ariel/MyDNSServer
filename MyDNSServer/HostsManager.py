from Domain import Domain
import dns.resolver


HOSTS_FILE_PATH = 'hosts.dat' # public host (cache)
MY_HOSTS_FILE_PATH = 'my-hosts.dat' # private host by me (to destroy the world)
ALL_DOMAINS = []
MY_DOMAINS = []



def get_ip_by_domain_name(domain):
	if domain.endswith('.'):
		domain = domain[:-1]
	resolver = dns.resolver.Resolver()
	resolver.nameservers = ['1.1.1.1', '8.8.8.8'] # CloudFlare DNS and Google DNS
	ip = resolver.resolve(domain)[0].to_text()
	return ip


def get_domain(name):
	domain = None
	
	if name in MY_DOMAINS:
		idx = MY_DOMAINS.index(name)
		domain = MY_DOMAINS[idx]
	elif name in ALL_DOMAINS:
		idx = ALL_DOMAINS.index(name)
		domain = ALL_DOMAINS[idx]
	else:
		# if we don't have this IP we request it
		try:
			domain = Domain(name, get_ip_by_domain_name(name))
			ALL_DOMAINS.append(domain)
		except dns.resolver.NXDOMAIN:
			domain = None

	return domain


def load():
	try:
		with open(HOSTS_FILE_PATH, 'r') as f:
			for line in f:
				if not line.startswith('#'):
					splited = line.split()
					if len(splited) == 2:
						domain, ip = splited
						if domain not in ALL_DOMAINS:
							ALL_DOMAINS.append(Domain(domain, ip))
			
	except IOError:
		pass

	try:
		with open(MY_HOSTS_FILE_PATH, 'r') as f:
			for line in f:
				if not line.startswith('#'):
					splited = line.split()
					if len(splited) == 2:
						domain, ip = splited
						if domain not in MY_DOMAINS:
							MY_DOMAINS.append(Domain(domain, ip))
	except IOError:
		pass
	

def save():
	with open(HOSTS_FILE_PATH, 'w') as f:
		for i in ALL_DOMAINS:
			f.write('%s %s\n' % (i.domain, i.IP))
