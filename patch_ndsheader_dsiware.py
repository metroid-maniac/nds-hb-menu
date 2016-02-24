# inspired by https://github.com/Relys/Project_CTR/blob/master/makerom/srl.h
# if the header size of the input nds file is 0x200 (homebrew)
# 	the header size of the output nds file will be patched to 0x4000 (normal ds/dsi header), 0x3E00 offset
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

file = open(fname, 'rb')
fsize=getSize(file)
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
srlHeaderFormat='<12s4s2scbb9sbcIIIIIIIIIIIIIIIIIII2cHII8sII56s156s2s32s'
srlHeader=SrlHeader._make(unpack_from(srlHeaderFormat, data[0:0x17E]))
pprint(dict(srlHeader._asdict()))

# Fix srlHeader
srlHeaderPatched=srlHeader._replace(
	#arm7Autoload=					33557088,
	secure_transfer_timeout=		'\xfa',
	secureDisable=					37224728,
	secureAreaCrc=					'o',
	secureCardControlRegSettings=	1575160,
	normalCardControlRegSettings=	5791744,
	arm9RomOffset=					srlHeader.arm9RomOffset+0x3E80,
	arm7RomOffset=					srlHeader.arm9RomOffset+0x3E80,
	fatOffset=						srlHeader.fatOffset+0x3E80,
	fntOffset=						srlHeader.fntOffset+0x3E80,
	icon_bannerOffset=				srlHeader.icon_bannerOffset+0x3E80,
	headerSize=						srlHeader.headerSize+0x3E80,
	reserved1=						0x4000
	)
pprint(dict(srlHeaderPatched._asdict()))

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
if srlHeader.reserved1<0x300:
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
if srlHeader.reserved1<0x1100:
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
writeBlankuntilAddress(filew,0x17E,0x180);
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