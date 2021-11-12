#!/usr/bin/env python
from mail_client import imapClient, smtpClient
from tables.table_management import tables
from parser import alertParser
import lib.schedule
import time

def agent():
    backup_tables = tables
    imap = imapClient(  recipient="email@domain.com",
                        password="passphrase")
    imap.login()

    smtp = smtpClient(  sender="email@domain.com", 
                        password="passphrase")
    smtp.login()

    messages = imap.get_messages(subject='')

    # looping until no more messages
    for msg in messages:
        
        # check if valid ID format
        if not '#' in msg['subject'] :
            print("Unknown mail received, forwarding")
            smtp.send_message(  receiver="email@domain.com",
                                msg_subject=("Unknown mail received: " + msg['subject']),
                                msg_body=msg['body'])

            imap.move_message(msg['num'])  
         
        # Run remainder of code. If the else has not been reached, a new iteration of the loop will start   
        else: 
            # check if backup/clientID is known in settings_table
            clientID = backup_tables.clientID_read(msg['subject'])
            if clientID not in backup_tables.table_read(name_table="settings_table"):
                tables.add_client_to_tables(clientID, grace=1)   
                smtp.send_message(  receiver="email@domain.com",
                                    msg_subject=("Added to database: " + clientID),
                                    msg_body=("Handle accordingly"))
        
            # regardless of result parser, run tables.run_table_counter_reset for the msg it retrieves
            tables.run_table_counter_reset( client=clientID,
                                            settings_table=backup_tables.table_read(name_table="settings_table"), 
                                            run_table=backup_tables.table_read(name_table="run_table"))

            result = alertParser(msg['subject'], msg['body'])
            imap.move_message(msg['num'])

            if (result == 'alert'):
                smtp.send_message(  receiver="email@domain.com",
                                    msg_subject=("FW: " + msg['subject']),
                                    msg_body=(msg['body']))      

            # -------------------------------------- END LOOP --------------------------------------

    tables.run_table_decrement_counter(run_table=backup_tables.table_read(name_table="run_table"))

    missing_clients = tables.run_table_check_counter(run_table=backup_tables.table_read(name_table="run_table"))
    for client in missing_clients: 
        smtp.send_message(  receiver="email@domain.com",
                            msg_subject=("Missing backup report for: " + client),
                            msg_body="Handle accordingly")    

    # as soon as loop and table managing is done, proceed to logout smtp and imap and stop script.
    smtp.logout()
    imap.logout()

lib.schedule.every().day.at("07:00").do(agent)

def main():
    while True:
        lib.schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    main()
