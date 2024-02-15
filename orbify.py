#!/usr/bin/env python3
if __name__ != "__main__":
    print("attempted to load orbify.py as a module. this is unsupported. goodbye!")
    exit(0)

from utils.save import load_save_as_dict, write_dict_as_save, write_timestamped_backup

write_timestamped_backup()
print("[info] your save has been backed up automatically, likely in the backups folder.")
print("[warn] make sure geometry dash is closed before running this!")
input("press ctrl+c to close, or enter to continue > ")
parsed_save = load_save_as_dict()

parsed_save.get("GS_value").update({'22': '999999999'}) # set stupid high to force a recalculation. https://twitter.com/TheRealGDColon/status/1753120438337646658
# official levels
for k, v in parsed_save.get("GLM_01").items():
    if v.get('k19') is None or v.get('k71') is None:
        continue
    if v.get('k19') != v.get('k71'):
        parsed_save["GLM_01"][k]["k71"] = v.get('k19') # update level orb count
        parsed_save["GS_10"][k] = str(v.get('k19')) # set dict orb count. also, why is this a string?
# custom levels
for k, v in parsed_save.get("GLM_03").items():
    if v.get('k19') is None or v.get('k71') is None:
        continue
    if v.get('k19') != v.get('k71'):
        parsed_save["GLM_03"][k]["k71"] = v.get('k19')
        parsed_save["GS_7"][k] = str(v.get('k19'))

# done with our changes! write the new save
write_dict_as_save(parsed_save)

print("[info] save has been modified!")