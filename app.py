import asyncio
import aiohttp
from flask import Flask, request, jsonify
from dotenv import load_dotenv

load_dotenv()

from init import run_research, send_to_synthesis

app = Flask(__name__)


def run_async(coro):
    """Run an async coroutine from synchronous Flask context."""
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


@app.route("/research", methods=["POST"])
def research():
    body = request.get_json(silent=True)
    if not body or "companyName" not in body:
        return jsonify({"error": "Missing required field: companyName"}), 400

    company_name = body["companyName"]

    try:
        research_results = run_async(run_research(company_name))
    except (aiohttp.ClientError, asyncio.TimeoutError) as exc:
        return jsonify({
            "error": "Research webhooks failed",
            "details": str(exc),
        }), 500

    try:
        synthesis = run_async(send_to_synthesis(research_results, company_name))
    except (aiohttp.ClientError, asyncio.TimeoutError) as exc:
        return jsonify({
            "error": "Synthesis webhook failed",
            "details": str(exc),
        }), 500

    return jsonify({
        "company": company_name,
        "research": research_results,
        "synthesis": synthesis,
    })


if __name__ == "__main__":
    app.run(debug=True, port=5000)
