"""Step 8: Groq 플러그인 설치 및 Credentials 설정"""
import asyncio
import sys
import os
from pathlib import Path

from dotenv import load_dotenv

sys.path.insert(0, os.path.dirname(__file__))

load_dotenv(Path(__file__).resolve().parent / ".env")

from config import DifyConfig
from dify_client import DifyClient

async def main():
    groq_api_key = os.getenv("GROQ_API_KEY", "").strip()
    if not groq_api_key:
        print("[ERROR] GROQ_API_KEY가 설정되지 않았습니다. tools/.env에 GROQ_API_KEY를 추가하세요.")
        return False

    config = DifyConfig()
    client = DifyClient(config)

    # 8-3: 로그인
    print("Dify 로그인 중...")
    try:
        await client._ensure_authenticated()
        print("로그인 성공")
    except Exception as e:
        print(f"로그인 실패: {e}")
        return False

    # 8-4: Groq 플러그인 확인 및 설치
    print("Groq 플러그인 확인 중...")
    try:
        plugins = await client.list_plugins()
        groq_installed = any("groq" in p.get("plugin_id", "") for p in plugins.get("plugins", []))
    except Exception as e:
        print(f"플러그인 목록 조회 실패: {e}")
        groq_installed = False

    if not groq_installed:
        print("Groq 플러그인 설치 중...")
        try:
            import httpx
            async with httpx.AsyncClient(timeout=15.0) as http:
                resp = await http.post(
                    "https://marketplace.dify.ai/api/v1/plugins/batch",
                    json={"plugin_ids": ["langgenius/groq"]},
                )
                uid = resp.json()["data"]["plugins"][0]["latest_package_identifier"]
            print(f"설치할 패키지 ID: {uid}")

            result = await client.install_marketplace_plugin([uid])
            print(f"설치 요청 결과: {result}")

            print("설치 완료 대기 중 (최대 240초)...")
            for i in range(24):
                await asyncio.sleep(10)
                resp = await client._request("GET", "/workspaces/current/plugin/tasks")
                tasks = resp.get("tasks", [])
                if not tasks:
                    print("설치 완료")
                    groq_installed = True
                    break
                plugin_status = tasks[0]["plugins"][0]["status"]
                print(f"  설치 상태: {plugin_status} ({(i+1)*10}s)")
                if plugin_status == "success":
                    groq_installed = True
                    break
                if plugin_status == "failed":
                    print(f"설치 실패: {tasks[0]['plugins'][0].get('message', '')}")
                    break
        except Exception as e:
            print(f"Groq 플러그인 설치 중 오류: {e}")
    else:
        print("Groq 플러그인이 이미 설치되어 있습니다.")
        groq_installed = True

    if not groq_installed:
        print("Settings > Model Providers에서 Groq 플러그인을 수동 설치해주세요.")
        return False

    # 8-5: Credentials 검증 및 저장
    print("Groq Credentials 검증 중...")
    credentials = {"api_key": groq_api_key}
    try:
        await client.validate_provider_credentials("langgenius/groq/groq", credentials)
        print("Credentials 검증 성공")
    except Exception as e:
        print(f"Groq API Key가 유효하지 않습니다: {e}")
        print("Settings > Model Providers에서 수동 설정해주세요.")
        return False

    print("Groq Credentials 저장 중...")
    try:
        await client.save_provider_credentials("langgenius/groq/groq", credentials)
        print("Groq 모델 프로바이더 설정 완료")
        return True
    except Exception as e:
        print(f"Credentials 저장 실패: {e}")
        return False


if __name__ == "__main__":
    result = asyncio.run(main())
    sys.exit(0 if result else 1)
