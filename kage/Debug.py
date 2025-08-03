import core as c
class DebugKage(c.Kage):
    def __init__(self, *args, debug=False, **kwargs):
        super().__init__(*args, **kwargs)
        self.debug = debug

    def execute(self):
        if self.debug:
            print(f"🚀 Starting execution with {len(self.functions)} functions")
            print(f"📋 Execution order: {self._resolve_execution_order()}")

        execution_order = self._resolve_execution_order()

        for func_name in execution_order:
            binding = self.functions[func_name]

            if self.debug:
                print(f"⚡ Executing: {func_name}")
                print(f"   Input mapping: {binding.input_mapping}")
                print(f"   Dependencies: {binding.dependencies}")

            try:
                # Prepare arguments
                kwargs = {}
                for param_name, input_key in binding.input_mapping.items():
                    if input_key in self.execution_results:
                        kwargs[param_name] = self.execution_results[input_key]
                    else:
                        kwargs[param_name] = self._get_nested_value(input_key, self.input_data)

                if self.debug:
                    print(f"   Arguments: {kwargs}")

                # Execute
                result = binding.func(**kwargs)
                self.execution_results[func_name] = result

                if self.debug:
                    print(f"   Result: {result}")

                # Update output
                if binding.output_key:
                    self._set_nested_value(binding.output_key, result, self.output_data)
                    if self.debug:
                        print(f"   Stored in output['{binding.output_key}']")

            except Exception as e:
                if self.debug:
                    print(f"❌ Error in {func_name}: {e}")
                raise c.ExecutionError(f"Error executing function '{func_name}': {str(e)}") from e

        if self.debug:
            print(f"✅ Execution completed successfully")
            print(f"📤 Final output keys: {list(self.output_data.keys())}")

        return self.output_data



