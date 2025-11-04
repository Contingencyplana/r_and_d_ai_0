Contract Samples (Skeleton)

Layout
- emoji_runtime/: golden input payloads (emoji-runtime@1.0)
- factory_order_expected/: expected outputs (factory-order@1.0)

Filename pairs
- For each emoji_runtime/<name>.json there should be a matching
  factory_order_expected/<name>.json.

Scope
- Cover Level-0 templates at minimum: basic_ritual, guarded_delivery,
  signal_loop, conditional_repeat.

Validation
- Runner validates schemas for both input and expected, then performs
  structural checks (to be extended by implementers).

