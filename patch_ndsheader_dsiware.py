# inspired from https://github.com/Relys/Project_CTR/blob/master/makerom/srl.h
from struct import *
from collections import namedtuple
from collections import OrderedDict
from pprint import pprint
import os, sys

def getSize(fileobject):
    fileobject.seek(0,2) # move the cursor to the end of the file
    size = fileobject.tell()
    return size

def skipUntilAddress(f_in,f_out, caddr, taddr):
    chunk = f_in.read(taddr-caddr)
    f_out.write(chunk)

#fname='nds-hb-menu.nds'
#fname='SUDOKU-Electronic_Arts_Inc..nds'
fname='00000000.nds'

file = open(fname, 'rb')
fsize=getSize(file)
file.close()

filer = open(fname, 'rb')
data = filer.read(0x300)

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
srlHeaderFormat='<12s4s2scbb9sbcIIIIIIIIIIIIIIIIIII2cHII8sII56s156s2s32s'
srlHeader=SrlHeader._make(unpack_from(srlHeaderFormat, data[0:0x17E]))
pprint(dict(srlHeader._asdict()))

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
srlTwlExtHeader=SrlTwlExtHeader._make(unpack_from(srlTwlExtHeaderFormat, data[0x180:0x300]))
pprint(dict(srlTwlExtHeader._asdict()))

# Fix srlTwlExtHeader
srlTwlExtHeader=srlTwlExtHeader._replace(
	title_id=			srlHeader.gameCode[::-1]+"\x04\x00\x03\x00",
	accessControl=		'\x10\x00\x00\x00',
	arm7ScfgExtMask=	'\x06\x00\x04\x00',
	arm7iLoadAddress=	srlHeader.arm7RamAddress,
	arm7iRomOffset=		srlHeader.arm7RomOffset,
	arm7iSize=			srlHeader.arm7Size,
	arm9iLoadAddress=	srlHeader.arm9RamAddress,
	arm9iRomOffset=		srlHeader.arm9RomOffset,
	arm9iSize=			srlHeader.arm9Size,
	twlRomSize=			fsize,
	configSettings=		"\x81\x85\x89\x8d\x80\x84\x88\x8c\x90\x94\x98\x9c\x80\x84\x88\x8c\x90\x94\x98\x9c\x00\x00\x00\x00@7\xc0\x07\x007@\x07\xc07\x00\x08@7\xc0\x07\x007@\x07\x0f\x00\x00\x03\x02\x00\x00\x00",
	pubSaveDataSize=	81920
	)
#pprint(dict(srlTwlExtHeader._asdict()))

data2=pack(*[srlTwlExtHeaderFormat]+srlTwlExtHeader._asdict().values())

# write the rest of the file
filew = open(fname+".tmp", "wb")
filew.write(data[0:0x180])
filew.write(data2)

skipUntilAddress(filer,filew,0x300,fsize)

filew.close()
filer.close()

#os.remove(fname)
#os.rename(fname+".tmp",fname)