from django.conf import settings
from django.core.cache import cache
from django.shortcuts import redirect, render
from django.urls import path

from urllib.parse import urlparse
import string



from django.core.validators import URLValidator
from django.core.exceptions import ValidationError

import json
from pprint import pprint 
from collections import deque

# Server of search for the shortest route of airports.
# Our task was to make a server where we could search for the shortest route 
# such airports as airbaltic, ryanair, wizzair.
# 1. Extract the necessary data from the file airbaltic.json, 
# ryanair.json and wizzair.json. Function which use is 'airbaltic_code()',
# 'ryanair_code()', 'wizzair_code()', 'airbaltic_city()', 'ryanair_city()', 'wizzair_city()'.
# 2. Then compare the input data with that which have if valid 
# change our input data from City to code. use function is 'rewrite_code()'
# 3. One of the important functions use is 'find_path()'. 
# it is responsible for search the shortest route of airports.
# 4. After that change the code to the City and append them to the list. 
# Use function is 'rewrite_code_2()'
# For avoids the same names we use function 'del_same_city'.

if not settings.configured:
    settings.configure(
        DEBUG=True,
        ROOT_URLCONF=__name__,
        TEMPLATES=[{
            'BACKEND': 'django.template.backends.django.DjangoTemplates',
            'DIRS': ['']
        }]
    )


with open('airbaltic.json') as f:       
    a=json.load(f)

with open('ryanair.json') as f:       
    r=json.load(f)

with open('wizzair.json') as f:
    w=json.load(f)


# avozy= str(input().title())
# bvozy= str(input().title())

class Air():
    def __init__(self, file):
        self.file = file

    # extraction necessary data from file .json. 
    # format 'AAA':['BBB', 'CCC', ], 'DDD':['CCC']
    def airbaltic_code(self):
        di={}
        for k, v in self.file.items():
            if 'destinations' in v:       
                c=v['code']
                d=v['destinations']
            ls=[a[0:3] for a, b in d.items()] 
            di[c]=ls
        airbaltic=di
        # print('1. airbaltic_code - good')       #
        return airbaltic

    # extraction necessary data from file .json. 
    # format [['City' , 'AAA'], ['City', 'BBB']]
    def airbaltic_city(self):
        dis=[]
        for k, v in self.file.items():
            ind=[]
            if 'country' and 'code' in v: 
                contr= v['city']
                coddd= v['code']
                ind.append(contr)
                ind.append(coddd)           
            dis.append(ind)
        # print('2. airbaltic_city - good')
        return dis

    # extraction necessary data from file .json. 
    # format 'AAA':['BBB', 'CCC', ], 'DDD':['CCC']
    def ryanair_code(self):
        di={}
        for v in self.file.values():
            for i in v:
                for k_v, v_v in i.items():
                    if 'iataCode' in k_v:
                        c = i['iataCode']
                        # print(c)
                    if 'routes' in k_v:
                        r= i['routes']
                        g= [i_r.split(':', maxsplit=1) for i_r in r]
                        y = [b.split('|')[0] for a, b in g if a == 'airport']
                        di[c]=y
        ryanair= di
        # print('1. ryanair_code - good')
        return ryanair

    # extraction necessary data from file .json. 
    # format [['City' , 'AAA'], ['City', 'BBB']]
    def ryanair_city(self):
        dis=[]
        for v in self.file.values():
            for i in v:
                for k, v, in i.items():
                    ind=[]
                    if 'iataCode'and 'cityCode'  in k:
                        
                        co = i['iataCode']
                        ko = i['cityCode']
                        ko=ko.split('_')
                        ko=' '.join(ko)
                        ko=ko.title()

                        ind.append(ko)
                        ind.append(co)
                        dis.append(ind)
        # print('2. ryanair_city - good')                  
        return dis

    # extraction necessary data from file .json. 
    # format 'AAA':['BBB', 'CCC', ], 'DDD':['CCC']
    def wizzair_code(self):
        di = {}
        for i in self.file:
            if 'iata' and 'connections' in i:
                c=i['iata']
                r=[k['iata'] for k in i['connections']]
                di[c]=r
        wizzair= di
        # print('1. wizzair_code - good')
        return wizzair

    # extraction necessary data from file .json. 
    # format [['City' , 'AAA'], ['City', 'BBB']]
    def wizzair_city(self):
        dis=[]
        for i in self.file:
            if 'iata' and 'aliases':
                co= i['iata']
                ko=i['aliases']
                ind = []
                for l in ko:
                    # l=l.split('')
                    # # l=l[0]
                    l=l.split(' -')
                    l=l[0]
                    l=l.split('-')
                    l=l[0]
                    
                    l=l.split(' ')
                    
                    if len(l[0])>3:
                        l=l[0]
                    else:
                        l=' '.join(l)
                    l=l.split('\r\n')
                    l=l[0]
                    
                    
                    ind.append(l)
                    ind.append(co)
            dis.append(ind)
        # print('2. wizzair_city - good')    
        return dis


class rewrite_name():
    def __init__(self, dis):
        self.dis = dis
    
    def dis_city(self):
        for i in self.dis:
            if 'Kiev' in i[0]:
                i[0]='Kyiv'
            if 'Aalesund'in i[0]:
                i[0]= 'Alesund'
            if 'Kharkov' in i[0]:
                i[0] = 'Kharkiv'
            if 'Brønnøysund' in i[0]:
                i[0]= 'Bronnoysund'
            if 'Kraków' in i[0]:
                i[0]='Krakow'
            if 'Niš' in i[0]:
                i[0] = 'Nis'
            if 'Memmingen/Munich' in i[0]:
                i[0] = 'Memmingen'
            if 'Prishtina' in i[0]:
                i[0]= 'Pristina'
        return self.dis
       
a_c = Air(a)
a_c = a_c.airbaltic_code()

r_c = Air(r)
r_c = r_c.ryanair_code()

w_c = Air(w)
w_c = w_c.wizzair_code()

a_ci = Air(a)
a_ci = a_ci.airbaltic_city()
a_ci = rewrite_name(a_ci)
a_ci = a_ci.dis_city()

r_ci = Air(r)
r_ci = r_ci.ryanair_city()
r_ci = rewrite_name(r_ci)
r_ci = r_ci.dis_city()

w_ci = Air(w)
w_ci = w_ci.wizzair_city()
w_ci = rewrite_name(w_ci)
w_ci = w_ci.dis_city()


def find_path(graph, start, end):
        dist = {start: [start]}
        q = deque([start])
        while len(q):
            at = q.popleft()
            for next in graph[at]:
                if next not in graph:
                    continue
                if next not in dist:
                    dist[next] = [*dist[at], next]
                    q.append(next)
        return dist[end]
# def find_path(graph, start, end, path=[]):
#     path = path + [start]
#     if start == end:
#         return path
#     if start not in graph:
#         return None
#     for node in graph[start]:
#         if node not in path:
#             newpath = find_path(graph, node, end, path)
#             if newpath: return newpath
#     # print('3. find_code - good')
#     return None

              
class change_code():
    def __init__(self, air_ci, a, b, air_c):
        self.air_ci = air_ci
        self.a = a
        self.b = b
        self.air_c = air_c

    #this we change code from city to AAA, like 'Kyiv' to 'KBP'/
    # air_ci is code whene ['Kyiv', 'KBP']   
    # a and b are names for citise 
    # air_c is code whene {'KBP':['FKI', 'ALL'], ... }
    def rewrite_code(self):           
        try:
            for l in self.air_ci: 
                if self.a == l[0]:
                    nach = l[1]
                if self.b == l[0]:
                    cone = l[1]
            return find_path(self.air_c, nach, cone)
        except:
            nach='KRK'
            cone= 'KRK'
            return find_path(self.air_c, nach, cone)

class change_code_2():
    def __init__(self, l_redi, air_ci):
        self.l_redi = l_redi
        self.air_ci = air_ci

    #this we change code from AAA to Kyiv, like  'KBP' to 'Kyiv',
    # air_ci is code whene ['Kyiv', 'KBP']   
    # l_redi is result from function of def rewrite_code()
    def rewrite_code_2(self):  
        s=[]
        for r in self.l_redi:
            for l in self.air_ci: 
                if r == l[1]:
                    # s.append( [l[0], l[1]] )
                    s.append(l[0] )    # for one variant
        if len(s) == 1 :
            er= ['Unfortunately, our airplane can\'t depart or arrive to the country']
            return er
        else:
            return s
    
class updata_city():
    def __init__(self, list_go):
        self.list_go = list_go

    # if get the same city step by step we must use that function
    def del_same_city(self):
        s=1
        n=len(self.list_go)
        if n>2:
            while True:  
                n=len(self.list_go)
                if s>=n:
                    break            
                
                if self.list_go[s-1] == self.list_go[s]:
                    del self.list_go[s-1]
                else:
                    s+=1
        else:
            pass
        return self.list_go

def index(request):
    avozy, bvozy = None, None 
    cache.add(avozy, bvozy)

    avozy = request.POST.get("avozy")
    bvozy = request.POST.get("bvozy")
    try:   
        avozy= str(avozy.title())
        bvozy= str(bvozy.title())
    except:
        pass

    if avozy and bvozy:
        try:
            
            air_a = change_code(a_ci, avozy, bvozy, a_c)
            a = air_a.rewrite_code()

            a_ch = change_code_2(a, a_ci)
            a_ch = a_ch.rewrite_code_2()


            air_r = change_code(r_ci, avozy, bvozy, r_c)
            r = air_r.rewrite_code()

            r_ch = change_code_2(r, r_ci)
            r_ch = r_ch.rewrite_code_2()


            air_w = change_code(w_ci, avozy, bvozy, w_c)
            w = air_w.rewrite_code()

            w_ch = change_code_2(w, w_ci)
            w_ch = w_ch.rewrite_code_2()


            res_a = updata_city(a_ch)
            res_a = res_a.del_same_city()

            res_r = updata_city(r_ch)
            res_r = res_r.del_same_city()

            res_w = updata_city(w_ch)
            res_w = res_w.del_same_city()


            d={}

            d['Airbaltic ']= res_a
            d['Ryanair ']= res_r
            d['Wizzair ']= res_w

            return render(request, 'index.html', {'air_0': res_a, 'a':'Airbaltic: ','air_1': res_r, 'r':'Ryanair: ','air_2': res_a, 'w':'Wizzair: '})
  
        except:
            return render(request, 'index.html')
    else:
        return render(request, 'index.html')

def redirect_view(request, avozy, bvozy):
    link = cache.get(avozy, bvozy)

    try:
        return redirect(link)
    except:
        return redirect(to='/')


urlpatterns = [
    path('', index),
    path(r'<avozy, bvozy>', redirect_view),
]


if __name__ == '__main__':
    import sys
    from django.core.management import execute_from_command_line
    execute_from_command_line(sys.argv)