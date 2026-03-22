# Troubleshooting

## Common Issues

### "Command not found: brainstormer"

The CLI isn't installed or not on your PATH.

```bash
cd /path/to/BrainStormer/cli
pip install -e .
```

Or run directly:
```bash
python /path/to/BrainStormer/cli/brainstormer.py init
```

### "Obsidian vault not found"

Your vault path isn't configured or the path doesn't exist.

```bash
# Set your vault path
brainstormer config set vault_path /path/to/your/vault

# Verify
brainstormer doctor
```

### "Already initialized"

Running `brainstormer init` on a project that's already set up.

```bash
# To re-sync templates without overwriting your files:
brainstormer init --update
```

### Files weren't created

BrainStormer skips files that already exist. Check with:
```bash
brainstormer status
```

If you see files missing that should be there, the template might not exist in your BrainStormer installation:
```bash
brainstormer doctor
```

### Obsidian sync not working

1. Check vault path: `brainstormer config get vault_path`
2. Make sure the vault directory exists
3. Run sync manually: `brainstormer sync`
4. Check for file permission issues

### Agent list is empty

Agents should be at `~/.claude/agents/`. Check:
```bash
ls ~/.claude/agents/ | wc -l
```

If empty, you may need to reinstall agents from the BrainStormer package.

---

## Getting Help

- Run `brainstormer help` for command overview
- Run `brainstormer help <command>` for specific command help
- Run `brainstormer doctor` to diagnose issues
