import discord
import random
from discord import app_commands
from discord.ext import commands
import os
from dotenv import load_dotenv
import random
import aiohttp
from datetime import datetime

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")

intents = discord.Intents.default()
client = commands.Bot(command_prefix='!', intents=intents)

piadas_tech = {
    "geral": [
        "Por que os programadores preferem o escuro? Porque luz atrapalha o debug.",
        "Na computação, quando algo está aquecido demais, colocamos mais ventoinhas. Na vida, é terapia mesmo.",
        "99 little bugs in the code... take one down, patch it around... 127 bugs in the code.",
    ],
    "frontend": [
        "Quantos desenvolvedores frontend são necessários para trocar uma lâmpada? Nenhum, isso é trabalho do backend.",
        "CSS é como mágica negra: você mexe num lugar e algo quebra do outro lado.",
    ],
    "backend": [
        "O que o banco de dados disse ao desenvolvedor? Pare de me dar consultas ruins, já estou exausto!",
        "Programador backend não sofre com design feio... sofre com código legado.",
    ],
    "segurança": [
        "Criptografia é como mágica: se você entende, não é boa o suficiente.",
        "Usuário: 'Minha senha é 123456' — Hacker: 'Obrigado!'",
    ]
}

@client.event
async def on_ready():
    print(f'Bot conectado como {client.user}')
    try:
        synced = await client.tree.sync()
        print(f'Slash commands sincronizados: {len(synced)} comando(s)')
    except Exception as e:
        print(f'Erro ao sincronizar comandos: {e}')

@client.tree.command(name='ping', description='Responde com Pong!')
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message("Pong!")

@client.tree.command(name="soma", description="Soma dois números")
@app_commands.describe(a="Primeiro número", b="Segundo número")
async def soma(interaction: discord.Interaction, a: int, b: int):
    resultado = a + b
    await interaction.response.send_message(f"O resultado é {resultado}")


@client.tree.command(name="piada", description="Receba uma piada aleatória sobre tecnologia ou programação.")
@app_commands.describe(tema="Escolha um tema (opcional): geral, frontend, backend, segurança")
async def piada(interaction: discord.Interaction, tema: str = "geral"):
    tema = tema.lower()
    if tema not in piadas_tech:
        temas_disponiveis = ", ".join(piadas_tech.keys())
        await interaction.response.send_message(
            f"Tema inválido. Temas disponíveis: {temas_disponiveis}", ephemeral=True)
        return

    piada_escolhida = random.choice(piadas_tech[tema])
    await interaction.response.send_message(f"🧠 {piada_escolhida}")

@client.tree.command(name="status_api", description="Verifica o status da API.")
async def status_api(interaction: discord.Interaction):
    API_URL = ''
    await interaction.response.defer(ephemeral = False)
    try:
        async with aiohttp.ClientSession() as Session:
            async with Session.get(API_URL, timeout = 10) as response:
                if (response.status == 200):
                    data = await response.json()
                    
                    timestamp_original  = data.get('timestamp')
                    timestamp_formatado = timestamp_original

                    if (timestamp_original):
                        try:
                            dt_objeto           = datetime.strptime(timestamp_original, "%m/%d/%y %I:%M:%S %p")
                            timestamp_formatado = dt_objeto.strftime("%d/%m/%y %H:%M:%S")
                        except ValueError:
                            print(f"Não foi possível formatar a data: {timestamp_original}")
                            pass

                    embed = discord.Embed(
                        title = "✅ Status da API: Online",
                        description = data.get('message', 'A API está online e operando corretamente.'),
                        color = discord.Color.green()
                    )
                    embed.add_field(name = "Status Geral", value = f"**{data.get('status', 'online').capitalize()}**", inline = True)
                    embed.add_field(name = "Banco de Dados", value = f"**{data.get('database', 'N/A').capitalize()}**", inline = True)
                    embed.set_footer(text = f"Verificado em: {timestamp_formatado}")
                elif (response.status == 503):
                    data = await response.json()

                    embed = discord.Embed(
                        title = "⚠️ Status da API: Instável",
                        description = "A API está acessível, mas um serviço interno crítico apresenta falhas.",
                        color = discord.Color.orange()
                    )
                    embed.add_field(name="Status Geral", value=f"**{data.get('status', 'unhealthy').capitalize()}**", inline = True)
                    embed.add_field(name="Banco de Dados", value=f"**{data.get('database', 'disconnected').capitalize()}**", inline = True)
                    embed.add_field(name="Detalhe do Erro", value=f"```{data.get('error', 'Não especificado.')}```", inline = False)
                else:
                    embed = discord.Embed(
                        title = "❌ Status da API: Erro",
                        description = "A API respondeu com um erro inesperado.",
                        color = discord.Color.red()
                    )
                    embed.add_field(name="Código de Status", value=f"`{response.status}`", inline = True)
                    embed.add_field(name="Resposta", value=f"```{await response.text()}```", inline = False)
    except (aiohttp.ClientConnectionError):
        embed = discord.Embed(
            title = "❌ Status da API: Offline",
            description = "Não foi possível conectar à API. Verifique se o serviço está no ar ou se a URL está correta.",
            color = discord.Color.dark_red()
        )
    except Exception as E:
        print(f"Erro inesperado ao verificar a API: {E}")
        embed = discord.Embed(
            title = "🚨 Erro no Bot",
            description = "Ocorreu um erro interno no bot ao tentar verificar a API.",
            color = discord.Color.dark_gray()
        )
        embed.add_field(name = "Detalhe", value = f"´´´{E}´´´")
    await interaction.followup.send(embed = embed)

client.run(TOKEN)

