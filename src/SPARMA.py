#!/bin/python3
# -*- coding: utf-8 -*-

# SPARMA
# D C Potts 2024

# Built-in includes
import sys, os, logging, argparse, enum
import subprocess
from pathlib import Path

# Libary includes
from enum_actions import enum_action

# Application Includes
import Settings as settings
from Config import Config

def downloadMods(gameId, mods):
    return

def updateServer(config):
    logging.info("Updating via steam")

    # needs refactoring
    #
    # Update
    cmd = [config.steamcmdPath]
    cmd.extend(["+force_install_dir", config.getGamePathStr()])
    cmd.extend(["+login", config.steamUser])
    #cmd.extend(["+app_update", str(config.gameId)])

    for mod in config.modlist:
        cmd.extend(["+workshop_download_item", str(config.gameId), str(mod.id)])

    cmd.extend(["+quit"])
    #print(cmd)
    
    try:
        print(cmd)
        #subprocess.run(cmd, check = True)
    except subprocess.CalledProcessError as e:
        print("Subprocess error when updating:")
        print(e)
        sys.exit(1)
    
    #
    # Validate
    '''
    logging.info("Validating")
    cmd = [config.steamcmdPath]
    cmd.extend(["+force_install_dir", config.getGamePathStr()])
    cmd.extend(["+login", config.steamUser])
    #cmd.extend(["+app_update", str(config.gameId), "validate"])

    for mod in config.modlist:
        cmd.extend(["+workshop_download_item", str(config.gameId), str(mod.id)])
        cmd.extend(["validate"])

    cmd.extend(["+quit"])
    
    try:
        subprocess.run(cmd, check = True)
    except subprocess.CalledProcessError as e:
        print("Subprocess error when validating:")
        print(e)
        sys.exit(1)
    '''

    #
    # Mod folder
    logging.info("Updating symbolic links")
    # Make game mods folder if it doesn't exist
    try:
        os.mkdir(config.basePath / config.gameFolder / Path("mods"))
    except FileExistsError:
        pass


    # 
    # Each mod, unlink, rename files, link
    for mod in config.modlist:
        # needs shortening
        modLinkPath = config.basePath / config.gameFolder / Path("mods") / Path(str(mod.name))
        workshopPath = config.basePath / config.gameFolder / Path("steamapps/workshop/content") / Path(str(config.gameId)) / Path(str(mod.id))

        # Unlink previous (does this need to happen?)
        try:
            os.unlink(modLinkPath)
        except FileNotFoundError:
                pass

        # Rename all files (remove upper-case)
        #find . -depth -exec rename 's/(.*)\/([^\/]*)/$1\/\L$2/' {} \;
        cmd = ["find", ".", "-depth", "-exec",  "rename", "'s/(.*)\/([^\/]*)/$1\/\L$2/'", "{}", "\;"]
        subprocess.run(cmd, shell = True,  check = True, cwd = workshopPath)

        # Link
        cmd = ["ln", "-s", workshopPath, modLinkPath]
        subprocess.run(cmd, check = True)

    logging.info("Finished")
    return

def runServer(config):
    logging.info("Running Arma3 server")
    cmd = ["cd", str(config.gameFolder)]
    subprocess.run(cmd, check = True, shell = True)

    cmd = [str(config.basePath / config.gameFolder) + "/arma3server_x64", "-name=server", "-config=server.cfg"]
    modstring = "-mod="
    for mod in config.modlist:
        modstring += "mods/" 
        modstring += mod.name
        modstring += ";"

    cmd.extend([modstring[:-1]])
    subprocess.run(cmd, check = True, cwd=str(config.basePath / config.gameFolder))
    return

def runHeadless(config):
    logging.info("Running Arma3 headless client")
    cmd = ["cd", str(config.gameFolder)]
    subprocess.run(cmd, check = True, shell = True)

    cmd = [str(config.basePath / config.gameFolder) + "/arma3server_x64", "-client", "-connect=127.0.0.1", f"-password={config.serverPassword}"]
    modstring = "-mod="
    for mod in config.modlist:
        modstring += "mods/" 
        modstring += mod.name
        modstring += ";"

    cmd.extend([modstring[:-1]])
    os.chdir(config.basePath / config.gameFolder)
    subprocess.run(cmd, check = True, cwd=str(config.basePath / config.gameFolder))
    return

class CommandAction(enum.Enum):
    UPDATE = 1
    RUN = 2
    RUN_HEADLESS = 3

if __name__ == "__main__":
    print("-"*80)
    print(f"{settings.NAME} - v{settings.VERSION}")
    print("")
    if sys.stdout is not None:
        print("Encoding:", sys.stdout.encoding)
    print("-"*80, end=os.linesep*2)
    
    logging.basicConfig(level = logging.DEBUG)

    # Setup exception logging/display
    #sys.excepthook = excepthook

    parser = argparse.ArgumentParser(
        prog = "SPARMA",
        description = "Simple Arma3 linux server helper"
        )

    parser.add_argument(
        "action",
        action=enum_action(CommandAction),
        help="Action to run")

    parser.add_argument("configFile", type = argparse.FileType('r'))

    args = parser.parse_args()

    logging.info("Reading config")
    config = Config(args.configFile)

    # Targets Python < 3.10
    if args.action == CommandAction.UPDATE:
        updateServer(config)
    elif args.action == CommandAction.RUN:
        runServer(config)
    elif args.action == CommandAction.RUN_HEADLESS:
        runHeadless(config)
    else:
        logger.error("Unknown action supplied, exiting...")
        sys.exit(1)

