from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.uix.progressbar import ProgressBar
from kivy.core.window import Window
from kivy.uix.popup import Popup
from kivy.graphics import Color, Rectangle
from kivy.properties import StringProperty, NumericProperty
from kivy.clock import Clock
import os
from pathlib import Path
from Tool.util import RFCExtractor
from tkinter import filedialog
import tkinter as tk

class SteamButton(Button):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ''
        self.background_down = ''
        self.background_color = (0.36, 0.49, 0.06, 1)  # Steam green
        self.color = (1, 1, 1, 1)  # White text
        self.font_size = 12
        self.size_hint_y = None
        self.height = 30
        self.padding = (10, 5)

class SteamLabel(Label):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.color = (0.78, 0.83, 0.87, 1)  # Steam light text
        self.font_size = 12
        self.text_size = self.size
        self.halign = 'left'
        self.valign = 'middle'
        self.bind(size=self._update_text_size)

    def _update_text_size(self, instance, value):
        self.text_size = value

class SteamProgressBar(ProgressBar):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_color = (0.1, 0.1, 0.1, 1)  # Dark background
        self.color = (0.1, 0.62, 1, 1)  # Steam blue
        self.size_hint_y = None
        self.height = 20
        self.max = 100
        self.value = 0

class RFCExtractorGUI(BoxLayout):
    selected_file = StringProperty('')
    progress_value = NumericProperty(0)
    status_text = StringProperty('Ready to extract')
    progress_max = NumericProperty(100)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = 10
        self.spacing = 10
        self.extractor = RFCExtractor()
        
        # Set window background color
        Window.clearcolor = (0.11, 0.16, 0.22, 1)  # Steam dark blue
        Window.size = (400, 300)  # Set minimum window size
        
        # Create header with image
        header = BoxLayout(size_hint_y=None, height=40, padding=[10, 0])
        # Add a spacer on the left
        header.add_widget(Label(size_hint_x=1))
        
        logo = Image(
            source='Images/text.png',
            fit_mode='contain',
            size_hint_x=None,
            width=200  # Adjust this value to control the image width
        )
        header.add_widget(logo)
        
        # Add a spacer on the right
        header.add_widget(Label(size_hint_x=1))
        self.add_widget(header)
        
        # Create file selection section
        file_section = BoxLayout(orientation='vertical', spacing=5)
        file_section.add_widget(SteamLabel(text='File Selection', bold=True))
        
        file_buttons = BoxLayout(size_hint_y=None, height=30, spacing=5)
        select_button = SteamButton(text='Select RFC File', on_press=self.show_file_dialog)
        file_buttons.add_widget(select_button)
        self.file_label = SteamLabel(text='No file selected')
        file_buttons.add_widget(self.file_label)
        file_section.add_widget(file_buttons)
        
        self.add_widget(file_section)
        
        # Create progress section
        progress_section = BoxLayout(orientation='vertical', spacing=5)
        progress_section.add_widget(SteamLabel(text='Extraction Progress', bold=True))
        
        self.progress_bar = SteamProgressBar()
        progress_section.add_widget(self.progress_bar)
        
        self.status_label = SteamLabel(text='Ready to extract')
        progress_section.add_widget(self.status_label)
        
        self.add_widget(progress_section)
        
        # Create action buttons
        button_section = BoxLayout(size_hint_y=None, height=30)
        self.extract_button = SteamButton(
            text='Extract Files',
            on_press=self.extract_files,
            disabled=True
        )
        button_section.add_widget(self.extract_button)
        self.add_widget(button_section)

    def show_file_dialog(self, instance):
        # Create a hidden root window for tkinter
        root = tk.Tk()
        root.withdraw()
        
        # Show the file dialog
        file_path = filedialog.askopenfilename(
            title='Select RFC File',
            filetypes=[('RFC Files', '*.rfc')],
            initialdir=os.path.expanduser('~')
        )
        
        if file_path:
            self.selected_file = file_path
            self.file_label.text = f'Selected: {os.path.basename(self.selected_file)}'
            self.extract_button.disabled = False
            self.status_text = 'Ready to extract'
            self.progress_value = 0
            self.progress_bar.value = 0

    def extract_files(self, instance):
        if not self.selected_file:
            return
            
        try:
            # Create output directory
            output_dir = os.path.join(
                os.path.dirname(self.selected_file),
                f"{Path(self.selected_file).stem}_extracted"
            )
            
            # Update UI
            self.extract_button.disabled = True
            self.status_text = 'Extracting files...'
            self.progress_bar.value = 0
            self.progress_bar.max = 100  # Will be updated when we know total files
            
            def progress_callback(current, total, filename):
                def update_ui(dt):
                    self.progress_bar.max = total
                    self.progress_bar.value = current
                    self.status_label.text = f'Extracting: {filename}'
                Clock.schedule_once(update_ui, 0)
            
            # Extract files
            success, result = self.extractor.extract_files(
                self.selected_file,
                output_dir,
                progress_callback
            )
            
            if success:
                # Ensure progress bar shows completion
                def update_complete(dt):
                    self.progress_bar.value = self.progress_bar.max
                    self.status_label.text = 'Extraction complete!'
                Clock.schedule_once(update_complete, 0)
                
                self.show_popup(
                    'Success',
                    f'Extraction complete!\n\nExtracted {result} files to:\n{output_dir}'
                )
            else:
                self.show_popup('Error', f'An error occurred during extraction:\n\n{result}')
            
        except Exception as e:
            self.show_popup('Error', f'An error occurred:\n\n{str(e)}')
        finally:
            # Reset UI
            def reset_ui(dt):
                self.extract_button.disabled = False
                self.status_label.text = 'Ready to extract'
                self.progress_bar.value = 0
            Clock.schedule_once(reset_ui, 1)  # Reset after a short delay

    def update_progress(self, current, total, filename):
        def update_ui(dt):
            self.progress_max = total
            self.progress_value = current
            self.progress_bar.max = total
            self.progress_bar.value = current
            self.status_text = f'Extracting: {filename}'
            self.status_label.text = self.status_text
        Clock.schedule_once(update_ui, 0)

    def show_popup(self, title, message):
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # Create a label with proper text wrapping
        msg_label = SteamLabel(
            text=message,
            size_hint_y=None,
            height=100  # Adjust based on content
        )
        content.add_widget(msg_label)
        
        button = SteamButton(text='OK', size_hint_y=None, height=30)
        content.add_widget(button)
        
        popup = Popup(
            title=title,
            content=content,
            size_hint=(None, None),
            size=(400, 200),  # Increased size
            title_color=(0.78, 0.83, 0.87, 1)  # Steam light text color
        )
        
        button.bind(on_press=popup.dismiss)
        popup.open()

class RFCExtractorApp(App):
    def build(self):
        return RFCExtractorGUI()

if __name__ == '__main__':
    RFCExtractorApp().run() 