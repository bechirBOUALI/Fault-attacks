from __future__ import print_function, division

import time
import logging
import os
from collections import namedtuple
import csv

import numpy as np

import chipwhisperer as cw
from chipwhisperer.capture.api.programmers import STM32FProgrammer

logging.basicConfig(level=logging.WARN)
scope = cw.scope()
target = cw.target(scope)

# setup parameters needed for glitch the stm32f
scope.glitch.clk_src = 'clkgen'

scope.gain.gain = 45
scope.adc.samples = 5000
scope.adc.offset = 0
scope.adc.basic_mode = "rising_edge"
scope.clock.clkgen_freq = 7370000
scope.clock.adc_src = "clkgen_x4"
scope.trigger.triggers = "tio4"
scope.io.tio1 = "serial_rx"
scope.io.tio2 = "serial_tx"
scope.io.hs2 = "glitch"

target.go_cmd = ""
target.key_cmd = ""

# program the stm32f with the built hex file
def flash():
    programmer = STM32FProgrammer()
    programmer.scope = scope
    programmer._logging = None
    programmer.open()
    programmer.find()
    programmer.erase()
    #glitch_simple_firmware_dir = os.path.join(FIRMWARE_DIR, 'glitch-simple')
    #glitch_simple_hex = os.path.join(glitch_simple_firmware_dir, r"glitchsimple-CW308_STM32F3.hex")
    programmer.program("./glitch_bootloader.hex", memtype="flash", verify=True)
    programmer.close()

#flash()

# format output table
headers = ['target output', 'width', 'offset', 'success']
#glitch_display = GlitchResultsDisplay(headers)

# set glitch parameters
# trigger glitches with external trigger
scope.glitch.trigger_src = 'ext_single'
scope.glitch.repeat = 105

traces = []
outputs = []
widths = []
offsets = []

# named tuples to make it easier to change the scope of the test
Range = namedtuple('Range', ['min', 'max', 'step'])
width_range = Range(-20, 20, 1)  #Range(-40, 40, 0.39*5)
offset_range = Range(-20, 20, 1) #Range(-40, 40, 0.39*5)

# glitch cycle
scope.glitch.width = width_range.min
open('glitch_out.csv', 'w').close()
f = open('glitch_out.csv', 'a')
writer = csv.writer(f)
target.init()
print(scope)
while scope.glitch.width < width_range.max:
    scope.glitch.offset = offset_range.min
    while scope.glitch.offset < offset_range.max:
        # call before trace things here

        # flush the garbage from the computer's target read buffer
        target.ser.flush()

        # run aux stuff that should run before the scope arms here

        # target enters reset state
        scope.io.nrst = 'low'

        scope.arm()

        # run aux stuff that should run after the scope arms here

        # target exits reset state and starts execution
        scope.io.nrst = 'high'

        timeout = 50
        # wait for target to finish
        while target.isDone() is False and timeout:
            timeout -= 1
            time.sleep(0.01)

        try:
            ret = scope.capture()
            if ret:
                logging.warning('Timeout happened during acquisition')
        except IOError as e:
            logging.error('IOError: %s' % str(e))

        # get the results from the scope
        #trace = scope.get_last_trace()
        # read from the targets buffer
        output = target.ser.read(32, timeout=100)
        #traces.append(trace)
        outputs.append(output)  
        widths.append(scope.glitch.width)
        offsets.append(scope.glitch.width)

        # for table display purposes
        success = 'Glitch' in repr(output) # check for glitch success (depends on targets active firmware)
        data = [repr(output), scope.glitch.width, scope.glitch.offset, success]
        #glitch_display.add_data(data)
        writer.writerow(data)
        print(data)
        if str(data[3]) == "True":
            print("[+] Congrats ! Success glitch")
            exit()

        # run aux stuff that should happen after trace here
        scope.glitch.offset += offset_range.step

    scope.glitch.width += width_range.step
f.close()
#traces = np.asarray(traces)
# the rest of the data is available with the outputs, widths, and offsets lists
#glitch_display.display_table()
print('Done')
