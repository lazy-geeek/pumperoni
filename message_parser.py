import re
from telethon.tl.patched import Message


def parse_message(message_obj: Message) -> dict:
    text = message_obj.text
    chat_id = (
        message_obj.peer_id.user_id
        if hasattr(message_obj.peer_id, "user_id")
        else message_obj.peer_id.channel_id
    )
    data = {
        "message_id": message_obj.id,
        "chat_id": chat_id,
        "timestamp": message_obj.date.isoformat(),
    }
    if hasattr(message_obj, "reply_to") and message_obj.reply_to:
        data["reply_to_message_id"] = message_obj.reply_to.reply_to_msg_id

    # Token Address
    token_address_match = re.search(r"💊 `(.*)`", text)
    if token_address_match:
        data["token_address"] = token_address_match.group(1).strip()

    # Token Name
    token_name_match = re.search(r"\[\*\*(.*?)\*\*\]", text)
    if token_name_match:
        data["token_name"] = token_name_match.group(1).strip()

    # USD
    usd_match = re.search(r"`USD:\s*`\*\*(\$[0-9,.]+)\*\*", text)
    if usd_match:
        usd_str = usd_match.group(1)
        data["usd"] = float(usd_str.replace("$", "").replace(",", ""))

    # MC (Market Cap)
    mc_match = re.search(r"`MC:\s*`\*\*(\$[0-9,.]+K?)\*\*", text)
    if mc_match:
        mc_str = mc_match.group(1)
        mc_str = mc_str.replace("$", "").replace(",", "")
        if "K" in mc_str:
            data["mc"] = int(float(mc_str.replace("K", "")) * 1000)
        elif "M" in mc_str:
            data["mc"] = int(float(mc_str.replace("M", "")) * 1000000)
        elif "B" in mc_str:
            data["mc"] = int(float(mc_str.replace("B", "")) * 1000000000)
        else:
            data["mc"] = int(float(mc_str))

    # VOL (Volume)
    vol_match = re.search(r"`Vol:\s*`\*\*(\$[0-9,.]+K?)\*\*", text)
    if vol_match:
        vol_str = vol_match.group(1)
        vol_str = vol_str.replace("$", "").replace(",", "")
        if "K" in vol_str:
            data["vol"] = int(float(vol_str.replace("K", "")) * 1000)
        elif "M" in vol_str:
            data["vol"] = int(float(vol_str.replace("M", "")) * 1000000)
        elif "B" in vol_str:
            data["vol"] = int(float(vol_str.replace("B", "")) * 1000000000)
        else:
            data["vol"] = int(float(vol_str))

    # Dex Exchange
    dex_match = re.search(r"`Dex:\s*`\*\*([^*]+)\*\*", text)
    if dex_match:
        data["dex"] = dex_match.group(1).strip()

    # Dex Paid Status
    dex_paid_match = re.search(r"`Dex Paid:\s*`\*\*([🔴🟢])\*\*", text)
    if dex_paid_match:
        data["dex_paid"] = dex_paid_match.group(1) == "🟢"

    # Holder Top 10
    holder_match = re.search(r"`Holder:\s*`Top 10:\s*\*\*[🟡🔴🟢]?\s*(\d+)%\*\*", text)
    if holder_match:
        data["top10_holder"] = int(holder_match.group(1))

    # Extract x value from messages like "💹 **8.6x** 288.3K to 2.5M"
    x_match = re.search(r"\*\*([0-9.]+)x\*\*", text)
    if x_match:
        data["x"] = float(x_match.group(1))
    else:
        data["x"] = -1  # Default value if x is not found

    # Validate either main signal or reply with growth data
    is_main_signal = data.get("token_address") is not None
    is_valid_reply = (
        data.get("reply_to_message_id") is not None and data.get("x", -1) != -1
    )

    if is_main_signal or is_valid_reply:
        return data
    else:
        return None
