
DEVNAME = 'Dev1'

# DIGITAL OUTPUTS
DIGITAL_OUTPUTS  = {
    'camera_trigger': DEVNAME + '/port0/line0', # camera trigger
    # CoolLED triggers
    'led365_trigger':  DEVNAME + '/port0/line1', 
    'led450_trigger':  DEVNAME + '/port0/line2',
    'led550_trigger':  DEVNAME + '/port0/line4',
    # PV850 pump trigger
    'pump':  DEVNAME + '/port0/line5'
}

ANALOG_INPUTS = {
    # copies of digital outputs to ensure experiment worked
    'camera_trigger':  DEVNAME + '/ai0',
    'led365_trigger':  DEVNAME + '/ai1',
    'led450_trigger':  DEVNAME + '/ai2',
    'led550_trigger':  DEVNAME + '/ai3',
    'led635_trigger':  DEVNAME + '/ai4',
    'pump_trigger':  DEVNAME + '/ai5',

    # camera timing signal
    'camera_output':  DEVNAME + '/ai6'
}
