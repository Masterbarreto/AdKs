import os
import site
import sys

def patch_genai():
    # Find site-packages
    site_packages = site.getsitepackages()
    target_file = None
    
    for sp in site_packages:
        potential_path = os.path.join(sp, 'google', 'genai', 'types.py')
        if os.path.exists(potential_path):
            target_file = potential_path
            break
            
    if not target_file:
        print("Could not find google/genai/types.py")
        sys.exit(1)
        
    print(f"Patching {target_file}...")
    
    with open(target_file, 'r', encoding='utf-8') as f:
        content = f.read()
        
    # Patch httpx_client
    old_str_1 = 'description="""A custom httpx client to be used for the request.""",'
    new_str_1 = 'description="""A custom httpx client to be used for the request.""", exclude=True,'
    
    # Patch httpx_async_client
    old_str_2 = 'description="""A custom httpx async client to be used for the request.""",'
    new_str_2 = 'description="""A custom httpx async client to be used for the request.""", exclude=True,'
    
    if 'exclude=True' in content:
        print("File already patched or different version.")
    else:
        new_content = content.replace(old_str_1, new_str_1).replace(old_str_2, new_str_2)
        
        if new_content == content:
            print("String to replace not found. Check version.")
            sys.exit(1)
            
        with open(target_file, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print("Patch applied successfully.")

if __name__ == "__main__":
    patch_genai()
