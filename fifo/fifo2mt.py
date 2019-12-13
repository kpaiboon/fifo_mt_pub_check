'''
MIT License

Copyright (c) 2019-present Paiboon Kupthanakorn

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
'''

#Fifo
# Version 7
# 2019-12-13 1. fix (*) checksum, reverse #1
# Version 6
# 2019-10-30 1. MIT License
# Version 5
# 2019-16-23 1. force speed > 5km force MT-IO setbit 0x04 2. Add func mt2fi 3.Fix bug incorrect A01
# 4.almcode-param 5. code 37 <= alm38/38
# 6. MT:: AD1|AD2|AD3|Battery analog|External power|AD4|AD5 <= Fi:: bat_ad|ext_ad|ad1|ad2
# 7. MT.Ext_ad = 3.86847 x Fi.Ext_ad 8. MT.Bat_ad = 0.16113 x Fi.Bat_ad 9.foreach test sample
# Version 4
# 2019-16-23 1. if in2 = High then MT-IO setbit 0x04 2. IOST are uppercase 0xFF <= 0xff
# Version 3
# 2019-16-12 1. Add code_vesion 2. Add RFID

# Version 2
# 2019-16-06 fiexed Analog data requires 5 addresses

__code_version = 'fifo2mt.v7'

__autoSpeedforceIO = 5 #5km/h

    
Sampledat = [
    '$$126,867688039948074,15,A01,14|8.2,190626083616,A,13.904353,100.529748,0,44,135,0,2828,4000008A,02,0,520|5|430|13444E0,9F2|D6|6|3,,*28',
    '$$117,868998030242818,220,A01,,181112133629,A,13.904270,100.529836,0,179,2,0,0,0000,02,0,520|3|2337|28CA3B0,1A7|4DE|0|0,1,*04',    
    '$$119,868998030242818,221,A01,,181112133650,A,13.904270,100.529836,0,182,-12,0,0,0000,02,0,520|3|2337|28CA3B0,1A7|4E4|0|0,1,*6D',
    '$$o207,868998031044130,AAA,35,14.180526,100.597311,181113022225,A,12,8,0,274,0.8,0,1979805,3691944,520|15|17F3|011329E7,0000,0052|0000|0000|018C|0961,00000001,0|0|0|0,108,0000,,3,0,,0|0000|0000|0000|0000|0000*3F',
    '$$p207,868998031044130,AAA,35,14.180526,100.597311,181113022315,A,12,9,0,274,0.8,0,1979805,3691994,520|15|17F3|01132F0B,0000,0052|0000|0000|018D|0962,00000001,0|0|0|0,108,0000,,3,0,,0|0000|0000|0000|0000|0000*4B',
    '$$263,863835029419947,29,A01,,170705072751,A,22.621798,114.036116,57,0,126,1627,404,80000000,02,0,460|0|24A4|F82,13C|0,%^SUKSAWADDEE$SAITHARN$MISS^^?;6007643100500157891=150619800909=?+24 2 0004552 00100 ?,*4E',
    ]
       
    
Samplecmd = [
    '$$k28,864507030181266,B25,60*1B',
    '@@k28,864507030181266,B25,60*1B',
    '@@z25,864507030181266,E91*9B\r\n',
    '@@\60,864507030181266,C50,22,23,24,0,0,0,0,0,0,0,0,0,0,0,0,0*D4',
    '@@a31,868998030242818,C07,*102#*99', #This Fifo USSD for Dtac '*102#'
    '@@G25,864507030181266,B70*62']


import re

""" Calculate  the checksum for NMEA sentence 
    from a GPS device. An NMEA sentence comprises
    a number of comma separated fields followed by
    a checksum (in hex) after a "*". An example
    of NMEA sentence with a correct checksum (of
    0x76) is:
    
      GPGSV,3,3,10,26,37,134,00,29,25,136,00*76"
"""

def checksum(sentence,_verbose=False):
    #_verbose=True
    """ Remove any newlines """
    if re.search("\n$", sentence):
        sentence = sentence[:-1]

    #nmeadata,cksum = re.split(r'\*', sentence)
    
    #if _verbose:
    #    print(">>fun checksum:org nmeadata::[",nmeadata,"]")
    #    print(">>fun checksum:org cksum::[",cksum,"]")

    _s_loc = sentence.rfind('*')
    nmeadata = sentence[:_s_loc]
    cksum = sentence[_s_loc+1:len(sentence)]

    if _verbose:
        print(">>fun checksum:new _s_loc::[",_s_loc,"]")
        print(">>fun checksum:new nmeadata::[",nmeadata,"]")
        print(">>fun checksum:new cksum::[",cksum,"]")

    calc_cksum = 0
    for s in nmeadata:
        calc_cksum ^= ord(s)

    """ Return the nmeadata, the checksum from
        sentence, and the calculated checksum
    """
    return nmeadata,'0x'+cksum,hex(calc_cksum)






def fifo2mt(datin,_verbose=False):
    datret =""
    if _verbose:
        print(__code_version)
        print(datin)
    
    predat = datin.split(",")
    
    for (i, dat) in enumerate(predat):        
        if(len(dat)<1):
            if _verbose:
                print(">>Invalid empty/null str location: ",i,"autofix")
            predat[i] = '0' # autofix empty string  '' to '0' 
            
    if _verbose:
        print(predat)
    
    #if len(predat)<=2:
    if len(predat)<=10:
        return "" # warning small raw

            
    
    if not ( predat[3] =='A01'):
        if _verbose:
            print("# Wrong raw data Crazy protocol")
            
        return "" # error incorrect protocol
    
    #Fifo
    # 0 #<Len><ID><work-no>A01
    # 4 #<alm-code|alm-para><date-time><fix_flag><latitude>
    # 8 #<longitude><speed><course><altitude>
    # 12 #<odometer><fuel_consume><status><input-st>
    # 16 #<output-st><MCC|MNC|LAC|CI><bat-ad|ext-ad|ad1…adN><rfid_data>
    # 20 #<Temp digital-sensor>
    # 21 # <*Checksum>\r\n
    #Change fifo S20 <fuel_consume> to fifo S500-T <runtime> 
    
    #pre nstat of status
    #28 —31 satellite number, range [0,12], 
    #Example 80000000  means satellite number is 8 and no status bit
    
    #predat[14] = 'FFF'
    _nsat = int(predat[14][0],16) #Status
    
    
    
    #Version 5 New IO setbit 0x04 , Autospeed setbit 0x04
    
    #predat[15] = '2' #test i/o in2 = high ( 0b0010 )
    
    #predat[15] = '88' #test i/o
    #predat[15] = '8' #test i/o
    #predat[15] = 'af' #test i/o lowercase
    #predat[15] = '2' #test i/o
    
    #predat[9] = '299' #test speed
    #predat[9] = '9' #test speed
    #predat[9] = '4' #test speed

    
    #process hear
    
    int_iost = int(predat[15],16 )
    if not (int_iost & 2 ) == 0 :
        int_iost = int_iost | int('0x04',16)
    
    
    int_speed = int(predat[9])
    if int_speed > __autoSpeedforceIO:
        int_iost = int_iost | int('0x04',16)
    
    
    predat[15] = hex(int_iost)[2:] # hex(x)[2:] use hex() without 0x get the first two characters removed
       
    #pre iostatus
    if(len(predat[15])<2):
        predat[15] =  '0'+ predat[15]
         
    predat[15] =  predat[15][0] + predat[15][1] # fix ii
         
    if(len(predat[16])<2):
        predat[16] =  '0'+ predat[16]
    predat[16] =  predat[16][0] + predat[16][1] # fix oo         
    

    _iost = predat[15]+predat[16] #combine iostatus [input-st][output-st] ii oo -> iioo
    
    _iost = _iost.upper() #force UPcase 
        
    predat[18] = predat[18]+'|0|0|0|0|0' #Analog 0|1|2|3|4|5|6 ;  5 fields
    
    # 6. MT:: AD1|AD2|AD3|Battery analog|External power|AD4|AD5 <= Fi:: bat_ad|ext_ad|ad1|ad2|ad3
    _adcdat = predat[18].split('|')
    
    # 7. MT.Ext_ad = 3.86847 x Fi.Ext_ad 8. MT.Bat_ad = 0.16113 x Fi.Bat_ad
    c = _adcdat[0] #bat_ad
    a = int(c,16)
    a =a * 0.16113
    a = int(a)
    #print(hex(a))
    
    _adcdat[0] = hex(a).upper()[2:] # uppercase and remove 0x
    
    c = _adcdat[1] #ext_ad
    a = int(c,16)
    a =a * 3.86847
    a = int(a)
    #print(hex(a))
    
    _adcdat[1] = hex(a).upper()[2:] # uppercase and remove 0x

    _adcnew = _adcdat[2] + '|' + _adcdat[3] + '|' + _adcdat[4] + '|' + _adcdat[0] + '|' + _adcdat[1] + '|0|0|0|0|0'
    
    _rfid = predat[19] #load rfid
    _pcode = '35' # default
    
    #predat[4] = '36|8.2V' #  test value
    #predat[4] = '39|8.2V' #  test value
    #predat[4] = '' #  test value
    
    _almcodeparam = predat[4].split('|')
    
    
    _almcode = _almcodeparam[0]
    
    if len(_almcodeparam) >1 :
        _almparam = _almcodeparam[1]
    else :
        _almparam = ''
         
    if _verbose:   
        print(len(_almcodeparam))
        print(_almcode)
        print(_almparam)
    
    if int(_almcode) >0:
        _pcode = _almcode
        
    
    #if "37" in predat[4]:
        #_pcode = '37' #@Overide by Alm-code 37 to 37
    if int(_almcode) ==38:
        _pcode = '37'
        
    if int(_almcode) ==39:
        _pcode = '37'        

    if _verbose:
        print(_nsat)

    postdat=""
       
    postdat= postdat + predat[0]+','+ predat[1] + ',' + 'AAA' + ',' + _pcode + ','    # $$<Data identifier><Data length><IMEI>AAA<Event code>
    postdat= postdat + predat[7]+','+ predat[8] + ',' + predat[5] + ',' + predat[6] + ','    # <Latitude><Longitude><Date and time><Positioning status>
    postdat= postdat + str(_nsat) +',' + '8' +',' + predat[9] +',' + predat[10] +','    # <Number of satellites><GSM signal strength><Speed><Direction>
    postdat= postdat + '0.9' +',' + predat[11] +',' + predat[12] +',' + predat[13] +','    # <Horizontal dilution of precision(HDOP)><Altitude><Mileage><Total time>
    postdat= postdat + predat[17] +',' + _iost +',' + _adcnew +',' + _rfid +','    # <Base station info><I/O port status><Analog input value><Assisted event info>
    postdat= postdat + 'alm|' + predat[4] +',' + '108' +',' + '0' +',' + '0' +','    # <Customized data><Extended protocol version 108><Fuel percentage><Temperature sensor No. + Temperature value>
    postdat= postdat + '0' +',' + '0' +',' + '0' +',' + '0' +','    # <Data N>
    postdat= postdat +'*FF\r\n' # <*Checksum>\r\n
        
    
    if _verbose:
        print(postdat)    
    
    datret = postdat
    return datret

        

def mt2fi(datin,_verbose=False):
    datret =""
    if _verbose:
        print(__code_version)
        print(datin)
    
    
    if not ("@@" in datin):
        print("# Missing @@ raw data Crazy protocol")
        return "" # warning small raw
            
    txt = datin
    #txt = "@@J28,864507030181266,B25,60*FA"

    w = '1' #work no. simple alway 1

    #print(txt)

    #cut IMEI + Payload
    x = txt.find(",")
    #y = txt.find("*")
    y = txt.rfind("*")
    txt = txt[x+1:y]

    if _verbose:
        print(txt)
        print(x)
        print(y)


    #insert work-no
    x = txt.find(",")
    txt = txt[:x] +','+ w + txt[x:]
    
    if _verbose:
        print(txt)
        print(x)


    postdat='##'+ str(len(txt)+1) + ','+ txt #add , +1
       
    data,cksum,calc_cksum = checksum(postdat + '*FF') # add *FF to fix bug checksum 
    
    #calc_cksum = calc_cksum.upper() # uppercase
    
    calc_cksum = calc_cksum.upper()[2:] # uppercase and remove 0x
    
    if _verbose:
        print(calc_cksum)   

    postdat= postdat + '*' + calc_cksum + '\r\n' # <*Checksum>\r\n
        
    
    if _verbose:
        print(postdat)    
    
    datret = postdat
    return datret

        

def main():
    print("main program")
    

    """ NMEA sentence with checksum error (3rd field 
       should be 10 not 20)
    """
    line = "GPGSV,3,3,20,26,37,134,00,29,25,136,00*76\n"
    line = "GPGSV,3,3,20,26,37,134,0*0,29,25,136,00*76\n"

    """ Get NMEA data and checksums """    
    print("Input: %s" % (line))
    data,cksum,calc_cksum = checksum(line)

    """ Verify checksum (will report checksum error) """ 
    if cksum != calc_cksum:
        #print("Error in checksum for: %s" % (data))
        print("Error in checksum for: %s" % (line))
        print("Checksums are %s and %s" % (cksum,calc_cksum))
    else:
        print("Fun checksum fault!!")
        
    line = "GPGSV,3,3,10,26,37,134,00,29,25,136,00*76\n"
    
    """ Get NMEA data and checksums """
    print("Input: %s" % (line))
    data,cksum,calc_cksum = checksum(line)

    """ Verify checksum (will report checksum True) """ 
    if cksum == calc_cksum:
        #print("True in checksum for: %s" % (data))
        print("True in checksum for: %s" % (line))
        print("Checksums are %s and %s" % (cksum,calc_cksum))
    else:
        print("Fun checksum fault!!")        
    
    fifo2mt("SSS")
    fifo2mt("CCC",_verbose=True)
    
    for (i, dat) in enumerate(Sampledat):
        fifo2mt(dat,_verbose=True)
        
 
    mt2fi("SSS")
    mt2fi("CCC",_verbose=True)
    
    for (i, dat) in enumerate(Samplecmd):
        mt2fi(dat,_verbose=True)
 

if __name__=='__main__':
    main()



'''

fifo2mt.v6/7.error (DTAC *102#)
@@a31,868998030242818,C07,*102#*99
868998030242818,C07,
5
26
868998030242818,1,C07,
15
>>fun checksum: nmeadata::[ ##23,868998030242818,1,C07, ]
>>fun checksum: cksum::[ FF ]
4C
##23,868998030242818,1,C07,*4C

fifo2mt.v6/7 OK
@@G25,864507030181266,B70*62
864507030181266,B70
5
25
864507030181266,1,B70
15
>>fun checksum: nmeadata::[ ##22,864507030181266,1,B70 ]
>>fun checksum: cksum::[ FF ]
69
##22,864507030181266,1,B70*69

'''


'''
::Noted Fifo V1

FT A500
---------------------------------------------------------------------------
$$117,868998030242818,220,A01,,181112133629,A,13.904270,100.529836,0,179,2,0,0,0000,02,0,520|3|2337|28CA3B0,1A7|4DE|0|0,1,*04

$$119,868998030242818,221,A01,,181112133650,A,13.904270,100.529836,0,182,-12,0,0,0000,02,0,520|3|2337|28CA3B0,1A7|4E4|0|0,1,*6D


MT T333
---------------------------------------------------------------------------
$$o207,868998031044130,AAA,35,14.180526,100.597311,181113022225,A,12,8,0,274,0.8,0,1979805,3691944,520|15|17F3|011329E7,0000,0052|0000|0000|018C|0961,00000001,0|0|0|0,108,0000,,3,0,,0|0000|0000|0000|0000|0000*3F


$$p207,868998031044130,AAA,35,14.180526,100.597311,181113022315,A,12,9,0,274,0.8,0,1979805,3691994,520|15|17F3|01132F0B,0000,0052|0000|0000|018D|0962,00000001,0|0|0|0,108,0000,,3,0,,0|0000|0000|0000|0000|0000*4B

'''


'''
////

main program
fifo2mt v1
CCC
['CCC']
fifo2mt v1
$$117,868998030242818,220,A01,,181112133629,A,13.904270,100.529836,0,179,2,0,0,0000,02,0,520|3|2337|28CA3B0,1A7|4DE|0|0,1,*04
['$$117', '868998030242818', '220', 'A01', '0', '181112133629', 'A', '13.904270', '100.529836', '0', '179', '2', '0', '0', '0000', '02', '0', '520|3|2337|28CA3B0', '1A7|4DE|0|0', '1', '*04']
0
$$117,868998030242818,AAA,35,13.904270,100.529836,181112133629,A,0,8,0,179,0.9,2,0,0,520|3|2337|28CA3B0,0200,1A7|4DE|0|0|0000,1,0,108,0,0,0,0,0,0,*FF

fifo2mt v1
$$119,868998030242818,221,A01,,181112133650,A,13.904270,100.529836,0,182,-12,0,0,0000,02,0,520|3|2337|28CA3B0,1A7|4E4|0|0,1,*6D
['$$119', '868998030242818', '221', 'A01', '0', '181112133650', 'A', '13.904270', '100.529836', '0', '182', '-12', '0', '0', '0000', '02', '0', '520|3|2337|28CA3B0', '1A7|4E4|0|0', '1', '*6D']
0
$$119,868998030242818,AAA,35,13.904270,100.529836,181112133650,A,0,8,0,182,0.9,-12,0,0,520|3|2337|28CA3B0,0200,1A7|4E4|0|0|0000,1,0,108,0,0,0,0,0,0,*FF

fifo2mt v1
$$o207,868998031044130,AAA,35,14.180526,100.597311,181113022225,A,12,8,0,274,0.8,0,1979805,3691944,520|15|17F3|011329E7,0000,0052|0000|0000|018C|0961,00000001,0|0|0|0,108,0000,,3,0,,0|0000|0000|0000|0000|0000*3F
['$$o207', '868998031044130', 'AAA', '35', '14.180526', '100.597311', '181113022225', 'A', '12', '8', '0', '274', '0.8', '0', '1979805', '3691944', '520|15|17F3|011329E7', '0000', '0052|0000|0000|018C|0961', '00000001', '0|0|0|0', '108', '0000', '0', '3', '0', '0', '0|0000|0000|0000|0000|0000*3F']
# Wrong raw data Crazy protocol
1
$$o207,868998031044130,AAA,35,A,12,100.597311,181113022225,1,8,8,0,0.9,274,0.8,0,0000,3652,0052|0000|0000|018C|0961|0000,00000001,14.180526,108,0,0,0,0,0,0,*FF

fifo2mt v1
$$p207,868998031044130,AAA,35,14.180526,100.597311,181113022315,A,12,9,0,274,0.8,0,1979805,3691994,520|15|17F3|01132F0B,0000,0052|0000|0000|018D|0962,00000001,0|0|0|0,108,0000,,3,0,,0|0000|0000|0000|0000|0000*4B
['$$p207', '868998031044130', 'AAA', '35', '14.180526', '100.597311', '181113022315', 'A', '12', '9', '0', '274', '0.8', '0', '1979805', '3691994', '520|15|17F3|01132F0B', '0000', '0052|0000|0000|018D|0962', '00000001', '0|0|0|0', '108', '0000', '0', '3', '0', '0', '0|0000|0000|0000|0000|0000*4B']
# Wrong raw data Crazy protocol
1
$$p207,868998031044130,AAA,35,A,12,100.597311,181113022315,1,8,9,0,0.9,274,0.8,0,0000,3652,0052|0000|0000|018D|0962|0000,00000001,14.180526,108,0,0,0,0,0,0,*FF
'''

    
'''
A01 to AAA OK
[*] Received 130 bytes from local
[*] Timestamp: 2019-06-24 03:38:23.157259 
[*] Received--RAW
> 00000000  24 24 31 32 30 2c 38 36 37 36 38 38 30 33 39 39  |$$120,8676880399|
> 00000010  34 38 30 37 34 2c 32 44 2c 41 30 31 2c 2c 31 39  |48074,2D,A01,,19|
> 00000020  30 36 32 34 30 33 33 37 30 33 2c 41 2c 31 33 2e  |0624033703,A,13.|
> 00000030  39 30 34 33 35 33 2c 31 30 30 2e 35 32 39 37 34  |904353,100.52974|
> 00000040  38 2c 30 2c 35 34 2c 32 34 2c 30 2c 32 32 33 39  |8,0,54,24,0,2239|
> 00000050  2c 39 30 30 30 30 30 36 30 2c 30 32 2c 30 2c 35  |,90000060,02,0,5|
> 00000060  32 30 7c 35 7c 34 33 30 7c 31 33 34 31 37 30 30  |20|5|430|1341700|
> 00000070  2c 39 46 33 7c 31 34 41 7c 36 43 2c 2c 2a 37 31  |,9F3|14A|6C,,*71|
> 00000080  0d 0a                                            |..              |
[*] Received--TRANS--local
> 00000070  2a 32 36 0d 0a                                   |*26..           |
[*] Received--TRANS--local
[*] dataret0 =  $$107,867688039944529,AAA,35,13.904458,100.529778,190624033614,V,0,8,0,0,0.9,0,3,3592,0|0|0|0,0000,9D7|0|6C|0|0,0,15,108,0,0,0,0,0,0,*FF

[*] Received--TRANS 138 bytes from local
> 00000000  24 24 31 30 37 2c 38 36 37 36 38 38 30 33 39 39  |$$107,8676880399|
> 00000010  34 34 35 32 39 2c 41 41 41 2c 33 35 2c 31 33 2e  |44529,AAA,35,13.|
> 00000020  39 30 34 34 35 38 2c 31 30 30 2e 35 32 39 37 37  |904458,100.52977|
> 00000030  38 2c 31 39 30 36 32 34 30 33 33 36 31 34 2c 56  |8,190624033614,V|
> 00000040  2c 30 2c 38 2c 30 2c 30 2c 30 2e 39 2c 30 2c 33  |,0,8,0,0,0.9,0,3|
> 00000050  2c 33 35 39 32 2c 30 7c 30 7c 30 7c 30 2c 30 30  |,3592,0|0|0|0,00|
> 00000060  30 30 2c 39 44 37 7c 30 7c 36 43 7c 30 7c 30 2c  |00,9D7|0|6C|0|0,|
> 00000070  30 2c 31 35 2c 31 30 38 2c 30 2c 30 2c 30 2c 30  |0,15,108,0,0,0,0|
> 00000080  2c 30 2c 30 2c 2a 46 46 0d 0a                    |,0,0,*FF..      |
C06 resp err , try to encode AAA


[*] Received 125 bytes from local
[*] Timestamp: 2019-06-24 03:40:54.935605 
[*] Received--RAW
> 00000000  24 24 31 31 35 2c 38 36 37 36 38 38 30 33 39 39  |$$115,8676880399|
> 00000010  34 34 35 32 39 2c 31 2c 43 30 36 2c 38 36 37 36  |44529,1,C06,8676|
> 00000020  38 38 30 33 39 39 34 34 35 32 39 2c 34 35 2e 36  |88039944529,45.6|
> 00000030  33 2e 31 30 37 2e 31 30 38 3a 34 30 30 36 33 2c  |3.107.108:40063,|
> 00000040  54 43 50 3b 41 50 4e 3a 69 6e 74 65 72 6e 65 74  |TCP;APN:internet|
> 00000050  2c 2c 2c 45 58 54 3a 30 2e 30 30 56 2c 42 41 54  |,,,EXT:0.00V,BAT|
> 00000060  3a 33 2e 39 37 56 3b 42 30 33 3a 33 30 2c 35 30  |:3.97V;B03:30,50|
> 00000070  2c 41 43 43 20 4f 46 46 2a 31 36 0d 0a           |,ACC OFF*16..   |
[*] Received--TRANS--local
Fatal error: protocol.data_received() call failed.
protocol: <__main__.PyProxLocal object at 0x7fecb9176dd8>
transport: <_SelectorSocketTransport fd=7 read=polling write=<idle, bufsize=0>>
Traceback (most recent call last):
  File "/usr/local/lib/python3.7/asyncio/selector_events.py", line 824, in _read_ready__data_received
    self._protocol.data_received(data)
  File "5pyprox.pro.py", line 106, in data_received
    dataret0 = p0.fifo2mt(data.decode('utf8'),_verbose=False)
  File "/home/boon/fifo2mt.py", line 110, in fifo2mt
    _nsat = int(predat[14][0],16) #Status
IndexError: list index out of range
[!] Connection lost from local - ('1.47.161.29', 63531)
[+] New connection from local - ('1.46.136.50', 59199)
[+] Connection made to remote ('54.169.38.75', 30240)

[*] Received 125 bytes from local
[*] Timestamp: 2019-06-24 03:41:07.353119 
[*] Received--RAW
> 00000000  24 24 31 31 35 2c 38 36 37 36 38 38 30 33 39 39  |$$115,8676880399|
> 00000010  34 34 35 32 39 2c 31 2c 43 30 36 2c 38 36 37 36  |44529,1,C06,8676|
> 00000020  38 38 30 33 39 39 34 34 35 32 39 2c 34 35 2e 36  |88039944529,45.6|
> 00000030  33 2e 31 30 37 2e 31 30 38 3a 34 30 30 36 33 2c  |3.107.108:40063,|
> 00000040  54 43 50 3b 41 50 4e 3a 69 6e 74 65 72 6e 65 74  |TCP;APN:internet|
> 00000050  2c 2c 2c 45 58 54 3a 30 2e 30 30 56 2c 42 41 54  |,,,EXT:0.00V,BAT|
> 00000060  3a 33 2e 39 37 56 3b 42 30 33 3a 33 30 2c 35 30  |:3.97V;B03:30,50|
> 00000070  2c 41 43 43 20 4f 46 46 2a 31 36 0d 0a           |,ACC OFF*16..   |
[*] Received--TRANS--local
Fatal error: protocol.data_received() call failed.
protocol: <__main__.PyProxLocal object at 0x7fecb9176dd8>
transport: <_SelectorSocketTransport fd=7 read=polling write=<idle, bufsize=0>>
Traceback (most recent call last):
  File "/usr/local/lib/python3.7/asyncio/selector_events.py", line 824, in _read_ready__data_received
    self._protocol.data_received(data)
  File "5pyprox.pro.py", line 106, in data_received
    dataret0 = p0.fifo2mt(data.decode('utf8'),_verbose=False)
  File "/home/boon/fifo2mt.py", line 110, in fifo2mt
    _nsat = int(predat[14][0],16) #Status
IndexError: list index out of range
[!] Connection lost from local - ('1.46.136.50', 59199)
[+] New connection from local - ('1.47.43.66', 27415)
[+] Connection made to remote ('54.169.38.75', 30240)

[*] Received 125 bytes from local
[*] Timestamp: 2019-06-24 03:41:22.110951 
[*] Received--RAW

'''
