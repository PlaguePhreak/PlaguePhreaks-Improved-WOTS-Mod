#!/bin/bash
# one ship: bundle -> obj -> 3 break kits; keeps .brk, removes big objs unless KEEP
n=$1; SEA=/mnt/user-data/uploads/StreamingAssets/override/unit/sea; K=/tmp/claude-0/kits
[ -f $K/brk/$n/${n}_aft.brk ] && exit 0
mkdir $K/lock_$n 2>/dev/null || exit 0
[ -f $SEA/$n/$n ] || { echo "$n NOBUNDLE" >> $K/log.txt; exit 0; }
timeout 900 python3 -I /mnt/project-files/ship_break/tools/ship2mesh.py $SEA $n $K/obj/$n > $K/logs/$n.txt 2>&1 || { echo "$n MESHFAIL" >> $K/log.txt; exit 0; }
timeout 2400 python3 /mnt/project-files/ship_break/tools/break2.py -- $K/obj/$n/$n.obj $K/obj/$n/${n}_mats.json $K/brk/$n $n fore:0.28,mid:0,aft:-0.28 3 >> $K/logs/$n.txt 2>&1
if [ -f $K/brk/$n/${n}_aft.brk ]; then echo "$n OK $(grep '^cut' $K/logs/$n.txt | tr '\n' ' ')" >> $K/log.txt; else echo "$n BREAKFAIL" >> $K/log.txt; fi
if ! grep -qw $n $K/keep.txt; then rm -f $K/brk/$n/*.obj $K/brk/$n/*.mtl; rm -rf $K/obj/$n; fi
