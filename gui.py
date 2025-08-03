import tkinter as tk
import ttkbootstrap as ttk


class ChartAppGUI:
    def __init__(self, master):
        """Flags"""
        self.master = master
        self.device_selector = None
        self.start_datetime_selector = None
        self.end_datetime_selector = None
        self.start_hour_entry = None
        self.start_minute_entry = None
        self.end_hour_entry = None
        self.end_minute_entry = None
        self.x_axis_list = None
        self.y_axis_list = None
        self.temp_selector = None
        self.humidity_selector = None
        self.load_json_button = None
        self.loading_bar = None

        self._initialize_widgets()
        self._configure_time_validation()

    def _initialize_widgets(self):
        """Styles ttkbootstrap"""
        style = ttk.Style(theme='litera')
        style.configure('TButton', font=('Arial', 10), padding=8, borderadius=15)
        style.configure('TLabel', font=('Arial', 10))
        style.configure('TCheckbutton', font=('Arial', 10))
        style.configure('TRadiobutton', font=('Arial', 10))
        style.configure('TLabelframe', font=('Arial', 11, 'bold'), borderadius=10)
        style.configure('TLabelframe.Label', font=('Arial', 11, 'bold'))

        """Creating and placing frames"""
        primary_frame = ttk.Frame(self.master, padding=10)
        primary_frame.grid(row=0, column=0, sticky='nesw')
        self.master.grid_columnconfigure(0, weight=1)
        self.master.grid_rowconfigure(0, weight=1)
        left_frame = ttk.Frame(primary_frame, padding=5)
        left_frame.grid(row=0, column=0, sticky='nsw', padx=5)
        right_frame = ttk.Frame(primary_frame, padding=5)
        right_frame.grid(row=0, column=1, sticky='nesw', padx=5)
        primary_frame.columnconfigure(0, weight=1)
        primary_frame.columnconfigure(1, weight=1)

        """data load frame"""
        data_load_frame = ttk.LabelFrame(left_frame, text='Загрузка данных', padding=10, bootstyle='primary')
        data_load_frame.grid(row=0, column=0, sticky='ew', pady=5)
        data_load_frame.columnconfigure(1, weight=1)

        """load_json_button and loading_bar"""
        self.load_json_button = ttk.Button(data_load_frame, text='Загрузить JSON',
                                           command=self.master.data_processor._begin_json_load, bootstyle='primary')
        self.load_json_button.grid(row=0, column=0, padx=5, sticky='w')
        self.loading_bar = ttk.Progressbar(data_load_frame, orient='horizontal', mode='determinate', length=200,
                                           bootstyle='primary')
        self.loading_bar.grid(row=0, column=1, padx=5, sticky='ew')
        self.loading_bar.grid_remove()

        """device_select_frame"""
        device_select_frame = ttk.LabelFrame(left_frame, text='Выбор устройств', padding=10, bootstyle='primary')
        device_select_frame.grid(row=1, column=0, sticky='ew', pady=5)
        device_select_frame.columnconfigure(1, weight=1)
        ttk.Label(device_select_frame, text='Устройство :').grid(row=0, column=0, padx=5, sticky='e')
        self.device_selector = ttk.Combobox(device_select_frame, state='readonly', font=('Arial', 10),
                                            bootstyle='primary')
        self.device_selector.grid(row=0, column=1, padx=5, sticky='ew')
        self.device_selector.bind('<<ComboboxSelected>>', self.master.data_processor._handle_x_device_selection)
        self.device_selector.bind('<<ComboboxSelected>>', self.master.data_processor._handle_y_device_selection)

        """axis_params_frame"""
        axis_params_frame = ttk.LabelFrame(left_frame, text='Параметры осей', padding=10, bootstyle='primary')
        axis_params_frame.grid(row=2, column=0, sticky='ew', pady=5)
        axis_params_frame.columnconfigure(0, weight=1)
        axis_params_frame.columnconfigure(1, weight=1)
        x_axis_frame = ttk.LabelFrame(axis_params_frame, text='Ось X', padding=5, bootstyle='primary')
        x_axis_frame.grid(row=0, column=0, padx=5, sticky='ew')
        self.x_axis_list = tk.Listbox(x_axis_frame, selectmode='single', width=25, height=6, exportselection=False,
                                      font=('Arial', 10))
        self.x_axis_list.pack(side='left', fill='y')
        x_scrollbar = ttk.Scrollbar(x_axis_frame, orient='vertical', command=self.x_axis_list.yview,
                                    bootstyle='primary')
        x_scrollbar.pack(side='right', fill='y')
        self.x_axis_list.config(yscrollcommand=x_scrollbar.set)
        y_axis_frame = ttk.LabelFrame(axis_params_frame, text='Ось Y', padding=5, bootstyle='primary')
        y_axis_frame.grid(row=0, column=1, padx=5, sticky='ew')
        self.y_axis_list = tk.Listbox(y_axis_frame, selectmode='extended', width=25, height=6, exportselection=False,
                                      font=('Arial', 10))
        self.y_axis_list.pack(side='left', fill='y')
        y_scrollbar = ttk.Scrollbar(y_axis_frame, orient='vertical', command=self.y_axis_list.yview,
                                    bootstyle='primary')
        y_scrollbar.pack(side='right', fill='y')
        self.y_axis_list.config(yscrollcommand=y_scrollbar.set)

        """settings_frame"""
        settings_frame = ttk.LabelFrame(right_frame, text='Настройки', padding=10, bootstyle='primary')
        settings_frame.grid(row=0, column=0, sticky='ew', pady=5)
        settings_frame.columnconfigure(0, weight=1)
        settings_frame.columnconfigure(1, weight=2)
        settings_frame.columnconfigure(2, weight=1)
        settings_frame.columnconfigure(3, weight=1)
        ttk.Checkbutton(settings_frame, text='Фильтр по дате', variable=self.master.filter_by_date,
                        command=self._toggle_date_filter, bootstyle='primary').grid(row=0, column=0, columnspan=4,
                                                                                    sticky='w', padx=5, pady=5)
        ttk.Label(settings_frame, text='С:').grid(row=1, column=0, sticky='e', padx=5, pady=2)
        self.start_datetime_selector = ttk.Combobox(settings_frame, state='disabled', font=('Arial', 10),
                                                    bootstyle='primary')
        self.start_datetime_selector.grid(row=1, column=1, padx=5, pady=2, sticky='ew')
        self.start_hour_entry = ttk.Entry(settings_frame, state='disabled', width=4, font=('Arial', 10))
        self.start_hour_entry.grid(row=1, column=2, padx=2, pady=2, sticky='e')
        self.start_minute_entry = ttk.Entry(settings_frame, state='disabled', width=4, font=('Arial', 10))
        self.start_minute_entry.grid(row=1, column=3, padx=2, pady=2, sticky='w')
        ttk.Label(settings_frame, text='По:').grid(row=2, column=0, sticky='e', padx=5, pady=2)
        self.end_datetime_selector = ttk.Combobox(settings_frame, state='disabled', font=('Arial', 10),
                                                  bootstyle='primary')
        self.end_datetime_selector.grid(row=2, column=1, padx=5, pady=2, sticky='ew')
        self.end_hour_entry = ttk.Entry(settings_frame, state='disabled', width=4, font=('Arial', 10))
        self.end_hour_entry.grid(row=2, column=2, padx=2, pady=2, sticky='e')
        self.end_minute_entry = ttk.Entry(settings_frame, state='disabled', width=4, font=('Arial', 10))
        self.end_minute_entry.grid(row=2, column=3, padx=2, pady=2, sticky='w')
        ttk.Checkbutton(settings_frame, text='ЭТ + Теплоощущение', variable=self.master.effective_temp_mode,
                        bootstyle='primary').grid(row=3, column=0, columnspan=4, sticky='w', padx=5, pady=5)
        ttk.Label(settings_frame, text='Температура:').grid(row=4, column=0, sticky='e', padx=5, pady=2)
        self.temp_selector = ttk.Combobox(settings_frame, state='readonly', width=15, font=('Arial', 10),
                                          bootstyle='primary')
        self.temp_selector.grid(row=4, column=1, padx=5, pady=2, sticky='ew')
        ttk.Label(settings_frame, text='Влажность:').grid(row=4, column=2, sticky='e', padx=5, pady=2)
        self.humidity_selector = ttk.Combobox(settings_frame, state='readonly', width=15, font=('Arial', 10),
                                              bootstyle='primary')
        self.humidity_selector.grid(row=4, column=3, padx=5, pady=2, sticky='ew')
        ttk.Checkbutton(settings_frame, text='Среднее за 1 ч', variable=self.master.avg_one_hour,
                        bootstyle='primary').grid(row=5, column=0, sticky='w', padx=5, pady=2)
        ttk.Checkbutton(settings_frame, text='Среднее за 3 ч', variable=self.master.avg_three_hours,
                        bootstyle='primary').grid(row=5, column=1, sticky='w', padx=5, pady=2)
        ttk.Checkbutton(settings_frame, text='Среднее за 1 д', variable=self.master.avg_one_day,
                        bootstyle='primary').grid(row=5, column=2, sticky='w', pady=2)
        ttk.Checkbutton(settings_frame, text='Мин/макс за 1 д', variable=self.master.min_max_daily,
                        bootstyle='primary').grid(row=5, column=3, sticky='w', padx=5, pady=2)

        """chart_type_frame"""
        chart_type_frame = ttk.LabelFrame(right_frame, text='Тип графика', padding=10, bootstyle='primary')
        chart_type_frame.grid(row=1, column=0, sticky='ew', pady=5)
        for label, value in [('Линейный', 'line'), ('Столбчатый', 'bar'), ('Точечная', 'scatter')]:
            ttk.Radiobutton(chart_type_frame, text=label, variable=self.master.chart_style, value=value,
                            bootstyle='primary').pack(side='left', padx=10, pady=5)

        """button_frame"""
        button_frame = ttk.Frame(right_frame, padding=10)
        button_frame.grid(row=2, column=0, sticky='ew', pady=5)
        ttk.Button(button_frame, text='Построить', command=self.master.data_processor.render_chart,
                   bootstyle='primary').grid(row=0, column=0, padx=5)

    def _configure_time_validation(self):
        hour_validator = (self.master.register(self._validate_hour), '%P')
        self.start_hour_entry.configure(validate='key', validatecommand=hour_validator)
        self.end_hour_entry.configure(validate='key', validatecommand=hour_validator)

        minute_validator = (self.master.register(self._validate_minute), '%P')
        self.start_minute_entry.configure(validate='key', validatecommand=minute_validator)
        self.end_minute_entry.configure(validate='key', validatecommand=minute_validator)

        self.start_hour_entry.bind('<FocusOut>', self._correct_hour)
        self.end_hour_entry.bind('<FocusOut>', self._correct_hour)
        self.start_minute_entry.bind('<FocusOut>', self._correct_minute)
        self.end_minute_entry.bind('<FocusOut>', self._correct_minute)

    @staticmethod
    def _validate_hour(value):
        if value == "":
            return True
        try:
            hour = int(value)
            return 0 <= hour <= 23
        except ValueError:
            return False

    @staticmethod
    def _validate_minute(value):
        if value == "":
            return True
        try:
            minute = int(value)
            return 0 <= minute <= 59
        except ValueError:
            return False

    @staticmethod
    def _correct_hour(event):
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

    @staticmethod
    def _correct_minute(event):
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

    def _toggle_date_filter(self):
        state_combobox = 'readonly' if self.master.filter_by_date.get() else 'disabled'
        state_entry = 'normal' if self.master.filter_by_date.get() else 'disabled'
        self.start_datetime_selector.config(state=state_combobox)
        self.end_datetime_selector.config(state=state_combobox)
        self.start_hour_entry.config(state=state_entry)
        self.start_minute_entry.config(state=state_entry)
        self.end_hour_entry.config(state=state_entry)
        self.end_minute_entry.config(state=state_entry)
