# AI_Prompts.py

# A centralized registry for standardized prompts and prompt wrappers
# Used for ChatGPT, other LLMs, or even in-game AI behavior scripting

from typing import Callable, Dict

PROMPTS = {
    "check_repo": "check the repo history, ",
    "update": "update the development plan, ",
    "complete": "if milestone was completed, ",
    "continue": "continue to next milestone, ",
    "apply_patch": "apply full patch to: "
}

reference0 = "reference: /VoxelSpaceGame, "
website0 = "website: https://github.com/UrukuTelal/, "

files = {
    "api": "api.readme",
    "sun_color": "assets/2k_sun_color.jpg",
    "sun_color_inverted": "assets/2k_sun_color_inverted.jpg",
    "sun_grayscale": "assets/2k_sun_grayscale.jpg",

    "block_types": "core/block_types.py",
    "constants": "core/constants.py",
    "coordinates": "core/coordinates.py",
    "planet_projection": "core/planet_projection.py",
    "voxel_math": "core/voxel_math.py",

    "main": "main.py",

    "rendering": "rendering/rendering.py",
    "block_vert": "rendering/shaders/cube.vert",
    "block_frag": "rendering/shaders/cube.frag",
    "texture_loader": "rendering/texture_loader.py",

    "biomes": "world/biomes.py",
    "block": "world/block.py",
    "chunks": "world/chunks.py",
    "planet_generator": "world/planet_generator.py",

    "development_plan": "development_plan.md"
}

def add_file(label, path):
    if label not in files:
        files[label] = path
        print(f"Added: {label} → {path}")
    else:
        print(f"{label} already exists: {files[label]}")

def generate_prompt(check_repo=False, update=False, complete=False, files_list=None):
    todo = reference0
    if files_list is None:
        files_list = []

    if check_repo:
        todo += "check the repo history, "

    if update:
        todo += "update the, "
        for file in files_list:
            todo += f"{file}, "

    if complete:
        todo += "if milestone was completed, continue to next milestone, "

    return {
        "reference0": reference0,
        "website0": website0,
        "todo": todo.strip(", "),
        "development_plan": "development_plan"
    }

class PromptRegistry:
    def __init__(self):
        self.prompts: Dict[str, str] = {}
        self.wrappers: Dict[str, Callable[[str], str]] = {}

    def register_prompt(self, name: str, template: str):
        """Register a named prompt template."""
        self.prompts[name] = template

    def register_wrapper(self, name: str, func: Callable[[str], str]):
        """Register a named prompt wrapper function."""
        self.wrappers[name] = func

    def get_prompt(self, name: str, **kwargs) -> str:
        """Render the named prompt with kwargs."""
        template = self.prompts.get(name)
        if not template:
            raise ValueError(f"Prompt '{name}' not found.")
        return template.format(**kwargs)

    def apply_wrapper(self, wrapper_name: str, prompt_text: str) -> str:
        """Apply a wrapper to a given prompt string."""
        wrapper = self.wrappers.get(wrapper_name)
        if not wrapper:
            raise ValueError(f"Wrapper '{wrapper_name}' not found.")
        return wrapper(prompt_text)

# --- Instance ---
prompts = PromptRegistry()

# --- Example Prompts ---
prompts.register_prompt("species_description", "Describe the species evolving under {environment} conditions on a {planet_type} world.")
prompts.register_prompt("shader_explanation", "Explain this GLSL shader code in simple terms:\n\n{shader_code}")

# --- Example Wrappers ---
def concise_wrapper(text: str) -> str:
    return f"Be concise and direct.\n\n{text}"

def lore_style_wrapper(text: str) -> str:
    return f"Present this information as if told by a wise historian AI.\n\n{text}"

prompts.register_wrapper("concise", concise_wrapper)
prompts.register_wrapper("lore", lore_style_wrapper)

# --- Example Usage ---
if __name__ == "__main__":
    # Generate and print a prompt from registry and wrap it
    base_prompt = prompts.get_prompt("species_description", environment="cryonic methane seas", planet_type="tidally locked")
    final_prompt = prompts.apply_wrapper("lore", base_prompt)
    print("Wrapped Prompt:\n", final_prompt)
    
    # Generate a todo prompt example
    todo_prompt = generate_prompt(check_repo=True, update=True, complete=True, files_list=["development_plan", "chunks.py"])
    print("\nGenerated TODO prompt:")
    for key, val in todo_prompt.items():
        print(f"{key}: {val}")

    # Add a new file example
    add_file("new_module", "core/new_module.py")
