def save_graph_png(graph, output="storage/agent_flow.png"):
    try:
        # 修复正确写法
        with open(output, "wb") as f:
            f.write(graph.get_graph().draw_mermaid_png())
        print(f"流程图已保存至 {output}")
    except Exception as e:
        print(f"可视化失败：{e}")