GAME_TITLE="nds-hb-menu"
GAME_SUBTITLE1="built with devkitARM"
GAME_SUBTITLE2="http://devkitpro.org"
GAME_INFO="DSHB 01 DSHOMEBREW"
$DEVKITARM/bin/ndstool -c nds-hb-menu.nds -9 hbmenu.elf -h 0xF70 -g $GAME_INFO -b icon.bmp  "$GAME_TITLE;$GAME_SUBTITLE1;$GAME_SUBTITLE2"

python patch_ndsheader_dsiware.py

./make_cia.exe --srl=nds-hb-menu.nds