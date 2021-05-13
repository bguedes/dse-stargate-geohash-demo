

#  Single page Web application written in Python. Displays geo-
#  spatial and GraphQL using K8ssandra.
#
#    .  Web page will serve at localhost:8084
#
#       There are instructions on this Web page; How this program
#       functions.


#############################################################
## Imports ##################################################


#  Flask is our Python based Web server.
#
#  pip3 install flask
#
from flask import Flask, render_template, request, jsonify


#  This import allows us to use a directory other than the
#  default for Flask CSS files and related.
#
import os


#  This import allows us to read connection values from a local
#  file titled,   .env
#
#  pip3 install python-decouple
#
from decouple import config


#  Geohash library
#
#  pip3 install libgeohash
#
import libgeohash as gh


#  Ability to execute queries using GraphQL
#
#   pip3 install gql
#
import requests
import json
import urllib3
import time
   #
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport


#  Suppresses SSL warnings (this being a demo program)
#
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


#############################################################
#############################################################


#  Used to connect with our database server
#

#MY_STARGATE_IP = config('MY_STARGATE_IP')
MY_STARGATE_IP = "172.27.0.5"

MY_DB_USERNAME = "cassandra"
MY_DB_PASSWORD = "cassandra"
#MY_DB_USERNAME = config('MY_CASS_USER')
#MY_DB_PASSWORD = config('MY_CASS_PASS')
   #
MY_MAXRETRIES  = 10


#############################################################
#############################################################


#  Get Authorization Token to be able to speak to C*
#

l_url1 = "http://" + MY_STARGATE_IP + ":8081/v1/auth"
      #
l_data1 = '{"username":"' + MY_DB_USERNAME + '", \
   "password":"' + MY_DB_PASSWORD + '"}'

for _ in range(MY_MAXRETRIES):
   try:
      response = requests.post(l_url1, data=l_data1,headers=
         {"Content-Type": "application/json"})
   except:
      #  If Astra free tier, we get the occasional time outs
      #
      time.sleep(0.25)
      print("NOTICE: Bump 1")
      continue
   else:
      break
else:
   print("")
   print("")
   print("ERROR (7442): Failed to connect with K8ssandra/Cassandra instance.")
   print("")
   print("")
   exit(3)

my_authToken = response.json()['authToken']
   #
print("INFO: Got Authorization Token, " + my_authToken)


#############################################################
#############################################################


#  Connection handle, Query below via GraphQL
#

l_url3 = "http://" + MY_STARGATE_IP + ":8080/graphql/my_keyspace"

l_transport=RequestsHTTPTransport(
    url=l_url3,
    use_json=True,
    headers={
        "Content-type": "application/json",
        "X-Cassandra-Token": my_authToken,
    },
    verify=False,
    retries=3,
)

m_client = Client(
    transport=l_transport,
    fetch_schema_from_transport=True,
)


#############################################################
## Inits, Opens, and Sets ###################################


#  Instantiate Flask object
#
m_app = Flask(__name__)


#  Set flask defaults for locating files
#
m_templateDir = os.path.abspath("45_views" )
m_staticDir   = os.path.abspath("44_static")
   #
m_app.template_folder = m_templateDir
m_app.static_folder   = m_staticDir


#############################################################
## Our Web pages (page handlers) ############################


#
#  This is our main page.
#
#  This ia a single page Web app; after this page loads,
#  everything else is just data/AJAX.
#
@m_app.route('/')
def do_servePage():
   return render_template("60_Index.html")


      ###############################################


#  This is our query response (page)
#

@m_app.route('/_do_query')
def do_query():

   l_lat        = request.args.get('h_lat'        )
   l_lng        = request.args.get('h_lng'        )
   l_textFilter = request.args.get('h_textFilter' )
      #
   l_latLng = gh.encode(float(l_lat), float(l_lng), precision=5)
      #
   print("")
   print("INFO: Query using (geo_hash5), " + l_latLng)
   print("")

   l_markers = query_function(l_latLng, l_textFilter)
      #
   return jsonify(l_markers)


      ###############################################


#  sample output from gh.neighbors(),
#
#    {'e': '9xj3v', 'sw': '9xj3e', 'ne': '9xj6j', 'n': '9xj6h',
#       's': '9xj3s', 'w': '9xj3g', 'se': '9xj3t', 'nw': '9xj65'}
#

def query_function(i_latLng, i_textFilter):
   global m_client


   #  'C0' is our center point, where we query from
   #
   #  This is also the data set displayed when walking
   #
   l_loca_C0 = i_latLng

   #  'neighbors1' are the first set of points just past our
   #  center, the first ring, if you will
   #
   #  This is also the data set displayed when driving slow
   #
   l_neighbors1 = gh.neighbors(l_loca_C0)

   #  And anything (2) are our second ring of points, just
   #  past our first ring. Generally displayed when driving
   #  fast.
   #
   l_N2  = gh.neighbors(l_neighbors1['n' ])['n' ]
   l_E2  = gh.neighbors(l_neighbors1['e' ])['e' ]
   l_S2  = gh.neighbors(l_neighbors1['s' ])['s' ]
   l_W2  = gh.neighbors(l_neighbors1['w' ])['w' ]
      #
   l_NE2 = gh.neighbors(l_neighbors1['ne'])['ne']
   l_SE2 = gh.neighbors(l_neighbors1['se'])['se']
   l_SW2 = gh.neighbors(l_neighbors1['sw'])['sw']
   l_NW2 = gh.neighbors(l_neighbors1['nw'])['nw']

   #  Building our query string when a name is specified for
   #  a business.
   #
   if (len(i_textFilter) >= 7):
      l_textFilter = ', name7: "' + i_textFilter[:7] + '"'
   elif (len(i_textFilter) >= 5):
      l_textFilter = ', name5: "' + i_textFilter[:5] + '"'
   elif (len(i_textFilter) >= 3):
      l_textFilter = ', name3: "' + i_textFilter[:3] + '"'
   else:
      l_textFilter = ' '
         #
   print(len(l_textFilter))
   print("INFO: Text Filter, " + l_textFilter)

   #  The column list we return from query
   #
   l_columnList = " md_lat md_lng md_name md_address md_city md_province md_phone md_subcategory "

   print("values 0: -- " + l_loca_C0)
   print("values 1: -- " + l_neighbors1['n'])
   print("values 2: -- " + l_neighbors1['e'])
   print("values 3: -- " + l_neighbors1['s'])
   print("values 4: -- " + l_neighbors1['w'])
   print("values 5: -- " + l_neighbors1['ne'])
   print("values 6: -- " + l_neighbors1['se'])
   print("values 7: -- " + l_neighbors1['sw'])
   print("values 8: -- " + l_neighbors1['nw'])
   print("values 9: -- " + l_N2)
   print("values 10: -- " + l_E2)
   print("values 11: -- " + l_S2)
   print("values 12: -- " + l_W2)
   print("values 13: -- " + l_NE2)
   print("values 14: -- " + l_SE2)
   print("values 15: -- " + l_SW2)
   print("values 16: -- " + l_NW2)
   print("values 17: -- " + l_textFilter)
   print("values 18: -- " + l_columnList)


   #  Building the final query string; GraphQL query strings can get long
   #
   l_queryString = '''
      query {{

        C0 : my_mapdata(value:  {{ geo_hash5: "{0}"  {17} }} ) {{ values {{ {18} }} }}

        N1 : my_mapdata(value:  {{ geo_hash5: "{1}"  {17} }} ) {{ values {{ {18} }} }}
        E1 : my_mapdata(value:  {{ geo_hash5: "{2}"  {17} }} ) {{ values {{ {18} }} }}
        S1 : my_mapdata(value:  {{ geo_hash5: "{3}"  {17} }} ) {{ values {{ {18} }} }}
        W1 : my_mapdata(value:  {{ geo_hash5: "{4}"  {17} }} ) {{ values {{ {18} }} }}

        NE1 : my_mapdata(value: {{ geo_hash5: "{5}"  {17} }} ) {{ values {{ {18} }} }}
        SE1 : my_mapdata(value: {{ geo_hash5: "{6}"  {17} }} ) {{ values {{ {18} }} }}
        SW1 : my_mapdata(value: {{ geo_hash5: "{7}"  {17} }} ) {{ values {{ {18} }} }}
        NW1 : my_mapdata(value: {{ geo_hash5: "{8}"  {17} }} ) {{ values {{ {18} }} }}

        N2 : my_mapdata(value:  {{ geo_hash5: "{9}"  {17} }} ) {{ values {{ {18} }} }}
        E2 : my_mapdata(value:  {{ geo_hash5: "{10}" {17} }} ) {{ values {{ {18} }} }}
        S2 : my_mapdata(value:  {{ geo_hash5: "{11}" {17} }} ) {{ values {{ {18} }} }}
        W2 : my_mapdata(value:  {{ geo_hash5: "{12}" {17} }} ) {{ values {{ {18} }} }}

        NE2 : my_mapdata(value: {{ geo_hash5: "{13}" {17} }} ) {{ values {{ {18} }} }}
        SE2 : my_mapdata(value: {{ geo_hash5: "{14}" {17} }} ) {{ values {{ {18} }} }}
        SW2 : my_mapdata(value: {{ geo_hash5: "{15}" {17} }} ) {{ values {{ {18} }} }}
        NW2 : my_mapdata(value: {{ geo_hash5: "{16}" {17} }} ) {{ values {{ {18} }} }}

      }}
   '''
      #
   l_queryString = gql(l_queryString.format(
      l_loca_C0,
      l_neighbors1['n'],
      l_neighbors1['e'],
      l_neighbors1['s'],
      l_neighbors1['w'],
      l_neighbors1['ne'],
      l_neighbors1['se'],
      l_neighbors1['sw'],
      l_neighbors1['nw'],
      l_N2,
      l_E2,
      l_S2,
      l_W2,
      l_NE2,
      l_SE2,
      l_SW2,
      l_NW2,
      l_textFilter,
      l_columnList ))

   #  Retry fetch loop
   #
   for _ in range(MY_MAXRETRIES):
      try:
         l_result = m_client.execute(l_queryString)
      except:
         #  If using the Astra free tier, we get the occasional time outs
         #
         time.sleep(0.25)
         print("NOTICE: Bump 2")
         continue
      else:
         break
   else:
      print("")
      print("")
      print("ERROR (7443): Failed to connect with K8ssandra/Cassandra instance.")
      print("")
      print("")
      exit(3)

   return l_result


#############################################################
#############################################################


#
#  And then running our Web site proper.
#
if __name__=='__main__':

   m_app.run(host = "localhost", port = int("8888"), debug=True)
