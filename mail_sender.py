import datetime as dt
import re
import time as t
from tkinter import messagebox

import win32com.client as client


class MailSender:
    def __init__(self):
        self.outlook_obj = client.dynamic.Dispatch('outlook.application')
        self.current_timestamp = dt.datetime.fromtimestamp(t.time()).strftime('%m-%d-%Y_%H:%M_%p')

    def send_mail(self, plist_attachments, **kwargs):
        try:
            mail = self.outlook_obj.CreateItem(0x0)

            str_mail_to = kwargs.get("pstr_mail_to", None)
            str_mail_cc = kwargs.get("pstr_mail_cc", None)
            str_mail_bcc = kwargs.get("pstr_mail_bcc", None)
            str_mail_display = kwargs.get("pstr_mail_display", False)

            str_mail_subject = kwargs.get("pstr_mail_subject", None)
            str_mail_body = kwargs.get("pstr_mail_body", None)

            for attachments in plist_attachments:
                mail.Attachments.Add(attachments)

            if str_mail_to is not None:
                list_mail_to = re.split(';|,', "".join(str_mail_to.split()))
                for recipient in list_mail_to:
                    mail.Recipients.Add(recipient)
            else:
                mail.To = str_mail_to

            if str_mail_cc is not None:
                mail.CC = str_mail_cc

            if str_mail_bcc is not None:
                mail.BCC = str_mail_bcc

            if str_mail_subject is not None:
                mail.Subject = str_mail_subject
            else:
                mail.Subject = 'Execution Started on ' + self.current_timestamp

            if str_mail_body is not None:
                mail.HTMLBody = str_mail_body
            else:
                mail.HTMLBody = 'Please find the attached doc !!'

            if str_mail_display:
                mail.display()

            mail.Send()

            messagebox.showinfo("Success",
                                f"Email successfully sent to the recipient(s) ({', '.join(map(str, list_mail_to))}) !!")

        except Exception as exception:
            print(f"Exception occurred while sending mail: {exception}")
