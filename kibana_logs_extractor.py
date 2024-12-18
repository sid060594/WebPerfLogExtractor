"""
Created on Fri May 28 09:34:13 2020
@author: Siddharth Singh
"""
import datetime as dt
import getpass
import os
import time as t
from tkinter import messagebox

import xlsxwriter
from elasticsearch import Elasticsearch

from mail_sender import MailSender

"""
Description: 
	|  This class fetches kibana logs through elastic search api. Apply filter accordingly.
.. note:: 
	|  str_choose_env => ["dev", "staging", "prod", "internal_dev", "internal_staging", "internal_prod"]
	|  str_db_type => ["onprem", "cloud", "cloud_china", "cloud_sg", "onprem_old"]
	|  str_cs_browser_name => ["Chrome", "IE", "Firefox", "Chrome Mobile", "HeadlessChrome", "Chrome Mobile WebView", "Mobile Safari"]
	|  bln_meet_threshold => [True, False, None]
	|  
	|  
"""


class KibanaLogsExtractor:

    def __init__(self):
        self.current_timestamp = dt.datetime.fromtimestamp(t.time()).strftime('%m-%d-%Y_%H-%M_%p_EST')
        self.bln_flag = True
        self.mail_sender = MailSender()
        self.project_dir = os.path.dirname(os.path.abspath(__file__))
        self.str_choose_env = self.str_db_type = self.str_service_route_path = self.str_cache_type = self.str_cs_browser_name = self.int_fetch_max_rows = self.str_relative_time_from = self.str_relative_time_to = self.excel_file_name = self.sheet_name = self.file_name = self.elastic_client = self.int_cell_threshold = self.int_max_threshold = self.int_min_threshold = self.dict_query_body = self.str_application_host = self.elastic_client = self.str_SRP_condition = self.str_exclude_condition = self.mail_to = ""
        self.bln_meet_threshold = None
        self.dict_hosts = dict(dev=fr"http://avlogesd-query.midevcld.spglobal.com:9200/",
                               staging=fr"http://avlogess-query.mistage.int:9200/",
                               prod=fr"http://avlogesp-query.prod.mktint.global:9200/")

        self.str_kingcharles_srp = "kingcharles=1"
        self.str_exclude_eeegads_params = "eeegads=1"

        self.list_sort_filter_condition = [dict(Timestamp=dict(order="desc"))]

        self.dict_application_hosts = dict(dev_onprem=fr"platform.midev.spglobal.com",
                                           dev_cloud=fr"platform.midevcld.spglobal.com",
                                           dev_cloud_china=fr"platform.midevcld.spglobal.cn",
                                           dev_onprem_old=fr"www.snldev.int",
                                           dev_blue_stack=fr"platform-1-av.midevcld.spglobal.com",
                                           dev_green_stack=fr"platform-3-av.midevcld.spglobal.com",
                                           dev_internal=fr"platform.internaldev.spglobal.com",
                                           staging_onprem=fr"platform.mistage.spglobal.com",
                                           staging_cloud=fr"platform.mistagecld.spglobal.com",
                                           staging_cloud_china=fr"platform.spgistg.spglobal.cn",
                                           staging_cloud_sg=fr"platform-as.mistagecld.spglobal.com",
                                           staging_onprem_old=fr"www.snlnet.com",
                                           staging_av_stack=fr"platform-av.mistagecld.spglobal.com",
                                           staging_internal=fr"platform.internalstg.spglobal.com",
                                           prod_onprem=fr"platform.mi.spglobal.com",
                                           prod_cloud=fr"platform.marketintelligence.spglobal.com",
                                           prod_cloud_china=fr"platform.mi.spglobal.cn",
                                           prod_cloud_sg=fr"platform-as.marketintelligence.spglobal.com",
                                           prod_onprem_old=fr"www.snl.com",
                                           prod_stack_1=fr"platform-1-av.marketintelligence.spglobal.com",
                                           prod_stack_2=fr"platform-2-av.marketintelligence.spglobal.com",
                                           prod_sg_stack_1=fr"platform-1-as.marketintelligence.spglobal.com",
                                           prod_sg_stack_2=fr"platform-2-as.marketintelligence.spglobal.com",
                                           prod_internal=fr"platform.internal.spglobal.com"
                                           )

    def assign_query_fields(self, plist_labels, plist_args, pdict_query_fields):
        try:
            self.str_service_route_path = pdict_query_fields['Service.route.params']

            self.str_choose_env = pdict_query_fields['Environment']
            self.str_db_type = pdict_query_fields['DB Type']
            self.str_cache_type = pdict_query_fields['Cache Type']
            self.str_cs_browser_name = pdict_query_fields['Browser']
            self.int_fetch_max_rows = pdict_query_fields['Maximum Rows to Fetch']

            self.bln_meet_threshold = None if pdict_query_fields['Fetch'] == "All records" else True if \
                pdict_query_fields['Fetch'] == "Only threshold ones" else False
            self.str_relative_time_from = pdict_query_fields['Start.date']
            self.str_relative_time_to = pdict_query_fields['End.date']
            self.mail_to = pdict_query_fields.get('Mail.to', None) if len(plist_args) > (
                        len(plist_labels) - 1) else None

            self.excel_file_name = fr'{self.str_cs_browser_name.lower()}_{self.str_choose_env.lower()}_{self.str_db_type.lower()}_{self.str_cache_type.lower()}_[{self.str_service_route_path.replace("/", "_").lower()}]_logs_{self.current_timestamp}.xlsx'
            self.sheet_name = f'{self.str_cs_browser_name.lower()}_{self.str_cache_type.lower()}_cache'
            self.file_name = self.project_dir + '\\' + self.excel_file_name

            self.elastic_client = Elasticsearch(hosts=[self.dict_hosts.get(self.str_choose_env, None)])

            if self.bln_meet_threshold is None:
                self.int_min_threshold = self.int_max_threshold = None
            elif self.bln_meet_threshold:
                self.int_min_threshold = 200
            else:
                self.int_min_threshold = 4000

            if self.str_cache_type.lower() == "cold":
                self.str_SRP_condition = "must"
                self.str_exclude_condition = "perfType=perfwarm"
                if self.bln_meet_threshold is None: self.int_cell_threshold = 4000
            else:
                self.str_SRP_condition = "must_not"
                self.str_exclude_condition = "perfType=perfcold"
                if self.bln_meet_threshold is None: self.int_cell_threshold = 2000

            if self.bln_meet_threshold is None:
                self.int_min_threshold = self.int_max_threshold = None
            elif self.bln_meet_threshold:
                self.int_max_threshold = self.int_cell_threshold = 2000
            else:
                self.int_cell_threshold = self.int_min_threshold
                self.int_max_threshold = self.int_min_threshold * 100

            if self.str_choose_env.lower() in [*self.dict_hosts] and self.str_db_type.lower() in list(
                    pdict_query_fields.values()):
                if str(self.str_choose_env.lower() + "_" + self.str_db_type.lower()) in [*self.dict_application_hosts]:
                    self.str_application_host = self.dict_application_hosts.get(
                        f"{self.str_choose_env.lower()}_{self.str_db_type.lower()}",
                        None)
                    self.bln_flag = True
                else:
                    messagebox.showinfo("Re-enter the fields",
                                        f"Fetching Performance Stats on {self.str_choose_env.lower()}_{self.str_db_type.lower()} is not applicable !!")
                    self.bln_flag = False
            else:
                messagebox.showinfo('Failure',
                                    f'Incorrect str_choose_env ({self.str_choose_env!r}) and str_db_type ({self.str_db_type!r}) passed during input !!')

            self.dict_query_body = {
                "size": self.int_fetch_max_rows,
                "_source": ["@timestamp", "Duration", "Id", "Url", "Name", "browser"],
                "query": {
                    "bool": {
                        "must": [
                            {"match_phrase": {"Browser.name": self.str_cs_browser_name}},
                            {"match_phrase": {"Service.Route.Path": self.str_service_route_path}},
                            {"match_phrase": {"Application.LogType": "jspageview"}},
                            {"match_phrase": {"Application.Host": self.str_application_host}},
                            {"range": {
                                "@timestamp": {"gte": self.str_relative_time_from, "lte": self.str_relative_time_to}}},
                            {"bool": {
                                self.str_SRP_condition: [
                                    {"match_phrase": {"Service.Route.Params": self.str_kingcharles_srp}}]}},
                            {"range": {"Duration": {"gte": self.int_min_threshold, "lte": self.int_max_threshold}}},
                            {"bool": {
                                "must_not": [
                                    {"match_phrase": {"Service.Route.Params": self.str_exclude_eeegads_params}},
                                    {"match_phrase": {"Service.Route.Params": self.str_exclude_condition}}
                                ]}}
                        ]
                    }
                }
                , "sort": self.list_sort_filter_condition
            }
        except Exception as e:
            messagebox.showinfo('Failure', f'Exception occurred -> {e}!!')

    def fetch_perf_stats__and__store_in_excel(self, pobj_elastic_client, pstr_kibana_query, pstr_workbook,
                                              pstr_worksheet):

        result = pobj_elastic_client.search(index='mi-services-perf-*', body=pstr_kibana_query)

        list_kibana_response = result["hits"]["hits"]

        try:
            if os.path.isfile(pstr_workbook):
                print(f'Excel file already present at root dir: {pstr_workbook} !!')
            else:
                # Create a workbook and add a worksheet.
                workbook = xlsxwriter.Workbook(pstr_workbook)
                worksheet = workbook.add_worksheet(pstr_worksheet)

                column_names_list = (
                    ['Timestamp', 'Duration', 'Operation.Id', 'URL', 'Service.Route.Path']
                )

                # Start from the first cell. Rows and columns are zero indexed.
                row = 0
                col = 0

                # bold format to highlight cells
                header_cell_format = workbook.add_format({'bold': True, 'font_color': 'black', 'bg_color': '#a9a9a9'})
                passed_cell_format = workbook.add_format({'bold': True, 'font_color': 'black', 'bg_color': '#90ee90'})
                failed_cell_format = workbook.add_format({'bold': True, 'font_color': 'black', 'bg_color': '#cd5c5c'})
                average_cal_cell_format = workbook.add_format(
                    {'bold': True, 'font_color': 'black', 'bg_color': '#a9a9a9'})

                # Iterate over the data and write it out row by row.
                for names in column_names_list:
                    worksheet.write(row, col, names, header_cell_format)
                    col += 1

                # writing in sheet
                column = 0
                count = 1

                for dic in list_kibana_response:
                    for k, v in dic.items():
                        if k.lower() == '_source':
                            for k_new, v_new in v.items():
                                try:
                                    v_new = dt.datetime.strptime(v_new, "%Y-%m-%dT%H:%M:%S.%fZ").strftime(
                                        "%A_%B_%d_%Y_%H:%M_%p_UTC")
                                except:
                                    pass
                                worksheet.write(row + 1, column + count - 1, v_new)
                                count += 1

                    row += 1
                    count = 1

                worksheet.set_column(0, 0, len(max(column_names_list, key=len)) + 17)
                worksheet.set_column(2, 2, len(max(column_names_list, key=len)) + 17)
                worksheet.set_column(3, 4, len(max(column_names_list, key=len)))

                # Avg duration calculation
                if not row <= 1:
                    duration_average_time = '=ROUND(AVERAGE(B2:B' + str(row + 1) + ')/1000, 2)'
                    worksheet.write(row + 1, column, 'Average (secs)', header_cell_format)

                    worksheet.write(row + 1, column + 1, duration_average_time, average_cal_cell_format)

                worksheet.conditional_format(f'B2:B{str(row + 1)}',
                                             {'type': 'cell', 'criteria': '>=', 'value': self.int_cell_threshold,
                                              'format': failed_cell_format})
                worksheet.conditional_format(f'B2:B{str(row + 1)}',
                                             {'type': 'cell', 'criteria': '<', 'value': self.int_cell_threshold,
                                              'format': passed_cell_format})

                # chart object
                chart = workbook.add_chart({'type': 'column'})

                #  series
                chart.add_series({
                    'name': f'={self.sheet_name}!$B$1',
                    'categories': f'={self.sheet_name}!$A$2:$A${row + 1}',
                    'values': f'={self.sheet_name}!$B$2:$B${row + 1}'
                })

                # y-axis label
                chart.set_y_axis({'name': f'Duration (ms)',
                                  'name_font': {'size': 13}})

                # x-axis label
                chart.set_x_axis({'name': f'Timestamp ({self.str_cs_browser_name})',
                                  'name_font': {'size': 13},
                                  'reverse': True})

                # add chart to the worksheet
                worksheet.insert_chart(f'I2', chart, {'x_scale': 2, 'y_scale': 1})

                workbook.close()
        except Exception as e:
            messagebox.showinfo('Failure', f'Exception occurred -> {e}!!')

    def fetch_logs(self, plist_labels, plist_args, pdict_query_fields):
        try:
            self.current_timestamp = dt.datetime.fromtimestamp(t.time()).strftime('%m-%d-%Y_%H-%M_%p_EST')
            self.assign_query_fields(plist_labels, plist_args, pdict_query_fields)
            recipient = f'{getpass.getuser().replace("_", ".")}@spglobal.com' if self.mail_to is None else self.mail_to
            if self.bln_flag:
                self.fetch_perf_stats__and__store_in_excel(self.elastic_client, self.dict_query_body,
                                                           self.excel_file_name,
                                                           self.sheet_name)

                self.mail_sender.send_mail([self.file_name],
                                           pstr_mail_body=f'<p><span style="font-size: 14px; font-family: ;">Kibana Elastic Search Report:</span></p><ul><li><span style="font-family: Courier New, courier;"><span style="font-size: 13px;">Timeframe.from:&nbsp;</span><span style="font-size: 16px;"><span style="background-color: rgb(153, 204, 255); font-size: 13px;"><strong>{self.str_relative_time_from}</strong></span></span></span></li><li><span style="font-family: Courier New, courier;"><span style="font-size: 13px;">Timeframe.to:&nbsp;</span><span style="font-size: 16px;"><span style="background-color: rgb(153, 204, 255); font-size: 13px;"><strong>{self.str_relative_time_to}</strong></span></span></span></li><li><span style="font-family: Courier New, courier;"><span style="font-size: 13px;">Browser.name: <span style="background-color: #99ccff;"><strong>{self.str_cs_browser_name}</strong></span></span></span></li><li><span style="font-size: 13px;"><span style="font-family: Courier New, courier;">Cache.type: <span style="background-color: #99ccff;"><strong>{self.str_cache_type}</strong></span></span></span></li><li><span style="font-size: 13px;"><span style="font-family: Courier New, courier;">Max.records.fetched: <span style="background-color: #99ccff;"><strong>{self.int_fetch_max_rows}</strong></span></span></span></li><li><span style="font-size: 13px;"><span style="font-family: Courier New, courier;">Application.host: <span style="background-color: #99ccff;"><strong>{self.str_application_host}</strong></span></span></span></li><li><span style="font-family: Courier New, courier;"><span style="font-size: 13px;">Service.route.path:&nbsp;</span><span style="font-size: 16px;"><span style="background-color: rgb(153, 204, 255); font-size: 13px;"><strong>{self.str_service_route_path}</strong></span></span></span></li><li><span style="font-family: Courier New, courier;"><span style="font-size: 13px;">Meet.threshold:&nbsp;</span><span style="font-size: 16px;"><span style="background-color: rgb(153, 204, 255); font-size: 13px;"><strong>{self.bln_meet_threshold}</strong></span></span></span></li></ul><p><span style="font-size: 14px; font-family: ;">Please find the attached doc !!</span></p><p><span style="font-size: 14px; font-family: ;">[THIS IS AN AUTOMATED MESSAGE]</span></p>',
                                           pstr_mail_subject=f'[{self.str_service_route_path}] > {self.str_cs_browser_name.upper()}_{self.str_cache_type.upper()} - {self.str_choose_env.upper()}_{self.str_db_type.upper()}: Stats fetched on {self.current_timestamp}'
                                           , pstr_mail_to=recipient
                                           )

                os.remove(self.excel_file_name)

        except Exception as e:
            messagebox.showinfo('Failure', f'Exception occurred -> {e}!!')
