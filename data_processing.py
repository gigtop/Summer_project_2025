import tkinter as tk
import pandas as pd
import json
import time
import threading
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from tkinter import messagebox, filedialog
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.dates as mdates

class DataProcessor:
    def __init__(self, master):
        self.master = master
        self.master.chart_figure = go.Figure()
        self.loading_thread = None

    @staticmethod
    def _parse_datetime(date_combobox, hour_entry, minute_entry, min_datetime=None):
        try:
            date_str = date_combobox.get()
            if not date_str:
                return None
            year = min_datetime.year if min_datetime else pd.Timestamp.now().year
            date_struct = time.strptime(date_str, "%d-%m")
            hour = int(hour_entry.get()) if hour_entry.get() else 0
            minute = int(minute_entry.get()) if minute_entry.get() else 0
            return year, date_struct.tm_mon, date_struct.tm_mday, hour, minute
        except ValueError as e:
            print(
                f"Ошибка парсинга даты: {e}, date_str={date_str}, hour={hour_entry.get()}, minute={minute_entry.get()}")
            return None

    def _begin_json_load(self):
        self.master.gui.load_json_button.config(state='disabled')
        self.master.gui.loading_bar.grid()
        self.master.gui.loading_bar['value'] = 0
        threading.Thread(target=self._process_json_load, daemon=True).start()

    def _process_json_load(self):
        file_path = filedialog.askopenfilename(filetypes=[('JSON', '*.json;*.txt')])
        if not file_path:
            self.master.after(0, self._complete_load)
            return
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                json_data = json.load(file)
            temp_device_data = {}

            for num, value in enumerate(json_data.values()):
                value_num = num / len(json_data.values())
                self.master.after(0, lambda: self.master.gui.loading_bar.config(value=value_num * 100))
                if 'uName' not in value or 'serial' not in value or 'Date' not in value or 'data' not in value:
                    continue
                device_name = f"{value['uName']} ({value['serial']})"
                if device_name not in temp_device_data:
                    temp_device_data[device_name] = []
                record = {'Date': pd.to_datetime(value['Date'])}
                record.update(value['data'])
                temp_device_data[device_name].append(record)
            self.master.device_data = {
                name: pd.DataFrame(records).set_index('Date').apply(pd.to_numeric, errors='coerce').dropna(how='all')
                for name, records in temp_device_data.items()}
            if not self.master.device_data:
                raise ValueError("Нет данных для устройств")
            self.master.after(0, self._update_device_lists)
            self.master.after(0, lambda: messagebox.showinfo("Успех", f"JSON загружен: {file_path}"))
        except Exception as e:
            self.master.after(0, lambda: messagebox.showerror('Ошибка', str(e)))
        finally:
            self.master.after(0, self._complete_load)

    def _complete_load(self):
        self.master.gui.loading_bar.grid_remove()
        self.master.gui.load_json_button.config(state='normal')
        self.master.gui.loading_bar['value'] = 0

    def _update_device_lists(self):
        device_names = list(self.master.device_data.keys())
        self.master.gui.device_selector['values'] = device_names
        if device_names:
            self.master.gui.device_selector.set(device_names[0])
            self._handle_x_device_selection(None)
            self._handle_y_device_selection(None)

    def _handle_x_device_selection(self, event=None):
        """
        Событие <<ComboboxSelected>> автоматически передает объект события (event) как аргумент в привязанный метод.
        Соответственно метод _handle_x_device_selection определённый без параметра event выдаст ошибку.
        """
        selected_device = self.master.gui.device_selector.get()
        if selected_device in self.master.device_data:
            dataframe = self.master.device_data[selected_device]
            self.master.gui.x_axis_list.delete(0, 'end')
            self.master.gui.x_axis_list.insert('end', 'Date')
            for column in dataframe.columns:
                self.master.gui.x_axis_list.insert('end', column)
            self.master.gui.x_axis_list.selection_clear(0, 'end')
            self.master.gui.x_axis_list.selection_set(0)
            self.master.min_datetime = dataframe.index.min()
            self.master.max_datetime = dataframe.index.max()
            if self.master.min_datetime and self.master.max_datetime:
                date_range = pd.date_range(start=self.master.min_datetime, end=self.master.max_datetime, freq='D')
                date_strs = [dt.strftime("%d-%m") for dt in date_range]
                self.master.gui.start_datetime_selector['values'] = date_strs
                self.master.gui.end_datetime_selector['values'] = date_strs
                self.master.gui.start_datetime_selector.set(self.master.min_datetime.strftime("%d-%m"))
                self.master.gui.end_datetime_selector.set(self.master.max_datetime.strftime("%d-%m"))
                self.master.gui.start_hour_entry.delete(0, 'end')
                self.master.gui.start_hour_entry.insert(0, self.master.min_datetime.strftime("%H"))
                self.master.gui.start_minute_entry.delete(0, 'end')
                self.master.gui.start_minute_entry.insert(0, self.master.min_datetime.strftime("%M"))
                self.master.gui.end_hour_entry.delete(0, 'end')
                self.master.gui.end_hour_entry.insert(0, self.master.max_datetime.strftime("%H"))
                self.master.gui.end_minute_entry.delete(0, 'end')
                self.master.gui.end_minute_entry.insert(0, self.master.max_datetime.strftime("%M"))

    def _handle_y_device_selection(self, event=None):
        """
        Событие <<ComboboxSelected>> автоматически передает объект события (event) как аргумент в привязанный метод.
        Соответственно метод _handle_y_device_selection определённый без параметра event выдаст ошибку.
        """
        selected_y_device = self.master.gui.device_selector.get()
        if selected_y_device in self.master.device_data:
            self.master.gui.device_selector.set(selected_y_device)
            self._handle_x_device_selection(None)
            dataframe = self.master.device_data[selected_y_device]
            numeric_columns = [col for col in dataframe.columns if pd.api.types.is_numeric_dtype(dataframe[col])]
            self.master.gui.y_axis_list.delete(0, 'end')
            for col in numeric_columns:
                self.master.gui.y_axis_list.insert('end', col)
            temp_priority = ['weather_temp', 'BME280_temp', 'temperature']
            humidity_priority = ['weather_humidity', 'BME280_humidity', 'humidity']
            temp_candidates = [col for col in temp_priority if col in numeric_columns] + [col for col in numeric_columns
                                                                                          if col not in temp_priority]
            humidity_candidates = [col for col in humidity_priority if col in numeric_columns] + [col for col in
                                                                                                  numeric_columns if
                                                                                                  col not in humidity_priority]
            self.master.gui.temp_selector['values'] = temp_candidates
            self.master.gui.humidity_selector['values'] = humidity_candidates
            default_temp = next((col for col in temp_priority if col in numeric_columns),
                                temp_candidates[0] if temp_candidates else None)
            if default_temp:
                self.master.gui.temp_selector.set(default_temp)
            default_humidity = next((col for col in humidity_priority if col in numeric_columns),
                                    humidity_candidates[0] if humidity_candidates else None)
            if default_humidity:
                self.master.gui.humidity_selector.set(default_humidity)

    def clear_chart(self):
        self.master.chart_figure.data = []
        self.master.chart_figure.layout = go.Layout()
        if self.master.chart_display:
            self.master.chart_display.destroy()
            self.master.chart_display = None
        if self.master.chart_canvas:
            self.master.chart_canvas.get_tk_widget().destroy()
            self.master.chart_canvas = None
        if self.master.matplotlib_figure:
            plt.close(self.master.matplotlib_figure)
            self.master.matplotlib_figure = None

    @staticmethod
    def _classify_sensation(effective_temp):
        if pd.isna(effective_temp):
            return None
        thresholds = [(30, 'Очень жарко'), (24, 'Жарко'), (18, 'Тепло'), (12, 'Умеренно тепло'),
                      (6, 'Прохладно'), (0, 'Умеренно холодно'), (-12, 'Холодно'), (-24, 'Очень холодно')]
        for threshold, sensation in thresholds:
            if effective_temp >= threshold:
                return sensation
        return 'Крайне холодно'

    def _get_selected_device_and_parameters(self):
        device = self.master.gui.device_selector.get()
        if not device or device not in self.master.device_data:
            messagebox.showwarning('Нет устройства', 'Выберите устройство.')
            return None, None, None
        x_selection = self.master.gui.x_axis_list.curselection()
        if not x_selection:
            messagebox.showwarning('Нет полей', 'Выберите поле для оси X.')
            return None, None, None
        x_parameter = self.master.gui.x_axis_list.get(x_selection[0])
        y_parameters = [self.master.gui.y_axis_list.get(i) for i in
                        self.master.gui.y_axis_list.curselection()] if self.master.gui.y_axis_list.curselection() else []
        return device, x_parameter, y_parameters

    def _filter_data_by_date(self, data, start_datetime, end_datetime):
        if not self.master.filter_by_date.get():
            return data
        if not start_datetime or not end_datetime:
            messagebox.showerror('Ошибка', 'Некорректный формат даты/времени.')
            return None
        start_timestamp = pd.Timestamp(year=start_datetime[0], month=start_datetime[1], day=start_datetime[2],
                                      hour=start_datetime[3], minute=start_datetime[4])
        end_timestamp = pd.Timestamp(year=end_datetime[0], month=end_datetime[1], day=end_datetime[2],
                                    hour=end_datetime[3], minute=end_datetime[4])
        if start_timestamp < self.master.min_datetime:
            start_timestamp = self.master.min_datetime
        if end_timestamp > self.master.max_datetime:
            end_timestamp = self.master.max_datetime
        if start_timestamp > end_timestamp:
            messagebox.showerror('Ошибка', 'Неверный временной диапазон.')
            return None
        return data[(data.index >= start_timestamp) & (data.index <= end_timestamp)]

    def _calculate_effective_temperature(self, data, temp_column, humidity_column):
        if not temp_column or not humidity_column:
            messagebox.showwarning('Ошибка', 'Выберите температуру и влажность.')
            return None, None
        if temp_column not in data.columns or humidity_column not in data.columns:
            messagebox.showerror('Ошибка', 'Выбранные параметры температуры или влажности отсутствуют в данных.')
            return None, None
        temperature = data[temp_column]
        humidity = data[humidity_column]
        effective_temp = temperature - 0.4 * (temperature - 10) * (1 - humidity / 100)
        if effective_temp.isna().all():
            messagebox.showerror('Ошибка', 'Невозможно вычислить эффективную температуру: данные содержат только NaN.')
            return None, None
        return effective_temp, effective_temp.apply(self._classify_sensation)

    def _create_chart_window(self, title):
        self.clear_chart()
        self.master.chart_display = tk.Toplevel(self.master)
        self.master.chart_display.protocol("WM_DELETE_WINDOW", self.clear_chart)
        self.master.chart_display.title(title)
        self.master.chart_display.geometry("800x600")
        self.master.matplotlib_figure = plt.figure(figsize=(8, 6))



    def _add_effective_temp_traces(self, chart_type, effective_temp, sensation, device):

        if effective_temp.empty:
            messagebox.showerror('Ошибка', 'Нет валидных данных для построения графика теплоощущения.')
            self.clear_chart()
            return

        unique_sensations = sensation.dropna().unique()
        self._create_chart_window("График")

        for category in unique_sensations:
            mask = sensation == category
            x_values = effective_temp.index[mask]
            y_values = effective_temp[mask]

            trace_label = f'{category} ({device})'
            if chart_type == 'line':
                self.master.chart_figure.add_trace(go.Scatter(
                    x=x_values,
                    y=y_values,
                    mode='lines',
                    line=dict(width=2, color=self.master.sensation_colors.get(category, '#000000')),
                    name=trace_label
                ))
            elif chart_type == 'bar':
                self.master.chart_figure.add_trace(go.Bar(
                    x=x_values,
                    y=y_values,
                    marker=dict(color=self.master.sensation_colors.get(category, '#000000')),
                    name=trace_label
                ))
            elif chart_type == 'scatter':
                self.master.chart_figure.add_trace(go.Scatter(
                    x=x_values,
                    y=y_values,
                    mode='markers',
                    marker=dict(
                        size=8,
                        color=self.master.sensation_colors.get(category, '#000000'),
                        opacity=0.7
                    ),
                    name=trace_label
                ))

        self.master.chart_figure.update_layout(
            yaxis_title='Эф. температура (°C)',
            title=dict(text=f'ЭТ и Теплоощущение\nПрибор: {device}', font=dict(size=16)),
            template='plotly_white',
            margin=dict(t=100),
            hovermode='x unified',
            plot_bgcolor='white',
            paper_bgcolor='white',
            xaxis_rangeslider_visible=True,
            xaxis=dict(
                title='Дата',
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

    def _add_regular_traces(self, chart_type, x_data, y_data, x_parameter, y_parameters, device):
        x_values = x_data[x_parameter] if x_parameter != 'Date' else x_data.index
        for column in y_parameters:
            trace_label = f'{column} ({device})'
            if chart_type == 'line':
                self.master.chart_figure.add_trace(
                    go.Scatter(x=x_values, y=y_data[column], mode='lines', line=dict(width=2), name=trace_label))
            elif chart_type == 'bar':
                self.master.chart_figure.add_trace(go.Bar(x=x_values, y=y_data[column],
                                                          name=trace_label, width=0.1))

            elif chart_type == 'scatter':
                self.master.chart_figure.add_trace(
                    go.Scatter(x=x_values, y=y_data[column], mode='markers', marker=dict(size=8, opacity=0.7),
                               name=trace_label))


        if any([self.master.avg_one_hour.get(), self.master.avg_three_hours.get(),
                self.master.avg_one_day.get(), self.master.min_max_daily.get()]):
            resampled_data = y_data[y_parameters].copy()
            if not resampled_data.empty:
                last_row = resampled_data.iloc[-1].copy()
                last_timestamp = resampled_data.index[-1]
                new_timestamp = last_timestamp + pd.Timedelta(minutes=1 if len(resampled_data) <= 1 else min(
                    (resampled_data.index[1:] - resampled_data.index[:-1]).total_seconds() / 60))
                last_row.name = new_timestamp
                resampled_data = pd.concat([resampled_data, last_row.to_frame().T])
            if self.master.avg_one_hour.get():
                resampled_one_hour = resampled_data.resample('1h').mean()
                for column in y_parameters:
                    self.master.chart_figure.add_trace(
                        go.Scatter(x=resampled_one_hour.index, y=resampled_one_hour[column], mode='lines',
                                   line=dict(dash='dash', width=1.5, shape='hv'), name=f'{column} 1ч ({device})'))
            if self.master.avg_three_hours.get():
                resampled_three_hours = resampled_data.resample('3h').mean()
                for column in y_parameters:
                    self.master.chart_figure.add_trace(
                        go.Scatter(x=resampled_three_hours.index, y=resampled_three_hours[column], mode='lines',
                                   line=dict(dash='dot', width=1.5, shape='hv'), name=f'{column} 3ч ({device})'))
            if self.master.avg_one_day.get():
                resampled_one_day = resampled_data.resample('D').mean()
                for column in y_parameters:
                    if not resampled_one_day[column].dropna().empty:
                        self.master.chart_figure.add_trace(
                            go.Scatter(x=resampled_one_day.index, y=resampled_one_day[column], mode='lines',
                                       line=dict(dash='dashdot', width=1.5, shape='hv'), name=f'{column} 1д ({device})'))
            if self.master.min_max_daily.get():
                daily_min = resampled_data.resample('D').min()
                daily_max = resampled_data.resample('D').max()
                for col in y_parameters:
                    if not daily_min[col].dropna().empty:
                        #Следующая строка нужна для правильной min линии
                        if resampled_data.index[-1].strftime('%H:%M:%S') > "01:00:00":
                            daily_min = pd.concat([daily_min, pd.DataFrame({col: [daily_min[col].iloc[-1]]}, index=[
                                daily_min.index[-1] + pd.Timedelta(days=1)])])
                        self.master.chart_figure.add_trace(
                            go.Scatter(x=daily_min.index, y=daily_min[col], mode='lines',
                                       line=dict(dash='dash', width=1, color='blue'), name=f'{col} min 1д ({device})'))
                    if not daily_max[col].dropna().empty:
                        # Следующая строка нужна для правильной max линии
                        if resampled_data.index[-1].strftime('%H:%M:%S') > "01:00:00":
                            daily_max = pd.concat([daily_max, pd.DataFrame({col: [daily_max[col].iloc[-1]]}, index=[
                            daily_max.index[-1] + pd.Timedelta(days=1)])])
                        print([index for index in daily_max.index])
                        self.master.chart_figure.add_trace(
                            go.Scatter(x=daily_max.index, y=daily_max[col], mode='lines',
                                       line=dict(dash='solid', width=1, color='red'), name=f'{col} max 1д ({device})'))

    def _render_matplotlib(self, x_parameter, device):
        for trace in self.master.chart_figure.data:
            label = trace['name'] if trace['name'] else 'Unnamed'
            if trace['type'] == 'scatter' and trace['mode'] == 'markers':
                plt.scatter(
                    trace['x'],
                    trace['y'],
                    label=label,
                    s=64,
                    alpha=0.7,
                    color=trace['marker']['color'] if 'marker' in trace and 'color' in trace['marker'] else None
                )
            elif trace['type'] == 'scatter' and trace['mode'] == 'lines':
                if '1ч' in label or '3ч' in label or '1д' in label:
                    plt.step(
                        trace['x'],
                        trace['y'],
                        label=label,
                        color=trace['line']['color'] if 'line' in trace and 'color' in trace['line'] else None,
                        where='post'
                    )
                else:
                    plt.plot(
                        trace['x'],
                        trace['y'],
                        label=label,
                        color=trace['line']['color'] if 'line' in trace and 'color' in trace['line'] else None
                    )
            elif trace['type'] == 'bar':
                plt.bar(
                    trace['x'],
                    trace['y'],
                    label=label,
                    color=trace['marker']['color'] if 'marker' in trace and 'color' in trace['marker'] else None
                )
        plt.xlabel(x_parameter if x_parameter != 'Date' else 'Дата')
        plt.ylabel('Значение')
        plt.title(f'График\nПрибор: {device}')
        plt.grid(True)
        if x_parameter == 'Date':
            plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
            plt.gca().xaxis.set_major_locator(mdates.AutoDateLocator())
            plt.xticks(rotation=45)
        if plt.gca().get_legend_handles_labels()[0]:
            plt.legend()
        self.master.chart_canvas = FigureCanvasTkAgg(self.master.matplotlib_figure, master=self.master.chart_display)
        self.master.chart_canvas.draw()
        self.master.chart_canvas.get_tk_widget().grid(row=0, column=0, sticky='nsew')
        self.master.chart_display.grid_rowconfigure(0, weight=1)
        self.master.chart_display.grid_columnconfigure(0, weight=1)

    def render_chart(self):
        # Получение выбранного устройства и параметров
        device, x_parameter, y_parameters = self._get_selected_device_and_parameters()
        if not device:
            return

        # Подготовка данных
        data = self.master.device_data[device].copy()
        chart_type = self.master.chart_style.get()

        # Фильтрация данных по времени
        if self.master.filter_by_date.get():
            start_datetime = self._parse_datetime(self.master.gui.start_datetime_selector,
                                                  self.master.gui.start_hour_entry, self.master.gui.start_minute_entry)
            end_datetime = self._parse_datetime(self.master.gui.end_datetime_selector,
                                                self.master.gui.end_hour_entry, self.master.gui.end_minute_entry)
            filtered_data = self._filter_data_by_date(data, start_datetime, end_datetime)
            if filtered_data is None:
                return
            data = filtered_data
            data = data.loc[data.index.intersection(data.index)]  # Синхронизация индексов

        # Проверка параметров Y в обычном режиме
        if not self.master.effective_temp_mode.get() and not y_parameters:
            messagebox.showwarning('Нет полей', 'Выберите поля для оси Y.')
            return

        # Проверка данных для эффективной температуры
        if self.master.effective_temp_mode.get():
            effective_temp, sensation = self._calculate_effective_temperature(
                data, self.master.gui.temp_selector.get(), self.master.gui.humidity_selector.get())
            if effective_temp is None:
                return
            valid_data = effective_temp.dropna()
            valid_sensation = sensation[effective_temp.notna()]
            if valid_data.empty:
                messagebox.showerror('Ошибка', 'Нет валидных данных для построения графика теплоощущения.')
                return

        # Создание окна графика только после всех проверок
        self._create_chart_window("График")

        # Режим эффективной температуры
        if self.master.effective_temp_mode.get():
            self._add_effective_temp_traces(chart_type, valid_data, valid_sensation, device)
        else:
            self._add_regular_traces(chart_type, data, data, x_parameter, y_parameters, device)
            self.master.chart_figure.update_layout(
                yaxis_title='Значение',
                title=dict(text=f'График данных\nПрибор: {device}', font=dict(size=16)),
                template='plotly_white', margin=dict(t=100), hovermode='x unified', plot_bgcolor='white',
                paper_bgcolor='white',
                xaxis_rangeslider_visible=True,
                xaxis=dict(title=x_parameter if x_parameter != 'Date' else 'Дата', showline=True, linecolor='black',
                           linewidth=1, mirror=True,
                           showgrid=True, gridcolor='lightgrey', gridwidth=1, griddash='dot'),
                yaxis=dict(showline=True, linecolor='black', linewidth=1, mirror=True, showgrid=True,
                           gridcolor='lightgrey', gridwidth=1, griddash='dot'))

        # Отрисовка графика в matplotlib
        if self.master.chart_figure.data:
            self._render_matplotlib(x_parameter, device)

