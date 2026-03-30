from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/research", methods=["POST"])
def research():
    data = request.get_json()
    question = (data or {}).get("question", "").strip()
    if not question:
        return jsonify({"error": "Please enter a research question."}), 400

    try:
        from langchain_core.messages import AIMessage, ToolMessage, HumanMessage
        from main import graph

        final_state = graph.invoke(HumanMessage(content=question))
        messages = final_state if isinstance(final_state, list) else [final_state]

        # Walk through all AI messages and collect each draft/revision
        iterations = []
        seen_queries = []

        for msg in messages:
            if isinstance(msg, AIMessage) and msg.tool_calls:
                for tc in msg.tool_calls:
                    args = tc.get("args", {})
                    if "answer" not in args:
                        continue
                    reflection = args.get("reflection", {})
                    queries = args.get("search_queries", [])
                    # deduplicate queries while preserving order
                    for q in queries:
                        if q not in seen_queries:
                            seen_queries.append(q)
                    iterations.append({
                        "answer": args.get("answer", ""),
                        "search_queries": queries,
                        "missing": reflection.get("missing", "") if isinstance(reflection, dict) else getattr(reflection, "missing", ""),
                        "superfluous": reflection.get("superfluous", "") if isinstance(reflection, dict) else getattr(reflection, "superfluous", ""),
                        "references": args.get("references", []),
                    })

        if not iterations:
            return jsonify({"error": "No answer generated."}), 500

        final = iterations[-1]

        return jsonify({
            "answer": final["answer"],
            "references": final["references"],
            "search_queries": seen_queries,
            "num_revisions": len(iterations) - 1,   # drafts after the first
            "reflection": {
                "missing": final["missing"],
                "superfluous": final["superfluous"],
            },
        })

    except Exception as e:
        import traceback; traceback.print_exc()
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True, port=5004)
