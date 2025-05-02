import hashlib
import inspect
import os
from typing import Optional
from itertools import count

# Atomic counters for each component type
_button_counter = count()
_form_counter = count()

def generate_component_key(
    component_type: str,
    component_name: str,
    extra_context: Optional[str] = None
) -> str:
    """
    Guaranteed unique key generator with atomic counters.
    Uses multiple uniqueness strategies as fallbacks.
    """
    # Get caller context
    frame = inspect.currentframe().f_back.f_back.f_back  # Go back to actual caller
    caller_info = f"{os.path.basename(frame.f_code.co_filename)}:{frame.f_lineno}"
    
    # Build unique base using multiple strategies
    unique_parts = [
        component_type,
        component_name,
        caller_info,
        str(next(_button_counter if component_type == "button" else _form_counter)),
        str(os.getpid()),  # Process ID
        str(id(frame))  # Memory address
    ]
    
    if extra_context:
        unique_parts.append(extra_context)
        
    base_key = "_".join(unique_parts)
    
    # Generate SHA3-256 hash
    return f"{component_type[:3]}_{hashlib.sha3_256(base_key.encode()).hexdigest()[:16]}"