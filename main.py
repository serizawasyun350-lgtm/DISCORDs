import os
import random
import discord
from discord.ext import commands

# Botの初期設定（インテントの有効化）
intents = discord.Intents.default()
intents.message_content = intents.members = True
bot = commands.Bot(command_prefix="!", intents=intents)


@bot.event
async def on_ready():
  print(f"ログインしました: {bot.user.name} (ID: {bot.user.id})")


# --- 98個め: verify_panel ---
@bot.command(name="verify_panel")
@commands.has_permissions(administrator=True)
async def verify_panel(ctx, role: discord.Role):
  """認証パネルを設置するコマンド"""

  class VerifyButton(discord.ui.View):

    def __init__(self):
      super().__init__(timeout=None)

    @discord.ui.button(
        label="認証する",
        style=discord.ButtonStyle.green,
        custom_id="verify_button",
    )
    async def verify(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
      await interaction.user.add_roles(role)
      await interaction.response.send_message(
          f"{role.mention} を付与しました！", ephemeral=True
      )

  embed = discord.Embed(
      title="サーバー認証",
      description="下のボタンを押して認証を完了し、ロールを取得してください。",
      color=discord.Color.green(),
  )
  await ctx.send(embed=embed, view=VerifyButton())


# --- 99個め: ticket_panel ---
@bot.command(name="ticket_panel")
@commands.has_permissions(administrator=True)
async def ticket_panel(ctx):
  """お問い合わせチケットパネルを設置するコマンド"""

  class TicketView(discord.ui.View):

    def __init__(self):
      super().__init__(timeout=None)

    @discord.ui.button(
        label="チケットを作成",
        style=discord.ButtonStyle.blurple,
        custom_id="create_ticket",
    )
    async def create_ticket(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
      guild = interaction.guild
      overwrites = {
          guild.default_role: discord.PermissionOverwrite(read_messages=False),
          interaction.user: discord.PermissionOverwrite(
              read_messages=True, send_messages=True
          ),
      }
      category = discord.utils.get(guild.categories, name="チケット")
      if not category:
        category = await guild.create_category("チケット")

      channel = await guild.create_text_channel(
          f"ticket-{interaction.user.name}",
          category=category,
          overwrites=overwrites,
      )
      await interaction.response.send_message(
          f"チケットを作成しました: {channel.mention}", ephemeral=True
      )

  embed = discord.Embed(
      title="お問い合わせ",
      description=(
          "質問やご用件がある場合は、下のボタンを押して専用チャンネルを作成してください。"
      ),
      color=discord.Color.blue(),
  )
  await ctx.send(embed=embed, view=TicketView())


# --- おまけゲーム機能: 数当てゲーム ---
@bot.command(name="number_game")
async def number_game(ctx):
  """1〜100の数当てゲーム"""
  number = random.randint(1, 100)
  await ctx.send(
      "1から100までの数字を選んだよ！チャットで数字を送信してね（制限時間30秒）。"
  )

  def check(m):
    return (
        m.author == ctx.author
        and m.channel == ctx.channel
        and m.content.isdigit()
    )

  try:
    msg = await bot.wait_for("message", timeout=30.0, check=check)
    guess = int(msg.content)
    if guess == number:
      await ctx.send("正解です！おめでとう！")
    else:
      await ctx.send(f"残念！正解は {number} でした。")
  except TimeoutError:
    await ctx.send(f"時間切れです！正解は {number} でした。")


# その他のコマンド（例としてランダム選択やサイコロなど、残りの97個のイメージ）
@bot.command(name="dice")
async def dice(ctx):
  """サイコロを振る"""
  await ctx.send(f"🎲 出た目: {random.randint(1, 6)}")


# Botの起動
TOKEN = os.getenv("DISCORD_BOT_TOKEN")
bot.run(TOKEN)
