# -*- coding: utf-8 -*-
# SPARMA
# D C Potts 2024

import sys, os, logging
from  pathlib import Path
from typing import TextIO

from yaml import safe_load, YAMLError

from Mod import Mod

class Config:
    steamUser = None
    basePath = None
    steamcmdPath = None
    gameFolder = None
    gameId = None
    serverPassword = None

    def __init__(self, configFile: TextIO):
        print(configFile)

        self.basePath = Path(os.path.realpath(configFile.name)).parent
        logging.debug(f"Base path: {self.basePath}")

        try:
            yaml = safe_load(configFile)
        except YAMLError as e:
            logger.error(f"YAMLError when reading config file '{configFile.name}'")
            sys.exit(1)

        self.steamUser = yaml["paths"]["steam_user"]
        self.steamcmdPath = Path(yaml["paths"]["steamcmd_path"])
        self.gameFolder = Path(yaml["paths"]["arma_path"])
        self.gameId = yaml["paths"]["game_workshop_id"]
        self.serverPassword = yaml["paths"]["server_password"]

        self.modlist = []
        for key, item in yaml["mods"].items():
            self.modlist.append(Mod(key, item))

        logging.info(f"Loaded {len(self.modlist)} mod(s) from config file")

    def getGamePathStr(self):
        return str(self.basePath / self.gameFolder)




