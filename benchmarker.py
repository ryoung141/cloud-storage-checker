#!/usr/bin/env python

import sys
import time
import string
import socket
import struct
import requests
from httplib import HTTPConnection

class Benchmarker(object):

	TARGETS = [1, 2, 3] #GET vars for accessing the AWS download files

	#5MB, 20MB, 50MB file sizes
	GOOGLE_TARGETS = ["/uc?export=download&id=1qrdr2duyO7icb-XTRDJ_Qx9cZWg05jEu", "/uc?export=download&id=1iTq9a-g4G3lc56cD0WceNnS3WWq98spO", "/uc?export=download&id=1gS1Z-92XN_cVm5nU0pEJoV4JZRQwngUQ"]

	DROPBOX_TARGETS = ["/s/qxivhtkx2ozub5y/5MB%20%281%29.zip?dl=1", "/s/wy3t49dd4rwglm0/20MB%20%282%29.zip?dl=1", "/s/sbh8fti3s8x16px/50MB.zip?dl=1"]

	PORT = 33445 
	MAX_HOPS =  30

	#sock const inits
	UDP = socket.getprotobyname('udp')
	ICMP = socket.getprotobyname('icmp')

	def __init__(self, iterations, host=None):
		if host == None:
			self.host = "ec2-18-188-17-9.us-east-2.compute.amazonaws.com"
		else:
			self.host = host
		self.iterations = iterations


	def connect(self, url):
		try:
			conn = HTTPConnection(url)
			conn.connect()
			return conn

		except:
			print("Host not accessible at this time")

	def download(self):

		#init vars
		total_dl = 0
		start = time.time()
		for target in Benchmarker.TARGETS:
			print("http://" +self.host + "/download.php?f=" + str(target))
			for _iter in range(self.iterations):
				r = requests.get("http://" + self.host + "/download.php?f="+str(target))
				total_dl += len(r.content)
				print total_dl

		total_time = (time.time() - start)


		return total_dl / (1000000.0 * total_time) #B/s --> MB/s

	def customDownload(self, path_list):

		total_dl = 0
		start = time.time()
		for target in path_list:
			print("http://" + self.host + str(target))
			for _iter in range(self.iterations):
				r = requests.get("http://"+self.host + str(target))
				total_dl += len(r.content)
				print total_dl

		total_time = (time.time() - start)

		return total_dl / (1000000.0 * total_time)

	def init_sockets(self, ttl):
		out_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, Benchmarker.UDP)
		in_sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, Benchmarker.ICMP)
		out_sock.setsockopt(socket.SOL_IP, socket.IP_TTL, ttl)
		in_sock.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)

		t_o = struct.pack("ll", 5, 0)
		in_sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVTIMEO, t_o)

		return in_sock, out_sock

	def get_rtt_hops(self, host = None):
		if host == None:
			host = self.host
		destination = socket.gethostbyname(host)
		print(host)
		ttl = 1
		rtt = time.time()

		while True:
			in_sock, out_sock = self.init_sockets(ttl)
			in_sock.bind(("", Benchmarker.PORT))
			out_sock.sendto(b'', (host, Benchmarker.PORT))

			try:
				pack, current = in_sock.recvfrom(512)
				current = current[0]

				try:
					name = socket.gethostbyaddr(current)[0]
				except socket.error:
					name = current

			except Exception, e:
				if str(e) != "[Errno 11] Resource temporarily unavailable":
					print(e)
				pass

			finally:
				in_sock.close()
				out_sock.close()

			if current is not None:
				current_host = "%s : %s" % (current, name)
			else:
				current_host = "*"
			print("%d\t%s" % (ttl, current_host))

			if current == destination:
				rtt_end = time.time() - rtt
			if ttl >= Benchmarker.MAX_HOPS:
				print("Max Hop count reached, terminating...")
				print("Last hop attempted: \n" + current_host)
				return ttl
			ttl += 1	

	def amazonTest(self):
		print "NOW RUNNING AMAZON TEST SUITE\n"
		dl_speed = self.download()
		hop_count = 0
		print "NOW PERFORMING TRACEROUTE FOR AMAZON\n"
		for _iter in range(self.iterations):
			hop_count += self.get_rtt_hops()
		hop_count = hop_count / self.iterations
		ratio = dl_speed / hop_count
		return ratio

	def googleTest(self):
		print "NOW RUNNING GOOGLE DRIVE TEST SUITE\n"
		dl_speed = self.customDownload(Benchmarker.GOOGLE_TARGETS)
		hop_count = 0
		print "NOW PERFORMING TRACEROUTE FOR GOOGLE DRIVE\n"
		for _iter in range(self.iterations):
			hop_count += self.get_rtt_hops()
		hop_count = hop_count / self.iterations
		ratio = dl_speed / hop_count
		return ratio

	def dropboxTest(self):
		print "NOW RUNNING DROPBOX TEST SUITE\n"
		dl_speed = self.customDownload(Benchmarker.DROPBOX_TARGETS)
		hop_count = 0
		print "NOW PERFORMING TRACEROUTE FOR DROPBOX\n"
		for _iter in range(self.iterations):
			hop_count += self.get_rtt_hops()
		hop_count = hop_count / self.iterations
		ratio = dl_speed / hop_count
		return ratio



def main():
	b1 = Benchmarker(int(sys.argv[1]))
	b2 = Benchmarker(int(sys.argv[1]), "drive.google.com")
	b3 = Benchmarker(int(sys.argv[1]), "dropbox.com")

	a = b1.amazonTest()
	g = b2.googleTest()
	d = b3.dropboxTest()

	arr = {'Amazon': a, 'Google Drive': g, 'Dropbox': d}
	arr = sorted(arr.items(), key=lambda x: x[1], reverse=True)
	i=0
	for tup in arr:
		key = [x[0] for x in arr]
		val = [x[1] for x in arr]
		print str(key[i]) + " had CQuality factor of: " + str(val[i])
		print "Rank: " + str(i+1)
		i+=1


if __name__ == '__main__':
	main()