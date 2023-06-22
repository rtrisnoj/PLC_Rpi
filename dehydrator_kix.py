## Written by Luca Keighley for AKT-International 2022
## Last updated 5/2/2023
## --------INSTALL INSTRUCTIONS----------

## pip install python-dotenv
## pip install pysimplegui
## pip install simple-pid
## git clone https://github.com/Industrial-Shields/rpiplc-python3-lib
## cd rpiplc-python3-lib
## python setup.py install


## import required modules
import os
import time
import dotenv
import hashlib
import PySimpleGUI as sg
from simple_pid import PID
from rpiplc_lib import rpiplc

dotenv_file = dotenv.find_dotenv()
dotenv.load_dotenv(dotenv_file)

## global variables
machine_status = False

impact_temp_loop = [0]*30
flameback_loop = [0]*30
impact_temp = 0
flameback_temp = 0

test_var = False

E_fault = False
Al_fault = False
F_fault = False
Ag_fault = False
Agoc_fault = False
I_fault = False
Fb_fault = False
B_fault = False  ## not yet implemented physically
fire = False

B_status = False
Ag_status = False
F_status = False
Al_status = False
I_status = False
Ir_status = False

fault_lowhigh = rpiplc.HIGH

# Define a minimum window size
min_w, min_h = 800, 600

window_sizing = sg.Window("testing", layout=[[sg.Text("Test")]], finalize=True, alpha_channel=0, )
window_sizing.Maximize()

# Get screen dimensions
screen_w, screen_h = sg.Window.get_screen_dimensions(window_sizing)
window_sizing.close()
# Compute final width and height, considering minimum size
w = max(screen_w - 40, min_w)
h = max(screen_h - 70, min_h)

generic_text_size = (20, 2)
generic_text_font = ("calibri", 14)

com_text_size = (20, 1)
com_text_font = ("calibri", 12)

header_text_size = (20, 1)
header_text_font = ("calibri", 20)

title_text_font = ("calibri", 25)

main_buttons = (30, 3)
input_size = (5, 1)
confirm_size = (9, 1)
generic_button_size = (12, 3)
infeed_button_size = (20, 3)

gui_main_left = [
    [sg.Image(key="-IMAGE-")],
    [sg.Text("Machine status", font=header_text_font)],
    [sg.Button("Turn machine ON", font=generic_text_font, key="-Status-", size=(20, 5))],
]
gui_settings_1 = [
    [sg.Text("Infeed proportional term: ", font=generic_text_font, size=generic_text_size)],
    [sg.Text("Infeed integral term: ", font=generic_text_font, size=generic_text_size)],
    [sg.Text("Infeed derivative term: ", font=generic_text_font, size=generic_text_size)],
    [sg.Text("Fan Speed: ", font=generic_text_font, size=generic_text_size)],
]
gui_settings_2 = [
    [sg.Input(str(int(os.environ["P_controller"]) * -1), key='-P_setting-', enable_events = True, size=input_size, font=header_text_font),
     sg.Button("Confirm", size=confirm_size, key="-P_settingb-", font=generic_text_font)],
    [sg.Input(str(int(os.environ["I_controller"]) * -1), key='-I_setting-', enable_events = True, size=input_size, font=header_text_font),
     sg.Button("Confirm", size=confirm_size, key="-I_settingb-", font=generic_text_font)],
    [sg.Input(str(int(os.environ["D_controller"]) * -1), key='-D_setting-', enable_events = True, size=input_size, font=header_text_font),
     sg.Button("Confirm", size=confirm_size, key="-D_settingb-", font=generic_text_font)],
    [sg.Input(str(int(os.environ["Fan_speed"])), key="-Fan_setting-", enable_events = True, size=input_size, font=header_text_font),
     sg.Button("Confirm", size=confirm_size, key="-Fan_settingb-", font=generic_text_font)],
]
gui_settings = [
    [sg.Text("Settings", font=title_text_font)],
    [
        sg.Column(gui_settings_1, size=(w / 4, h * 3 / 5)),
        sg.Column(gui_settings_2, size=(w / 4, h * 3 / 5)),
    ],
]
gui_commission_1 = [
    [sg.Text("General settings", font=header_text_font, size=header_text_size)],
    [sg.Text("Flameback Max Temp: ", font=com_text_font, size=com_text_size)],
    [sg.Text("Turning on Timing", font=header_text_font, size=header_text_size)],
    [sg.Text("Airlock to Fan delay: ", font=com_text_font, size=com_text_size)],
    [sg.Text("Fan to Agitator delay: ", font=com_text_font, size=com_text_size)],
    [sg.Text("Agitator to Burner delay: ", font=com_text_font, size=com_text_size)],
    [sg.Text("Turning off timing", font=header_text_font, size=header_text_size)],
    [sg.Text("Burner to Infeed delay: ", font=com_text_font, size=com_text_size)],
    [sg.Text("Infeed to Agitator delay: ", font=com_text_font, size=com_text_size)],
    [sg.Text("Agitator to Fan delay: ", font=com_text_font, size=com_text_size)],
    [sg.Text("Fan to Airlock delay: ", font=com_text_font, size=com_text_size)],
]
gui_commission_2 = [
    [sg.Text("", font=header_text_font, size=header_text_size)],
    [sg.Input(os.environ["Flameback_temp_max"], key="-Fb_max-", enable_events = True, size=input_size, font=header_text_font),
     sg.Button("Confirm", size=confirm_size, key="-Fb_maxb-", font=generic_text_font)],
    [sg.Text("", font=header_text_font, size=header_text_size)],
    [sg.Input(os.environ["Airlock_to_fan_delay_on"], key="-AL2F-", enable_events = True, size=input_size, font=header_text_font),
     sg.Button("Confirm", size=confirm_size, key="-AL2Fb-", font=generic_text_font)],
    [sg.Input(os.environ["Fan_to_agitator_delay_on"], key="-F2AG-", enable_events = True, size=input_size, font=header_text_font),
     sg.Button("Confirm", size=confirm_size, key="-F2AGb-", font=generic_text_font)],
    [sg.Input(os.environ["Agitator_to_burner_delay_on"], key="-AG2B-", enable_events = True, size=input_size, font=header_text_font),
     sg.Button("Confirm", size=confirm_size, key="-AG2Bb-", font=generic_text_font)],
    [sg.Text("", font=header_text_font, size=header_text_size)],
    [sg.Input(os.environ["Burner_to_Infeed_delay_off"], key="-B2I-", enable_events = True, size=input_size, font=header_text_font),
     sg.Button("Confirm", size=confirm_size, key="-B2Ib-", font=generic_text_font)],
    [sg.Input(os.environ["Infeed_to_agitator_off"], key="-I2AG-", enable_events = True, size=input_size, font=header_text_font),
     sg.Button("Confirm", size=confirm_size, key="-I2AGb-", font=generic_text_font)],
    [sg.Input(os.environ["Agitator_to_fan_delay_off"], key="-AG2F-", enable_events = True, size=input_size, font=header_text_font),
     sg.Button("Confirm", size=confirm_size, key="-AG2Fb-", font=generic_text_font)],
    [sg.Input(os.environ["Fan_to_airlock_delay_off"], key="-F2AL-", enable_events = True, size=input_size, font=header_text_font),
     sg.Button("Confirm", size=confirm_size, key="-F2ALb-", font=generic_text_font)],
]
gui_commission = [
    [sg.Text("", font=title_text_font)],
    [
        sg.Column(gui_commission_1, size=(w / 6, h * 4 / 5)),
        sg.Column(gui_commission_2, size=(w / 6, h * 4 / 5)),
    ],
]
gui_commission2_1 = [
    [sg.Text("Outputs", font=header_text_font)],
    [sg.Text("Burner On/Off Port: ", font=com_text_font, size=com_text_size)],
    [sg.Text("Agitator On/Off Port: ", font=com_text_font, size=com_text_size)],
    [sg.Text("Fan On/Off Port: ", font=com_text_font, size=com_text_size)],
    [sg.Text("Airlock On/Off Port: ", font=com_text_font, size=com_text_size)],
    [sg.Text("Infeed Reverse Port: ", font=com_text_font, size=com_text_size)],
    [sg.Text("Infeed On/Off Port: ", font=com_text_font, size=com_text_size)],
    [sg.Text("Fan Speed Analog Port: ", font=com_text_font, size=com_text_size)],
    [sg.Text("Infeed Speed Analog Port: ", font=com_text_font, size=com_text_size)],
    [sg.Text("Auto Off Safety Port:", font=com_text_font, size=com_text_size)],
]
gui_commission3_1 = [
    [sg.Text("Inputs", font=header_text_font)],
    [sg.Text("Emergency Stop Port: ", font=com_text_font, size=com_text_size)],
    [sg.Text("Airlock Fault Port: ", font=com_text_font, size=com_text_size)],
    [sg.Text("Fan Fault Port: ", font=com_text_font, size=com_text_size)],
    [sg.Text("Agitator Fault Port: ", font=com_text_font, size=com_text_size)],
    [sg.Text("Agitator Over Current Fault Port: ", font=com_text_font, size=com_text_size)],
    [sg.Text("Infeed Fault Port: ", font=com_text_font, size=com_text_size)],
    [sg.Text("Impact Temperature Analog Port: ", font=com_text_font, size=com_text_size)],
    [sg.Text("Flameback Temperature Analog Port: ", font=com_text_font, size=com_text_size)],
]
gui_commission2_2 = [
    [sg.Text("", font=title_text_font)],
    [sg.Input(os.environ["Burner_status_output"], key="-B_port-", enable_events = True, size=input_size, font=header_text_font),
     sg.Button("Confirm", size=confirm_size, key="-B_portb-", font=generic_text_font)],
    [sg.Input(os.environ["Agitator_output"], key="-Ag_port-", enable_events = True, size=input_size, font=header_text_font),
     sg.Button("Confirm", size=confirm_size, key="-Ag_portb-", font=generic_text_font)],
    [sg.Input(os.environ["Fan_output"], key="-F_port-", enable_events = True, size=input_size, font=header_text_font),
     sg.Button("Confirm", size=confirm_size, key="-F_portb-", font=generic_text_font)],
    [sg.Input(os.environ["Airlock_output"], key="-Al_port-", enable_events = True, size=input_size, font=header_text_font),
     sg.Button("Confirm", size=confirm_size, key="-Al_portb-", font=generic_text_font)],
    [sg.Input(os.environ["Infeed_reverse_output"], key="-Ir_port-", enable_events = True, size=input_size, font=header_text_font),
     sg.Button("Confirm", size=confirm_size, key="-Ir_portb-", font=generic_text_font)],
    [sg.Input(os.environ["Infeed_output"], key="-I_port-", enable_events = True, size=input_size, font=header_text_font),
     sg.Button("Confirm", size=confirm_size, key="-I_portb-", font=generic_text_font)],
    [sg.Input(os.environ["Fan_speed_output"], key="-Fs_port-", enable_events = True, size=input_size, font=header_text_font),
     sg.Button("Confirm", size=confirm_size, key="-Fs_portb-", font=generic_text_font)],
    [sg.Input(os.environ["Infeed_speed_output"], key="-Is_port-", enable_events = True, size=input_size, font=header_text_font),
     sg.Button("Confirm", size=confirm_size, key="-Is_portb-", font=generic_text_font)],
    [sg.Input(os.environ["Auto_off_safety_output"], key="-Aos_port-", enable_events = True, size=input_size, font=header_text_font),
     sg.Button("Confirm", size=confirm_size, key="-Aos_portb-", font=generic_text_font)],
]
gui_commission3_2 = [
    [sg.Text("", font=title_text_font)],
    [sg.Input(os.environ["Emergency_stop"], key="-E_port-", enable_events = True, size=input_size, font=header_text_font),
     sg.Button("Confirm", size=confirm_size, key="-E_portb-", font=generic_text_font)],
    [sg.Input(os.environ["Airlock_fault"], key="-Al_f_port-", enable_events = True, size=input_size, font=header_text_font),
     sg.Button("Confirm", size=confirm_size, key="-Al_f_portb-", font=generic_text_font)],
    [sg.Input(os.environ["Fan_fault"], key="-F_f_port-", enable_events = True, size=input_size, font=header_text_font),
     sg.Button("Confirm", size=confirm_size, key="-F_f_portb-", font=generic_text_font)],
    [sg.Input(os.environ["Agitator_fault"], key="-Ag_f_port-", enable_events = True, size=input_size, font=header_text_font),
     sg.Button("Confirm", size=confirm_size, key="-Ag_f_portb-", font=generic_text_font)],
    [sg.Input(os.environ["Over_Current_fault"], key="-Agoc_f_port-", enable_events = True, size=input_size, font=header_text_font),
     sg.Button("Confirm", size=confirm_size, key="-Agoc_f_portb-", font=generic_text_font)],
    [sg.Input(os.environ["Infeed_fault"], key="-I_f_port-", enable_events = True, size=input_size, font=header_text_font),
     sg.Button("Confirm", size=confirm_size, key="-I_f_portb-", font=generic_text_font)],
    [sg.Input(os.environ["Impact_temp_input"], key="-Im_temp_port-", enable_events = True, size=input_size, font=header_text_font),
     sg.Button("Confirm", size=confirm_size, key="-Im_temp_portb-", font=generic_text_font)],
    [sg.Input(os.environ["Flameback_temp_input"], key="-Fb_temp_port-", enable_events = True, size=input_size, font=header_text_font),
     sg.Button("Confirm", size=confirm_size, key="-Fb_temp_portb-", font=generic_text_font)],

]
gui_recipes = [

]
gui_manual_1 = [
    [sg.Text("Burner: ", font=generic_text_font, size=generic_text_size)],
    [sg.Text("Agitator: ", font=generic_text_font, size=generic_text_size)],
    [sg.Text("Fan: ", font=generic_text_font, size=generic_text_size)],
    [sg.Text("Airlock: ", font=generic_text_font, size=generic_text_size)],
    [sg.Text("", font=generic_text_font, size=generic_text_size)]
]
gui_manual_2 = [
    [
        sg.Button("Turn on Burner", key="-B_man-", font=generic_text_font, size=generic_button_size),
        sg.Button("Clear Machine Over Temperature Fault", key="-B_fault-", font=generic_text_font,
                  size=generic_button_size, visible=False),
        sg.Button("Clear Flameback Fault", key="-Fb_fault-", font=generic_text_font, size=generic_button_size,
                  visible=False),
    ],
    [
        sg.Button("Turn on Agitator", key="-Ag_man-", font=generic_text_font, size=generic_button_size),
        sg.Button("Clear Agitator Fault", key="-Ag_fault-", font=generic_text_font, size=generic_button_size,
                  visible=False),
        sg.Button("Reset Agitator Over Current Fault", key="-Agoc_fault-", font=generic_text_font,
                  size=generic_button_size, visible=False),
    ],
    [
        sg.Button("Turn on Fan", key="-F_man-", font=generic_text_font, size=generic_button_size),
        sg.Button("Clear Fan Fault", key="-F_fault-", font=generic_text_font, size=generic_button_size, visible=False),
    ],
    [
        sg.Button("Turn on Airlock", key="-Al_man-", font=generic_text_font, size=generic_button_size),
        sg.Button("Clear Airlock Fault", key="-Al_fault-", font=generic_text_font, size=generic_button_size,
                  visible=False),
    ],
    [
        sg.Button("Clear E-Stop Fault", key="-E_fault-", font=generic_text_font, size=generic_button_size,
                  visible=False),
        sg.Button("Clear Infeed Fault", key="-I_fault-", font=generic_text_font, size=generic_button_size,
                  visible=False),
    ],
]
gui_manual = [
    [sg.Text("Manual Operation")],
    [
        sg.Column(gui_manual_1, size=(w / 4, h * 4 / 5)),
        sg.Column(gui_manual_2, size=(w / 4, h * 4 / 5)),
    ],
]
gui_temp_1 = [
    [sg.Text("Temperature", font=header_text_font, size=header_text_size)],
    [sg.Text("Impact Temp: ", font=generic_text_font, size=generic_text_size)],
    [sg.Text("Flameback Temp: ", font=generic_text_font, size=generic_text_size)],
]
gui_temp_2 = [
    [sg.Text("", font=header_text_font)],
    [sg.Text(key="-Impact_temp-", font=generic_text_font, size=generic_text_size)],
    [sg.Text(key="-Flameback_temp-", font=generic_text_font, size=generic_text_size)],
]
gui_temp_3 = [
    [sg.Text("", font=header_text_font)],
    [sg.Text("Set point temp", font=generic_text_font, size=generic_text_size)],
    [sg.Input(os.environ["Temperature_setpoint"], key='-SetPoint-', enable_events = True, size=input_size, font=header_text_font),
     sg.Button("Confirm", size=confirm_size, key="-SetPointb-")],
]
gui_infeed_1 = [
    [sg.Text("Infeed Speed: ", font=generic_text_font, size=generic_text_size)],
    [sg.Button("Turn on Infeed", key="-Infeed_enable-", font=generic_text_font, size=infeed_button_size)],
    [sg.Button("Turn on Infeed Reverse", key="-Reverse_infeed-", font=generic_text_font, size=infeed_button_size)],
]
gui_infeed_2 = [
    [sg.Input(os.environ["Infeed_max"], key="-Infeed_max-", enable_events = True, size=input_size, font=header_text_font),
     sg.Button("Confirm", size=confirm_size, key="-Infeed_maxb-")],
    [sg.Text(key="-Infeed_speed-", font=generic_text_font, size=generic_text_size)],
    [sg.Button("Toggle Infeed to manual", key="-Infeed_manual-", font=generic_text_font, size=infeed_button_size)],
]
gui_bottom_buttons = [
    [
        sg.Button("Main Page", key="-Main_menu_button-", font=generic_text_font, size=main_buttons, visible=False),
        sg.Button("Recipes", key="-Recipes_button-", font=generic_text_font, size=main_buttons, visible=False),
        sg.Button("Settings", key="-Settings_button-", font=generic_text_font, size=main_buttons),
        sg.Button("Manual operation", key="-Manual_button-", font=generic_text_font, size=main_buttons),
        sg.Button("Commission Settings", key="-Commission-", font=generic_text_font, size=main_buttons, visible=False),
    ]
]
gui_bottom_right_buttons = [
    [
        sg.Text(''),
        sg.Button("Exit", key="-Exit-", font=generic_text_font, size=main_buttons, visible=True),
        sg.Text(''),
    ]
]
gui_bottom_keyboard = [
    [
        sg.Button(str(i), key="-KEYBOARD" + str(i) + "-", size=(5, 2)) for i in range(10) 
        
    ] +
    [
        sg.Button('Reset', key='-Reset-', size=(10,2))
    ]
]
gui_layout_right = [
    [
        sg.Column(gui_temp_1, size=(w / 6, h * 2 / 5)),
        sg.Column(gui_temp_2, size=(w / 6, h * 2 / 5)),
        sg.Column(gui_temp_3, size=(w / 6, h * 2 / 5)),
    ],
    [
        sg.Column(gui_infeed_1, size=(w / 4, h * 2 / 5)),
        sg.Column(gui_infeed_2, size=(w / 4, h * 2 / 5)),
    ],
]
gui_commission2 = [
    [sg.Text("Commission Settings", font=title_text_font)],
    [
        sg.Column(gui_commission2_1, size=(w / 6, h * 4 / 5)),
        sg.Column(gui_commission2_2, size=(w / 6, h * 4 / 5)),
    ],
]
gui_commission3 = [
    [sg.Text("", font=title_text_font)],
    [
        sg.Column(gui_commission3_1, size=(w / 6, h * 4 / 5)),
        sg.Column(gui_commission3_2, size=(w / 6, h * 4 / 5)),
    ]
]
gui_layout = [
    [
        sg.Column(gui_layout_right, key="-Main_menu2_gui-", size=(w / 2, h * 4 / 5)),
        sg.Column(gui_commission2, key="-Commission2_gui-", size=(w / 3, h * 4 / 5), visible=False),
        sg.Column(gui_main_left, key="-Main_menu_gui-", size=(w / 2, h * 4 / 5)),
        sg.Column(gui_settings, key="-Settings_gui-", size=(w / 2, h * 4 / 5), visible=False),
        sg.Column(gui_commission3, key="-Commission3_gui-", size=(w / 3, h * 4 / 5), visible=False),
        sg.Column(gui_commission, key="-Commission_gui-", size=(w / 3, h * 4 / 5), visible=False),
        sg.Column(gui_recipes, key="-Recipes_gui-", size=(w / 2, h * 4 / 5), visible=False),
        sg.Column(gui_manual, key="-Manual_gui-", size=(w / 2, h * 4 / 5), visible=False),
    ],
    [
        ## TODO add indication for each element
    ],
    [
        sg.Column(gui_bottom_buttons, size=(w * 3 / 4, h * 1 / 10)),
        sg.Column(gui_bottom_right_buttons, size=(w * 1 / 4, h * 1 / 10))
    ],
    [
            sg.Column(gui_bottom_keyboard, size=(w, h* 1 / 10))   # Adjust the size according to your requirements
    ]
]

window = sg.Window(title="AKT-International Dehydrator Program", layout=gui_layout,
                   margins=(10, 10), element_padding=(5, 5), finalize=True)
window.Maximize()


## initialise the raspberry pi environment
def initialise():
    rpiplc.init("RPIPLC_42")  ## 012003000400 model PLC is RPIPLC_42
    global machine_status
    machine_status = False


## initialise the input and output pins
def initialise_IO():
    test_var = True
    ## Initialise all input ports
    rpiplc.pin_mode(os.environ["Emergency_stop"], rpiplc.INPUT)
    rpiplc.pin_mode(os.environ["Airlock_fault"], rpiplc.INPUT)
    rpiplc.pin_mode(os.environ["Fan_fault"], rpiplc.INPUT)
    rpiplc.pin_mode(os.environ["Agitator_fault"], rpiplc.INPUT)
    rpiplc.pin_mode(os.environ["Over_Current_fault"], rpiplc.INPUT)
    rpiplc.pin_mode(os.environ["Infeed_fault"], rpiplc.INPUT)
    rpiplc.pin_mode(os.environ["Impact_temp_input"], rpiplc.INPUT)
    rpiplc.pin_mode(os.environ["Flameback_temp_input"], rpiplc.INPUT)

    ## Initialise all output ports
    rpiplc.pin_mode(os.environ["Burner_status_output"], rpiplc.OUTPUT)
    rpiplc.pin_mode(os.environ["Agitator_output"], rpiplc.OUTPUT)
    rpiplc.pin_mode(os.environ["Fan_output"], rpiplc.OUTPUT)
    rpiplc.pin_mode(os.environ["Airlock_output"], rpiplc.OUTPUT)
    rpiplc.pin_mode(os.environ["Infeed_reverse_output"], rpiplc.OUTPUT)
    rpiplc.pin_mode(os.environ["Infeed_output"], rpiplc.OUTPUT)
    rpiplc.pin_mode(os.environ["Fan_speed_output"], rpiplc.OUTPUT)
    rpiplc.pin_mode(os.environ["Infeed_speed_output"], rpiplc.OUTPUT)
    rpiplc.pin_mode(os.environ["Auto_off_safety_output"], rpiplc.OUTPUT)


def PasswordMatches(password, a_hash):
    password_utf = password.encode('utf-8')
    sha1hash = hashlib.sha1()
    sha1hash.update(password_utf)
    password_hash = sha1hash.hexdigest()
    # print(password_hash)
    # print(a_hash)
    return password_hash == a_hash


def fault_check():
    if E_fault or Al_fault or F_fault or Ag_fault or Agoc_fault or I_fault or Fb_fault:
        # sg.popup_non_blocking("Please Clear Faults before attempting operation")
        return True
    else:
        return False


def turn_port_on_off(Status, port, key, name):
    if not Status:
        rpiplc.digital_write(os.environ[port], rpiplc.LOW)
        # print("turned off " + str(name))
        window[key].update("Turn on " + str(name))
    elif not fault_check():
        if Status:
            # print("turning on "+ os.environ[port])
            rpiplc.digital_write(os.environ[port], rpiplc.HIGH)
            # print("turned on " + str(name))
            window[key].update("Turn off " + str(name))


def turn_machine_on():
    global Al_status
    global F_status
    global Ag_status
    global B_status
    Al_status = True
    turn_port_on_off(Al_status, "Airlock_output", "-Al_man-", "Airlock")
    rpiplc.delay(int(os.environ["Airlock_to_fan_delay_on"]) * 1000)
    F_status = True
    turn_port_on_off(F_status, "Fan_output", "-F_man-", "Fan")
    rpiplc.delay(int(os.environ["Fan_to_agitator_delay_on"]) * 1000)
    while False:  ## TODO check with Jordan about sensors (once soft starter is done)
        rpiplc.delay(100)
        test_var = True
    Ag_status = True
    turn_port_on_off(Ag_status, "Agitator_output", "-Ag_man-", "Agitator")
    rpiplc.delay(int(os.environ["Agitator_to_burner_delay_on"]) * 1000)
    while False:  ## TODO check with Jordan about sensors (once over no load)
        rpiplc.delay(100)
        test_var = true
    B_status = True
    turn_port_on_off(B_status, "Burner_status_output", "-B_man-", "Burner")


def safety_cutoff():
    Al_status = False
    F_status = False
    Ag_status = False
    B_status = False
    I_status = False
    turn_port_on_off(Al_status, "Airlock_output", "-Al_man-", "Airlock")
    turn_port_on_off(F_status, "Fan_output", "-F_man-", "Fan")
    turn_port_on_off(Ag_status, "Agitator_output", "-Ag_man-", "Agitator")
    turn_port_on_off(B_status, "Burner_status_output", "-B_man-", "Burner")
    turn_port_on_off(I_status, "Infeed_output", "-Infeed_enable-", "Infeed")


def read_inputs():
    global E_fault
    global Al_fault
    global F_fault
    global Ag_fault
    global I_status
    global Agoc_fault
    global I_fault
    global Fb_fault
    global impact_temp_loop
    global flameback_loop
    global impact_temp
    global flameback_temp
    global fire

    ## Check if E-stop has been triggeredut
    if rpiplc.digital_read(os.environ["Emergency_stop"]) == fault_lowhigh:
        window["-E_fault-"].update(visible=True)
        if not E_fault:
            E_fault = True
            safety_cutoff()
            sg.popup_non_blocking("The emegency stop has been activated, operation has been halted.")

    ## Check if an airlock fault has occured
    if rpiplc.digital_read(os.environ["Airlock_fault"]) == fault_lowhigh:
        window["-Al_fault-"].update(visible=True)
        if not Al_fault:
            Al_fault = True
            safety_cutoff()
            sg.popup_non_blocking("An airlock fault has occured, operation has been halted.")

            ## Check if a fan fault has occured
    if rpiplc.digital_read(os.environ["Fan_fault"]) == fault_lowhigh:
        window["-F_fault-"].update(visible=True)
        if not F_fault:
            F_fault = True
            safety_cutoff()
            sg.popup_non_blocking("A fan fault has occured, operation has been halted.")

    ## Check if an agitator fault has occured
    if rpiplc.digital_read(os.environ["Agitator_fault"]) == fault_lowhigh:
        window["-Ag_fault-"].update(visible=True)
        if not Ag_fault:
            Ag_fault = True
            safety_cutoff()
            sg.popup_non_blocking("An agitator fault has occured, operation has been halted.")

    ## Check if an agitator over current fault has occured
    if rpiplc.digital_read(os.environ["Over_Current_fault"]) == fault_lowhigh:
        if not Ag_fault:
            Ag_fault = True
            sg.popup_non_blocking(
                "An agitator over current fault has occured, Infeed bin has been disabled while the fault is active.")
            turn_port_on_off(False, "Infeed_output", "-Infeed_enable-", "Infeed")
    else:
        Ag_fault = False
        turn_port_on_off(I_status, "Infeed_output", "-Infeed_enable-", "Infeed")

    ## Check if an infeed fault fault has occured
    if rpiplc.digital_read(os.environ["Infeed_fault"]) == fault_lowhigh:
        window["-I_fault-"].update(visible=True)
        if not I_fault:
            I_fault = True
            safety_cutoff()
            sg.popup_non_blocking("An infeed fault has occured, operation has been halted")

    # set the moving average length
    ma_length = 30
    ## Get current flameback temp
    if len(flameback_loop) >= ma_length:
        flameback_loop.pop(0) # remove oldest data
    flameback_loop.append(rpiplc.analog_read(os.environ["Flameback_temp_input"]) * 1.6 / 3)
    flameback_temp = sum(flameback_loop) / len(flameback_loop) * 10
    # print(flameback_loop)
    # Update GUI for flameback temperature
    window["-Flameback_temp-"].update(round(flameback_temp, 1))

    # Update current impact temperature
    if len(impact_temp_loop) >= ma_length:
        impact_temp_loop.pop(0) # remove oldest data
    impact_temp_loop.append(rpiplc.analog_read(os.environ["Impact_temp_input"]) * 1.6 / 3)
    impact_temp = sum(impact_temp_loop) / len(impact_temp_loop) * 10
    window["-Impact_temp-"].update(round(impact_temp, 1))

    ## Check if temperature is over set limit
    if flameback_temp >= int(os.environ["Flameback_temp_max"]):
        window["-Fb_fault-"].update(visible=True)
        if impact_temp >= 400 or fire:
            safety_cutoff()
            fire = True
            sg.popup_non_blocking("Overtemperature, Safety Cut off trigger")

        elif not fire or fire and impact_temp < 250:
            fire = False
            Al_status = False
            Ag_status = False
            B_status = False
            I_status = False
            turn_port_on_off(Al_status, "Airlock_output", "-Al_man-", "Airlock")
            turn_port_on_off(Ag_status, "Agitator_output", "-Ag_man-", "Agitator")
            turn_port_on_off(B_status, "Burner_status_output", "-B_man-", "Burner")
            turn_port_on_off(I_status, "Infeed_output", "-Infeed_enable-", "Infeed")

        if not Fb_fault:
            Fb_fault = True
            # safety_cutoff()
            sg.popup_non_blocking("The flameback temp maximum has been reached, operation has been halted")


def IO_change(port_name, new_port):
    valid_names = [
        "I0.0", "I0.1", "I0.2", "I0.3", "I0.4", "I0.5", "I0.6",
        "I0.7", "I0.8", "I0.9", "I0.10", "I0.11", "I0.12",
        "Q0.0", "Q0.1", "Q0.2", "Q0.3", "Q0.4", "Q0.5", "Q0.6",
        "Q0.7", "A0.5", "A0.6", "A0.7",
        "I1.0", "I1.1", "I1.2", "I1.3", "I1.4", "I1.5", "I1.6",
        "I1.7", "I1.8", "I1.9", "I1.10", "I1.11", "I1.12",
        "Q1.0", "Q1.1", "Q1.2", "Q1.3", "Q1.4", "Q1.5", "Q1.6",
        "Q1.7", "A1.5", "A1.6", "A1.7"
    ]
    if new_port in valid_names:
        dotenv.set_key(dotenv_file, port_name, new_port)
    else:
        sg.popup_non_blocking(
            "Please enter a valid port name (I0.0-I0.12, Q0.0-Q0.7, A0.5-A0.7, I1.0-I1.12, Q1.0-Q1.7, A1.5-A1.7")


def fan_speed():
    print(str(os.environ["Fan_speed"]))
    print(str(round(((int(os.environ["Fan_speed"]) - 40) / 20) * 4095 * 2)))
    output = round(((int(os.environ["Fan_speed"]) - 40) / 20) * 4095 * 2)
    ##print(str(output))
    rpiplc.analog_write(os.environ["Fan_speed_output"], int(output))


def turn_machine_off():
    global Al_status
    global F_status
    global Ag_status
    global B_status
    global I_status
    B_status = False
    turn_port_on_off(B_status, "Burner_status_output", "-B_man-", "Burner")
    rpiplc.delay(int(os.environ["Burner_to_Infeed_delay_off"]) * 1000)
    I_status = False
    turn_port_on_off(I_status, "Infeed_output", "-Infeed_enable-", "Infeed")
    while False:  ## TODO check with Jordan about sensors (Agitator current is above no load)
        rpiplc.delay(100)
        test_var = true
    Ag_status = False
    turn_port_on_off(Ag_status, "Agitator_output", "-Ag_man-", "Agitator")
    rpiplc.delay(int(os.environ["Agitator_to_fan_delay_off"]) * 1000)
    F_status = False
    turn_port_on_off(F_status, "Fan_output", "-F_man-", "Fan")
    rpiplc.delay(int(os.environ["Fan_to_airlock_delay_off"]) * 1000)
    Al_status = False
    turn_port_on_off(Al_status, "Airlock_output", "-Al_man-", "Airlock")


def pid_loop(pid):  ## TODO figure out how PID works
    test_var = True
    if impact_temp > int(os.environ["Temperature_setpoint"]) - 5 or not pid.auto_mode:
        ##rpiplc.digital_write(os.environ["Infeed_output"], rpiplc.HIGH)
        control = pid(impact_temp)
        output = (control / 100) * 4095
        print(output)
        rpiplc.analog_write(os.environ["Infeed_speed_output"], int(output))


def main():
    try:
        initialise()
        initialise_IO()
        safety_cutoff()

        rpiplc.digital_write(os.environ["Auto_off_safety_output"], rpiplc.HIGH)
        time.sleep(1)
        rpiplc.digital_write(os.environ['Auto_off_safety_output'], rpiplc.LOW)

        global machine_status
        global Al_status
        global F_status
        global Ag_status
        global B_status
        global I_status
        global Ir_status
        global E_fault
        global Al_fault
        global F_fault
        global Ag_fault
        global I_status
        global Agoc_fault
        global I_fault
        global Fb_fault

        machine_status = False
        active_input = None
        pid = PID(int(os.environ["P_controller"]), int(os.environ["I_controller"]), int(os.environ["D_controller"]),
                int(os.environ["Temperature_setpoint"]))
        pid.proportional_on_measurement = True
        pid.output_limits = (0, int(os.environ["Infeed_max"]))
        while True:
            read_inputs()
            event, values = window.read(timeout=1000)
            if event == sg.WIN_CLOSED or event == 'Exit':
                Al_status = False
                F_status = False
                Ag_status = False
                B_status = False
                I_status = False
                turn_port_on_off(Al_status, "Airlock_output", "-Al_man-", "Airlock")
                turn_port_on_off(F_status, "Fan_output", "-F_man-", "Fan")
                turn_port_on_off(Ag_status, "Agitator_output", "-Ag_man-", "Agitator")
                turn_port_on_off(B_status, "Burner_status_output", "-B_man-", "Burner")
                turn_port_on_off(I_status, "Infeed_output", "-Infeed_enable-", "Infeed")
                break

            ## Turning machine On/Off
            elif event == '-Status-':
                if not machine_status:
                    if not fault_check():
                        # reset variables
                        Al_status = False
                        F_status = False
                        Ag_status = False
                        B_status = False
                        I_status = False
                        window["-Status-"].update("Turning ON")
                        # sg.Popup("Please wait...", "Machine is turning on.", non_blocking=False)
                        window.perform_long_operation(turn_machine_on, "-Machine_on-")
                elif machine_status:
                    # reset variables
                    Al_status = False
                    F_status = False
                    Ag_status = False
                    B_status = False
                    I_status = False
                    window["-Status-"].update("Turning OFF")
                    # sg.Popup("Please wait...", "Machine is turning off.", non_blocking=False)
                    window.perform_long_operation(turn_machine_off, "-Machine_off-")

            elif event == '-Machine_on-':
                machine_status = True
                window["-Status-"].update("Turn machine OFF")

            elif event == '-Machine_off-':
                machine_status = False
                window["-Status-"].update("Turn machine ON")

            ## Data entry events
            elif event == '-SetPointb-':
                text = values["-SetPoint-"]
                try:
                    number = int(text)
                    if number >= 0 and number <= int(os.environ["Max_temp"]):
                        dotenv.set_key(dotenv_file, "Temperature_setpoint", text)
                        pid.setpoint = number
                    else:
                        raise
                except:
                    sg.popup_non_blocking("Please enter an integer between 0 and " + os.environ["Max_temp"])

            elif event == '-Infeed_maxb-':
                text = values["-Infeed_max-"]
                try:
                    number = int(text)
                    if number >= 0 and number <= 100:
                        dotenv.set_key(dotenv_file, "Infeed_max", text)
                        pid.output_limits = (0, number)
                        # pid.output_limits((0, number))
                        # print("successful test")
                    else:
                        # print("fail test")
                        raise
                except:
                    sg.popup_non_blocking("Please enter an integer between 0 and 100")

            elif event == '-P_settingb-':
                text = values["-P_setting-"]
                try:
                    number = int(text)
                    if number >= 0 and number <= 1000:
                        dotenv.set_key(dotenv_file, "P_controller", "-" + text)
                        pid.Kp = -number
                    else:
                        raise
                except:
                    sg.popup_non_blocking("Please enter an integer between 0 and 1000")

            elif event == '-I_settingb-':
                text = values["-I_setting-"]
                try:
                    number = int(text)
                    if number >= 0 and number <= 1000:
                        dotenv.set_key(dotenv_file, "I_controller", "-" + text)
                        pid.Ki = -number
                    else:
                        raise
                except:
                    sg.popup_non_blocking("Please enter an integer between 0 and 1000")

            elif event == '-D_settingb-':
                text = values["-D_setting-"]
                try:
                    number = int(text)
                    if number >= 0 and number <= 1000:
                        dotenv.set_key(dotenv_file, "D_controller", "-" + text)
                        pid.Kd = -number
                    else:
                        raise
                except:
                    sg.popup_non_blocking("Please enter an integer between 0 and 1000")

            elif event == '-Fan_settingb-':
                text = values["-Fan_setting-"]
                try:
                    number = int(text)
                    if number >= 40 and number <= 60:
                        dotenv.set_key(dotenv_file, "Fan_speed", text)
                        fan_speed()
                    else:
                        raise
                except:
                    sg.popup_non_blocking("Please enter an integer between 40 and 60")

            elif event == '-AL2Fb-':
                text = values["-AL2F-"]
                try:
                    number = int(text)
                    if number >= 0 and number <= 1000:
                        dotenv.set_key(dotenv_file, "Airlock_to_fan_delay_on", text)
                    else:
                        raise
                except:
                    sg.popup_non_blocking("Please enter an integer between 0 and 1000")

            elif event == '-F2AGb-':
                text = values["-F2AG-"]
                try:
                    number = int(text)
                    if number >= 0 and number <= 1000:
                        dotenv.set_key(dotenv_file, "Fan_to_agitator_delay_on", text)
                    else:
                        raise
                except:
                    sg.popup_non_blocking("Please enter an integer between 0 and 1000")

            elif event == '-AG2Bb-':
                text = values["-AG2B-"]
                try:
                    number = int(text)
                    if number >= 0 and number <= 1000:
                        dotenv.set_key(dotenv_file, "Agitator_to_burner_delay_on", text)
                    else:
                        raise
                except:
                    sg.popup_non_blocking("Please enter an integer between 0 and 1000")

            elif event == '-B2Ib-':
                text = values["-B2I-"]
                try:
                    number = int(text)
                    if number >= 0 and number <= 1000:
                        dotenv.set_key(dotenv_file, "Burner_to_Infeed_delay_off", text)
                    else:
                        raise
                except:
                    sg.popup_non_blocking("Please enter an integer between 0 and 1000")

            elif event == '-I2AGb-':
                text = values["-I2AG-"]
                try:
                    number = int(text)
                    if number >= 0 and number <= 1000:
                        dotenv.set_key(dotenv_file, "Infeed_to_agitator_off", text)
                    else:
                        raise
                except:
                    sg.popup_non_blocking("Please enter an integer between 0 and 1000")

            elif event == '-AG2Fb-':
                text = values["-AG2F-"]
                try:
                    number = int(text)
                    if number >= 0 and number <= 1000:
                        dotenv.set_key(dotenv_file, "Agitator_to_fan_delay_off", text)
                    else:
                        raise
                except:
                    sg.popup_non_blocking("Please enter an integer between 0 and 1000")

            elif event == '-F2ALb-':
                text = values["-F2AL-"]
                try:
                    number = int(text)
                    if number >= 0 and number <= 1000:
                        dotenv.set_key(dotenv_file, "Fan_to_airlock_delay_off", text)
                    else:
                        raise
                except:
                    sg.popup_non_blocking("Please enter an integer between 0 and 1000")

            elif event == '-Fb_maxb-':
                text = values["-Fb_max-"]
                try:
                    number = int(text)
                    if number >= 20 and number <= 55:
                        dotenv.set_key(dotenv_file, "Flameback_temp_max", text)
                    else:
                        raise
                except:
                    sg.popup_non_blocking("Please enter an integer between 20 and 55")

            elif event == '-B_portb-' and F_status:
                IO_change("Burner_status_output", values["-B_port-"])

            elif event == '-Ag_portb-':
                IO_change("Agitator_output", values["-Ag_port-"])

            elif event == '-F_portb-':
                IO_change("Fan_output", values["-F_port-"])

            elif event == '-Al_portb-':
                IO_change("Airlock_output", values["-Al_port-"])

            elif event == '-Ir_portb-':
                IO_change("Infeed_reverse_output", values["-Ir_port-"])

            elif event == '-I_portb-':
                IO_change("Infeed_output", values["-I_port-"])

            elif event == '-Fs_portb-':
                IO_change("Fan_speed_output", values["-Fs_port-"])

            elif event == '-Is_portb-':
                IO_change("Infeed_speed_output", values["-Is_port-"])

            elif event == '-E_portb-':
                IO_change("Emergency_stop", values["-E_port-"])

            elif event == '-Al_f_portb-':
                IO_change("Airlock_fault", values["-Al_f_port-"])

            elif event == '-F_f_portb-':
                IO_change("Fan_fault", values["-F_f_port-"])

            elif event == '-Ag_f_portb-':
                IO_change("Agitator_fault", values["-Ag_f_port-"])

            elif event == '-Agoc_f_portb-':
                IO_change("Over_Current_fault", values["-Agoc_f_port-"])

            elif event == '-I_f_portb-':
                IO_change("Infeed_fault", values["-I_f_port-"])

            elif event == '-Im_temp_portb-':
                IO_change("Impact_temp_input", values["-Im_temp_port-"])

            elif event == '-Fb_temp_portb-':
                IO_change("Flameback_temp_input", values["-Fb_temp_port-"])


            ## Turn outputs On/Off
            elif event == '-Infeed_enable-':
                turn_port_on_off(not I_status, "Infeed_output", '-Infeed_enable-', "Infeed")
                I_status = not I_status

            elif event == '-Reverse_infeed-':
                turn_port_on_off(not Ir_status, "Infeed_reverse_output", '-Reverse_infeed-', "Infeed Reverse")
                sg.popup_non_blocking("Caution! Reversing infeed")
                Ir_status = not Ir_status


            ## Change Pages
            elif event == '-Recipes_button-':  ## not part of scope for now
                machine_status = True  # TODO replace with acutal code to open different page

            elif event == '-Commission-':
                password = sg.popup_get_text("Password: ", password_char='*')
                if password and PasswordMatches(password, os.environ["password"]):
                    window["-Commission-"].update(visible=False)
                    window["-Main_menu_button-"].update(visible=True)
                    window["-Manual_button-"].update(visible=True)
                    window["-Settings_button-"].update(visible=True)

                    window["-Main_menu_gui-"].update(visible=False)
                    window["-Main_menu2_gui-"].update(visible=False)
                    window["-Manual_gui-"].update(visible=False)
                    window["-Settings_gui-"].update(visible=False)
                    window["-Commission2_gui-"].update(visible=True)
                    window["-Commission3_gui-"].update(visible=True)
                    window["-Commission_gui-"].update(visible=True)
                else:
                    sg.popup_non_blocking("Sorry that password is incorrect.")

            elif event == '-Settings_button-':
                window["-Main_menu_button-"].update(visible=True)
                window["-Manual_button-"].update(visible=True)
                window["-Commission-"].update(visible=True)
                window["-Settings_button-"].update(visible=False)

                window["-Main_menu_gui-"].update(visible=False)
                window["-Manual_gui-"].update(visible=False)
                window["-Commission2_gui-"].update(visible=False)
                window["-Commission3_gui-"].update(visible=False)
                window["-Commission_gui-"].update(visible=False)
                window["-Main_menu2_gui-"].update(visible=True)
                window["-Settings_gui-"].update(visible=True)

            elif event == '-Manual_button-':
                window["-Main_menu_button-"].update(visible=True)
                window["-Settings_button-"].update(visible=True)
                window["-Manual_button-"].update(visible=False)
                window["-Commission-"].update(visible=False)

                window["-Main_menu_gui-"].update(visible=False)
                window["-Settings_gui-"].update(visible=False)
                window["-Commission2_gui-"].update(visible=False)
                window["-Commission3_gui-"].update(visible=False)
                window["-Commission_gui-"].update(visible=False)
                window["-Main_menu2_gui-"].update(visible=True)
                window["-Manual_gui-"].update(visible=True)

            elif event == '-Main_menu_button-':
                window["-Manual_button-"].update(visible=True)
                window["-Main_menu2_gui-"].update(visible=True)
                window["-Settings_button-"].update(visible=True)
                window["-Main_menu_button-"].update(visible=False)
                window["-Commission-"].update(visible=False)

                window["-Manual_gui-"].update(visible=False)
                window["-Settings_gui-"].update(visible=False)
                window["-Commission2_gui-"].update(visible=False)
                window["-Commission3_gui-"].update(visible=False)
                window["-Commission_gui-"].update(visible=False)
                window["-Main_menu2_gui-"].update(visible=True)
                window["-Main_menu_gui-"].update(visible=True)

            elif event == sg.WINDOW_CLOSED or event == '-Exit-':
                break
            ## Fault events
            elif event == '-B_fault-':
                B_fault = False
                window["-B_fault-"].update(visible=False)

            elif event == '-Fb_fault-':
                Fb_fault = False
                window["-Fb_fault-"].update(visible=False)

            elif event == '-Ag_fault-':
                Ag_fault = False
                window["-Ag_fault-"].update(visible=False)

            elif event == '-Agoc_fault-':
                Agoc_fault = False
                window["-Agoc_fault-"].update(visible=False)

            elif event == '-F_fault-':
                F_fault = False
                window["-F_fault-"].update(visible=False)

            elif event == '-Al_fault-':
                Al_fault = False
                window["-Al_fault-"].update(visible=False)

            elif event == '-E_fault-':
                E_fault = False
                window["-E_fault-"].update(visible=False)

            elif event == '-I_fault-':
                I_fault = False
                window["-I_fault-"].update(visible=False)



            ## Manual events
            elif event == '-Infeed_manual-':
                if not pid.auto_mode:
                    window["-Infeed_manual-"].update("Toggle Infeed to manual")
                    pid.set_auto_mode(True, last_output=int(os.environ["Infeed_max"]))
                elif pid.auto_mode:
                    window["-Infeed_manual-"].update("Toggle Infeed to automatic")
                    pid.auto_mode = False

            elif event == '-B_man-' and (B_status or not B_status and Ag_status and F_status) and not fault_check():
                turn_port_on_off(not B_status, "Burner_status_output", '-B_man-', "Burner")
                B_status = not B_status

            elif event == '-Ag_man-' and not fault_check():
                turn_port_on_off(not Ag_status, "Agitator_output", '-Ag_man-', "Agitator")
                Ag_status = not Ag_status
                if B_status:
                    B_status = False
                    turn_port_on_off(B_status, "Burner_status_output", '-B_man-', "Burner")

            elif event == '-F_man-' and not fault_check():
                turn_port_on_off(not F_status, "Fan_output", '-F_man-', "Fan")
                F_status = not F_status
                if B_status:
                    B_status = False
                    turn_port_on_off(B_status, "Burner_status_output", '-B_man-', "Burner")


            elif event == '-Al_man-' and not fault_check():
                turn_port_on_off(not Al_status, "Airlock_output", '-Al_man-', "Airlock")
                Al_status = not Al_status
        
            if event in ('-SetPoint-', '-Infeed_max-', '-P_setting-', '-I_setting-', '-D_setting-', '-Fan_setting-', '-Fb_max-', '-AL2F-', '-F2AG-', '-AG2B-', '-B2I-', '-I2AG-', '-AG2F-', '-F2AL-', '-B_port-', '-Ag_port-', '-F_port-', '-Al_port-', '-Ir_port-', '-I_port-', '-Fs_port-', '-Is_port-', '-Aos_port-', '-E_port-', '-Al_f_port-', '-F_f_port-', '-Ag_f_port-', '-Agoc_f_port-', '-I_f_port-', '-Im_temp_port-', '-Fb_temp_port-' ):
                active_input = event
            elif "-KEYBOARD" in event:
                digit = event.replace("-KEYBOARD", "").replace("-", "")
                    
                # Only do something if an input is selected
                if active_input is not None:
                    current_value = values[active_input]
                    window[active_input].update(current_value + digit)
            elif event =='-Reset-':
                if active_input is not None:
                    window[active_input].update('')
            else:
                if machine_status:
                    pid.setpoint = int(os.environ["Temperature_setpoint"])
                    pid_loop(pid)
                elif not machine_status:
                    pid.setpoint = 0
    except Exception as e:
        print(f"An error occurred: {e}")
        
        # reset variables
        Al_status = False
        F_status = False
        Ag_status = False
        B_status = False
        I_status = False
        turn_port_on_off(Al_status, "Airlock_output", "-Al_man-", "Airlock")
        turn_port_on_off(F_status, "Fan_output", "-F_man-", "Fan")
        turn_port_on_off(Ag_status, "Agitator_output", "-Ag_man-", "Agitator")
        turn_port_on_off(B_status, "Burner_status_output", "-B_man-", "Burner")
        turn_port_on_off(I_status, "Infeed_output", "-Infeed_enable-", "Infeed")



if __name__ == "__main__":
    main()
