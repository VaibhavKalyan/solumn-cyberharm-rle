def test_authorized_only(scope):
    assert [a.asset_id for a in scope["assets"]] == ["asset-01", "asset-02", "asset-03", "asset-04"]
    assert all(a.in_scope for a in scope["assets"])


def test_network_context_out_of_scope(scope):
    ctx = scope["network_context"]
    assert [a.asset_id for a in ctx] == ["ext-meridian-billing"]
    assert all(not a.in_scope for a in ctx)
    assert ctx[0].port == 9009
