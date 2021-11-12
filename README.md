# outlook-automated-backup-control
Backup monitoring on a mailbox:
In this mailbox there will be backup logs.

The identification will based on the following syntax:
[#ID_BACKUP_GRACEPERIOD]

We register this in two tables: run-table, and settings-table.

*settings-table:*
#ID_BACKUP_GRACEPERIOD GRACEPERIOD

The settings-table serves as the main database for storing clients and graceperiods respectively. This table is immutable, except when a new client has been identified, then the settings-table will be appended accordingly.

*run-table:*
#ID_BACKUP_GRACEPERIOD COUNTER

The run-table serves as a way to check whether backup logs are sent. The counter decrements after each iteration of the script. If counter < 0, then a notice will be issued to support.

A parser function will parse through each backup log to decide whether or not this log needs a follow up.
This function results in a string:
‘alert’ = log needs follow up, issue ticket
‘ok’     = log needs no follow up, no ticket
