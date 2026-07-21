"""Run the deterministic foundation graph from the repository root."""

import asyncio
import json

from enterprise_agent.modules.agent_runtime.graphs.main_graph.builder import build_main_graph


async def main() -> None:
    result = await build_main_graph().ainvoke(
        {"run_id": "demo-run", "query": "enterprise leave policy"}
    )
    serializable = {
        **result,
        "evidence": [item.model_dump() for item in result.get("evidence", [])],
    }
    print(json.dumps(serializable, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
