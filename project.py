import tkinter as tk
from tkinter import filedialog, messagebox
import ttkbootstrap as ttk
import pandas as pd
import json
import plotly.graph_objects as go
import time
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import threading

"""
Блок 1: Определение основного класса приложения
Этот блок содержит класс ChartApp, который управляет главным окном приложения,
инициализирует переменные и создает пользовательский интерфейс.
"""
class ChartApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Practica")
        self.geometry("1200x400")
        self.resizable(False, False)

        self.device_data = {}
        self.filter_by_date = tk.BooleanVar(value=False)
        self.effective_temp_mode = tk.BooleanVar(value=False)
        self.avg_one_hour = tk.BooleanVar(value=False)
        self.avg_three_hours = tk.BooleanVar(value=False)
        self.avg_one_day = tk.BooleanVar(value=False)
        self.min_max_daily = tk.BooleanVar(value=False)
        self.chart_style = tk.StringVar(value='line')

        self.sensation_colors = {
            'Крайне холодно': '#000080', 'Очень холодно': '#0000FF', 'Холодно': '#87CEFA',
            'Умеренно холодно': '#ADD8E6', 'Прохладно': '#008000', 'Умеренно тепло': '#9ACD32',
            'Тепло': '#FFD700', 'Жарко': '#FF8C00', 'Очень жарко': '#FF0000'
        }


        self.min_datetime = None  # Минимальная дата из данных (pd.Timestamp)
        self.max_datetime = None  # Максимальная дата из данных (pd.Timestamp)
        self.x_axis_list = None  # Список для выбора параметра оси X
        self.y_axis_list = None  # Список для выбора параметров оси Y
        self.device_selector = None  # Выпадающий список для устройства
        self.start_datetime_selector = None  # Выпадающий список для начальной даты
        self.end_datetime_selector = None  # Выпадающий список для конечной даты
        self.start_hour_entry = None  # Поле для часов начала
        self.start_minute_entry = None  # Поле для минут начала
        self.end_hour_entry = None  # Поле для часов конца
        self.end_minute_entry = None  # Поле для минут конца
        self.chart_figure = go.Figure()  # Объект Plotly для построения графика
        self.chart_display = None  # Окно для отображения графика
        self.chart_canvas = None  # Холст для рендеринга графика в Tkinter
        self.loading_bar = None  # Прогресс-бар для загрузки JSON
        self.load_json_button = None  # Кнопка загрузки JSON

        # Создание интерфейса
        self._initialize_widgets()
        self._configure_time_validation()

    """
    Блок 2: Инициализация пользовательского интерфейса
    Этот блок создает и размещает все виджеты интерфейса.
    """
    def _initialize_widgets(self):
        # Настройка стиля с использованием ttkbootstrap
        style = ttk.Style(theme='litera')  # Тема с округлым стилем
        style.configure('TButton', font=('Arial', 10), padding=8, borderadius=15)
        style.configure('TLabel', font=('Arial', 10))
        style.configure('TCheckbutton', font=('Arial', 10))
        style.configure('TRadiobutton', font=('Arial', 10))
        style.configure('TLabelframe', font=('Arial', 11, 'bold'), borderadius=10)
        style.configure('TLabelframe.Label', font=('Arial', 11, 'bold'))

        # Главный контейнер с двухколоночной структурой
        primary_frame = ttk.Frame(self, padding=10)
        primary_frame.grid(row=0, column=0, sticky='nsew')
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Левая колонка для "Загрузка данных", "Выбор устройств" и "Параметры осей"
        left_frame = ttk.Frame(primary_frame, padding=5)
        left_frame.grid(row=0, column=0, sticky='nsw', padx=5)

        # Правая колонка для "Настройки", "Тип графика" и кнопки "Построить"
        right_frame = ttk.Frame(primary_frame, padding=5)
        right_frame.grid(row=0, column=1, sticky='nsew', padx=5)
        primary_frame.columnconfigure(0, weight=1)
        primary_frame.columnconfigure(1, weight=1)

        # Секция загрузки данных (в левой колонке)
        data_load_frame = ttk.LabelFrame(left_frame, text='Загрузка данных', padding=10, bootstyle='primary')
        data_load_frame.grid(row=0, column=0, sticky='ew', pady=5)
        data_load_frame.columnconfigure(1, weight=1)

        self.load_json_button = ttk.Button(data_load_frame, text='Загрузить JSON', command=self._begin_json_load, bootstyle='primary')
        self.load_json_button.grid(row=0, column=0, padx=5, sticky='w')

        self.loading_bar = ttk.Progressbar(data_load_frame, orient='horizontal', mode='determinate', length=200, bootstyle='primary')
        self.loading_bar.grid(row=0, column=1, padx=5, sticky='ew')
        self.loading_bar.grid_remove()

        # Секция выбора устройств (в левой колонке)
        device_select_frame = ttk.LabelFrame(left_frame, text='Выбор устройств', padding=10, bootstyle='primary')
        device_select_frame.grid(row=1, column=0, sticky='ew', pady=5)
        device_select_frame.columnconfigure(1, weight=1)
        device_select_frame.columnconfigure(3, weight=1)

        ttk.Label(device_select_frame, text='Устройство X:').grid(row=0, column=0, padx=5, sticky='e')
        self.device_selector = ttk.Combobox(device_select_frame, state='readonly', font=('Arial', 10), bootstyle='primary')
        self.device_selector.grid(row=0, column=1, padx=5, sticky='ew')
        self.device_selector.bind('<<ComboboxSelected>>', self._handle_x_device_selection)
        self.device_selector.bind('<<ComboboxSelected>>', self._handle_y_device_selection)

        # Секция выбора параметров осей (в левой колонке)
        axis_params_frame = ttk.LabelFrame(left_frame, text='Параметры осей', padding=10, bootstyle='primary')
        axis_params_frame.grid(row=2, column=0, sticky='ew', pady=5)
        axis_params_frame.columnconfigure(0, weight=1)
        axis_params_frame.columnconfigure(1, weight=1)

        x_axis_frame = ttk.LabelFrame(axis_params_frame, text='Ось X', padding=5, bootstyle='primary')
        x_axis_frame.grid(row=0, column=0, padx=5, sticky='ew')
        self.x_axis_list = tk.Listbox(x_axis_frame, selectmode='single', width=25, height=6, exportselection=False,
                                      font=('Arial', 10))
        self.x_axis_list.pack(side='left', fill='y')
        x_scrollbar = ttk.Scrollbar(x_axis_frame, orient='vertical', command=self.x_axis_list.yview, bootstyle='primary')
        x_scrollbar.pack(side='right', fill='y')
        self.x_axis_list.config(yscrollcommand=x_scrollbar.set)

        y_axis_frame = ttk.LabelFrame(axis_params_frame, text='Ось Y', padding=5, bootstyle='primary')
        y_axis_frame.grid(row=0, column=1, padx=5, sticky='ew')
        self.y_axis_list = tk.Listbox(y_axis_frame, selectmode='extended', width=25, height=6, exportselection=False,
                                      font=('Arial', 10))
        self.y_axis_list.pack(side='left', fill='y')
        y_scrollbar = ttk.Scrollbar(y_axis_frame, orient='vertical', command=self.y_axis_list.yview, bootstyle='primary')
        y_scrollbar.pack(side='right', fill='y')
        self.y_axis_list.config(yscrollcommand=y_scrollbar.set)

        # Секция настроек (в правой колонке)
        settings_frame = ttk.LabelFrame(right_frame, text='Настройки', padding=10, bootstyle='primary')
        settings_frame.grid(row=0, column=0, sticky='ew', pady=5)
        settings_frame.columnconfigure(0, weight=1)
        settings_frame.columnconfigure(1, weight=2)
        settings_frame.columnconfigure(2, weight=1)
        settings_frame.columnconfigure(3, weight=1)

        ttk.Checkbutton(settings_frame, text='Фильтр по дате', variable=self.filter_by_date,
                        command=self._toggle_date_filter, bootstyle='primary').grid(row=0, column=0, columnspan=4, sticky='w', padx=5, pady=5)

        # Начальная дата и время
        ttk.Label(settings_frame, text='С:').grid(row=1, column=0, sticky='e', padx=5, pady=2)
        self.start_datetime_selector = ttk.Combobox(settings_frame, state='disabled', font=('Arial', 10), bootstyle='primary')
        self.start_datetime_selector.grid(row=1, column=1, padx=5, pady=2, sticky='ew')
        self.start_hour_entry = ttk.Entry(settings_frame, state='disabled', width=4, font=('Arial', 10))
        self.start_hour_entry.grid(row=1, column=2, padx=2, pady=2, sticky='e')
        self.start_minute_entry = ttk.Entry(settings_frame, state='disabled', width=4, font=('Arial', 10))
        self.start_minute_entry.grid(row=1, column=3, padx=2, pady=2, sticky='w')

        # Конечная дата и время
        ttk.Label(settings_frame, text='По:').grid(row=2, column=0, sticky='e', padx=5, pady=2)
        self.end_datetime_selector = ttk.Combobox(settings_frame, state='disabled', font=('Arial', 10), bootstyle='primary')
        self.end_datetime_selector.grid(row=2, column=1, padx=5, pady=2, sticky='ew')
        self.end_hour_entry = ttk.Entry(settings_frame, state='disabled', width=4, font=('Arial', 10))
        self.end_hour_entry.grid(row=2, column=2, padx=2, pady=2, sticky='e')
        self.end_minute_entry = ttk.Entry(settings_frame, state='disabled', width=4, font=('Arial', 10))
        self.end_minute_entry.grid(row=2, column=3, padx=2, pady=2, sticky='w')

        ttk.Checkbutton(settings_frame, text='ЭТ + Теплоощущение', variable=self.effective_temp_mode, bootstyle='primary').grid(
            row=3, column=0, columnspan=4, sticky='w', padx=5, pady=5)

        ttk.Label(settings_frame, text='Температура:').grid(row=4, column=0, sticky='e', padx=5, pady=2)
        self.temp_selector = ttk.Combobox(settings_frame, state='readonly', width=15, font=('Arial', 10), bootstyle='primary')
        self.temp_selector.grid(row=4, column=1, padx=5, pady=2, sticky='ew')
        ttk.Label(settings_frame, text='Влажность:').grid(row=4, column=2, sticky='e', padx=5, pady=2)
        self.humidity_selector = ttk.Combobox(settings_frame, state='readonly', width=15, font=('Arial', 10), bootstyle='primary')
        self.humidity_selector.grid(row=4, column=3, padx=5, pady=2, sticky='ew')

        ttk.Checkbutton(settings_frame, text='Среднее за 1 ч', variable=self.avg_one_hour, bootstyle='primary').grid(
            row=5, column=0, sticky='w', padx=5, pady=2)
        ttk.Checkbutton(settings_frame, text='Среднее за 3 ч', variable=self.avg_three_hours, bootstyle='primary').grid(
            row=5, column=1, sticky='w', padx=5, pady=2)
        ttk.Checkbutton(settings_frame, text='Среднее за 1 д', variable=self.avg_one_day, bootstyle='primary').grid(
            row=5, column=2, sticky='w', pady=2)
        ttk.Checkbutton(settings_frame, text='Мин/макс за 1 д', variable=self.min_max_daily, bootstyle='primary').grid(
            row=5, column=3, sticky='w', padx=5, pady=2)

        # Секция выбора типа графика (в правой колонке)
        chart_type_frame = ttk.LabelFrame(right_frame, text='Тип графика', padding=10, bootstyle='primary')
        chart_type_frame.grid(row=1, column=0, sticky='ew', pady=5)
        for label, value in [('Линейный', 'line'), ('Столбчатый', 'bar'), ('Круговая', 'pie')]:
            ttk.Radiobutton(chart_type_frame, text=label, variable=self.chart_style, value=value, bootstyle='primary').pack(side='left', padx=10, pady=5)

        # Секция для кнопки построения графика (в правой колонке)
        button_frame = ttk.Frame(right_frame, padding=10)
        button_frame.grid(row=2, column=0, sticky='ew', pady=5)
        ttk.Button(button_frame, text='Построить', command=self.render_chart, bootstyle='primary').grid(row=0, column=0, padx=5)

    """
    Блок 3: Валидация времени
    Этот блок содержит методы для проверки и коррекции введенных значений часов и минут.
    """
    def _configure_time_validation(self):
        # Валидация часов (00-23)
        hour_validator = (self.register(self._validate_hour), '%P')
        self.start_hour_entry.configure(validate='key', validatecommand=hour_validator)
        self.end_hour_entry.configure(validate='key', validatecommand=hour_validator)

        # Валидация минут (00-59)
        minute_validator = (self.register(self._validate_minute), '%P')
        self.start_minute_entry.configure(validate='key', validatecommand=minute_validator)
        self.end_minute_entry.configure(validate='key', validatecommand=minute_validator)

        # Коррекция при потере фокуса
        self.start_hour_entry.bind('<FocusOut>', self._correct_hour)
        self.end_hour_entry.bind('<FocusOut>', self._correct_hour)
        self.start_minute_entry.bind('<FocusOut>', self._correct_minute)
        self.end_minute_entry.bind('<FocusOut>', self._correct_minute)

    def _validate_hour(self, value):
        if value == "":
            return True
        try:
            hour = int(value)
            return 0 <= hour <= 23
        except ValueError:
            return False

    def _validate_minute(self, value):
        if value == "":
            return True
        try:
            minute = int(value)
            return 0 <= minute <= 59
        except ValueError:
            return False

    def _correct_hour(self, event):
        entry = event.widget
        value = entry.get()
        if value == "":
            entry.insert(0, "00")
        else:
            try:
                hour = int(value)
                if not (0 <= hour <= 23):
                    entry.delete(0, 'end')
                    entry.insert(0, "00")
            except ValueError:
                entry.delete(0, 'end')
                entry.insert(0, "00")

    def _correct_minute(self, event):
        entry = event.widget
        value = entry.get()
        if value == "":
            entry.insert(0, "00")
        else:
            try:
                minute = int(value)
                if not (0 <= minute <= 59):
                    entry.delete(0, 'end')
                    entry.insert(0, "00")
            except ValueError:
                entry.delete(0, 'end')
                entry.insert(0, "00")

    """
    Блок 4: Управление фильтром по дате
    Этот блок содержит методы для включения/выключения виджетов даты и времени,
    а также для парсинга выбранных значений.
    """
    def _toggle_date_filter(self):
        state_combobox = 'readonly' if self.filter_by_date.get() else 'disabled'
        state_entry = 'normal' if self.filter_by_date.get() else 'disabled'
        self.start_datetime_selector.config(state=state_combobox)
        self.end_datetime_selector.config(state=state_combobox)
        self.start_hour_entry.config(state=state_entry)
        self.start_minute_entry.config(state=state_entry)
        self.end_hour_entry.config(state=state_entry)
        self.end_minute_entry.config(state=state_entry)

    def _parse_datetime(self, date_combobox, hour_entry, minute_entry):
        try:
            date_str = date_combobox.get()
            # Парсим дату с помощью time.strptime
            date_struct = time.strptime(date_str, "%d-%m-%Y")
            hour = int(hour_entry.get()) if hour_entry.get() else 0
            minute = int(minute_entry.get()) if minute_entry.get() else 0
            # Возвращаем кортеж с годом, месяцем, днем, часом и минутой
            return (date_struct.tm_year, date_struct.tm_mon, date_struct.tm_mday, hour, minute)
        except Exception:
            return None

    """
    Блок 5: Загрузка и обработка JSON-данных
    Этот блок управляет процессом загрузки JSON-файлов, их парсингом,
    а также отображением прогресса загрузки.
    """
    def _begin_json_load(self):
        self.load_json_button.config(state='disabled')
        self.loading_bar.grid()
        self.loading_bar['value'] = 0
        threading.Thread(target=self._process_json_load1, daemon=True).start()

    def _process_json_load1(self):
        file_path = filedialog.askopenfilename(filetypes=[('JSON', '*.json;*.txt')])
        if not file_path:
            self._complete_load()
            return
        try:
            threading.Thread(target=self._process_json_load2, daemon=True).start()
            with open(file_path, 'r', encoding='utf-8') as file:
                json_data = json.load(file)

            temp_device_data = {}
            for value in json_data.values():
                if 'uName' not in value or 'serial' not in value or 'Date' not in value or 'data' not in value:
                    continue
                device_name = f"{value['uName']} ({value['serial']})"
                if device_name not in temp_device_data:
                    temp_device_data[device_name] = []
                record = {'Date': pd.to_datetime(value['Date'])}
                record.update(value['data'])
                temp_device_data[device_name].append(record)

            self.device_data = {}
            for name, records in temp_device_data.items():
                dataframe = pd.DataFrame(records).set_index('Date')
                dataframe = dataframe.apply(pd.to_numeric, errors='coerce').dropna(how='all')
                self.device_data[name] = dataframe

            if not self.device_data:
                raise ValueError("Нет данных для устройств")

            self.after(0, self._update_device_lists)
            self.after(0, lambda: messagebox.showinfo("Успех", f"JSON загружен: {file_path}"))

        except Exception as e:
            self.after(0, lambda: messagebox.showerror('Ошибка', str(e)))
        finally:
            self._complete_load()

    def _process_json_load2(self):
        for i in range(10):
            time.sleep(2)
            self.loading_bar['value'] += 10
            self.update()

    def _complete_load(self):
        self.loading_bar.grid_remove()
        self.load_json_button.config(state='normal')
        self.loading_bar['value'] = 0

    """
    Блок 6: Обработка выбора устройств и дат
    Этот блок содержит методы для обновления списков устройств, параметров и дат.
    """
    def _update_device_lists(self):
        device_names = list(self.device_data.keys())
        self.device_selector['values'] = device_names
        self.device_selector['values'] = device_names
        if device_names:
            self.device_selector.set(device_names[0])
            self.device_selector.set(device_names[0])
            self._handle_x_device_selection(None)
            self._handle_y_device_selection(None)

    def _handle_x_device_selection(self, event):
        selected_device = self.device_selector.get()
        if selected_device in self.device_data:
            dataframe = self.device_data[selected_device]
            self.x_axis_list.delete(0, 'end')
            self.x_axis_list.insert('end', 'Date')
            for column in dataframe.columns:
                self.x_axis_list.insert('end', column)
            self.x_axis_list.selection_clear(0, 'end')
            self.x_axis_list.selection_set(0)

            self.min_datetime = dataframe.index.min()
            self.max_datetime = dataframe.index.max()

            # Заполнение выпадающих списков дат
            if self.min_datetime and self.max_datetime:
                date_range = pd.date_range(start=self.min_datetime, end=self.max_datetime, freq='D')
                date_strs = [dt.strftime("%d-%m-%Y") for dt in date_range]
                self.start_datetime_selector['values'] = date_strs
                self.end_datetime_selector['values'] = date_strs
                self.start_datetime_selector.set(self.min_datetime.strftime("%d-%m-%Y"))
                self.end_datetime_selector.set(self.max_datetime.strftime("%d-%m-%Y"))
                self.start_hour_entry.delete(0, 'end')
                self.start_hour_entry.insert(0, self.min_datetime.strftime("%H"))
                self.start_minute_entry.delete(0, 'end')
                self.start_minute_entry.insert(0, self.min_datetime.strftime("%M"))
                self.end_hour_entry.delete(0, 'end')
                self.end_hour_entry.insert(0, self.max_datetime.strftime("%H"))
                self.end_minute_entry.delete(0, 'end')
                self.end_minute_entry.insert(0, self.max_datetime.strftime("%M"))

    def _handle_y_device_selection(self, event):
        selected_y_device = self.device_selector.get()
        if selected_y_device in self.device_data:
            self.device_selector.set(selected_y_device)
            self._handle_x_device_selection(None)

            dataframe = self.device_data[selected_y_device]
            numeric_columns = [col for col in dataframe.columns if pd.api.types.is_numeric_dtype(dataframe[col])]
            self.y_axis_list.delete(0, 'end')
            for col in numeric_columns:
                self.y_axis_list.insert('end', col)

            temp_priority = ['weather_temp', 'BME280_temp', 'temperature']
            humidity_priority = ['weather_humidity', 'BME280_humidity', 'humidity']

            def unique_ordered(sequence):
                seen = set()
                return [x for x in sequence if not (x in seen or seen.add(x))]

            temp_candidates = unique_ordered(
                [col for col in temp_priority if col in numeric_columns] +
                [col for col in numeric_columns if col not in temp_priority]
            )
            humidity_candidates = unique_ordered(
                [col for col in humidity_priority if col in numeric_columns] +
                [col for col in numeric_columns if col not in humidity_priority]
            )

            self.temp_selector['values'] = temp_candidates
            self.humidity_selector['values'] = humidity_candidates

            default_temp = next((col for col in temp_priority if col in numeric_columns), None)
            if default_temp:
                self.temp_selector.set(default_temp)
            elif temp_candidates:
                self.temp_selector.set(temp_candidates[0])

            default_humidity = next((col for col in humidity_priority if col in numeric_columns), None)
            if default_humidity:
                self.humidity_selector.set(default_humidity)
            elif humidity_candidates:
                self.humidity_selector.set(humidity_candidates[0])

    """
    Блок 7: Построение и отображение графиков
    Этот блок содержит методы для построения графика с учетом усреднений.
    """
    def clear_chart(self):
        self.chart_figure.data = []
        self.chart_figure.layout = go.Layout()
        if self.chart_display:
            self.chart_display.destroy()
            self.chart_display = None
            self.chart_canvas = None

    def render_chart(self):
        x_device = self.device_selector.get()
        y_device = self.device_selector.get()
        if not x_device or x_device not in self.device_data or not y_device or y_device not in self.device_data:
            messagebox.showwarning('Нет устройства', 'Выберите устройства для X и Y')
            return

        x_data = self.device_data[x_device].copy()
        y_data = self.device_data[y_device].copy()

        x_selection = self.x_axis_list.curselection()
        if not x_selection:
            messagebox.showwarning('Нет полей', 'Выберите поле для оси X')
            return
        x_parameter = self.x_axis_list.get(x_selection[0])

        if self.filter_by_date.get():
            start_datetime = self._parse_datetime(self.start_datetime_selector, self.start_hour_entry, self.start_minute_entry)
            end_datetime = self._parse_datetime(self.end_datetime_selector, self.end_hour_entry, self.end_minute_entry)

            if not start_datetime or not end_datetime:
                messagebox.showerror('Ошибка', 'Некорректный формат даты/времени')
                return

            start_timestamp = pd.Timestamp(year=start_datetime[0], month=start_datetime[1], day=start_datetime[2],
                                          hour=start_datetime[3], minute=start_datetime[4])
            end_timestamp = pd.Timestamp(year=end_datetime[0], month=end_datetime[1], day=end_datetime[2],
                                        hour=end_datetime[3], minute=end_datetime[4])

            if start_timestamp < self.min_datetime:
                start_timestamp = self.min_datetime
            if end_timestamp > self.max_datetime:
                end_timestamp = self.max_datetime

            if start_timestamp > end_timestamp:
                messagebox.showerror('Ошибка', 'Неверный временной диапазон')
                return

            x_data = x_data[(x_data.index >= start_timestamp) & (x_data.index <= end_timestamp)]
            y_data = y_data[(y_data.index >= start_timestamp) & (y_data.index <= end_timestamp)]

            common_index = x_data.index.intersection(y_data.index)
            x_data = x_data.loc[common_index]
            y_data = y_data.loc[common_index]

        y_selection = self.y_axis_list.curselection()
        y_parameters = [self.y_axis_list.get(i) for i in y_selection] if y_selection else []

        self.clear_chart()

        if self.effective_temp_mode.get():
            temp_column, humidity_column = self.temp_selector.get(), self.humidity_selector.get()
            if not temp_column or not humidity_column:
                messagebox.showwarning('Ошибка', 'Выберите Температуру и Влажность')
                return
            if temp_column not in y_data.columns or humidity_column not in y_data.columns:
                messagebox.showerror('Ошибка', 'Выбранные параметры температуры или влажности отсутствуют в данных')
                return

            temperature = y_data[temp_column]
            humidity = y_data[humidity_column]
            effective_temp = temperature - 0.4 * (temperature - 10) * (1 - humidity / 100)

            if effective_temp.isna().all():
                messagebox.showerror('Ошибка', 'Невозможно вычислить эффективную температуру: данные содержат только NaN')
                return

            sensation = effective_temp.apply(self._classify_sensation)
            valid_data = effective_temp.dropna()
            valid_sensation = sensation[effective_temp.notna()]

            if valid_data.empty:
                messagebox.showerror('Ошибка', 'Нет валидных данных для построения графика теплоощущения')
                return

            chart_type = self.chart_style.get()

            if chart_type == 'pie':
                sensation_counts = valid_sensation.value_counts()
                labels = sensation_counts.index.tolist()
                values = sensation_counts.values.tolist()
                colors = [self.sensation_colors.get(cat, '#000000') for cat in labels]

                self.chart_display = tk.Toplevel(self)
                self.chart_display.title("Круговая диаграмма теплоощущения")
                self.chart_display.geometry("800x600")

                mpl_fig = plt.figure(figsize=(8, 6))
                plt.pie(values, labels=labels, autopct='%1.1f%%', startangle=90, colors=colors)
                plt.axis('equal')
                plt.title(f'Распределение теплоощущений\nПрибор: {y_device}')

                self.chart_canvas = FigureCanvasTkAgg(mpl_fig, master=self.chart_display)
                self.chart_canvas.draw()
                self.chart_canvas.get_tk_widget().pack(fill='both', expand=True)

            else:
                segment_groups = []
                current_segment = []
                previous_category = None

                for timestamp, value, category in zip(valid_data.index, valid_data, valid_sensation):
                    if category != previous_category and previous_category is not None:
                        if current_segment:
                            segment_groups.append((previous_category, current_segment))
                        current_segment = [(timestamp, value)]
                    else:
                        current_segment.append((timestamp, value))
                    previous_category = category

                if current_segment:
                    segment_groups.append((previous_category, current_segment))

                if not segment_groups:
                    messagebox.showerror('Ошибка', 'Нет валидных данных для построения графика теплоощущения')
                    return

                added_categories = set()

                for category, segment in segment_groups:
                    if not segment:
                        continue
                    x_values, y_values = zip(*segment)
                    if category not in added_categories:
                        show_in_legend = True
                        added_categories.add(category)
                    else:
                        show_in_legend = False

                    if chart_type == 'line':
                        self.chart_figure.add_trace(go.Scatter(
                            x=x_values,
                            y=y_values,
                            mode='lines',
                            line=dict(color=self.sensation_colors.get(category, '#000000'), width=2),
                            name=category,
                            showlegend=show_in_legend,
                            legendgroup=category,
                        ))
                    elif chart_type == 'bar':
                        self.chart_figure.add_trace(go.Bar(
                            x=x_values,
                            y=y_values,
                            name=category,
                            marker_color=self.sensation_colors.get(category, '#000000'),
                            showlegend=show_in_legend,
                            legendgroup=category,
                        ))

                self.chart_figure.update_layout(
                    yaxis_title='Эф. температура (°C)',
                    title=dict(
                        text=f'ЭТ и Теплоощущение\nПрибор: {y_device}',
                        font=dict(size=16)
                    ),
                    legend=dict(
                        x=1.02,
                        y=1,
                        bgcolor='rgba(255,255,255,0.9)',
                        bordercolor='black',
                        borderwidth=1,
                        font=dict(size=12),
                    ),
                    template='plotly_white',
                    margin=dict(t=100),
                    hovermode='x unified',
                    showlegend=True,
                    plot_bgcolor='white',
                    paper_bgcolor='white',
                    xaxis_rangeslider_visible=True,
                    xaxis=dict(
                        showline=True,
                        linecolor='black',
                        linewidth=1,
                        mirror=True,
                        showgrid=True,
                        gridcolor='lightgrey',
                        gridwidth=1,
                        griddash='dot'
                    ),
                    yaxis=dict(
                        showline=True,
                        linecolor='black',
                        linewidth=1,
                        mirror=True,
                        showgrid=True,
                        gridcolor='lightgrey',
                        gridwidth=1,
                        griddash='dot'
                    )
                )

                self.chart_display = tk.Toplevel(self)
                self.chart_display.title("График теплоощущения")
                self.chart_display.geometry("800x600")

                mpl_fig = plt.figure(figsize=(8, 6))
                for trace in self.chart_figure.data:
                    if trace['type'] == 'scatter':
                        line_color = trace['line']['color'] if 'line' in trace and 'color' in trace['line'] else None
                        mpl_fig.gca().plot(trace['x'], trace['y'], label=trace['name'], color=line_color)
                    elif trace['type'] == 'bar':
                        mpl_fig.gca().bar(trace['x'], trace['y'], label=trace['name'], color=trace['marker']['color'])

                mpl_fig.gca().set_xlabel('Дата')
                mpl_fig.gca().set_ylabel('Эф. температура (°C)')
                mpl_fig.gca().set_title(f'ЭТ и Теплоощущение\nПрибор: {y_device}')
                mpl_fig.gca().grid(True)

                self.chart_canvas = FigureCanvasTkAgg(mpl_fig, master=self.chart_display)
                self.chart_canvas.draw()
                self.chart_canvas.get_tk_widget().pack(fill='both', expand=True)

        else:
            if not y_parameters and self.chart_style.get() != 'pie':
                messagebox.showwarning('Нет полей', 'Выберите поля для оси Y')
                return

            if self.chart_style.get() == 'pie':
                if not y_parameters:
                    messagebox.showwarning('Нет полей', 'Выберите поля для оси Y для круговой диаграммы')
                    return

                self.chart_display = tk.Toplevel(self)
                self.chart_display.title("Круговая диаграмма")
                self.chart_display.geometry("800x600")

                mean_values = [y_data[param].mean() for param in y_parameters]
                labels = [f'{param} ({y_device})' for param in y_parameters]

                if any(val < 0 or pd.isna(val) for val in mean_values):
                    messagebox.showerror('Ошибка', 'Круговая диаграмма не поддерживает отрицательные значения или NaN')
                    self.chart_display.destroy()
                    return

                mpl_fig = plt.figure(figsize=(8, 6))
                plt.pie(mean_values, labels=labels, autopct='%1.1f%%', startangle=90, colors=plt.cm.Paired.colors)
                plt.axis('equal')
                plt.title(f'Распределение средних значений\nПрибор: {y_device}')

                self.chart_canvas = FigureCanvasTkAgg(mpl_fig, master=self.chart_display)
                self.chart_canvas.draw()
                self.chart_canvas.get_tk_widget().pack(fill='both', expand=True)

            else:
                x_values = x_data[x_parameter] if x_parameter != 'Date' else x_data.index
                for column in y_parameters:
                    trace_label = f'{column} ({y_device})'
                    if self.chart_style.get() == 'line':
                        self.chart_figure.add_trace(go.Scatter(
                            x=x_values,
                            y=y_data[column],
                            mode='lines',
                            line=dict(width=2),
                            name=trace_label,
                            showlegend=True
                        ))
                    elif self.chart_style.get() == 'bar':
                        self.chart_figure.add_trace(go.Bar(
                            x=x_values,
                            y=y_data[column],
                            name=trace_label,
                            showlegend=True
                        ))

                if any([self.avg_one_hour.get(), self.avg_three_hours.get(), self.avg_one_day.get(), self.min_max_daily.get()]):
                    resampled_data = y_data[y_parameters].copy()
                    if not resampled_data.empty:
                        last_row = resampled_data.iloc[-1].copy()
                        last_timestamp = resampled_data.index[-1]

                        if len(resampled_data) > 1:
                            time_diff = resampled_data.index[1:] - resampled_data.index[:-1]
                            min_interval = min(time_diff).total_seconds() / 60  # Интервал в минутах
                            new_timestamp = last_timestamp + pd.Timedelta(minutes=min_interval)
                        else:
                            new_timestamp = last_timestamp + pd.Timedelta(minutes=1)
                        last_row.name = new_timestamp
                        resampled_data = pd.concat([resampled_data, last_row.to_frame().T])

                    if self.avg_one_hour.get():
                        resampled_one_hour = resampled_data.resample('1h').mean()
                        for column in y_parameters:
                            self.chart_figure.add_trace(go.Scatter(
                                x=resampled_one_hour.index,
                                y=resampled_one_hour[column],
                                mode='lines',
                                line=dict(dash='dash', width=1.5, shape='hv'),
                                name=f'{column} 1ч ({y_device})'
                            ))
                    if self.avg_three_hours.get():
                        resampled_three_hours = resampled_data.resample('3h').mean()
                        for column in y_parameters:
                            self.chart_figure.add_trace(go.Scatter(
                                x=resampled_three_hours.index,
                                y=resampled_three_hours[column],
                                mode='lines',
                                line=dict(dash='dot', width=1.5, shape='hv'),
                                name=f'{column} 3ч ({y_device})'
                            ))
                    if self.avg_one_day.get():
                        resampled_one_day = resampled_data.resample('D').mean()
                        for column in y_parameters:
                            if not resampled_one_day[column].dropna().empty:
                                self.chart_figure.add_trace(go.Scatter(
                                    x=resampled_one_day.index,
                                    y=resampled_one_day[column],
                                    mode='lines',
                                    line=dict(dash='dashdot', width=1.5, shape='hv'),
                                    name=f'{column} 1д ({y_device})'
                                ))
                            else:
                                print(f"Warning: No valid 1-day resampled data for {column}")

                    if self.min_max_daily.get():
                        daily_min = resampled_data.resample('D').min()
                        daily_max = resampled_data.resample('D').max()
                        for col in y_parameters:
                            if not daily_min[col].dropna().empty:
                                self.chart_figure.add_trace(go.Scatter(
                                    x=daily_min.index,
                                    y=daily_min[col],
                                    mode='lines',
                                    line=dict(dash='dash', width=1, color='blue'),
                                    name=f'{col} min 1д ({y_device})'
                                ))
                            else:
                                print(f"Warning: No valid daily min data for {col}")
                            if not daily_max[col].dropna().empty:
                                self.chart_figure.add_trace(go.Scatter(
                                    x=daily_max.index,
                                    y=daily_max[col],
                                    mode='lines',
                                    line=dict(dash='solid', width=1, color='red'),
                                    name=f'{col} max 1д ({y_device})'
                                ))
                            else:
                                print(f"Warning: No valid daily max data for {col}")

                self.chart_figure.update_layout(
                    yaxis_title='Значение',
                    title=dict(
                        text=f'График данных\nПрибор X: {x_device}\nПрибор Y: {y_device}',
                        font=dict(size=16)
                    ),
                    legend=dict(
                        x=1.02,
                        y=1,
                        bgcolor='rgba(255,255,255,0.9)',
                        bordercolor='black',
                        borderwidth=1,
                        font=dict(size=12),
                    ),
                    template='plotly_white',
                    margin=dict(t=100),
                    hovermode='x unified',
                    showlegend=True,
                    plot_bgcolor='white',
                    paper_bgcolor='white',
                    xaxis_rangeslider_visible=True,
                    xaxis=dict(
                        title=x_parameter,
                        showline=True,
                        linecolor='black',
                        linewidth=1,
                        mirror=True,
                        showgrid=True,
                        gridcolor='lightgrey',
                        gridwidth=1,
                        griddash='dot'
                    ),
                    yaxis=dict(
                        showline=True,
                        linecolor='black',
                        linewidth=1,
                        mirror=True,
                        showgrid=True,
                        gridcolor='lightgrey',
                        gridwidth=1,
                        griddash='dot'
                    )
                )

                self.chart_display = tk.Toplevel(self)
                self.chart_display.title("График")
                self.chart_display.geometry("800x600")

                mpl_fig = plt.figure(figsize=(8, 6))
                for trace in self.chart_figure.data:
                    if trace['type'] == 'scatter':
                        line_color = trace['line']['color'] if 'line' in trace and 'color' in trace['line'] else None
                        # Handle stepped line for all averaged traces (1ч, 3ч, 1д) in matplotlib
                        if '1ч' in trace['name'] or '3ч' in trace['name'] or '1д' in trace['name']:
                            mpl_fig.gca().step(trace['x'], trace['y'], label=trace['name'], color=line_color, where='post')
                        else:
                            mpl_fig.gca().plot(trace['x'], trace['y'], label=trace['name'], color=line_color)
                    elif trace['type'] == 'bar':
                        mpl_fig.gca().bar(trace['x'], trace['y'], label=trace['name'])

                mpl_fig.gca().set_xlabel(x_parameter)
                mpl_fig.gca().set_ylabel('Значение')
                mpl_fig.gca().set_title(f'График\nПрибор X: {x_device}\nПрибор Y: {y_device}')
                mpl_fig.gca().legend()
                mpl_fig.gca().grid(True)

                self.chart_canvas = FigureCanvasTkAgg(mpl_fig, master=self.chart_display)
                self.chart_canvas.draw()
                self.chart_canvas.get_tk_widget().pack(fill='both', expand=True)

    """
    Блок 8: Классификация теплоощущения
    Этот блок содержит метод для определения категории теплоощущения.
    """
    def _classify_sensation(self, effective_temp):
        if pd.isna(effective_temp):
            return None
        if effective_temp >= 30:
            return 'Очень жарко'
        elif effective_temp >= 24:
            return 'Жарко'
        elif effective_temp >= 18:
            return 'Тепло'
        elif effective_temp >= 12:
            return 'Умеренно тепло'
        elif effective_temp >= 6:
            return 'Прохладно'
        elif effective_temp >= 0:
            return 'Умеренно холодно'
        elif effective_temp >= -12:
            return 'Холодно'
        elif effective_temp >= -24:
            return 'Очень холодно'
        else:
            return 'Крайне холодно'

"""
Блок 9: Запуск приложения
"""
if __name__ == '__main__':
    app = ChartApp()
    app.mainloop()