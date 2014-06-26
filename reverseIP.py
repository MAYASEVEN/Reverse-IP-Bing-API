# -*- coding: utf-8 -*-

__author__ = 'MaYaSeVeN'
__version__ = 'reverseIP version 0.2 ( http://mayaseven.com )'

import urllib
import urllib2
import json
import re
import sys
import optparse
import socket


def main():
    print "\n" + __version__

    usage = "Usage: python " + sys.argv[
        0] + " -k [Bing API Key] [IP_1] [IP_2] [IP_N] [Domain_1] [Domain_2] [Domain_N]\nUsage: python " + \
            sys.argv[
                0] + " -k [Bing API Key] -l [list file of IP address]"
    parser = optparse.OptionParser(usage=usage)
    parser.add_option("-k", "--key", dest="key", help="Bing API key")
    parser.add_option("-l", "--list", dest="file", metavar="FILE", help="list file of IP address")
    parser.add_option("-d", "--disable", action="store_false",
                      help="set this option to disable to recheck is that the domain is in IP address",
                      default=True)
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
    recheck = options.disable
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
        ipl = list(set(find_ip))
        for ip in ipl:
            reverse_ip(ip, key, recheck)
    except IOError:
        print "[-] Error: File does not appear to exist."
        exit(1)


def reverse_ip(ip, key, recheck):
    raw_domains_temp = []
    domains = []
    name = ""
    if not re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$", ip):
        try:
            name = ip
            ip = socket.gethostbyname(ip)
        except socket.gaierror:
            print "[-] unable to get address for " + ip
            return

    query = "IP:" + ip
    print "\n[*] Host: " + ip + " " + name
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
                    print "[+] " + l.encode('utf8')
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
            print '[-] Wrong API Key or not sign up to use Bing Search API'
            print """
you need to..
1.register or use microsoft account for get Bing API key -> https://datamarket.azure.com/
2.choose free plan 5,000 Transactions/month -> https://datamarket.azure.com/dataset/bing/search
        """
            exit(1)
        print "[-] Something's gone wrong!!"
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
            print "[!] Can not recheck domain " + l.encode('utf8') + " please check it by hand."
            continue
        ipc = socket.gethostbyname(l)
        if ipc == ip:
            print "[+] " + l.encode('utf8')
        else:
            print "[!] " + l.encode('utf8') + " is on the other IP address, please recheck it by hand."


if __name__ == "__main__":
    main()
