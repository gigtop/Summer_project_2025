import tkinter as tk
from gui import ChartAppGUI
from data_processing import DataProcessor


class ChartApp(tk.Tk):
    def __init__(self):
        super().__init__()

        """TitleBar"""
        self.title("Calculus Graphicus")
        self.geometry("1200x400")
        self.resizable(False, False)
        self.iconbitmap(r"myApp.ico")

        """Device data"""
        self.device_data = {}

        """Flags"""
        self.filter_by_date = tk.BooleanVar(value=False)
        self.effective_temp_mode = tk.BooleanVar(value=False)
        self.avg_one_hour = tk.BooleanVar(value=False)
        self.avg_three_hours = tk.BooleanVar(value=False)
        self.avg_one_day = tk.BooleanVar(value=False)
        self.min_max_daily = tk.BooleanVar(value=False)
        self.min_datetime = None
        self.max_datetime = None

        """Chart Flags"""
        self.chart_style = tk.StringVar(value='line')
        self.chart_figure = None
        self.chart_display = None
        self.chart_canvas = None
        self.matplotlib_figure = None

        self.sensation_colors = {
            'Крайне холодно': '#000080',
            'Очень холодно': '#0000FF',
            'Холодно': '#87CEFA',
            'Умеренно холодно': '#ADD8E6',
            'Прохладно': '#008000',
            'Умеренно тепло': '#9ACD32',
            'Тепло': '#FFD700',
            'Жарко': '#FF8C00',
            'Очень жарко': '#FF0000'
        }

        self.data_processor = DataProcessor(self)
        self.gui = ChartAppGUI(self)
        self.protocol("WM_DELETE_WINDOW", self._on_closing)

    def _on_closing(self):
        self.data_processor.clear_chart()
        self.quit()
        self.destroy()


if __name__ == '__main__':
    app = ChartApp()
    app.mainloop()
