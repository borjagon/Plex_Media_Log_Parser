
#!/usr/bin/env python
#Borja González Rivero March 2016


from sys import argv
import operator
from datetime import datetime

#function returns date and time 
def Get_Time(line,year):

	date_time = line.split(" [")[0]
	date_time = date_time.replace(",","")
	new_time = date_time.split(year)[1]
	new_date = date_time.split(new_time,1)[0]
	new_date = new_date.replace(",", "")
	parsed_date_time = new_date + new_time
			
	return parsed_date_time
			
#function returns plex client ID 		
def Get_Plex_Client_ID(line):

	plex_client_ID = line.split("X-Plex-Client-Identifier=")[1]
	plex_client_ID = plex_client_ID.split("&")[0]
	
	return plex_client_ID
		
#function returns seconds given time in HH:MM:SS		
def Get_Seconds(time):

	seconds = str(time).split(':')
	seconds = int(seconds[0]) * 3600 + int(seconds[1]) * 60 + int(seconds[2])
	
	return seconds
	
#function transforms time to seconds from first time 		
def Get_Time_In_Seconds(first_time, time):

	first_time = datetime.strptime(first_time, '%b %d %Y %H:%M:%S')
	time = datetime.strptime(time, '%b %d %Y %H:%M:%S')
	time = time - first_time
	time = Get_Seconds(time)
	
	return time
		
# function returns window size according to user bit rate 
#Change bit rate range values to suit bandwidth demand
def Get_Size(bitrate):

	size = 0
	
	if (int(bitrate) > 3000):
		size = 2
		
	elif (int(bitrate) > 1600 and int(bitrate) < 3000):
		size = 4
		
	elif (int(bitrate) > 400 and int(bitrate) < 1600):
		size = 8
		
	elif (int(bitrate) > 200 and int(bitrate) < 400): 
		size = 16
		
	else:
		size = 32
	
	return size	
	
		
#function generates xml file with desired format and data  
def Output(mylist):

	i = 0
	
	file = open('CCSim_Plex_Input.xml','w')
	file.write('<?xml version="1.0" encoding="UTF-8"?><input>\n')
	
	for i in range(0, len(mylist)):
	
		file.write('<task>\n')
		file.write('\t<id>' + str(mylist[i][1]) + '</id>\n')
		file.write('\t<t_arrive>' + str(mylist[i][0]) + '.0</t_arrive>\n')
		file.write('\t<size>' + str(mylist[i][2]) +  '</size>\n')
		file.write('\t<w_size>' + str(mylist[i][3]) + '</w_size>\n')
		file.write('\t<t_leave>' + str(mylist[i][4]) + '.0</t_leave>\n')
		file.write('</task>\n')
		i = i + 1    
		  
	file.write('</input>\n')
	file.close()
	
	
#Gets all the info, processes it and stores it in a list	
def Parser():

	start_time = 0
	first_time = datetime.strptime('Sep 30 3000 19:10:34', '%b %d %Y %H:%M:%S')
	bitrate = 0
	size = 0
	ID = 0
	year = "2016" # Change this value depending on year
	
	dict_ID = {} #store client IDs
	mylist = [] #store all events from clients in appropriate format and in chronological order
	start_times = []# store times of arrival
	
	for line in FILE:
		
		if ('Request: ' in line and 'X-Plex-Client-Identifier' in line):#Looks for client ID
			
			plex_client_ID =  Get_Plex_Client_ID(line)
			
			
		if ('Direct Play is disabled' in line): #Looks for Time of Arrival
			
			start_time = Get_Time(line,year)
			
		if ('Clipped max bitrate to' in line): #Looks for bit rate
		
			bitrate = line.split("to ")[1]
			bitrate = bitrate.split(" based")[0]
			bitrate = bitrate.split("Kbps")[0]
			size = Get_Size(bitrate)
			bitrate_time = Get_Time(line,year)
			
			if (start_time not in start_times):
			
				start_times.append(start_time)
							
			if (not plex_client_ID in dict_ID): #Changes Plex ID to number ID
				
				dict_ID[plex_client_ID] = ID	
				ID = ID + 1
			
			first_time = start_times[0]
			time_seconds = Get_Time_In_Seconds(first_time,bitrate_time)

			if (time_seconds not in mylist): #Saves info to list
			
					mylist.append([time_seconds, dict_ID[plex_client_ID], bitrate, size])
				
		if ('Client [' in line and 'stopped' in line):# Looks for Time of Departure
		
			stop_time = Get_Time(line,year)
			client = line.split('Client [')[1]
			client = client.split(']')[0]
			played = line.split("of ")[1]
			played = played.split("/")[0]
				
			if (client in dict_ID):
			
				stop_time = Get_Time_In_Seconds(first_time,stop_time)
				
				for sublist in mylist: #Adds stop time to corresponding client
				
					if sublist[1] == dict_ID[client]:
						sublist.append(stop_time)
						
    	
	Output(mylist)#Calls function to generate output file

#Checks for correct input (Only one file per execution)
if (len(argv) == 2 and '.log' in argv[1]):
	
	logfile = open(argv[1],'r')
	FILE = logfile.readlines()
	Parser()
	logfile.close()
	
else:

	print "Usage: ./Plex_Media_Log_Parser.py [log_file_name.log]"
	