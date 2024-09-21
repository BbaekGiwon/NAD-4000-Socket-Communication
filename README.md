# NAD-4000-Socket-Communication
Socket Communication program for Metal Detector NAD-4000

## How to use
1. Write IP and Port
2. Choose CMD and Data
3. Get the decoded information

## Function & Algorithm
- decode_string_to_hex : decode string data from machine to hex
- cal_send_DATA_CMD_3A : if CMD is 3A, calculate the data to hex
- cal_LRC : calculate the LRC value
- decode_CMD_xx : decode the message from machine by each form of CMD
- print_result : print the result by calling other funcions
- terminate_socket : terminate the socket after 10 sec
