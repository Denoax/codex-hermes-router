# Contributing

Keep changes small and evidence-backed. Before opening a PR:

```bash
bash -n bin/hermes-worker install.sh uninstall.sh
python -m unittest discover -s tests -v
```

Do not add new routing claims, supported versions, benchmark results, or security guarantees without evidence. Keep project-specific agent behavior out of the global `local-worker` skill.
