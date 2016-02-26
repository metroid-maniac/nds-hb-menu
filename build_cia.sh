GAME_TITLE="nds-hb-menu"
GAME_SUBTITLE1="built with devkitARM"
GAME_SUBTITLE2="http://devkitpro.org"
GAME_INFO="AMCE 01 0001DSBREW"
cp bootstrap/bootstrap.nds bootstrap.nds
#$DEVKITARM/bin/ndstool -c nds-hb-menu.raw.nds -9 hbmenu.elf -g $GAME_INFO -b icon.bmp "$GAME_TITLE;$GAME_SUBTITLE1;$GAME_SUBTITLE2"
#$DEVKITARM/bin/ndstool -c nds-hb-menu.nds -9 hbmenu.elf -h 0x3800 -g $GAME_INFO -b icon.bmp  "$GAME_TITLE;$GAME_SUBTITLE1;$GAME_SUBTITLE2"
$DEVKITARM/bin/ndstool -c nds-hb-menu.nds -9 hbmenu.elf -g $GAME_INFO -b icon.bmp  "$GAME_TITLE;$GAME_SUBTITLE1;$GAME_SUBTITLE2"

python patch_ndsheader_dsiware.py nds-hb-menu.nds
#python patch_ndsheader_dsiware.py NDS_Backup_Tool_Wifi.nds

#$DEVKITARM/bin/ndstool
$DEVKITARM/bin/ndstool -i nds-hb-menu.nds.orig.nds
$DEVKITARM/bin/ndstool -i nds-hb-menu.nds
#cp nds-hb-menu.nds nds-hb-menu.nds.crypt
#$DEVKITARM/bin/ndstool -sE nds-hb-menu.nds.crypt
$DEVKITARM/bin/ndstool -i nds-hb-menu.nds


$DEVKITARM/bin/ndstool -i WoodDumper_DSi_r89.nds
$DEVKITARM/bin/ndstool -i NDS_Backup_Tool_Wifi.nds
$DEVKITARM/bin/ndstool -i 00000000.nds

./make_cia.exe --srl=nds-hb-menu.nds