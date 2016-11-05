#!/usr/bin/python
import time
import dns.resolver #import the module
import subprocess

nginx_proc="/opt/nginx/sbin/nginx"
nginx_reload_arg = "-s reload"
nginx_upstream_conf = "/opt/nginx/conf/upstream.conf"

def validate_ip(s):
    a = s.split('.')
    if len(a) != 4:
        return False
    for x in a:
        if not x.isdigit():
            return False
        i = int(x)
        if i < 0 or i > 255:
            return False
    return True

def populate_hosts(fname):
  servers= []
  with open(fname) as f:
    for line in f:
      l = line.strip()
      if l.startswith("server "):
        s = l.split()[1]
        s = s.split(":")[0]
        if not validate_ip(s):
          servers.append(s)
  return servers
        
def resolve_dns(servers):
  servers_dict = {}
  myResolver = dns.resolver.Resolver() #create a new instance named 'myResolver'
  for server in servers:
    try:
      myAnswers = myResolver.query(server, "A") 
      resolvered_ips = {}
      for rdata in myAnswers:
        #print("resolving server :" + server + " with ip:" + str(rdata))
        resolvered_ips[str(rdata)] = 1
        
      #print("add server :" + server + " values:" + str(resolvered_ips))
      servers_dict[server] = resolvered_ips
    except Exception as e:
      a=1
      #print "Query failed for server:" + server +  ", Error:" + str(e)
  return servers_dict

def compare_dict(old_dict, new_dict):
  for key in old_dict:
    #print("Checking Host: " + key )
    old_val = old_dict[key]
    if key in new_dict:
      new_val = new_dict[key]
    else:
      print("Host: " + key + ", not found in new dict")
      return False
    if not new_val or not old_val:
      print("Host: " + key + ", not found")
      return False
    if type(new_val) is dict and type(old_val) is dict:
      if not compare_dict(old_val, new_val):
        return False
  return True

old_dict = {}  
while True:
  #print("#####Loading the nginx upstream file")
  servers = populate_hosts(nginx_upstream_conf)
  new_dict=resolve_dns(servers)
  #print("#####Comparing with previous dns results")
  #print("old_dict:" + str(old_dict))
  #print("new_dict:" + str(new_dict))
  if not compare_dict(old_dict, new_dict):
    print("reload nginx..")
    subprocess.call(nginx_proc, nginx_reload_arg)
  old_dict = new_dict
  time.sleep( 5 )
