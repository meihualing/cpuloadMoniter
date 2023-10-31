import curses
from curses import wrapper
import time
import os
import threading
from cpustat import get_current_cpuload


def get_current_terminal_size():
    size = os.get_terminal_size()
    terminal_columns = size.columns
    terminal_lines = size.lines
    #print ("columns is", terminal_columns, "lines is", terminal_lines)
    return terminal_columns,terminal_lines



CPUSTATFILE = "/proc/stat"

def get_current_cpuload():
    current_array_index = 0
    previous_array_index = 0
    number_array = [[j for j in range(8)] for i in range(2)]

    pad,curve_pad,command_pad = create_pads(1)
    i = 0
    while True:
        if current_array_index == 0 and previous_array_index == 0:
            current_array_index = 0
        elif current_array_index == 0 and previous_array_index == 1:
            current_array_index = 1
            previous_array_index = 0
        else:
            current_array_index = 0
            previous_array_index = 1
        #print(current_array_index, previous_array_index)

        cpustatfile = open(CPUSTATFILE, "r")
        for line in cpustatfile.readlines():
            data = line.split(' ')
            #print(data)
            number_array[current_array_index] = [int(x) for x in data[2:9]]
            if previous_array_index != current_array_index:
                current_cpuidle = number_array[current_array_index][3] - number_array[previous_array_index][3]
                current_cpuall = sum(number_array[current_array_index][2:9]) - sum(number_array[previous_array_index][2:9])
                #print('current_cpuidle is {}, current_cpuall is {}'.format(current_cpuidle, current_cpuall))
                current_cpuload = current_cpuidle/current_cpuall*100
                i = i+1 
                refresh_pads(pad,i,round(current_cpuload,2),curve_pad,command_pad)
                #print(current_cpuload)
            else:
                current_array_index = 1
            break # we just need to read the first line of this stat file here
        cpustatfile.close()
        time.sleep(3)


def create_pads(i):
    summary_pad = curses.newpad(4, 10)
    curve_pad = curses.newpad(10,30)
    command_pad = curses.newpad(2,40) 
    return summary_pad,curve_pad,command_pad


def refresh_pads(pad,i,cpuload,curve_pad,command_pad):
    columns, lines = get_current_terminal_size()
    #for y in range(0, 4):
    #    for x in range(0, 9):
    #        pad.addch(y,x, ord('a') + i)
    
    # Displays a section of the pad in the middle of the screen.
    # (0,0) : coordinate of upper-left corner of pad area to display.
    # (4,terminal_columns-80) : coordinate of upper-left corner of window area to be filled
    #         with pad content.
    # (8, terminal_columns-70) : coordinate of lower-right corner of window area to be
    #          : filled with pad content.
    pad.addstr(0,0,"cpuload:")
    pad.addstr(1,0,str(cpuload))
    pad.refresh(0,0, 4,columns-40, 8, columns-30)
    curve_pad.addch(0,10,ord('a') + i)
    curve_pad.addstr(0,0,"curve_pad")
    curve_pad.addstr(9,0,"curve_pad")
    curve_pad.refresh(0,0,0,0,10,30)
    command_pad.addch(0,12,ord('a') + i)
    command_pad.addstr(0,0,"command_pad")
    command_pad.addstr(1,0,"command_pad")
    command_pad.refresh(0,0,lines-2,0,lines-1,40)

    time.sleep(1)
    
     
def main(stdscr):
    # Clear screen
    stdscr.clear()

    columns, lines = get_current_terminal_size()
    print ("columns is", columns, "lines is", lines)
    time.sleep(1)

    # This raises ZeroDivisionError when i == 10.
    #for i in range(0, 9):
    #    v = i-10
    #    stdscr.addstr(i, i, '10 divided by {} is {}'.format(v, 10/v))

    stdscr.refresh()
    
    
    thread_01 = threading.Thread(target=get_current_cpuload, name="worker thread")  
    thread_01.setDaemon(True)
    thread_01.start() 
    
    #print ("we start the main thread")
    time.sleep(3)
   
    #here is the main thread, we handling the keyboard input commands.
    while True:
        input_key = stdscr.getkey()
        if input_key == 'q':
           print ("print now: ")
           print (input_key)
           time.sleep(1)
           break
        elif input_key == 't':
           print ("still alive...")
        else:
           #do nothing here, just update the CPUload print per second
           print ("print q to quit")



wrapper(main)
