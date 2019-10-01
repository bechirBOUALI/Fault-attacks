from __future__ import print_function, division

import time
import logging
from collections import namedtuple
import csv

import numpy as np
import matplotlib.pyplot as plt

import chipwhisperer as cw
from chipwhisperer.capture.api.programmers import STM32FProgrammer

from bokeh.plotting import figure, show, output_file
from bokeh.io import output_notebook
from bokeh.models import CrosshairTool


logging.basicConfig(level=logging.WARN)
scope = cw.scope()
target = cw.target(scope)

# setup parameters needed for glitch the stm32f
scope.glitch.clk_src = 'clkgen'

scope.gain.gain = 45
scope.adc.samples = 3000
scope.adc.offset = 0
scope.adc.basic_mode = "rising_edge"
scope.clock.clkgen_freq = 7370000
scope.clock.adc_src = "clkgen_x4"
scope.trigger.triggers = "tio4"
scope.io.tio1 = "serial_rx"
scope.io.tio2 = "serial_tx"
scope.io.hs2 = "clkgen"
scope.io.glitch_hp = False
scope.io.glitch_lp = True
target.go_cmd = ""
target.key_cmd = ""

# program the stm32f with the built hex file
def flash():
    programmer = STM32FProgrammer()
    #programmer = XMEGAProgrammer()
    programmer.scope = scope
    programmer._logging = None
    programmer.open()
    programmer.find()
    programmer.erase()
    programmer.program("./STM32F3-sure_glitch.hex", memtype="flash", verify=True)
    programmer.close()



#flash()


def read_buffer(): 
    line = "" 
    
    for j in range(20):

        while "\n" not in line: 
            time.sleep(0.1) 
            line += target.ser.read(15) 
          
        lines = line.split("\n") 
        if len(lines) > 1: 
            line = lines[-1] 
        else: 
            line = "" 
          
        while "\n" not in line: 
            time.sleep(0.1) 
            line += target.ser.read(15) 
         
        if "hello" in line: 
           return "Target crashed" 

        return line
# format output table
headers = ['target output', 'width', 'offset', 'success','ext_offset','repeat']

# set glitch parameters
# trigger glitches with external trigger
scope.glitch.output = 'glitch_only'
scope.glitch.trigger_src = 'ext_single'
#scope.glitch.offset_fine = 24
#scope.glitch.ext_offset = 9
scope.glitch.arm_timing = 'after_scope'


traces = []
outputs = []
widths = []
offsets = []

# named tuples to make it easier to change the scope of the test
Range = namedtuple('Range', ['min', 'max', 'step'])
width_range = Range(10,14, 0.39)  
offset_range = Range(-11, -5, 0.39 ) 

# glitch cycle

open('glitch_stm32f3_out.csv', 'w').close()
f = open('glitch_stm32f3_out.csv', 'a')
writer = csv.writer(f)


target.init()
print(scope)


for repeat in range(1,2):

	scope.glitch.repeat = repeat
	scope.glitch.width = width_range.min

	while scope.glitch.width < width_range.max:
		scope.glitch.offset = offset_range.min
		while scope.glitch.offset < offset_range.max:
            # call before trace things here
			for extOffset in range(10,30):

				scope.glitch.ext_offset = extOffset
				# flush the garbage from the computer's target read buffer
				target.ser.flush()

				# run aux stuff that should run before the scope arms here

				scope.io.nrst = 'low'

				scope.arm()
				#time.sleep(0.01)

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
				trace = scope.get_last_trace()
				# read from the targets buffer

				output = target.ser.read(32, timeout=10)
				success = 'Glitch' in repr(output)
				data = [repr(output), scope.glitch.width, scope.glitch.offset, success, extOffset, repeat]

				writer.writerow(data)

                                #In case you want to print the voltage trace uncomment the lines below 
				# output_file("./traces/xmega_traces/single_traces_with_glitch.html")
				# p = figure(plot_width=1200, plot_height=600, title = "single_w=-38_offs=38_traces_with_glitch]")
				# x_range = range(0, len(trace))
				# p.line(x_range, trace)
				# show(p)


				if str(data[3]) == "True":
					print("[+] Congrats! it's success glitch")
                                        #print(data)
					exit()


			scope.glitch.offset += offset_range.step
		scope.glitch.width += width_range.step


f.close()
print('Done')


scope.dis()
target.dis()
