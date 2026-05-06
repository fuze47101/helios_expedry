# import pandas as pd

from os import curdir, path
from os.path import join, dirname

from kivy.app import App
from kivy.lang import Builder
from kivy.uix.popup import Popup

curdir = dirname(__file__)
Builder.load_file(join(curdir, 'SaveDialog.kv'))

class SaveDialog(Popup):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.app = App.get_running_app()

    def get_default_path(self):
        self.path = path.expanduser("/media/usb1")
        return self.path
    
    def save(self, path):
        # try:
        #     test_settings = {
        #         'SATURATION POINT': [self.app.root.switch_point],
        #         'END POINT': [self.app.root.endpoint]
        #     }
        #     ouput_data = {
        #         'HUMIDITY(%)': {},
        #         'TEMPERATURE(°C)': {}  
        #     }
        #     data = self.app.root.data_save
        #     for item in data:
        #         ouput_data['HUMIDITY(%)'].update({item[0]: item[1]})
        #         ouput_data['TEMPERATURE(°C)'].update({item[0]: item[2]})
        #     save_path = f"{path}\\{self.ids.text_input.text}.xlsx"
        #     header_data = pd.DataFrame(test_settings)
        #     save_data = pd.DataFrame(ouput_data)
        #     writer = pd.ExcelWriter(save_path, engine='xlsxwriter')
        #     header_data.to_excel(writer, startcol=1, index=False)
        #     save_data.to_excel(writer, startrow=3)
        #     workbook = writer.book
        #     chart1 = workbook.add_chart({'type': 'line'})
        #     chart1.add_series({
        #         'name': 'Humidity Data',
        #         'categories': '=Sheet1!$A$5:$A{x1}'.format(x1=len(data)+4),
        #         'values' : '=Sheet1!$B$5:$B{x1}'.format(x1=len(data)+4),
        #     })
        #     chart1.set_legend({'none': True})
        #     chart1.set_size({'width': 960, 'height': 500})
        #     chart1.set_x_axis({
        #         'name': 'Time(s)',
        #         'position_axis': 'on_tick',
        #         'major_tick_mark': 'none',
        #         'num_font':  {'rotation': 90}
        #     })
        #     chart1.set_y_axis({
        #         'name': 'Humidity(%)',
        #         'min': 0,
        #         'max': 100
        #     })
        #     worksheet = writer.sheets['Sheet1']
        #     worksheet.set_column(1,2,18)
        #     worksheet.insert_chart(3, 3, chart=chart1)
        #     writer.close()
        #     self.dismiss()
        # except Exception as e:
        #     print(e) #TODO:Handle error on screen
        pass