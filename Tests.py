import json
import unittest
import tkinter as tk
from unittest.mock import mock_open, patch, MagicMock
import ttkbootstrap as ttk

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
        self.assertEqual(result, (1, 12, 30))

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
                    self.processor._process_json_load1()
                    self.assertTrue(mock_after.called)
                    self.assertEqual(len(self.mock_app.device_data), 1)



    def tearDown(self):
        self.root.destroy()


if __name__ == '__main__':
    unittest.main()
