#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Fix Script 2 bracket issues"""

import re

file_path = r'e:\ProjLegacy\DeepPsych\psyclaw.html'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Find all script blocks with their positions
script_pattern = r'(<script[^>]*>)(.*?)(</script>)'
scripts = list(re.finditer(script_pattern, content, re.DOTALL))

print(f'Found {len(scripts)} script blocks')

if len(scripts) >= 3:
    # Script 2 is the third one (index 2) - the DOMContentLoaded script
    script2_match = scripts[2]
    script2_content = script2_match.group(2)
    
    print(f'\nScript 2 (DOMContentLoaded):')
    print(f'  Start: {script2_match.start()}')
    print(f'  End: {script2_match.end()}')
    print(f'  Length: {len(script2_content)} chars')
    
    # Count brackets
    open_braces = script2_content.count('{')
    close_braces = script2_content.count('}')
    open_brackets = script2_content.count('[')
    close_brackets = script2_content.count(']')
    
    print(f'  Braces: {open_braces} open, {close_braces} close (diff: {open_braces - close_braces})')
    print(f'  Brackets: {open_brackets} open, {close_brackets} close (diff: {open_brackets - close_brackets})')
    
    # The issue might be that the script content includes the next </script> tag
    # Let's check
    print(f'\n  Last 100 chars: {repr(script2_content[-100:])}')
else:
    print('Not enough script blocks found')
