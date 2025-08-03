# Calculus Graphicus  
Chose read version:
[Russian](#RU)/[English](#EN)
# RU
## Описание  
Calculus Graphicus — это приложение на Python для визуализации данных с устройств. 

## Оглавление:
- [Возможности](#Возможности)
- [Требования](#Требования)
- [Установка](#Установка)
- [Структура проекта](#Структура-проекта)
- [Использование](#Использование)
- [Формат JSON](#Формат-JSON)
- [Замечания](#Замечания)
- [Ограничения](#Ограничения)

## Возможности

#### Загрузка данных:  
Чтение JSON-файлов с данными устройств.  
  
  
#### Выбор параметров:  
Выбор устройства и параметров для осей X и Y.  
Приоритетный выбор температуры и влажности для расчета ЭТ.  
  
  
#### Фильтрация по времени:  
Выбор временного диапазона с точностью до минут.  
  
  
#### Типы графиков:  
Линейный, столбчатый, точечный.  
Отображение нескольких параметров на одном графике.  
  
  
#### Обработка данных:  
Данные как есть.  
Осреднение за 1 час, 3 часа, сутки.  
Минимальные и максимальные значения за сутки.  
  
  
#### Эффективная температура:  
Расчет ЭТ: t - 0.4 * (t - 10) * (1 - h/100), где t — температура, h — влажность.  
Классификация теплоощущения (например, "Очень жарко", "Холодно").  
Цветовая кодировка теплоощущения на графике.  
  
  
  
## Требования
  
Python 3.8+  
#### Библиотеки:  
- tkinter 
- ttkbootstrap 
- threading
- time
- pandas
- plotly
- matplotlib
- json

  
Файл иконки: myApp.ico (для Windows).  
  
## Установка
  
Установите Python 3.8+.  
Установите зависимости:
- tkinter 
- ttkbootstrap 
- threading
- time
- pandas
- plotly
- matplotlib
- json

Поместите файл myApp.ico в корневую папку проекта (для иконки окна).  
  
## Структура проекта
  
#### main.py:
Главный файл, инициализирующий приложение и управляющий его жизненным циклом.  
#### gui.py: 
Реализация графического интерфейса.  
#### data_processing.py: 
Обработка данных, загрузка JSON, построение графиков.
#### tests.py:
Тесты для проверки работоспособности компонентов приложения.
  
## Использование
  
#### Запустите приложение:
python main.py  
  
#### В интерфейсе:  
Нажмите "Загрузить JSON" и выберите файл с данными.  
Выберите устройство в разделе "Выбор устройств".  
Выберите параметры для осей X и Y в разделе "Параметры осей".  

(Опционально) Включите фильтр по дате и задайте диапазон в "Настройки".  
Выберите тип графика (линейный, столбчатый, точечный).  
Включите режим ЭТ или осреднение (1 ч, 3 ч, сутки, мин/макс).  
Нажмите "Построить" для отображения графика.  
  
  
  
## Формат JSON
Пример структуры JSON-файла:  
```
{  
  "device1": {  
    "uName": "Device Name",  
    "serial": "12345",  
    "Date": "2023-01-01 12:00:00",  
    "data": {  
      "weather_temp": 20.5,  
      "weather_humidity": 60.0  
    }  
  }  
}  
```
  
## Замечания
  
Для корректной работы JSON-файл должен содержать ключи uName, serial, Date и data.  
Графики отображаются в отдельном окне с использованием matplotlib.  
Длительная загрузка больших JSON-файлов сопровождается индикатором прогресса.  
  
## Ограничения
  
Приложение не поддерживает работу с файлами, не соответствующими ожидаемой структуре JSON.  
Некорректные данные в JSON могут вызвать ошибки, отображаемые в интерфейсе.  

# EN
## Description  
Calculus Graphicus is a Python application for visualizing data from devices. 

## Table of Contents:
- [Features](#Features)
- [Requirements](#Requirements)
- [Installation](#Installation)
- [Project Structure](#Project-Structure)
- [Usage](#Usage)
- [JSON Format](#Format-JSON)
- [Remarks](#Remarks)
- [Restrictions](#Restrictions)

## Features

#### Uploading data:  
Reading JSON files with meteorological device data.  
  
  
#### Selection of parameters:  
Selecting the device and parameters for the X and Y axes.  
Priority selection of temperature and humidity for calculating ET.  
  
  
#### Filtering by time:  
Selecting a time range accurate to minutes.  
  
  
#### Types of graphs:  
Linear, columnar, and dotted.  
Displaying multiple parameters on a single graph.  
  
  
#### Data processing:  
The data is as it is.  
Averaging over 1 hour, 3 hours, and a day.  
Minimum and maximum values per day.  
  
  
#### Effective temperature:  
Calculation of ET: t - 0.4 * (t - 10) * (1 - h/100), where t is temperature, h is humidity.  
Classification of heat perception (for example, "Very hot", "Cold").  
Color coding of heat perception on the graph.  
  
  
  
## Requirements
  Python 3.8+  
#### Libraries:  
- tkinter 
- ttkbootstrap 
- threading
- time
- pandas
- plotly
- matplotlib
- json

  
Icon file: MyApp.ico (for Windows).  
  
## Installation
  Install Python 3.8+.  
Install the dependencies:
- tkinter 
- ttkbootstrap 
- threading
- time
- pandas
- plotly
- matplotlib
- json

Place the MyApp.ico file in the root folder of the project (for the window icon).  
  
## Project structure
  #### main.py:
The main file that initializes the application and manages its lifecycle.  
#### gui.py: 
Implementation of the graphical interface.  
#### data_processing.py: 
Data processing, JSON loading, and plotting.
#### tests.py:
Tests to check the functionality of application components.
  
## Usage
  #### Launch the app:
python main.py  
  
#### In the interface:  
Click "Upload JSON" and select the data file.  
Select a device in the "Device Selection" section.  
Select the options for the X and Y axes in the Axis Options section.  

(Optional) Turn on the date filter and set the range in Settings.  
Select the graph type (linear, columnar, dotted).  
Turn on the ET or averaging mode (1 hour, 3 hours, day, min/max).  
Click "Build" to display the graph.  
  
  
  
## JSON format
Example of a JSON file structure:  
```
{  
  "device1": {  
    "uName": "Device Name",  
    "serial": "12345",  
    "Date": "2023-01-01 12:00:00",  
    "data": {  
      "weather_temp": 20.5,  
      "weather_humidity": 60.0  
    }  
  }  
}  
```
  ## Remarks
  For the JSON file to work correctly, it must contain the uName, serial, Date, and data keys.  
The graphs are displayed in a separate window using matplotlib.  
Long-term loading of large JSON files is accompanied by a progress indicator.  
  
## Restrictions
  The application does not support working with files that do not match the expected JSON structure.  
Incorrect data in JSON can cause errors displayed in the interface.  