# Firefox DevContainer with Safe YOLO Mode

This devcontainer configuration provides a secure, isolated development environment for Firefox with Claude Code's "Safe YOLO Mode" enabled. This allows Claude Code to run commands without permission prompts while maintaining security through network isolation.

## What is Safe YOLO Mode?

Safe YOLO Mode uses the `--dangerously-skip-permissions` flag in Claude Code within a containerized environment that has restricted network access. This provides:

- **Faster development**: No permission prompts for every command
- **Security through isolation**: Container has limited network access via firewall rules
- **Reversible operations**: Work is isolated in a container
- **Ideal for**: Fixing lint errors, running builds, generating boilerplate code

## Architecture

The devcontainer includes:

1. **Dockerfile**: Debian-based container with all Firefox build dependencies
2. **devcontainer.json**: VS Code configuration with extensions and settings
3. **init-firewall.sh**: Network firewall that restricts outbound connections to:
   - GitHub and Git operations
   - Mozilla infrastructure (hg.mozilla.org, bugzilla, phabricator)
   - Package registries (npm, PyPI, crates.io)
   - Anthropic API (for Claude Code)
   - Local host network

## Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop) or Docker Engine
- At least 30GB of free disk space
- 8GB+ RAM recommended
- Optional: [VS Code](https://code.visualstudio.com/) with [Dev Containers extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers) if you want to use VS Code

## Getting Started

### Using Without VS Code (Docker CLI)

If you prefer to use the devcontainer without VS Code, use the provided scripts:

```bash
# 1. Build the container image
./.devcontainer/build.sh

# 2. Test the container
./.devcontainer/test.sh

# 3a. Run an interactive shell
./.devcontainer/run.sh

# 3b. Or run Claude Code directly
./.devcontainer/run-claude.sh
```

Once in the container, you can:
- Run Firefox bootstrap: `python3 python/mozboot/bin/bootstrap.py --no-interactive`
- Build Firefox: `./mach build`
- Run Claude: `claude --dangerously-skip-permissions`

### First Time Setup (VS Code)

1. **Open the repository in VS Code**

2. **Reopen in Container**
   - Press `F1` or `Cmd/Ctrl+Shift+P`
   - Type "Dev Containers: Reopen in Container"
   - Select it and wait for the container to build (first time takes 10-20 minutes)

3. **Verify firewall**
   The firewall script runs automatically on container start. Check the output:
   ```bash
   # Should show "Firewall working correctly"
   sudo /usr/local/bin/init-firewall.sh
   ```

4. **Bootstrap Firefox**
   Run the Mozilla bootstrap script to set up remaining dependencies:
   ```bash
   python3 python/mozboot/bin/bootstrap.py --no-interactive
   ```

5. **Build Firefox**
   ```bash
   ./mach build
   ```

### Using Claude Code in Safe YOLO Mode

Once the container is running, use Claude Code from the terminal:

```bash
claude --dangerously-skip-permissions
```

Claude Code will be able to run commands without prompting for permission, but network access is restricted by the firewall.

Note: The CLI command is `claude`, not `claude-code`.

## Volume Persistence

The following directories are persisted across container rebuilds:

- `firefox-commandhistory`: Bash command history
- `firefox-claude-config`: Claude Code configuration
- `firefox-mozbuild`: Mozilla build state and dependencies
- `firefox-cargo`: Rust Cargo package cache
- `firefox-rustup`: Rust toolchain

This means your build artifacts, downloaded dependencies, and configuration survive container rebuilds.

## Network Access

The firewall allows access to:

### Allowed
- GitHub (git operations, releases)
- Mozilla infrastructure (Mercurial, Bugzilla, Phabricator, CI)
- Package managers (npm, PyPI, crates.io, Rust)
- Anthropic API (Claude Code)
- Local network (host machine)
- DNS and SSH

### Blocked
- General internet access
- Most external websites
- Data exfiltration targets

## Customization

### Adding Allowed Domains

Edit `.devcontainer/init-firewall.sh` and add domains to the appropriate arrays:

```bash
MOZILLA_DOMAINS=(
    "hg.mozilla.org"
    "your-domain.mozilla.org"  # Add here
)
```

Then rebuild the firewall:
```bash
sudo /usr/local/bin/init-firewall.sh
```

### Changing System Dependencies

Edit `.devcontainer/Dockerfile` and add packages to the `apt-get install` section. Then rebuild the container:
- Press `F1` → "Dev Containers: Rebuild Container"

## Troubleshooting

### Container won't start
- Ensure Docker has enough resources (8GB RAM, 30GB disk)
- Check Docker logs: `docker logs <container-id>`

### Network access issues
- Verify firewall is running: `sudo iptables -L -n`
- Test specific domain: `curl -v https://hg.mozilla.org`
- Check allowed IPs: `sudo ipset list allowed-domains`

### Build failures
- Ensure bootstrap completed: `python3 python/mozboot/bin/bootstrap.py --no-interactive`
- Check disk space: `df -h`
- Clean and rebuild: `./mach clobber && ./mach build`

### Firewall blocks needed service
1. Find the domain/IP that needs access
2. Add it to `init-firewall.sh`
3. Restart firewall: `sudo /usr/local/bin/init-firewall.sh`

## Security Considerations

This setup is designed for development work with Claude Code. It provides:

- **Isolation**: Work happens in a container separate from your host system
- **Network restrictions**: Firewall limits data exfiltration risk
- **Audit trail**: All commands run by Claude Code are logged in shell history

However, keep in mind:

- This is not a security sandbox for untrusted code
- Claude Code has full access to files in the workspace
- The allowed domains can still be used for data exfiltration if targeted
- Always review code changes before committing

## Differences from Standard Firefox Development

When using this devcontainer:

1. **All work is in `/workspace`**: The Firefox source is mounted there
2. **Bootstrap runs inside container**: Don't run it on your host machine
3. **Artifacts persist**: Build outputs survive container restarts via volumes
4. **Git config**: You may need to configure git inside the container:
   ```bash
   git config --global user.name "Your Name"
   git config --global user.email "your.email@example.com"
   ```

## Resources

- [Claude Code Best Practices](https://www.anthropic.com/engineering/claude-code-best-practices)
- [Firefox Build Documentation](https://firefox-source-docs.mozilla.org/setup/linux_build.html)
- [VS Code Dev Containers](https://code.visualstudio.com/docs/devcontainers/containers)

## Support

For issues with:
- **DevContainer setup**: File an issue in the Firefox repository
- **Claude Code**: See [Claude Code documentation](https://github.com/anthropics/claude-code)
- **Firefox builds**: See [Firefox build documentation](https://firefox-source-docs.mozilla.org/)
