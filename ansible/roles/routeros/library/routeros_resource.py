#!/usr/bin/python
# Managed in the Home-Lab repo (ansible/roles/routeros).

DOCUMENTATION = r"""
module: routeros_resource
short_description: Make one RouterOS v7 menu match a list of entries, over the REST API
description:
  - Reads the menu at I(path), matches existing entries to I(entries) by the I(key) fields,
    then adds missing entries, updates fields that differ and, with I(purge), removes entries
    that aren't listed. Dynamic entries are never touched.
  - Only the fields given in an entry are compared, any other fields on the router are left alone.
  - Supports check mode and diff mode.
options:
  url: {type: str, required: true, description: Base URL of the router, e.g. https://10.10.10.1}
  username: {type: str, required: true}
  password: {type: str, required: true, no_log: true}
  validate_certs: {type: bool, default: true}
  timeout: {type: int, default: 30}
  path: {type: str, required: true, description: Menu path as in the REST URL, e.g. ip/dhcp-server/lease}
  key: {type: list, elements: str, required: true, description: Fields that identify an entry}
  entries: {type: list, elements: dict, required: true}
  purge: {type: bool, default: false, description: Remove non-dynamic entries that aren't in entries}
  ordered: {type: bool, default: false, description: Keep the listed entries in the order given (firewall rules)}
"""

import json

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.urls import open_url
from ansible.module_utils.six.moves.urllib.error import HTTPError

TRUE_VALUES = ("true", "yes")
FALSE_VALUES = ("false", "no")


def normalise(value):
    """RouterOS returns every value as a string, so compare everything as strings."""
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (list, tuple)):
        return ",".join(sorted(normalise(v) for v in value))
    text = "" if value is None else str(value).strip()
    if text.lower() in TRUE_VALUES:
        return "true"
    if text.lower() in FALSE_VALUES:
        return "false"
    return text


def compare_form(field, value):
    """MAC addresses are compared ignoring case, RouterOS shows them in upper case."""
    text = normalise(value)
    return text.lower() if "mac" in field else text


def same(desired, existing, field=""):
    """A desired list matches a comma separated value in any order, e.g. tagged ports."""
    if isinstance(desired, (list, tuple)):
        existing = sorted(p for p in str(existing or "").split(",") if p)
    return compare_form(field, desired) == compare_form(field, existing)


def to_router(value):
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (list, tuple)):
        return ",".join(str(v) for v in value)
    return str(value)


def entry_key(entry, key):
    return tuple(compare_form(field, entry.get(field)) for field in key)


def plan(current, desired, key, purge=False, ordered=False):
    """Work out what has to change. Pure, so it can be tested without a router.

    Returns a dict of create (entries to add), update (id, fields to set, before),
    delete (existing entries) and order (desired keys in the order they should end up).
    """
    static = [e for e in current if normalise(e.get("dynamic")) != "true"]
    by_key = {}
    for e in static:
        by_key.setdefault(entry_key(e, key), e)

    seen = set()
    create, update = [], []
    for want in desired:
        k = entry_key(want, key)
        if k in seen:
            raise ValueError("Duplicate entry for key %s: %s" % (", ".join(key), k))
        seen.add(k)
        have = by_key.get(k)
        if have is None:
            create.append(want)
            continue
        changes = {f: v for f, v in want.items() if not same(v, have.get(f), f)}
        if changes:
            update.append({"id": have[".id"], "set": changes, "before": {f: have.get(f) for f in changes}})

    delete = [e for e in static if entry_key(e, key) not in seen] if purge else []
    return {"create": create, "update": update, "delete": delete,
            "order": [entry_key(w, key) for w in desired] if ordered else []}


def moves_needed(current, order, key):
    """Moves (id, destination id) that put the ordered keys in sequence, walking back from the end."""
    positions = [entry_key(e, key) for e in current if normalise(e.get("dynamic")) != "true"]
    ids = {entry_key(e, key): e[".id"] for e in current if normalise(e.get("dynamic")) != "true"}
    moves = []
    for i in range(len(order) - 2, -1, -1):
        this, after = order[i], order[i + 1]
        if positions.index(this) > positions.index(after):
            moves.append((ids[this], ids[after]))
            positions.remove(this)
            positions.insert(positions.index(after), this)
    return moves


class RouterOS(object):
    def __init__(self, module):
        p = module.params
        self.module = module
        self.base = p["url"].rstrip("/") + "/rest/"
        self.auth = dict(url_username=p["username"], url_password=p["password"], force_basic_auth=True,
                         validate_certs=p["validate_certs"], timeout=p["timeout"])

    def call(self, method, path, body=None):
        data = json.dumps(body) if body is not None else None
        try:
            response = open_url(self.base + path, method=method, data=data,
                                headers={"Content-Type": "application/json"}, **self.auth)
            text = response.read()
            return json.loads(text) if text else None
        except HTTPError as e:
            detail = e.read().decode("utf-8", "replace") if hasattr(e, "read") else ""
            self.module.fail_json(msg="%s %s failed: HTTP %s %s" % (method, path, e.code, detail))
        except Exception as e:  # connection refused, TLS, timeout
            self.module.fail_json(msg="%s %s failed: %s" % (method, path, e))


def main():
    module = AnsibleModule(
        argument_spec=dict(
            url=dict(type="str", required=True),
            username=dict(type="str", required=True),
            password=dict(type="str", required=True, no_log=True),
            validate_certs=dict(type="bool", default=True),
            timeout=dict(type="int", default=30),
            path=dict(type="str", required=True),
            key=dict(type="list", elements="str", required=True),
            entries=dict(type="list", elements="dict", required=True),
            purge=dict(type="bool", default=False),
            ordered=dict(type="bool", default=False),
        ),
        supports_check_mode=True,
    )
    p = module.params
    path = p["path"].strip("/")
    api = RouterOS(module)

    for want in p["entries"]:
        missing = [f for f in p["key"] if f not in want]
        if missing:
            module.fail_json(msg="An entry in %s has no %s: %s" % (path, ", ".join(missing), want))

    current = api.call("GET", path) or []
    try:
        changes = plan(current, p["entries"], p["key"], p["purge"], p["ordered"])
    except ValueError as e:
        module.fail_json(msg="%s: %s" % (path, e))

    result = dict(
        changed=False, path=path,
        created=[c for c in changes["create"]],
        updated=[{"key": u["before"], "set": u["set"]} for u in changes["update"]],
        deleted=[{f: d.get(f) for f in p["key"]} for d in changes["delete"]],
        moved=[],
    )
    result["changed"] = bool(changes["create"] or changes["update"] or changes["delete"])

    if not module.check_mode:
        for want in changes["create"]:
            api.call("PUT", path, {f: to_router(v) for f, v in want.items()})
        for u in changes["update"]:
            api.call("PATCH", "%s/%s" % (path, u["id"]), {f: to_router(v) for f, v in u["set"].items()})
        for d in changes["delete"]:
            api.call("DELETE", "%s/%s" % (path, d[".id"]))

    if changes["order"]:
        after = current if module.check_mode else (api.call("GET", path) or [])
        if not module.check_mode or not (changes["create"] or changes["delete"]):
            moves = moves_needed(after, changes["order"], p["key"])
            result["moved"] = [m[0] for m in moves]
            if moves:
                result["changed"] = True
            if not module.check_mode:
                for entry_id, destination in moves:
                    api.call("POST", "%s/move" % path, {"numbers": entry_id, "destination": destination})

    if module._diff and result["changed"]:
        result["diff"] = dict(
            before="".join("%s %s\n" % (path, json.dumps(u["before"])) for u in changes["update"])
                   + "".join("%s %s\n" % (path, json.dumps({f: d.get(f) for f in p["key"]})) for d in changes["delete"]),
            after="".join("%s %s\n" % (path, json.dumps(u["set"])) for u in changes["update"])
                  + "".join("%s %s\n" % (path, json.dumps(c)) for c in changes["create"]),
        )
    module.exit_json(**result)


if __name__ == "__main__":
    main()
