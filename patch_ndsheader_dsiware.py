# -*- coding: utf8 -*-
# inspired by https://github.com/Relys/Project_CTR/blob/master/makerom/srl.h
# if the header size of the input nds file is 0x200 (homebrew)
# 	the header size of the output nds file will be patched to 0x4000 (normal ds/dsi header), 0x3E00 offset
from struct import *
from collections import namedtuple
from collections import OrderedDict
from pprint import pprint
import os, sys
import binascii

#
# CRC16 MODULE
#
# includes CRC16 and CRC16 MODBUS
#

from ctypes import c_ushort

# from https://github.com/cristianav/PyCRC/blob/master/demo.py
class CRC16(object):
    crc16_tab = []

    # The CRC's are computed using polynomials. Here is the most used
    # coefficient for CRC16
    crc16_constant = 0xA001  # 40961

    def __init__(self, modbus_flag=False):
        # initialize the precalculated tables
        if not len(self.crc16_tab):
            self.init_crc16()
        self.mdflag = bool(modbus_flag)

    def calculate(self, input_data=None):
        try:
            is_string = isinstance(input_data, str)
            is_bytes = isinstance(input_data, (bytes, bytearray))

            if not is_string and not is_bytes:
                raise Exception("Please provide a string or a byte sequence "
                                "as argument for calculation.")

            crc_value = 0x0000 if not self.mdflag else 0xffff

            for c in input_data:
                d = ord(c) if is_string else c
                tmp = crc_value ^ d
                rotated = crc_value >> 8
                crc_value = rotated ^ self.crc16_tab[(tmp & 0x00ff)]

            return crc_value
        except Exception as e:
            print("EXCEPTION(calculate): {}".format(e))

    def init_crc16(self):
        """The algorithm uses tables with precalculated values"""
        for i in range(0, 256):
            crc = c_ushort(i).value
            for j in range(0, 8):
                if crc & 0x0001:
                    crc = c_ushort(crc >> 1).value ^ self.crc16_constant
                else:
                    crc = c_ushort(crc >> 1).value
            self.crc16_tab.append(crc)

def getSize(fileobject):
    fileobject.seek(0,2) # move the cursor to the end of the file
    size = fileobject.tell()
    return size

def skipUntilAddress(f_in,f_out, caddr, taddr):
    chunk = f_in.read(taddr-caddr)
    f_out.write(chunk)
	
def writeBlankuntilAddress(f_out, caddr, taddr):
	f_out.write("\x00"*(taddr-caddr))

fname='nds-hb-menu.nds'
#fname='hbmenu.nds'
#fname='SUDOKU-Electronic_Arts_Inc..nds'
#fname='00000000.nds'
#fname='WoodDumper_DSi_r89.nds'
#fname='NDS_Backup_Tool_Wifi.nds'
#fname='bootstrap.nds'

#offset of 0x4600 created

# File size compute
file = open(fname, 'rb')
fsize=getSize(file)
file.close()

#CRC header compute "CRC-16 (Modbus)"
file = open(fname, 'rb')
#0x15E from https://github.com/devkitPro/ndstool/ ... source/header.cpp
hdr = file.read(0x15E)
hdrCrc=CRC16(modbus_flag=True).calculate(hdr)
print("{:10s} {:20X}".format('HDR CRC-16 ModBus', hdrCrc))
#print "origin header cr c"+hdr[0x15E:0x15F]
filew = open(fname+".hdr", "wb")
filew.write(hdr);
filew.close()
file.close()


filer = open(fname, 'rb')
data = filer.read(0x180)
caddr=0x180

SrlHeader = namedtuple('SrlHeader', 
	"gameTitle "
	"gameCode "
	"makerCode "
	"unitCode "
	"encryptionSeedSelect "
	"deviceCapacity "
	"reserved0 " 
	"romVersion "
	"internalFlag "
	"arm9RomOffset "
	"arm9EntryAddress "
	"arm9RamAddress "
	"arm9Size "
	"arm7RomOffset "
	"arm7EntryAddress "
	"arm7RamAddress "
	"arm7Size "
	"fntOffset "
	"fntSize "
	"fatOffset "
	"fatSize "
	"arm9OverlayOffset "
	"arm9OverlaySize "
	"arm7OverlayOffset "
	"arm7OverlaySize "
	"normalCardControlRegSettings "
	"secureCardControlRegSettings "
	"icon_bannerOffset "
	"secureAreaCrc "
	"secure_transfer_timeout "
	"arm9Autoload "
	"arm7Autoload "
	"secureDisable "
	"ntrRomSize "
	"headerSize "
	"reserved1 "
	"nintendoLogo "
	"nintendoLogoCrc "
	"headerCrc "
	"debugReserved ")
srlHeaderFormat='<12s4s2scbb9sbcIIIIIIIIIIIIIIIIIIIHHII8sII56s156s2sH32s'
srlHeader=SrlHeader._make(unpack_from(srlHeaderFormat, data))
#pprint(dict(srlHeader._asdict()))
print "origin header crc "+hex(srlHeader.headerCrc)
print "origin secure crc "+hex(srlHeader.secureAreaCrc)

#SecureArea CRC compute "CRC-16 (Modbus)"
file = open(fname, 'rb')
#0x15E from https://github.com/devkitPro/ndstool/ ... source/header.cpp
file.read(0x200)
sec = file.read(0x4000)
secCrc=CRC16(modbus_flag=True).calculate(sec)
print("{:10s} {:20X}".format('SEC CRC-16 ModBus', secCrc))
#print "origin header cr c"+hdr[0x15E:0x15F]
filew = open(fname+".sec", "wb")
filew.write(sec);
filew.close()
file.close()
srlHeaderPatched=srlHeaderPatched._replace(secureAreaCrc=secCrc)

# Fix srlHeader
srlHeaderPatched=srlHeader._replace(
	secureCardControlRegSettings=	1575160,
	normalCardControlRegSettings=	5791744,
	internalFlag=					'\x00',
	arm9RomOffset=					srlHeader.arm9RomOffset+0x3E80,
	arm7RomOffset=					srlHeader.arm7RomOffset+0x3E80,
	fatOffset=						srlHeader.fatOffset+0x3E80,
	fntOffset=						srlHeader.fntOffset+0x3E80,
	icon_bannerOffset=				srlHeader.icon_bannerOffset+0x3E80,						
	ntrRomSize=						srlHeader.ntrRomSize+0x3E80,	
	headerSize=						0x4000,
	nintendoLogo= 					"$\xff\xaeQi\x9a\xa2!=\x84\x82\n\x84\xe4\t\xad\x11$\x8b\x98\xc0\x81\x7f!\xa3R\xbe\x19\x93\t\xce \x10FJJ\xf8'1\xecX\xc7\xe83\x82\xe3\xce\xbf\x85\xf4\xdf\x94\xceK\t\xc1\x94V\x8a\xc0\x13r\xa7\xfc\x9f\x84Ms\xa3\xca\x9aaX\x97\xa3'\xfc\x03\x98v#\x1d\xc7a\x03\x04\xaeV\xbf8\x84\x00@\xa7\x0e\xfd\xffR\xfe\x03o\x950\xf1\x97\xfb\xc0\x85`\xd6\x80%\xa9c\xbe\x03\x01N8\xe2\xf9\xa24\xff\xbb>\x03Dx\x00\x90\xcb\x88\x11:\x94e\xc0|c\x87\xf0<\xaf\xd6%\xe4\x8b8\n\xacr!\xd4\xf8\x07",
	nintendoLogoCrc= 				'V\xcf',
	secureAreaCrc=secCrc
	)
data1=pack(*[srlHeaderFormat]+srlHeaderPatched._asdict().values())
newHdrCrc=CRC16(modbus_flag=True).calculate(data1[0:0x15E])
srlHeaderPatched=srlHeaderPatched._replace(headerCrc=newHdrCrc)
print "new header crc "+hex(newHdrCrc)
#pprint(dict(srlHeaderPatched._asdict()))



data1=pack(*[srlHeaderFormat]+srlHeaderPatched._asdict().values())

#TWL Only Data
SrlTwlExtHeader = namedtuple('SrlTwlExtHeader', 
	"configSettings "
	"accessControl "
	"arm7ScfgExtMask "
	"reserved_flags "
	"arm9iRomOffset "
	"reserved2 "
	"arm9iLoadAddress "
	"arm9iSize "
	"arm7iRomOffset "
	"struct_param_baseAddress "
	"arm7iLoadAddress "
	"arm7iSize "
	"digest_ntrRegionOffset "
	"digest_ntrRegionSize "
	"digest_twlRegionOffset "
	"digest_twlRegionSize "
	"digestSectorHashtableOffset "
	"digestSectorHashtableSize "
	"digest_blockHashtableOffset "
	"digest_blockHashtableSize "
	"digestSectorSize "
	"digest_blockSectorcount "
	"reserved3 "
	"twlRomSize "
	"unknown "
	"modcryptArea1Offset "
	"modcryptArea1Size "
	"modcryptArea2Offset "
	"modcryptArea2Size "
	"title_id "
	"pubSaveDataSize "
	"privSaveDataSize "
	"reserved4")
srlTwlExtHeaderFormat="<52s4s4s4sI4sIIIIIIIIIIIIIIII8sQ8sIIII8sII192s"
if srlHeader.headerSize<0x300:
	#homebrew
	srlTwlExtHeader=SrlTwlExtHeader._make(unpack_from(srlTwlExtHeaderFormat, "\x00" * (0x300-0x180)))
else:
	data = filer.read(0x300-0x180)
	srlTwlExtHeader=SrlTwlExtHeader._make(unpack_from(srlTwlExtHeaderFormat, data))
	caddr=0x300

#pprint(dict(srlTwlExtHeader._asdict()))

# Fix srlTwlExtHeader
srlTwlExtHeader=srlTwlExtHeader._replace(
	title_id=			srlHeader.gameCode[::-1]+"\x04\x00\x03\x00",
	#accessControl=		'\x10\x1C\x00\x00',
	#arm7ScfgExtMask=	'\x06\x00\x04\x00',
	#arm7iLoadAddress=	srlHeader.arm7RamAddress,
	#arm7iRomOffset=		srlHeader.arm7RomOffset,
	#arm7iSize=			srlHeader.arm7Size,
	#arm9iLoadAddress=	srlHeader.arm9RamAddress,
	#arm9iRomOffset=		srlHeader.arm9RomOffset,
	#arm9iSize=			srlHeader.arm9Size,
	#twlRomSize=			fsize,
	configSettings= 	'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xff\xff\xff\xff',
	#pubSaveDataSize=	81920,
	reserved3=			'@\x08\x00\x00\x00\x00\x01\x00',
	reserved_flags=		'\x00\x00\x00\x10'
	)
pprint(dict(srlTwlExtHeader._asdict()))

data2=pack(*[srlTwlExtHeaderFormat]+srlTwlExtHeader._asdict().values())

#TWL and Signed NTR
SrlSignedHeader = namedtuple('SrlSignedHeader', 
	"arm9WithSecAreaSha1Hmac "
	"arm7Sha1Hmac "
	"digestMasterSha1Hmac "
	"bannerSha1Hmac "
	"arm9iSha1Hmac "
	"arm7iSha1Hmac "
	"reserved5 "
	"arm9Sha1Hmac "
	"reserved6 "
	"reserved7 "
	"signature "
	)
srlSignedHeaderFormat="<s20s20s20s20s20s20s0x40s20s2636s384s128"
if srlHeader.headerSize<0x1100:
	#homebrew
	srlSignedHeader=SrlSignedHeader._make(unpack_from(srlSignedHeaderFormat, "\x00" * (0x1081-0x300)))
else:
	data = filer.read(0x1081-0x300)
	srlSignedHeader=SrlSignedHeader._make(unpack_from(srlSignedHeaderFormat, data))
	caddr=0x1081

#pprint(dict(srlSignedHeader._asdict()))

# Fix srlSignedHeader
srlSignedHeader=srlSignedHeader._replace(
	arm7Sha1Hmac=				'\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff',
	arm9iSha1Hmac=				'\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\x00',
	bannerSha1Hmac=				'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xff',
	digestMasterSha1Hmac=		'\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\x00',
	arm9WithSecAreaSha1Hmac=	'\xff'
)
pprint(dict(srlSignedHeader._asdict()))

data3=pack(*[srlSignedHeaderFormat]+srlSignedHeader._asdict().values())

# write the file
filew = open(fname+".tmp", "wb")
filew.write(data1)
filew.write(data2)
filew.write(data3[0:0xC80])
filew.write('\xff\xff\xff\xff\xff\xff\xff\xff')
filew.write('\xff\xff\xff\xff\xff\xff\xff\xff')
filew.write('\xff\xff\xff\xff\xff\xff\xff\xff')
filew.write('\xff\xff\xff\xff\xff\xff\xff\xff')
filew.write('\xff\xff\xff\xff\xff\xff\xff\xff')
filew.write('\xff\xff\xff\xff\xff\xff\xff\xff')
filew.write('\xff\xff\xff\xff\xff\xff\xff\xff')
filew.write('\xff\xff\xff\xff\xff\xff\xff\xff')
filew.write('\xff\xff\xff\xff\xff\xff\xff\xff')
filew.write('\xff\xff\xff\xff\xff\xff\xff\xff')
filew.write('\xff\xff\xff\xff\xff\xff\xff\xff')
filew.write('\xff\xff\xff\xff\xff\xff\xff\xff')
filew.write('\xff\xff\xff\xff\xff\xff\xff\xff')
filew.write('\xff\xff\xff\xff\xff\xff\xff\xff')
filew.write('\xff\xff\xff\xff\xff\xff\xff\xff')
filew.write('\xff\xff\xff\xff\xff\xff\xff\xff')
writeBlankuntilAddress(filew,0x1000,0x4000);

skipUntilAddress(filer,filew,caddr,fsize);

filew.close()
filer.close()
if os.path.exists(fname+".orig.nds"):
	os.remove(fname+".orig.nds")
os.rename(fname,fname+".orig.nds")
#os.remove(fname)
os.rename(fname+".tmp",fname)