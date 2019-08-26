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

with open('airbaltic.json') as f:       
    a=json.load(f)

with open('ryanair.json') as f:       
    r=json.load(f)

with open('wizzair.json') as f:
    w=json.load(f)


if not settings.configured:
    settings.configure(
        DEBUG=True,
        ROOT_URLCONF=__name__,
        TEMPLATES=[{
            'BACKEND': 'django.template.backends.django.DjangoTemplates',
            'DIRS': ['']
        }]
    )


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
           
            #  extraction necessary data from file .json. 
            # format 'AAA':['BBB', 'CCC', ], 'DDD':['CCC']
            def airbaltic_code(file):
                di={}
                for k, v in file.items():
                    if 'destinations' in v:       
                        c=v['code']
                        d=v['destinations']
                    ls=[a[0:3] for a, b in d.items()] 
                    di[c]=ls
                airbaltic=di
                # print('1. airbaltic_code - good')       #
                return airbaltic
            a_c=airbaltic_code(a)
           
            #  extraction necessary data from file .json. 
            # format 'AAA':['BBB', 'CCC', ], 'DDD':['CCC']
            def ryanair_code(file):
                di={}
                for v in file.values():
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
            r_c=ryanair_code(r)
           
            #  extraction necessary data from file .json. 
            # format {'AAA':['BBB', 'CCC', ], 'DDD':['CCC']}
            def wizzair_code(file):
                di = {}
                for i in file:
                    if 'iata' and 'connections' in i:
                        c=i['iata']
                        r=[k['iata'] for k in i['connections']]
                        di[c]=r
                wizzair= di
                # print('1. wizzair_code - good')
                return wizzair
            w_c=wizzair_code(w)


            #  extraction necessary data from file .json. 
            # format [['City' , 'AAA'], ['City', 'BBB']]
            def airbaltic_city(file):
                dis=[]
                for k, v in file.items():
                    ind=[]
                    if 'country' and 'code' in v: 
                        contr= v['city']
                        coddd= v['code']
                        ind.append(contr)
                        ind.append(coddd)           
                    dis.append(ind)
                for i in dis:
                    if 'Kiev' in i[0]:
                        i[0]='Kyiv'
                    if 'Aalesund'in i[0]:
                        i[0]= 'Alesund'
                    if 'Kharkov' in i[0]:
                        i[0] = 'Kharkiv'
                    if 'Brønnøysund' in i[0]:
                        i[0]= 'Bronnoysund'
                # print('2. airbaltic_city - good')
                return dis
            a_ci=airbaltic_city(a)

            #  extraction necessary data from file .json. 
            # format [['City' , 'AAA'], ['City', 'BBB']]
            def ryanair_city(file):
                dis=[]
                for v in file.values():
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
                for i in dis:
                    if 'Kiev' in i[0]:
                        i[0]='Kyiv' 
                    if 'Brønnøysund' in i[0]:
                        i[0]= 'Bronnoysund' 
                # print('2. ryanair_city - good')                  
                return dis
            r_ci=ryanair_city(r)

            #  extraction necessary data from file .json. 
            # format [['City' , 'AAA'], ['City', 'BBB']]
            def wizzair_city(file):
                dis=[]
                for i in file:
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

                for i in dis:
                    if 'Kraków' in i[0]:
                        i[0]='Krakow'
                    if 'Niš' in i[0]:
                        i[0] = 'Nis'
                    if 'Memmingen/Munich' in i[0]:
                        i[0] = 'Memmingen'
                    if 'Prishtina' in i[0]:
                        i[0]= 'Pristina'
                    if 'Brønnøysund' in i[0]:
                        i[0]= 'Bronnoysund'
                # print('2. wizzair_city - good')    
                return dis
            w_ci=wizzair_city(w)

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






            #this we change code from city to AAA, like 'Kyiv' to 'KBP'/
            # air_ci is code whene ['Kyiv', 'KBP']   
            # a and b are names for citise 
            # air_c is code whene {'KBP':['FKI', 'ALL'], ... }

            def rewrite_code(air_ci, a, b, air_c):           
                try:
                    for l in air_ci: 
                        if a == l[0]:
                            nach = l[1]
                        if b == l[0]:
                            cone = l[1]
                    return find_path(air_c, nach, cone)
                except:
                    nach='KRK'
                    cone= 'KRK'
                    return find_path(air_c, nach, cone)
 


            



            #this we change code from AAA to Kyiv, like  'KBP' to 'Kyiv',
            # air_ci is code whene ['Kyiv', 'KBP']   

            # l_redi is result from function of def rewrite_code()
            def rewrite_code_2(l_redi, air_ci):  
                s=[]
                for r in l_redi:
                    for l in air_ci: 
                        if r == l[1]:
                            # s.append( [l[0], l[1]] )
                            s.append(l[0] )    # for one variant
                if len(s) == 1 :
                    er= ['Unfortunately, our airplane can\'t depart or arrive to the country']
                    return er
                else:
                    return s




            # if get the same city step by step we must use that function
            def del_same_city(list_go):
                s=1
                n=len(list_go)
                if n>2:
                    while True:  
                        n=len(list_go)
                        if s>=n:
                            break            
                        
                        if list_go[s-1] == list_go[s]:
                            del list_go[s-1]
                        else:
                            s+=1
                else:
                    pass
                return list_go

            block_air_ci=[a_ci,r_ci,w_ci]
            block_air_c=[a_c, r_c, w_c]

            u=[]
            try: 
                for air_c, air_ci in zip(block_air_c, block_air_ci):
                    r_c=rewrite_code(air_ci, avozy, bvozy, air_c)
                    r_c_2 = rewrite_code_2(r_c, air_ci)  
                    h=del_same_city(r_c_2)                  
                    u.append(h)
            except:
                return render(request, 'index.html', {'err':'Try again, one of the cities: '+'\"'+avozy+'\"'+' or '+'\"'+bvozy+'\"'+' isn`t correct'})
            # d={}
            # # u[0].insert(0, 'Airbaltic: ')
            # # u[1].insert(0, 'Ryanair: ')
            # # u[2].insert(0, 'Wizzair: ')
            # # print(u)
            # d['Airbaltic ']= u[0]
            # d['Ryanair ']= u[1]
            # d['Wizzair ']= u[2]
            # print(timeit(lambda:d))

            # pprint(d)
    #         aaa= del_same_city(end)
           
            return render(request, 'index.html', {'air_0': u[0], 'a':'Airbaltic: ','air_1': u[1], 'r':'Ryanair: ','air_2': u[2], 'w':'Wizzair: '})
  
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