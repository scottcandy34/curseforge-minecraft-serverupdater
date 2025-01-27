# Curseforge Minecraft Server Updater Tool
This tool will auto update upon start of server.

### Settings
In the updater.py file at the top labled settings
- projectID is the mod id number from curseforge site. Can be found on right side of page.
- copyFiles is a list of all files to be copied from the old release to the latest update.
- javaVersionRequired can be set to any specific JDK version from oracle.
- serverLaunch is the launch script for the server within the updated folder.

### Install and Running
- Please install python 3 to the system. This code was initially tested with 3.12.
- This was only tested on windows 10 and 11. Not mac or linux.
- This was only tested with (All the Mods 10 - ATM10)
- Just run the .bat file and it should launch it directecly

### Functionality
- Will first download latest serverpack from curseforge and extract it.
- Then will copy over all folders and files listed in 'copyFiles' setting.
- Will then remove all server folders but the latest 2. That way you have your prior copy.
- Will also remove any leftover server zipped file except the latest.
- It will then check the java version to match 'javaVersionRequired' setting.
- If it does not match will download it directly and place inside folder. Server will launch using this version over installed version.
- Finally will launch server script using 'serverLaunch' setting.

## Tasks
This is a work in progress and will get updated if needed. Please submit a pullrequest if you have fixed something or added functionality.
- Add Mac support
- Add Linux Support
- maybe add auto install python
- maybe add launch changelog as txt after updating.
