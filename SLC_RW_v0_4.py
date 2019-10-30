import asyncore, socket, random, time, re, string, struct, array, platform, mysql.connector, sys, getopt, logging, math
from db_cnx import MySQLClient

_verbose = False
_debug = False
_read =False
_write = False
_store = False
_address = ""
_database = ""
_table = ""
_value = 0
_units = "DegF"
_timeoutCTR = 0
_TTL =256
_length = 1

class ParsedDataAddress():
    RE1 = r"(?i)^\s*(?P<FileType>([SBCTRNFAIO])|(ST))(?P<FileNumber>\d{1,3}):(?P<ElementNumber>\d{1,3})([./](?P<BitNumber>\d{1,4}))?\s*$"# Changed / to [./]
    RE2 = r"(?i)^\s*(?P<FileType>[BN])(?P<FileNumber>\d{1,3})(/(?P<BitNumber>\d{1,4}))\s*$"
    RE3 = r"(?i)^\s*(?P<FileType>[CT])(?P<FileNumber>\d{1,3}):(?P<ElementNumber>\d{1,3})[./](?P<SubElement>(ACC|PRE|EN|DN|TT|CU|CD|DN|OV|UN|UA))\s*$"# Changed [.] to [./]
    RE4 = r"(?i)^\s*(?P<FileType>([IOS])):(?P<ElementNumber>\d{1,3})([.](?P<SubElement>[0-7]))?(/(?P<BitNumber>\d{1,4}))?\s*$"
    RE1_address_pattern = re.compile(RE1)
    RE2_address_pattern = re.compile(RE2)
    RE3_address_pattern = re.compile(RE3)
    RE4_address_pattern = re.compile(RE4)

    def __init__(self, addressString):
        if (_debug):
            print (">>Entering ParsedDataAddress::__init__(", addressString, ")")
        self.raw_string = addressString
        self.FileType = -20
        self.FileNumber = -20
        self.SubElement = -20
        self.ElementNumber = -20
        self.BitNumber = -20
        self.BytesPerElement = -20
        if (addressString != ''):
            results = self.parse_address()
        if (_debug):
            print ("<<Leaving ParsedDataAddress::__init__()")
            
    def parse_address(self):
        if (_debug):
            print (">>Entering ParsedDataAddress::parse_address()")
        match = self.RE1_address_pattern.match(self.raw_string)
        if (match != None):
            results = self.RE1_address_pattern.search(self.raw_string)
            if (_debug):
                print (" ParsedDataAddress::parse_address() match RE1 results = ",results)
        else:
            match = self.RE2_address_pattern.match(self.raw_string)
            if (match != None):
                results = self.RE2_address_pattern.search(self.raw_string)
                if (_debug):
                    print (" ParsedDataAddress::parse_address() match RE2 results = ",results)
            else:
                match = self.RE3_address_pattern.match(self.raw_string)
                if (match != None):
                    results = self.RE3_address_pattern.search(self.raw_string)
                    if (_debug):
                        print (" ParsedDataAddress::parse_address() match R3 results = ",results)
                else:
                    match = self.RE4_address_pattern.match(self.raw_string)
                    if (match != None):
                        results = self.RE4_address_pattern.search(self.raw_string)
                        if (_debug):
                            print (" ParsedDataAddress::parse_address() match R4 results = ",results)
                    else:
                        if (_debug):
                            print (" ParsedDataAddress::parse_address() match results = None")

        if (results != None):
            try:
                self.FileType = results.group('FileType')
            except:
                pass
            try:
                self.FileNumber = results.group('FileNumber')# we have an I,O,or S address without a file designation
            except:
                if (addressString[0] == 'i' or addressString[0] == 'I'):
                    self.FileNumber = 1
                elif (addressString[0] == 'o' or addressString[0] == 'O'):
                    self.FileNumber = 0
                else:
                    self.FileNumber = 2
            try:
                self.BitNumber = results.group('BitNumber')
            except:
                pass
            try:
                self.ElementNumber =  results.group('ElementNumber')
            except:
                self.ElementNumber = (self.BitNumber) >> 4
                self.BitNumber = (self.BitNumber) % 16
            try:
                self.SubElement = results.group('SubElement')
                if (self.SubElement == 'PRE'):
                    self.SubElement = 1
                elif (self.SubElement == 'ACC'):
                    self.SubElement = 2
                elif (self.SubElement == 'EN'):
                    self.SubElement = 15
                elif (self.SubElement == 'TT'):
                    self.SubElement = 14
                elif (self.SubElement == 'DN'):
                    self.SubElement = 13
                elif (self.SubElement == 'CU'):
                    self.SubElement = 15
                elif (self.SubElement == 'CD'):
                    self.SubElement = 14
                elif (self.SubElement == 'OV'):
                    self.SubElement = 12
                elif (self.SubElement == 'UN'):
                    self.SubElement = 11
                elif (self.SubElement == 'UA'):
                    self.SubElement = 10
                elif (self.SubElement == '0'):
                    self.SubElement = 0
                elif (self.SubElement == '1'):
                    self.SubElement = 1
                elif (self.SubElement == '2'):
                    self.SubElement = 2
                elif (self.SubElement == '3'):
                    self.SubElement = 3
                elif (self.SubElement == '4'):
                    self.SubElement = 4
                elif (self.SubElement == '5'):
                    self.SubElement = 5
                elif (self.SubElement == '6'):
                    self.SubElement = 6
                elif (self.SubElement == '7'):
                    self.SubElement = 7
                elif (self.SubElement == '8'):
                    self.SubElement = 8
                else:
                    self.SubElement = -20
                    
                if (self.SubElement > 4):#these subelements are bit level
                    self.BitNumber = self.SubElement
                    self.SubElement = 0
            except:
                pass
            
            if (self.FileType != -20):
                self.FileType = self.FileType.upper()

            if (int(self.ElementNumber) < 256):
                self.BytesPerElement = 2
                if (self.FileType == "N"):
                    self.FileType = 0x89
                if (self.FileType == "B"):
                    self.FileType = 0x85
                if (self.FileType == "T"):
                    self.FileType = 0x86
                if (self.FileType == "C"):
                    self.FileType = 0x87
                if (self.FileType == "F"):
                    self.FileType = 0x8A
                    self.BytesPerElement = 4
                if (self.FileType == "S"):
                    self.FileType = 0x84
                if (self.FileType == "ST"):
                    self.FileType = 0x8D
                    self.BytesPerElement = 76
                if (self.FileType == "A"):
                    self.FileType = 0x8E
                if (self.FileType == "R"):
                    self.FileType = 0x88
                if (self.FileType == "O"):
                    self.FileType = 0x8B
                if (self.FileType == "I"):
                    self.FileType = 0x8C
                if (_debug):
                    print ("<<Leaving ParsedDataAddress::parsed_address() with a match")
        else:
             if (_debug):
                 print ("<<Leaving ParsedDataAddress::parsed_address() with no match")
                        
class CIPClient(asyncore.dispatcher_with_send):
    def __init__(self):
        if (_debug):
            print (">>Entering CIPClient::__init__()")
        asyncore.dispatcher_with_send.__init__(self)
        self.TNS = (random.randint(0, 65535) & 0x7F) + 1
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        if (_debug):
            self.logger = logging.getLogger('CIP' + str(self.TNS))
        self.xTNS = 0
        self.rTNS = 0
        self.data = []
        self.value = 0
        self.commanddata = []
        self.elements = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
        self.sessionID=[0,0,0,0]
        self.write_buffer = ''
        self.read_buffer = ''
        self.responded = [False for x in range(256)]
        self.isconnected = False
        self.datapackets = [[0 for x in range(256)] for x in range(256)]
        self.reply = 0
        self.Func = 0
        self.WriteTrigger = False
        self.BytesToRead = 0
        self.ArrayElements = 0
        self.parsedResult = 0
        self.waiting = False
        self.numberOfElements = 0
        
        if (_debug):
            print ("<<Leaving CIPClient::__init__()")
        
    def init_connect(self, host, port) :
        if (_debug):
            print(">>Entering CIPClient::init_connect(", host, port,")")
        if (_verbose):
            print("...connecting to SLC")
        try:
            self.connect((host, port))
        except socket.gaierror:
            if (_verbose or _debug):
                print('...connection to SLC failed')
        if (_verbose or _debug):
            print ("...connected to SLC")
        if (_debug):
            print ("<<Leaving CIPClient::init_connect()")    
        
    def handle_connect(self):
        if (_debug):
            print(">>CIPClient::handle_connect()<<")
        pass
        
    def handle_close(self):
        if (_debug):
            print(">>CIPClient::handle_close()<<")
	#self.close()
        self.socket.close()
        asyncore.close_all()
    def close_connection(self):
        if (_debug):
            print(">>CIPClient::close_connection()<<")
        self.socket.close()
        asyncore.close_all()

    def readable(self):
        if (_debug):
            print(">>CIPClient::readable()<< connected = ", self.connected)
        # connection string, requeest session ID
        if (self.connected):   
            self.WriteTrigger = True
        self.write_elements = [1,1,0,0,0,0,0,0,0,0,0,0,0,4,0,5,0,0,0,0,0,0,0,0,0,0,0]
        self.write_buffer=bytearray(self.write_elements)

        return True

    def writable(self):
        if (_debug):
            print(">>CIPClient::writeable()<<")
        is_writable = (len(self.write_buffer) > 0)
        if (not self.waiting):
            return is_writable
        else:
            return False
    

    def handle_read(self):
        
        if (_debug):
            print(">>Entering CIPClient::handle_read() ", _timeoutCTR)
        data = [0 for x in range(468)]
        if (platform.system() == "Windows"):
            data = self.recv(40)
        else:    
            data = bytearray(self.recv(468))
        #if (_debug):
        #    self.logger.debug('handle_read() -> %d bytes', len(data))
        #    self.logger.debug(data)
        self.data = data
        #####
        time.sleep(.1)
        #####
        if (self.isconnected == False):
            if (_debug):
                print ("...sessionID not established")
            self.sessionID[0] = data[4]
            self.sessionID[1] = data[5]
            self.sessionID[2] = data[6]
            self.sessionID[3] = data[7]
            self.responded[0] = True
            self.isconnected = True
            if (_debug):
                print ('...session ID:', self.sessionID)
            if (_read):
                self.ReadAny(_address,_length)
            if (_write):
                writebuf=[_value]
                self.WriteData(_address,1,writebuf)
        else:
            if (_debug):
                print ("...sessionID established")
            self.waiting = False
            
            if (len(data)>35):
                self.xTNS = data[35]
            else:
                self.xTNS = 0
            self.datapackets[self.xTNS] = data
            self.ProcessReceivedData(data)
            
            self.reply = self.PrefixAndSend(0xF, True)
            dataSubset = [0 for x in range(self.BytesToRead)]
            offset = 0
            if (data[len(data)-1] == 7 and data[len(data)-2] == 2):
                if (_debug):
                    print("...Unexpected data placement, applying offset")
                offset = 2
            elif (data[len(data)-1] == 1 and data[len(data)-2] == 2):
                if (_debug):
                    print("...Unexpected data placement, applying offset")
                offset = 2
            for i in range(self.BytesToRead):
                dataSubset[i] = data[len(data)-(self.BytesToRead - i) - offset]
          
            if (data[1]==7):
                if (dataSubset != []):
                    self.value = self.ExtractRegister(dataSubset)
                self.socket.close()
                asyncore.close_all()
        if (_debug):
            print("<<Leaving CIPClient::handle_read()")
            
    def handle_write(self):
        global _timeoutCTR
        _timeoutCTR += 1
        if (_debug):
            print(">>Entering CIPClient::handle_write() with timeoutCTR = ", _timeoutCTR, " WriteTrigger = ", self.WriteTrigger)
        if (_timeoutCTR>=_TTL):
            self.value = [0]
            self.socket.close()
            asyncore.close_all()
            print ("...request timed out after ", _timeoutCTR, " attempts.")
            return 0
        if (self.WriteTrigger):
            sent = self.send(self.write_buffer)
            self.write_buffer = self.write_buffer[sent:]
            if (platform.system() == "Windows" or not _debug):
                time.sleep(.01)
            else:
                time.sleep(.001)
#########
        #TODO JJS : this sleep ^ needs adjusting if no value retrieved
#########            
            
           # ('handle_write() -> "%s"', self.write_buffer[:sent])
            if (self.isconnected == False):
                pass
            else:
                self.WriteTrigger = False
        if (_debug):
            print("<<Leaving CIPClient::handle_write()")        
        
    def handle_expt(self):
        if (_debug):
            print(">>CIPClient::handle_expt()<<")
        pass
        self.close()
        
    def handle_accept(self):
        if (_debug):
            print(">>CIPClient::handle_accept()<<")
        pass

    def ReadAny(self,startaddress,length):
        if (_debug):
            print(">>Entering CIPClient::ReadAny(", startaddress, length,")")
        data = [0x00,0x00,0x00,0x00,0x00]
        numberOfBytes = 0
        if (length > 256):
            if(_debug or _verbose):
                print ("...Reads are limited to 256 elements")
            length = 256   
        
        self.parsedResult = ParsedDataAddress(startaddress)
        #self.parsedResult.parse_address()
        if (self.parsedResult != None):
            self.ArrayElements = length - 1
            if (self.ArrayElements < 0):
                self.ArrayElements = 0
            if (self.parsedResult.BitNumber != None and int(self.parsedResult.BitNumber) < 16):
                self.ArrayElements = math.floor(length / 16)
                if (self.ArrayElements % 16 > 0):
                    data[0] = 1 + data[0]
            
            if (self.parsedResult.FileType == 0x8D):
                numberOfBytes = ((self.ArrayElements + 1)) * 82
            elif (self.parsedResult.FileType == 0x8A):
                numberOfBytes = ((self.ArrayElements + 1)) * 4
            else:
                numberOfBytes = ((self.ArrayElements + 1)) * 2
           
            if (self.parsedResult.SubElement > 0 and (self.parsedResult.FileType == 0x86 or self.parsedResult.FileType == 0x87)):
                numberOfBytes = (numberOfBytes * 3) - 4
            
            self.reply = 0
            ReturnedData = [0 for x in range(numberOfBytes)]#self.datapackets = [[0 for x in range(256)] for x in range(256)]
            ReturnedDataIndex = 0

            self.BytesToRead = 0
            
            #'*Only 236 bytes can be read at once, so break it into chunks
            Retries = 0
            while (self.reply == 0 and ReturnedDataIndex < numberOfBytes):
                if (numberOfBytes - ReturnedDataIndex > 168 and self.parsedResult.FileType == 0x8D):
               #'* Only two string elements can be read on each read (168 bytes)
                    self.BytesToRead = 168
                elif (numberOfBytes - ReturnedDataIndex > 234 and (self.parsedResult.FileType == 0x86 or self.parsedResult.FileType == 0x87)):
                    #'* Timers & counters read in multiples of 6 bytes
                    self.BytesToRead = 234
                
                elif (numberOfBytes - ReturnedDataIndex > 236):
                    self.BytesToRead = 236
                else:
                    self.BytesToRead = numberOfBytes - ReturnedDataIndex
            
                ReturnedData2 = bytes(0 for x in range(self.BytesToRead))
                ReturnedData2 = self.ReadRawData(self.BytesToRead)
                #* Point to next set of bytes to read in block
                if (self.reply == 0):
                    #'* Point to next element to begin reading
                
                    for i in range(len(ReturnedData2)):
                         ReturnedData[i+ReturnedDataIndex] = ReturnedData2[i]
                    ReturnedDataIndex = self.BytesToRead + ReturnedDataIndex
                    #'* Point to next block of elements to read
 
                    if (ReturnedDataIndex < numberOfBytes):
                        if (self.parsedResult.FileType == "0x8A"):
                            self.parsedResult.Element = (self.BytesToRead / 4) + self.parsedResult.Element
                        elif (self.parsedResult.FileType == "0x8D"):
                            self.parsedResult.Element = (self.BytesToRead / 84) + self.parsedResult.Element  #'* Each string elements is 84 bytes
                        elif (self.parsedResult.FileType == "0x86" or self.parsedResult.FileType == "0x87"):
                            self.parsedResult.Element = (self.BytesToRead / 6) + self.parsedResult.Element   #'* Timers or counters
                        else:
                            self.parsedResult.Element = (self.BytesToRead / 2) + self.parsedResult.Element
                elif (Retries < 2):
                    Retries += 1
                    self.reply = 0
                else:
                    #'* An error was returned from the read operation
                    if (_debug or _verbose):
                        print ("...Error in ReadAny() ", self.DecodeMessage(self.reply))
                    return None
        if (_debug):
            print("<<Leaving CIPClient::ReadAny()")

    def ExtractRegister(self,data):
        if (_debug):
            print(">>Entering CIPClient::ExtractRegister(", data, ")")
        if (self.parsedResult.FileType == 0x85): result = [' ']
        else: result = []
        StringLength = 0
        dataByteArray = array.array('B',data).tostring()

        if (self.parsedResult.FileType == 0x8A): 			#'* Flooating point read (&H8A)
            for ff in range (0,_length):
                result.append(struct.unpack_from('f',dataByteArray,ff*4)[0])
        elif (self.parsedResult.FileType == 0x89): 			#Short Integer
            for zz in range (0,_length):
                result.append(struct.unpack_from('h',dataByteArray,zz*2)[0])
        elif (self.parsedResult.FileType == 0x8D): 			# ' * String
            for i in range((self.ArrayElements)):
                StringLength = data[i * 84]
                    #'* The controller may falsely report the string length, so set to max allowed
                if (StringLength > 82):
                    StringLength = 82
                    #'* use a string builder for increased performance
                result2 = [' ' * 82]
                j = 2
                    #'* Stop concatenation if a zero (NULL) is reached
                while (j < StringLength + 2 and data[(i * 84) + j + 1] > 0):
                    result2.append(chr(data[(i * 84) + j + 1]))
                        #'* Prevent an odd length string from getting a Null added on
                    if (j < StringLength + 1 and (data[(i * 84) + j]) > 0):
                        result2.append(Chr(data[(i * 84) + j]))
                    j += 2
                result[i] = str(result2)
        elif (self.parsedResult.FileType == 0x86 or self.parsedResult.FileType == 0x87):  #'* Timer, counter
                #'* If a sub element is designated then read the same sub element for all timers
                j = 0
                for i in range((self.ArrayElements)):
                    if (self.parsedResult.SubElement > 0):
                        j = i * 6
                    else:
                        j = i * 2
                    result[i] = int(data[j])

        else:
            if (self.ArrayElements <= 1 ):
                self.ArrayElements = 1
            for i in range((self.ArrayElements)):
                try:
                    result[i] = int(data[i * 2])
                except:
                    print ("Exception in ExtractRegister()")

        #'******************************************************************************
        #'* If the number of words to read is not specified, then return a single value
        #'******************************************************************************
        #'* Is it a bit level and N or B file?
        if (self.parsedResult.BitNumber != None and int(self.parsedResult.BitNumber) >= 0 and int (self.parsedResult.BitNumber) < 16):
            BitResult = [' ']
            BitPos = self.parsedResult.BitNumber
            WordPos = 0
            #'* Set array of consectutive bits
            #for i in range(len(numberOfElements - 1)):
            BitResult = bool(result[WordPos] & 2 ** int(BitPos))
            #    BitPos += 1
            #    if (BitPos > 15):
            #        BitPos = 0
            #        WordPos = 1 + WordPos 
            return BitResult
            
        if (_debug):
            print("<<Leaving CIPClient::ExtractRegister()")
        return result
        
    def ReadRawData(self, numberOfBytes):
        if (_debug):
            print(">>Entering CIPClient::ReadRawData(", numberOfBytes, ")")
        DataSize = 0
        self.Func = 0
        #Function &HA1 is the same as &HA2, but without the Sub Element
        if (self.parsedResult.SubElement == -20):
            DataSize = 3
            self.Func = 0xA1
        else:
            DataSize = 4
            self.Func = 0xA2
        self.commanddata= [0 for x in range(DataSize+1)]

        #'* Number of bytes to read -
        if (_debug):
            print ("Number of Bytes: ", numberOfBytes)
        self.commanddata[0] = numberOfBytes
        if (self.commanddata[0] < 0): self.commanddata[0] = 0

        #'* File Number
        if (_debug):
            print ("File Number: ", self.parsedResult.FileNumber)
        self.commanddata[1] = int(self.parsedResult.FileNumber)
        if (self.commanddata[1] < 0): self.commanddata[1] = 0

        #'* File Type
        if (_debug):
            print ("File Type: ", self.parsedResult.FileType)
        self.commanddata[2] = self.parsedResult.FileType
        
        #'* Starting Element Number
        if (_debug):
            print ("Element Number: ", self.parsedResult.ElementNumber)
        self.commanddata[3] = int(self.parsedResult.ElementNumber)
        if (self.commanddata[3] < 0): self.commanddata[3] = 0
        #'* Sub Element
        if (DataSize == 4):
            if (_debug):
                print ("Sub Element: ", self.parsedResult.SubElement)
            self.commanddata[4] = self.parsedResult.SubElement
            if (self.commanddata[4] < 0): self.commanddata[4] = 0


        self.rTNS = 0
        # '* Try function A1 to see if it works on ML1500 and PLC5

        Result = [0 for x in range(numberOfBytes - 1)]
        if (self.reply == 0):
            DataPosition = 36

           # '***************************************************
           # '* Extract returned data into appropriate data type
           # '***************************************************
            
            for i in range((numberOfBytes - 1)):
                try:
                    Result[i] = self.datapackets[self.rTNS][(DataPosition + i)]
                except:    
                    if (_debug or _verbose):
                        print (i, numberOfBytes, self.rTNS, DataPosition, Result)
                        print ("Exception in ReadRawData()")
                    pass
        if (_debug):
            print ("<<Leaving CIPClient::ReadRawData() with Result = ", Result)  
        return Result

    def DecodeMessage(self,msgNumber):
        if (_debug):
            print(">>CIPClient::DecodeMessage(", msgNumber, ")<<")        
        if (msgNumber == 0):
            return ""
        elif (msgNumber == -2):
            return "Not Acknowledged (NAK)"
        elif (msgNumber == -3):
            return "No Reponse, Check COM Settings"
        elif (msgNumber == -4):
            return "Unknown Message from DataLink Layer"
        elif (msgNumber == -5):
            return "Invalid Address"
        elif (msgNumber == -6):
            return "Could Not Open Com Port"
        elif (msgNumber == -7):
            return "No data specified to data link layer"
        elif (msgNumber == -8):
            return "No data returned from PLC"
        elif (msgNumber == -20):
            return "No Data Returned"
#'*** Errors coming from PLC
        elif (msgNumber == 16):
            return "Illegal Command or Format, Address may not exist or not enough elements in data file"
        elif (msgNumber == 32):
            return "PLC Has a Problem and Will Not Communicate"
        elif (msgNumber == 48):
            return "Remote Node Host is Misssing, Disconnected, or Shut Down"
        elif (msgNumber == 64):
            return "Host Could Not Complete Function Due To Hardware Fault"
        elif (msgNumber == 80):
            return "Addressing problem or Memory Protect Rungs"
        elif (msgNumber == 96):
            return "Function not allows due to command protection selection"
        elif (msgNumber == 112):
            return "Processor is in Program mode"
        elif (msgNumber == 128):
            return "Compatibility mode file missing or communication zone problem"
        elif (msgNumber == 144):
            return "Remote node cannot buffer command"
        elif (msgNumber == 240):
            return "Error code in EXT STS Byte"
        else:
            return "Unknown Message - " & msgNumber
        
    def PrefixAndSend(self,Command,Wait):
    #'**************************************************************
    #'* This method implements the common application routine
    #'* as discussed in the Software Layer section of the AB manual
    #'**************************************************************  
        if (_debug):
            print(">>Entering CIPClient::PrefixAndSend( ",Command,Wait, ")")
        self.IncrementTNS()

        PacketSize = 0
        PacketSize = len(self.commanddata) + 37
        CommandPacket = [0 for x in range(PacketSize)]
        BytePos = 0

        #'**********************************
        #'* Build the Ethernet Header
        #'**********************************
        CommandPacket[0] = 1  #' 1=Request, 2=Response
        CommandPacket[1] = 7     #'7=PCCC command
        #'* Length of data packet
        CommandPacket[2] = int((len(self.commanddata) + 9) / 256)
        CommandPacket[3] = (len(self.commanddata) + 9) & 255

        #'* Session ID
        CommandPacket[4] = self.sessionID[0]
        CommandPacket[5] = self.sessionID[1]
        CommandPacket[6] = self.sessionID[2]
        CommandPacket[7] = self.sessionID[3]

        #'Elements 8-11 = Status=0

        #'* Not sure what these 16 bytes represent
        CommandPacket[12] = 0x35

        CommandPacket[28] = 0
        CommandPacket[29] = 5   #'Ths was pulled from Ron Gage libarary and from sniffing the packet
        CommandPacket[30] = 0
        CommandPacket[31] = 0
        BytePos = 32

        CommandPacket[BytePos] = Command
        CommandPacket[BytePos + 1] = 0
        CommandPacket[BytePos + 2] = 1
        CommandPacket[BytePos + 3] = (self.TNS & 255)
        CommandPacket[BytePos + 4] = self.Func
        for i in range(len(self.commanddata)):
            CommandPacket[(BytePos + 5) + i] = self.commanddata[i]
        self.rTNS = self.TNS & 0xFF
        self.responded[self.rTNS] = False
        self.result = 0
        self.SendData(CommandPacket)
        if (_debug):
            print("<<Leaving CIPClient::PrefixAndSend() with CommandPacket = ", CommandPacket)
        return self.result

    def IncrementTNS(self):
        if (_debug):
            print(">>Entering CIPClient::IncrementTNS()")
        #'* Incement the TransactionNumber value
        if (self.TNS < 65535):
            self.TNS = 1 + self.TNS
        else:
            self.TNS = 1
        if (_debug):
            print("<<Leaving CIPClient::IncrementTNS() with TNS = ", self.TNS)    
                
    def SendData(self,data):
        if (_debug):
            print(">>Entering CIPClient::SendData(", data,")",)
        #'* connect if it has not been already
        if (self.isconnected == False):
            print ("... SLC connection failure")
            self.value = [0]
            return 0
        self.write_elements = data
        self.write_buffer=bytearray(self.write_elements)
        try:
            self.WriteTrigger = True
            self.handle_write()
        except:
            e = sys.exc_info()[0]
            if (_debug or _verbose):
                print("Error in Send data - ", e)
        if (_debug):
            print("<<Leaving CIPClient::SendData() with write_buffer=", self.write_buffer)        
                
    def WriteData(self,startAddress,numberOfElements,dataToWrite):
        if (_debug):
            print(">>Entering CIPClient::WriteData(", startAddress, numberOfElements,dataToWrite,")")
        self.parsedResult = ParsedDataAddress(startAddress)
        self.parsedResult.parse_address()
        time.sleep(.11)
        if (self.parsedResult != None):
            if (_debug):
                print (self.parsedResult.BytesPerElement)
            ConvertedDataSize = numberOfElements * self.parsedResult.BytesPerElement
            ConvertedData = [0 for x in range(ConvertedDataSize)]
            i = 0
            if (self.parsedResult.FileType == 0x8A):
#floating point F file
                bytes = [0x00,0x00,0x00,0x00,0x00]
                j = 0
                for i in range(numberOfElements):
                    bytes = bytearray(struct.pack('<f',dataToWrite[i]))
                    for j in range(0,4):
                        ConvertedData[i * 4 + j] = bytes[j]
                if (_debug):
                    print("<<Leaving CIPClient::WriteData() successfully, writing to F file")
                return self.WriteRawData(numberOfElements * self.parsedResult.BytesPerElement, ConvertedData)
            else:
                while (i < numberOfElements):
                    try:
                        if (dataToWrite[i] >32767 or dataToWrite[i] <-32768):
                            if (_debug or _verbose):
                                print (".... Write Error, data out of range")

                        ConvertedData[i] = dataToWrite[i] & 0xFF
                        ConvertedData[i+1] = (dataToWrite[i] >> 8) & 0xFF
                        i+=2
                    except:
                        pass
                if (_debug):
                    print("<<Leaving CIPClient::WriteData() successfully, writing to N file")
                return self.WriteRawData(numberOfElements * self.parsedResult.BytesPerElement, ConvertedData)

        if (_debug):
                print("<<Leaving CIPClient::WriteData() UNsuccessfully")                 
            
    def WriteRawData(self, numberOfBytes, dataToWrite):
        if (_debug):
            print (">>Entering CIPClient::WriteRawData( ", numberOfBytes,dataToWrite,")")
        try:
            dataC = []
            if (self.parsedResult.FileType == 0):
                if (_debug or _verbose):
                    print ("... SLC File Type was zero")
                raise Exception
            dataC.append(numberOfBytes & 0xFF)
            dataC.append(int(self.parsedResult.FileNumber))
            dataC.append(self.parsedResult.FileType)
            dataC.append(int(self.parsedResult.ElementNumber))
            dataC.append(0)
            if (self.parsedResult.BitNumber != None and self.parsedResult.BitNumber < 16):
                self.Func =0xAB
                dataC.append((2**self.parsedResult.BitNumber)&0xFF)
                dataC.append(2**(self.parsedResult.BitNumber-8))
                if (dataToWrite[0] <= 0):
                # Set bits to clear
                    dataC.append(0)
                    dataC.append(0)
                else:
                    # Bits to turn on
                    dataC.append((2 ** (self.parsedResult.BitNumber)) & 0xFF)
                    dataC.append(2 ** (self.parsedResult.BitNumber - 8))
            else:
                self.Func = 0xAA
                for i in range(numberOfBytes):
                    dataC.append((dataToWrite[i] & 0xFF))
            dataC.append(0)        
            self.commanddata = dataC
            self.rTNS = 0
            
            self.reply = self.PrefixAndSend(0xF,True)
            if (_debug):
                print ("<< Leaving CIPClient::WriteRawData() with data = ", self.data)          
            if self.reply == 0:
                return 0
        except:
            #raise Exception("!Error from Prefix and send")
            if (_debug or _verbose):
                print ("!Error in WriteRawData()", self.DecodeMessage(self.reply))
                print ("<< Leaving CIPClient::WriteRawData() with exceptions") 
            return (-1)
    
    def ProcessReceivedData(self,data):
        if (_debug):
            print (">>Entering CIPClient::ProcessReceivedData( ", data,")")
        #'* Store the returned data in an array based on the LSB of the TNS
        #'* If there is no TNS, then store in 0
        
        #'* make sure there is enough data and it is not a command (commands are less than 31)
        #If bytecount > 4 And ReceivedDataPacket.Count > 31 Then
        bytecount = len(data)
        
        if (bytecount > 35):
            self.xTNS = data[35]
        else:
            self.xTNS = 0
        
        #'********************************************************************
        #'* Store data in a array of collection using TNS's low byte as index
        #'********************************************************************
       
        self.datapackets[self.xTNS] = bytes(data)

        if (bytecount > 1):
            if (data[1] == 1):
                #'*************************************************************
                #'* A command of 1 (submode) means that a sessionID was sent back
                #'*************************************************************
                if (bytecount > 7):
                    for i in range(3):
                        self.sessionID[i] = data[i + 4]
                    
                    self.responded[0] = True
                    

                    #'*******************************************************
                    #'* A command of 7 (submode) encapsulated PCCC command
                    #'*********************************************************
            if (data[1] == 7):
                self.responded[self.xTNS] = True
            
            #'***************************************************************************
            #'* Send back an response to indicate whether data was received successfully
            #'***************************************************************************
            
            if (self.datapackets[self.xTNS][1] == 7):# and self.datapackets[self.xTNS][2] > 31):
                
                #'* Let application layer know that new data has came back
               # DF1DataLink1_DataReceived()###
            #    pass 
            #else:
                #'****************************************************
                #'****************************************************
                #'* Handle the unsolicited message
                #'* This is where the simulator code would be placed
                #'****************************************************
                #'* Command &h0F Function &HAA - Logical Write
                if (self.datapackets[self.xTNS][2] == 15 and self.datapackets[self.xTNS][6] == 0xAA):
                    
                    #'* Send back response - Page 7-18
                    
                    self.TNS = self.datapackets[self.xTNS][5] * 256 + self.datapackets[self.xTNS][4]
                    receivedAddress = UnparsedDataAddress()
                    #'* Extract the information
                    receivedAddress.ElementCount = DataPackets[self.xTNS][7]
                    receivedAddress.FileNumber = DataPackets[self.xTNS][8]
                    receivedAddress.FileType = DataPackets[self.xTNS][9]
                    receivedAddress.ElementNumber = DataPackets[self.xTNS][10]
                    receivedAddress.SubElement = DataPackets[self.xTNS][11]
                    receivedAddress.StringFileType = ''
                    receivedAddress.BytesPerElement = 0

                    if (receivedAddress.FileType == 0x89):
                        receivedAddress.StringFileType ="N"
                        receivedAddress.BytesPerElement = 2
                            
                    elif (receivedAddress.FileType == 0x85):
                        receivedAddress.StringFileType ="B"
                        receivedAddress.BytesPerElement = 2
                    elif (receivedAddress.FileType == 0x86):
                        receivedAddress.StringFileType ="T"
                        receivedAddress.BytesPerElement = 6
                    elif (receivedAddress.FileType == 0x87):
                        receivedAddress.StringFileType ="C"
                        receivedAddress.BytesPerElement = 6
                    elif (receivedAddress.FileType == 0x84):
                        receivedAddress.StringFileType ="S"
                        receivedAddress.BytesPerElement = 2
                    elif (receivedAddress.FileType == 0x8A):
                        receivedAddress.StringFileType ="F"
                        receivedAddress.BytesPerElement = 4
                    elif (receivedAddress.FileType == 0x8D):
                        receivedAddress.StringFileType ="ST"
                        receivedAddress.BytesPerElement = 84
                    elif (receivedAddress.FileType == 0x8E):
                        receivedAddress.StringFileType ="A"
                        receivedAddress.BytesPerElement = 2
                    elif (receivedAddress.FileType == 0x88):
                        receivedAddress.StringFileType = "R"
                        receivedAddress.BytesPerElement = 6
                    elif (receivedAddress.FileType == 0x82 or receivedAddress.FileType == 0x8B):
                        receivedAddress.StringFileType ="O"
                        receivedAddress.BytesPerElement = 2
                    elif (receivedAddress.FileType == 0x83 or receivedAddress.FileType == 0x8C):
                        receivedAddress.StringFileType ="I"
                        receivedAddress.BytesPerElement = 2
                    else:
                        receivedAddress.StringFileType = "Undefined"
                        receivedAddress.BytesPerElement = 2
        if (_debug):
            print ("<<Leaving CIPClient::ProcessReceivedData() with xTNS = ",self.xTNS)
            
def HandleCLI(argv):
    global _read
    global _address
    global _store
    global _database
    global _table
    global _write
    global _value
    global _data
    global _debug
    global _verbose
    global _pass
    global _user
    global _length

    try:
        opts, args = getopt.getopt(argv, "hr:sl:d:t:w:u:p:DVv:",["help","read=","store","length=","database=","table=","write=","user=","pass=","Debug","Verbose","value="])
    except getopt.GetoptError:
        CLIUsage()
        sys.exit(2)

    if (opts == []):
        CLIUsage()
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            CLIUsage()
            sys.exit()
        elif opt in ("-r", "--read"):
            _read = True
            _address = arg
        elif opt in ("-s", "--store"):
            _store = True
        elif opt in ("-d", "--database"):
            _database = arg
        elif opt in ("-t", "--table"):
            _table = arg    
        elif opt in ("-w", "--write"):
            _write = True
            _address = arg
        elif opt in ("-u", "--user"):
            _user = arg
        elif opt in ("-p", "--pass"):
            _pass = arg
        elif opt in ("-D", "--Debug"):
            _debug = True
        elif opt in ("-V", "--Verbose"):
            _verbose = True
        elif opt in ("-l", "--length"):
            _length = int(arg)
        elif opt in ("-v", "--value"):
            if (_address[0] == 'f' or _address[0] == 'F'):
                _value = float(arg) 
            else:
                _value = int(arg)
    if ((_read or _write) and _address is None):
        print ("!Address Required!")

def CLIUsage():
    print (sys.argv[0])
    print ("\nOptions:")
    print ("\t-h\t--help")
    print ("\t-r\t--read")
    print ("\t\t-s\t--store")
    print ("\t\t-d\t--database")
    print ("\t\t-p\t--port")
    print ("\t\t-t\t--table")
    print ("\t\t-d\t--database user")
    print ("\t\t-d\t--database password")
    print ("\t-w\t--write")
    print ("\t\t-v\t--value")
    print ("\t-D\t--Debug")
    print ("\t-V\t--Verbose")

def writeToSLC(IP):
    global _read
    global _address
    global _store
    global _database
    global _table
    global _write
    global _value
    global _data
    global _debug
    global _verbose
    global _timeoutCTR
    global _length
 
    _length = 1
    _timeoutCTR = 0

    client = CIPClient()
    client.elements = [1,1,0,0,0,0,0,0,0,0,0,0,0,4,0,5,0,0,0,0,0,0,0,0,0,0,0]
    client.write_buffer = bytearray(client.elements)
    client.init_connect(IP,2222)
    time.sleep(.11)

    if (_verbose and _write):
        print('...writing \"' + str(_value) + '\" to ' + _address)

    asyncore.loop()
    if (_read):
        #if (_debug or _verbose):
        print(str(client.value[0]))
        return(str(client.value[0]))
        time.sleep(.11)
    if (_debug or _verbose):
        print("...closing")
    client.close_connection()

 
def readFromSLC(IP):
    global _read
    global _address
    global _store
    global _database
    global _table
    global _write
    global _value
    global _data
    global _debug
    global _verbose
    global _timeoutCTR
    global _length

    _length = 1
    _timeoutCTR = 0

    client = CIPClient()
    client.elements = [1,1,0,0,0,0,0,0,0,0,0,0,0,4,0,5,0,0,0,0,0,0,0,0,0,0,0]
    client.write_buffer = bytearray(client.elements)
    client.init_connect(IP,2222)
    time.sleep(.11)
    if (_verbose and _read):
        print('...reading from ' + _address)
    asyncore.loop()
    if (_read):
        if client.parsedResult.FileType == 0x85:
            print(str(client.value))
            return(str(client.value))
        else:
            print(str(client.value[0]))
            return(str(client.value[0]))           
        time.sleep(.11)
    if (_debug or _verbose):
        print("...closing")
    client.close_connection()


if __name__ == '__main__':
    HandleCLI(sys.argv[1:])

    if (_read):
        time.sleep(.11)
        readFromSLC("10.1.1.139")
        if (_store):
            HistorianConnector = MySQLClient('localhost',3306,'Thermostat','soho','')
            HistorianConnector.connect()
            table_name="`HouseTemp_" + time.strftime("%Y_%B") + "`"
            table_string = table_name + "( `primary_key` mediumint(8) NOT NULL AUTO_INCREMENT, `time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP, `ActualTemp` float NOT NULL,`CurrentSP` float NOT NULL, `units` varchar(20) NOT NULL, PRIMARY KEY (`primary_key`)) ENGINE=InnoDB DEFAULT CHARSET=utf8"
            HistorianConnector.new_table(table_string)
            args = (["value",client.value[0]],
                    ["units",_units]
            )
            HistorianConnector.insert(table_name,args)
            HistorianConnector.close()
    if (_write):
        writeToSLC("10.1.1.139")
    if (_debug or _verbose):
        print("...closing")
