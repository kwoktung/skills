#!/bin/bash
# check_domain.sh — Check if a domain name is available for registration.
# Usage: ./check_domain.sh <domain>
# Output: prints one of: AVAILABLE, REGISTERED, UNKNOWN, TIMEOUT
# Exit codes: 0=available, 1=registered, 2=unknown/error, 124=timeout

DOMAIN=$(echo "$1" | tr '[:upper:]' '[:lower:]')

if [ -z "$DOMAIN" ]; then
    echo "Usage: $0 <domain>" >&2
    exit 2
fi

# --- whois check (primary signal) ---
WHOIS_OUT=$(timeout 10 whois "$DOMAIN" 2>&1)
WHOIS_EXIT=$?

if [ $WHOIS_EXIT -eq 124 ]; then
    # whois timed out — fall through to dig rather than giving up
    WHOIS_OUT=""
fi

# Availability patterns gathered across TLDs:
#   .com/.net:         "No match for domain"
#   .uk/.co.uk:        "No match for" / "has not been registered"
#   .io/.ai/.au/.org:  "Domain not found."
#   .me/.com.au:       "Domain not found."
#   .de:               "Status: free"
#   .fr:               "NOT FOUND"
#   .us:               "No Data Found"
#   .ca:               "Not found:"
#   .xyz/.co:          "DOMAIN NOT FOUND"
AVAIL_PATTERN='no match for|not found|status:[[:space:]]*free|no data found|is available|free to register|has not been registered'

# Registration patterns (present when a domain IS registered)
REG_PATTERN='domain name:|registrar:|creation date:|registered on:|registered until|paid-till:|expires on:|registry expiry'

WHOIS_AVAIL=$(echo "$WHOIS_OUT" | grep -ciE "$AVAIL_PATTERN")
WHOIS_REG=$(echo "$WHOIS_OUT" | grep -ciE "$REG_PATTERN")

# Whois is conclusive — available
if [ "$WHOIS_AVAIL" -gt 0 ] && [ "$WHOIS_REG" -eq 0 ]; then
    echo "AVAILABLE"
    exit 0
fi

# Whois is conclusive — registered
if [ "$WHOIS_REG" -gt 0 ] && [ "$WHOIS_AVAIL" -eq 0 ]; then
    echo "REGISTERED"
    exit 1
fi

# --- dig fallback (secondary signal when whois is ambiguous/empty) ---
# Uses Cloudflare DNS (1.1.1.1) to avoid local DNS overrides.
# NXDOMAIN = no DNS record = likely available; NOERROR = has DNS = likely registered.
# dig header line: ";; ->>HEADER<<- opcode: QUERY, status: NXDOMAIN, id: ..."
# field 6 is the status value; strip trailing comma
DIG_STATUS=$(dig @1.1.1.1 "$DOMAIN" A +time=5 +tries=1 2>/dev/null | awk '/status:/{gsub(/,/,"",$6); print $6}')

case "$DIG_STATUS" in
    NXDOMAIN)
        echo "AVAILABLE"
        exit 0
        ;;
    NOERROR|SERVFAIL)
        # NOERROR = domain resolves; SERVFAIL often means registered but
        # nameservers refusing external queries (parked/misconfigured DNS)
        echo "REGISTERED"
        exit 1
        ;;
    *)
        echo "UNKNOWN"
        exit 2
        ;;
esac
