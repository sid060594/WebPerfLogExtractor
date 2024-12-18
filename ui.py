import os
import tkinter
import tkinter.scrolledtext as ScrolledText
import webbrowser
from datetime import date
from tkinter import *
from tkinter import messagebox
from tkinter.ttk import Combobox

from kibana_logs_extractor import KibanaLogsExtractor
from tkcalendar import DateEntry

list_labels = ["Service.route.params", "Environment", "DB Type", "Cache Type", "Browser", "Maximum Rows to Fetch",
               "Fetch", "Start.date", "End.date", "Mail.to"]

list_mail_labels = ["Mail.to"]

# customize combo boxes
tuple_srp = (r"company/peeranalysis", r"company/environmentalBriefingArchiveDetail", r"company/physicalRisk",
             r"company/environmentalBriefingArchive")
tuple_env = ("dev", "staging", "prod")
tuple_db_type = (
    "cloud", "onprem", "cloud_china", "cloud_sg", "onprem_old", "blue_stack", "green_stack", "av_stack", "stack_1",
    "stack_2", "sg_stack_1", "sg_stack_2", "internal")
tuple_cache_type = ("warm", "cold")
tuple_browser = ("Chrome", "IE", "Firefox", "Chrome Mobile", "HeadlessChrome", "Chrome Mobile WebView", "Mobile Safari")
tuple_rows_to_fetch = ("10", "20", "50", "100", "250", "500", "1000", "2500", "5000", "10000")
tuple_threshold = ("All records", "Only threshold ones", "Only non-threshold ones")
tuple_from = ("now-15m", "now-30m", "now-1h", "now-2h", "now-5h", "now-1d", "now-2d", "now-5d")  # deprecated
tuple_to = ("now")  # deprecated

str_mail_to = ""

list_entries = [tuple_srp, tuple_env, tuple_db_type, tuple_cache_type, tuple_browser, tuple_rows_to_fetch,
                tuple_threshold]

list_date_entries = [tuple_from, tuple_to]

list_mail_entries = [str_mail_to]

dict_query_fields = {}

window = Tk()  # setup the app obj

window.title('S&P Global - Kibana Performance Logs Extractor')

kibana_logs_extractor = KibanaLogsExtractor()

# setting up labels
y = 0

for labels in list_labels:
    Label(window, text=labels, fg='black', font=("Comic Sans MS", 10)).place(x=60, y=y + 50)
    y += 50


def fetch_logs(plist_labels, plist_args):
    try:
        int_counter = 0

        # assign query fields
        for _ in plist_labels:
            if int_counter < len(plist_args):
                dict_query_fields.update({_: plist_args[int_counter]})
                int_counter += 1
        kibana_logs_extractor.fetch_logs(plist_labels, plist_args, dict_query_fields)
    except Exception as e:
        messagebox.showinfo('Failure', f'Exception occurred -> {e}!!')


def fetch_gui_args(pdict_gui):
    try:
        list_args = []
        for k, v in pdict_gui.items():
            if v.get() != "":
                list_args.append(v.get())

        return list_args
    except Exception as e:
        messagebox.showinfo('Failure', f'Exception occurred -> {e}!!')


# set callback method
def fetch_values():
    try:
        list_args = fetch_gui_args(dict_temp)
        dict_mandatory_fields = {k: v for k, v in dict_temp.items() if
                                 not ((lambda k, v: 'mail' in k)(k, v))}  # predicate to filter
        list_mandatory_args = [x for x in list_args if "@" not in x]
        if len(list_mandatory_args) != len(dict_mandatory_fields):
            messagebox.showinfo(f"{len(dict_mandatory_fields) - len(list_mandatory_args)} Missing Input(s)",
                                "Except Mail, All fields are mandatory !!")

        if len(dict_mandatory_fields) == len(list_mandatory_args):
            fetch_logs(list_labels, list_args)
    except Exception as e:
        messagebox.showinfo('Failure', f'Exception occurred -> {e}!!')


# customize combo boxes
y = 0
dict_temp = {}

for i in range(len(list_entries)):
    dict_temp.update({fr'cb_{i}': Combobox(window, values=list_entries[i], state='normal' if i == 0 else 'readonly')})
    dict_temp.get(fr'cb_{i}').current(0)
    dict_temp.get(fr'cb_{i}').place(x=285, y=y + 50)
    y += 50

for i in range(len(list_date_entries)):
    dict_temp.update({fr'date_cb_{i}': DateEntry(window, width=20, date_pattern='yyyy-mm-dd',
                                                 day=date.today().day - (len(list_date_entries) - (i + 1)),
                                                 background='darkred', foreground='white', borderwidth=0)})
    dict_temp.get(fr'date_cb_{i}').get()
    dict_temp.get(fr'date_cb_{i}').place(x=285, y=y + 50)
    y += 50

# customize the mail entry boxes
for i in range(len(list_mail_entries)):
    dict_temp.update({fr'mail_cb_{i}': Entry(window, width=23)})
    dict_temp.get(fr'mail_cb_{i}').get()
    dict_temp.get(fr'mail_cb_{i}').place(x=285, y=y + 50)
    y += 50

# customize the buttons
submit_btn = Button(window, text="Fetch Logs", fg='black', command=fetch_values, width=23, height=2)
submit_btn.place(x=285, y=y + 50)
quit_btn = Button(window, text=f"Quit", command=lambda: window.destroy(), width=7, height=1)
quit_btn.place(x=60, y=y + 50)


def open_blog():
    try:
        url = fr'https://thehub.spglobal.com/people/siddharth_singh/blog/2020/07/13/performance-logs-extractor'
        webbrowser.open(url, new=1)
    except Exception as e:
        messagebox.showinfo('Failure', f'Exception occurred -> {e}!!')


blog_btn = Button(window, text="Visit blog", fg='black', command=open_blog, height=1)
blog_btn.place(x=160, y=y + 50)

window.geometry("550x700+600+200")
window.mainloop()
