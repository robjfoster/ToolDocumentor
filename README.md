# ToolDocumentor

ToolDocumentor is a script for automatically generating documentation for ToolAnalysis Tools. It captures every `Get` and `Set` interaction with the DataModel for a Tool and documents the store, variable and key for future reference.

Note that the documentor cannot capture DataModel interactions where the key is a string variable, the key must be hardcoded. It may also trip up if the file has weird whitespacing.
