def test_docs_crud_and_search(client) -> None:
    create = client.post(
        "/docs",
        json={
            "space": "project-alpha",
            "title": "주간 회의록",
            "content": "이번 주 주요 결정사항 정리",
            "tags": ["meeting", "weekly"],
        },
    )
    assert create.status_code == 200
    doc_id = create.json()["id"]

    search = client.get("/docs/search/query", params={"q": "결정사항"})
    assert search.status_code == 200
    assert len(search.json()["docs"]) == 1

    update = client.patch(f"/docs/{doc_id}", json={"content": "업데이트된 내용"})
    assert update.status_code == 200
    assert update.json()["content"] == "업데이트된 내용"


def test_chat_channel_and_message(client) -> None:
    ch = client.post("/chat/channels", json={"name": "rnd", "description": "R&D"})
    assert ch.status_code == 200
    channel_id = ch.json()["id"]

    msg = client.post(
        f"/chat/channels/{channel_id}/messages",
        json={"sender": "agent", "content": "오늘 커밋 요약했습니다."},
    )
    assert msg.status_code == 200
    assert msg.json()["sender"] == "agent"

    logs = client.get(f"/chat/channels/{channel_id}/messages")
    assert logs.status_code == 200
    assert len(logs.json()["messages"]) == 1
