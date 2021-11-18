from dislash import *
import nextcord
from .helper_cog import HelperCog
from sys import version_info, version
from helpful_modules import checks, cooldowns, custom_embeds
from helpful_modules.threads_or_useful_funcs import get_git_revision_hash

import resource
class MiscCommandsCog(HelperCog):
    def __init__(self,bot):
        super().__init__(bot)
        self.bot = bot
    
    @slash_command(name = "info", description = "Bot info!", options = [
      Option(name = "include_extra_info", description = "Whether to include extra, technical info", required = False, type = OptionType.BOOLEAN)
    ])
    async def info(self,inter, include_extra_info = False):
        embed = custom_embeds.SimpleEmbed(title = "Bot info")
        embed = embed.add_field(name = "Original Bot Developer", value = "ay136416#2707", inline = False) #Could be sufficient for attribution (except for stating changes).
        embed = embed.add_field(name = "Latest Git Version", value = str(get_git_revision_hash()), inline = False) 
        embed = embed.add_field(name = "Current Latency to Discord", value = self.bot.latency, inline = False)
        current_version_info = version_info
        python_version_as_str = f"Python {current_version_info.major}.{current_version_info.minor}.{current_version_info.micro}{current_version_info.releaselevel}"

        embed = embed.add_field(name = "Python version", value=python_version_as_str, inline = False)
        if include_extra_info:
            embed = embed.add_field(name= "Python version given by sys.version", value = str(version))
        
            embed = embed.add_field(name = "Nextcord version", value = str(nextcord.__version__))
            
            memory_limit = resource.getrlimit(resource.RUSAGE_SELF)[0]
            max_cpu = resource.RLIMIT_CPU
            current_usage = resource.getrusage(resource.RUSAGE_SELF)

            embed = embed.add_field(name = "Memory Usage", value = 
            f"{round((current_usage.ixrss/memory_limit)*1000)/100}%")
            embed = embed.add_field(name = "", value = "", inline = False)


        await inter.reply(embed=embed)

    
