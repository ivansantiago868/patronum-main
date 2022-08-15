
#
# https://api.supermetrics.com/enterprise/v2/query/data/json?
# json={
#   "ds_id":"FBPD",
#   "ds_accounts":["ClaudiaLopezCL"],
#   "ds_user":"andresbeltc@gmail.com",
#   "date_range_type":"last_week_sun_sat",
#   "fields":["post_link","message","created_time","updated_time","type","from_id","from_name","story","likes_count","reactions_love","reactions_haha","reactions_wow","reactions_sad","reactions_thankful","reactions_angry","reactions_pride","reactions_count","comments_count","shares_count"],
#   "settings":{"report_type":"PagePosts"},
#   "max_rows":10000,
#   "api_key":"api_Uk4gd0rRxxCfH1UBnT4S9OlResQMyjX3doyn3_euJ8AmlPB6hJzudFsOT1S0b3dY6P0JASPLN4morqA7Dk3T9staSZ7cUTZrw7UN"
# }
#
#
import requests as requesthttp
import json
from Utilities.log import log_file


class SuperMetricsQueryClass():
    def __init__(self = None, ds_id = None, ds_user = None, ds_accounts = None, data_range_type = None, fields = None, settings = None, max_rows = None, url = None, api_key = None, log = None):
        try:
            self.ds_id = ds_id
            self.ds_user = ds_user
            self.ds_accounts = ds_accounts
            self.data_range_type = data_range_type
            self.fields = fields
            self.settings = settings
            self.max_rows = max_rows
            self.log = log
            self.api_key = api_key
            self.url = url
        except Exception as e:
            self.log.error(str(e),True,True)

    def startMultiQuery(self,dictClientsById):
        try:
            jsonQuery = json.dumps({
                    'ds_id': self.ds_id,
                    'ds_user': self.ds_user,
                    'ds_accounts' :  self.ds_accounts,
                    'date_range_type': self.data_range_type,
                    'fields': self.fields,
                    'settings': self.settings,
                    'max_rows': self.max_rows,
                    'api_key': self.api_key
                })
            request_query = requesthttp.get(self.url+str(jsonQuery))
            data = json.loads(request_query.text)
            if request_query.status_code == 200:
                if data['data'] != []:
                    return data
                elif  data['data'] == []:
                        self.log.warning('Code: '+str(request_query.status_code)+' not data found in time range of '+str(self.data_range_type) +'for the clients ' ,True)                 
            elif request_query.status_code >= 400:
                try:
                    if data['error']['description'].find('license limit'):
                            self.log.error('Code: '+ str(request_query.status_code) + ' Usuario '+str(self.ds_accounts)+str(data['error']['description']),True,True)
                            return 'limit'
                    else:
                        self.log.error('Code: '+ str(request_query.status_code) + ' Usuario '+str(self.ds_accounts)+str(data['error']['description']),True,True)

                except:
                    self.log.error('Code: '+ str(request_query.status_code)+ ' Usuario '+str(self.ds_accounts)+str(data['error']['message']),True,True)
        except Exception as e:
            self.log.error(str(e),True,True)
    def startQuery(self):
        try:
            jsonQuery = json.dumps({
                    'ds_id': self.ds_id,
                    'ds_user': self.ds_user,
                    'ds_accounts' :  self.ds_accounts,
                    'date_range_type': self.data_range_type,
                    'fields': self.fields,
                    'settings': self.settings,
                    'max_rows': self.max_rows,
                    'api_key': self.api_key            
                })
            request_query = requesthttp.get(self.url+str(jsonQuery))
            data = json.loads(request_query.text)
            if request_query.status_code == 200 and data['data'] != []:
                self.log.warning('Code: '+str(request_query.status_code)+' data found in time range of '+str(self.data_range_type) +' for the client '+str(self.ds_accounts) + '  Posts: '+str(len(data['data']) - 1) ,True)
                return data, self.ds_accounts
            elif request_query.status_code == 200 and data['data'] == []:
                self.log.warning('Code: '+str(request_query.status_code)+' not data found in time range of '+str(self.data_range_type) +' for the client '+str(self.ds_accounts) ,True)
                return 'NotFound',str(self.ds_accounts)
            elif request_query.status_code >= 400:
                    if data['error']['description'].find('license limit') > 0:
                        self.log.error('Code: '+ str(request_query.status_code) + ' Usuario '+str(self.ds_accounts)+str(data['error']['description']),True,True)
                        return 'limit',str(self.ds_accounts)
                    else:
                        try:
                            self.log.error('Code: '+ str(request_query.status_code) + ' Usuario '+str(self.ds_accounts)+str(data['error']['description']),True,True)
                            return 'NotFound',str(self.ds_accounts)
                        except:
                            self.log.error('Code: '+ str(request_query.status_code)+ ' Usuario '+str(self.ds_accounts)+str(data['error']['message']),True,True)
                            return 'NotFound',str(self.ds_accounts)
                    
        except Exception as e:
            self.log.error(str(e),True,True)
