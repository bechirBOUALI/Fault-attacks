/*
    This file is part of the ChipWhisperer Example Targets
    Copyright (C) 2012-2015 NewAE Technology Inc.

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
*/

#include <stdio.h>
#include "hal.h"


void uart_puts(char * s){
    while(*s){
        putch(*(s++));
    }
}


void sure_glitch(void)
{

    volatile uint32_t victim1 = 0xffffffff;
    volatile uint32_t victim2 = 0xffffffff;

    led_ok(1);
    led_error(0);


    uart_puts("Before\n");

    trigger_high();
    trigger_low();

    uart_puts("After\n");
    
    while((victim1 == 0xffffffff) && (victim2 == 0xffffffff))
    {
        ;
    }

    uart_puts("Glitch\n");
}

int main(void){

    platform_init();
    init_uart();    
    trigger_setup();

    /* Uncomment this to get a HELLO message for debug */
    putch('h');
    putch('e');
    putch('l');
    putch('l');
    putch('o');
    putch('\n');
    
    //This is needed on XMEGA examples, but not normally on ARM. ARM doesn't have this macro normally anyway.
    #ifdef __AVR__
    _delay_ms(20);
    #endif
        
    while(1){
      sure_glitch();
    }

    
        
    return 1;
}
