#!/usr/bin/python3
# Threader3000 - Multi-threader Port Scanner
# A project by The Mayor
# v1.0.6
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

# Start Threader3000 with clear terminal
# subprocess.call('clear', shell=True)

def printBanner(printFlag):
    if printFlag:
        print("-" * 60)
        print("        Threader 3000 - Multi-threaded Port Scanner       ")
        print("                       Version 1.0.6c                     ")
        print("      A project by The Mayor (cli fork by TuxTheXplorer)  ")
        print("-" * 60)

# Main Function
def main(argv):
    socket.setdefaulttimeout(0.30)
    print_lock = threading.Lock()
    discovered_ports = []

# Welcome Banner
    # Take input as a command line argument instead of reading in from stdin
    # target = input("Enter your target IP address or URL here: ")
    target = ''
    usage = "usage: threader3000.py -u <Target-IP> -t <Thread-count>"
    error = ("Invalid Input")

    # Set default values
    threadCount = 200
    printBMsg = True
    ruNmap = False

    # CLI argument implementation
    '''
        TO-DO:
         - Add nmap output dirName (--output)
         - Tidy automate() function
         - Add nmap toggle (--scan)
         - Tidy long format
         - Quiet option (--quiet)
         - Interactive toggle (--interactive)
    '''

    # Command line argument handler
    try:
        opts, args = getopt.getopt(argv, "hu:t:iqso",["--help","--ip", "--thread", "--interactive", "--quiet", "--scan", "--output"])
    except getopt.GetoptError:
        print(usage)
        sys.exit(2)

    # Check is no arguments have been submitted
    if len(opts) == 0:
        # Checks if only one argument (probably IP)
        # was given and run threader on it.
        # REWRITE THIS TO ENABLE parsing of other args
        if len(argv) == 1:
            target = argv[0]
        else:
            print(usage)
            sys.exit(2)
    else:
        for opt, arg in opts:
            if opt in ('-h', '--help'):
                print(usage)
                sys.exit()
            elif opt in ('-u'):
                target = arg
            elif opt in ('-t', '--thread'):
                print(opts, args)
                threadCount = int(arg)
            elif opt in ('-q', '--quiet'):
                printBMsg = False
            elif opt in ('-i', '--interactive'):
            # Add vanilla threader here
            # Import it from orignial script OOB style
                pass
            elif opt in ('-s', '--scan'):
                ruNmap = True
            elif opt in ('-o', '--output'):
                pass


    # Print banner here, instead of at the beginning
    printBanner(printBMsg)
    try:
        t_ip = socket.gethostbyname(target)
    except (UnboundLocalError, socket.gaierror):
        print("\n[-]Invalid format. Please use a correct IP or web address[-]\n")
        sys.exit()
    #Banner
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
    print("Threader3000 recommends the following Nmap scan:")
    print("*" * 60)
    print("nmap -p{ports} -sV -sC -T4 -Pn -oA {ip} {ip}".format(ports=",".join(discovered_ports), ip=target))
    print("*" * 60)
    outfile = "nmap -p{ports} -sV -sC -Pn -T4 -oA {ip} {ip}".format(ports=",".join(discovered_ports), ip=target)
    t3 = datetime.now()
    total1 = t3 - t1

#Nmap Integration (in progress)
#    def automate():
#        choice = '0'
#       while choice == '0':
#        #if not ruNmap: 
#            print("Would you like to run Nmap or quit to terminal?")
#            print("-" * 60)
#            print("1 = Run suggested Nmap scan")
#            print("2 = Run another Threader3000 scan")
#            print("3 = Exit to terminal")
#            print("-" * 60)
#            choice = input("Option Selection: ")
#            if choice == "1":
#                try:
#                   print(outfile)
#                   os.mkdir(target)
#                   os.chdir(target)
#                   os.system(outfile)
#                   #The xsltproc is experimental and will convert XML to a HTML readable format; requires xsltproc on your machine to work
#                   #convert = "xsltproc "+target+".xml -o "+target+".html"
#                   #os.system(convert)
#                   t3 = datetime.now()
#                   total1 = t3 - t1
#                   print("-" * 60)
#                   print("Combined scan completed in "+str(total1))
#                   print("Press enter to quit...")
#                   input()
#                except FileExistsError as e:
#                   print(e)
#                   exit()
#            elif choice =="2":
#                main(sys.argv[1:])
#            elif choice =="3":
#                sys.exit()
#            else:
#                print("Please make a valid selection")
#                automate()
#        #else:
#        #   choice = '2'
#    automate()

if __name__ == '__main__':
    try:
        main(sys.argv[1:])
    except KeyboardInterrupt:
        print("\nGoodbye!")
        quit()
