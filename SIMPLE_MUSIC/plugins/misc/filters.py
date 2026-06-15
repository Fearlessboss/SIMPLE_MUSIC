# -----------------------------------------------
# 🔸 SIMPLE MUSIC Project - BYPASS TERMINATOR
# -----------------------------------------------
from SIMPLE_MUSIC import app
from pyrogram import filters

@app.on_message(filters.group, group=1)
async def bye_terminator(client, message):
    if not message.text:
        return

    text = message.text.strip().lower()
    
    # Agar message me "bye", "gn", ya "brb" jaisa kuch bhi ho
    if text == "bye" or text.startswith("bye ") or text.endswith(" bye") or text == "gn" or text == "brb":
        # stop_propagation() lagane se bot ka koi bhi dusra function 
        # (jaise watcher ya afk) is message ko read nahi kar payega.
        message.stop_propagation()
