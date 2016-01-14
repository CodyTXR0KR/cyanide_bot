#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
import urllib2
import re
import smtplib

# Email dependancies
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from time import strftime
# Requires Imgur's Python api to be installed. >> https://github.com/Imgur/imgurpython
# Documentation >> https://api.imgur.com/
from imgurAPIClient import StartClient
from helpers import get_config

#  Retrieve account credentials from config file
config = get_config()
config.read('auth.ini')
password = config.get('credentials', 'password')

#  Message handler settings (errors/confirmations sent to dev email)
botmail = config.get('credentials', 'botmail')
devmail = config.get('credentials', 'devmail')


def EmailNotify(link):
    msg = MIMEMultipart()
    msg['Subject'] = 'webdev-server.cyanideBot -- message'
    msg['From'] = botmail
    msg['To'] = devmail

    text = MIMEText("cyanideBot>>explosmdotnet has posted an image to Imgur\n" + link)
    msg.attach(text)

    server = smtplib.SMTP('smtp.gmail.com:587')
    server.ehlo()
    server.starttls()
    server.ehlo()
    server.login(botmail, password)
    server.sendmail(botmail, devmail, msg.as_string())
    server.quit()


def EmailError(msg):
    msg = MIMEMultipart()
    msg['Subject'] = 'webdev-server.cyanideBot -- error'
    msg['From'] = botmail
    msg['To'] = devmail

    text = MIMEText("cyanideBot>>explosmdotnet has bailed with error:\n" + msg)
    msg.attach(text)

    server = smtplib.SMTP('smtp.gmail.com:587')
    server.ehlo()
    server.starttls()
    server.ehlo()
    server.login(botmail, password)
    server.sendmail(botmail, devmail, msg.as_string())
    server.quit()

def GetDate():
    return strftime('%b %d %Y')

#  Returns a string containing first regEx match
def GetUrls():
	urls = {}
	response = urllib2.urlopen('http://explosm.net')
	html = response.read()
	urls['imgUrl'] = "http://" + re.findall(r'<img id="featured-comic" src="//(.*?)"/></a>', html)[0]
	urls['permalinkUrl'] = re.findall(r'<input id="permalink" type="text" value="(.*?)" onclick=', html)[0]
	urls['hotlinkUrl'] = re.findall(r'<a href="(.*?)"><img id="featured-comic" src="', html)[0]
	try:
		#return "http://" + imgUrl[0], linkUrl[0]
		return urls
	except Exception as error:
		EmailError(error)
		sys.exit()


def MakePost(client):
	urls = GetUrls()
	meta = {}
	meta['album'] = None
	meta['name'] = None
	meta['title'] = "Daily dose of Cyanide for " + GetDate()
	meta['description'] = "Todays comic -- " + urls['hotlinkUrl'] + "\nPermalink -- " + urls['permalinkUrl'] + "\nFind more at: http://explosm.net"
	try:
		response = client.upload_from_url(urls['imgUrl'], meta, anon=False)
		EmailNotify(response['link'])
	except Exception as error:
		EmailError(error)
		sys.exit()


""" BOT FUNCTIONALITY """
client = StartClient()
MakePost(client)

""" TESTING """
#print GetUrls()