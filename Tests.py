import unittest
from unittest.mock import patch, MagicMock
import pandas as pd
from main import ChartApp


class TestChartApp(unittest.TestCase):
    def setUp(self):
        self.app = ChartApp()

    def test_validate_hour_valid(self):
        """Тестирование валидации корректных часов."""
        self.assertTrue(self.app._validate_hour("12"))
        self.assertTrue(self.app._validate_hour("0"))
        self.assertTrue(self.app._validate_hour("23"))
        self.assertTrue(self.app._validate_hour(""))  # Пустое значение допустимо

    def test_validate_hour_invalid(self):
        """Тестирование валидации некорректных часов."""
        self.assertFalse(self.app._validate_hour("24"))
        self.assertFalse(self.app._validate_hour("-1"))
        self.assertFalse(self.app._validate_hour("abc"))

    def test_validate_minute_valid(self):
        """Тестирование валидации корректных минут."""
        self.assertTrue(self.app._validate_minute("59"))
        self.assertTrue(self.app._validate_minute("0"))
        self.assertTrue(self.app._validate_minute("30"))
        self.assertTrue(self.app._validate_minute(""))  # Пустое значение допустимо

    def test_validate_minute_invalid(self):
        """Тестирование валидации некорректных минут."""
        self.assertFalse(self.app._validate_minute("60"))
        self.assertFalse(self.app._validate_minute("-1"))
        self.assertFalse(self.app._validate_minute("abc"))

    def test_correct_hour_empty(self):
        """Тестирование коррекции пустого значения часов."""
        entry = MagicMock()
        entry.get.return_value = ""
        entry.insert = MagicMock()
        self.app._correct_hour(MagicMock(widget=entry))
        entry.insert.assert_called_with(0, "00")

    def test_correct_hour_invalid(self):
        """Тестирование коррекции некорректного значения часов."""
        entry = MagicMock()
        entry.get.return_value = "25"
        entry.delete = MagicMock()
        entry.insert = MagicMock()
        self.app._correct_hour(MagicMock(widget=entry))
        entry.delete.assert_called_with(0, 'end')
        entry.insert.assert_called_with(0, "00")

    def test_correct_hour_valid(self):
        """Тестирование коррекции корректного значения часов."""
        entry = MagicMock()
        entry.get.return_value = "15"
        entry.delete = MagicMock()
        entry.insert = MagicMock()
        self.app._correct_hour(MagicMock(widget=entry))
        entry.delete.assert_not_called()
        entry.insert.assert_not_called()

    def test_correct_minute_empty(self):
        """Тестирование коррекции пустого значения минут."""
        entry = MagicMock()
        entry.get.return_value = ""
        entry.insert = MagicMock()
        self.app._correct_minute(MagicMock(widget=entry))
        entry.insert.assert_called_with(0, "00")

    def test_correct_minute_invalid(self):
        """Тестирование коррекции некорректного значения минут."""
        entry = MagicMock()
        entry.get.return_value = "60"
        entry.delete = MagicMock()
        entry.insert = MagicMock()
        self.app._correct_minute(MagicMock(widget=entry))
        entry.delete.assert_called_with(0, 'end')
        entry.insert.assert_called_with(0, "00")

    def test_correct_minute_valid(self):
        """Тестирование коррекции корректного значения минут."""
        entry = MagicMock()
        entry.get.return_value = "45"
        entry.delete = MagicMock()
        entry.insert = MagicMock()
        self.app._correct_minute(MagicMock(widget=entry))
        entry.delete.assert_not_called()
        entry.insert.assert_not_called()

    def test_parse_datetime_valid(self):
        """Тестирование парсинга корректной даты и времени."""
        date_combobox = MagicMock()
        date_combobox.get.return_value = "01-01-2023"
        hour_entry = MagicMock()
        hour_entry.get.return_value = "14"
        minute_entry = MagicMock()
        minute_entry.get.return_value = "30"
        result = self.app._parse_datetime(date_combobox, hour_entry, minute_entry)
        self.assertEqual(result, (2023, 1, 1, 14, 30))

    def test_parse_datetime_invalid(self):
        """Тестирование парсинга некорректной даты."""
        date_combobox = MagicMock()
        date_combobox.get.return_value = "invalid-date"
        hour_entry = MagicMock()
        hour_entry.get.return_value = "14"
        minute_entry = MagicMock()
        minute_entry.get.return_value = "30"
        result = self.app._parse_datetime(date_combobox, hour_entry, minute_entry)
        self.assertIsNone(result)

    def test_classify_sensation(self):
        """Тестирование классификации теплоощущения."""
        test_cases = [
            (35, "Очень жарко"),
            (25, "Жарко"),
            (20, "Тепло"),
            (15, "Умеренно тепло"),
            (10, "Прохладно"),
            (3, "Умеренно холодно"),
            (-5, "Холодно"),
            (-20, "Очень холодно"),
            (-30, "Крайне холодно"),
            (float('nan'), None)
        ]
        for temp, expected in test_cases:
            with self.subTest(temp=temp):
                result = self.app._classify_sensation(temp)
                self.assertEqual(result, expected)

    @patch('tkinter.filedialog.askopenfilename')
    @patch('builtins.open', new_callable=unittest.mock.mock_open)
    @patch('json.load')
    def test_process_json_load1_valid(self, mock_json_load, mock_open, mock_filedialog):
        """Тестирование загрузки корректного JSON."""
        mock_filedialog.return_value = "test.json"
        mock_json_load.return_value = {
            "device1": {
                "uName": "Device 1",
                "serial": "123",
                "Date": "2023-01-01 12:00:00",
                "data": {"weather_temp": 20, "weather_humidity": 60}
            }
        }
        self.app._process_json_load1()
        self.assertIn("Device 1 (123)", self.app.device_data)
        df = self.app.device_data["Device 1 (123)"]
        self.assertIsInstance(df, pd.DataFrame)
        self.assertEqual(df.index[0], pd.to_datetime("2023-01-01 12:00:00"))


    @patch('tkinter.filedialog.askopenfilename')
    def test_process_json_load1_no_file(self, mock_filedialog):
        """Тестирование загрузки при отсутствии выбранного файла."""
        mock_filedialog.return_value = ""
        self.app._process_json_load1()
        self.assertEqual(self.app.device_data, {})
        self.assertEqual(self.app.loading_bar['value'], 0)

    @patch('tkinter.filedialog.askopenfilename')
    @patch('builtins.open', new_callable=unittest.mock.mock_open)
    @patch('json.load')
    def test_process_json_load1_invalid_json(self, mock_json_load, mock_open, mock_filedialog):
        """Тестирование загрузки некорректного JSON."""
        mock_filedialog.return_value = "test.json"
        mock_json_load.side_effect = ValueError("Invalid JSON")
        with patch.object(self.app, 'after') as mock_after:
            self.app._process_json_load1()
            mock_after.assert_called()
            self.assertEqual(self.app.device_data, {})


if __name__ == '__main__':
    unittest.main()