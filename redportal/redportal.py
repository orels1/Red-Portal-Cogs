import discord
from discord.ext import commands
from urllib.parse import quote
import aiohttp


class Redportal:
    """Interact with cogs.red through your bot"""

    def __init__(self, bot):
        self.bot = bot

    @commands.group(pass_context=True, aliases=['redp'])
    async def redportal(self, ctx):
        """Interact with cogs.red through your bot"""

        if ctx.invoked_subcommand is None:
            await self.bot.send_cmd_help(ctx)

    async def _search_redportal(self, ctx, url):
        # future response dict
        data = None

        try:
            async with aiohttp.get(url, headers={"User-Agent": "Sono-Bot"}) as response:
                data = await response.json()

        except:
            return None

        if data is not None and not data['error'] and len(data['results']['list']) > 0:

            # a list of embeds
            embeds = []

            for cog in data['results']['list']:
                embed = discord.Embed(title=cog['name'],
                                      url='https://cogs.red{}'.format(cog['links']['self']),
                                      description= (len(cog['description']) > 175 and '{}...'.format(cog['description'][:175]) or cog['description']) or cog['short'],
                                      color=0xfd0000)
                embed.add_field(name='Type', value=cog['repo']['type'], inline=True)
                embed.add_field(name='Author', value=cog['author']['name'], inline=True)
                embed.add_field(name='Repo', value=cog['repo']['name'], inline=True)
                embed.add_field(name='Command to add repo',
                                value='{}cog repo add {} {}'.format(ctx.prefix, cog['repo']['name'], cog['links']['github']['repo']),
                                inline=False)
                embed.add_field(name='Command to add cog',
                                value='{}cog install {} {}'.format(ctx.prefix, cog['repo']['name'], cog['name']),
                                inline=False)
                embeds.append(embed)

            return embeds

        else:
            return None

    @redportal.command(pass_context=True)
    async def search(self, ctx, *, term: str):
        """Searches for a cog"""

        # base url for the cogs.red search API
        base_url = 'https://cogs.red/api/v1/cogs/search'

        done = False

        # query params
        limit = 1
        offset = 0

        while not done:
            # construct querystring from params
            querystring = 'limit={}&offset={}'.format(limit, offset)

            # final request url
            url = '{}/{}?{}'.format(base_url, quote(term), querystring)

            embeds = await self._search_redportal(ctx, url)

            if embeds is not None:
                # save message for future deletion
                messages = []
                for embed in embeds:
                    messages.append(await self.bot.say(embed=embed))

                messages .append(await self.bot.say('Type `next` to show more results'))

                answer = await self.bot.wait_for_message(timeout=15, author=ctx.message.author)

                if answer is not None and answer.content.strip().lower() == 'next':
                    # pagination step
                    offset += 1

                    # cleanup
                    messages.append(answer)
                    try:
                        await self.bot.delete_messages(messages)
                    except:
                        pass

                else:
                    done = True
            else:
                await self.bot.say('No cogs were found or there was an error in the process')
                done = True


def setup(bot):
    bot.add_cog(Redportal(bot))
