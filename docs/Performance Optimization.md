## Performance Optimization

### Memory-Optimized Execution

```python
import gc
from typing import Iterator

class StreamingKage(Kage):
    """Memory-efficient Kage for large datasets"""

    def __init__(self, *args, chunk_size: int = 1000, **kwargs):
        super().__init__(*args, **kwargs)
        self.chunk_size = chunk_size

    def process_streaming_data(self, data_stream: Iterator[Dict]) -> Iterator[Dict]:
        """Process data in chunks to minimize memory usage"""

        chunk = []
        for item in data_stream:
            chunk.append(item)

            if len(chunk) >= self.chunk_size:
                # Process chunk
                chunk_input = {"items": chunk}

                # Create temporary Kage for chunk
                temp_kage = Kage(chunk_input, self.input_schema, self.output_schema)

                # Copy function bindings
                for name, binding in self.functions.items():
                    temp_kage.functions[name] = binding

                # Execute chunk
                result = temp_kage.execute()
                yield result

                # Clear chunk and force garbage collection
                chunk.clear()
                del temp_kage
                gc.collect()

        # Process remaining items
        if chunk:
            chunk_input = {"items": chunk}
            temp_kage = Kage(chunk_input, self.input_schema, self.output_schema)

            for name, binding in self.functions.items():
                temp_kage.functions[name] = binding

            result = temp_kage.execute()
            yield result

# Usage for large datasets
def process_large_dataset():
    def data_generator():
        # Simulate large dataset
        for i in range(10000):
            yield {"id": i, "value": i * 2, "category": f"cat_{i % 10}"}

    streaming_kage = StreamingKage({}, {}, chunk_size=500)

    def process_chunk(items):
        return {
            "count": len(items),
            "sum_values": sum(item["value"] for item in items),
            "categories": list(set(item["category"] for item in items))
        }

    streaming_kage.bind_function(
        process_chunk,
        {"items": "items"},
        output_key="chunk_result"
    )

    # Process in chunks
    total_count = 0
    total_sum = 0
    all_categories = set()

    for chunk_result in streaming_kage.process_streaming_data(data_generator()):
        result = chunk_result["chunk_result"]
        total_count += result["count"]
        total_sum += result["sum_values"]
        all_categories.update(result["categories"])

    return {
        "total_items": total_count,
        "total_sum": total_sum,
        "unique_categories": len(all_categories)
    }
```
