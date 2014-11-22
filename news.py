# coding=utf-8
import urllib2
import urllib
import os
import string
import sys
import json
import httplib
import threading
import time
import datetime
import re
import chardet

from bs4 import BeautifulSoup

f = file("filter.json")
myFilter = json.load(f)
f.close

def baidu(keyword, index):
	try:
		url = 'http://news.baidu.com/ns?word=%s&pn=%d&cl=2&ct=1&tn=news&rn=100&ie=utf-8&bt=0&et=0' % (keyword, index)
		req = urllib2.Request(url)
		response = urllib2.urlopen(req)
		the_page = response.read()
		soup = BeautifulSoup(the_page)
		result = soup.find_all('li', {'class':'result'})
		for item in result:
			title = item.h3.a.get_text()
			url = item.h3.a['href'].encode("utf-8")
			s = item.div.p.get_text().encode("utf-8")
			index = s.find('  ')
			source = s[0:index]
			time = s[index + 4:len(s)]
			dateTime = datetime.datetime.strptime(time, "%Y-%m-%d  %H:%M:%S")

			newsDetail(url)

			
			# print title
			# print url
			# print source
			# print dateTime

			print "---------"
	except Exception, e:
		print e
	finally:
		print "done!"

def newsDetail(url):
	try:
		domain = getDomain(url)
		detailFilter = myFilter.get(domain)
		# print myFilter[domain], '111'
		if detailFilter == None:
			print "FILTER NONE - ", url
		else:
			req = urllib2.Request(url)
			req.add_header("User-Agent", "User-Agent	Mozilla/5.0 (iPhone; CPU iPhone OS 7_0 like Mac OS X) AppleWebKit/537.51.1 (KHTML, like Gecko) Version/7.0 Mobile/11A465 Safari/9537.53")
			response = urllib2.urlopen(req)
			the_page = response.read()
			charset = chardet.detect(the_page)
			the_page = the_page.decode(charset['encoding'])
			print charset['encoding']
			soup = BeautifulSoup(the_page)
			# for tag in soup.find_all(attrs={"class":re.compile("\.*gg*")}):
			# 	# print tag
			# 	tag.clear()
			# print "----------"
			# print soup
			result = soup.find(detailFilter['tag'], {detailFilter['attr']: detailFilter['attr_r']})
			print result


			# plainText = result.get_text()


	except Exception, e:
		print e
	finally:
		print "DONE - ", url

def getDomain(url):
	res = r'http:\/\/.*?\/'
	m = re.findall(res, url)
	if len(m) > 0:
		return m[0]

baidu('委员', 100)
# newsDetail('http://news.163.com/14/0522/14/9SRSNH6E00014AEE.html')







