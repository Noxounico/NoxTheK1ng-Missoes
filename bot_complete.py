# Na seção de GLOBAL VARIABLES, add isso:
loop_task = None

# Substitui o comando /orbs start:
@bot.tree.command(name="orbs")
@app_commands.describe(
    action="Ação: status, start, stop, clear"
)
async def orbs_command(interaction: discord.Interaction, action: str = "status"):
    """Controla automation de Orbs."""
    global loop_task
    
    if action == "status":
        with open("orbs_progress.json") as f:
            prog = json.load(f)
        embed = discord.Embed(
            title="🎁 Orbs Quest Status",
            color=discord.Color.blurple()
        )
        embed.add_field(name="✅ Completadas", value=str(prog.get("completed", 0)), inline=True)
        embed.add_field(name="❌ Falhadas", value=str(prog.get("failed", 0)), inline=True)
        embed.add_field(name="🎥 Vídeos", value=str(prog.get("videos", 0)), inline=True)
        embed.add_field(name="🎮 Games", value=str(prog.get("games", 0)), inline=True)
        embed.add_field(name="📊 Total", value=str(prog.get("total", 0)), inline=True)
        embed.add_field(name="⏰ Última sync", value=prog.get("last_sync", "Nunca"), inline=True)
        await interaction.response.send_message(embed=embed, ephemeral=True)

    elif action == "start":
        # CHECA se loop_task existe E está rodando
        if loop_task is not None and not loop_task.done():
            await interaction.response.send_message(
                "⚠️ Automação já está rodando! Use `/orbs stop` pra parar.",
                ephemeral=True
            )
            return

        # Se task existe MAS está morta, mata ela:
        if loop_task is not None and loop_task.done():
            try:
                loop_task.cancel()
            except:
                pass

        # Cria NOVA task fresca
        loop_task = bot.loop.create_task(orbs_loop(interaction.user.id))
        logger.info(f"✅ Orbs automation iniciada por {interaction.user}")
        await interaction.response.send_message(
            "✅ Automação iniciada! Processando quests...",
            ephemeral=True
        )

    elif action == "stop":
        if loop_task is None or loop_task.done():
            await interaction.response.send_message(
                "⚠️ Automação não está rodando.",
                ephemeral=True
            )
            return

        loop_task.cancel()
        try:
            await loop_task
        except asyncio.CancelledError:
            pass
        
        logger.info(f"⛔ Orbs automation parada por {interaction.user}")
        await interaction.response.send_message(
            "⛔ Automação parada.",
            ephemeral=True
        )

    elif action == "clear":
        data = {
            "completed": 0,
            "failed": 0,
            "videos": 0,
            "games": 0,
            "total": 0,
            "last_sync": "Resetada"
        }
        with open("orbs_progress.json", "w") as f:
            json.dump(data, f, indent=2)
        await interaction.response.send_message(
            "🗑️ Progress resetado.",
            ephemeral=True
        )
