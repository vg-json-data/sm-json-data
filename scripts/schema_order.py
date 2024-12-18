def resolve_schema(schema, resolver):
    if "$ref" in schema:
        res = resolver.lookup(schema["$ref"])
        ref_schema = res.contents
        schema = {**ref_schema, **schema}
        return schema, res.resolver
    else:
        return schema, resolver

def order_by_schema(obj, schema, resolver):
    schema, resolver = resolve_schema(schema, resolver)
    if isinstance(obj, dict):
        out = {}
        for k, s in schema["properties"].items():
            if k in obj:
                out[k] = order_by_schema(obj[k], s, resolver)
        return out
    elif isinstance(obj, list):
        return [order_by_schema(x, schema["items"], resolver) for x in obj]
    else:
        return obj