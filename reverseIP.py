# -*- coding: utf-8 -*-

__author__ = 'MaYaSeVeN'

import urllib
import urllib2
import json
import commands
import re
import sys
import subprocess
import platform


def main():
    if len(sys.argv) != 3:
        print "Usage: python " + sys.argv[0] + " " + "[Target IP] [Bing API key]"
        exit(1)

    ip = sys.argv[1]
    key = sys.argv[2]

    if not re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$", ip):
        print "Wrong IP address"
        exit(1)

    query = "IP:" + ip
    print "\nFinding domains in host: " + ip + "\n"
    raw_domains = bing_search(query, key)
    mal_validation(raw_domains)
    check_domain_name_in_scope(raw_domains, ip)


def bing_search(query, key):
    domains = []
    query = urllib.quote(query)
    user_agent = 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Trident/4.0; FDM; .NET CLR 2.0.50727; InfoPath.2; .NET CLR 1.1.4322)'
    credentials = (':%s' % key).encode('base64')[:-1]
    auth = 'Basic %s' % credentials
    url = 'https://api.datamarket.azure.com/Bing/SearchWeb/v1/Web?Query=%27' + query + '%27&$format=json'
    request = urllib2.Request(url)
    request.add_header('Authorization', auth)
    request.add_header('User-Agent', user_agent)
    request_opener = urllib2.build_opener()
    try:
        response = request_opener.open(request)
    except urllib2.HTTPError, e:
        if e.code == 401:
            print 'Wrong API Key or '
            exit(1)
        print "Something's gone wrong!!"
        exit(1)

    response_data = response.read()
    json_result = json.loads(response_data)
    result_list = json_result

    for i in range(len(result_list['d']['results'])):
        domain = result_list['d']['results'][i]['DisplayUrl']
        domain = domain.replace("http://", "").replace("https://", "")
        rest = domain.split('/', 1)[0]
        domains.append(rest)

    raw_domains = list(set(domains))
    return raw_domains


def mal_validation(raw_domains):
    for k in raw_domains:
        if not (re.match('^[a-zA-Z0-9:.-]*$', k)):
            print "Something's gone wrong!!!"
            exit(1)


def check_domain_name_in_scope(raw_domains, ip):
    for l in raw_domains:
        if platform.system() == "Linux":
            status, output = commands.getstatusoutput("nslookup " + l)
            if status != 0:
                print "Something's gone wrong!!!!"
                exit(1)
        elif platform.system() == "Windows":
            p = subprocess.Popen(['nslookup', l], stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
            output, stderr = p.communicate()
        else:
            print "Not support for this OS"
        find_ip = re.findall(r'[0-9]+(?:\.[0-9]+){3}', output)
        ipL = list(set(find_ip))
        for m in ipL:
            if m == ip:
                print l
                break


if __name__ == "__main__":
    main()
