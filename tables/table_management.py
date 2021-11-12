class tables:
    def __init__(self, clientID, grace, run_table, settings_table):
        self.clientID = clientID
        self.grace = grace
        self.run_table = run_table
        self.settings_table = settings_table

    def clientID_read(msg_subject):
        substring = msg_subject.partition("[")[2]
        clientID = substring.partition("]")[0]
        return clientID

    def table_read(name_table):
        table = {}
        file = open(name_table + ".txt", 'r')
        
        for line in file:
            if (line == '\n'):
                continue

            key, value_str = line.split()
            value = int(value_str)
            table[key] = value

        file.close()
        return table

    def settings_table_append(clientID, grace):
        file = open("settings_table.txt", 'a')
        grace_str = str(grace)
        file.write('\n' + clientID + ' ' + grace_str)
        file.close()
        return tables.table_read(name_table="settings_table")

    def run_table_append(clientID, counter):
        file = open("run_table.txt", 'a')
        counter_str = str(counter)
        file.write('\n' + clientID + ' ' + counter_str)
        file.close()
        return tables.table_read(name_table="run_table")
        
    def run_table_decrement_counter(run_table):
        lines = []

        for key in run_table:
            value = run_table[key] - 1
            value_str = str(value)
             
            if (key == list(run_table)[-1]):
                lines.append(key + ' ' + value_str)
            else:
                lines.append(key + ' ' + value_str + '\n')

        file = open("run_table.txt", 'w')
        file.writelines(lines)
        file.close()
        return 0             

    def run_table_check_counter(run_table):
        clientlist = []
        for key in run_table:
            if (run_table[key] < 0):
                clientlist.append(key)

        return clientlist
            
    def run_table_counter_reset(client, settings_table, run_table):
        lines = []
        counter = settings_table[client]

        for key in run_table:  
            value = run_table[key]            
            value_str = str(value)

            if (key == client):
                value_str = str(counter)

            if (key == list(run_table)[-1]):
                    lines.append(key + ' ' + value_str)
            else:
                    lines.append(key + ' ' + value_str + '\n')

        file = open("run_table.txt", 'w')
        file.writelines(lines)
        file.close()

        return 0

    def add_client_to_tables(clientID, grace):
        tables.settings_table_append(clientID, grace)
        tables.run_table_append(clientID, grace)       
        return 0