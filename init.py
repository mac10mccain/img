import os
import aiohttp
import asyncio

ANTHROPIC_WEBHOOK = os.getenv("ANTHROPIC_WEBHOOK")
OPENAI_WEBHOOK = os.getenv("OPENAI_WEBHOOK")
GEMINI_WEBHOOK = os.getenv("GEMINI_WEBHOOK")
SYNTHESIS_WEBHOOK = os.getenv("SYNTHESIS_WEBHOOK")

REQUEST_TIMEOUT = aiohttp.ClientTimeout(total=300)


async def call_webhook(session, url, params):
    async with session.get(url, params=params, timeout=REQUEST_TIMEOUT) as resp:
        return await resp.json()


async def run_research(company_name):
    params = {"companyName": company_name}
    async with aiohttp.ClientSession() as session:
        gemini, openai, anthropic = await asyncio.gather(
            call_webhook(session, GEMINI_WEBHOOK, params),
            call_webhook(session, OPENAI_WEBHOOK, params),
            call_webhook(session, ANTHROPIC_WEBHOOK, params),
        )
    return {"gemini": gemini, "openai": openai, "anthropic": anthropic}


async def send_to_synthesis(research, company_name):
    async with aiohttp.ClientSession() as session:
        async with session.get(
            SYNTHESIS_WEBHOOK,
            json={"companyName": company_name, "research": research},
            timeout=REQUEST_TIMEOUT,
        ) as resp:
            return await resp.json()
