import tkinter
from tkinter import filedialog

import DB_Utils
import DB_Utils as db
import os.path

# Module Globals
advertisers = []
# Methods


def is_new_advertiser(_advertiser):
    for advertiser in advertisers:
        if advertiser.address == _advertiser.address:
            return False

    return True


def update_advertisers(_advertiser):
    for advertiser in advertisers:
        if advertiser.address == _advertiser.address:
            advertiser.item_count += 1
            advertiser.last_time_stamp = _advertiser.first_time_stamp
            return False

    return True


def get_file_name():
    _file = tkinter.StringVar()
    try:
        _file.set(filedialog.askopenfilename(filetypes=[("Ellisys Raw Packet Import Format", "*.bttrp")]))
        # items = get_lines(_file.get())
    except ValueError:
        pass
#    finally:
#        return _file.get()

def Table_Schemas(table_name):

    if table_name == "line_items":
        create_table_string = """ CREATE TABLE IF NOT EXISTS line_items (
                        id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                        time integer,
                        aa text,
                        rssi real,
                        rfchannel integer,
                        phy text,
                        rawdata text,
                        header text,
                        pdu_type text,
                        flags text,
                        length integer,
                        data text,
                        address text
                    );"""
        return create_table_string


def insert_queries(qname):
    if qname == "line_item_insert":
        insert_query_string = """ INSERT INTO line_items (
                        time,
                        aa,
                        rssi,
                        rfchannel,
                        phy,
                        rawdata,
                        header,
                        pdu_type,
                        flags,
                        length,
                        data,
                        address) """
        return insert_query_string


def select_advertiser_query(advertiser_address):
#    select_query_string = """SELECT id, aa, address FROM line_items WHERE id=50"""
#    return select_query_string

    select_query_string = """ SELECT 
                                time, 
                                (time - lag (time, 1, time) OVER (ORDER BY id)) deltafromprevious
                            FROM line_items 
                            WHERE address = \"""" + advertiser_address + """\" 
                            AND rfchannel = 0 
                            AND pdu_type = 'ADV_IND'
                            """
    return select_query_string


def select_advertiser_query_x(advertiser_address):
#    select_query_string = """SELECT id, aa, address FROM line_items WHERE id=50"""
#    return select_query_string

    select_query_string = """ SELECT 
                                time
                            FROM line_items 
                            WHERE address = \"""" + advertiser_address + """\" 
                            AND rfchannel = 0
                            AND pdu_type = 'ADV_IND'                     
                            """
    return select_query_string


def select_advertiser_query_y(advertiser_address):
#    select_query_string = """SELECT id, aa, address FROM line_items WHERE id=50"""
#    return select_query_string

    select_query_string = """ SELECT 
                                (time - lag (time, 1, time) OVER (ORDER BY id)) deltafromprevious
                            FROM line_items 
                            WHERE address = \"""" + advertiser_address + """\" 
                            AND rfchannel = 0
                            AND pdu_type = 'ADV_IND'
                            """
    return select_query_string


def select_advertiser_query_bucketed_xy(advertiser_address):
    select_query_string = """ SELECT 
                            ROUND(time/1000000000, 1) AS Bucket, 5000000000/COUNT(*)
                            FROM line_items 
                            WHERE address = \"""" + advertiser_address + """\" 
                            AND rfchannel = 0
                            AND pdu_type = 'ADV_IND'
                            GROUP BY time/5000000000
                            """
    return select_query_string


def select_connection_ind_query():
    select_query_string = """ SELECT
                                *
                                FROM line_items
                                WHERE pdu_type = 'CONNECT_IND'
                                """
    return select_query_string


def get_lines(_source_file, _data_file, pbar, parent):
    try:
        print(_source_file)
        print(_data_file)
        # Ensure fresh new database


        con = db.connect_to_db(_data_file)

#        result = db.create_table(con, "CREATE TABLE line_items(id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, time INTEGER, aa CHAR(10))")
        db.create_table(con, Table_Schemas("line_items"))
#        result = db.create_table(con, "CREATE TABLE advertisers(id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, firsttime INTEGER, address CHAR(10))")
        cur = db.get_cursor(con)

        insert_query = tkinter.StringVar()
#        insert_query.set(insert_queries("line_item_insert"))
        file1 = open(_source_file, 'r')
        lines = file1.readlines()
        linecount = len(lines)
        pbar['value'] = 100
        file1.close()
#        print(linecount)
        items = []
        x=0
        for line in lines:
            x += 1
            if (x % 100) == 0:
#                print(x)
#                print(len(advertisers))
                pbar['value'] = int((x/linecount)*100)
#                parent.update_idletasks()
                parent.update()

#            print(x)
            if len(line.split()) > 5:
                this_item: Imported_Event_Line = Imported_Event_Line(line)
                items.append(this_item)
                if this_item.packet_type() == "Advertising":
#                    _advertiser = Advertiser(this_item)
                    if this_item.advertiser is None:
                        print('null advertiser')
                    elif update_advertisers(this_item.advertiser):
                        advertisers.append(this_item.advertiser)
                        print(this_item.advertiser.address)
#                print(len(advertisers))
#                print(this_item.data_record())
                insert_query.set(insert_queries("line_item_insert") + " VALUES " + this_item.data_record() + ";")
                db.insert_query(con, insert_query.get())
#        db.close_cursor(cur)
        db.commit(con)
        db.close_connection(con)
        print("End of getlines")
        print("Items: " + str(len(items)))
        print("Advertisers: " + str(len(advertisers)))
        return advertisers
    except ValueError:
        print("exception get_lines")
        pass


def get_advertiser_timing_data(data_file, advertiser_address):
    # query_string = select_advertiser_query(advertiser_address)
    # query_x = select_advertiser_query_x(advertiser_address)
    # query_y = select_advertiser_query_y(advertiser_address)
    query_buckets = select_advertiser_query_bucketed_xy(advertiser_address)
    con = db.connect_to_db(data_file)
    # results = db.select_query(con, query_string)
    # resultsx = db.select_query(con, query_x)
    # resultsy = db.select_query(con, query_y)
    resultsxy = db.select_query(con, query_buckets)
    db.close_connection(con)
    return resultsxy



class Imported_Event_Line:
    def __init__(self, line: str):
        self.time = ""
        self.aa = ""
        self.rssi = ""
        self.rfchannel = ""
        self.phy = ""
        self.rawdata = ""
        self.header = ""
        self.pdu_Type = ""
        self.flags = ""
        self.length = ""
        self.data = ""
        self.address = ""
        self.advertiser = None
        things = line.split()
        for thing in things:
            iotas = thing.split("=")
            if len(iotas)>1:
                if iotas[0] == "time":
                    self.time = iotas[1]
                elif iotas[0] == "aa":
                    self.aa = iotas[1]
                elif iotas[0] == "rssi":
                    self.rssi = iotas[1]
                elif iotas[0] == "rfchannel":
                    self.rfchannel = iotas[1]
                elif iotas[0] == "phy":
                    self.phy = iotas[1]
                elif iotas[0] == "rawdata":
                    break

        big_splits = line.split("\"")
        if len(big_splits) > 1:
            self.rawdata = big_splits[1]
            self.data_strings = self.rawdata.split()
            if self.packet_type() == "Advertising":
                if len(self.data_strings) >= 8:
                    self.advertiser = Advertiser(self)
                    self.address = " ".join(str(e) for e in self.advertiser.address)

        self.header = "header"
        self.pdu_Type = self.pdu_type()
        self.flags = "flags"
        self.data = self.rawdata
        self.length = len(self.rawdata)

    def data_record(self):
        _lstring = "({}, '{}', {}, {}, '{}', '{}', '{}', '{}', '{}', {}, '{}', '{}')"
#        print(_lstring.format(self.time, self.aa, self.rssi, self.rfchannel, self.phy, self.rawdata, self.header, self.pdu_Type, self.flags, self.length, self.data, self.address))
        return _lstring.format(self.time, self.aa, self.rssi, self.rfchannel, self.phy, self.rawdata, self.header, self.pdu_Type, self.flags, self.length, self.data, self.address)

#        return self


    def packet_type(self):
        if self.aa == "0x8E89BED6":
            return "Advertising"
        else:
            return "Data"

    def pdu_type(self):
        _pdu_num = self.data_strings[0][1]
        _pdu_type_int = int(self.data_strings[0], 16)
        _mask = int(15)
        _pdu_type_masked = _pdu_type_int & _mask
        _rfu = _pdu_type_int & 16
        _chsel = _pdu_type_int & 32
        _TxAdd = _pdu_type_int & 64
        _RxAdd = _pdu_type_int & 128
#        print(_pdu_num)
        if self.packet_type() == "Advertising":


            if _pdu_num == "0":
                return "ADV_IND"
            elif _pdu_num == "1":
                return "ADV_DIRECT_IND"
            elif _pdu_num == "2":
                return "ADV_NONCONN_IND"
            elif _pdu_num == "3":
                return "SCAN_REQ"
            elif _pdu_num == "4":
                return "SCAN_RESP"
            elif _pdu_num == "5":
                return "CONNECT_IND"
            elif _pdu_num == "6":
                return "ADV_SCAN_IND"
            elif _pdu_num == "7":
                return "ADV_EXT_IND"
            elif _pdu_num == "8":
                return "AUX_CONNECT_RSP"
            else:
                return _pdu_num
        elif self.packet_type() == "Data":
            return _pdu_num


class Advertiser:
    address = []
    item_count = 0
    first_time_stamp = 0
    last_time_stamp = 0

    def __init__(self, imported_event_line):
        x = 7
        y = len(imported_event_line.data_strings)
        self.address = []
        if y < x:
            x = y
        while x >= 2:
            self.address.append(imported_event_line.data_strings[x])
            x = x-1
        self.first_time_stamp = imported_event_line.time
        self.last_time_stamp = imported_event_line.time
        self.item_count = 1


def parse_reverse_endianess(bytes):
    result = []
    if len(bytes)>0:
        x = len(bytes)
        while x>0:
            x = x - 1
            result.append(bytes[x])
    return result

def parse_reverse_endianess_to_string_space(bytes):
    result = ""
    if len(bytes)>0:
        x = len(bytes)
        while x>0:
            x = x - 1
            result = result + bytes[x]
            if x>0:
                result = result + " "
    return result

def parse_reverse_endianess_to_string_0x_nospace(bytes):
    result = ""
    if len(bytes)>0:
        x = len(bytes)
        while x>0:
            x = x - 1
            result = result + str(bytes[x])
    return result


def find_connections(datafile, addr = []):
    select_query = select_connection_ind_query()
    con = db.connect_to_db(datafile)
    results = db.select_query(con, select_query)
    connections = []
    for result in results:
        temp_connection = BLE_Connection(result)
        if len(addr) > 0:
            if ((str(temp_connection.central_address) == addr)) or (str(temp_connection.peripheral_address) == addr):
                connections.append(temp_connection)
        else:
            connections.append(temp_connection)

    if len(connections)>0:
        for connection in connections:

            select_query = """SELECT
                            MIN(time)
                            FROM line_items
                            WHERE aa = """ + "'" + connection.access_address + "'"
            results = db.select_query(con, select_query)
            tempmin = results[0][0]
            connection.first_data_packet_timestamp = tempmin
            select_query = """SELECT
                            MAX(time)
                            FROM line_items
                            WHERE aa = """ + "'" + connection.access_address + "'"
            results = db.select_query(con, select_query)
            tempmax = results[0][0]
            connection.last_data_timestamp = tempmax

    con.close()
    return connections


class BLE_Connection:
    central_address = []
    peripheral_address = []
    access_address = []
    connect_ind_timestamp = 0
    first_data_packet_timestamp = 0
    last_data_timestamp = 0

    def __init__(self, connect_ind_record):
        data_string = connect_ind_record[6]
        data_bytes = data_string.split()
        self.central_address = parse_reverse_endianess_to_string_space(data_bytes[2:8])
        self.peripheral_address = parse_reverse_endianess_to_string_space(data_bytes[8:14])
        self.access_address = "0x" + parse_reverse_endianess_to_string_0x_nospace(data_bytes[14:18])
        self.connect_ind_timestamp = int(connect_ind_record[1])


#    def set_first_and_last_packet_timestamps(self):










