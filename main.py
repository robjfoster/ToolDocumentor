import argparse
import datetime
import os
import re
import sys
from typing import List


def cmdline_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="This script tracks a Tool's interactions with the DataModel and documents them.")
    p.add_argument(
        "path", help="Path to the Tool directory or a directory of Tools", type=str)
    p.add_argument("-r", "--recursive", help="Required if path is a directory of Tools",
                   default=False, action="store_true")
    p.add_argument(
        "-o", "--output", help="If not specified, output is stdout", choices=["stdout", "readme"], type=str, required=False)
    return p.parse_args()


def get_src_file(path: str) -> str:
    tool_name = os.path.basename(os.path.normpath(path))
    src_file = f"{path}/{tool_name}.cpp"
    return src_file


def get_readme_file(path: str) -> str:
    readme_file = f"{path}/README.md"
    return readme_file


def print_output(m_vars: List[str],
                 m_data_get: List[str],
                 m_data_set: List[str],
                 skipped: List[str]
                 ) -> None:
    print("ToolDocumentor output:\n")
    print("m_variables:", m_vars, "\n")
    print("m_data->Stores->Get:", m_data_get, "\n")
    print("m_data->Stores->Set:", m_data_set, "\n")
    print("Skipped:", skipped, "\n")


def pretty_output(m_vars: List[tuple[str, str]],
                  m_data_get: List[tuple[str, str, str]],
                  m_data_set: List[tuple[str, str, str]],
                  skipped: List[str]
                  ) -> None:
    print("ToolDocumentor output:\n")
    print("The following m_variables are read from the config file:")
    print("Key", " "*37, "Variable")
    print("-"*60)
    for var in m_vars:
        print(var[0], " "*(40-len(var[0])), var[1])
    print("\n")
    print("The following keys are retrieved ('Get') from the DataModel:")
    print("Store", " "*15, "Key", " "*17, "Variable")
    print("-"*60)
    for var in m_data_get:
        print(var[0], " "*(20-len(var[0])),
              var[1], " "*(20-len(var[1])), var[2])
    print("\n")
    print("The following keys are stored ('Set') in the DataModel:")
    print("Store", " "*15, "Key", " "*17, "Variable")
    print("-"*60)
    for var in m_data_set:
        print(var[0], " "*(20-len(var[0])),
              var[1], " "*(20-len(var[1])), var[2])
    print("\n")
    print("The following interactions with the DataModel were skipped:")
    for var in skipped:
        print(var)


def output_markdown(m_vars: List[tuple[str, str]],
                    m_data_get: List[tuple[str, str, str]],
                    m_data_set: List[tuple[str, str, str]],
                    skipped: List[str],
                    readme_file: str
                    ) -> None:
    with open(readme_file, "a") as f:
        f.write("\n***\n")
        f.write("## ToolDocumentor:\n")
        f.write(
            "These are all the interactions between this Tool and the DataModel:\n\n\n")
        f.write("The following m_variables are read from the config file:\n")
        f.write("|Key|Variable|\n")
        f.write("|---|---|\n")
        for var in m_vars:
            f.write(f"|{var[0]}|`{var[1]}`|\n")
            # f.write(f"{var[0]}: (assigned to variable name {var[1]})\n")
        f.write("\n")
        f.write("The following keys are retrieved (`Get`) from the DataModel:\n")
        f.write("|Store|Key|Variable|\n")
        f.write("|---|---|---|\n")
        for var in m_data_get:
            f.write(f"|{var[0]}|{var[1]}|`{var[2]}`|\n")
        f.write("\n")
        f.write("The following keys are stored (`Set`) in the DataModel:\n")
        f.write("|Store|Key|Variable|\n")
        f.write("|---|---|---|\n")
        for var in m_data_set:
            f.write(f"|{var[0]}|{var[1]}|`{var[2]}`|\n")
        f.write("\n")
        f.write("The following interactions with the DataModel were skipped:\n")
        if skipped:
            for var in skipped:
                f.write(f'`{var}` \n')
        f.write(
            f"\n\nThis documentation was automatically generated. Last updated: {datetime.datetime.now().date()}\n")
        f.write("\n***\n")


def scan_tool(filename: str) -> tuple[List[tuple[str, str]],
                                      List[tuple[str, str, str]],
                                      List[tuple[str, str, str]],
                                      List[tuple[str]]]:
    with open(filename, "r") as f:
        # Just load the entire file into memory, files shouldn't be too big
        code = f.read()
        m_vars = []
        m_data_set = []
        m_data_get = []
        skipped = []
        m_vars_tokens = re.findall(r"m_variables.*;", code)
        m_data_tokens = re.findall(r"m_data->Stores.*;", code)
        # Trying out a different regex to avoid matching commented out lines, not working yet?
        # m_vars_tokens = re.findall(r"(?!\/\/\s)(?!\/\/).m_variables.*;", code)
        # m_data_tokens = re.findall(
        #     r"(?!\/\/\s)(?!\/\/).m_data->Stores.*;", code)
        for token in m_vars_tokens:
            # m_variables should only be "get"s
            if "Get" in token:
                key_string = re.findall(r'"([^"]*)"', token)[0]
                key_string = "".join(key_string.split())
                var_name = re.findall(r',(.*?)\)', token)[0]
                var_name = "".join(var_name.split())
                m_vars.append((key_string, var_name))
        for token in m_data_tokens:
            if ".count" in token:
                skipped.append(token)
                continue
            try:
                in_quotes = re.findall(r'"([^"]*)"', token)
                single_quotes = re.findall(r"'([^']*)'", token)
                # This whole block is required because people often use
                # single and double quotes within the same file (or line)
                if len(single_quotes) > 0:
                    if len(single_quotes) == 2:
                        in_quotes = single_quotes
                    elif len(in_quotes) == 1 and len(single_quotes) == 1:
                        single_index = token.index(single_quotes[0])
                        double_index = token.index(in_quotes[0])
                        if single_index < double_index:
                            in_quotes = [single_quotes[0], in_quotes[0]]
                        else:
                            in_quotes = [in_quotes[0], single_quotes[0]]
                    else:
                        print(f"Did not understand {token}, skipping")
                        continue
                store_name = "".join(in_quotes[0].split())
                key_string = "".join(in_quotes[1].split())
                var_name = re.findall(r',(.*?)\)', token)[0]
                var_name = "".join(var_name.split())
            except IndexError:
                # If we get here then it is a store statement that does not follow
                # the standard format
                print(filename)
                print(f'\nSkipping "{token}" due to IndexError - '
                      'does not look like get or set statement')
                if "Get" in token:
                    print("-> 'Get' statements should use a hardcoded string literal as a key, "
                          "not a variable!\n")
                    print(token)
                if "Set" in token:
                    print("-> 'Set' statements should use a hardcoded string literal as a key, "
                          "not a variable!\n")
                skipped.append(token)
                continue
            if "Get" in token:
                m_data_get.append((store_name, key_string, var_name))
            if "Set" in token:
                m_data_set.append((store_name, key_string, var_name))
    return m_vars, m_data_get, m_data_set, skipped


if __name__ == "__main__":
    args = cmdline_args()
    dirname = os.path.abspath(args.path)
    if args.recursive:
        if not os.path.isdir(args.path):
            print("Path must be a directory if recursive is specified")
            sys.exit(1)
        for filename in os.listdir(dirname):
            if not os.path.exists(f"{dirname}/{filename}/{filename}.cpp"):
                print(
                    f"################### {filename} does not exist ###############")
                continue
            m_vars, m_data_get, m_data_set, skipped = scan_tool(
                f"{dirname}/{filename}/{filename}.cpp")
            if args.output == "readme":
                output_markdown(m_vars, m_data_get, m_data_set,
                                skipped, get_readme_file(f"{dirname}/{filename}"))
            else:
                print_output(m_vars, m_data_get, m_data_set, skipped)
    else:
        filename = get_src_file(args.path)
        m_vars, m_data_get, m_data_set, skipped = scan_tool(filename)
        if args.output == "readme":
            output_markdown(m_vars, m_data_get, m_data_set,
                            skipped, get_readme_file(dirname))
        else:
            print_output(m_vars, m_data_get, m_data_set, skipped)
