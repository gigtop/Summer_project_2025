import json
import unittest
import tkinter as tk
from unittest.mock import mock_open, patch, MagicMock
import ttkbootstrap as ttk
import pandas as pd
import plotly.graph_objects as go

from main import ChartApp
from gui import ChartAppGUI
from data_processing import DataProcessor


class TestChartApp(unittest.TestCase):
    def setUp(self):
        # Setup ChartApp
        self.chart_app = ChartApp()

        # Setup GUI
        self.chart_app_gui = ChartAppGUI(self.chart_app)

        # Setup DataProcessor
        self.root = tk.Tk()
        self.mock_app = MagicMock()
        self.mock_app.gui = MagicMock()
        self.mock_app.device_data = {}
        self.mock_app.filter_by_date = tk.BooleanVar(value=False)
        self.mock_app.effective_temp_mode = tk.BooleanVar(value=False)
        self.mock_app.avg_one_hour = tk.BooleanVar(value=False)
        self.mock_app.avg_three_hours = tk.BooleanVar(value=False)
        self.mock_app.avg_one_day = tk.BooleanVar(value=False)
        self.mock_app.min_max_daily = tk.BooleanVar(value=False)
        self.mock_app.chart_style = tk.StringVar(value="line")
        self.mock_app.min_datetime = None
        self.mock_app.max_datetime = None
        self.mock_app.chart_figure = None
        self.mock_app.chart_display = None
        self.mock_app.chart_canvas = None
        self.mock_app.matplotlib_figure = None
        self.mock_app.sensation_colors = {
            'Крайне холодно': '#000080', 'Очень холодно': '#0000FF', 'Холодно': '#87CEFA',
            'Умеренно холодно': '#ADD8E6', 'Прохладно': '#008000', 'Умеренно тепло': '#9ACD32',
            'Тепло': '#FFD700', 'Жарко': '#FF8C00', 'Очень жарко': '#FF0000'
        }
        self.processor = DataProcessor(self.mock_app)


    # ==TestChartAppMain==
    def test_initialization_main(self):
        """TitleBar"""
        self.assertEqual(self.chart_app.title(), "Calculus Graphicus")
        self.assertEqual(self.chart_app.geometry().split('+')[0], "1200x400")
        self.assertFalse(self.chart_app.resizable()[0])
        self.assertFalse(self.chart_app.resizable()[1])

        """Device data"""
        self.assertIsInstance(self.chart_app.device_data, dict)

        """Flags"""
        self.assertIsInstance(self.chart_app.filter_by_date, tk.BooleanVar)
        self.assertIsInstance(self.chart_app.effective_temp_mode, tk.BooleanVar)
        self.assertIsInstance(self.chart_app.avg_one_hour, tk.BooleanVar)
        self.assertIsInstance(self.chart_app.avg_three_hours, tk.BooleanVar)
        self.assertIsInstance(self.chart_app.avg_one_day, tk.BooleanVar)
        self.assertIsInstance(self.chart_app.min_max_daily, tk.BooleanVar)
        self.assertIsInstance(self.chart_app.chart_style, tk.StringVar)

        """Chart Flags"""
        self.assertEqual(self.chart_app.chart_style.get(), "line")
        self.assertIsNone(self.chart_app.min_datetime)
        self.assertIsNone(self.chart_app.max_datetime)
        self.assertIsNone(self.chart_app.chart_display)
        self.assertIsNone(self.chart_app.chart_canvas)
        self.assertIsNone(self.chart_app.matplotlib_figure)

        self.assertIsInstance(self.chart_app.sensation_colors, dict)
        self.assertEqual(len(self.chart_app.sensation_colors), 9)

    def test_on_closing(self):
        self.chart_app.data_processor.clear_chart = lambda: None
        self.chart_app._on_closing()

    # ==TestChartAppGUI==
    def test_initialization_gui(self):
        """Flags"""
        self.assertIsInstance(self.chart_app_gui.master, ChartApp)
        self.assertIsNotNone(self.chart_app_gui.device_selector)
        self.assertIsNotNone(self.chart_app_gui.start_datetime_selector)
        self.assertIsNotNone(self.chart_app_gui.end_datetime_selector)
        self.assertIsNotNone(self.chart_app_gui.start_hour_entry)
        self.assertIsNotNone(self.chart_app_gui.start_minute_entry)
        self.assertIsNotNone(self.chart_app_gui.end_hour_entry)
        self.assertIsNotNone(self.chart_app_gui.end_minute_entry)
        self.assertIsNotNone(self.chart_app_gui.x_axis_list)
        self.assertIsNotNone(self.chart_app_gui.y_axis_list)
        self.assertIsNotNone(self.chart_app_gui.temp_selector)
        self.assertIsNotNone(self.chart_app_gui.humidity_selector)
        self.assertIsNotNone(self.chart_app_gui.load_json_button)
        self.assertIsNotNone(self.chart_app_gui.loading_bar)

    def test_initialize_widgets(self):
        """Styles ttkbootstrap"""
        style = ttk.Style()
        self.assertEqual(style.theme.name, "litera")
        self.assertEqual(style.lookup("TButton", "font"), "Arial 10")
        self.assertEqual(style.lookup("TButton", "padding"), 8)
        self.assertEqual(style.lookup("TButton", "borderadius"), 15)
        self.assertEqual(style.lookup("TLabel", "font"), "Arial 10")
        self.assertEqual(style.lookup("TCheckbutton", "font"), "Arial 10")
        self.assertEqual(style.lookup("TRadiobutton", "font"), "Arial 10")
        self.assertEqual(style.lookup("TLabelframe", "font"), "Arial 11 bold")
        self.assertEqual(style.lookup("TLabelframe.Label", "font"), "Arial 11 bold")

        """Creating and placing frames"""
        primary_frame = self.chart_app_gui.master.winfo_children()[0]
        self.assertIsInstance(primary_frame, ttk.Frame)
        self.assertEqual(primary_frame.grid_info()["row"], 0)
        self.assertEqual(primary_frame.grid_info()["column"], 0)
        self.assertEqual(primary_frame.grid_info()["sticky"], "nesw")

        left_frame = primary_frame.winfo_children()[0]
        right_frame = primary_frame.winfo_children()[1]
        self.assertIsInstance(left_frame, ttk.Frame)
        self.assertIsInstance(right_frame, ttk.Frame)
        self.assertEqual(left_frame.grid_info()["sticky"], "nsw")
        self.assertEqual(right_frame.grid_info()["sticky"], "nesw")

        """data load frame"""
        data_load_frame = left_frame.winfo_children()[0]
        self.assertIsInstance(data_load_frame, ttk.LabelFrame)
        self.assertEqual(data_load_frame.cget("text"), "Загрузка данных")
        self.assertEqual(data_load_frame.grid_info()["row"], 0)
        self.assertEqual(data_load_frame.grid_info()["column"], 0)

        """load_json_button and loading_bar"""
        self.assertIsInstance(self.chart_app_gui.load_json_button, ttk.Button)
        self.assertEqual(self.chart_app_gui.load_json_button.cget("text"), "Загрузить JSON")
        self.assertEqual(self.chart_app_gui.load_json_button.grid_info()["row"], 0)
        self.assertEqual(self.chart_app_gui.load_json_button.grid_info()["column"], 0)
        self.assertIsInstance(self.chart_app_gui.loading_bar, ttk.Progressbar)
        self.assertEqual(str(self.chart_app_gui.loading_bar.cget("orient")), "horizontal")
        self.assertEqual(str(self.chart_app_gui.loading_bar.cget("mode")), "determinate")
        self.assertFalse(self.chart_app_gui.loading_bar.winfo_ismapped())

        """device_select_frame"""
        device_select_frame = left_frame.winfo_children()[1]
        self.assertIsInstance(device_select_frame, ttk.LabelFrame)
        self.assertEqual(device_select_frame.cget("text"), "Выбор устройств")
        self.assertIsInstance(self.chart_app_gui.device_selector, ttk.Combobox)
        self.assertEqual(str(self.chart_app_gui.device_selector.cget("state")), "readonly")
        self.assertEqual(self.chart_app_gui.device_selector.grid_info()["row"], 0)
        self.assertEqual(self.chart_app_gui.device_selector.grid_info()["column"], 1)

        """axis_params_frame"""
        axis_params_frame = left_frame.winfo_children()[2]
        self.assertIsInstance(axis_params_frame, ttk.LabelFrame)
        self.assertEqual(axis_params_frame.cget("text"), "Параметры осей")
        x_axis_frame = axis_params_frame.winfo_children()[0]
        y_axis_frame = axis_params_frame.winfo_children()[1]
        self.assertEqual(x_axis_frame.cget("text"), "Ось X")
        self.assertEqual(y_axis_frame.cget("text"), "Ось Y")
        self.assertIsInstance(self.chart_app_gui.x_axis_list, tk.Listbox)
        self.assertEqual(self.chart_app_gui.x_axis_list.cget("selectmode"), "single")
        self.assertIsInstance(self.chart_app_gui.y_axis_list, tk.Listbox)
        self.assertEqual(self.chart_app_gui.y_axis_list.cget("selectmode"), "extended")

        """settings_frame"""
        settings_frame = right_frame.winfo_children()[0]
        self.assertIsInstance(settings_frame, ttk.LabelFrame)
        self.assertEqual(settings_frame.cget("text"), "Настройки")
        self.assertIsInstance(self.chart_app_gui.start_datetime_selector, ttk.Combobox)
        self.assertEqual(str(self.chart_app_gui.start_datetime_selector.cget("state")), "disabled")
        self.assertIsInstance(self.chart_app_gui.start_hour_entry, ttk.Entry)
        self.assertEqual(str(self.chart_app_gui.start_hour_entry.cget("state")), "disabled")
        self.assertIsInstance(self.chart_app_gui.temp_selector, ttk.Combobox)
        self.assertEqual(str(self.chart_app_gui.temp_selector.cget("state")), "readonly")

        """chart_type_frame"""
        chart_type_frame = right_frame.winfo_children()[1]
        self.assertIsInstance(chart_type_frame, ttk.LabelFrame)
        self.assertEqual(chart_type_frame.cget("text"), "Тип графика")
        radiobuttons = chart_type_frame.winfo_children()
        self.assertEqual(len(radiobuttons), 3)
        self.assertEqual(radiobuttons[0].cget("text"), "Линейный")
        self.assertEqual(radiobuttons[1].cget("text"), "Столбчатый")
        self.assertEqual(radiobuttons[2].cget("text"), "Точечная")

        """button_frame"""
        button_frame = right_frame.winfo_children()[2]
        self.assertIsInstance(button_frame, ttk.Frame)
        build_button = button_frame.winfo_children()[0]
        self.assertIsInstance(build_button, ttk.Button)
        self.assertEqual(build_button.cget("text"), "Построить")

    def test_configure_time_validation(self):
        self.assertEqual(self.chart_app_gui.start_hour_entry.cget("validate"), "key")
        self.assertIsNotNone(self.chart_app_gui.start_hour_entry.cget("validatecommand"))
        self.assertEqual(self.chart_app_gui.end_hour_entry.cget("validate"), "key")
        self.assertIsNotNone(self.chart_app_gui.end_hour_entry.cget("validatecommand"))
        self.assertEqual(self.chart_app_gui.start_minute_entry.cget("validate"), "key")
        self.assertIsNotNone(self.chart_app_gui.start_minute_entry.cget("validatecommand"))
        self.assertEqual(self.chart_app_gui.end_minute_entry.cget("validate"), "key")
        self.assertIsNotNone(self.chart_app_gui.end_minute_entry.cget("validatecommand"))

        start_hour_bindings = self.chart_app_gui.start_hour_entry.bind()
        end_hour_bindings = self.chart_app_gui.end_hour_entry.bind()
        start_minute_bindings = self.chart_app_gui.start_minute_entry.bind()
        end_minute_bindings = self.chart_app_gui.end_minute_entry.bind()

        self.assertIn("<FocusOut>", start_hour_bindings)
        self.assertIn("<FocusOut>", end_hour_bindings)
        self.assertIn("<FocusOut>", start_minute_bindings)
        self.assertIn("<FocusOut>", end_minute_bindings)

    def test_time_validation_hour(self):
        self.assertTrue(self.chart_app_gui._validate_hour(""))
        self.assertTrue(self.chart_app_gui._validate_hour("0"))
        self.assertTrue(self.chart_app_gui._validate_hour("23"))
        self.assertFalse(self.chart_app_gui._validate_hour("24"))
        self.assertFalse(self.chart_app_gui._validate_hour("abc"))

    def test_time_validation_minute(self):
        self.assertTrue(self.chart_app_gui._validate_minute(""))
        self.assertTrue(self.chart_app_gui._validate_minute("0"))
        self.assertTrue(self.chart_app_gui._validate_minute("59"))
        self.assertFalse(self.chart_app_gui._validate_minute("60"))
        self.assertFalse(self.chart_app_gui._validate_minute("abc"))

    def test_correct_hour(self):
        event = tk.Event()
        event.widget = self.chart_app_gui.start_hour_entry

        self.chart_app_gui.start_hour_entry.delete(0, tk.END)
        self.chart_app_gui.start_hour_entry.insert(0, "")
        self.chart_app_gui._correct_hour(event)
        self.assertEqual(self.chart_app_gui.start_hour_entry.get(), "")

        self.chart_app_gui.start_hour_entry.delete(0, tk.END)
        self.chart_app_gui.start_hour_entry.insert(0, "24")
        self.chart_app_gui._correct_hour(event)
        self.assertEqual(self.chart_app_gui.start_hour_entry.get(), "")

        self.chart_app_gui.start_hour_entry.delete(0, tk.END)
        self.chart_app_gui.start_hour_entry.insert(0, "abc")
        self.chart_app_gui._correct_hour(event)
        self.assertEqual(self.chart_app_gui.start_hour_entry.get(), "")

    def test_correct_minute(self):
        event = tk.Event()
        event.widget = self.chart_app_gui.start_minute_entry

        self.chart_app_gui.start_minute_entry.delete(0, tk.END)
        self.chart_app_gui.start_minute_entry.insert(0, "")
        self.chart_app_gui._correct_minute(event)
        self.assertEqual(self.chart_app_gui.start_minute_entry.get(), "")

        self.chart_app_gui.start_minute_entry.delete(0, tk.END)
        self.chart_app_gui.start_minute_entry.insert(0, "60")
        self.chart_app_gui._correct_minute(event)
        self.assertEqual(self.chart_app_gui.start_minute_entry.get(), "")

        self.chart_app_gui.start_minute_entry.delete(0, tk.END)
        self.chart_app_gui.start_minute_entry.insert(0, "abc")
        self.chart_app_gui._correct_minute(event)
        self.assertEqual(self.chart_app_gui.start_minute_entry.get(), "")

    def test_toggle_date_filter(self):
        self.chart_app_gui.master.filter_by_date.set(True)
        self.chart_app_gui._toggle_date_filter()
        self.assertEqual(str(self.chart_app_gui.start_datetime_selector.cget("state")), "readonly")
        self.assertEqual(str(self.chart_app_gui.start_hour_entry.cget("state")), "normal")

        self.chart_app_gui.master.filter_by_date.set(False)
        self.chart_app_gui._toggle_date_filter()
        self.assertEqual(str(self.chart_app_gui.start_datetime_selector.cget("state")), "disabled")
        self.assertEqual(str(self.chart_app_gui.start_hour_entry.cget("state")), "disabled")

    # ==TestDataProcessor==
    def test_parse_datetime(self):
        self.mock_app.gui.start_datetime_selector.get.return_value = "01-01"
        self.mock_app.gui.start_hour_entry.get.return_value = "12"
        self.mock_app.gui.start_minute_entry.get.return_value = "30"
        result = self.processor._parse_datetime(
            self.mock_app.gui.start_datetime_selector,
            self.mock_app.gui.start_hour_entry,
            self.mock_app.gui.start_minute_entry
        )
        self.assertEqual(result, (2025, 1, 1, 12, 30))

        self.mock_app.gui.start_datetime_selector.get.return_value = "invalid"
        result = self.processor._parse_datetime(
            self.mock_app.gui.start_datetime_selector,
            self.mock_app.gui.start_hour_entry,
            self.mock_app.gui.start_minute_entry
        )
        self.assertIsNone(result)

    def test_classify_sensation(self):
        self.assertEqual(self.processor._classify_sensation(31), "Очень жарко")
        self.assertEqual(self.processor._classify_sensation(25), "Жарко")
        self.assertEqual(self.processor._classify_sensation(20), "Тепло")
        self.assertEqual(self.processor._classify_sensation(15), "Умеренно тепло")
        self.assertEqual(self.processor._classify_sensation(10), "Прохладно")
        self.assertEqual(self.processor._classify_sensation(3), "Умеренно холодно")
        self.assertEqual(self.processor._classify_sensation(-10), "Холодно")
        self.assertEqual(self.processor._classify_sensation(-20), "Очень холодно")
        self.assertEqual(self.processor._classify_sensation(-30), "Крайне холодно")
        self.assertIsNone(self.processor._classify_sensation(float("nan")))

    #Отсюда тесты без последовательности
    def test_process_json_load(self):
        mock_data = {
            "device1": {
                "uName": "Test Device",
                "serial": "12345",
                "Date": "2023-01-01 12:00:00",
                "data": {"weather_temp": 20.5, "weather_humidity": 60.0}
            }
        }
        with patch('builtins.open', mock_open(read_data=json.dumps(mock_data))):
            with patch('tkinter.filedialog.askopenfilename', return_value='test.json'):
                with patch.object(self.mock_app, 'after') as mock_after:
                    self.processor._process_json_load()
                    self.assertTrue(mock_after.called)
                    self.assertEqual(len(self.mock_app.device_data), 1)

    # ==TestDataProcessorNewMethods==
    def test_get_selected_device_and_parameters(self):
        self.mock_app.gui.device_selector.get.return_value = "Test Device (12345)"
        self.mock_app.device_data = {"Test Device (12345)": pd.DataFrame()}
        self.mock_app.gui.x_axis_list.curselection.return_value = (0,)
        self.mock_app.gui.x_axis_list.get.return_value = "Date"
        self.mock_app.gui.y_axis_list.curselection.return_value = (0, 1)
        self.mock_app.gui.y_axis_list.get.side_effect = ["weather_temp", "weather_humidity"]
        device, x_param, y_params = self.processor._get_selected_device_and_parameters()
        self.assertEqual(device, "Test Device (12345)")
        self.assertEqual(x_param, "Date")
        self.assertEqual(y_params, ["weather_temp", "weather_humidity"])
        self.mock_app.gui.device_selector.get.return_value = ""
        device, x_param, y_params = self.processor._get_selected_device_and_parameters()
        self.assertIsNone(device)
        self.assertIsNone(x_param)
        self.assertIsNone(y_params)
        self.mock_app.gui.device_selector.get.return_value = "Test Device (12345)"
        self.mock_app.gui.x_axis_list.curselection.return_value = ()
        device, x_param, y_params = self.processor._get_selected_device_and_parameters()
        self.assertIsNone(device)
        self.assertIsNone(x_param)
        self.assertIsNone(y_params)

    def test_filter_data_by_date(self):
        data = pd.DataFrame(
            {"weather_temp": [20, 21, 22]},
            index=pd.to_datetime(["2023-01-01 12:00", "2023-01-01 13:00", "2023-01-02 12:00"])
        )
        self.mock_app.filter_by_date.set(False)
        result = self.processor._filter_data_by_date(data, None, None)
        self.assertTrue(data.equals(result))
        self.mock_app.filter_by_date.set(True)
        self.mock_app.min_datetime = pd.Timestamp("2023-01-01 00:00")
        self.mock_app.max_datetime = pd.Timestamp("2023-01-02 23:59")
        start_datetime = (2023, 1, 1, 12, 0)
        end_datetime = (2023, 1, 1, 14, 0)
        result = self.processor._filter_data_by_date(data, start_datetime, end_datetime)
        expected = data[
            (data.index >= pd.Timestamp("2023-01-01 12:00")) & (data.index <= pd.Timestamp("2023-01-01 14:00"))]
        self.assertTrue(expected.equals(result))
        start_datetime = (2023, 1, 2, 12, 0)
        end_datetime = (2023, 1, 1, 12, 0)
        result = self.processor._filter_data_by_date(data, start_datetime, end_datetime)
        self.assertIsNone(result)
        start_datetime = None
        result = self.processor._filter_data_by_date(data, start_datetime, end_datetime)
        self.assertIsNone(result)

    def test_calculate_effective_temperature(self):
        data = pd.DataFrame({
            "weather_temp": [20.0, 25.0, None],
            "weather_humidity": [50.0, 60.0, 70.0]
        })
        temp_column, humidity_column = "weather_temp", "weather_humidity"
        effective_temp, sensation = self.processor._calculate_effective_temperature(data, temp_column, humidity_column)
        expected_temp = pd.Series([18.0, 22.6, None], index=effective_temp.index)
        expected_sensation = pd.Series(["Тепло", "Тепло", None],
                                       index=effective_temp.index)  # Исправлено: 22.6 -> "Тепло"
        pd.testing.assert_series_equal(effective_temp, expected_temp, check_dtype=False)
        pd.testing.assert_series_equal(sensation, expected_sensation, check_dtype=False)

        result = self.processor._calculate_effective_temperature(data, None, humidity_column)
        self.assertIsNone(result[0])
        self.assertIsNone(result[1])

        data_invalid = pd.DataFrame({"other_column": [1, 2, 3]})
        result = self.processor._calculate_effective_temperature(data_invalid, temp_column, humidity_column)
        self.assertIsNone(result[0])
        self.assertIsNone(result[1])

        data_nan = pd.DataFrame({"weather_temp": [None, None], "weather_humidity": [None, None]})
        result = self.processor._calculate_effective_temperature(data_nan, temp_column, humidity_column)
        self.assertIsNone(result[0])
        self.assertIsNone(result[1])


    def test_create_chart_window(self):
        with patch.object(self.processor, 'clear_chart') as mock_clear:
            with patch('tkinter.Toplevel') as mock_toplevel:
                with patch('matplotlib.pyplot.figure') as mock_figure:
                    self.processor._create_chart_window("Test Chart")
                    mock_clear.assert_called_once()
                    mock_toplevel.assert_called_once_with(self.mock_app)
                    mock_toplevel().protocol.assert_called_once_with("WM_DELETE_WINDOW", self.processor.clear_chart)
                    mock_toplevel().title.assert_called_once_with("Test Chart")
                    mock_toplevel().geometry.assert_called_once_with("800x600")
                    mock_figure.assert_called_once_with(figsize=(8, 6))
                    self.assertIsNotNone(self.mock_app.chart_display)
                    self.assertIsNotNone(self.mock_app.matplotlib_figure)

    def test_add_effective_temp_traces(self):
        valid_data = pd.Series([18.0, 25.0], index=pd.to_datetime(["2023-01-01", "2023-01-02"]))
        valid_sensation = pd.Series(["Тепло", "Жарко"], index=valid_data.index)
        self.mock_app.chart_figure = go.Figure()

        # Mock the _create_chart_window to avoid GUI interaction
        with patch.object(self.processor, '_create_chart_window') as mock_create_window:
            # Test line chart
            self.processor._add_effective_temp_traces("line", valid_data, valid_sensation, "Test Device")
            self.assertEqual(len(self.mock_app.chart_figure.data), 2)
            self.assertEqual(self.mock_app.chart_figure.data[0]['mode'], 'lines')
            self.assertEqual(self.mock_app.chart_figure.data[0]['name'], 'Тепло')
            self.assertEqual(self.mock_app.chart_figure.data[1]['name'], 'Жарко')
            self.assertEqual(self.mock_app.chart_figure.data[0]['line']['color'],
                             self.mock_app.sensation_colors['Тепло'])

            # Test bar chart
            self.mock_app.chart_figure = go.Figure()
            self.processor._add_effective_temp_traces("bar", valid_data, valid_sensation, "Test Device")
            self.assertEqual(len(self.mock_app.chart_figure.data), 2)
            self.assertEqual(self.mock_app.chart_figure.data[0]['type'], 'bar')
            self.assertEqual(self.mock_app.chart_figure.data[0]['name'], 'Тепло')
            self.assertEqual(self.mock_app.chart_figure.data[1]['name'], 'Жарко')
            self.assertEqual(self.mock_app.chart_figure.data[0]['marker']['color'],
                             self.mock_app.sensation_colors['Тепло'])

            # Test scatter chart
            self.mock_app.chart_figure = go.Figure()
            self.processor._add_effective_temp_traces("scatter", valid_data, valid_sensation, "Test Device")
            self.assertEqual(len(self.mock_app.chart_figure.data), 2)
            self.assertEqual(self.mock_app.chart_figure.data[0]['mode'], 'markers')
            self.assertEqual(self.mock_app.chart_figure.data[0]['name'], 'Тепло')
            self.assertEqual(self.mock_app.chart_figure.data[1]['name'], 'Жарко')
            self.assertEqual(self.mock_app.chart_figure.data[0]['marker']['color'],
                             self.mock_app.sensation_colors['Тепло'])
            self.assertEqual(self.mock_app.chart_figure.data[0]['marker']['size'], 8)
            self.assertEqual(self.mock_app.chart_figure.data[0]['marker']['opacity'], 0.7)

            # Test empty data
            empty_data = pd.Series([], dtype=float)
            empty_sensation = pd.Series([], dtype=object)
            self.mock_app.chart_figure = go.Figure()
            with patch('tkinter.messagebox.showerror') as mock_error:
                with patch.object(self.processor, 'clear_chart') as mock_clear:
                    self.processor._add_effective_temp_traces("line", empty_data, empty_sensation, "Test Device")
                    mock_error.assert_called_once_with('Ошибка',
                                                       'Нет валидных данных для построения графика теплоощущения.')
                    mock_clear.assert_called_once()

    def test_add_regular_traces(self):
        data = pd.DataFrame({
            "weather_temp": [20.0, 21.0, 22.0],
            "weather_humidity": [50.0, 60.0, 70.0]
        }, index=pd.to_datetime(["2023-01-01 12:00", "2023-01-01 13:00", "2023-01-01 14:00"]))
        self.mock_app.chart_figure = MagicMock()
        self.mock_app.avg_one_hour.set(True)
        self.processor._add_regular_traces("line", data, data, "Date", ["weather_temp"], "Test Device")
        self.mock_app.chart_figure.add_trace.assert_called()
        self.assertGreaterEqual(self.mock_app.chart_figure.add_trace.call_count, 2)  # Основной график + осреднение

    def test_add_regular_traces_scatter(self):
        self.mock_app.chart_style.set('scatter')
        self.mock_app.device_data = {
            'Test Device (12345)': pd.DataFrame({
                'weather_temp': [20.5, 21.0],
                'weather_humidity': [60.0, 65.0]
            }, index=pd.to_datetime(['2023-01-01 12:00:00', '2023-01-01 13:00:00']))
        }
        self.mock_app.gui.device_selector.get.return_value = 'Test Device (12345)'
        self.mock_app.gui.x_axis_list.curselection.return_value = (0,)
        self.mock_app.gui.x_axis_list.get.return_value = 'Date'
        self.mock_app.gui.y_axis_list.curselection.return_value = (0,)
        self.mock_app.gui.y_axis_list.get.return_value = 'weather_temp'
        self.mock_app.chart_figure = go.Figure()
        self.processor._add_regular_traces('scatter', self.mock_app.device_data['Test Device (12345)'],
                                           self.mock_app.device_data['Test Device (12345)'], 'Date', ['weather_temp'],
                                           'Test Device (12345)')
        self.assertEqual(len(self.mock_app.chart_figure.data), 1)
        self.assertEqual(self.mock_app.chart_figure.data[0]['mode'], 'markers')
        self.assertEqual(self.mock_app.chart_figure.data[0]['name'], 'weather_temp (Test Device (12345))')
        self.assertEqual(self.mock_app.chart_figure.data[0]['marker']['size'], 8)
        self.assertEqual(self.mock_app.chart_figure.data[0]['marker']['opacity'], 0.7)


    def tearDown(self):
        self.root.destroy()


if __name__ == '__main__':
    unittest.main()
