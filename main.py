import os
import re
import sys

dirname = sys.argv[1]

for filename in os.listdir(dirname):
    if not os.path.exists(f"/home/rob/software/ToolAnalysis/UserTools/{filename}/{filename}.cpp"):
        print(f"################### {filename} does not exist ###############")
        continue
    with open(f"/home/rob/software/ToolAnalysis/UserTools/{filename}/{filename}.cpp", 'r') as f:
        code = f.read()
        m_vars = []
        m_data_set = []
        m_data_get = []
        m_vars_tokens = re.findall(r"m_variables.*;", code)
        m_data_tokens = re.findall(r"m_data->Stores.*;", code)
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
                # print(token)
                # print("Count statement, skipping")
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
                print(f"Skipping {token} due to IndexError, "
                      "does not look like get or set statement")
                if "Get" in token:
                    print("'Get' statements should use a string literal as a key, "
                          "not a variable!")
                    print(token)
                if "Set" in token:
                    print("'Set' statements should use a string literal as a key, "
                          "not a variable!")
                    print(token)
                continue
            if "Get" in token:
                m_data_get.append((store_name, key_string, var_name))
            if "Set" in token:
                m_data_set.append((store_name, key_string, var_name))

    if filename == "MRDLoopbackAnalysis":
        print("ajsnd;ak jsdksajdkasdaskdaskdjaksd;kas mkdsakdlsa dnajsn sandnas ksad ############################################################################################################################")
        print(f"m_variables: {m_vars}")
        print("----------------")
        print(f"m_data_gets: {m_data_get}")
        print("----------------")
        print(f"m_data_sets: {m_data_set}")


def scan_tool(filename):
    with open(filename, "r") as f:
        # Just load the entire file into memory, files shouldn't be too big
        code = f.read()
        m_vars = []
        m_data_set = []
        m_data_get = []
        skipped = []
        m_vars_tokens = re.findall(r"m_variables.*;", code)
        m_data_tokens = re.findall(r"m_data->Stores.*;", code)
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
                # print(token)
                # print("Count statement, skipping")
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
                print(f"Skipping {token} due to IndexError, "
                      "does not look like get or set statement")
                if "Get" in token:
                    print("'Get' statements should use a string literal as a key, "
                          "not a variable!")
                    print(token)
                if "Set" in token:
                    print("'Set' statements should use a string literal as a key, "
                          "not a variable!")
                    print(token)
                skipped.append(token)
                continue
            if "Get" in token:
                m_data_get.append((store_name, key_string, var_name))
            if "Set" in token:
                m_data_set.append((store_name, key_string, var_name))
    return m_vars, m_data_get, m_data_set, skipped
