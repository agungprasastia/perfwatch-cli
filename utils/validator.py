"""
Perfwatch Validator - URL and input validation utilities.
"""

import re
from urllib.parse import urlparse, urlunparse
from typing import Optional


def validate_url(url: str) -> tuple[bool, Optional[str]]:
    """
    Validate a URL.
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not url:
        return False, "URL cannot be empty"
    
    # Add scheme if missing
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    
    try:
        parsed = urlparse(url)
        
        # Check for valid scheme
        if parsed.scheme not in ('http', 'https'):
            return False, f"Invalid scheme: {parsed.scheme}. Must be http or https"
        
        # Check for valid netloc (domain)
        if not parsed.netloc:
            return False, "Invalid URL: missing domain"
        
        # Basic domain validation
        domain_pattern = r'^[a-zA-Z0-9]([a-zA-Z0-9-]*[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9-]*[a-zA-Z0-9])?)*\.[a-zA-Z]{2,}$'
        
        # Extract domain without port
        domain = parsed.netloc.split(':')[0]
        
        # Allow localhost and IP addresses for testing
        if domain == 'localhost' or _is_valid_ip(domain):
            return True, None
        
        if not re.match(domain_pattern, domain):
            return False, f"Invalid domain: {domain}"
        
        return True, None
        
    except Exception as e:
        return False, f"Invalid URL: {str(e)}"


def validate_domain(domain: str) -> tuple[bool, Optional[str]]:
    """
    Validate a domain name.
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not domain:
        return False, "Domain cannot be empty"
    
    # Remove any scheme if present
    if '://' in domain:
        domain = domain.split('://')[1]
    
    # Remove path if present
    domain = domain.split('/')[0]
    
    # Remove port if present
    domain = domain.split(':')[0]
    
    # Domain validation pattern
    domain_pattern = r'^[a-zA-Z0-9]([a-zA-Z0-9-]*[a-zA-Z0-9])?(\.[a-zA-Z0-9]([a-zA-Z0-9-]*[a-zA-Z0-9])?)*\.[a-zA-Z]{2,}$'
    
    if not re.match(domain_pattern, domain):
        return False, f"Invalid domain format: {domain}"
    
    return True, None


def normalize_url(url: str) -> str:
    """
    Normalize a URL by adding scheme if missing and cleaning up.
    """
    if not url:
        return url
    
    # Add https if no scheme
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    
    parsed = urlparse(url)
    
    # Rebuild URL with normalized components
    normalized = urlunparse((
        parsed.scheme,
        parsed.netloc.lower(),  # lowercase domain
        parsed.path or '/',
        parsed.params,
        parsed.query,
        ''  # remove fragment
    ))
    
    return normalized


def _is_valid_ip(ip: str) -> bool:
    """Check if string is a valid IP address."""
    # IPv4 pattern
    ipv4_pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
    
    if re.match(ipv4_pattern, ip):
        # Validate each octet
        octets = ip.split('.')
        return all(0 <= int(octet) <= 255 for octet in octets)
    
    return False


def extract_domain(url: str) -> str:
    """Extract domain from URL."""
    if not url:
        return ""
    
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    
    parsed = urlparse(url)
    return parsed.netloc.split(':')[0]
