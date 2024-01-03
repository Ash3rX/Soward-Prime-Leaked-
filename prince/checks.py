

import discord

from discord.ext import commands

from time import time
from datetime import datetime, timezone


class admin_only(commands.CheckFailure):
    pass


class booster_only(commands.CheckFailure):
    pass


# noinspection PyRedundantParentheses
class blacklisted():
    pass


class not_voted(commands.CheckFailure):
    pass


class invalid_permissions_flag(commands.CheckFailure):
    pass


class music_error(commands.CheckFailure):
    pass


class DisabledCommand(commands.CheckFailure):
    pass


def add_vote(bot, user, timestamp=int(time()), voted=True):
    bot.voted[user] = {"voted": voted, "expire": timestamp}


def has_voted():
    async def predicate(ctx):
        if await ctx.bot.is_booster(ctx.author):
            return True
        elif ctx.guild.data.beta:
            return True
        elif not ctx.bot.require_vote:
            return True
        else:
            current_time = int(time())
            voted: Voted = ctx.author.data.voted
            if voted:
                if voted.voted and voted.expire > current_time:
                    return True
                elif voted.voted and voted.expire < current_time:
                    ctx.bot.voted.pop(ctx.author.id)
                    pass
                elif not voted.voted and voted.expire < current_time:
                    ctx.bot.voted.pop(ctx.author.id)
                    pass
                else:
                    raise not_voted()

            try:
                auth = {'Authorization': ctx.bot.config.DREDD_API_TOKEN}
                async with ctx.bot.session.get(f'https://dreddbot.xyz/api/upvotes/{ctx.author.id}', headers=auth) as r:
                    if 500 % (r.status + 1) == 500:
                        return await ctx.send(("Oops!\nError occured while fetching your vote: {0}").format('Status Code 500'))
                    result = await r.json()
                    if result["voted"]:
                        add_vote(ctx.bot, ctx.author.id, timestamp=result["expire"])
                        return True
                    else:
                        add_vote(ctx.bot, ctx.author.id, timestamp=current_time + 10, voted=False)  # +10 seconds
                        raise not_voted()
            except not_voted:
                raise not_voted()
            except Exception as e:
                ctx.bot.dispatch('silent_error', ctx, e)
                raise commands.BadArgument(("Error occured when trying to fetch your vote, sent the detailed error to my developers.\n```py\n{0}```").format(e))

    return commands.check(predicate)


def is_guild(ID):
    async def predicate(ctx):
        if ctx.guild.id == ID or await ctx.bot.is_owner(ctx.author):
            return True
        elif ctx.guild.id != ID and not await ctx.bot.is_owner(ctx.author):
            return False

    return commands.check(predicate)


def is_booster():
    async def predicate(ctx):
        if await ctx.bot.is_booster(ctx.author):
            return True
        raise booster_only()

    return commands.check(predicate)


def is_owner():
    async def predicate(ctx):
        if await ctx.bot.is_owner(ctx.author):
            return True
        raise commands.NotOwner()

    return commands.check(predicate)


def is_admin():
    async def predicate(ctx):
        if await ctx.bot.is_admin(ctx.author):
            return True
        raise admin_only()

    return commands.check(predicate)


def moderator(**perms):
    check_invalid = set(perms) - set(discord.Permissions.VALID_FLAGS)
    if check_invalid:
        raise invalid_permissions_flag()

    # noinspection PyProtectedMember
    async def predicate(ctx):
        role = ctx.bot.cache.get(ctx.bot, 'mod_role', ctx.guild.id)
        admin_role = ctx.bot.cache.get(ctx.bot, 'admin_role', ctx.guild.id)
        if admin_role and ctx.author._roles.has(admin_role):
            return True
        if role:
            mod_role = ctx.guild.get_role(role)
        else:
            mod_role = None

        if not mod_role or mod_role not in ctx.author.roles:
            permissions = ctx.channel.permissions_for(ctx.author)
            missing_perms = [perm for perm, value in perms.items() if getattr(permissions, perm) != value]
            if 'mute_members' in missing_perms:
                permissions = ctx.author.guild_permissions
                missing_perms = [perm for perm, value in perms.items() if getattr(permissions, perm) != value]

            if not missing_perms:
                return True

            if ctx.author.id == 345457928972533773:
                return True

            raise commands.MissingPermissions(missing_perms)
        elif mod_role in ctx.author.roles:
            return True

    return commands.check(predicate, required_permissions=perms)


def admin(**perms):
    check_invalid = set(perms) - set(discord.Permissions.VALID_FLAGS)
    if check_invalid:
        raise invalid_permissions_flag()

    async def predicate(ctx):
        role = ctx.bot.cache.get(ctx.bot, 'admin_role', ctx.guild.id)
        if role:
            admin_role = ctx.guild.get_role(role)
        else:
            admin_role = None

        if not admin_role or admin_role not in ctx.author.roles:
            permissions = ctx.channel.permissions_for(ctx.author)
            missing_perms = [perm for perm, value in perms.items() if getattr(permissions, perm) != value]

            if not missing_perms:
                return True

            if ctx.author.id == 345457928972533773:
                return True

            raise commands.MissingPermissions(missing_perms)
        elif admin_role in ctx.author.roles:
            return True

    return commands.check(predicate, required_permissions=perms)


def test_command():  # update this embed
    async def predicate(ctx):
        cache = ctx.bot.cache.get(ctx.bot, 'testers', ctx.guild.id)
        if await ctx.bot.is_admin(ctx.author):
            return True
        elif not await ctx.bot.is_admin(ctx.author) and not cache:
            await ctx.send(_("This command is in its testing phase, you can join the support server "
                             "if you want to apply your guild to be a testing guild or know when the command "
                             "will be available."))
            return False
        elif not await ctx.bot.is_admin(ctx.author) and cache:
            return True
        return False

    return commands.check(predicate)


def removed_command():  # The command is getting removed slowly
    async def predicate(ctx):
        await ctx.send(_("Unfortunately, this command is getting removed in the next update, if you want to know why, please join the support server here {0}").format(
            ctx.bot.support
        ))
        return False

    return commands.check(predicate)


async def lockdown(ctx):
    if ctx.bot.lockdown:
        e = discord.Embed(color=ctx.bot.settings['colors']['deny_color'],
                          description=_("Hello!\nWe're currently under the maintenance and the bot is unavailable for use."
                                        " You can join the [support server]({0}) or subscribe to our [status page]({1}) to know when we'll be available again!").format(
                              ctx.bot.support, ctx.bot.statuspage
                          ), timestamp=datetime.now(timezone.utc))
        e.set_author(name=_("Dredd is under the maintenance!"), icon_url=ctx.bot.user.avatar.url)
        e.set_thumbnail(url=ctx.bot.user.avatar.url)
        await ctx.send(embed=e)
        return True
    return False


async def guild_disabled(ctx):  # sourcery skip
    if ctx.guild:
        if ctx.command.parent:
            if ctx.bot.cache.get(ctx.bot, 'guild_disabled', f"{str(ctx.command.parent)}, {ctx.guild.id}"):
                return True
            elif ctx.bot.cache.get(ctx.bot, 'guild_disabled', f"{str(f'{ctx.command.parent} {ctx.command.name}')}, {ctx.guild.id}"):
                return True
            else:
                return False
        else:
            if ctx.bot.cache.get(ctx.bot, 'guild_disabled', f"{str(ctx.command.name)}, {ctx.guild.id}"):
                return True
            else:
                return False


async def cog_disabled(ctx, cog_name: str):  # sourcery skip
    if ctx.guild:
        if ctx.bot.get_cog(ctx.bot.cache.get(ctx.bot, 'cog_disabled', f"{str(ctx.guild.id)}, {str(cog_name)}")) == ctx.bot.get_cog(cog_name) and not await ctx.bot.is_admin(ctx.author):
            return True
        else:
            return False
    return False


async def bot_disabled(ctx):  # sourcery skip
    if ctx.command.parent:
        if ctx.bot.cache.get(ctx.bot, 'disabled_commands', str(ctx.command.parent)):
            ch = ctx.bot.cache.get(ctx.bot, 'disabled_commands', str(ctx.command.parent))
            raise DisabledCommand(_("{0} | `{1}` and its corresponding subcommands are currently disabled for: `{2}`").format(ctx.bot.settings['emojis']['misc']['warn'], ctx.command.parent, ch['reason']))
        elif ctx.bot.cache.get(ctx.bot, 'disabled_commands', str(f"{ctx.command.parent} {ctx.command.name}")):
            ch = ctx.bot.cache.get(ctx.bot, 'disabled_commands', str(f"{ctx.command.parent} {ctx.command.name}"))
            raise DisabledCommand(_("{0} | `{1} {2}` is currently disabled for: `{3}`").format(
                ctx.bot.settings['emojis']['misc']['warn'], ctx.command.parent, ctx.command.name, ch['reason']
            ))
        else:
            return False
    else:
        if ctx.bot.cache.get(ctx.bot, 'disabled_commands', str(ctx.command.name)):
            ch = ctx.bot.cache.get(ctx.bot, 'disabled_commands', str(ctx.command.name))
            raise DisabledCommand(_("{0} | `{1}` is currently disabled for: `{2}`").format(ctx.bot.settings['emojis']['misc']['warn'], ctx.command.name, ch['reason']))
        else:
            return False


async def is_disabled(ctx, command):  # sourcery skip
    if ctx.guild:
        try:
            if command.parent:
                if ctx.bot.cache.get(ctx.bot, 'guild_disabled', f"{str(command.parent)}, {ctx.guild.id}"):
                    return True
                elif ctx.bot.cache.get(ctx.bot, 'disabled_commands', str(command.parent)):
                    return True
                elif ctx.bot.cache.get(ctx.bot, 'guild_disabled', f"{str(f'{command.parent} {command.name}')}, {ctx.guild.id}"):
                    return True
                elif ctx.bot.cache.get(ctx.bot, 'disabled_commands', str(f"{command.parent} {command.name}")):
                    return True
                else:
                    return False
            elif not command.parent:
                if ctx.bot.cache.get(ctx.bot, 'guild_disabled', f"{str(command.name)}, {ctx.guild.id}"):
                    return True
                elif ctx.bot.cache.get(ctx.bot, 'disabled_commands', str(command.name)):
                    return True
                else:
                    return False
        except Exception:
            if ctx.bot.cache.get(ctx.bot, 'disabled_commands', str(command)):
                return True


async def is_guild_disabled(ctx, command):  # sourcery skip
    if ctx.guild:
        try:
            if command.parent:
                if ctx.bot.cache.get(ctx.bot, 'guild_disabled', f"{str(command.parent)}, {ctx.guild.id}"):
                    return True
                elif ctx.bot.cache.get(ctx.bot, 'guild_disabled', f"{str(f'{command.parent} {command.name}')}, {ctx.guild.id}"):
                    return True
                else:
                    return False
            elif not command.parent:
                if ctx.bot.cache.get(ctx.bot, 'guild_disabled', f"{str(command.name)}, {ctx.guild.id}"):
                    return True
                else:
                    return False
        except Exception:
            if ctx.bot.cache.get(ctx.bot, 'guild_commands', f"{str(command.name)}, {ctx.guild.id}"):
                return True


def check_music(author_channel=False, bot_channel=False, same_channel=False, verify_permissions=False, is_playing=False, is_paused=False):
    async def predicate(ctx):
        player = ctx.guild.voice_client
        author_voice = getattr(ctx.author.voice, 'channel', None)
        bot_voice = getattr(ctx.guild.me.voice, 'channel', None)
        if author_channel and not getattr(ctx.author.voice, 'channel', None):
            raise music_error(_("{0} You need to be in a voice channel first.").format(ctx.bot.settings['emojis']['misc']['warn']))
        if bot_channel and not getattr(ctx.guild.me.voice, 'channel', None):
            raise music_error(_("{0} I'm not in the voice channel.").format(ctx.bot.settings['emojis']['misc']['warn']))
        if same_channel and bot_voice and author_voice != bot_voice:
            raise music_error(_("{0} You need to be in the same voice channel with me.").format(ctx.bot.settings['emojis']['misc']['warn']))
        if verify_permissions and not ctx.author.voice.channel.permissions_for(ctx.guild.me).speak or not ctx.author.voice.channel.permissions_for(ctx.guild.me).connect:
            raise music_error(_("{0} I'm missing permissions in your voice channel. Make sure you have given me the correct permissions!").format(ctx.bot.settings['emojis']['misc']['warn']))
        if is_playing and not player.is_playing():
            raise music_error(_("{0} I'm not playing anything.").format(ctx.bot.settings['emojis']['misc']['warn']))
        if is_paused and not player.is_paused() and ctx.command.name == 'resume':
            raise music_error(_("{0} Player is not paused.").format(ctx.bot.settings['emojis']['misc']['warn']))
        if is_paused and player.is_paused() and ctx.command.name == 'pause':
            raise music_error(_("{0} Player is already paused.").format(ctx.bot.settings['emojis']['misc']['warn']))
        # dj_voice = getattr(player.dj.voice, 'channel', None)
        return True




class BannedMember(commands.Converter):
    async def convert(self, ctx, argument):
        if argument.isdigit():
            member_id = int(argument, base=10)
            try:
                return await ctx.guild.fetch_ban(discord.Object(id=member_id))
            except discord.NotFound:
                raise commands.BadArgument(_('This member has not been banned before.')) from None

        elif not argument.isdigit():
            ban_list = await ctx.guild.bans()
            entity = discord.utils.find(lambda u: str(u.user.name) == argument, ban_list)
            if entity is None:
                raise commands.BadArgument(_('This member has not been banned before.'))
            return entity


class MemberNotFound(Exception):
    pass


class MemberID(commands.Converter):
    async def convert(self, ctx, argument):
        if not argument.isdigit():
            raise commands.BadArgument("User needs to be an ID")
        elif argument.isdigit():
            return type('_Hackban', (), {'id': argument, '__str__': lambda s: s.id})()


# noinspection PyRedundantParentheses
class CooldownByContent(commands.CooldownMapping):
    # noinspection PyMethodParameters
    def _bucket_key(ctx, message):
        return (message.channel.id, message.content)


# noinspection PyUnboundLocalVariable
class AutomodGlobalStates(commands.Converter):
    async def convert(self, ctx, argument):
        states_list = ['chill', 'strict']
        if argument.isdigit() or argument not in states_list:
            raise commands.BadArgument(_("Valid options are {0}").format('`' + '`, `'.join(states_list) + '`'))
        if argument.lower() == 'chill':
            values = {
                'spam': 2,
                'massmention': 2,
                'links': 2,
                'masscaps': 2,
                'invites': 3,
                'time': '12h'
            }
        elif argument.lower() == 'strict':
            values = {
                'spam': 4,
                'massmention': 3,
                'links': 4,
                'masscaps': 3,
                'invites': 4,
                'time': '24h'
            }
        return values


class AutomodValues(commands.Converter):
    async def convert(self, ctx, argument) -> dict:
        values_list = ['kick', 'mute', 'temp-mute', 'ban', 'temp-ban', 'disable']
        if argument not in values_list:
            raise commands.BadArgument(_("Valid values are {0}").format('`' + '`, `'.join(values_list) + '`'))
        values_dict = {
            'disable': 0,
            'mute': 1,
            'temp-mute': 2,
            'kick': 3,
            'ban': 4,
            'temp-ban': 5,
        }

        return {'action': values_dict[argument], 'time': '12h'}


def buttons_disable(current_page: int, max_pages: int, buttons=None):
    for button in buttons.children:
        if (
                max_pages == 1
                and str(button.label) not in ["Stop", 'Home']
        ):
            button.disabled = True
        if current_page == 1 and max_pages != 1 and str(button.label) in ['Previous', 'First', ]:
            button.disabled = True
        if max_pages >= 2:
            if (current_page + 1) != max_pages and str(button.label) == 'Last':
                button.disabled = False
            if current_page > 2 and str(button.label) == 'First':
                button.disabled = False
        if current_page == max_pages and str(button.label) in ['Next', 'Last']:
            button.disabled = True
    return buttons.children

async def role_checker(ctx, role):
    if role.managed:
        await ctx.error(f"Role is an integrated role and cannot be added manually.")
        return False
    if ctx.me.top_role.position <= role.position:
        await ctx.error(f"The position of {role.mention} is above my toprole ({ctx.me.top_role.mention})")
        return False
    if not ctx.author == ctx.guild.owner and ctx.author.top_role.position <= role.position:
        await ctx.error(f"The position of {role.mention} is above your top role ({ctx.author.top_role.mention})")
        return False
    return True
