#!/usr/bin/env python3
"""
Generate PKCE (Proof Key for Code Exchange) Parameters

Generates cryptographically secure code_verifier and code_challenge
for OAuth 2.0 Authorization Code Flow with PKCE (RFC 7636).

PKCE is MANDATORY as of RFC 9700 (January 2025) for all OAuth clients.

Usage:
    python generate_pkce.py [--method METHOD] [--length LENGTH]

Methods:
    S256 - SHA256 hash (RECOMMENDED and default)
    plain - No hash (NOT RECOMMENDED, only for debugging)

RFC 7636 Requirements:
- code_verifier: 43-128 characters, [A-Z, a-z, 0-9, -, ., _, ~]
- code_challenge_method: S256 (REQUIRED by RFC 9700)
"""

import secrets
import hashlib
import base64
import argparse


def generate_code_verifier(length: int = 64) -> str:
    """
    Generate a cryptographically random code verifier.
    
    RFC 7636: code verifier must be 43-128 characters long and
    use only [A-Z, a-z, 0-9, -, ., _, ~] characters.
    
    Args:
        length: Number of bytes for random generation (default: 64)
        
    Returns:
        URL-safe base64 encoded string (without padding)
    """
    if not 43 <= length <= 128:
        print(f"⚠️  Warning: RFC 7636 recommends length between 43-128 characters")
    
    # Generate cryptographically secure random bytes
    random_bytes = secrets.token_bytes(length)
    
    # Base64url encode and remove padding
    code_verifier = base64.urlsafe_b64encode(random_bytes).decode('utf-8').rstrip('=')
    
    # Ensure length is within RFC bounds
    if len(code_verifier) < 43:
        code_verifier += secrets.token_urlsafe(43 - len(code_verifier))
    elif len(code_verifier) > 128:
        code_verifier = code_verifier[:128]
    
    return code_verifier


def generate_code_challenge(code_verifier: str, method: str = 'S256') -> str:
    """
    Generate code challenge from code verifier.
    
    Args:
        code_verifier: The code verifier string
        method: 'S256' (recommended) or 'plain' (not recommended)
        
    Returns:
        Code challenge string
    """
    if method == 'S256':
        # SHA256 hash
        digest = hashlib.sha256(code_verifier.encode('utf-8')).digest()
        # Base64url encode and remove padding
        code_challenge = base64.urlsafe_b64encode(digest).decode('utf-8').rstrip('=')
    elif method == 'plain':
        # Plain method (not recommended)
        code_challenge = code_verifier
    else:
        raise ValueError(f"Invalid method: {method}. Use 'S256' or 'plain'")
    
    return code_challenge


def main():
    parser = argparse.ArgumentParser(
        description='Generate PKCE parameters for OAuth 2.0 Authorization Code Flow',
        epilog='RFC 9700 requires PKCE for ALL OAuth clients (public and confidential)'
    )
    parser.add_argument(
        '--method',
        choices=['S256', 'plain'],
        default='S256',
        help='Code challenge method (default: S256, REQUIRED by RFC 9700)'
    )
    parser.add_argument(
        '--length',
        type=int,
        default=64,
        help='Code verifier length in bytes (default: 64)'
    )
    parser.add_argument(
        '--count',
        type=int,
        default=1,
        help='Number of PKCE pairs to generate (default: 1)'
    )

    args = parser.parse_args()

    if args.method == 'plain':
        print("\n⚠️  WARNING: 'plain' method is NOT RECOMMENDED!")
        print("   RFC 9700 requires using S256 for all OAuth clients.")
        print("   The 'plain' method provides no security benefits.\n")

    print(f"\nGenerating {args.count} PKCE parameter pair(s):\n")
    print("=" * 80)
    
    for i in range(args.count):
        code_verifier = generate_code_verifier(args.length)
        code_challenge = generate_code_challenge(code_verifier, args.method)
        
        if args.count > 1:
            print(f"\n🔐 PKCE Pair {i+1}:")
        else:
            print(f"\n🔐 PKCE Parameters:")
        
        print(f"\ncode_verifier:")
        print(f"  {code_verifier}")
        print(f"  (Length: {len(code_verifier)} characters)")
        
        print(f"\ncode_challenge:")
        print(f"  {code_challenge}")
        print(f"  (Method: {args.method})")
        
        print("\n" + "=" * 80)
    
    print("\n📋 Usage Instructions:")
    print("\n1. Authorization Request - Send to authorization server:")
    print("   - Include: code_challenge")
    print(f"   - Include: code_challenge_method={args.method}")
    print("\n2. Token Request - Send to token endpoint:")
    print("   - Include: code_verifier")
    print("   - Include: authorization_code (from step 1 callback)")
    
    print("\n⚠️  IMPORTANT:")
    print("   - Store code_verifier SECURELY (session/secure storage)")
    print("   - code_verifier is SECRET - never expose in URLs or logs")
    print("   - code_challenge is safe to send in authorization request")
    print("   - Generate NEW pair for EACH authorization request")
    
    print("\n🔒 Security Notes:")
    print("   - PKCE is MANDATORY as of RFC 9700 (January 2025)")
    print("   - Always use S256 method (SHA-256)")
    print("   - Never reuse code_verifier across sessions")
    print("   - code_verifier must be stored securely between auth and token requests")


if __name__ == "__main__":
    main()
