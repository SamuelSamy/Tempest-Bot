import re

from domain.enums.moderation import BannedWord, ModFormat
from domain.enums.general import Emotes
from repository.json_repo import ModerationRepo
from service._general.utils import get_urls
from service.moderation.commands_functions import handle_case


DISCORD_URLS =  ['discord.com', 'discord.gg', 'discord.gift', 'dis.gd']
UPPERCASE_MAX = 70  # %


async def check_for_banned_words(bot, guild, member, message):
    
    member = guild.get_member(member.id)

    moderation_repo = ModerationRepo()
    banned_words_entries = moderation_repo.get_banned_words(guild.id)

    punishments = []

    for entry in banned_words_entries.values():
        word = entry[BannedWord.word]

        if word in message.content.lower():
            punishments.append(entry)

    if len(punishments) != 0:

        await message.delete()

        punishments.sort(key = lambda punishment: punishment[BannedWord.flags][BannedWord.flag_type])
        
        highest_punishments = [punishments[0]]
        highest_punishment = punishments[0]

        index = 1
        while index < len(punishments) \
            and highest_punishment[BannedWord.flags][BannedWord.flag_type] == punishments[index][BannedWord.flags][BannedWord.flag_type]:
            highest_punishments.append(punishments[index])
            index += 1

        highest_punishments.sort(
            key = lambda punishment: punishment[BannedWord.flags][BannedWord.flag_duration], 
            reverse = highest_punishment[BannedWord.flags][BannedWord.flag_type] == 'mute'
        )
        
        punishment_to_apply = highest_punishments[0]
        notify_channel = None

        if punishment_to_apply[BannedWord.flags][BannedWord.flag_notify_channel] != 0:
            notify_channel = bot.get_channel(punishment_to_apply[BannedWord.flags][BannedWord.flag_notify_channel])


        await handle_case(
            bot = bot,
            guild = guild, 
            channel = notify_channel,
            moderator = bot.user,
            user = member,
            case_type = punishment_to_apply[BannedWord.flags][BannedWord.flag_type],
            reason = f"Usage of banned word **({punishment_to_apply[BannedWord.word]})**",
            duration = punishment_to_apply[BannedWord.flags][BannedWord.flag_duration],
            message = message.content
        )



def link_protected(guild, user, channel):
        
    member = guild.get_member(user.id)
    channel_id = channel.id 

    moderation_repo = ModerationRepo()

    if channel_id in moderation_repo.get_link_protected_channels(guild.id):
        return True

    for role in member.roles:
        if role.id in moderation_repo.get_link_protected_roles(guild.id):
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
                    await user.send(f"{Emotes.no_entry} You can not post links from that website!")
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
                await user.send(f"{Emotes.no_entry} You are not allowed to send that many **CAPS** in your message!")
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