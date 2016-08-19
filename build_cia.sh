GAME_TITLE="nds-hb-menu"
GAME_SUBTITLE1="built with devkitARM"
GAME_SUBTITLE2="http://devkitpro.org"
GAME_INFO="KHBE 01 TWLHOMEBREW"

cp bootstrap/bootstrap.*.elf .
$DEVKITARM/bin/ndstool	-c bootstrap.nds -7 bootstrap.arm7.elf -9 bootstrap.arm9.elf -g $GAME_INFO -b icon.bmp  "$GAME_TITLE;$GAME_SUBTITLE1;$GAME_SUBTITLE2"  -r9 0x2000000 -r7 0x2380000 -e9 0x2000000 -e7 0x2380000
python patch_ndsheader_dsiware.py --read bootstrap.nds > bootstrap.nds_before_patch_header.txt
python patch_ndsheader_dsiware.py --mode dsi bootstrap.nds
python patch_ndsheader_dsiware.py --read bootstrap.nds > bootstrap.nds_after_patch_header.txt

$DEVKITARM/bin/ndstool -c nds-hb-menu.nds -7 hbmenu.arm7.elf -9 hbmenu.arm9.elf -g $GAME_INFO -b icon.bmp  "$GAME_TITLE;$GAME_SUBTITLE1;$GAME_SUBTITLE2"
cp nds-hb-menu.nds nds-hb-menu-ds.nds
cp nds-hb-menu.nds nds-hb-menu-ds-r4.nds
cp nds-hb-menu.nds nds-hb-menu-dsi.nds
cp nds-hb-menu.nds nds-hb-menu-dsi-r4.nds
cp nds-hb-menu.nds nds-hb-menu-dsi-dldi.nds
cp nds-hb-menu.nds nds-hb-menu-dsi-nogba.nds

./dlditool.exe BootStrap/r4tfv2.dldi nds-hb-menu-dsi-r4.nds
./dlditool.exe BootStrap/r4tfv2.dldi nds-hb-menu-ds-r4.nds
./dlditool.exe dsisd.dldi nds-hb-menu-dsi-dldi.nds

python patch_ndsheader_dsiware.py --mode ds  --title "NDSHOMEBREW" --maker 01 --code ASMP  nds-hb-menu-ds.nds
python patch_ndsheader_dsiware.py --mode ds  --title "NDSHOMEBREW" --maker 01 --code ASMP  nds-hb-menu-ds-r4.nds
python patch_ndsheader_dsiware.py --mode dsi nds-hb-menu-dsi.nds 
python patch_ndsheader_dsiware.py --mode dsi nds-hb-menu-dsi-r4.nds
python patch_ndsheader_dsiware.py --mode dsi nds-hb-menu-dsi-dldi.nds
python patch_ndsheader_dsiware.py --mode dsinogba nds-hb-menu-dsi-nogba.nds

python patch_ndsheader_dsiware.py --read nds-hb-menu.nds > nds-hb-menu.nds_header.txt

python patch_ndsheader_dsiware.py --read nds-hb-menu-ds.nds > nds-hb-menu-ds.nds_header.txt

python patch_ndsheader_dsiware.py --read nds-hb-menu-dsi.nds > nds-hb-menu-dsi.nds_header.txt

./make_cia.exe --srl=nds-hb-menu-ds.nds
./make_cia.exe --srl=nds-hb-menu-dsi.nds
./make_cia.exe --srl=nds-hb-menu-dsi-r4.nds
./make_cia.exe --srl=nds-hb-menu-dsi-dldi.nds
./make_cia.exe --srl=bootstrap.nds