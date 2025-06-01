import json
import numpy
import pandas
import plotly.express as px
import time
data = json.load(open("content.json", "r", encoding="utf-8"))
"""
{"0":{
"Date":"2025-05-01 00:00:44", "uName":"Сервер dbrobo","serial":"01","data":{"system_HDD_Total":null,
"system_HDD_Used":null,"system_IDLE":92.5,"system_LA1":0.0,"system_LA15":0.0,"system_LA5":0.0,
"system_Num_cores":1.0,"system_Processes_Running":1.0,"system_Processes_Sleeping":102.0,
"system_Processes_Stopped":0.0,"system_Processes_Total":103.0,"system_Processes_Zombie":0.0,
"system_RAM_Total":2004.0,"system_RAM_Used":258.0,"system_SWAP_Total":1956.0,"system_SWAP_Used":0.0,
"system_Version":"2021-06-02"}}
"""

class Models:

    arr_x = []
    arr_y = []

    def __init__(self, mode):
        self.mode = mode

    def show(self):
        now = time.localtime().tm_hour
        print(now)
        for key in data:
            entry = data[key]
            date = entry.get("Date")
            idle = entry.get("data", {}).get("weather_temp")
            if self.mode == 1:
                if now - 1 <= int(date[11:13]) <= now:
                    self.arr_x.append(date)
                    self.arr_y.append(idle)
                    print(date, idle)
                if int(date[11:13]) > now:
                    break
            elif self.mode == 2:
                if now - 3 <= int(date[11:13]) <= now:
                    self.arr_x.append(date)
                    self.arr_y.append(idle)
                    print(date, idle)
                if int(date[11:13]) > now:
                    break
            elif self.mode == 3:
                self.arr_x.append(date)
                self.arr_y.append(idle)
                print(date, idle)
            else:
                print("IDK this mode")

        fig = px.line(x=self.arr_x, y=self.arr_y)
        fig.show()

mod = Models(3)
mod.show()
