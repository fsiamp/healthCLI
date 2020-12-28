from __future__ import unicode_literals

__title__ = 'Health Measurement and Notification CLI'
__version__ = '1.0'
__author__ = 'Fanis Siampos'
__license__ = 'Nokia'
__copyright__ = 'Copyright 2017 Fanis Siampos'

from ast import literal_eval
import sys
import re
import readline

import operator
import arrow
import datetime
import json
import requests
import random
import time
from arrow.parser import ParserError
from requests_oauthlib import OAuth1, OAuth1Session

print("Health Measurement and Notification CLI (version 1.0)")
print("Type \"help\" in order to view the available commands")

CONSUMER_KEY="8ee080dd8ffdb3e28dbfeb8c6d16fe94bf3de6b2e3220559b27506159"
CONSUMER_SECRET="e47d72df21787f26917103c6f20e63d0ffd721e8ee6b3e714389c40194d27"

file_name=random.randint(1000000,9999999)
export_data=[]

sleep_properties= ['id', 'timezone', 'date', 'model', 'wakeupduration', 'deepsleepduration', 'remsleepduration', 'lightsleepduration','durationtosleep','wakeupcount']
printed_sleep_entries= ['Sleep Id: ','Timezone: ','Date: ','Model: ','Wakeup Duration: ','Deep Sleep Duration: ','REM Sleep Duration: ','Light Sleep Duration: ','Sleep Duration: ','Wakeup Count: ']
activity_properties= ['distance', 'elevation', 'calories', 'totalcalories', 'steps', 'date', 'timezone', 'soft', 'moderate','intense']
printed_activity_entries= ['Distance: ', 'Elevation: ', 'Active Calories: ' ,'Total Calories: ' , 'Steps: ','Date: ' ,'Timezone: ' ,'Soft Activities Duration: ','Moderate Activities Duration: ','Intense Activities Duration: ']
body_properties= ['date', 'category', 'attrib', 'grpid', 'type', 'value', 'unit']
printed_body_entries= ['Date: ', 'Category: ', 'Way of Measure Attribution: ' ,'Measure Group ID: ' ,'Measure Type: ' ,'Measure Value: ' ,'Measure Unit: ']

notification_properties= ['callbackurl', 'comment', 'expires', 'grpid', 'type', 'value', 'unit']
printed_notification_entries= ['Callback URL: ', 'Comment: ', 'Expires: ']

workout_properties= ['category', 'timezone', 'attrib', 'model', 'date', 'metcumul', 'distance', 'elevation', 'hr_min', 'hr_average', 'calories', 'intensity', 'steps', 'hr_zone_0', 'hr_zone_1', 'hr_zone_2', 'hr_zone_3', 'effduration', 'hr_max', 'strokes', 'pool_length', 'pool_laps']
printed_workout_entries= ['Category: ','Timezone: ','Way of Measure Attribution: ','Model: ','Date: ','Cumulated Activity: ','Distance: ','Elevation: ','Minimum Heart Rate: ','Average Heart Rate: ','Calories: ','Intensity: ','Steps: ','Heart Rate Zone 0: ','Heart Rate Zone 1: ','Heart Rate Zone 2: ','Heart Rate Zone 3: ','Effective Duration: ','Maximum Heart Rate: ', 'Movements: ', 'Pool Size: ' ,'Swim Laps: ']

categories_workout = {'1': 'Walking', '2': 'Running', '3': 'Hiking', '4': 'Staking', '5': 'BMX', '6': 'Bicycling', '7': 'Swimming', '8': 'Surfing', '9': 'KiteSurfing', '10': 'Windsurfing', '11': 'Bodyboard', '12': 'Tennis', '13': 'TableTennis', '14': 'Squash', '15': 'Badminton', '16': 'LiftWeights', '17': 'Calisthenics', '18': 'Elliptical', '19': 'Pilates', '20': 'Basketball', '21': 'Soccer', '22': 'Football', '23': 'Rugby', '24': 'VolleyBall', '25': 'WaterPolo', '26': 'HorseRiding', '27': 'Golf', '28': 'Yoga', '29': 'Dancing', '30': 'Boxing', '31': 'Fencing', '32': 'Wrestling', '33': 'MartialArts', '34': 'Skiing', '35': 'SnowBoarding', '186': 'Base', '187': 'Rowing', '188': 'Zumba', '191': 'Baseball', '192': 'Handball', '193': 'Hockey', '194': 'IceHockey', '195': 'Climbing', '196': 'IceSkating'}


body_measuretypes = {'1': 'Weight', '4': 'Height', '5': 'Fat Free Mass', '6': 'Fat Ratio', '8': 'Fat Mass Weight', '9': 'Diastolic Blood Pressure', '10': 'Systolic Blood Pressure', '11': 'Heart Pulse', '12': 'Temperature', '54': 'SPO2', '71': 'Body Temperature', '73': 'Skin Temperature', '76': 'Muscle Mass', '77': 'Bone Mass', '91': 'Pulse Wave Velocity'}

sleep_states = {'0': 'Awake', '1': 'Light Sleep', '2': 'Deep Sleep', '3': 'REM Sleep'}
sleep_models = {'16': 'Pulse', '32': 'Aura'}


body_categories = {'1': 'Real Measurements', '2': 'User Objectives'}

workout_models = {'16': 'Activity Tracker', '32': 'Aura', '54': 'Pulse'}

status_codes = {'0': 'Operation was successful', '247': 'The userid provided is absent, or incorrect', '250': 'The provided userid and/or Oauth credentials do not match' , '283': "Token is invalid or doesn't exist", '286': 'No such subscription was found', '293': 'The callback URL is either absent or incorrect', '294':'No such subscription could be deleted', '304': 'The comment is either absent or incorrect', '305': 'Too many notifications are already set', '328': 'The user is deactivated', '342': 'The signature (using Oauth) is invalid', '343': "Wrong Notification Callback Url don't exist", '601':'Too Many Request', '2554':'Wrong action or wrong webservice', '2555':'An unknown error occurred', '2556':'Service is not defined'}

status_definitions = sys.modules[__name__]
status_definitions.code = ''


def print_error():
    if str(status_definitions.code) in status_codes:
       print(status_codes[str(status_definitions.code)])
    else:
       print("Invalid request was sent")
    return;
    
def print_invalid():
    print("Invalid command was entered")
    return;

class NokiaCredentials(object):
    def __init__(self, access_token=None, access_token_secret=None,
                 consumer_key=None, consumer_secret=None, user_id=None):
        self.access_token = access_token
        self.access_token_secret = access_token_secret
        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret
        self.user_id = user_id


class NokiaAuth(object):
    URL = 'https://developer.health.nokia.com/account'

    def __init__(self, consumer_key, consumer_secret):
        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret
        self.oauth_token = None
        self.oauth_secret = None

    def get_authorize_url(self, callback_uri=None):
        oauth = OAuth1Session(self.consumer_key,
                              client_secret=self.consumer_secret,
                              callback_uri=callback_uri)

        tokens = oauth.fetch_request_token('%s/request_token' % self.URL)
        self.oauth_token = tokens['oauth_token']
        self.oauth_secret = tokens['oauth_token_secret']

        return oauth.authorization_url('%s/authorize' % self.URL)

    def get_credentials(self, oauth_verifier):
        oauth = OAuth1Session(self.consumer_key,
                              client_secret=self.consumer_secret,
                              resource_owner_key=self.oauth_token,
                              resource_owner_secret=self.oauth_secret,
                              verifier=oauth_verifier)
        tokens = oauth.fetch_access_token('%s/access_token' % self.URL)
        return NokiaCredentials(
            access_token=tokens['oauth_token'],
            access_token_secret=tokens['oauth_token_secret'],
            consumer_key=self.consumer_key,
            consumer_secret=self.consumer_secret,
            user_id=tokens['userid'],
        )


def is_date(key):
    return 'date' in key


def is_date_class(val):
    return isinstance(val, (datetime.date, datetime.datetime, arrow.Arrow, ))


class NokiaApi(object):
    URL = 'https://api.health.nokia.com'

    def __init__(self, credentials):
        self.credentials = credentials
        self.oauth = OAuth1(credentials.consumer_key,
                            credentials.consumer_secret,
                            credentials.access_token,
                            credentials.access_token_secret,
                            signature_type='query')
        self.client = requests.Session()
        self.client.auth = self.oauth
        self.client.params.update({'userid': credentials.user_id})
        print("User ID: " + credentials.user_id)

    def request(self, service, action, params=None, method='GET',
                version=None):
        params = params or {}
        params['action'] = action
        for key, val in params.items():
            if is_date(key) and is_date_class(val):
                params[key] = arrow.get(val).timestamp
        url_parts = filter(None, [self.URL, version, service])
        message = self.client.request(method, '/'.join(url_parts), params=params)
        response = json.loads(message.content.decode())
        if response['status'] != 0:
            status_definitions.code = response['status']
            raise Exception("Error code %s" % status_definitions.code)
        return response.get('body', None)

    def get_user(self):
        return self.request('user', 'getbyuserid')

    def get_activities(self, start_date, end_date, **kwargs):
        params = {'startdateymd': start_date,'enddateymd': end_date}
        params.update(kwargs)
        activity_data = self.request('measure', 'getactivity', params, version='v2')
        return activity_data
    def get_workouts(self, start_date, end_date, **kwargs):
        params = {'startdateymd': start_date,'enddateymd': end_date}
        params.update(kwargs)
        workout_data = self.request('measure', 'getworkouts', params, version='v2')
        return workout_data
    def get_body_measures(self, start_date, end_date, **kwargs):
        params = {'startdate': start_date,'enddate': end_date}
        params.update(kwargs)
        body_data = self.request('measure', 'getmeas', params)
        return body_data
    def get_intraday(self, start_date, end_date, **kwargs):
        params = {'startdate': start_date,'enddate': end_date}
        params.update(kwargs)
        intraday_data = self.request('measure', 'getintradayactivity', params, version='v2')
        intraday_info = json.dumps(intraday_data)
        export_data.append(intraday_info)
        return intraday_info
    def get_sleep_measures(self, start_date, end_date, **kwargs):
        params = {'startdate': start_date,'enddate': end_date}
        params.update(kwargs)
        sleep_measure_data = self.request('sleep', 'get', params, version='v2')
        return sleep_measure_data
    def get_sleep_summary(self, start_date, end_date, **kwargs):
        params = {'startdate': start_date,'enddate': end_date}
        params.update(kwargs)
        sleep_summary_data = self.request('sleep', 'getsummary', params, version='v2')
        sleep_info = json.dumps(sleep_summary_data)
        return sleep_info
    def subscribe(self, callback_url, user_id, appli, comment, **kwargs):
        params = {'callbackurl': callback_url, 'comment': comment, 'appli': appli, 'userid': user_id}
        params.update(kwargs)
        self.request('notify', 'subscribe', params)
    def unsubscribe(self, callback_url, appli, **kwargs):
        params = {'callbackurl': callback_url, 'appli': appli}
        params.update(kwargs)
        revoke_data= self.request('notify', 'revoke', params)
        revoke_info = json.dumps(revoke_data)
        export_data.append(revoke_info)
        return revoke_data
    def get_notification_info(self, callback_url, appli, **kwargs):
        params = {'callbackurl': callback_url, 'appli': appli}
        params.update(kwargs)
        notification_data = self.request('notify', 'get', params)
        notification_info = json.dumps(notification_data)
        return notification_info

    def list_subscriptions(self, appli):
        subscriptions_data = self.request('notify', 'list', {'appli': appli})
        return subscriptions_data
        
    def replace_workout(self, printed_text, dict_value):
        if dict_value=="TableTennis":
            print(printed_text + "Table Tennis")
        elif dict_value=="WaterPolo":
            print(printed_text + "Water Polo")
        elif dict_value=="SnowBoarding":
            print(printed_text + "Snow Boarding")
        elif dict_value=="MartialArts":
            print(printed_text + "Martial Arts")
        elif dict_value=="LiftWeights":
            print(printed_text + "Lift Weights")
        elif dict_value=="IceHockey":
            print(printed_text + "Ice Hockey")
        elif dict_value=="Windsurfing":
            print(printed_text + "Wind Surfing")
        elif dict_value=="IceSkating":
            print(printed_text + "Ice Skating")
        else:
            print(printed_text + dict_value)  

while True:
   try:
    name= raw_input('# ')
    word_list = name.split()
    if word_list[0]=='authorize':
       try:
          if len(word_list) > 1:
             raise Exception
          auth = NokiaAuth(CONSUMER_KEY, CONSUMER_SECRET)
          authorize_url = auth.get_authorize_url()
          print("%s" % authorize_url)
       except:
          print_error()
    elif word_list[0]=='notify':
       try:
           if len(word_list) > 5 or len(word_list) < 5:
             raise Exception
           comment=re.findall(r'"([^"]*)"', name)
           measures = client.subscribe(word_list[1], word_list[2], word_list[3], comment)
           print("Request for a new notification was already sent")
       except:
           print_error()
    elif word_list[0]=='show':
       try:
           if len(word_list) > 3 or len(word_list) < 3:
             raise Exception
           notification_info = client.get_notification_info(word_list[1],word_list[2])
           childjson = json.dumps(notification_info)
           complete_text=json.loads(childjson)
           export_data.append(childjson)
           converted_info=json.loads(complete_text)
           index_looper = 0
           while (index_looper < 3):
                  value_grabbed=converted_info[notification_properties[index_looper]]
                  info_activity = json.dumps(value_grabbed)
                  noquote_text= info_activity.replace('"', '')
                  print(printed_notification_entries[index_looper] + noquote_text)
                  index_looper = index_looper + 1
           print("Measure Type: " + word_list[2])
       except:
          print_error()
    elif word_list[0]=='set':
       try:
           if len(word_list) > 2 or len(word_list) < 2:
             raise Exception
           creds = auth.get_credentials(word_list[1])
           client = NokiaApi(creds)
       except:
          print_invalid()
    elif word_list[0]=='list':
       try:
             if len(word_list) > 2 or len(word_list) < 2:
                raise Exception
             notifications = client.list_subscriptions(word_list[1])
             childjson = json.dumps(notifications)
             complete_text=json.loads(childjson)
             export_data.append(childjson)
             length= len(complete_text['profiles'])
             for i in range(0,length):
                 if i<length:
                    print("")
                 callback_attribute= complete_text["profiles"][i]["callbackurl"]
                 info_callback = json.dumps(callback_attribute)
                 noquote_text= info_callback.replace('"', '')
                 print("Callback URL: " + noquote_text)

                 comment_attribute= complete_text["profiles"][i]["comment"]
                 info_comment = json.dumps(comment_attribute)
                 noquote_text= info_comment.replace('"', '')
                 print("Comment: " + noquote_text)

                 if i==(length-1):
                    print("")
       except:
          print_error()
    elif word_list[0]=='body':
       try:
          if len(word_list) > 4 or len(word_list) < 3:
             raise Exception
          converted_startdate=int(time.mktime(datetime.datetime.strptime(word_list[1], "%Y-%m-%d").timetuple()))
          converted_enddate=int(time.mktime(datetime.datetime.strptime(word_list[2], "%Y-%m-%d").timetuple()))
          if len(word_list) == 3:
              body_measurements =client.get_body_measures(converted_startdate,converted_enddate)
          else:
              body_measurements =client.get_body_measures(converted_startdate,converted_enddate,offset=word_list[3])
          childjson = json.dumps(body_measurements)
          complete_text=json.loads(childjson)
          export_data.append(childjson)

          callback_attribute=complete_text["timezone"]
          info_notification = json.dumps(callback_attribute)
          noquote_text= info_notification.replace('"', '')
          print("Timezone: " + noquote_text)
          callback_attribute=complete_text["updatetime"]
          info_notification = json.dumps(callback_attribute)
          noquote_text= info_notification.replace('"', '')
          converted_updatetime=datetime.datetime.fromtimestamp(int(noquote_text)).strftime('%Y-%m-%d %H:%M:%S')
          print("Update Time: " + converted_updatetime)
          
          length= len(complete_text['measuregrps'])
          for i in range(0,length):
              if i<length:
                 print("")
              for j in range(0,4):
                  if (body_properties[j] in complete_text['measuregrps'][i]):
                      if (body_properties[j]=='date'):
                           json_value= str(complete_text['measuregrps'][i]["date"])
                           converted_responsedate=datetime.datetime.fromtimestamp(int(json_value)).strftime('%Y-%m-%d')
                           print(printed_body_entries[j] + converted_responsedate)
                      elif (body_properties[j]=='category'):
                           json_value= str(complete_text['measuregrps'][i]["category"])  
                           dict_value= body_categories[json_value]
                           print(printed_body_entries[j] + dict_value)                    
                      else:
                           body_attribute=complete_text['measuregrps'][i][body_properties[j]]
                           info_body = json.dumps(body_attribute)
                           noquote_text= info_body.replace('"', '')
                           print(printed_body_entries[j] + noquote_text)
              group_measurement=complete_text['measuregrps'][i]['measures']
              for k in range(4,7):
                  if (body_properties[k] in group_measurement[0]):
                      if (body_properties[k]=='type'):
                           json_value= str(group_measurement[0]["type"])
                           dict_value= body_measuretypes[json_value]
                           print(printed_body_entries[k] + dict_value)
                      else:
                          set_text=group_measurement[0][body_properties[k]]
                          measure_bodydata = json.dumps(set_text)
                          body_text= measure_bodydata.replace('"', '')
                          print(printed_body_entries[k] + body_text)
              if i==(length-1):
                 print("")
       except:
          print_error()
    elif word_list[0]=='sleep':
       try:
          if len(word_list) > 4 or len(word_list) < 4:
             raise Exception
          if word_list[1]=='measures':
             try:
                converted_startdate=int(time.mktime(datetime.datetime.strptime(word_list[2], "%Y-%m-%d").timetuple()))
                converted_enddate=int(time.mktime(datetime.datetime.strptime(word_list[3], "%Y-%m-%d").timetuple()))
                sleep_measures = client.get_sleep_measures(converted_startdate,converted_enddate)
                childjson = json.dumps(sleep_measures)

                complete_text=json.loads(childjson)
                backslash_text=childjson.replace("\\", "")
                export_data.append(backslash_text)
                length= len(complete_text['series'])

                state_attribute=complete_text["model"]
                info_model = json.dumps(state_attribute)
                noquote_text= info_model.replace('"', '')
                replaced_model=sleep_models[noquote_text]
                print("Model: " + replaced_model)

                for i in range(0,length):
                    if i<length:
                       print("")
                    
                    start_attribute=complete_text["series"][i]["startdate"]
                    info_sleepmeasure = json.dumps(start_attribute)
                    noquote_text= info_sleepmeasure.replace('"', '')  
                    converted_startdate=datetime.datetime.fromtimestamp(int(noquote_text)).strftime('%Y-%m-%d %H:%M:%S')

                    print("Start Time: " + converted_startdate)
                    end_attribute=complete_text["series"][i]["enddate"]
                    info_endmeasure = json.dumps(end_attribute)
                    noquote_text= info_endmeasure.replace('"', '')
                    converted_enddate=datetime.datetime.fromtimestamp(int(noquote_text)).strftime('%Y-%m-%d %H:%M:%S')
                    print("End Time: " + converted_enddate)

                    state_attribute=complete_text["series"][i]["state"]
                    info_state = json.dumps(state_attribute)
                    noquote_text= info_state.replace('"', '')
                    replaced_state=sleep_states[noquote_text]
                    print("State: " + replaced_state)
                    
                    if i==(length-1):
                       print("")
             except:
                print_error()
          elif word_list[1]=='summary':
             try:
                converted_startdate=int(time.mktime(datetime.datetime.strptime(word_list[2], "%Y-%m-%d").timetuple()))
                converted_enddate=int(time.mktime(datetime.datetime.strptime(word_list[3], "%Y-%m-%d").timetuple()))

                sleep_summary = client.get_sleep_summary(converted_startdate,converted_enddate)
                childjson = json.dumps(sleep_summary)
    
                complete_text=json.loads(childjson)
                backslash_json=childjson.replace("\\", "")
                export_data.append(backslash_json)

                converted_info=json.loads(complete_text)
                length= len(converted_info['series'])
                for i in range(0,length):
                    if i<length:
                       print("")
                    for j in range(0,4):
                        if (sleep_properties[j] in converted_info["series"][i]):
                           if (sleep_properties[j]=='model'):
                              json_value= str(converted_info["series"][i]["model"])
                              dict_value= sleep_models[json_value]
                              print(printed_sleep_entries[j] + dict_value)
                           else:
                              callback_attribute=converted_info["series"][i][sleep_properties[j]]
                              info_summary = json.dumps(callback_attribute)
                              noquote_text= info_summary.replace('"', '')
                              print(printed_sleep_entries[j] + noquote_text)
                    for f in range(4,10):
                        if (sleep_properties[f] in converted_info["series"][i]['data']):
                           callback_attribute=converted_info["series"][i]['data'][sleep_properties[f]]
                           info_summary = json.dumps(callback_attribute)
                           noquote_text= info_summary.replace('"', '')
                           print(printed_sleep_entries[f] + noquote_text)
                    if i==(length-1):
                       print("")
             except:
                print_error()
          else:
             print_invalid()
       except:
          print_error() 
    elif word_list[0]=='activity':
       try:
          if len(word_list) > 4 or len(word_list) < 3:
             raise Exception
          if len(word_list) == 3:
              activities = client.get_activities(word_list[1],word_list[2])
          else:
              activities = client.get_activities(word_list[1],word_list[2],offset=word_list[3])
          childjson = json.dumps(activities)
          complete_text=json.loads(childjson)
          export_data.append(childjson)
          length= len(complete_text['activities'])
          for i in range(0,length):
              if i<length:
                 print("")
              for j in range(0,10):
                  if (activity_properties[j] in complete_text["activities"][i]):
                     value_grabbed=complete_text["activities"][i][activity_properties[j]]
                     info_activity = json.dumps(value_grabbed)
                     noquote_text= info_activity.replace('"', '')
                     print(printed_activity_entries[j] + noquote_text)
              if i==(length-1):
                 print("")
       except:
          print_error()
    elif word_list[0]=='export':
       try:
          if len(word_list) > 2 or len(word_list)< 2:
             raise Exception
          if word_list[1]=='file':
             json.dumps(export_data)
             experimental = open("log/"+ str(file_name) + ".txt", "w+")
             for item in export_data:
               experimental.write("%s\n\n" % item)
             experimental.close()
             print("Measurements and notification data were saved at log/" + str(file_name) + ".txt")
          elif word_list[1]=='local':
             json.dumps(export_data)
             print("")
             for item in export_data:
               print("%s\n" % item)
          else:
             print_invalid()
       except:
          print_error()        
    elif word_list[0]=='intraday':
      try:
          if len(word_list) > 2 or len(word_list) < 2:
             raise Exception
          activities = client.get_activities(word_list[1],word_list[1])
          intraday_part = json.dumps(activities)
          intraday_content=json.loads(intraday_part)
          export_data.append(intraday_part)
          length= len(intraday_content['activities'])
          for i in range(0,length):
              if i<length:
                 print("")
              for j in range(0,10):
                  if (activity_properties[j] in intraday_content["activities"][i]):
                     value_intraday=intraday_content["activities"][i][activity_properties[j]]
                     info_activity = json.dumps(value_intraday)
                     intraday_text= info_activity.replace('"', '')
                     print(printed_activity_entries[j] + intraday_text)
              if i==(length-1):
                 print("")
      except:
          print_error() 
    elif word_list[0]=='workouts':
       try:
          if len(word_list) > 4 or len(word_list) < 3:
             raise Exception
          if len(word_list) == 3:
              workouts = client.get_workouts(word_list[1],word_list[2])
          else:
              workouts = client.get_workouts(word_list[1],word_list[2],offset=word_list[3])
          childjson = json.dumps(workouts)
          complete_text=json.loads(childjson)
          export_data.append(childjson)
          length= len(complete_text['series'])
          for i in range(0,length):
              if i<length:
                 print("")
              for p in range(0,5):
                  if (workout_properties[p] in complete_text["series"][i]):
                     if (workout_properties[p]=='category'):
                        json_value= str(complete_text["series"][i]["category"])
                        dict_value= categories_workout[json_value]
                        client.replace_workout(printed_workout_entries[p],dict_value)
                     #elif (workout_properties[p]=='model'):
                     #   json_value= str(complete_text["series"][i]["model"])
                     #   dict_value= workout_models[json_value]
                     #   print(printed_workout_entries[p] + dict_value)
                     else:
                        workout_value=complete_text["series"][i][workout_properties[p]]
                        info_workout = json.dumps(workout_value)
                        noquote_workout= info_workout.replace('"', '')
                        print(printed_workout_entries[p] + noquote_workout)
              for b in range(5,22):
                  if (workout_properties[b] in complete_text["series"][i]["data"]):
                     workout_data=complete_text["series"][i]["data"][workout_properties[b]]
                     info_specific = json.dumps(workout_data)
                     noquote_workout= info_specific.replace('"', '')
                     print(printed_workout_entries[b] + noquote_workout)
              if i==(length-1):
                 print("")
       except:
          print_error() 
    elif word_list[0]=='search':
       try:
          if len(word_list) > 5 or len(word_list) < 4:
             raise Exception
          if len(word_list) == 4:
              workouts = client.get_workouts(word_list[2],word_list[3])
          else:
              workouts = client.get_workouts(word_list[2],word_list[3],offset=word_list[4])
          childjson = json.dumps(workouts)
          complete_text=json.loads(childjson)
          export_data.append(childjson)
          length= len(complete_text['series'])
          for i in range(0,length):

              json_value= str(complete_text["series"][i]["category"])
              dict_value= categories_workout[json_value]
              if (dict_value.lower()==word_list[1].lower()):
                  if i<length:
                     print("")
                  for p in range(0,5):
                     if (workout_properties[p] in complete_text["series"][i]):
                        if (workout_properties[p]=='category'):
                           json_value= str(complete_text["series"][i]["category"])
                           dict_value= categories_workout[json_value]
                           client.replace_workout(printed_workout_entries[p],dict_value)
                        #elif (workout_properties[p]=='model'):
                        #   json_value= str(complete_text["series"][i]["model"])
                        #   dict_value= workout_models[json_value]
                        #   print(printed_workout_entries[p] + dict_value)
                        else:
                           workout_value=complete_text["series"][i][workout_properties[p]]
                           info_workout = json.dumps(workout_value)
                           noquote_workout= info_workout.replace('"', '')
                           print(printed_workout_entries[p] + noquote_workout)
                  for b in range(5,22):
                     if (workout_properties[b] in complete_text["series"][i]["data"]):
                        workout_data=complete_text["series"][i]["data"][workout_properties[b]]
                        info_specific = json.dumps(workout_data)
                        noquote_workout= info_specific.replace('"', '')
                        print(printed_workout_entries[b] + noquote_workout)
              if i==(length-1):
                 print("")
       except:
          print_error()
    elif word_list[0]=='visualize':
       try:
          if len(word_list) > 5 or len(word_list) < 4:
             raise Exception
          if len(word_list) == 4:
              workouts = client.get_workouts(word_list[2],word_list[3])
          else:
              workouts = client.get_workouts(word_list[2],word_list[3],offset=word_list[4])
          childjson = json.dumps(workouts)
          complete_text=json.loads(childjson)
          export_data.append(childjson)
          length= len(complete_text['series'])
          if word_list[1]=='steps':
             for i in range(0,length):
                 if i<length:
                           print("")
                           date_value= str(complete_text["series"][i]["date"])
                           step_data=complete_text["series"][i]["data"]["steps"]
                           info_specific = json.dumps(step_data)
                           convert_date = json.dumps(date_value)
                           noquote_workout= int(info_specific.replace('"', ''))
                           noquote_date= convert_date.replace('"', '')
                           if (noquote_workout > 12000):
                               print(noquote_date + " " + 13*("*"))
                           elif (noquote_workout <= 12000 and noquote_workout > 11000):
                               print(noquote_date + " " + 12*("*"))
                           elif (noquote_workout <= 11000 and noquote_workout > 10000):
                               print(noquote_date + " " + 11*("*"))
                           elif (noquote_workout <= 10000 and noquote_workout > 9000):
                               print(noquote_date + " " + 10*("*"))
                           elif (noquote_workout <= 9000 and noquote_workout > 8000):
                               print(noquote_date + " " + 9*("*"))
                           elif (noquote_workout <= 8000 and noquote_workout > 7000):
                               print(noquote_date + " " + 8*("*"))    
                           elif (noquote_workout <= 7000 and noquote_workout > 6000):
                               print(noquote_date + " " + 7*("*"))
                           elif (noquote_workout <= 6000 and noquote_workout > 5000):
                               print(noquote_date + " " + 6*("*"))      
                           elif (noquote_workout <= 5000 and noquote_workout > 4000):
                               print(noquote_date + " " + 5*("*"))
                           elif (noquote_workout <= 4000 and noquote_workout > 3000):
                               print(noquote_date + " " + 4*("*"))
                           elif (noquote_workout <= 3000 and noquote_workout > 2000):
                               print(noquote_date + " " + 3*("*"))
                           elif (noquote_workout <= 2000 and noquote_workout > 1000):
                               print(noquote_date + " " + 2*("*"))
                           else:
                               print(noquote_date + " " + 1*("*"))                            
                 if i==(length-1):
                    print("")
          elif word_list[1]=='calories':
             for i in range(0,length):
                 if i<length:
                           print("")
                           date_value= str(complete_text["series"][i]["date"])
                           calories_data=complete_text["series"][i]["data"]["calories"]
                           info_specific = json.dumps(calories_data)
                           convert_date = json.dumps(date_value)
                           noquote_workout= int(info_specific.replace('"', ''))
                           noquote_date= convert_date.replace('"', '')
                           if (noquote_workout > 600):
                               print(noquote_date + " " + 13*("*"))
                           elif (noquote_workout <= 550 and noquote_workout > 500):
                               print(noquote_date + " " + 12*("*"))
                           elif (noquote_workout <= 500 and noquote_workout > 450):
                               print(noquote_date + " " + 11*("*"))
                           elif (noquote_workout <= 450 and noquote_workout > 400):
                               print(noquote_date + " " + 10*("*"))
                           elif (noquote_workout <= 400 and noquote_workout > 350):
                               print(noquote_date + " " + 9*("*"))
                           elif (noquote_workout <= 350 and noquote_workout > 300):
                               print(noquote_date + " " + 8*("*"))    
                           elif (noquote_workout <= 300 and noquote_workout > 250):
                               print(noquote_date + " " + 7*("*"))
                           elif (noquote_workout <= 250 and noquote_workout > 200):
                               print(noquote_date + " " + 6*("*"))      
                           elif (noquote_workout <= 200 and noquote_workout > 150):
                               print(noquote_date + " " + 5*("*"))
                           elif (noquote_workout <= 150 and noquote_workout > 100):
                               print(noquote_date + " " + 4*("*"))
                           elif (noquote_workout <= 100 and noquote_workout > 50):
                               print(noquote_date + " " + 3*("*"))
                           elif (noquote_workout <= 50 and noquote_workout > 10):
                               print(noquote_date + " " + 2*("*"))
                           else:
                               print(noquote_date + " " + 1*("*"))                            
                 if i==(length-1):
                    print("")
          elif word_list[1]=='intensity':
             for i in range(0,length):
                 if i<length:
                           print("")
                           date_value= str(complete_text["series"][i]["date"])
                           intensity_data=complete_text["series"][i]["data"]["intensity"]
                           info_specific = json.dumps(intensity_data)
                           convert_date = json.dumps(date_value)
                           noquote_workout= int(info_specific.replace('"', ''))
                           noquote_date= convert_date.replace('"', '')
                           if (noquote_workout > 100):
                               print(noquote_date + " " + 11*("*"))
                           elif (noquote_workout <= 100 and noquote_workout > 90):
                               print(noquote_date + " " + 10*("*"))
                           elif (noquote_workout <= 90 and noquote_workout > 80):
                               print(noquote_date + " " + 9*("*"))
                           elif (noquote_workout <= 80 and noquote_workout > 70):
                               print(noquote_date + " " + 8*("*"))    
                           elif (noquote_workout <= 70 and noquote_workout > 60):
                               print(noquote_date + " " + 7*("*"))
                           elif (noquote_workout <= 60 and noquote_workout > 50):
                               print(noquote_date + " " + 6*("*"))      
                           elif (noquote_workout <= 50 and noquote_workout > 40):
                               print(noquote_date + " " + 5*("*"))
                           elif (noquote_workout <= 40 and noquote_workout > 30):
                               print(noquote_date + " " + 4*("*"))
                           elif (noquote_workout <= 30 and noquote_workout > 20):
                               print(noquote_date + " " + 3*("*"))
                           elif (noquote_workout <= 20 and noquote_workout > 10):
                               print(noquote_date + " " + 2*("*"))
                           else:
                               print(noquote_date + " " + 1*("*"))                            
                 if i==(length-1):
                    print("")
          else:
             print_invalid()  
       except:
          print_error()
    elif word_list[0]=='revoke':
       try:
           if len(word_list) > 3 or len(word_list) < 3:
             raise Exception
           revoke_output = client.unsubscribe(word_list[1],word_list[2])
           print("Revoke action for " + word_list[1] + "was executed")
       except:
          print_error() 
    elif word_list[0]=='help':
      try:
       if len(word_list) > 1:
           raise Exception
       print("\nAvailable Commands:\n\nauthorize\nset <oauth_verifier>\nlist <measure_type>\nworkouts <start_date> <end_date> <offset>\nintraday <date>\nshow <callback_url> <measure_type>\nnotify <callback_url> <user_id> <measure_type> <comment>\nexport <file|local>\nsleep <measures> <start_date> <end_date>\nsleep summary <start_date> <end_date>\nbody <start_date> <end_date> <offset>\nactivity <start_date> <end_date> <offset>\nsearch <workout_name> <start_date> <end_date> <offset>\nvisualize <workout_metadata> <start_date> <end_date> <offset>\nrevoke <callback_url> <measure_type>\nhelp\nexit\n\nNotes:\n\n* Date format should be Y-M-d (e.g 2017-07-19)\n* Measures type values can be 1,4,16 or 44.\n\n1 : Weight\n4 : Heart Rate, Diastolic pressure, Systolic pressure, Oxymetry\n16 : Activity Measure ( steps, calories, distance, elevation)\n44 : Sleep\n\n* Comments in notify command should be enclosed in double quotes\n* Offset value is optional\n* Workout metadata value in visualize command can be 'calories', 'steps' or 'intensity'\n\nExamples:\n\n- authorize\n- set LE7cUteGGRmQEsIUC0s\n- activity 2017-09-15 2017-09-20\n- workouts 2017-09-15 2017-10-07\n- list 44\n- notify http://nokia.com 13584569 16 \"test one\"\n- revoke http://nokia.com 16\n- sleep summary 2017-06-24 2017-10-04\n- export local\n- sleep measures 2017-06-24 2017-10-04\n- show http://nokia.com 16\n- body 2017-05-15 2017-10-07\n- search walking 2017-05-01 2017-10-07\n- intraday 2017-09-07\n- visualize steps 2017-06-15 2017-10-20\n")
      except:
         print_invalid()
    elif word_list[0]=='exit' and len(word_list) < 2:
         sys.exit()
    else:
       print_invalid()
   except Exception:
       pass