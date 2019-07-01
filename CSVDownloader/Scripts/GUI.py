#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Import Dependencies
import wx
import os

# Import Files
from Scripts import CSV_downloader


class GUI(wx.Frame):

    def __init__(self, parent, title):
        # Variables
        self.customer = None
        self.user = None
        self.pw = None
        self.general_downloads = ["Cost Codes",
                                  "Subs and Vendors",
                                  "Customer Contacts",
                                  "Lead Opportunities",
                                  "Lead Proposals List",
                                  "Jobs List"]

        self.financial_downloads = ["Owner Invoices",
                                    "Bids",
                                    "Bills And POs",
                                    "PO Payments",
                                    "Budget"]

        self.pm_downloads = ["Schedule",
                             "To Do's",
                             "Change Orders",
                             "Warranty",
                             "Time Clock"]

        self.print_to_pdf = ["Estimates",
                             "Daily Logs",
                             "Selections"]

        self.checkbox_ids = []
        self.checkboxes = []

        width, height = wx.GetDisplaySize()
        self.static_font = wx.Font(wx.FontInfo(12))
        self.hero_font = wx.Font(wx.FontInfo(20).FaceName("Helvetica"))
        self.empty_font = wx.Font(wx.FontInfo(30).FaceName("Helvetica"))
        super(GUI, self).__init__(parent, title=title, size=(width / 2, height / 2))

        self.InitUI()
        self.Centre()

    def InitUI(self):
        # Set up the panel
        panel = wx.Panel(self)
        panel.SetBackgroundColour((42, 45, 52))

        sizer = wx.GridBagSizer(5, 5)

        text1 = wx.StaticText(panel, label="CSV Downloader")
        text1.SetFont(self.static_font)
        text1.SetForegroundColour('white')
        sizer.Add(text1, pos=(0, 0), flag=wx.TOP | wx.LEFT | wx.BOTTOM,
                  border=30)

        path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        filename = os.path.join(path, 'images', "logo-white-bg.png")
        image = wx.Image(filename, wx.BITMAP_TYPE_ANY)
        image_bitmap = wx.StaticBitmap(panel, wx.ID_ANY, wx.Bitmap(image))
        sizer.Add(image_bitmap, pos=(0, 4), flag=wx.TOP | wx.RIGHT | wx.ALIGN_RIGHT,
                  border=30)

        line = wx.StaticLine(panel)
        sizer.Add(line, pos=(1, 0), span=(1, 5),
                  flag=wx.EXPAND | wx.BOTTOM, border=30)

        # text2 = wx.StaticText(panel, label="Company Name")
        # text2.SetForegroundColour('white')
        # sizer.Add(text2, pos=(2, 0), flag=wx.LEFT, border=10)
        #
        # self.customer = wx.TextCtrl(panel)
        # sizer.Add(self.customer, pos=(2, 1), span=(1, 4), flag=wx.TOP | wx.EXPAND)
        #
        text3 = wx.StaticText(panel, label="User Name")
        text3.SetForegroundColour('white')
        sizer.Add(text3, pos=(3, 0), flag=wx.LEFT | wx.TOP, border=10)

        self.user = wx.TextCtrl(panel)
        sizer.Add(self.user, pos=(3, 1), span=(1, 4), flag=wx.TOP | wx.EXPAND,
                  border=5)

        text4 = wx.StaticText(panel, label="Password")
        text4.SetForegroundColour('white')
        sizer.Add(text4, pos=(4, 0), flag=wx.TOP | wx.LEFT, border=10)

        self.pw = wx.TextCtrl(panel, style=wx.TE_PASSWORD)
        sizer.Add(self.pw, pos=(4, 1), span=(1, 4),
                  flag=wx.TOP | wx.EXPAND, border=5)

        # General Download Group
        # sb1 = wx.StaticBox(panel, label="General Downloads")
        # sb1.SetForegroundColour('white')
        # boxsizer1 = wx.StaticBoxSizer(sb1, wx.VERTICAL)
        # for elem in self.general_downloads:
        #     boxsizer1.Add(self.create_checkbox(panel, elem))
        #
        # sizer.Add(boxsizer1, pos=(5, 0), span=(1, 5),
        #           flag=wx.EXPAND | wx.TOP | wx.LEFT | wx.RIGHT, border=10)
        #
        # # Financial Download Group
        # sb2 = wx.StaticBox(panel, label="Financial Downloads")
        # sb2.SetForegroundColour('white')
        # boxsizer2 = wx.StaticBoxSizer(sb2, wx.VERTICAL)
        # for elem in self.financial_downloads:
        #     boxsizer2.Add(self.create_checkbox(panel, elem))
        #
        # sizer.Add(boxsizer2, pos=(6, 0), span=(1, 5),
        #           flag=wx.EXPAND | wx.TOP | wx.LEFT | wx.RIGHT, border=10)
        #
        # # Project Management Download Group
        # sb3 = wx.StaticBox(panel, label="Project Management Downloads")
        # sb3.SetForegroundColour('white')
        # boxsizer3 = wx.StaticBoxSizer(sb3, wx.VERTICAL)
        # for elem in self.pm_downloads:
        #     boxsizer3.Add(self.create_checkbox(panel, elem))
        #
        # sizer.Add(boxsizer3, pos=(7, 0), span=(1, 5),
        #           flag=wx.EXPAND | wx.TOP | wx.LEFT | wx.RIGHT, border=10)
        #
        # # Print to PDF Download Group
        # sb4 = wx.StaticBox(panel, label="Print to PDF Downloads")
        # sb4.SetForegroundColour('white')
        # boxsizer4 = wx.StaticBoxSizer(sb4, wx.VERTICAL)
        # for elem in self.print_to_pdf:
        #     boxsizer4.Add(self.create_checkbox(panel, elem))
        #
        # sizer.Add(boxsizer4, pos=(8, 0), span=(1, 5),
        #           flag=wx.EXPAND | wx.TOP | wx.LEFT | wx.RIGHT, border=10)
        #
        # # Check All Button
        # sizer.Add(self.create_checkbox(panel, "Check All"), pos=(9, 0),
        #           flag=wx.LEFT, border=10)
        #
        button = wx.Button(panel, label='Run')
        button.Bind(wx.EVT_BUTTON, self.run_crawler)
        sizer.Add(button, pos=(10, 4), flag=wx.ALIGN_RIGHT, border=30)

        sizer.AddGrowableCol(2)
        panel.SetSizer(sizer)
        sizer.Fit(self)
        self.Bind(wx.EVT_CHECKBOX, self.check_all)

    def check_all(self, event):
        clicked = event.GetEventObject()
        if clicked.GetId() == self.checkbox_ids[-1]:
            for cb in self.checkboxes:
                cb.SetValue(clicked.GetValue())

    def create_checkbox(self, panel, label):
        inner_sizer = wx.BoxSizer(wx.HORIZONTAL)
        text4 = wx.StaticText(panel, label=label)
        text4.SetForegroundColour('white')
        cb = wx.CheckBox(panel)
        inner_sizer.Add(cb,
                        flag=wx.LEFT | wx.TOP, border=5)
        self.checkbox_ids.append(cb.GetId())
        self.checkboxes.append(cb)
        inner_sizer.Add(text4, flag=wx.TOP | wx.LEFT, border=2)
        return inner_sizer

    def run_crawler(self, event):
        # flags = []
        # for cb in self.checkboxes:
        #     flags.append(cb.GetValue())
        # customer = self. customer.GetValue()
        user = self.user.GetValue()
        pw = self.pw.GetValue()

        CSV_downloader.WebCrawler.main(user, pw)


def main():
    app = wx.App()
    ex = GUI(None, title="BT Downloader")
    ex.Show()
    app.MainLoop()


if __name__ == '__main__':
    main()
