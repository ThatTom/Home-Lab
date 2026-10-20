# Managed in the Home-Lab repo (ansible/roles/tplink_easy_smart).
# The Easy Smart switches have no API: each web page carries its data as JavaScript variables,
# e.g. var info_ds = {descriStr:["floo"], ...}; or var logonInfo = new Array(0, 0);
# tplink_vars turns those into a dict of plain values.

import json
import re

_VARIABLE = re.compile(r"var\s+([A-Za-z0-9_]+)\s*=\s*(.+?);\s*(?=var\s|$|//|\n)", re.DOTALL)
_NEW_ARRAY = re.compile(r"^new\s+Array\s*\((.*)\)$", re.DOTALL)
_BARE_KEY = re.compile(r"([{,]\s*)([A-Za-z_][A-Za-z0-9_]*)\s*:")
_TRAILING_COMMA = re.compile(r",\s*([}\]])")


def _scalar(text):
    text = text.strip().strip("\"'")
    try:
        return int(text)
    except ValueError:
        return text


def _value(text):
    text = text.strip()
    array = _NEW_ARRAY.match(text)
    if array:
        items = array.group(1).strip()
        return [_scalar(i) for i in items.split(",")] if items else []
    if text[:1] in "{[":
        as_json = _BARE_KEY.sub(r'\1"\2":', text.replace("'", '"'))
        as_json = _TRAILING_COMMA.sub(r"\1", as_json)
        try:
            return json.loads(as_json)
        except ValueError:
            return text
    return _scalar(text)


def tplink_vars(page):
    """Every `var name = value;` in the page's scripts, parsed."""
    scripts = re.findall(r"<script[^>]*>(.*?)</script>", page or "", re.DOTALL | re.IGNORECASE)
    result = {}
    for script in scripts:
        for name, value in _VARIABLE.findall(script):
            result[name] = _value(value)
    return result


SPEEDS = {0: "down", 1: "auto", 2: "10h", 3: "10f", 4: "100h", 5: "100f", 6: "1000f", 7: "unknown"}


def tplink_port(number, all_info):
    """One port's settings and link state from PortSettingRpm.htm's all_info, by port number (from 1)."""
    i = int(number) - 1
    return {
        "port": int(number),
        "enabled": all_info["state"][i] == 1,
        "speed": SPEEDS.get(all_info["spd_cfg"][i], all_info["spd_cfg"][i]),
        "link": SPEEDS.get(all_info["spd_act"][i], all_info["spd_act"][i]),
        "flow_control": all_info["fc_cfg"][i] == 1,
    }


def tplink_port_changes(desired, state, uplink):
    """Ports from desired (tplink_ports) whose settings differ from state (tplink_port_state).

    Fields left out of a desired entry keep their current value. Raises an error rather than ever
    disabling or slowing down the uplink port, since that would cut the switch off.
    """
    changes = []
    for want in desired or []:
        number = int(want["port"])
        if not 1 <= number <= len(state):
            raise ValueError("Port %s doesn't exist, this switch has %d ports" % (number, len(state)))
        have = state[number - 1]
        new = {
            "port": number,
            "enabled": bool(want.get("enabled", have["enabled"])),
            "speed": str(want.get("speed", have["speed"])),
            "flow_control": bool(want.get("flow_control", have["flow_control"])),
        }
        if new["speed"] not in SPEEDS.values() or new["speed"] in ("down", "unknown"):
            raise ValueError("Port %d: speed %s isn't one of auto, 10h, 10f, 100h, 100f, 1000f" % (number, new["speed"]))
        if number == int(uplink) and (not new["enabled"] or new["speed"] not in ("auto", "1000f")):
            raise ValueError("Port %d is the uplink to the router, disabling or slowing it would cut the switch off. "
                             "Change it in the web UI if that's really intended." % number)
        if any(new[f] != have[f] for f in ("enabled", "speed", "flow_control")):
            changes.append(new)
    return changes


class FilterModule(object):
    def filters(self):
        return {"tplink_vars": tplink_vars, "tplink_port": tplink_port, "tplink_port_changes": tplink_port_changes}
