# Managed in the Home-Lab repo (ansible/roles/routeros).


def _static(entries):
    return [e for e in entries or [] if str(e.get("dynamic", "false")).lower() not in ("true", "yes")]


def routeros_inventory(menus):
    """Turn the menus read by read.yml into the inventory variables apply.yml expects.

    menus is the registered result of the "Read each managed menu" loop: each item has the
    section definition in .item and the router's entries in .json. Dynamic entries are dropped,
    and only the section's listed fields with a value are kept.
    """
    out = {}
    for menu in menus:
        section = menu["item"]
        entries = []
        for entry in _static(menu.get("json")):
            entries.append({f: entry[f] for f in section["fields"] if entry.get(f) not in (None, "")})
        out[section["var"]] = entries
    return out


def routeros_uncommented(entries):
    """Static entries without a comment, which a comment-keyed menu can't match up."""
    return [e for e in _static(entries) if not e.get("comment")]


class FilterModule(object):
    def filters(self):
        return {"routeros_inventory": routeros_inventory, "routeros_uncommented": routeros_uncommented}
