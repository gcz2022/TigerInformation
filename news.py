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
import jieba
import jieba.analyse
import math
import md5
import sqlite3
from urlparse import urlparse
from bs4 import BeautifulSoup
reload(sys)
sys.setdefaultencoding('utf8')

f = file("filter.json")
myFilter = json.load(f)
f.close

cx = sqlite3.connect("test2.db");
# cu = cx.cursor()

# cu.execute("create table if not exists keyword (name varchar(30))")
# cu.execute("create table if not exists article (keyword varchar(30), title text, source varchar(100), date date, content text, plainText text)")
# cu.execute("insert into keyword values('卢雍政')")
# cx.commit()



def baidu(keyword, index):
	try:
		url = 'http://news.baidu.com/ns?word=%s&pn=%d&cl=3&ct=1&tn=news&rn=100&ie=utf-8&bt=0&et=0' % (keyword, index)
		req = urllib2.Request(url)
		response = urllib2.urlopen(req)
		the_page = response.read()
		soup = BeautifulSoup(the_page)
		result = soup.find_all('li', {'class':'result'})
		for item in result:
			# print item
			title = item.h3.a.get_text()
			url = item.h3.a['href'].encode("utf-8")
			s = item.div.p.get_text().encode("utf-8")
			temp = "  "
			index = s.find(temp)
			source = s[0:index]
			# index = source.find(temp)
			# source = s[0:index]
			time = s[index + 4:len(s)]
			dateTime = datetime.datetime.strptime(time, "%Y-%m-%d  %H:%M:%S")

			newsDetail(url, keyword, title, source, dateTime)

			
			# print title
			# print url
			# print source
			# print dateTime

			# print "---------"
	except Exception, e:
		print e
	finally:
		#print "done!"
		pass

def newsDetail(url, keyword, title, source, dateTime):
	try:
		print "newsDetail"
		domain = getDomain(url)
		detailFilter = myFilter.get(domain)
		# print myFilter[domain], '111'
		if detailFilter == None:
			print "no filter - ", url
		else:
			req = urllib2.Request(url)
			req.add_header("User-Agent", "User-Agent	Mozilla/5.0 (iPhone; CPU iPhone OS 7_0 like Mac OS X) AppleWebKit/537.51.1 (KHTML, like Gecko) Version/7.0 Mobile/11A465 Safari/9537.53")
			response = urllib2.urlopen(req, timeout = 5)
			the_page = response.read()
			charset = chardet.detect(the_page)
			the_page = the_page.decode(charset['encoding'])
			print charset['encoding'], url
			soup = BeautifulSoup(the_page)
			# for tag in soup.find_all(attrs={"class":re.compile("\.*gg*")}):
			# 	# print tag
			# 	tag.clear()
			# print "----------"
			# print soup
			result = soup.find(detailFilter['tag'], {detailFilter['attr']: detailFilter['attr_r']})
			if result == None:
				result = soup.find('font',{"id":"zoom"})
				if result == None:
					result = soup.find('font',{"id":"Zoom"})
					if result == None:
						print "Error"
						return None
			if result == None:
				print "Error"
				return None
			print "1"

			# aList = getArticles(keyword)
			# for article in aList:
			# 	aPlain = article[5]
			# 	aDist = getDistResult(aPlain, result.get_text())
			# 	if aDist < 0.5:
			# 		return None

			# print "2"
			imgdir = 'images'
			for image in result.find_all('img'):
				imgsrc = image['src']
				basename = md5.new(imgsrc).hexdigest()
				extension = os.path.splitext(urlparse(imgsrc).path)[1]
				filename = basename + extension
				image['src'] = filename
				print 'downloading', imgsrc, 'as', filename
				urllib.urlretrieve(imgsrc, '%s/%s' % (imgdir, filename))

			cu = cx.cursor()
			print "insert begin"
			# print type(keyword), type(title), type(unicode(result)), type(result.get_text())
			# print "insert into article (keyword, title, content, plainText) values(%s, %s, %s, %s)" % (keyword, title, unicode(result), result.get_text())
			cu.execute("insert into article (keyword, title, source, date, content, plainText) values('%s', '%s', '%s', '%s', '%s', '%s')" % (keyword, title, source, dateTime, unicode(result), result.get_text()))
			cx.commit()
			print "insert success"
			return result.get_text()
	except Exception, e:
		print e
	# finally:
		# print "done - ", url

def getSegmentation(content):
	result = jieba.analyse.extract_tags(content,20,True)
	# print result
	for string in result:
		print "tag: %s\t\t weight: %f" % (string[0],string[1])


# def cos_dist(a, b):
# 	if len(a) != len(b):
# 		return None
# 	part_up = 0.0
# 	a_sq = 0.0
# 	b_sq = 0.0
# 	for a1, b1 in zip(a,b):
# 		part_up += a1*b1
# 		a_sq += a1**2
# 		b_sq += b1**2
# 	part_down = math.sqrt(a_sq*b_sq)
# 	if part_down == 0.0:
# 		return None
# 	else:
# 		return part_up / part_down

def getDomain(url):
	# res = r'http:\/\/.*?\/'
	# m = re.findall(res, url)
	# if len(m) > 0:
	# 	return m[0]
	topHostPostfix = (
    '.com','.la','.io','.co','.info','.net','.org','.me','.mobi',
    '.us','.biz','.xxx','.ca','.co.jp','.com.cn','.net.cn',
    '.org.cn','.mx','.tv','.ws','.ag','.com.ag','.net.ag',
    '.org.ag','.am','.asia','.at','.be','.com.br','.net.br',
    '.bz','.com.bz','.net.bz','.cc','.com.co','.net.co','.gov.cn'
    '.nom.co','.de','.es','.com.es','.nom.es','.org.es',
    '.eu','.fm','.fr','.gs','.in','.co.in','.firm.in','.gen.in',
    '.ind.in','.net.in','.org.in','.it','.jobs','.jp','.ms',
    '.com.mx','.nl','.nu','.co.nz','.net.nz','.org.nz',
    '.se','.tc','.tk','.tw','.com.tw','.idv.tw','.org.tw',
    '.hk','.co.uk','.me.uk','.org.uk','.vg', ".com.hk")
	regx = r'[^\.]+('+'|'.join([h.replace('.',r'\.') for h in topHostPostfix])+')$'
	pattern = re.compile(regx,re.IGNORECASE)
	print "--"*40
	parts = urlparse(url)
	host = parts.netloc
	m = pattern.search(host)
	res =  m.group() if m else host
	return "unkonw" if not res else res



d = {}
log = lambda x: float('-inf') if not x else math.log(x)
prob = lambda x: d[x] if x in d else 0 if len(x)>1 else 1

def init(filename='SogouLabDic.dic'):
	d['_t_'] = 0.0
	with open(filename, 'r') as handle:
		for line in handle:
			word, freq = line.split('\t')[0:2]
			try:
				word = word.decode('gbk').encode('utf-8')
			except:
				word = word
			# print word
			# word = word.decode('gbk').encode('utf-8')
			d['_t_'] += int(freq)+1
			try:
				d[word] = int(freq)+1
			except:
				d[word] = int(freq)+1
 
def solve(s):
	l = len(s)
	p = [0 for i in range(l+1)]
	t = [0 for i in range(l)]
	for i in xrange(l-1, -1, -1):
		p[i], t[i] = max((log(prob(s[i:i+k])/d['_t_'])+p[i+k], k)
			for k in xrange(1, l-i+1))
	while p[l]<l:
		yield s[p[l]:p[l]+t[p[l]]]
		p[l] += t[p[l]]

def cos_dist(a, b):
	if len(a) != len(b):
		return None
	part_up = 0.0
	a_sq = 0.0
	b_sq = 0.0
	for a1, b1 in zip(a,b):
		part_up += a1*b1
		a_sq += a1**2
		b_sq += b1**2
	part_down = math.sqrt(a_sq*b_sq)
	if part_down == 0.0:
		return None
	else:
		return part_up / part_down

def getDistResult(a1, a2):

	s1 = list(solve(a1))
	s2 = list(solve(a2))

	print s1

	key = list(set(s1 + s2))
	keyLen=len(key)
	keyValue = 0

	sk1=[keyValue]*keyLen
	sk2=[keyValue]*keyLen
	for index,keyElement in enumerate(key):
		if keyElement in s1:
			sk1[index]=sk1[index]+1
		if keyElement in s2:
			sk2[index]=sk2[index]+1 
	return cos_dist(sk1, sk2)

def getAllKeywords():
	cu = cx.cursor()
	cu.execute("select name from keyword")
	return cu.fetchall()

def getArticles(keyword):
	cu = cx.cursor()
	# cu.execute("select title, date, content from article join keyword on keyword.rowid = article.keywordid where name = %s" % keyword)
	cu.execute("select * from article join keyword on keyword.name = article.keyword where name = %s" % keyword)
	#cu.execute("select title, date, content from article, keyword where keyword.rowid = article.keywordid and name = %s" % keyword)
	return cu.fetchall()



init()
keywordList = getAllKeywords()
for key in keywordList:
	print key[0]
	i = 0
	while i < 1000:
		baidu(key[0], i)
		i = i + 100




# s1 = '中国官员独董离职潮仍在继续。中国石油[0.52%资金研报]天然气股份有限公司将在5月22日召开年度股东大会，早前公布的会议议程显示，三位担任公司独立董事的前任副部级、部级官员已不在新一届董事会候选人名单中。'
# s2 = '测试测试测试haha'
# print getDistResult(s1, s2)

# getSegmentation('中国官员独董离职潮仍在继续。中国石油[0.52%资金研报]天然气股份有限公司将在5月22日召开年度股东大会，早前公布的会议议程显示，三位担任公司独立董事的前任副部级、部级官员已不在新一届董事会候选人名单中。')
# baidu('卢雍政', 100)
# newsDetail('http://news.163.com/14/1124/10/ABQEGPBS0001124J.html')



# url1 = 'http://news.163.com/14/1124/06/ABPVMOLE00014AED.html'
# url2 = 'http://news.hexun.com/2014-11-24/170701748.html?from=rss'
# d1 = newsDetail(url1)
# d2 = newsDetail(url2)
# print getDistResult(d1, d2)




