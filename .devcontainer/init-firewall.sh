#!/bin/bash
set -euo pipefail

echo "Initializing firewall"

# Fix volume permissions (for Docker volumes only, not bind mounts)
chown -R dev:dev /home/dev/.mozbuild /home/dev/.cargo /home/dev/.rustup /commandhistory 2>/dev/null || true

# Clean up existing rules
iptables-save | grep docker | iptables-restore || true
iptables -F OUTPUT
iptables -F INPUT
iptables -F FORWARD
ipset destroy allowed-domains 2>/dev/null || true

# Create ipset for allowed IPs
ipset create allowed-domains hash:net

# Fetch all IPs BEFORE blocking traffic
echo "Fetching GitHub IP ranges..."
GITHUB_IPS=$(curl -s https://api.github.com/meta | jq -r '.git[]')
for IP in $GITHUB_IPS; do
    if [[ $IP =~ ^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+/[0-9]+$ ]]; then
        echo "  Adding GitHub CIDR: $IP"
        ipset add allowed-domains "$IP" 2>/dev/null || true
    fi
done

echo "Resolving and adding Mozilla domains..."
MOZILLA_DOMAINS=(
    "hg.mozilla.org"
    "firefox-ci-tc.services.mozilla.com"
    "firefoxci.taskcluster-artifacts.net"
    "archive.mozilla.org"
    "download.mozilla.org"
    "ftp.mozilla.org"
    "bugzilla.mozilla.org"
    "phabricator.services.mozilla.com"
)

for DOMAIN in "${MOZILLA_DOMAINS[@]}"; do
    echo "  Resolving $DOMAIN..."
    IPS=$(dig +short "$DOMAIN" A | grep -E '^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+$' || true)
    for IP in $IPS; do
        echo "    Adding IP: $IP"
        ipset add allowed-domains "$IP/32" 2>/dev/null || true
    done
done

echo "Resolving and adding development infrastructure domains..."
DEV_DOMAINS=(
    "registry.npmjs.org"
    "nodejs.org"
    "pypi.org"
    "files.pythonhosted.org"
    "crates.io"
    "static.crates.io"
    "index.crates.io"
    "static.rust-lang.org"
    "sh.rustup.rs"
)

for DOMAIN in "${DEV_DOMAINS[@]}"; do
    echo "  Resolving $DOMAIN..."
    IPS=$(dig +short "$DOMAIN" A | grep -E '^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+$' || true)
    for IP in $IPS; do
        echo "    Adding IP: $IP"
        ipset add allowed-domains "$IP/32" 2>/dev/null || true
    done
done

echo "Resolving and adding Anthropic domains..."
ANTHROPIC_DOMAINS=(
    "api.anthropic.com"
    "claude.ai"
)

for DOMAIN in "${ANTHROPIC_DOMAINS[@]}"; do
    echo "  Resolving $DOMAIN..."
    IPS=$(dig +short "$DOMAIN" A | grep -E '^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+$' || true)
    for IP in $IPS; do
        echo "    Adding IP: $IP"
        ipset add allowed-domains "$IP/32" 2>/dev/null || true
    done
done

echo "Adding host network..."
HOST_NETWORK=$(ip route | grep 'default via' | awk '{print $3}' | sed 's/\.[0-9]*$/.0\/24/')
if [ -n "$HOST_NETWORK" ]; then
    echo "  Adding host network: $HOST_NETWORK"
    ipset add allowed-domains "$HOST_NETWORK"
fi

# NOW set up restrictive firewall rules
echo "Configuring firewall rules..."

# Set default policies to DROP
iptables -P INPUT DROP
iptables -P FORWARD DROP
iptables -P OUTPUT DROP

# Allow DNS queries
iptables -A OUTPUT -p udp --dport 53 -j ACCEPT
iptables -A INPUT -p udp --sport 53 -j ACCEPT

# Allow SSH
iptables -A OUTPUT -p tcp --dport 22 -j ACCEPT
iptables -A INPUT -p tcp --sport 22 -j ACCEPT

# Allow loopback
iptables -A INPUT -i lo -j ACCEPT
iptables -A OUTPUT -o lo -j ACCEPT

# Allow established connections
iptables -A OUTPUT -m state --state ESTABLISHED,RELATED -j ACCEPT
iptables -A INPUT -m state --state ESTABLISHED,RELATED -j ACCEPT

# Allow whitelisted domains
iptables -A OUTPUT -m set --match-set allowed-domains dst -j ACCEPT
iptables -A INPUT -m set --match-set allowed-domains src -j ACCEPT

# Reject everything else
iptables -A OUTPUT -j REJECT --reject-with icmp-port-unreachable
iptables -A INPUT -j REJECT --reject-with icmp-port-unreachable

echo "Firewall configuration complete!"
echo "Testing connectivity..."

if curl -s --max-time 5 https://api.github.com/zen > /dev/null; then
    echo "GitHub access: OK"
else
    echo "GitHub access: FAILED"
fi

if curl -s --max-time 5 https://example.com > /dev/null; then
    echo "WARNING: Unrestricted access detected (example.com is reachable)"
else
    echo "Firewall working correctly (example.com blocked)"
fi

echo "Firewall initialization complete!"
