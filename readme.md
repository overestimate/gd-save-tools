# gd-tools
misc. tools for manipulating geometry dash save data
## prerequisites
install python 3.11 and then `pip install -r requirements.txt`.
## orbify
grant all mana orbs for progress prior to when they were added.
### usage
`python orbify.py`, should automatically back up your save, edit it, and copy the edited one into place.
## migrator
allows for copying user ids from one account onto another's save, which lets you migrate your account (ie to change email). **cannot copy server-side stuff like your levels, likes, comments, friends, etc.**
### usage
`python migrator.py`, follow the steps it tells you. once done, your save should be migrated.
