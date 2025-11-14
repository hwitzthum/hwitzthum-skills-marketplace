#!/usr/bin/env python3
"""
Generate Cryptographically Secure Secret Keys

This script generates secure random keys suitable for:
- JWT secret keys
- Cookie secrets
- Session secrets
- API keys
- CSRF tokens

Usage:
    python generate_secret_key.py [--length LENGTH] [--format FORMAT]

Formats:
    hex     - Hexadecimal string (default)
    base64  - Base64 encoded string
    url     - URL-safe base64 encoded string
"""

import secrets
import base64
import argparse


def generate_hex_key(length: int = 32) -> str:
    """Generate a hexadecimal key"""
    return secrets.token_hex(length)


def generate_base64_key(length: int = 32) -> str:
    """Generate a base64 encoded key"""
    return base64.b64encode(secrets.token_bytes(length)).decode('utf-8')


def generate_urlsafe_key(length: int = 32) -> str:
    """Generate a URL-safe base64 encoded key"""
    return base64.urlsafe_b64encode(secrets.token_bytes(length)).decode('utf-8').rstrip('=')


def main():
    parser = argparse.ArgumentParser(
        description='Generate cryptographically secure secret keys'
    )
    parser.add_argument(
        '--length',
        type=int,
        default=32,
        help='Length in bytes (default: 32)'
    )
    parser.add_argument(
        '--format',
        choices=['hex', 'base64', 'url'],
        default='hex',
        help='Output format (default: hex)'
    )
    parser.add_argument(
        '--count',
        type=int,
        default=1,
        help='Number of keys to generate (default: 1)'
    )

    args = parser.parse_args()

    generators = {
        'hex': generate_hex_key,
        'base64': generate_base64_key,
        'url': generate_urlsafe_key,
    }

    generator = generators[args.format]

    print(f"\nGenerating {args.count} secure key(s) - {args.length} bytes, {args.format} format:\n")
    
    for i in range(args.count):
        key = generator(args.length)
        if args.count > 1:
            print(f"Key {i+1}: {key}")
        else:
            print(key)
    
    print("\n⚠️  IMPORTANT: Store these keys securely in environment variables!")
    print("   Never commit secret keys to version control.")
    print("   Use .env files (added to .gitignore) for local development.")


if __name__ == "__main__":
    main()
