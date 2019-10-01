# Fault attacks using Chipwhisperer-Lite

## Overview

* Chipwhisperer is an open source tool chain for embedded hardware security research. In this project I used ChipWhisperer-Lite (`ChipWhisperer-Lite 32-bit ARM target [1]`) which is a complete package for exploring how side-channel power analysis and glitching attacks work against the included target device. To mount a fault attack using chipwhisperer some parametres need to be adjusted.
* Basically I published this work in order to help people who want to test fault attacks find the right parameters of success glitch because it will take a quite important time to find the right combination.  
* In both attack types the target is STM32F3. Because it is given with the ChipWhisperer-Lite so no hardware setup needed
* Firmware.c: the firmware running in the target board
* STM32F3-sure_glitch.hex : the hex format of the firmware
* stm32f3_clock_glitch.py : script used to mount clock glitch
* *stm32f3_power_glitch.py : script used to mount power gltich

## Clock Glitching

* A clock glitching consists at controlling the target's clock, so by changing the pace of the clock the attacker could change the behaviour of the target by bypassing instruction. 
* To succeed a clock glitch you need to adjust only the width and the offset of a glitch. Because we are controlling the pace of CPU's clock so the compare instruction of the loop easly could bypassed by clock glitch that's why success glitch happens more often compared to vcc glitch. 

### Success glitchs:

    succes glitch1:
      width = -1.171875
      offset = -19.921875
    success glitch2:
      width = -16.40625 
      offste = 14.0625
    success glitch3:
      width = -8.203125 
      offset = 5.859375
    success glitch4: 
      width = -1.171875
      offste = -18.75

## Power supply glitch:

* The VCC or power glitch injects a fault in the system by driving the supply voltage out of the circuit stable range.
* After several attempts i found that the glitch success is persistent with width range[10,14] offset range[-14,-5] and ext_offset range [10,30]

### Success glitchs:

	success glitch1:
		width = 12.89
		offset = -9
		extoffset = 21
	success gltich2:
		width = 12.890625,
		offset = -9.375
		extoffset = 16
	success glitch3:
		width = 12.890625
		offset = -9.375
		extoffset = 11
	success glitch4:
		width = 13.28125
		offset = -9.375
		extoffest = 11


## Resources:

[1] Chipwhisperer-Lite python APIs: <https://chipwhisperer.readthedocs.io/en/latest/api.html#chipwhisperer.scopes.OpenADC.clock>
[2] ChipWhisperer-Lite Documentations : <https://chipwhisperer.readthedocs.io/en/latest/index.html>
[3] Vcc glitch attck using ChipWhisperer-Lite : <https://chipwhisperer.readthedocs.io/en/latest/tutorials/fault_2-openadc-cwlitearm.html#tutorial-fault-2-openadc-cwlitearm>
