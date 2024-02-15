#!/usr/bin/env python3
if __name__ != "__main__":
    print("attempted to load migrator.py as a module. this is unsupported. goodbye!")
    exit(0)

import os
import sys
from utils.save import load_save_as_dict, write_dict_as_save, write_timestamped_backup
write_timestamped_backup()
print("[info] your save has been backed up automatically, likely in the backups folder.")
# TODO: replace with input
print("[instruct] get your latest geometry dash save on your old account (either by cloud sync or local copy), close the game, and press enter to continue: ")

old_account_plist = load_save_as_dict()
"""
GJA_001 string username
GJA_003 int account id
GJA_005 string unknown
copy new save ids to old one and overwrite after writing old save
"""
print("[info] account data parsed, waiting for new account information.")
input("[instruct] log out of your old geometry dash account, log in to your new one, close the game, and press enter to continue: ")

new_account_plist = load_save_as_dict()

print("[info] copying new ids onto old save...")

old_account_plist["GJA_001"] = new_account_plist.get("GJA_001")
old_account_plist["GJA_003"] = new_account_plist.get("GJA_003")
old_account_plist["GJA_005"] = new_account_plist.get("GJA_005")

print("[info] modifications done, writing save...")
write_dict_as_save(old_account_plist)
print("[info] all done! refresh your login using your new account's credentials and upload your save.")