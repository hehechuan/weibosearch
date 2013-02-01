# -*- coding=UTF8 -*-

import urllib2
import urllib
import sys
import StringIO
import gzip
import re
import time
import random
import traceback
import os
import cookielib
import base64
import json
import hashlib
from xlwt.Workbook import *
from xlwt.Style import *


def get_page(url):
	html = fetch_page(url)
	sleep(sleeptime)
	if "pincode" in url.replace("\n", ""):
		print "try pincode"
		time.sleep(10)
		return fetch_page(url)
	else:
		return html

def printout(s):
	if setting['encoding'] != "utf8":
		s = s.decode("utf8").encode(encoding)
	print "%s" % s

def sleep(n):
	printout ("休息 %s 秒先" % n)
	time.sleep(n)

def fetch_page(url):
	global page_fetch_count
	if page_fetch_count == len(cookie):
		page_fetch_count = 0
	printout("%s 抓取页面：%s" % (cookie[page_fetch_count]['username'], url))
	req = urllib2.Request(url)

	header_content = ["Accept:text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8","Accept-Charset:GBK,utf-8;q=0.7,*;q=0.3","Accept-Encoding:gzip,deflate,sdch","Accept-Language:zh-CN,zh;q=0.8","Cache-Control:max-age=0","Connection:keep-alive","Host:s.weibo.com","Referer:http://s.weibo.com/weibo/%25E8%258E%25AB%25E8%25A8%2580%2520%25E8%25AF%25BA%25E8%25B4%259D%25E5%25B0%2594%25E5%25A5%2596&scope=ori&vip=1&timescope=custom:2012-10-13:2012-10-13&Refer=g","User-Agent:Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.97 Safari/537.11"]

	_cookiestr = cookie[page_fetch_count]['cookie']
	header_content.append("Cookie: %s" % _cookiestr)

	page_fetch_count += 1

	for line in header_content:
		tmp = line.strip().split(":")
		key = tmp[0]
		value = ":".join(tmp[1:])
		req.add_header( key , value ) 
	res = urllib2.urlopen( req ) 
	res_encoding = res.info().getheader('Content-Encoding')
	html = res.read() 
	res.close() 
	if res_encoding == "gzip":
		compressedstream = StringIO.StringIO(html)
		gzipper = gzip.GzipFile(fileobj=compressedstream)
		return gzipper.read()
	else:
		return html


def conv(s):
	s = strip_tags(s)
	try:
		return eval("u'%s'" % s).encode("utf8")
	except:
		return ""

def strip_tags(data):
	p = re.compile(r'<.*?>')
	return p.sub('', data)

def get_url(word, day, page):	
	startdate, enddate = day.split("_")
	u = "http://s.weibo.com/weibo/%s&scope=ori&timescope=custom:%s:%s&page=%s&Refer=g" % (urllib.quote(urllib.quote(word)), startdate, enddate, page)
	return u


def get_servertime():
	url = 'http://login.sina.com.cn/sso/prelogin.php?entry=weibo&callback=sinaSSOController.preloginCallBack&su=dW5kZWZpbmVk&client=ssologin.js(v1.3.18)&_=1329806375939'
	data = urllib2.urlopen(url).read()
	p = re.compile('\((.*)\)')
	try:
		json_data = p.search(data).group(1)
		data = json.loads(json_data)
		servertime = str(data['servertime'])
		nonce = data['nonce']
		return servertime, nonce
	except:
		print 'Get severtime error!'
		return None

def get_pwd(pwd, servertime, nonce):
	pwd1 = hashlib.sha1(pwd).hexdigest()
	pwd2 = hashlib.sha1(pwd1).hexdigest()
	pwd3_ = pwd2 + servertime + nonce
	pwd3 = hashlib.sha1(pwd3_).hexdigest()
	return pwd3

def get_user(username):
	username_ = urllib.quote(username)
	username = base64.encodestring(username_)[:-1]
	return username


def login(username, pwd):
	url = 'http://login.sina.com.cn/sso/login.php?client=ssologin.js(v1.3.18)'
	try:
		servertime, nonce = get_servertime()
	except:
		return None
	postdata = get_postdata()
	
	postdata['servertime'] = str(servertime)
	postdata['nonce'] = nonce
	postdata['su'] = get_user(username)
	postdata['sp'] = get_pwd(pwd, servertime, nonce)
	postdata = urllib.urlencode(postdata)
	headers = {'User-Agent':'Mozilla/5.0 (X11; Linux i686; rv:8.0) Gecko/20100101 Firefox/8.0'}
	req  = urllib2.Request(
		url = url,
		data = postdata,
		headers = headers
	)
	result = urllib2.urlopen(req)
	text = result.read()
	p = re.compile('location\.replace\(\'(.*?)\'\)')
	try:
		login_url = p.search(text).group(1)
		#print login_url
		res = urllib2.urlopen(login_url)
		header_info = res.info()
		cookie = []
		for line in header_info['set-cookie'].split(";"):			
			line = line.strip()
			for x in line.split(","):
				tmp = x.strip().split("=")
				if len(tmp) == 2:
					k, v = tmp
					if k not in ["expires", "domain", "path"]:
						cookie.append("%s=%s" %(k,v))						
		return "; ".join(cookie)
	except Exception, e:
		return None

def get_postdata():
	return {
		'entry': 'weibo',
		'gateway': '1',
		'from': '',
		'savestate': '7',
		'userticket': '1',
		'ssosimplelogin': '1',
		'vsnf': '1',
		'vsnval': '',
		'su': '',
		'service': 'miniblog',
		'servertime': '',
		'nonce': '',
		'pwencode': 'wsse',
		'sp': '',
		'encoding': 'UTF-8',
		'url': 'http://weibo.com/ajaxlogin.php?framelogin=1&callback=parent.sinaSSOController.feedBackUrlCallBack',
		'returntype': 'META'
		}




if len(sys.argv) != 2:
	printout("\n=================================================")
	printout("执行有错哈，执行方式：")
	printout("python %s 配置文件名" % sys.argv[0])
	printout("\n配置文件名需要包含三个选项：")
	printout("[search]hadoop flume,flume hbase,flume 安装")
	printout("[date]2012-12-22_2012-12-23,2012-12-24_2012-12-24")
	printout("[account]username/password username1/password1")
	printout("[sleep]抓取间隔时间")
	printout("[encoding]数据输入文件编码")
	printout("[output]输出文件名output.xls")	
	printout("=================================================\n")
	sys.exit()


cj = cookielib.LWPCookieJar()
cookie_support = urllib2.HTTPCookieProcessor(cj)
opener = urllib2.build_opener(cookie_support, urllib2.HTTPHandler)
urllib2.install_opener(opener)


wfile = sys.argv[1]

if os.path.isfile(wfile) == False:
	printout("\n=================================================")
	printout("文件不存在:%s " % sys.argv[1])
	printout("=================================================\n")
	sys.exit()

setting = {}
l = open(wfile)
for line in l:
	key, val = line.strip().split("]")
	setting[key[1:]] = val
l.close()


if setting.has_key("search") == False or setting.has_key("date") == False or setting.has_key("account") == False or setting.has_key("account") == False:
	printout("\n=================================================")
	printout("配置文件有误，请检查")
	printout("=================================================\n")
	sys.exit()


sword = setting['search'].split(",")
dates = setting['date'].split(",")

if setting.has_key("encoding") == False:
	setting['encoding'] = "utf8"

if setting.has_key("sleep"):
	sleeptime = int(setting['sleep'])
else:
	sleeptime = 60

accounts = setting['account'].split(" ")




cookie = {}
i = 0
for account in accounts:
	username, password = account.split("/")
	printout("测试使用%s进行登录" % username)
	_cookie = login(username, password)
	if _cookie != None:
		printout("...............成功")
		cookie[i] = {}
		cookie[i]['username'] = username
		cookie[i]['cookie'] = _cookie
		i += 1
	else:
		printout("...............失败")

if len(cookie) == 0:
	printout("\n=================================================")
	printout("所配置用户登录失败，请检查配置用户名和密码")
	printout("=================================================\n")
	sys.exit()
else:
	sleeptime = int(sleeptime / len(cookie))
	printout("\n=================================================")
	printout("开始进行抓取，抓取过程中请不要关闭本窗口")
	printout("抓取结果将保存到 weibo_%s.txt中" % sys.argv[1])
	if len(cookie) > 1:
		printout("由于您设置了%s个用户，所有抓取时间变更为 %s 秒" % (len(cookie), sleeptime))
	printout("=================================================")
	printout("\n\n登录成功\n\n")

re_username = re.compile("<dt class=\"face\">  <a href=\"(.*?)\" title=\"(.*?)\" target=\"_blank\"")
re_content = re.compile("<em>(.*?)<\/em>")
re_content_url = re.compile("allowForward=1&url=(.*?)&mid=")
re_forward = re.compile("action-type=\"feed_list_forward\"  suda-data=\"(.*?)\">(.*?)</a>")
re_comment = re.compile("action-type=\"feed_list_comment\" suda-data=\"(.*?)\">(.*?)</a>")
re_url_time = re.compile("<\/span> <a href=\"(.*?)\" title=\"(.*?)\" date=\"(.*?)\" class=\"date\" node-type=\"feed_list_item_date\" suda-data=\"(.*?)\">")


ff = open("weibo_%s.txt" % sys.argv[1], "w")

l = "关键词\t用户名\t微博内容\t微博地址\t转发数\t评论数\t发表时间\n"
ff.write(l)

last_url = ""
last_data = ""
page_fetch_count = 0
for word in sword:
	printout("开始抓取 %s " % word)
	if setting['encoding'] != "utf8":
		word = word.decode("gbk").encode("utf8")
	for day in dates:
		if 1 == 1:
			page = 0	
			try:
				url = get_url(word, day, 1)
				last_url = url
				data = get_page(url)
				last_data = data
				##get totalpage#
				content = data.replace("\\n", "").replace("\/", "/").replace("\\\"", "\"")
				re_page = re.compile("<p class=\"W_textc\" node-type=\"totalNum\">(.*?)<\/p>")
				tmp = re_page.findall(content)

				tt = tmp[0].split(" ")
				total = int(tt[1].replace(",", ""))

				page = int(total / 20) + 1
				if page > 50:
					page = 50
				printout( "总共有 %s 页需要抓取" % page )
			except Exception, e:
				printout("出错了哈")
				traceback.print_exc()
				sleep(10)
				pass
			current_page = 1
			
			while current_page <= page:
				try:
					url = get_url(word, day, current_page)
					current_page += 1
					#print url
					#continue
					if url != last_url:
						data = get_page(url)
					else:
						data = last_data
					
					s = "\"pid\":\"pl_weibo_feedlist\""
					tmp = data.split(s)
					end = tmp[1].split(")</script>")
					enda = end[0].split(",\"html\":\"")
					content = enda[1].replace("\\n", "").replace("\/", "/").replace("\\\"", "\"")
					#un = eval("u'%s'" % content)

					#weibo = content.split("<dl class=\"feed_list\"")


					username = []
					weibo_url = []
					weibo_content = []
					content_url = []
					forward = []
					comment = []
					posttime = []

					tmp = re_username.findall(content)
					if tmp != None:
						for i in range(len(tmp)):
							username.append(conv(tmp[i][1]))
							weibo_url.append(tmp[i][0])
							
					tmp = re_content.findall(content)
					if tmp != None:
						for x in tmp:
							weibo_content.append( strip_tags(conv(x)) )

					"""
					tmp = re_content_url.findall(content)
					if tmp != None:
						for x in tmp:
							content_url.append( x )
					"""
					tmp = re_forward.findall(content)
					if tmp != None:
						for x in tmp:
							t = x[1][12:].replace("(", "").replace(")", "")
							if t == "":
								t = "0"
							forward.append(t)

					tmp = re_comment.findall(content)
					if tmp != None:
						for x in tmp:
							t = x[1][12:].replace("(", "").replace(")", "")
							if t == "":
								t = "0"
							comment.append(t)



					tmp = re_url_time.findall(content)
					if tmp!= None:
						for x in tmp:
							content_url.append( x[0] )
							posttime.append( x[ 1])


					total = len(content_url)
					test = []
					for x in range(total):
						"""
						print word
						print username[x]
						print weibo_content[x]
						print content_url[x]
						print forward[x]
						print comment[x]
						print posttime[x]
						print "\n\n"
						"""
						l = "%s\t%s\t%s\t%s\t%s\t%s\t%s" % (word, username[x], weibo_content[x], content_url[x], forward[x], comment[x], posttime[x])
						test.append(l)
					test.append("")
					ff.write("\n".join(test))
				except Exception, e:
					printout ("出错了哈")
					traceback.print_exc()
					pass
ff.close()

printout("抓取完成，结果保存到： weibo_%s.txt" % sys.argv[1])



ff = open("weibo_%s.txt" % sys.argv[1])

style = XFStyle()
wb = Workbook()
ws = wb.add_sheet('0')
row = 0
for line in ff:
	col = 0
	tmp = line.strip().split("\t")
	for x in tmp:
		ws.write(row, col, unicode(x, "utf8"))
		col += 1
	row += 1
ff.close()
wb.save(setting['output'])

printout("生成EXCEL文件：%s" % setting['output'])
os.remove("weibo_%s.txt" % sys.argv[1])




