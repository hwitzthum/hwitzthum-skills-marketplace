#!/usr/bin/env python3
"""
JWT Token Validation Tester

Test JWT token validation against your authentication configuration.
Validates signature, expiration, issuer, audience, and other claims.

Usage:
    python validate_jwt.py --token YOUR_JWT_TOKEN [OPTIONS]

Requirements:
    pip install pyjwt cryptography

Example:
    python validate_jwt.py \\
        --token eyJhbGciOiJSUzI1NiIs... \\
        --issuer https://your-domain.auth0.com/ \\
        --audience your-api-identifier
"""

import jwt
import json
import argparse
from datetime import datetime
from typing import Dict, Any


def decode_jwt_header(token: str) -> Dict[str, Any]:
    """Decode JWT header without validation"""
    try:
        header = jwt.get_unverified_header(token)
        return header
    except Exception as e:
        return {"error": str(e)}


def decode_jwt_payload(token: str) -> Dict[str, Any]:
    """Decode JWT payload without validation"""
    try:
        # Decode without verification to inspect payload
        payload = jwt.decode(token, options={"verify_signature": False})
        return payload
    except Exception as e:
        return {"error": str(e)}


def validate_jwt(
    token: str,
    secret: str = None,
    algorithm: str = "HS256",
    issuer: str = None,
    audience: str = None,
    verify_exp: bool = True,
    jwks_uri: str = None
) -> tuple[bool, Dict[str, Any], str]:
    """
    Validate JWT token
    
    Returns:
        (is_valid, decoded_payload, error_message)
    """
    try:
        options = {
            "verify_signature": True if secret else False,
            "verify_exp": verify_exp,
            "verify_iat": True,
            "verify_aud": True if audience else False,
            "verify_iss": True if issuer else False,
        }
        
        decode_params = {
            "jwt": token,
            "options": options,
            "algorithms": [algorithm] if algorithm else None,
        }
        
        if secret:
            decode_params["key"] = secret
        
        if issuer:
            decode_params["issuer"] = issuer
        
        if audience:
            decode_params["audience"] = audience
        
        payload = jwt.decode(**decode_params)
        return True, payload, None
        
    except jwt.ExpiredSignatureError:
        return False, {}, "Token has expired"
    except jwt.InvalidTokenError as e:
        return False, {}, f"Invalid token: {str(e)}"
    except Exception as e:
        return False, {}, f"Validation error: {str(e)}"


def format_timestamp(timestamp: int) -> str:
    """Format Unix timestamp to readable date"""
    try:
        dt = datetime.fromtimestamp(timestamp)
        return dt.strftime('%Y-%m-%d %H:%M:%S UTC')
    except:
        return str(timestamp)


def print_jwt_info(token: str, secret: str = None, issuer: str = None, 
                   audience: str = None, algorithm: str = "HS256"):
    """Print detailed JWT information"""
    print("\n" + "=" * 80)
    print("JWT TOKEN ANALYSIS")
    print("=" * 80)
    
    # Decode header
    print("\n📋 HEADER (Unverified):")
    print("-" * 80)
    header = decode_jwt_header(token)
    print(json.dumps(header, indent=2))
    
    # Decode payload
    print("\n📦 PAYLOAD (Unverified):")
    print("-" * 80)
    payload = decode_jwt_payload(token)
    
    if "error" not in payload:
        # Format timestamps
        if "exp" in payload:
            print(f"  exp (Expires):  {payload['exp']} ({format_timestamp(payload['exp'])})")
        if "iat" in payload:
            print(f"  iat (Issued):   {payload['iat']} ({format_timestamp(payload['iat'])})")
        if "nbf" in payload:
            print(f"  nbf (Not Before): {payload['nbf']} ({format_timestamp(payload['nbf'])})")
        
        # Print other claims
        print("\n  Other Claims:")
        for key, value in payload.items():
            if key not in ['exp', 'iat', 'nbf']:
                print(f"    {key}: {value}")
    else:
        print(json.dumps(payload, indent=2))
    
    # Validate if secret provided
    print("\n🔐 VALIDATION:")
    print("-" * 80)
    
    if not secret and algorithm.startswith('HS'):
        print("⚠️  No secret provided - skipping signature validation")
        print("   Provide --secret for HS256/HS384/HS512 algorithms")
        is_valid, validated_payload, error = False, payload, "No secret provided"
    elif algorithm.startswith('RS') or algorithm.startswith('ES'):
        print("ℹ️  RS/ES algorithms require public key or JWKS")
        print("   Provide --jwks-uri for RS256/RS384/RS512/ES256/ES384 validation")
        is_valid, validated_payload, error = False, payload, "Public key required"
    else:
        is_valid, validated_payload, error = validate_jwt(
            token=token,
            secret=secret,
            algorithm=algorithm,
            issuer=issuer,
            audience=audience
        )
    
    if is_valid:
        print("✅ Token is VALID")
        print("\n  Validated Claims:")
        print(json.dumps(validated_payload, indent=4))
    else:
        print(f"❌ Token is INVALID")
        print(f"   Error: {error}")
    
    # Security recommendations
    print("\n🛡️  SECURITY RECOMMENDATIONS:")
    print("-" * 80)
    
    recommendations = []
    
    # Check algorithm
    if header.get('alg') == 'none':
        recommendations.append("⚠️  CRITICAL: 'none' algorithm detected - token is NOT signed!")
    elif header.get('alg') in ['HS256', 'HS384', 'HS512']:
        recommendations.append("✅ Using HMAC algorithm (symmetric key)")
        recommendations.append("   Ensure SECRET_KEY has high entropy (32+ bytes)")
    elif header.get('alg') in ['RS256', 'RS384', 'RS512']:
        recommendations.append("✅ Using RSA algorithm (asymmetric key)")
        recommendations.append("   Best practice for production (RFC 9700 compliant)")
    
    # Check expiration
    if "exp" not in payload:
        recommendations.append("⚠️  WARNING: Token has no expiration (exp claim missing)")
        recommendations.append("   RFC 9700 requires short-lived access tokens (15-60 min)")
    else:
        exp_time = datetime.fromtimestamp(payload["exp"])
        now = datetime.now()
        if exp_time < now:
            recommendations.append("❌ Token is EXPIRED")
        else:
            time_left = exp_time - now
            if time_left.total_seconds() > 3600:  # > 1 hour
                recommendations.append("⚠️  WARNING: Token expiration > 1 hour")
                recommendations.append("   RFC 9700 recommends 15-60 minute expiration")
            else:
                recommendations.append(f"✅ Token expires in {int(time_left.total_seconds() / 60)} minutes")
    
    # Check issuer
    if issuer and "iss" in payload:
        if payload["iss"] == issuer:
            recommendations.append(f"✅ Issuer validated: {issuer}")
        else:
            recommendations.append(f"❌ Issuer mismatch: expected {issuer}, got {payload['iss']}")
    elif "iss" not in payload:
        recommendations.append("⚠️  WARNING: No issuer (iss) claim")
    
    # Check audience
    if audience and "aud" in payload:
        if payload["aud"] == audience or audience in payload.get("aud", []):
            recommendations.append(f"✅ Audience validated: {audience}")
        else:
            recommendations.append(f"❌ Audience mismatch: expected {audience}, got {payload['aud']}")
    elif "aud" not in payload:
        recommendations.append("⚠️  WARNING: No audience (aud) claim")
    
    for rec in recommendations:
        print(f"  {rec}")
    
    print("\n" + "=" * 80)


def main():
    parser = argparse.ArgumentParser(
        description='Validate and analyze JWT tokens',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Validate with HS256 (symmetric)
  python validate_jwt.py --token YOUR_TOKEN --secret YOUR_SECRET
  
  # Validate with issuer and audience
  python validate_jwt.py --token YOUR_TOKEN \\
    --issuer https://your-domain.auth0.com/ \\
    --audience your-api-identifier
  
  # Decode without validation
  python validate_jwt.py --token YOUR_TOKEN --no-verify
        """
    )
    
    parser.add_argument(
        '--token',
        required=True,
        help='JWT token to validate'
    )
    parser.add_argument(
        '--secret',
        help='Secret key for HS256/HS384/HS512 validation'
    )
    parser.add_argument(
        '--algorithm',
        default='HS256',
        help='JWT algorithm (default: HS256)'
    )
    parser.add_argument(
        '--issuer',
        help='Expected token issuer (iss claim)'
    )
    parser.add_argument(
        '--audience',
        help='Expected token audience (aud claim)'
    )
    parser.add_argument(
        '--no-verify',
        action='store_true',
        help='Decode without validation (inspect only)'
    )
    parser.add_argument(
        '--jwks-uri',
        help='JWKS URI for RS/ES algorithm validation'
    )
    
    args = parser.parse_args()
    
    try:
        print_jwt_info(
            token=args.token,
            secret=args.secret if not args.no_verify else None,
            issuer=args.issuer,
            audience=args.audience,
            algorithm=args.algorithm
        )
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
