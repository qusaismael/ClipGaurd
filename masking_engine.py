"""
Masking Engine Module
Handles detection and masking of sensitive data in clipboard content.
"""

import re
from urllib.parse import urlparse, parse_qs, unquote, urlunparse
from typing import Dict, List, Tuple


class MaskingEngine:
    """
    Core engine for detecting and masking sensitive information.
    Supports both built-in and custom masking rules.
    """

    # Built-in masking patterns
    BUILTIN_PATTERNS = {
        "Email": {
            "pattern": r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            "replacement": "[REDACTED_EMAIL]",
            "enabled": True
        },
        "IPv4 Address": {
            "pattern": r'\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b',
            "replacement": "[REDACTED_IP]",
            "enabled": True
        },
        "Phone Number (US)": {
            "pattern": r'\b(?:\+?1[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})\b',
            "replacement": "[REDACTED_PHONE]",
            "enabled": True
        },
        "Credit Card": {
            "pattern": r'\b(?:\d{4}[-\s]?){3}\d{4}\b',
            "replacement": "[REDACTED_CC]",
            "enabled": True
        },
        "SSN": {
            "pattern": r'\b\d{3}-\d{2}-\d{4}\b',
            "replacement": "[REDACTED_SSN]",
            "enabled": True
        }
    }

    def __init__(self):
        """Initialize the masking engine with default patterns."""
        self.patterns = self.BUILTIN_PATTERNS.copy()
        self.custom_patterns: Dict[str, dict] = {}

    def set_patterns(self, patterns: Dict[str, dict]):
        """
        Update all patterns (built-in and custom).
        
        Args:
            patterns: Dictionary of pattern configurations
        """
        self.patterns = patterns

    def add_custom_pattern(self, name: str, pattern: str, replacement: str, enabled: bool = True):
        """
        Add a custom masking pattern.
        
        Args:
            name: Display name for the pattern
            pattern: Regex pattern to match
            replacement: Text to replace matches with
            enabled: Whether the pattern is active
        """
        self.custom_patterns[name] = {
            "pattern": pattern,
            "replacement": replacement,
            "enabled": enabled,
            "custom": True
        }

    def mask_text(self, text: str) -> Tuple[str, bool]:
        """
        Apply masking rules to the given text with smart detection.
        
        Smart Detection: Only mask if sensitive data is part of larger text.
        If clipboard contains ONLY a single piece of sensitive data and nothing else,
        it won't be masked (user likely copied it intentionally).
        
        Args:
            text: The text to mask
            
        Returns:
            Tuple of (masked_text, was_modified)
        """
        if not text or not text.strip():
            return text, False

        original_text = text
        
        # Combine all enabled patterns
        all_patterns = {**self.patterns, **self.custom_patterns}
        enabled_patterns = {
            name: data for name, data in all_patterns.items() 
            if data.get("enabled", True)
        }

        # Check if text is ONLY a single sensitive item (smart detection)
        if self._is_single_sensitive_item(text.strip(), enabled_patterns):
            return text, False

        # Apply masking
        masked_text = text
        for name, data in enabled_patterns.items():
            try:
                pattern = data["pattern"]
                replacement = data["replacement"]
                masked_text = re.sub(pattern, replacement, masked_text)
            except re.error:
                # Skip invalid regex patterns
                continue

        was_modified = masked_text != original_text
        return masked_text, was_modified

    def _is_single_sensitive_item(self, text: str, patterns: Dict[str, dict]) -> bool:
        """
        Check if text contains ONLY a single sensitive item and nothing else.
        
        Args:
            text: Trimmed text to check
            patterns: Enabled patterns to check against
            
        Returns:
            True if text is a single sensitive item only
        """
        for name, data in patterns.items():
            try:
                pattern = data["pattern"]
                matches = list(re.finditer(pattern, text))
                
                # If we find exactly one match and it covers the entire text
                if len(matches) == 1:
                    match = matches[0]
                    if match.start() == 0 and match.end() == len(text):
                        return True
            except re.error:
                continue
                
        return False

    def clean_link(self, url: str) -> Tuple[str, bool]:
        """
        Clean tracking parameters and unwrap redirectors from a URL.
        All operations are performed locally without network requests.
        
        Args:
            url: The URL to clean
            
        Returns:
            Tuple of (cleaned_url, was_modified)
        """
        if not url or not url.strip():
            return url, False

        original_url = url.strip()
        cleaned_url = original_url

        try:
            # Parse the URL
            parsed = urlparse(cleaned_url)
            
            # Unwrap common redirectors
            if 'google.com' in parsed.netloc and '/url' in parsed.path:
                # Extract target URL from Google redirector
                query_params = parse_qs(parsed.query)
                if 'q' in query_params:
                    cleaned_url = query_params['q'][0]
                    parsed = urlparse(cleaned_url)
            
            elif 'facebook.com' in parsed.netloc and '/l.php' in parsed.path:
                # Extract target URL from Facebook redirector
                query_params = parse_qs(parsed.query)
                if 'u' in query_params:
                    cleaned_url = unquote(query_params['u'][0])
                    parsed = urlparse(cleaned_url)

            # Strip AMP artifacts
            if 'google.com' in parsed.netloc and '/amp/s/' in parsed.path:
                # Convert google.com/amp/s/example.com/page to https://example.com/page
                amp_path = parsed.path.replace('/amp/s/', '')
                cleaned_url = f"https://{amp_path}"
                if parsed.query:
                    cleaned_url += f"?{parsed.query}"
                parsed = urlparse(cleaned_url)

            # Remove tracking parameters
            tracking_params = [
                'utm_source', 'utm_medium', 'utm_campaign', 'utm_term', 'utm_content',
                'fbclid', 'gclid', 'mc_eid', 'igshid', '_ga', 'ref', 'source'
            ]
            
            if parsed.query:
                query_params = parse_qs(parsed.query, keep_blank_values=True)
                
                # Filter out tracking parameters
                cleaned_params = {
                    key: values for key, values in query_params.items()
                    if key not in tracking_params
                }
                
                # Reconstruct query string
                if cleaned_params:
                    query_string = '&'.join(
                        f"{key}={values[0]}" if values else key
                        for key, values in cleaned_params.items()
                    )
                else:
                    query_string = ''
                
                # Rebuild URL
                cleaned_url = urlunparse((
                    parsed.scheme,
                    parsed.netloc,
                    parsed.path,
                    parsed.params,
                    query_string,
                    parsed.fragment
                ))

            was_modified = cleaned_url != original_url
            return cleaned_url, was_modified

        except Exception:
            # If anything goes wrong, return original URL
            return original_url, False


