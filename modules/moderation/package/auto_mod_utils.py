import re

from modules.moderation.package.enums import BannedWord, ExternalLinks, ModFormat
from modules.package.enums import *
from modules.package.utils import *
from modules.moderation.package.commands_functions import handle_case


DISCORD_URLS =  ['discord.com', 'discord.gg', 'discord.gift', 'dis.gd']
UPPERCASE_MAX = 70  # %


async def check_for_banned_words(bot, guild, member, message):
    
    json_file = open_json("data/moderation.json")

    guild_id = str(guild.id)
    member = guild.get_member(member.id)

    punishments = []

    for entry in json_file[guild_id][ModFormat.banned_words.value].values():
        word = entry[BannedWord.word.value]

        if word in message.content.lower():
            punishments.append(entry)

    if len(punishments) != 0:

        await message.delete()

        punishments.sort(key = lambda punishment: punishment[BannedWord.flags.value][BannedWord.flag_type.value])
        
        highest_punishments = [punishments[0]]
        highest_punishment = punishments[0]

        index = 1
        while index < len(punishments) \
            and highest_punishment[BannedWord.flags.value][BannedWord.flag_type.value] == punishments[index][BannedWord.flags.value][BannedWord.flag_type.value]:
            highest_punishments.append(punishments[index])
            index += 1

        highest_punishments.sort(
            key = lambda punishment: punishment[BannedWord.flags.value][BannedWord.flag_duration.value], 
            reverse = highest_punishment[BannedWord.flags.value][BannedWord.flag_type.value] == 'mute'
        )
        
        punishment_to_apply = highest_punishments[0]
        notify_channel = None

        if punishment_to_apply[BannedWord.flags.value][BannedWord.flag_notify_channel.value] != 0:
            notify_channel = bot.get_channel(punishment_to_apply[BannedWord.flags.value][BannedWord.flag_notify_channel.value])


        await handle_case(
            bot = bot,
            guild = guild, 
            channel = notify_channel,
            moderator = bot.user,
            user = member,
            case_type = punishment_to_apply[BannedWord.flags.value][BannedWord.flag_type.value],
            reason = f"Usage of banned word **({punishment_to_apply[BannedWord.word.value]})**",
            duration = punishment_to_apply[BannedWord.flags.value][BannedWord.flag_duration.value],
            message = message.content
        )



def link_protected(guild, user, channel):
    
    json_file = open_json("data/moderation.json")
    
    member = guild.get_member(user.id)
    channel_id = channel.id 
    guild_id = str(guild.id)

    if channel_id in json_file[guild_id][ModFormat.links.value][ExternalLinks.protected_channels.value]:
        return True

    for role in member.roles:
        
        if role.id in json_file[guild_id][ModFormat.links.value][ExternalLinks.protected_roles.value]:
            return True

    return False


async def check_for_external_links(guild, user, message):

    if not link_protected(guild, user, message.channel):

        urls = get_urls(message.content)

        for url in urls:

            url_domain = url.replace("https://", "")
            url_domain = url_domain.replace("http://", "")
            url_domain = url_domain.split('/', 1)[0]
            
            if url_domain not in DISCORD_URLS:
                
                try:
                    await message.delete()
                    await user.send(f"{Emotes.no_entry.value} You can not post links from that website!")
                except:
                    pass


async def check_for_mass_mention(bot, guild, user, message):
    
    if len(message.mentions) > 6:
        
        await handle_case(
            bot, 
            guild,
            message.channel,
            moderator = bot.user,
            user = user,
            case_type = 'warn',
            reason = 'Mass Mention'
        )


async def check_for_excesive_caps(user, message):
    
    message_content = message.content
    message_content = message_content.strip().replace(' ', '')

    upper_case_letters = len(re.findall('[A-Z]', message_content))
    percent = 0

    if len(message_content) != 0:
        percent =  upper_case_letters / len(message_content)

        if percent > UPPERCASE_MAX:
            
            try:
                await message.delete()
                await user.send(f"{Emotes.no_entry.value} You are not allowed to send that many **CAPS** in your message!")
            except:
                pass
    

async def check_for_discord_invites(bot, guild, user, message):

    
    guild_invites = await guild.invites()

    urls_gg = re.findall("discord.gg\/\S+", message.content)
    urls_com = re.findall("discord.com\/invite\/\S+", message.content)

    urls = []

    for url in urls_gg:
        urls.append(url.split("/", 1)[1])
    
    for url in urls_com:
        urls.append(url.split("/", 1)[1])

    invite_codes = ['bura']
    for invite in guild_invites:
        invite_codes.append(invite.code)
    
    for url in urls:

        if url not in invite_codes:

            try:
                await message.delete() 
            except:
                pass

            await handle_case(
                bot = bot,
                guild = guild, 
                channel = message.channel,
                user = user, 
                moderator = bot.user,
                case_type = 'warn',
                reason = "Posted an invte"
            )
 
            break