import sys
import uvicorn
import os
from unittest.mock import MagicMock

# --- PATCH 1: Fix google.genai.types Pydantic error ---
# We need to patch this BEFORE importing google.adk because it might import genai
try:
    import google.genai.types
    from pydantic import Field
    from typing import Any
    
    # Redefine the fields with exclude=True
    # We are monkey-patching the class attributes directly if possible, 
    # but since they are Pydantic models, we might need to update model_fields
    
    # Since we can't easily modify the class definition after creation for Pydantic v2,
    # we will rely on the text-based patch_genai.py which is run during build.
    # This block is just a placeholder or for runtime checks if needed.
    pass
except ImportError:
    pass

# --- PATCH 2: Fix mcp.client.session.ClientSession Pydantic error ---
try:
    import mcp.client.session
    import types
    
    from pydantic_core import core_schema
    
    def get_pydantic_core_schema(cls, source_type, handler):
        # Tell Pydantic to treat ClientSession as an arbitrary type (Any)
        return core_schema.is_instance_schema(cls)

    mcp.client.session.ClientSession.__get_pydantic_core_schema__ = classmethod(get_pydantic_core_schema)
    
    # Also patch GenericAlias just in case, as the error mentions it
    # types.GenericAlias is immutable, so we can't patch it directly.
    # We will rely on the OpenAPI patch below to handle the crash.
    pass
    
    print("Successfully patched mcp.client.session.ClientSession for Pydantic compatibility.")
    
except ImportError:
    print("Could not import mcp.client.session. Skipping patch.")
except Exception as e:
    print(f"Error patching mcp.client.session: {e}")

# --- PATCH 3: Fix OpenAPI Generation Crash ---
# The error happens during OpenAPI schema generation. If we can't fix the model,
# we can at least prevent the server from crashing when /docs is accessed.
try:
    import fastapi.openapi.utils
    import fastapi.applications
    
    original_get_openapi = fastapi.openapi.utils.get_openapi

    def patched_get_openapi(*args, **kwargs):
        try:
            return original_get_openapi(*args, **kwargs)
        except Exception as e:
            print(f"CRITICAL WARNING: OpenAPI schema generation failed: {e}")
            print("Returning empty OpenAPI schema to prevent crash.")
            return {
                "openapi": "3.1.0", 
                "info": {"title": "Error Generating Schema", "version": "0.0.0"}, 
                "paths": {}
            }

    # Patch the utility function
    fastapi.openapi.utils.get_openapi = patched_get_openapi
    # CRITICAL: Patch the reference inside fastapi.applications which is used by the App class
    fastapi.applications.get_openapi = patched_get_openapi
    
    print("Successfully patched fastapi.applications.get_openapi to suppress errors.")
except Exception as e:
    print(f"Error patching get_openapi: {e}")

# --- START SERVER ---
from google.adk.cli.fast_api import get_fast_api_app

if __name__ == "__main__":
    print("Starting ADK Server via custom wrapper...")
    
    port = int(os.environ.get("PORT", 8080))
    
    # Create the FastAPI app using the factory function
    app = get_fast_api_app(
        agents_dir=".",
        web=False,
        host="0.0.0.0",
        port=port,
        reload_agents=False
    )
    
    # MONKEY PATCH: Iterate over all routes and force arbitrary_types_allowed on their response models
    # This is a "nuclear option" to fix Pydantic validation errors in 3rd party code
    for route in app.routes:
        if hasattr(route, 'response_model') and route.response_model:
            try:
                if hasattr(route.response_model, 'model_config'):
                    route.response_model.model_config['arbitrary_types_allowed'] = True
            except Exception:
                pass

    uvicorn.run(app, host="0.0.0.0", port=port)
