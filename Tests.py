import unittest
import tkinter as tk
from unittest.mock import MagicMock

from main import ChartApp
from gui import ChartAppGUI
from data_processing import DataProcessor


class TestChartApp(unittest.TestCase):
    def setUp(self):
        self.app = ChartApp()

    def test_initialization(self):
        self.assertEqual(self.app.title(), "Calculus Graphicus")
        geometry = self.app.geometry()
        size = geometry.split('+')[0]
        self.assertEqual(size, "1200x400")
        self.assertFalse(self.app.resizable()[0])
        self.assertFalse(self.app.resizable()[1])
        self.assertIsInstance(self.app.device_data, dict)
        self.assertIsInstance(self.app.filter_by_date, tk.BooleanVar)
        self.assertIsInstance(self.app.effective_temp_mode, tk.BooleanVar)
        self.assertIsInstance(self.app.avg_one_hour, tk.BooleanVar)
        self.assertIsInstance(self.app.avg_three_hours, tk.BooleanVar)
        self.assertIsInstance(self.app.avg_one_day, tk.BooleanVar)
        self.assertIsInstance(self.app.min_max_daily, tk.BooleanVar)
        self.assertIsInstance(self.app.chart_style, tk.StringVar)
        self.assertEqual(self.app.chart_style.get(), "line")
        self.assertIsNone(self.app.min_datetime)
        self.assertIsNone(self.app.max_datetime)
        self.assertIsNone(self.app.chart_display)
        self.assertIsNone(self.app.chart_canvas)
        self.assertIsNone(self.app.matplotlib_figure)
        self.assertIsInstance(self.app.sensation_colors, dict)
        self.assertEqual(len(self.app.sensation_colors), 9)

    def test_on_closing(self):
        self.app.data_processor.clear_chart = lambda: None  # Mock clear_chart
        self.app._on_closing()


class TestChartAppGUI(unittest.TestCase):
    def setUp(self):
        self.root = ChartApp()
        self.app = ChartAppGUI(self.root)

    def tearDown(self):
        self.root.destroy()

    def test_initialization(self):
        self.assertIsInstance(self.app.master, ChartApp)
        self.assertIsNotNone(self.app.device_selector)
        self.assertIsNotNone(self.app.start_datetime_selector)
        self.assertIsNotNone(self.app.end_datetime_selector)
        self.assertIsNotNone(self.app.start_hour_entry)
        self.assertIsNotNone(self.app.start_minute_entry)
        self.assertIsNotNone(self.app.end_hour_entry)
        self.assertIsNotNone(self.app.end_minute_entry)
        self.assertIsNotNone(self.app.x_axis_list)
        self.assertIsNotNone(self.app.y_axis_list)
        self.assertIsNotNone(self.app.temp_selector)
        self.assertIsNotNone(self.app.humidity_selector)
        self.assertIsNotNone(self.app.load_json_button)
        self.assertIsNotNone(self.app.loading_bar)

    def test_time_validation_hour(self):
        self.assertTrue(self.app._validate_hour(""))
        self.assertTrue(self.app._validate_hour("0"))
        self.assertTrue(self.app._validate_hour("23"))
        self.assertFalse(self.app._validate_hour("24"))
        self.assertFalse(self.app._validate_hour("abc"))

    def test_time_validation_minute(self):
        self.assertTrue(self.app._validate_minute(""))
        self.assertTrue(self.app._validate_minute("0"))
        self.assertTrue(self.app._validate_minute("59"))
        self.assertFalse(self.app._validate_minute("60"))
        self.assertFalse(self.app._validate_minute("abc"))

    def test_correct_hour(self):
        # Create a mock event with a widget attribute
        event = tk.Event()
        event.widget = self.app.start_hour_entry

        self.app.start_hour_entry.delete(0, tk.END)
        self.app.start_hour_entry.insert(0, "")
        self.app._correct_hour(event)
        self.assertEqual(self.app.start_hour_entry.get(), "")

        self.app.start_hour_entry.delete(0, tk.END)
        self.app.start_hour_entry.insert(0, "24")
        self.app._correct_hour(event)
        self.assertEqual(self.app.start_hour_entry.get(), "")

        self.app.start_hour_entry.delete(0, tk.END)
        self.app.start_hour_entry.insert(0, "abc")
        self.app._correct_hour(event)
        self.assertEqual(self.app.start_hour_entry.get(), "")

    def test_correct_minute(self):
        # Create a mock event with a widget attribute
        event = tk.Event()
        event.widget = self.app.start_minute_entry

        self.app.start_minute_entry.delete(0, tk.END)
        self.app.start_minute_entry.insert(0, "")
        self.app._correct_minute(event)
        self.assertEqual(self.app.start_minute_entry.get(), "")

        self.app.start_minute_entry.delete(0, tk.END)
        self.app.start_minute_entry.insert(0, "60")
        self.app._correct_minute(event)
        self.assertEqual(self.app.start_minute_entry.get(), "")

        self.app.start_minute_entry.delete(0, tk.END)
        self.app.start_minute_entry.insert(0, "abc")
        self.app._correct_minute(event)
        self.assertEqual(self.app.start_minute_entry.get(), "")

    def test_toggle_date_filter(self):
        self.app.master.filter_by_date.set(True)
        self.app._toggle_date_filter()
        self.assertEqual(str(self.app.start_datetime_selector.cget("state")), "readonly")
        self.assertEqual(str(self.app.start_hour_entry.cget("state")), "normal")

        self.app.master.filter_by_date.set(False)
        self.app._toggle_date_filter()
        self.assertEqual(str(self.app.start_datetime_selector.cget("state")), "disabled")
        self.assertEqual(str(self.app.start_hour_entry.cget("state")), "disabled")


class TestDataProcessor(unittest.TestCase):
    def setUp(self):
        self.root = tk.Tk()
        self.app = MagicMock()
        self.app.gui = MagicMock()
        self.app.device_data = {}
        self.app.filter_by_date = tk.BooleanVar(value=False)
        self.app.effective_temp_mode = tk.BooleanVar(value=False)
        self.app.avg_one_hour = tk.BooleanVar(value=False)
        self.app.avg_three_hours = tk.BooleanVar(value=False)
        self.app.avg_one_day = tk.BooleanVar(value=False)
        self.app.min_max_daily = tk.BooleanVar(value=False)
        self.app.chart_style = tk.StringVar(value="line")
        self.app.min_datetime = None
        self.app.max_datetime = None
        self.app.chart_figure = None
        self.app.chart_display = None
        self.app.chart_canvas = None
        self.app.matplotlib_figure = None
        self.app.sensation_colors = {
            'Крайне холодно': '#000080', 'Очень холодно': '#0000FF', 'Холодно': '#87CEFA',
            'Умеренно холодно': '#ADD8E6', 'Прохладно': '#008000', 'Умеренно тепло': '#9ACD32',
            'Тепло': '#FFD700', 'Жарко': '#FF8C00', 'Очень жарко': '#FF0000'
        }
        self.processor = DataProcessor(self.app)

    def test_parse_datetime(self):
        self.app.gui.start_datetime_selector.get.return_value = "01-01"
        self.app.gui.start_hour_entry.get.return_value = "12"
        self.app.gui.start_minute_entry.get.return_value = "30"
        result = self.processor._parse_datetime(
            self.app.gui.start_datetime_selector,
            self.app.gui.start_hour_entry,
            self.app.gui.start_minute_entry
        )
        self.assertEqual(result, (1, 12, 30))

        self.app.gui.start_datetime_selector.get.return_value = "invalid"
        result = self.processor._parse_datetime(
            self.app.gui.start_datetime_selector,
            self.app.gui.start_hour_entry,
            self.app.gui.start_minute_entry
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


if __name__ == '__main__':
    unittest.main()
