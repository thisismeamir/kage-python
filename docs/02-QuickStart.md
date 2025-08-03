# Quick Start
In the following document we would build a very simple example of a system using KPF. The following plugin is a simple hello world example done using two different functions, bind and execut using Kage.

> It is adviced that before reading any documentation about Kage Python Framework, one has a good understanding about Kage main project, and Kage Ecosystem. You can find more [here]("https://github.com/thisismeamir/Kage-Ecosystem).

## Setting Up
To begin creating a plugin (node) in python. We first need to understand what a node is. Kage defines nodes as an abstraction of a task or a job. Given an input (json) it returns and output (json) and artifacts (side effects, files, and other object). A node can be defined in Kage using a node schema file which is a json with the following properties.

```json
{
  "name": "string",
  "version": "string",
  "type": "node",
  "model": {
    "execution_model": {
      "language": "string",
      "input_schema":  {},
      "output_schema": {},
      "artifacts": ["string"]
    },
    "source": "string",
    "working_directory": "string",
    "entry_file": "string",
    "output_directory": "string"
  },
  "metadata": {
    "description": "string",
    "authors": [
      {
        "name": "string",
        "email": "string",
        "url": "string"
      }
    ],
    "manual": "string",
    "repository": "string"
  }
}
```

To dive deep into understanding this file or nodes in general refer to the documentation of Kage itself. Here what we are interested in is the model key:
```json
{
    "model": {
    "execution_model": {
      "language": "string",
      "input_schema":  {},
      "output_schema": {},
      "artifacts": ["string"]
    },
    "source": "string",
    "working_directory": "string",
    "entry_file": "string"
  }
}
```
- `model`: Describes necessary information to Kage about the node (plugin).
- `execution_model`: Information about what language the plugin is written in. Helps because Kage commits to be language-agnostic, and therefore, needs to know what language this plugin/node is written in.
- `language`: Correct name of the language (e.g `python` not `py`).
- `input_schema`: An object that defines what does the json input should look like, both structure and type. This would be used further to make sure that the plugin would run correctly (apart from the errors that are internally caused by the plugin itself).
- `output_schema`: An object that shows what does the output of this plugin would look like. This is being used in graphs (another term for automation modules in Kage) to understand what is being sent to the next step of the process by this task.
- `artifacts`: Least of possible side effects and artifacts files.
- `source`: The path to the source of the plugin, or where the executables live.
- `working_directory`: Can be empty or in the input schema but if mentioned here tells Kage to execute this task in a specific folder.
- `entry_file`: The file that Kage would recognize as something that can be run for the desired output, defining this would enable you to have multiple files, folders and packages in the source directory, which makes writing more complex plugins easier.

## Writing A simple Plugin
### Step 01: Make The Schemas
Firstly, we would define what an input for this node would look like. Similar to how we define in the node json, but for educational purposes let us define input_schema, and output_schema alone without other keys:
```json
{
  "type": "object",
  "required": ["user"],
  "properties": {
    "name": "string",
    "email": "string",
    "age": "integer"
  }
}
```
and for output we require only one field of message:
```json
{
  "type": "object",
  "properties": {
    "message": "string"
  }
}
```

### Step 02: Define Functionality
Next we simply start writing the plugin functionality. We can use different files, paths, and packages. For this plugin we simply need to define a single function:
```python
def greeting(name: str, email: str, age: int) -> str:
    return f"Hello {name}, you're {age} year(s) old and have the email {email}"
```
> I advise that you only have a single functionality per node. You can for sure write a complete program that does everything needed for a workflow, but the purpose of Kage is to make building blocks so that later on you can extend functionalities without needing to start a new project.

### Step 03: Initializing Kage
Make a file named `<entry_file>.py`, where `<entry_file>` is the key value defined in your node json. Inside it we would
1. Initialize Kage:
2. Bind The Functions: 
3. Add Kage Main Function: 
4. Execute Kage:
5. Return the output: