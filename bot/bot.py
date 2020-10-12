import os
import logging
import discord
import discord.ext
from time import localtime, strftime

from bot.features.insult.insult import Insult
from bot.features.music.music import Music


class Bot(discord.ext.commands.Bot):
    """
    The Bot class.
    The bot can do lots of neat things
    """
    def __init__(self, CONFIG, OSTYPE):

        self.CONFIG = CONFIG
        self.OSTYPE = OSTYPE
        self.cogList = []
        self.thread = ""
        self.loop = ""

        # Check bot for minimal required params to make bot run properly
        REQUIRED_PARAMS = [
            'bot_name', 'bot_id', 'token', 'command_prefix', 'logging'
        ]
        MISSING_PARAMS = [
            param for param in REQUIRED_PARAMS if not CONFIG.get(param)
        ]
        if MISSING_PARAMS:
            raise AssertionError(f"config.yaml missing {MISSING_PARAMS}")

        # Pull information out of parsed config file
        self.name = CONFIG.get('bot_name')
        self.bot_id = CONFIG.get('bot_id')
        self.token = CONFIG.get('token')
        self.command_prefix = CONFIG.get('command_prefix')
        self.enabled_features = CONFIG.get('enabled_features')
        self.logging = CONFIG.get('logging')

        super().__init__(self.command_prefix)

        if self.logging:
            self.setupLogging()

        self.enableFeatures()

        self.log.info("Bot initalized")

    def setupLogging(self):
        # Logging setup
        try:
            if self.OSTYPE == "win":
                logPath = "logs"
            else:
                logPath = f"{os.sep}var{os.sep}log{os.sep}discordbot"

            os.mkdir(logPath)
        except FileExistsError:
            pass
        except Exception as e:
            raise AssertionError(
                f"logs directory was not able to be created for some reason: {e}"
            )

        FORMAT = "%(asctime)s:%(levelname)s:%(name)s: %(message)s"
        DATE_STAMP = strftime("%Y-%m-%d", localtime())
        FILE_NAME = f"{logPath}{os.sep}discordBot-{self.name}-{DATE_STAMP}.log"

        self.log = logging.getLogger(f"{self.name} Logger")
        self.log.setLevel(self.CONFIG['logging']['logging_level'])
        self.handler = logging.FileHandler(filename=FILE_NAME)
        self.handler.setFormatter(logging.Formatter(FORMAT))
        self.log.addHandler(self.handler)

    def enableFeatures(self):
        print(f"\n{self.name} enabled features:")
        for feature in self.enabled_features:
            if self.enabled_features[feature]["enabled"]:
                cog = getattr(
                    self, f"get{feature.capitalize()}", lambda:
                    (_ for _ in ()).throw(
                        Exception(
                            f"Feature {feature} does not exist. Review config.yaml"
                        )))()
                self.cogList.append(cog)
                self.cogList[-1].enableCog()
                print(f'  {feature}')
        print("")

    def get_token(self):
        return self.token

    def getMusic(self):
        return Music(self)

    def getInsult(self):
        return Insult(self)
