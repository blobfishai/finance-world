# Policy decoy library

Seeded into a task's document store when its `task.toml` sets
`[metadata] doc_mode = "buried"`. These are the adjacent policies a real finance function
actually maintains — they are plausible, self-consistent, and **never** contain the rule the
task turns on. Burying raises retrieval difficulty without introducing ambiguity: there is
still exactly one governing document and it is still discoverable.

This is the `tau2.retrieval_modes` lever (research/scenario-registry.json): the cheapest way
to escalate a task the flake scan labels `too_easy`, because it re-grades the same ground
truth against a harder search.
