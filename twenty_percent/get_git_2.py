import requests
import json
import os
import time

def get_ons_repos(output_file="ons_repos.txt", max_repos=10):
    """
    Retrieves a list of public Python repositories from the ONSdigital GitHub
    organization, along with their sizes, and saves the information to a file.
    Stops after finding a maximum of 'max_repos' Python repositories.
    Writes repository information to the file as soon as it's found.

    Args:
        output_file: The name of the file to save the repository information to.
        max_repos: The maximum number of Python repositories to retrieve.
    """

    url = "https://api.github.com/users/ONSdigital/repos"
    page = 1
    per_page = 10  # Maximum allowed by GitHub API is 100
    python_repos_count = 0 # Counter for Python repos found
    repos_info = [] # Keep this if you still need to return the list

    with open(output_file, "w") as f: # Open file once for writing
        while True:
            if python_repos_count >= max_repos:
                print(f"Reached maximum number of Python repositories ({max_repos}). Stopping.")
                break # Stop if we have found enough Python repos

            time.sleep(1.3) # Keep the delay

            params = {"page": page, "per_page": per_page}
            response = requests.get(url, params=params)
            response.raise_for_status()  # Raise an exception for bad status codes

            repos = response.json()
            if not repos:
                print("No more repositories found on GitHub API page. Exiting.")
                break  # No more repositories from GitHub API

            for repo in repos:
                if repo["language"] == "Python":  # Filter for Python repositories
                    python_repos_count += 1
                    repo_data = { #create dict for appending and writing
                        "name": repo["name"],
                        "url": repo["clone_url"],
                        "size": repo["size"],  # Size in KB
                    }
                    repos_info.append(repo_data) # Still append to the list if you need to return it

                    # Write to file immediately
                    f.write(f"Name: {repo_data['name']}, URL: {repo_data['url']}, Size: {repo_data['size']} KB\n")
                    print(f"Found and saved Python repo #{python_repos_count}: {repo_data['name']}")


                    if python_repos_count >= max_repos:
                        print(f"Reached maximum number of Python repositories ({max_repos}). Stopping inner loop.")
                        break # Break out of the inner loop (for repo in repos)

            if python_repos_count >= max_repos:
                break # Break out of the while loop as well if max is reached

            page += 1

    print(f"Retrieved information for {python_repos_count} Python repositories and saved to {output_file}")
    return repos_info # Return the list for later use


def batch_clone_repos(repos_info, clone_dir="ons_repos"):
    """
    Batch clones the repositories listed in repos_info.

    Args:
        repos_info: A list of dictionaries, each containing 'name' and 'url'
          keys for a repository.
        clone_dir: The directory to clone the repositories into.
    """

    os.makedirs(clone_dir, exist_ok=True)  # Create the directory if it doesn't exist

    for repo in repos_info:
        repo_name = repo["name"]
        clone_url = repo["url"]
        target_dir = os.path.join(clone_dir, repo_name)

        if os.path.exists(target_dir):
            print(f"Skipping {repo_name} (already cloned)")
            continue

        print(f"Cloning {repo_name} from {clone_url} into {target_dir}...")
        try:
            # Use git clone command
            result = os.system(f"git clone {clone_url} {target_dir}")
            if result != 0: #git returns a non-zero value on failure
                print(f"Error cloning {repo_name}. Result Code {result}")
        except Exception as e:
            print(f"Error cloning {repo_name}: {e}")



if __name__ == "__main__":
    output_file = "ons_python_repos_top100.txt" # More descriptive filename
    repo_list = get_ons_repos(output_file=output_file, max_repos=100) # Get max 10 repos
    print("\n--- Repo List (returned from function) ---") # Added print for clarity
    print(repo_list) # Print the list returned - optional, but useful for verification
    print(f"\nRepository information is written into the file: {output_file}") # Updated message

    #batch_clone_repos(repo_list) # Now you can call this if you want to clone