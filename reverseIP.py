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
import optparse


def main():
    usage = "Usage: python " + sys.argv[0] + " -k [Bing API Key] [IP_1] [IP_2] [IP_3] [IP_N]\nUsage: python " + \
            sys.argv[
                0] + " -k [Bing API Key] -l [list file of IP address]"
    parser = optparse.OptionParser(usage=usage)
    parser.add_option("-k", "--key", dest="key", help="Bing API key")
    parser.add_option("-l", "--list", dest="file", metavar="FILE", help="list file of IP address")
    parser.add_option("-r", "--recheck", action="store_true",
                      help="set this option to recheck is that the domain is in IP address with nslookup",
                      default=False)
    (options, args) = parser.parse_args()
    if not options.key or (not options.file and len(args) == 0):
        print parser.format_help()
        print """
you need to..
1.register or use microsoft account for get Bing API key -> https://datamarket.azure.com/
2.choose free plan 5,000 Transactions/month -> https://datamarket.azure.com/dataset/bing/search
        """
        exit(1)

    key = options.key
    recheck = options.recheck
    if not options.file:
        for ip in args:
            reverse_ip(ip, key, recheck)
        exit(0)

    filename = options.file
    file_check(filename, key, recheck)


def file_check(filename, key, recheck):
    try:
        file = open(filename, "r").read()
        find_ip = re.findall(r'[0-9]+(?:\.[0-9]+){3}', file)
        ipL = list(set(find_ip))
        for ip in ipL:
            reverse_ip(ip, key, recheck)
    except IOError:
        print "Error: File does not appear to exist."
        exit(1)


def reverse_ip(ip, key, recheck):
    raw_domains_temp = []
    domains = []
    if not re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$", ip):
        print "Wrong IP address"
        exit(1)

    query = "IP:" + ip
    print "\nHost: " + ip
    count = 0
    while 1:
        raw_domains = bing_call_api(query, key, count)
        if raw_domains == raw_domains_temp:
            break
        raw_domains_temp = raw_domains
        if raw_domains == -1:
            break
        count += 100
        if recheck:
            check_domain_name_in_scope(raw_domains, ip)
        else:
            for l in raw_domains:
                if l not in domains:
                    print l.encode('utf8')
                    domains.append(l)


def bing_call_api(query, key, count):
    domains = []
    query = urllib.quote(query)
    user_agent = 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Trident/4.0; FDM; .NET CLR 2.0.50727; InfoPath.2; .NET CLR 1.1.4322)'
    credentials = (':%s' % key).encode('base64')[:-1]
    auth = 'Basic %s' % credentials
    url = 'https://api.datamarket.azure.com/Bing/SearchWeb/v1/Web?Query=%27' + query + '%27&$format=json' + '&$skip=' + str(
        count)
    request = urllib2.Request(url)
    request.add_header('Authorization', auth)
    request.add_header('User-Agent', user_agent)
    request_opener = urllib2.build_opener()
    try:
        response = request_opener.open(request)
    except urllib2.HTTPError, e:
        if e.code == 401:
            print 'Wrong API Key or not sign up to use Bing Search API'
            print """
you need to..
1.register or use microsoft account for get Bing API key -> https://datamarket.azure.com/
2.choose free plan 5,000 Transactions/month -> https://datamarket.azure.com/dataset/bing/search
        """
            exit(1)
        print "Something's gone wrong!!"
        exit(1)

    response_data = response.read()
    json_result = json.loads(response_data)
    result_list = json_result
    if len(result_list['d']['results']) == 0:
        count = -1
        return count

    for i in range(len(result_list['d']['results'])):
        domain = result_list['d']['results'][i]['DisplayUrl']
        domain = domain.replace("http://", "").replace("https://", "")
        rest = domain.split('/', 1)[0]
        rest = rest.split(':', 1)[0]
        domains.append(rest)

    raw_domains = list(set(domains))
    return raw_domains


def check_domain_name_in_scope(raw_domains, ip):
    domains = []
    for l in raw_domains:
        if l not in domains:
            domains.append(l)
        else:
            continue
        if not (re.match('^[a-zA-Z0-9:.-]*$', l)):
            print "[!]Can not use nslookup to recheck domain " + l.encode('utf8')
            continue
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
                print l.encode('utf8')
                break


if __name__ == "__main__":
    main()
