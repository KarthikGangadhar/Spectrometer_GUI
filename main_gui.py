""" Graphical User interface for the AS726X Sparkfun breakout board connected to a PSoC controller
The data is saved in the data_class file, pyplot_embed has a matplotlib graph embedded into a tk.Frame to
display the data and usb_comm communicates with the device."""

# standard libraries
import array
import datetime
import logging
import os
import time
import tkinter as tk
# installed libraries
# local files
import device_settings
import psoc_spectrometers
import pyplot_embed
import usb_comm

__author__ = 'Kyle Vitautas Lopin'


class SpectrometerGUI(tk.Tk):
    def __init__(self, parent=None):
        tk.Tk.__init__(self, parent)
        logging.basicConfig(format='%(asctime)s %(module)s %(lineno)d: %(levelname)s %(message)s',
                            datefmt='%m/%d/%Y %I:%M:%S %p', level=logging.DEBUG)
        # make the main frame with the graph and button area
        main_frame = tk.Frame(self)
        main_frame.pack(side='top', fill=tk.BOTH, expand=True)

        # self.settings = device_settings.DeviceSettings_AS7262()
        self.device = psoc_spectrometers.AS7262(self)
        self.settings = self.device.settings

        self.graph = pyplot_embed.SpectroPlotter(main_frame, None)
        self.graph.pack(side='left', fill=tk.BOTH, expand=True)

        self.buttons_frame = ButtonFrame(main_frame, self.settings)
        self.buttons_frame.pack(side='left', padx=10)

        # make the status frame with the connect button and status information
        status_frame = StatusFrame(self, self.device)
        status_frame.pack(side='top', fill=tk.X)




BUTTON_PADY = 7


class ButtonFrame(tk.Frame):
    def __init__(self, parent: tk.Tk, settings: device_settings.DeviceSettings_AS7262):
        tk.Frame.__init__(self, parent)
        self.master = parent
        self.settings = settings

        # make all the buttons and parameters
        tk.Label(self, text="Gain Setting:").pack(side='top', pady=BUTTON_PADY)
        # gain_var_options = ["1", "3.7", "16", "64"]
        gain_var_options = device_settings.GAIN_SETTING_MAP.keys()
        tk.OptionMenu(self, settings.gain_var, *gain_var_options).pack(side='top', pady=BUTTON_PADY)

        tk.Label(self, text="Integration time (ms):").pack(side='top', pady=BUTTON_PADY)
        integration_time_var = ["{:.1f}".format(x*5.6) for x in range(255)]
        # tk.Spinbox(self, format="%.1f", from_=5.6, to=1428, increment=5.6,
        #            textvariable=settings.integration_time_var, command=self.validate_integration_time
        #            ).pack(side='top', pady=20)
        tk.OptionMenu(self, settings.integration_time_var, *integration_time_var).pack(side='top', pady=BUTTON_PADY)

        # make read frequency rate
        tk.Label(self, text="Set read rate:").pack(side='top', pady=BUTTON_PADY)
        # frequency_options = ["200 ms", "500 ms", "1 sec", "5 sec", "10 sec", "30 sec"]
        frequency_options = device_settings.READ_RATE_MAP.keys()
        tk.OptionMenu(self, settings.read_rate_var, *frequency_options).pack(side='top', pady=BUTTON_PADY)

        tk.Checkbutton(self, text="Integrate multiple reads", variable=settings.average_reads,
                       command=self.average_reads, onvalue=True, offvalue=False).pack(side='top', pady=BUTTON_PADY)

        # make LED control widgets
        tk.Label(self, text="LED power (mA):").pack(side='top', pady=BUTTON_PADY)
        # LED_power_options = ["12.5 mA", "25 mA", "50 mA", "100 mA"]
        LED_power_options = device_settings.LED_POWER_MAP.keys()
        tk.OptionMenu(self, settings.LED_power_level_var, *LED_power_options).pack(side='top', pady=BUTTON_PADY)

        self.LED_button = tk.Button(self, text="Turn LED On", command=self.LED_toggle)
        self.LED_button.pack(side='top', pady=BUTTON_PADY)

        self.run_button = tk.Button(self, text="Start", command=self.run_toggle)
        self

    # def validate_integration_time(self):
    #     """ Force the integration time variable to be a integral of 5.6 ms that the device uses """
    #     # convert the input to a float, then round it off and multiply by 5.6 to get an accurate value
    #     new_value = int(float(self.settings.integration_time_var.get()) / 5.6) * 5.6
    #     self.settings.integration_time_var.set("{:.1f}".format(new_value))

    def LED_toggle(self):
        print("Led tooggle", self.settings.LED_on)
        if self.settings.LED_on:
            # turn off the LED and change the button
            self.settings.toggle_LED(False)
            self.LED_button.config(text="Turn LED on", relief=tk.SUNKEN)
        else:
            self.settings.toggle_LED(True)
            self.LED_button.config(text="Turn LED off", relief=tk.RAISED)

    def run_toggle(self):
        if self.settings.reading:
            self.settings.reading = False

        else:
            self.settings.reading = True

    def average_reads(self):
        print("average read: ", self.settings.average_reads.get())


class StatusFrame(tk.Frame):
    def __init__(self, parent: tk.Tk, device: psoc_spectrometers.AS7262):
        tk.Frame.__init__(self, parent)
        status_str = tk.StringVar()
        if device.usb.spectrometer:
            status_str.set("Spectrometer: {0} connected".format(device.usb.spectrometer))
        elif device.usb.connected:
            status_str.set("Sensor not found on PSoC")
        elif device.usb.found:
            status_str.set("Device found but not responding properly")
        else:
            status_str.set("No device found")

        status_label = tk.Label(self, textvariable=status_str)
        status_label.pack(side='left')


if __name__ == '__main__':
    app = SpectrometerGUI()
    app.title("Spectrograph")
    app.geometry("900x650")
    app.mainloop()
