#!/bin/bash
mkdir db

echo "python bgplgdb.py >db/bgplgdb"
python bgplgdb.py >db/bgplgdb

echo "python wikiixp.py >db/wikiixp"
python wikiixp.py >db/wikiixp

echo "python pch.py db"
python pch.py db
