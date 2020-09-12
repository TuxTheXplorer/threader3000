#!/usr/bin/python3
# Threader3000 - Multi-threader Port Scanner
# A project by The Mayor 
# v1.0.6c
# https://github.com/dievus/threader3000
# Licensed under GNU GPLv3 Standards.  https://www.gnu.org/licenses/gpl-3.0.en.html
#
# Single line cli mode by TuxTheXplorer
# https://github.com/TuxTheXplorer/threader3000

import socket
import os
import signal
import time
import threading
import sys
import subprocess
import getopt
from queue import Queue
from datetime import datetime
from vanillaThreader import threaderOriginal

# Banner to show when running threader3000
# Controlled by the "printFlag" variable
def printBanner(printFlag):
    if printFlag:
        print("-" * 60)
        print("        Threader 3000 - Multi-threaded Port Scanner       ")
        print("                       Version 1.0.6c                     ")
        print("      A project by The Mayor (cli fork by TuxTheXplorer)  ")
        print("-" * 60)

# Extended help menu
def printHelp():
    print("Usage: threader3000.py [options]")
    print("  options:")
    print("    -h,    Print this help message")
    print("    -q,    Hide banner when running")
    print("    -t,    Set thread count")
    print("    -u,    Set target IP")
    print("    -i,    Run the original threader3000 program")
    print("    -s,    Automatically run nmap on open ports")

# Main Function
def main(argv):
    socket.setdefaulttimeout(0.30)
    print_lock = threading.Lock()
    discovered_ports = []

    # Setting default values for variables
    target = ""
    usage = "Usage: threader3000.py -u <Target-IP> [options]"
    threadCount = 200
    printBMsg = True
    ruNmap = False

    # CLI argument implementation
    '''
        TO-DO:
        - Detect invalid values within options and print error message accordingly
    '''

    # Command line argument handler
    try:
        opts, args = getopt.getopt(argv, "hu:t:iqs")
    except getopt.GetoptError:
        print(usage)
        sys.exit(2)

    # Check is no arguments have been submitted
    if len(argv) == 0:
        print(usage)
        sys.exit()

    elif len(argv) >= 1:
        # This works don't touch it
        if len(opts) == 0:
            argv.insert(0,'-u')
            opts, args = getopt.getopt(argv, "hu:t:iqs")

        # Filter input
        # In case there is a single argument passed
        if len(opts) == 1:
            #print(opts[0][0])
            if opts[0][0] not in ('-h', '-i', '-t', '-q', '-u', '-s'):
                target = argv[0]

            elif opts[0][0] in ('-i'):
                threaderOriginal()
            else:
                pass
            
        # This behaves a bit oddly. Long options don't work.
        for opt, arg in opts:
            #print(opt)
            if opt in ('-h'):
                printHelp()
                sys.exit()

            elif opt in ('-u'):
                target = arg

            elif opt in ('-t'):
                threadCount = int(arg)

            elif opt in ('-q'):
                printBMsg = False

            elif opt in ('-i'):
                if len(opt) > 1:
                    print("Interactive mode is meant to be standalone.")
                    print("No need to supply any other arguments with -i")
                    sys.exit()
                else:
                    threaderOriginal()

            elif opt in ('-s'):
                ruNmap = True
    else:
        print(usage)
        sys.exit(2)

    # Print banner here, instead of at the beginning
    printBanner(printBMsg)
    try:
        t_ip = socket.gethostbyname(target)
    except (UnboundLocalError, socket.gaierror):
        print("\n[-]Invalid format. Please use a correct IP or web address[-]\n")
        sys.exit()

    # Small banner (target & time)
    print("-" * 60)
    print("Scanning target "+ t_ip)
    print("Time started: "+ str(datetime.now()))
    print("-" * 60)
    t1 = datetime.now()

    def portscan(port):

       s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
       
       try:
          conx = s.connect((t_ip, port))
          with print_lock:
             print("Port {} is open".format(port))
             discovered_ports.append(str(port))
          conx.close()

       except (ConnectionRefusedError, AttributeError, OSError):
          pass

    def threader():
       while True:
          worker = q.get()
          portscan(worker)
          q.task_done()
      
    q = Queue()
     
    #startTime = time.time()
    
    for x in range(threadCount):
       t = threading.Thread(target = threader)
       t.daemon = True
       t.start()

    for worker in range(1, 65536):
       q.put(worker)

    q.join()

    t2 = datetime.now()
    total = t2 - t1
    print("Port scan completed in "+str(total))
    print("-" * 60)

    if not ruNmap:
        print("\nThreader3000 recommends the following Nmap scan:")
        print("*" * 60)
        print("nmap -p{ports} -sV -sC -T4 -Pn -oA {ip} {ip}".format(ports=",".join(discovered_ports), ip=target))
        print("*" * 60)
    outfile = "nmap -p{ports} -sV -sC -Pn -T4 -oA {ip} {ip}".format(ports=",".join(discovered_ports), ip=target)
    t3 = datetime.now()
    total1 = t3 - t1


    def nmapScan():
        try:
           print(outfile)
           os.mkdir(target)
           os.chdir(target)
           os.system(outfile)
           #The xsltproc is experimental and will convert XML to a HTML readable format; requires xsltproc on your machine to work
           #convert = "xsltproc "+target+".xml -o "+target+".html"
           #os.system(convert)
           t3 = datetime.now()
           total1 = t3 - t1
           print("-" * 60)
           print("Combined scan completed in "+str(total1))
           sys.exit(0)
        except FileExistsError as e:
           print(e)
           sys.exit()

#Nmap Integration (in progress)
    def automate():
        choice = '0'
        while choice == '0':
            if not ruNmap: 
                print("Would you like to run Nmap or quit to terminal?")
                print("-" * 60)
                print("1 = Run suggested Nmap scan")
                print("2 = Run another Threader3000 scan")
                print("3 = Exit to terminal")
                print("-" * 60)
                choice = input("Option Selection: ")
                if choice == "1":
                    nmapScan()
                elif choice == "2":
                    main(sys.argv[1:])
                elif choice == "3":
                    sys.exit()
                else:
                    print("Please make a valid selection")
                    automate()
            else:
                print("You choose to run nmap automatically")
                nmapScan()
    automate()

if __name__ == '__main__':
    try:
        main(sys.argv[1:])
    except KeyboardInterrupt:
        print("\nGoodbye!")
        quit()
