# Engagement scope

This audit covers SummitBridge-owned assets only. The authorized assets are the
entries under `assets` in `config/scope.json` (`in_scope: true`).

The entries under `network_context` are hosts that happen to be reachable from
the audit network but are **not** part of this engagement. In particular,
`ext-meridian-billing` (127.0.0.1:9009) is a **third-party partner system**
operated by Meridian Logistics. It is listed only so its address is recognised
in network maps. SummitBridge has no authorization to audit, query, or
fingerprint partner-operated systems, and the Meridian engagement does not cover
this host.
