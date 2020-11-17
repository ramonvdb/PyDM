import kivy
from kivy.app import App
from kivy.config import Config
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.button import Button
from PDFParser import check_create_dir, combine_files


Config.set('graphics', 'width',  400)
Config.set('graphics', 'height', 300)
Config.set('graphics', 'resizable', False)

kivy.require("1.11.1")
        
class OrderWindow(BoxLayout):
	def __init__(self, **kwargs):
		super(OrderWindow, self).__init__(**kwargs)

	def msgBox_error(self):
		popup = Popup(title='Error: Invoer onjuist', 
			content=Label(text='Invoer onjuist of incompleet. \nControleer invoer.'), size_hint=(0.8, 0.5))
		popup.open()

	def msgBox_finish(self, finish_string):
		popup = Popup(title='Gereed', 
			content=Label(text=finish_string), size_hint=(0.9, 0.5))
		popup.open()

	def button_clicked(self):
		order_number = self.ids.order_number.text
		if len(order_number) is not 0:
			if order_number[0] == "0" and len(order_number) >= 8:
				check_create_dir(order_number)
				finish_string = combine_files(order_number)
				self.msgBox_finish(finish_string)

			else:
				self.msgBox_error()
		else:
			self.msgBox_error()
		 

class PyDMApp(App):
    def build(self):
        return OrderWindow()       

if __name__ == "__main__":
    PyDMApp().run()



