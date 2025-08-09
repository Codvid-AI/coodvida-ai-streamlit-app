# Updated client code with mod_count support
from demo_modules import network
from typing import Any, Literal
from IPython.display import clear_output

# Initialize network
base_url = None


def init(env: Literal["development", "production", "local", "betamale"]):
    global base_url
    if env == "development":
        base_url = "https://codvid-ai-backend-development.up.railway.app"
    elif env == "production":
        base_url = "https://codvid-ai-backend-production.up.railway.app"
    elif env == "local":
        base_url = "http://localhost:8080"
    elif env == "betamale":
        base_url = "https://codvid-ai-backend-betamale.up.railway.app"
    else:
        raise ValueError(f"Invalid environment: {env}")
    network.init(base_url)
    print(f"Using base URL: {base_url}")


# Global variables
session_token: str = None
local_user_data = {"projects": {}}


def print_chats(project_name: str, max: int = -1):
    project = local_user_data["projects"][project_name]
    chat_txt = "-" * 15 + "start of chats" + "-" * 15 + "\n"
    chats = project["chats"][:]
    if max != -1:
        chats = chats[-max:]
    for msg in chats:
        chat_txt += f"""<sender: {msg["role"]}>\n"""
        for key in msg:
            chat_txt += f"[{key}]: {msg[key]}\n\n"
    chat_txt += "-" * 15 + "end of chats" + "-" * 15
    print(chat_txt)


def apply_user_data_mods(
    context_mods: list[
        dict[Literal["key_path"] | Literal["mode"] | Literal["value"], Any]
    ],
):
    # Keep track of projects that were modified to increment their mod_count
    modified_projects = set()

    for mod in context_mods:
        key_path = mod["key_path"]
        mode = mod["mode"]
        value = mod.get("value")

        # Check if this modification affects a project and should increment mod_count
        if (
            len(key_path) >= 2
            and key_path[0] == "projects"
            and isinstance(key_path[1], str)
            and mode in ["create", "edit", "del", "append"]
        ):
            # Don't increment mod_count if we're directly modifying the mod_count field itself
            if not (len(key_path) == 3 and key_path[2] == "mod_count"):
                modified_projects.add(key_path[1])

        # Traverse to the parent of the modification target node
        target = local_user_data
        for key in key_path[:-1]:
            if isinstance(target, dict):
                if key not in target:
                    if mode == "create":
                        target[key] = {}
                    else:
                        raise KeyError(f"Key '{key}' not found in path {key_path}")
                target = target[key]
            elif isinstance(target, list) and isinstance(key, int):
                if key >= len(target):
                    raise IndexError(f"Index {key} out of range in path {key_path}")
                target = target[key]
            else:
                raise TypeError(f"Cannot traverse key '{key}' in path {key_path}")
        last_key = key_path[-1]
        if mode == "create":
            if isinstance(target, dict):
                target[last_key] = value
            elif isinstance(target, list) and isinstance(last_key, int):
                if last_key == len(target):
                    target.append(value)
                elif last_key < len(target):
                    target[last_key] = value
                else:
                    raise IndexError(f"Index {last_key} out of range for create mode")
            else:
                raise TypeError(f"Cannot create at key '{last_key}' in path {key_path}")
        elif mode == "edit":
            if isinstance(target, dict):
                if last_key not in target:
                    raise KeyError(f"Key '{last_key}' not found for edit mode")
                target[last_key] = value
            elif isinstance(target, list) and isinstance(last_key, int):
                if last_key >= len(target):
                    raise IndexError(f"Index {last_key} out of range for edit mode")
                target[last_key] = value
            else:
                raise TypeError(f"Cannot edit at key '{last_key}' in path {key_path}")
        elif mode == "del":
            if isinstance(target, dict):
                if last_key in target:
                    del target[last_key]
            elif isinstance(target, list) and isinstance(last_key, int):
                if last_key < len(target):
                    target.pop(last_key)
            else:
                raise TypeError(f"Cannot delete at key '{last_key}' in path {key_path}")
        elif mode == "append":
            if isinstance(target, dict):
                if last_key not in target or not isinstance(target[last_key], list):
                    target[last_key] = []
                target[last_key].append(value)
            elif isinstance(target, list) and isinstance(last_key, int):
                if last_key < len(target):
                    if not isinstance(target[last_key], list):
                        target[last_key] = []
                    target[last_key].append(value)
                else:
                    raise IndexError(f"Index {last_key} out of range for append mode")
            else:
                raise TypeError(f"Cannot append at key '{last_key}' in path {key_path}")
        else:
            raise ValueError(f"Unknown mode: {mode}")

    # Increment mod_count for all modified projects
    for project_name in modified_projects:
        if project_name in local_user_data.get("projects", {}):
            current_mod_count = local_user_data["projects"][project_name].get(
                "mod_count", 0
            )
            local_user_data["projects"][project_name]["mod_count"] = (
                current_mod_count + 1
            )


def check_and_reload_project_data(project_name: str):
    """
    Check if the local mod_count matches the server mod_count.
    If not, reload the project data from the server.
    """
    # Get server mod_count
    content = {"project_name": project_name}
    response = network.send(
        "codvid-ai/project/get-project-mod-count",
        content=content,
        session_token=session_token,
    )

    if not response.get_dict()["result"]:
        print(f"Error getting server mod_count for project {project_name}")
        return False

    server_mod_count = response.get_dict()["response"]["mod_count"]
    local_mod_count = local_user_data["projects"][project_name].get("mod_count", None)

    if server_mod_count != local_mod_count:
        print(
            f"Mod count mismatch detected! Server: {server_mod_count}, Local: {local_mod_count}"
        )
        print("Reloading project data from server...")

        # Reload project data
        content = {"project_name": project_name}
        response = network.send(
            "codvid-ai/project/get-project-data",
            content=content,
            session_token=session_token,
        )

        if response.get_dict()["result"]:
            local_user_data["projects"][project_name] = response.get_dict()["response"][
                "project_data"
            ]
            print("Project data reloaded successfully!")
            return True
        else:
            print("Error reloading project data from server")
            return False

    print(
        f"server and local mod_count are the same! no reload needed: {server_mod_count} == {local_mod_count}"
    )
    return True


def ai_interact(project_name: str, message: dict, max_chats_printed=3):

    request_content = {
        "project_name": project_name,
        "message": message,
    }

    stream = network.send(
        method="POST",
        route="codvid-ai/ai/respond",
        session_token=session_token,
        content=request_content,
        stream=True,
    )
    chunk_list = []

    for chunk in stream:
        chunk_list.append(chunk)
        if chunk and chunk["result"]:
            apply_user_data_mods(chunk["response"]["data_mods"])
            clear_output()
            print_chats(project_name=project_name, max=max_chats_printed)
            print("AI typing...")
        elif chunk:
            print("issue:")
        else:
            print("error interaction. response format invalid!")

    clear_output()
    print_chats(project_name=project_name)

    # After the complete response, check if we need to reload project data
    check_and_reload_project_data(project_name)

    return chunk_list


def chat(project_name: str):
    print()
    pmpt = "Please input your message.\n"
    pmpt += """(type 3 empty lines to send, "/q" to cancel, "/r" to force respond without sending new message)"""

    msg_lines = []
    while True:
        inp = input(pmpt)
        if inp == "":
            if len(msg_lines) >= 2 and all(l == "" for l in msg_lines[-2:]):
                break
        elif inp == "/q":
            return False
        elif inp == "/r":
            msg_lines = []
            break
        elif inp == "/del":
            project = local_user_data["projects"][project_name]
            if project["chats"]:
                deleted_chat = project["chats"].pop()
                print(f"Deleted chat: {deleted_chat}")
                print_chats(project_name)
            else:
                print("No chats to delete")
            return True
        msg_lines.append(inp)
        print(inp)

    msg_lines = msg_lines[:-2]
    msg_txt = "\n".join(msg_lines)

    msg = {"role": "user", "type": "text", "text": msg_txt}

    if msg_txt:
        apply_user_data_mods(
            [
                {
                    "key_path": ["projects", project_name, "chats"],
                    "mode": "append",
                    "value": msg,
                }
            ]
        )

    ai_interact(project_name=project_name, message=msg)
    return True


# Example usage functions
def login(email: str, password: str):
    """Login and get session token"""
    global session_token
    data = {"auth_type": "email", "email": email, "password": password}
    response = network.send("/codvid-ai/auth/login", data)
    response.print()
    session_token = response.get_dict().get("token")
    return session_token is not None


def signup(email: str, password: str):
    """Signup and get session token"""
    global session_token
    data = {"auth_type": "email", "email": email, "password": password}
    response = network.send("/codvid-ai/auth/signup", data)
    response.print()
    session_token = response.get_dict().get("token")
    return session_token is not None


def delete_account():
    """Delete account"""
    response = network.send(
        "/codvid-ai/user/delete-account", session_token=session_token
    )
    response.print()
    return response.get_dict().get("result", False)


def get_project_list():
    """Get project list"""
    response = network.send(
        "/codvid-ai/project/get-project-list", session_token=session_token
    )
    response.print()
    return response.get_dict()["response"].get("project_list")


def create_project(project_name: str):
    """Create a new project"""
    data = {"project_name": project_name}
    response = network.send(
        "/codvid-ai/project/create-project", content=data, session_token=session_token
    )
    response.print()
    return response.get_dict().get("result", False)


def delete_project(project_name: str):
    """Delete a project"""
    response = network.send(
        "/codvid-ai/project/delete-project",
        content={"project_name": project_name},
        session_token=session_token,
    )
    if local_user_data.get("projects") and project_name in local_user_data["projects"]:
        del local_user_data["projects"][project_name]
    response.print()
    return response.get_dict().get("result", False)


def load_project_data(project_name: str):
    """Get project data and initialize local cache"""
    global local_user_data
    data = {"project_name": project_name}
    response = network.send(
        "codvid-ai/project/get-project-data", content=data, session_token=session_token
    )

    if response.get_dict()["result"]:
        project_data = response.get_dict()["response"]["project_data"]
        local_user_data = {
            "global_data": {"ai_memory": {}, "video_reflections": {}},
            "projects": {project_name: project_data},
        }
        return True
    return False


def start_chat(project_name: str):
    """Start an interactive chat session"""
    check_and_reload_project_data(project_name=project_name)
    print_chats(project_name)
    while chat(project_name):
        pass


# Test the implementation
if __name__ == "__main__":
    # Example usage
    print("Updated client with mod_count support")
    print(
        "Use login(), create_project(), get_project_data(), and start_chat() functions"
    )
