import re


def parse_message(text):
    data = {}

    # Token Address
    token_address_match = re.search(r"💊 `(.*)`", text)
    if token_address_match:
        data["token_address"] = token_address_match.group(1).strip()

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

    # Holder Top 10
    holder_match = re.search(r"`Holder:\s*`Top 10:\s*\*\*[🟡🔴🟢]?\s*(\d+)%\*\*", text)
    if holder_match:
        data["top10_holder"] = int(holder_match.group(1))

    # Extract x value from messages like "💹 **8.6x** 288.3K to 2.5M"
    x_match = re.search(r"\*\*([0-9.]+)x\*\*", text)
    if x_match:
        data["x"] = float(x_match.group(1))

    return data
