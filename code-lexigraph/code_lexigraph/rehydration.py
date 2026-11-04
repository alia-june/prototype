import ast
import keyword


class ConstructionError(ValueError):
    pass


def rehydrate(bundle):
    def require(condition, message):
        if not condition:
            raise ConstructionError(message)

    require(bundle["format"] == "code-lexigraph-rehydration/0.1",
            "unsupported bundle format")
    graph = bundle["graph"]
    require(graph["format"] == "code-lexigraph-example/0.1",
            "unsupported graph format")
    require(bundle["profile"] == "L01", "unsupported profile")
    nodes = {node["id"]: node for node in graph["nodes"]}
    require(len(nodes) == len(graph["nodes"]), "duplicate graph node")
    edge_ids = set()
    for edge in graph["edges"]:
        require(edge["id"] not in edge_ids, "duplicate graph edge")
        edge_ids.add(edge["id"])
        require(edge["from"] in nodes and edge["to"] in nodes,
                "unresolved graph endpoint")
        require(edge["relation"] in graph["relation_meanings"],
                "undeclared graph relation")

    def selected(key):
        require(key in bundle["bindings"], "missing binding: " + key)
        value = bundle["bindings"][key]
        require(value.get("status") == "selected",
                "unresolved binding: " + key)
        return value

    survivor = selected("survivor")
    boundary = selected("boundary")
    working = selected("working")
    require(survivor["representation"] == "caller_json_text",
            "unsupported survivor representation")
    require(boundary["value"] == "system_entry_to_return",
            "unsupported boundary")
    require(working["representation"] == "parsed_json_tree",
            "unsupported working representation")
    require(nodes["K01"]["profile"] == nodes["M01"]["profile"] == "L01",
            "contract/profile mismatch")

    def identifier(value):
        if isinstance(value, dict):
            require(value == {"binding": "survivor.parameter"},
                    "unknown identifier binding")
            value = survivor["parameter"]
        require(isinstance(value, str) and value.isidentifier()
                and not keyword.iskeyword(value), "invalid identifier")
        return value

    identifier(survivor["parameter"])
    lines, spans, declared = [], {}, set()

    def expression(spec):
        tag, *parts = spec
        if tag == "name":
            value, = parts
            return identifier(value)
        if tag == "bound":
            path, = parts
            require(path == "survivor.parameter", "unknown expression binding")
            return identifier(survivor["parameter"])
        if tag == "literal":
            value, = parts
            require(isinstance(value, str), "only string literals supported")
            return repr(value)
        if tag == "attr":
            owner, member = parts
            return expression(owner) + "." + identifier(member)
        if tag == "call":
            callee, arguments = parts
            return expression(callee) + "(" + ", ".join(
                expression(arg) for arg in arguments) + ")"
        if tag == "dict":
            pairs, = parts
            require(all(isinstance(key, str) for key, _ in pairs),
                    "dictionary keys must be strings")
            return "{" + ", ".join(
                repr(key) + ": " + expression(value)
                for key, value in pairs) + "}"
        if tag in ("is", "is_not"):
            left, right = parts
            operator = " is " if tag == "is" else " is not "
            return expression(left) + operator + expression(right)
        raise ConstructionError("unknown expression: " + str(tag))

    def line(level, text):
        lines.append("    " * level + text)

    def begin(record):
        key = record["id"]
        require(key not in declared, "duplicate construction ID: " + key)
        declared.add(key)
        return len(lines) + 1

    def suite(records, level):
        require(bool(records), "empty suite")
        for record in records:
            statement(record, level)

    def statement(record, level):
        start = begin(record)
        op = record["op"]
        if op == "from_import":
            line(level, "from " + identifier(record["module"])
                 + " import " + identifier(record["name"]))
        elif op == "import":
            line(level, "import " + identifier(record["name"]))
        elif op == "class":
            bases = ", ".join(identifier(x) for x in record["bases"])
            line(level, "class " + identifier(record["name"]) + "(" + bases + "):")
            suite(record["body"], level + 1)
        elif op == "function":
            parameters = ", ".join(identifier(x) for x in record["parameters"])
            line(level, "def " + identifier(record["name"])
                 + "(" + parameters + "):")
            suite(record["body"], level + 1)
        elif op == "assign":
            line(level, identifier(record["name"]) + " = "
                 + expression(record["value"]))
        elif op in ("return", "raise"):
            line(level, op + " " + expression(record["value"]))
        elif op == "expression":
            line(level, expression(record["value"]))
        elif op == "if":
            line(level, "if " + expression(record["test"]) + ":")
            suite(record["body"], level + 1)
        elif op == "try":
            line(level, "try:")
            suite(record["body"], level + 1)
            handler = record["handler"]
            handler_start = begin(handler)
            line(level, "except " + identifier(handler["type"])
                 + " as " + identifier(handler["name"]) + ":")
            suite(handler["body"], level + 1)
            spans[handler["id"]] = {"start": handler_start, "end": len(lines)}
        else:
            raise ConstructionError("unknown statement: " + str(op))
        spans[record["id"]] = {"start": start, "end": len(lines)}

    for record in bundle["module"]:
        statement(record, 0)
        lines.append("")
    source = "\n".join(lines).rstrip() + "\n"
    ast.parse(source)

    trace, inverse, linked_code, covered = [], {}, set(), set()

    def cover(key):
        require(key in spans, "unresolved construction: " + key)
        span = spans[key]
        for candidate, extent in spans.items():
            if span["start"] <= extent["start"] and extent["end"] <= span["end"]:
                covered.add(candidate)

    for link in bundle["construction_links"]:
        key, code_id = link["blueprint"], link["code"]
        require(code_id in nodes and nodes[code_id]["kind"] == "code",
                "unresolved code mapping")
        require(code_id not in linked_code, "duplicate code mapping")
        require(all(ref in nodes and nodes[ref]["kind"] not in ("code", "observation")
                    for ref in link["meanings"]), "invalid meaning mapping")
        linked_code.add(code_id)
        cover(key)
        trace.append(dict(link, generated=spans[key]))
        for ref in [code_id] + link["meanings"]:
            inverse.setdefault(ref, []).append(key)

    for support in bundle["supporting_declarations"]:
        require(all(ref in linked_code for ref in support["supports"]),
                "unresolved supporting declaration")
        cover(support["blueprint"])
        for ref in support["supports"]:
            inverse.setdefault(ref, []).append(support["blueprint"])
    require(linked_code == {key for key, node in nodes.items()
                            if node["kind"] == "code"}, "unmapped code entry")
    require(covered == declared, "unaccounted construction")
    contract = nodes["K01"]
    require(all(ref in nodes and nodes[ref]["kind"] == "commitment"
                for ref in contract["requirements"] + contract["permitted_categories"]),
            "unresolved contract commitment")
    human = [
        "Contract K01; profile L01.",
        "Survivor: exact caller-supplied JSON text named " + survivor["parameter"] + ".",
        "Boundary: system entry through return.",
        "Working representation: separately parsed JSON tree.",
        "Requirements:"
    ]
    human += ["- " + ref + ": " + nodes[ref]["text"]
              for ref in contract["requirements"]]
    human += ["Permitted categories:"]
    human += ["- " + ref + ": " + nodes[ref]["text"]
              for ref in contract["permitted_categories"]]
    human += ["Method M01:", nodes["M01"]["text"]]
    return {"python": source, "human": "\n".join(human),
            "trace": trace, "inverse": inverse, "spans": spans}
