# ToolDocumentor

ToolDocumentor is a script for automatically generating documentation for ToolAnalysis Tools. It captures every `Get` and `Set` interaction with the DataModel for a Tool and documents the store, variable and key for future reference.

Note that the documentor cannot capture DataModel interactions where the key is a string variable, the key must be hardcoded. It may also trip up if the file has weird whitespacing.

```
usage: main.py [-h] [-r] [-o {stdout,readme}] path

This script tracks a Tool's interactions with the DataModel and documents
them.

positional arguments:
  path                  Path to the Tool directory or a directory of Tools

options:
  -h, --help            show this help message and exit
  -r, --recursive       Required if path is a directory of Tools
  -o {stdout,readme}, --output {stdout,readme}
                        If not specified, output is stdout
 ```
