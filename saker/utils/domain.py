#!/usr/bin/env python
# -*- coding:utf-8 -*-

import re
import socket


class RES:
    ip = re.compile(r"^(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])$")
    cidr = re.compile(r"\d+\.\d+\.\d+\.\d+(?:\/\d+)?$")
    v4range = re.compile(r"\d+\.\d+\.\d+\.\d+\-\d+\.\d+\.\d+\.\d+$")
    v6range = re.compile(r"[0-9a-fA-F]+:[0-9A-Fa-f:.]+\-[0-9a-fA-F]+:[0-9A-Fa-f:.]+$")
    glob = re.compile(r"\d+\.\d+\.\d+\.\*$")
    bracket = re.compile(r"(.*?)\.(\d+)[\[\{\(](.*)[\)\}\]]$")  # parses '1.2.3.4[5-9]' or '1.2.3.[57]'
    hyphen = re.compile(r"(.*?)\.(\d+)\-(\d+)$")
    hostname = re.compile(r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?)', re.IGNORECASE)


def cidrize(ipstr):
    # TODO
    if isIPv4(ipstr):
        return [ipstr]
    ips = []
    if ',' in ipstr:
        for ip in ipstr.split(","):
            ips.extend(cidrize(ip))
        return list(set(ips))
    if RES.v4range.match(ipstr):
        return ips
    return ips


def isUniversalParsing(domain):
    # 判断是否为泛解析
    # 注：当一个域名解析为空的时候，也会返回True
    try:
        t1 = domain2ips(domain)
        t2 = domain2ips("this-would-not-exists." + domain)
        t3 = domain2ips("i-dont-believe-this-could-exists." + domain)
        if t1 == t2 and t1 == t3:
            return True
    except socket.gaierror as e:
        pass
    return False


def isIPv4(ip):
    # 判断是否为ipv4
    return bool(RES.ip.match(ip))


def isCDN(domain):
    # to do
    pass


def ip2domain(ip):
    domain = 'no-data'
    try:
        domain = socket.gethostbyaddr(ip)[0]
    except socket.herror as e:
        return None
    if domain == 'no-data':
        return None
    return domain


def domain2ips(domain):
    try:
        ips = map(lambda i: i[4][0], socket.getaddrinfo(domain, None))
    except socket.gaierror as e:
        return []
    ips = filter(lambda i: i != "0.0.0.0", ips)
    ips = filter(isIPv4, ips)
    return set(ips)


def gethostip():
    myname = socket.getfqdn(socket.gethostname())
    myaddr = socket.gethostbyname(myname)
    return myaddr


def isInternalIp(ip):

    # https://en.wikipedia.org/wiki/Private_network

    priv_lo = re.compile("^127\.\d{1,3}\.\d{1,3}\.\d{1,3}$")
    priv_24 = re.compile("^10\.\d{1,3}\.\d{1,3}\.\d{1,3}$")
    priv_20 = re.compile("^192\.168\.\d{1,3}.\d{1,3}$")
    priv_16 = re.compile("^172.(1[6-9]|2[0-9]|3[0-1]).[0-9]{1,3}.[0-9]{1,3}$")

    return priv_lo.match(ip) or priv_24.match(ip)\
        or priv_20.match(ip) or priv_16.match(ip) \
        or ip == "localhost"


def isInternal(seed, stype):

    if stype == "IP":
        return isInternalIp(seed)

    if stype == "DOMAIN" or stype == "MAIN_DOMAIN":
        ips = domain2ips(seed)
        for ip in ips:
            if isInternalIp(ip):
                return True

    if stype == "NETBLOCK":
        return isInternalIp(seed.split("/")[0])

    return False


def parseUrl(url):

    if not (url.startswith("http://") or url.startswith("https://")):
        if ':443' in url:
            url = "https://" + url
        else:
            url = "http://" + url

    url = (url + '/') if url[-1] != '/' else url

    return url
